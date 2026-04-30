#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_repo_path(raw_path: str | None, repo_root: Path) -> Path | None:
    if raw_path is None:
        return None
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (repo_root / path).resolve()


def ensure_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if value is None:
        payload[key] = []
        return payload[key]
    if not isinstance(value, list):
        raise ValueError(f"Observation field {key!r} must be a list")
    return value


def maybe_set(target: dict[str, Any], key: str, value: Any) -> None:
    if value is not None:
        target[key] = value


def update_snapshot(
    observation: dict[str, Any],
    *,
    label: str,
    path: str | None,
    capture_point: str | None,
) -> None:
    snapshots = ensure_list(observation, "snapshots")
    for entry in snapshots:
        if isinstance(entry, dict) and str(entry.get("label")) == label:
            maybe_set(entry, "path", path)
            maybe_set(entry, "capture_point", capture_point)
            return

    snapshots.append(
        {
            "label": label,
            "path": path,
            "capture_point": capture_point,
        }
    )


def add_breakpoint_hit(
    observation: dict[str, Any],
    *,
    kind: str,
    address: str | None,
    address_range: str | None,
    hit_count: int | None,
    pc: str | None,
    note: str | None,
    timestamp: str | None,
) -> None:
    hits = ensure_list(observation, "breakpoint_hits")
    entry = {
        "kind": kind,
        "timestamp": timestamp or utc_now(),
    }
    maybe_set(entry, "address", address)
    maybe_set(entry, "address_range", address_range)
    maybe_set(entry, "hit_count", hit_count)
    maybe_set(entry, "pc", pc)
    maybe_set(entry, "note", note)
    hits.append(entry)


def add_dispatch_observation(
    observation: dict[str, Any],
    *,
    opcode: str,
    handler_address: str,
    source_breakpoint: str | None,
    snapshot_label: str | None,
    note: str | None,
    timestamp: str | None,
) -> None:
    observations = ensure_list(observation, "dispatch_observations")
    entry = {
        "opcode": opcode,
        "handler_address": handler_address,
        "timestamp": timestamp or utc_now(),
    }
    maybe_set(entry, "source_breakpoint", source_breakpoint)
    maybe_set(entry, "snapshot_label", snapshot_label)
    maybe_set(entry, "note", note)
    observations.append(entry)


def add_table_mutation(
    observation: dict[str, Any],
    *,
    opcode: str,
    old_handler: str,
    new_handler: str,
    snapshot_label: str | None,
    snapshot_path: str | None,
    note: str | None,
    timestamp: str | None,
    source: str | None = None,
) -> None:
    mutations = ensure_list(observation, "table_mutations")
    entry = {
        "opcode": opcode,
        "old_handler": old_handler,
        "new_handler": new_handler,
        "timestamp": timestamp or utc_now(),
    }
    maybe_set(entry, "snapshot_label", snapshot_label)
    maybe_set(entry, "snapshot_path", snapshot_path)
    maybe_set(entry, "note", note)
    maybe_set(entry, "source", source)
    mutations.append(entry)


def add_note(observation: dict[str, Any], *, note: str, timestamp: str | None) -> None:
    notes = ensure_list(observation, "notes")
    notes.append(
        {
            "timestamp": timestamp or utc_now(),
            "text": note,
        }
    )


def maybe_reset_conclusion(observation: dict[str, Any]) -> None:
    observation["comparison_summary"] = None
    observation["conclusion"] = None


def maybe_finalize(
    *,
    script_path: Path,
    observation_path: Path,
    allow_missing_snapshots: bool,
) -> None:
    command = [sys.executable, str(script_path), str(observation_path), "--in-place"]
    if allow_missing_snapshots:
        command.append("--allow-missing-snapshots")
    subprocess.run(command, check=True)


