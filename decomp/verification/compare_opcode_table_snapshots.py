#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


def parse_int(value: str) -> int:
    return int(str(value), 0)


def to_hex(value: int, digits: int = 8) -> str:
    return f"0x{value:0{digits}X}"


def build_file_metadata(path: Path, *, display_path: str | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": display_path or str(path),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def load_export(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{path} does not contain a non-empty 'entries' list")
    return payload


def normalize_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_entries = payload["entries"]
    normalized: list[dict[str, Any]] = []
    for entry in raw_entries:
        index = int(entry["index"])
        opcode = parse_int(entry["opcode"])
        handler_address = parse_int(entry["handler_address"])
        normalized.append(
            {
                "index": index,
                "opcode": opcode,
                "handler_address": handler_address & 0xFFFFFFFF,
            }
        )

    normalized.sort(key=lambda item: item["index"])
    for expected_index, entry in enumerate(normalized):
        if entry["index"] != expected_index:
            raise ValueError(
                "Export indices are not contiguous: "
                f"expected {expected_index}, found {entry['index']}"
            )
    return normalized


def build_expected_blob(entries: list[dict[str, Any]], pointer_size: int) -> bytes:
    if pointer_size != 4:
        raise ValueError(f"Unsupported pointer size {pointer_size}; expected 4")
    return b"".join(struct.pack("<I", entry["handler_address"]) for entry in entries)


def parse_snapshot(path: Path, expected_size: int) -> list[int]:
    data = path.read_bytes()
    if len(data) != expected_size:
        raise ValueError(
            f"{path} has {len(data)} bytes, expected exactly {expected_size} "
            "bytes for the selected opcode table snapshot"
        )
    return [value[0] for value in struct.iter_unpack("<I", data)]


def summarize_snapshot(
    snapshot_path: Path,
    *,
    label: str,
    entries: list[dict[str, Any]],
    focus_opcodes: set[int],
    handler_to_opcodes: dict[int, list[int]],
    expected_size: int,
    display_path: str | None = None,
) -> dict[str, Any]:
    observed_handlers = parse_snapshot(snapshot_path, expected_size)
    changed_details: list[dict[str, Any]] = []
    focus_entries: list[dict[str, Any]] = []

    for entry, observed_handler in zip(entries, observed_handlers):
        expected_handler = entry["handler_address"]
        row = {
            "index": entry["index"],
            "opcode": to_hex(entry["opcode"], digits=2),
            "expected_handler": to_hex(expected_handler),
            "observed_handler": to_hex(observed_handler),
            "changed": observed_handler != expected_handler,
            "observed_matches_export_opcodes": [
                to_hex(opcode, digits=2) for opcode in handler_to_opcodes.get(observed_handler, [])
            ],
        }

        if row["changed"]:
            changed_details.append(row)
        if entry["opcode"] in focus_opcodes:
            focus_entries.append(row)

    return {
        "label": label,
        "path": display_path or str(snapshot_path),
        "file_metadata": build_file_metadata(snapshot_path, display_path=display_path),
        "size_bytes": expected_size,
        "matching_entries": len(entries) - len(changed_details),
        "changed_entries": len(changed_details),
        "focus_entries": focus_entries,
        "changed_details": changed_details,
    }


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare one or more raw RAM dumps of the copied opcode table against "
            "the binary-derived INITBTL export. This is intended for PCSX-Redux "
            "runtime passes where the table at 0x800F4C28 needs to be proven "
            "unchanged or patched."
        )
    )
    parser.add_argument(
        "export_json",
        type=Path,
        help="JSON export with an 'entries' array, e.g. decomp/evidence/inittbl_opcode_table.json.",
    )
    parser.add_argument(
        "snapshots",
        nargs="*",
        type=Path,
        help="Raw little-endian 4-byte pointer table dumps to compare against the export baseline.",
    )
    parser.add_argument(
        "--label",
        action="append",
        default=[],
        help=(
            "Optional snapshot label. Repeat once per snapshot, in the same order "
            "as the snapshot paths."
        ),
    )
    parser.add_argument(
        "--focus-opcode",
        action="append",
        default=[],
        help="Opcode to highlight even if unchanged. Repeatable; defaults to 0x80,0x81,0x82.",
    )
    parser.add_argument(
        "--runtime-table-address",
        default="0x800F4C28",
        help="Runtime RAM address of the copied table, used for metadata only.",
    )
    parser.add_argument(
        "--write-expected-bin",
        type=Path,
        help="Optional output path for the reconstructed baseline table bytes.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON report path. Defaults to stdout.",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.label and len(args.label) != len(args.snapshots):
        parser.error("Pass either zero --label values or exactly one per snapshot path.")

    payload = load_export(args.export_json)
    pointer_size = int(payload.get("pointer_size", 4))
    entries = normalize_entries(payload)
    expected_blob = build_expected_blob(entries, pointer_size)
    expected_size = len(expected_blob)

    if args.write_expected_bin is not None:
        args.write_expected_bin.parent.mkdir(parents=True, exist_ok=True)
        args.write_expected_bin.write_bytes(expected_blob)

    focus_opcodes = {parse_int(value) & 0xFF for value in (args.focus_opcode or [])}
    if not focus_opcodes:
        focus_opcodes = {0x80, 0x81, 0x82}

    handler_to_opcodes: dict[int, list[int]] = {}
    for entry in entries:
        handler_to_opcodes.setdefault(entry["handler_address"], []).append(entry["opcode"])

    snapshots: list[dict[str, Any]] = []
    for index, snapshot_path in enumerate(args.snapshots):
        label = args.label[index] if args.label else snapshot_path.stem
        snapshots.append(
            summarize_snapshot(
                snapshot_path,
                label=label,
                entries=entries,
                focus_opcodes=focus_opcodes,
                handler_to_opcodes=handler_to_opcodes,
                expected_size=expected_size,
            )
        )

    report = {
        "baseline_export": str(args.export_json),
        "baseline_export_metadata": build_file_metadata(args.export_json),
        "table_name": payload.get("table_name"),
        "binary_table_address": payload.get("table_address"),
        "runtime_table_address": to_hex(parse_int(args.runtime_table_address) & 0xFFFFFFFF),
        "entry_count": len(entries),
        "pointer_size": pointer_size,
        "expected_size_bytes": expected_size,
        "focus_opcodes": [to_hex(opcode, digits=2) for opcode in sorted(focus_opcodes)],
        "expected_bin_path": str(args.write_expected_bin) if args.write_expected_bin else None,
        "expected_bin_metadata": (
            build_file_metadata(args.write_expected_bin)
            if args.write_expected_bin is not None
            else None
        ),
        "snapshots": snapshots,
    }

    text = json.dumps(report, indent=2)
    if args.output is None:
        print(text)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text + "\n", encoding="utf-8")
    print(f"wrote snapshot comparison report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
