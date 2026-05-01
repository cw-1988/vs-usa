#!/usr/bin/env python3
"""Classify the repeated residual template families around opcode 0x80."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


LINE_RE = re.compile(
    r"^([0-9A-Fa-f]{4}):\s+((?:[0-9A-Fa-f]{2}\s+){0,15}[0-9A-Fa-f]{2})"
)


@dataclass(frozen=True)
class ParsedLine:
    line_index: int
    address: int
    opcode: int
    raw_bytes: tuple[int, ...]
    text: str

    @property
    def raw_hex(self) -> str:
        return " ".join(f"{value:02X}" for value in self.raw_bytes)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Classify the repeated residual 0x80 template families and their "
            "surrounding opcode bundles."
        )
    )
    parser.add_argument(
        "--residual-scan",
        type=Path,
        default=Path("decomp/evidence/opcode_0x80_residual_scan.json"),
        help="Input JSON produced by analyze_opcode_0x80_residuals.py.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("decomp/evidence/opcode_0x80_template_scan.json"),
        help="Output JSON path.",
    )
    return parser.parse_args()


def parse_script(path: Path) -> list[ParsedLine]:
    parsed: list[ParsedLine] = []
    for line_index, line in enumerate(
        path.read_text(encoding="utf-8", errors="ignore").splitlines()
    ):
        match = LINE_RE.match(line)
        if not match:
            continue
        raw_bytes = tuple(int(part, 16) for part in match.group(2).split())
        parsed.append(
            ParsedLine(
                line_index=line_index,
                address=int(match.group(1), 16),
                opcode=raw_bytes[0],
                raw_bytes=raw_bytes,
                text=line.rstrip(),
            )
        )
    return parsed


def classify_template(first_hex: str, second_hex: str | None) -> str:
    if first_hex == "80 01 41 80 7F" and second_hex == "80 01 42 80 7F":
        return "paired_41_42"
    if first_hex == "80 01 1D 80 7F" and second_hex == "80 01 1E 80 7F":
        return "paired_1D_1E"
    return "singleton_or_variant"


def summarize_template(records: list[dict[str, object]]) -> dict[str, object]:
    lead_in_counts = Counter(
        " ".join(record["lead_in_opcodes"]) for record in records if record["lead_in_opcodes"]
    )
    post_burst_counts = Counter(
        " ".join(record["post_burst_opcodes"]) for record in records if record["post_burst_opcodes"]
    )
    immediate_follow_counts = Counter(
        " | ".join(record["context_after_burst"][:3])
        for record in records
        if record["context_after_burst"]
    )
    later_pair_count = sum(1 for record in records if record["later_complete_pairs"])
    same_title_variant_count = sum(1 for record in records if record["same_title_variants"])
    no_family_anywhere_count = sum(1 for record in records if not record["family_anywhere"])
    return {
        "file_count": len(records),
        "files_with_no_sound_family_anywhere": no_family_anywhere_count,
        "files_with_later_complete_pairs": later_pair_count,
        "files_with_same_title_variant_pairs": same_title_variant_count,
        "lead_in_counts": dict(sorted(lead_in_counts.items())),
        "post_burst_counts": dict(sorted(post_burst_counts.items())),
        "immediate_follow_context_counts": dict(sorted(immediate_follow_counts.items())),
        "representative_paths": [record["path"] for record in records[:5]],
    }


def main() -> None:
    args = parse_args()
    repo_root = Path.cwd().resolve()
    residual_scan = json.loads(args.residual_scan.read_text(encoding="utf-8"))
    grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    normalized_records: list[dict[str, object]] = []

    for record in residual_scan["records"]:
        script_path = repo_root / record["path"]
        parsed = parse_script(script_path)
        first_index = int(record["first_0x80_index"])
        first_line = parsed[first_index]
        second_line = parsed[first_index + 1] if first_index + 1 < len(parsed) else None
        second_hex = second_line.raw_hex if second_line and second_line.opcode == 0x80 else None
        template_kind = classify_template(first_line.raw_hex, second_hex)
        burst_end_index = first_index + 2 if second_hex is not None else first_index + 1

        normalized = {
            "path": record["path"],
            "area": record["area"],
            "first_0x80_address": record["first_0x80_address"],
            "first_0x80_bytes": first_line.raw_hex,
            "second_0x80_bytes": second_hex,
            "template_kind": template_kind,
            "lead_in_opcodes": [f"0x{line.opcode:02X}" for line in parsed[max(0, first_index - 3) : first_index]],
            "lead_in_lines": [line.text for line in parsed[max(0, first_index - 3) : first_index]],
            "context_after_burst": [
                line.text for line in parsed[burst_end_index : min(len(parsed), burst_end_index + 5)]
            ],
            "post_burst_opcodes": [
                f"0x{line.opcode:02X}"
                for line in parsed[burst_end_index : min(len(parsed), burst_end_index + 5)]
            ],
            "family_anywhere": sorted(
                set(record["before_family_hits"]).union(record["after_family_hits"])
            ),
            "later_complete_pairs": record["after_complete_pairs"],
            "same_title_variants": record.get("same_title_variants_with_complete_pairs", []),
        }
        grouped[template_kind].append(normalized)
        normalized_records.append(normalized)

    summary = {
        "template_counts": {
            key: len(grouped[key]) for key in sorted(grouped.keys())
        },
        "templates": {
            key: summarize_template(grouped[key]) for key in sorted(grouped.keys())
        },
    }
    payload = {
        "target": "opcode 0x80",
        "analysis": "template clustering for residual first-0x80 files",
        "source_residual_scan": str(args.residual_scan).replace("\\", "/"),
        "summary": summary,
        "records": normalized_records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