def iter_compare_mutation_candidates(
    compare_report: dict[str, Any],
    *,
    include_non_focus: bool,
) -> list[dict[str, str | None]]:
    snapshots = compare_report.get("snapshots")
    if not isinstance(snapshots, list):
        raise ValueError("Compare report is missing a 'snapshots' list")

    candidates: list[dict[str, str | None]] = []
    for snapshot in snapshots:
        if not isinstance(snapshot, dict):
            continue
        snapshot_label = str(snapshot.get("label") or "unknown")
        snapshot_path = snapshot.get("path")
        rows = snapshot.get("changed_details")
        if not isinstance(rows, list):
            continue

        focus_rows: set[tuple[str, str, str]] = set()
        focus_entries = snapshot.get("focus_entries")
        if isinstance(focus_entries, list):
            for row in focus_entries:
                if not isinstance(row, dict) or not row.get("changed"):
                    continue
                focus_rows.add(
                    (
                        str(row.get("opcode") or ""),
                        str(row.get("expected_handler") or ""),
                        str(row.get("observed_handler") or ""),
                    )
                )

        for row in rows:
            if not isinstance(row, dict) or not row.get("changed"):
                continue

            opcode = str(row.get("opcode") or "")
            old_handler = str(row.get("expected_handler") or "")
            new_handler = str(row.get("observed_handler") or "")
            if not opcode or not old_handler or not new_handler:
                continue

            key = (opcode, old_handler, new_handler)
            if not include_non_focus and key not in focus_rows:
                continue

            candidates.append(
                {
                    "opcode": opcode,
                    "old_handler": old_handler,
                    "new_handler": new_handler,
                    "snapshot_label": snapshot_label,
                    "snapshot_path": str(snapshot_path) if snapshot_path is not None else None,
                    "note": "Imported from runtime snapshot compare report.",
                }
            )

    return candidates


def mutation_exists(
    mutations: list[Any],
    *,
    opcode: str,
    old_handler: str,
    new_handler: str,
    snapshot_label: str | None,
    snapshot_path: str | None,
    source: str,
) -> bool:
    for entry in mutations:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("opcode")) != opcode:
            continue
        if str(entry.get("old_handler")) != old_handler:
            continue
        if str(entry.get("new_handler")) != new_handler:
            continue
        if str(entry.get("source")) != source:
            continue
        if snapshot_label is not None and str(entry.get("snapshot_label")) != snapshot_label:
            continue
        if snapshot_path is not None and str(entry.get("snapshot_path")) != snapshot_path:
            continue
        return True
    return False


def clear_compare_report_mutations(observation: dict[str, Any]) -> int:
    mutations = ensure_list(observation, "table_mutations")
    kept = [
        entry
        for entry in mutations
        if not (isinstance(entry, dict) and str(entry.get("source")) == "compare_report")
    ]
    removed = len(mutations) - len(kept)
    observation["table_mutations"] = kept
    return removed


