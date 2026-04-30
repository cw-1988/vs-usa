#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return payload


def parse_int(value: Any) -> int:
    return int(str(value), 0)


def to_hex(value: int, digits: int = 8) -> str:
    return f"0x{value:0{digits}X}"


def load_compare_module(script_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(
        "compare_opcode_table_snapshots", script_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load compare helper from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_repo_path(raw_path: str | None, repo_root: Path) -> Path | None:
    if raw_path is None:
        return None
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (repo_root / path).resolve()


def format_repo_path(path: Path | None, repo_root: Path) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve_output_path(
    explicit_path: str | Path | None,
    observation: dict[str, Any],
    *,
    observation_path: Path,
    repo_root: Path,
    template_key: str,
    fallback_suffix: str,
) -> Path:
    if explicit_path is not None:
        path = Path(explicit_path)
        return path if path.is_absolute() else (repo_root / path).resolve()

    template_value = observation.get(template_key)
    if isinstance(template_value, str) and template_value:
        return resolve_repo_path(template_value, repo_root)  # type: ignore[return-value]

    stem = observation_path.stem
    if stem.endswith("_template"):
        stem = stem[: -len("_template")]
    return observation_path.with_name(f"{stem}{fallback_suffix}").resolve()


def collect_snapshots(
    observation: dict[str, Any],
    *,
    repo_root: Path,
    allow_missing_snapshots: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_snapshots = observation.get("snapshots")
    if not isinstance(raw_snapshots, list) or not raw_snapshots:
        raise ValueError("Observation JSON must contain a non-empty 'snapshots' list")

    available: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []

    for index, entry in enumerate(raw_snapshots):
        if not isinstance(entry, dict):
            raise ValueError(f"Snapshot entry {index} is not an object")

        label = str(entry.get("label") or f"snapshot_{index}")
        raw_path = entry.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            raise ValueError(f"Snapshot entry {label!r} is missing a string 'path'")

        resolved_path = resolve_repo_path(raw_path, repo_root)
        record = {
            "index": index,
            "label": label,
            "path": raw_path,
            "resolved_path": format_repo_path(resolved_path, repo_root),
            "capture_point": entry.get("capture_point"),
            "compare_report_path": entry.get("compare_report_path"),
        }

        if resolved_path is None or not resolved_path.exists():
            missing.append(record)
            continue

        available.append(record)

    if missing and not allow_missing_snapshots:
        missing_list = ", ".join(item["path"] for item in missing)
        raise FileNotFoundError(
            "Missing snapshot file(s). Re-run with --allow-missing-snapshots to "
            f"finalize a partial observation set: {missing_list}"
        )

    return available, missing


def build_compare_report(
    observation: dict[str, Any],
    *,
    observation_path: Path,
    repo_root: Path,
    compare_module: Any,
    expected_bin_path: Path | None,
    allow_missing_snapshots: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    baseline_export = observation.get("baseline_export")
    if not isinstance(baseline_export, str) or not baseline_export:
        raise ValueError("Observation JSON is missing 'baseline_export'")

    export_path = resolve_repo_path(baseline_export, repo_root)
    compare_payload = compare_module.load_export(export_path)
    pointer_size = int(compare_payload.get("pointer_size", 4))
    entries = compare_module.normalize_entries(compare_payload)
    expected_blob = compare_module.build_expected_blob(entries, pointer_size)
    expected_size = len(expected_blob)

    if expected_bin_path is not None:
        expected_bin_path.parent.mkdir(parents=True, exist_ok=True)
        expected_bin_path.write_bytes(expected_blob)

    focus_opcodes = observation.get("focus_opcodes")
    if not isinstance(focus_opcodes, list) or not focus_opcodes:
        focus_opcode_values = {0x80, 0x81, 0x82}
    else:
        focus_opcode_values = {parse_int(value) & 0xFF for value in focus_opcodes}

    handler_to_opcodes: dict[int, list[int]] = {}
    for entry in entries:
        handler_to_opcodes.setdefault(entry["handler_address"], []).append(entry["opcode"])

    available_snapshots, missing_snapshots = collect_snapshots(
        observation,
        repo_root=repo_root,
        allow_missing_snapshots=allow_missing_snapshots,
    )

    compared_snapshots: list[dict[str, Any]] = []
    for snapshot in available_snapshots:
        compared = compare_module.summarize_snapshot(
            resolve_repo_path(snapshot["resolved_path"], repo_root),
                label=snapshot["label"],
                entries=entries,
                focus_opcodes=focus_opcode_values,
                handler_to_opcodes=handler_to_opcodes,
                expected_size=expected_size,
        )
        compared["path"] = snapshot["path"]
        compared_snapshots.append(compared)

    report = {
        "observation_source": format_repo_path(observation_path, repo_root),
        "baseline_export": baseline_export,
        "table_name": compare_payload.get("table_name"),
        "binary_table_address": compare_payload.get("table_address"),
        "runtime_table_address": observation.get("runtime_table_address"),
        "entry_count": len(entries),
        "pointer_size": pointer_size,
        "expected_size_bytes": expected_size,
        "focus_opcodes": [to_hex(opcode, digits=2) for opcode in sorted(focus_opcode_values)],
        "expected_bin_path": format_repo_path(expected_bin_path, repo_root),
        "snapshots": compared_snapshots,
        "missing_snapshots": missing_snapshots,
    }

    metadata = {
        "entries": entries,
        "focus_opcode_values": focus_opcode_values,
        "available_snapshots": available_snapshots,
        "missing_snapshots": missing_snapshots,
        "expected_size": expected_size,
    }
    return report, metadata


def build_focus_summary(compare_report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for snapshot in compare_report["snapshots"]:
        for row in snapshot["focus_entries"]:
            opcode = row["opcode"]
            item = summary.setdefault(
                opcode,
                {
                    "expected_handler": row["expected_handler"],
                    "observed_handlers": [],
                    "changed_in_snapshots": [],
                    "snapshot_details": [],
                },
            )

            observed_handler = row["observed_handler"]
            if observed_handler not in item["observed_handlers"]:
                item["observed_handlers"].append(observed_handler)

            if row["changed"]:
                item["changed_in_snapshots"].append(snapshot["label"])

            item["snapshot_details"].append(
                {
                    "label": snapshot["label"],
                    "observed_handler": observed_handler,
                    "changed": row["changed"],
                    "observed_matches_export_opcodes": row[
                        "observed_matches_export_opcodes"
                    ],
                }
            )

    return summary


def infer_conclusion(
    observation: dict[str, Any],
    *,
    compare_report: dict[str, Any],
    focus_summary: dict[str, dict[str, Any]],
) -> str:
    existing = observation.get("conclusion")
    if isinstance(existing, str) and existing.strip():
        return existing.strip()

    compared_snapshots = compare_report["snapshots"]
    missing_snapshots = compare_report["missing_snapshots"]
    any_changed_entries = any(snapshot["changed_entries"] > 0 for snapshot in compared_snapshots)
    any_focus_changes = any(item["changed_in_snapshots"] for item in focus_summary.values())

    if not compared_snapshots:
        if missing_snapshots:
            return (
                "Runtime observation packet is not finalized yet: no listed snapshot files "
                "were available for comparison."
            )
        return "Runtime observation packet exists, but no snapshot comparisons were recorded."

    if any_focus_changes:
        return (
            "Runtime snapshots diverged from the INITBTL baseline for at least one focus opcode; "
            "treat the copied opcode table as patched until the rewritten handlers are reviewed."
        )

    if any_changed_entries:
        return (
            "Runtime snapshots diverged from the INITBTL baseline outside the focus opcodes; "
            "inspect the comparison report before narrowing the 0x80-0x82 contradiction."
        )

    dispatch_observations = observation.get("dispatch_observations")
    if isinstance(dispatch_observations, list) and dispatch_observations:
        return (
            "Recorded runtime snapshots matched the INITBTL baseline, and dispatch observations "
            "can now be compared directly against the unchanged copied table."
        )

    return (
        "Recorded runtime snapshots matched the INITBTL baseline for every compared entry; "
        "explicit dispatch breakpoint results are still needed to finish the 0x80-0x82 tie-breaker."
    )


def render_breakpoint_lines(observation: dict[str, Any]) -> list[str]:
    hits = observation.get("breakpoint_hits")
    if not isinstance(hits, list) or not hits:
        return ["- No breakpoint hits were recorded in the observation JSON yet."]

    lines: list[str] = []
    for entry in hits:
        if not isinstance(entry, dict):
            continue
        kind = entry.get("kind", "unknown")
        address = entry.get("address") or entry.get("address_range") or "unknown"
        hit_count = entry.get("hit_count")
        note = entry.get("note")
        parts = [f"- `{kind}` breakpoint at `{address}`"]
        if hit_count is not None:
            parts.append(f"hit `{hit_count}` time(s)")
        if note:
            parts.append(str(note))
        lines.append(", ".join(parts))
    return lines or ["- No breakpoint hits were recorded in the observation JSON yet."]


def render_dispatch_lines(observation: dict[str, Any]) -> list[str]:
    observations = observation.get("dispatch_observations")
    if not isinstance(observations, list) or not observations:
        return ["- No dispatch observations were recorded yet."]

    lines: list[str] = []
    for entry in observations:
        if not isinstance(entry, dict):
            continue
        opcode = entry.get("opcode", "unknown")
        handler = entry.get("handler_address") or entry.get("observed_handler") or "unknown"
        note = entry.get("note")
        line = f"- Opcode `{opcode}` dispatched to `{handler}`"
        if note:
            line += f": {note}"
        lines.append(line)
    return lines or ["- No dispatch observations were recorded yet."]


def render_snapshot_lines(compare_report: dict[str, Any]) -> list[str]:
    snapshots = compare_report["snapshots"]
    missing = compare_report["missing_snapshots"]
    lines: list[str] = []

    for snapshot in snapshots:
        lines.append(
            "- "
            f"`{snapshot['label']}` compared `{snapshot['size_bytes']}` bytes: "
            f"`{snapshot['matching_entries']}` matching entries, "
            f"`{snapshot['changed_entries']}` changed entries"
        )

    for snapshot in missing:
        lines.append(
            f"- Missing snapshot file for `{snapshot['label']}`: `{snapshot['path']}`"
        )

    return lines or ["- No snapshot comparisons were generated."]


def render_focus_lines(focus_summary: dict[str, dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for opcode in sorted(focus_summary):
        item = focus_summary[opcode]
        observed = ", ".join(f"`{value}`" for value in item["observed_handlers"])
        changed = ", ".join(f"`{value}`" for value in item["changed_in_snapshots"])
        line = (
            f"- `{opcode}` expected `{item['expected_handler']}`; observed handlers: {observed}"
        )
        if changed:
            line += f"; changed in snapshots: {changed}"
        lines.append(line)
    return lines or ["- No focus-opcode comparison rows were available."]


def build_support_note(
    observation: dict[str, Any],
    *,
    compare_report: dict[str, Any],
    focus_summary: dict[str, dict[str, Any]],
    conclusion: str,
) -> str:
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%SZ")
    target = observation.get("target", "unknown target")
    phase = observation.get("phase", "unknown phase")

    lines = [
        f"# {target} Runtime Observation Support Note",
        "",
        "## Scope",
        "",
        f"- Generated from `{phase}` on `{generated_at}`.",
        f"- Observation source: `{compare_report['observation_source']}`",
        f"- Baseline export: `{compare_report['baseline_export']}`",
        f"- Runtime table address: `{compare_report['runtime_table_address']}`",
        "",
        "## Snapshot Comparison",
        "",
        *render_snapshot_lines(compare_report),
        "",
        "## Focus Opcode Summary",
        "",
        *render_focus_lines(focus_summary),
        "",
        "## Breakpoint Hits",
        "",
        *render_breakpoint_lines(observation),
        "",
        "## Dispatch Observations",
        "",
        *render_dispatch_lines(observation),
        "",
        "## Conclusion",
        "",
        conclusion,
        "",
    ]
    return "\n".join(lines)


def update_observation_payload(
    observation: dict[str, Any],
    *,
    compare_report: dict[str, Any],
    focus_summary: dict[str, dict[str, Any]],
    conclusion: str,
    compare_report_path: Path,
    support_note_path: Path,
    expected_bin_path: Path | None,
    repo_root: Path,
) -> dict[str, Any]:
    updated = dict(observation)
    updated["compare_report_path"] = format_repo_path(compare_report_path, repo_root)
    updated["support_note_path"] = format_repo_path(support_note_path, repo_root)
    if expected_bin_path is not None:
        updated["expected_bin_path"] = format_repo_path(expected_bin_path, repo_root)
    updated["comparison_summary"] = {
        "generated_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "compared_snapshot_count": len(compare_report["snapshots"]),
        "missing_snapshot_count": len(compare_report["missing_snapshots"]),
        "all_compared_snapshots_match_baseline": all(
            snapshot["changed_entries"] == 0 for snapshot in compare_report["snapshots"]
        )
        if compare_report["snapshots"]
        else False,
        "any_focus_opcode_changed": any(
            item["changed_in_snapshots"] for item in focus_summary.values()
        ),
        "focus_opcodes": focus_summary,
    }
    updated["conclusion"] = conclusion
    return updated


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Finalize a runtime observation packet by validating snapshot paths, "
            "running the opcode table compare helper, and generating a short "
            "support note."
        )
    )
    parser.add_argument(
        "observation_json",
        type=Path,
        help="Observation template or partially filled observation JSON.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root used to resolve repo-relative paths.",
    )
    parser.add_argument(
        "--compare-script",
        type=Path,
        default=Path(__file__).resolve().with_name("compare_opcode_table_snapshots.py"),
        help="Path to the snapshot compare helper.",
    )
    parser.add_argument(
        "--compare-report",
        type=Path,
        help="Optional JSON report path. Defaults to compare_report_path in the observation JSON or a derived sibling path.",
    )
    parser.add_argument(
        "--support-note",
        type=Path,
        help="Optional markdown note path. Defaults to support_note_path in the observation JSON or a derived sibling path.",
    )
    parser.add_argument(
        "--expected-bin",
        type=Path,
        help="Optional output path for the reconstructed baseline table bytes.",
    )
    parser.add_argument(
        "--output-observation",
        type=Path,
        help="Optional output path for the updated observation JSON. Defaults to stdout unless --in-place is set.",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write the updated observation JSON back to the input path.",
    )
    parser.add_argument(
        "--allow-missing-snapshots",
        action="store_true",
        help="Generate partial output even if some listed snapshot files do not exist yet.",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.in_place and args.output_observation is not None:
        parser.error("Use either --in-place or --output-observation, not both.")

    repo_root = args.repo_root.resolve()
    observation_path = args.observation_json.resolve()
    observation = load_json(observation_path)

    compare_module = load_compare_module(args.compare_script.resolve())

    compare_report_path = resolve_output_path(
        args.compare_report,
        observation,
        observation_path=observation_path,
        repo_root=repo_root,
        template_key="compare_report_path",
        fallback_suffix="_snapshot_compare.json",
    )
    support_note_path = resolve_output_path(
        args.support_note,
        observation,
        observation_path=observation_path,
        repo_root=repo_root,
        template_key="support_note_path",
        fallback_suffix="_support.md",
    )
    expected_bin_path = (
        resolve_repo_path(str(args.expected_bin), repo_root)
        if args.expected_bin is not None
        else None
    )

    compare_report, _metadata = build_compare_report(
        observation,
        observation_path=observation_path,
        repo_root=repo_root,
        compare_module=compare_module,
        expected_bin_path=expected_bin_path,
        allow_missing_snapshots=args.allow_missing_snapshots,
    )
    focus_summary = build_focus_summary(compare_report)
    conclusion = infer_conclusion(
        observation, compare_report=compare_report, focus_summary=focus_summary
    )
    support_note = build_support_note(
        observation,
        compare_report=compare_report,
        focus_summary=focus_summary,
        conclusion=conclusion,
    )
    updated_observation = update_observation_payload(
        observation,
        compare_report=compare_report,
        focus_summary=focus_summary,
        conclusion=conclusion,
        compare_report_path=compare_report_path,
        support_note_path=support_note_path,
        expected_bin_path=expected_bin_path,
        repo_root=repo_root,
    )

    write_json(compare_report_path, compare_report)
    support_note_path.parent.mkdir(parents=True, exist_ok=True)
    support_note_path.write_text(support_note, encoding="utf-8")

    observation_output = None
    if args.in_place:
        observation_output = observation_path
    elif args.output_observation is not None:
        observation_output = args.output_observation.resolve()

    rendered_observation = json.dumps(updated_observation, indent=2) + "\n"
    if observation_output is not None:
        observation_output.parent.mkdir(parents=True, exist_ok=True)
        observation_output.write_text(rendered_observation, encoding="utf-8")
    else:
        print(rendered_observation, end="")

    print(f"wrote compare report to {compare_report_path}")
    print(f"wrote support note to {support_note_path}")
    if observation_output is not None:
        print(f"wrote updated observation JSON to {observation_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
