#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


def load_local_opcodes(repo_root: Path) -> dict[int, dict[str, Any]]:
    script_path = repo_root / "dump_mpd_script.py"
    spec = importlib.util.spec_from_file_location("dump_mpd_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    local: dict[int, dict[str, Any]] = {}
    for opcode, (name, size) in module.OPCODES.items():
        local[int(opcode)] = {"name": name, "size": int(size)}
    return local


def load_export(path: Path) -> dict[int, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("entries", [])
    exported: dict[int, dict[str, Any]] = {}
    for entry in entries:
        opcode = int(entry["opcode"], 0) if isinstance(entry["opcode"], str) else int(entry["opcode"])
        exported[opcode] = entry
    return exported


def reconcile(
    local: dict[int, dict[str, Any]],
    exported: dict[int, dict[str, Any]],
    *,
    issues_only: bool,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for opcode in sorted(set(local) | set(exported)):
        row: dict[str, Any] = {
            "opcode": f"0x{opcode:02X}",
            "local_name": local.get(opcode, {}).get("name"),
            "local_size": local.get(opcode, {}).get("size"),
            "binary_handler_name": exported.get(opcode, {}).get("handler_name"),
            "binary_handler_address": exported.get(opcode, {}).get("handler_address"),
            "issues": [],
        }

        if opcode not in local:
            row["issues"].append("missing-local-decoder-entry")
        if opcode not in exported:
            row["issues"].append("missing-binary-export-entry")

        local_name = row["local_name"]
        handler_name = row["binary_handler_name"]

        if local_name and local_name.startswith("Opcode") and handler_name and not handler_name.startswith(("func_", "_invalid")):
            row["issues"].append("placeholder-local-name-with-named-binary-handler")

        if local_name and not local_name.startswith("Opcode") and handler_name in {"func_800B66E4", "_invalidOpcode"}:
            row["issues"].append("named-local-opcode-but-binary-handler-looks-stublike")

        if row["issues"] or not issues_only:
            results.append(row)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare local opcode names against a binary-derived opcode table export."
    )
    parser.add_argument(
        "export_json",
        type=Path,
        help="Path to a JSON export with an 'entries' array containing opcode and handler data.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root containing dump_mpd_script.py",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show every opcode row, not just rows with issues.",
    )
    args = parser.parse_args()

    local = load_local_opcodes(args.repo_root)
    exported = load_export(args.export_json)
    rows = reconcile(local, exported, issues_only=not args.show_all)
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