def import_compare_mutations(
    observation: dict[str, Any],
    *,
    compare_report_path: Path,
    include_non_focus: bool,
    replace_derived: bool,
    timestamp: str | None,
) -> tuple[int, int, int]:
    compare_report = load_json(compare_report_path)
    candidates = iter_compare_mutation_candidates(
        compare_report,
        include_non_focus=include_non_focus,
    )

    removed = 0
    if replace_derived:
        removed = clear_compare_report_mutations(observation)

    mutations = ensure_list(observation, "table_mutations")
    imported = 0
    skipped = 0
    for candidate in candidates:
        if mutation_exists(
            mutations,
            opcode=str(candidate["opcode"]),
            old_handler=str(candidate["old_handler"]),
            new_handler=str(candidate["new_handler"]),
            snapshot_label=(
                str(candidate["snapshot_label"])
                if candidate["snapshot_label"] is not None
                else None
            ),
            snapshot_path=(
                str(candidate["snapshot_path"])
                if candidate["snapshot_path"] is not None
                else None
            ),
            source="compare_report",
        ):
            skipped += 1
            continue

        add_table_mutation(
            observation,
            opcode=str(candidate["opcode"]),
            old_handler=str(candidate["old_handler"]),
            new_handler=str(candidate["new_handler"]),
            snapshot_label=(
                str(candidate["snapshot_label"])
                if candidate["snapshot_label"] is not None
                else None
            ),
            snapshot_path=(
                str(candidate["snapshot_path"])
                if candidate["snapshot_path"] is not None
                else None
            ),
            note=str(candidate["note"]) if candidate["note"] is not None else None,
            timestamp=timestamp,
            source="compare_report",
        )
        imported += 1

    return imported, skipped, removed


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Record breakpoint hits, snapshot paths, dispatches, and notes into a "
            "checked-in runtime observation packet."
        )
    )
    parser.add_argument(
        "observation_json",
        type=Path,
        help="Checked-in runtime observation JSON to update in place.",
    )
    event_parent = argparse.ArgumentParser(add_help=False)
    event_parent.add_argument(
        "--timestamp",
        help="Optional UTC timestamp override, for example 2026-04-30T20:12:00Z.",
    )
    event_parent.add_argument(
        "--finalize",
        action="store_true",
        help="Rerun finalize_runtime_observation.py after recording this event.",
    )
    event_parent.add_argument(
        "--allow-missing-snapshots",
        action="store_true",
        help="Pass through to the finalize helper when --finalize is used.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser(
        "set-snapshot",
        parents=[event_parent],
        help="Create or update a named snapshot entry.",
    )
    snapshot_parser.add_argument("--label", required=True, help="Snapshot label.")
    snapshot_parser.add_argument("--path", help="Repo-relative or absolute dump path.")
    snapshot_parser.add_argument(
        "--capture-point",
        help="Short description of when the dump was captured.",
    )

    hit_parser = subparsers.add_parser(
        "add-breakpoint-hit",
        parents=[event_parent],
        help="Append one observed breakpoint hit.",
    )
    hit_parser.add_argument("--kind", required=True, help="Breakpoint kind, for example exec or write.")
    hit_parser.add_argument("--address", help="Single breakpoint address such as 0x800BFBB8.")
    hit_parser.add_argument(
        "--address-range",
        help="Range breakpoint such as 0x800F4C28-0x800F5027.",
    )
    hit_parser.add_argument("--hit-count", type=int, help="Observed hit count.")
    hit_parser.add_argument("--pc", help="Program counter when the hit was observed.")
    hit_parser.add_argument("--note", help="Short note to keep with the hit.")

    dispatch_parser = subparsers.add_parser(
        "add-dispatch",
        parents=[event_parent],
        help="Append one opcode dispatch observation.",
    )
    dispatch_parser.add_argument("--opcode", required=True, help="Opcode value, for example 0x80.")
    dispatch_parser.add_argument(
        "--handler-address",
        required=True,
        help="Observed dispatched handler address.",
    )
    dispatch_parser.add_argument(
        "--source-breakpoint",
        help="Breakpoint or function that surfaced the dispatch.",
    )
    dispatch_parser.add_argument(
        "--snapshot-label",
        help="Optional snapshot label that matches this observation.",
    )
    dispatch_parser.add_argument("--note", help="Short note to keep with the dispatch.")

    mutation_parser = subparsers.add_parser(
        "add-mutation",
        parents=[event_parent],
        help="Append one opcode-table mutation observation.",
    )
    mutation_parser.add_argument("--opcode", required=True, help="Opcode value, for example 0x80.")
    mutation_parser.add_argument("--old-handler", required=True, help="Previous handler address.")
    mutation_parser.add_argument("--new-handler", required=True, help="New handler address.")
    mutation_parser.add_argument("--snapshot-label", help="Snapshot label tied to this mutation.")
    mutation_parser.add_argument("--snapshot-path", help="Snapshot path tied to this mutation.")
    mutation_parser.add_argument("--note", help="Short note to keep with the mutation.")

    note_parser = subparsers.add_parser(
        "add-note",
        parents=[event_parent],
        help="Append one free-form runtime note.",
    )
    note_parser.add_argument("--note", required=True, help="Note text to append.")

    compare_parser = subparsers.add_parser(
        "import-compare",
        parents=[event_parent],
        help="Import changed opcode rows from a snapshot compare report into table_mutations.",
    )
    compare_parser.add_argument(
        "--compare-report",
        help=(
            "Compare report JSON to import from. Defaults to compare_report_path "
            "inside the observation JSON."
        ),
    )
    compare_parser.add_argument(
        "--include-non-focus",
        action="store_true",
        help="Import every changed opcode row, not just changed focus-opcode rows.",
    )
    compare_parser.add_argument(
        "--replace-derived",
        action="store_true",
        help="Drop existing compare-report-derived table_mutations before reimporting.",
    )

    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    observation_path = args.observation_json.resolve()
    observation = load_json(observation_path)

    # Once a human records fresh runtime facts, clear the stale generated summary
    # so the next finalize pass cannot be mistaken for current state.
    maybe_reset_conclusion(observation)

    repo_root = Path(__file__).resolve().parents[2]
    import_summary: tuple[int, int, int] | None = None

    if args.command == "set-snapshot":
        update_snapshot(
            observation,
            label=args.label,
            path=args.path,
            capture_point=args.capture_point,
        )
    elif args.command == "add-breakpoint-hit":
        if not args.address and not args.address_range:
            parser.error("add-breakpoint-hit requires --address or --address-range.")
        add_breakpoint_hit(
            observation,
            kind=args.kind,
            address=args.address,
            address_range=args.address_range,
            hit_count=args.hit_count,
            pc=args.pc,
            note=args.note,
            timestamp=args.timestamp,
        )
    elif args.command == "add-dispatch":
        add_dispatch_observation(
            observation,
            opcode=args.opcode,
            handler_address=args.handler_address,
            source_breakpoint=args.source_breakpoint,
            snapshot_label=args.snapshot_label,
            note=args.note,
            timestamp=args.timestamp,
        )
    elif args.command == "add-mutation":
        add_table_mutation(
            observation,
            opcode=args.opcode,
            old_handler=args.old_handler,
            new_handler=args.new_handler,
            snapshot_label=args.snapshot_label,
            snapshot_path=args.snapshot_path,
            note=args.note,
            timestamp=args.timestamp,
        )
    elif args.command == "add-note":
        add_note(observation, note=args.note, timestamp=args.timestamp)
    elif args.command == "import-compare":
        compare_report_path = (
            resolve_repo_path(args.compare_report, repo_root)
            if args.compare_report
            else resolve_repo_path(
                observation.get("compare_report_path")
                if isinstance(observation.get("compare_report_path"), str)
                else None,
                repo_root,
            )
        )
        if compare_report_path is None:
            parser.error(
                "import-compare requires --compare-report or a compare_report_path "
                "field in the observation JSON."
            )
        if not compare_report_path.exists():
            parser.error(f"Compare report does not exist: {compare_report_path}")
        import_summary = import_compare_mutations(
            observation,
            compare_report_path=compare_report_path,
            include_non_focus=args.include_non_focus,
            replace_derived=args.replace_derived,
            timestamp=args.timestamp,
        )
    else:
        parser.error(f"Unsupported command: {args.command}")

    write_json(observation_path, observation)
    print(f"updated observation JSON at {observation_path}")
    if import_summary is not None:
        imported, skipped, removed = import_summary
        print(
            "imported "
            f"{imported} compare-derived mutation(s), skipped {skipped} duplicate(s), "
            f"removed {removed} previous compare-derived mutation(s)"
        )

    if args.finalize:
        finalize_helper = observation.get("finalize_helper")
        finalize_path = (
            (repo_root / finalize_helper).resolve()
            if isinstance(finalize_helper, str) and finalize_helper
            else Path(__file__).resolve().with_name("finalize_runtime_observation.py")
        )
        maybe_finalize(
            script_path=finalize_path,
            observation_path=observation_path,
            allow_missing_snapshots=args.allow_missing_snapshots,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
