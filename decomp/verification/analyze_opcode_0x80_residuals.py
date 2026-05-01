#!/usr/bin/env python3
"""Analyze decoded-script files whose first 0x80 lacks an in-file sound pair."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


LINE_RE = re.compile(
    r"^([0-9A-Fa-f]{4}):\s+((?:[0-9A-Fa-f]{2}\s+){0,15}[0-9A-Fa-f]{2})"
)
PAIR_DEFS = {
    "sfx_pair": (0x85, 0x88),
    "music_pair": (0x90, 0x92),
    "queue_pair": (0x9D, 0x9E),
}
FAMILY_DEFS = {
    "sfx_family": (0x85, 0x86, 0x87, 0x88, 0x89),
    "music_family": (0x90, 0x91, 0x92, 0x99),
    "queue_family": (0x9D, 0x9E),
}


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
            "Scan decoded_scripts for files whose first opcode 0x80 appears "
            "before any complete neighboring sound-family pair."
        )
    )
    parser.add_argument(
        "--decoded-root",
        type=Path,
        default=Path("decoded_scripts"),
        help="Directory containing decoded MAP script text files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("decomp/evidence/opcode_0x80_residual_scan.json"),
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


def opcodes_present(lines: Iterable[ParsedLine]) -> set[int]:
    return {line.opcode for line in lines}


def family_hits(lines: Iterable[ParsedLine]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for family_name, members in FAMILY_DEFS.items():
        values = [f"0x{member:02X}" for member in members if any(line.opcode == member for line in lines)]
        if values:
            hits[family_name] = values
    return hits


def complete_pairs(lines: Iterable[ParsedLine]) -> list[str]:
    present = opcodes_present(lines)
    return [
        pair_name
        for pair_name, members in PAIR_DEFS.items()
        if set(members).issubset(present)
    ]


def normalize_title(stem: str) -> str:
    if "-" in stem:
        _, title = stem.split("-", 1)
    else:
        title = stem
    title = re.sub(r"\s*\([^)]*\)", "", title)
    return title.strip().lower()


def build_residual_records(repo_root: Path, decoded_root: Path) -> list[dict[str, object]]:
    all_scripts: list[dict[str, object]] = []
    title_groups: defaultdict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)

    for script_path in sorted(decoded_root.rglob("*.txt")):
        parsed = parse_script(script_path)
        first_0x80_index = next(
            (index for index, line in enumerate(parsed) if line.opcode == 0x80),
            None,
        )
        if first_0x80_index is None:
            continue

        before = parsed[:first_0x80_index]
        after = parsed[first_0x80_index + 1 :]
        record = {
            "path": script_path.relative_to(repo_root).as_posix(),
            "area": script_path.parent.name,
            "title_normalized": normalize_title(script_path.stem),
            "first_0x80_index": first_0x80_index,
            "first_0x80_address": f"0x{parsed[first_0x80_index].address:04X}",
            "first_0x80_bytes": parsed[first_0x80_index].raw_hex,
            "before_complete_pairs": complete_pairs(before),
            "before_family_hits": family_hits(before),
            "after_complete_pairs": complete_pairs(after),
            "after_family_hits": family_hits(after),
            "context_before": [line.text for line in parsed[max(0, first_0x80_index - 3) : first_0x80_index]],
            "context_at_and_after": [
                line.text for line in parsed[first_0x80_index : min(len(parsed), first_0x80_index + 4)]
            ],
            "previous_opcodes": [
                f"0x{line.opcode:02X}" for line in parsed[max(0, first_0x80_index - 3) : first_0x80_index]
            ],
            "next_opcodes": [
                f"0x{line.opcode:02X}" for line in parsed[first_0x80_index + 1 : min(len(parsed), first_0x80_index + 4)]
            ],
        }
        next_line = parsed[first_0x80_index + 1] if first_0x80_index + 1 < len(parsed) else None
        if next_line and next_line.opcode == 0x80:
            record["immediate_next_0x80_bytes"] = next_line.raw_hex
        all_scripts.append(record)
        title_groups[(record["area"], record["title_normalized"])].append(record)

    residual_records: list[dict[str, object]] = []
    for record in all_scripts:
        if record["before_complete_pairs"]:
            continue
        siblings = []
        for sibling in title_groups[(record["area"], record["title_normalized"])]:
            if sibling["path"] == record["path"]:
                continue
            if sibling["before_complete_pairs"]:
                siblings.append(
                    {
                        "path": sibling["path"],
                        "first_0x80_address": sibling["first_0x80_address"],
                        "before_complete_pairs": sibling["before_complete_pairs"],
                        "first_0x80_bytes": sibling["first_0x80_bytes"],
                    }
                )
        if siblings:
            record["same_title_variants_with_complete_pairs"] = siblings
        residual_records.append(record)

    return residual_records


def summarize_residuals(records: list[dict[str, object]]) -> dict[str, object]:
    first_signature_counts = Counter(record["first_0x80_bytes"] for record in records)
    paired_signature_counts = Counter(
        (
            record["first_0x80_bytes"],
            record.get("immediate_next_0x80_bytes"),
        )
        for record in records
    )
    previous_opcode_counts = Counter(tuple(record["previous_opcodes"]) for record in records)
    next_opcode_counts = Counter(tuple(record["next_opcodes"]) for record in records)
    area_counts = Counter(record["area"] for record in records)
    family_before_counts = Counter(
        family_name
        for record in records
        for family_name in record["before_family_hits"]
    )
    family_after_counts = Counter(
        family_name
        for record in records
        for family_name in record["after_family_hits"]
    )
    later_pair_counts = Counter(
        pair_name
        for record in records
        for pair_name in record["after_complete_pairs"]
    )

    no_family_before_count = sum(1 for record in records if not record["before_family_hits"])
    no_family_anywhere_count = sum(
        1 for record in records if not record["before_family_hits"] and not record["after_family_hits"]
    )
    same_title_variant_paths = [
        {
            "path": record["path"],
            "variants": record["same_title_variants_with_complete_pairs"],
        }
        for record in records
        if "same_title_variants_with_complete_pairs" in record
    ]
    later_pair_records = [
        {
            "path": record["path"],
            "after_complete_pairs": record["after_complete_pairs"],
            "after_family_hits": record["after_family_hits"],
        }
        for record in records
        if record["after_complete_pairs"]
    ]

    return {
        "residual_file_count": len(records),
        "files_with_no_sound_family_before_first_0x80": no_family_before_count,
        "files_with_no_sound_family_anywhere_in_file": no_family_anywhere_count,
        "files_with_later_complete_pair_after_first_0x80": len(later_pair_records),
        "later_complete_pair_counts": dict(sorted(later_pair_counts.items())),
        "first_0x80_signature_counts": dict(sorted(first_signature_counts.items())),
        "paired_immediate_0x80_signature_counts": {
            " | ".join(part for part in signature if part): count
            for signature, count in sorted(paired_signature_counts.items())
        },
        "previous_opcode_triplet_counts": {
            " ".join(values): count for values, count in sorted(previous_opcode_counts.items())
        },
        "next_opcode_triplet_counts": {
            " ".join(values): count for values, count in sorted(next_opcode_counts.items())
        },
        "area_counts": dict(sorted(area_counts.items())),
        "family_before_first_0x80_counts": dict(sorted(family_before_counts.items())),
        "family_after_first_0x80_counts": dict(sorted(family_after_counts.items())),
        "same_title_variant_matches": same_title_variant_paths,
        "later_complete_pair_records": later_pair_records,
    }


def main() -> None:
    args = parse_args()
    repo_root = Path.cwd().resolve()
    decoded_root = args.decoded_root.resolve()
    output_path = args.output.resolve()
    records = build_residual_records(repo_root=repo_root, decoded_root=decoded_root)
    payload = {
        "target": "opcode 0x80",
        "analysis": "residual first-0x80 files without an in-file complete neighboring sound pair",
        "decoded_root": decoded_root.as_posix(),
        "summary": summarize_residuals(records),
        "records": records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
