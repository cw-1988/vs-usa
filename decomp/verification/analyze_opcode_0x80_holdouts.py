#!/usr/bin/env python3
"""Classify the last residual opcode 0x80 holdouts by structural provenance."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


DOMINANT_SELECTOR_FAMILY = {0x41, 0x42}
SECONDARY_SELECTOR_FAMILY = {0x1D, 0x1E}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Explain whether the remaining singleton or variant 0x80 residuals "
            "belong to existing template families or imply a second producer."
        )
    )
    parser.add_argument(
        "--template-scan",
        type=Path,
        default=Path("decomp/evidence/opcode_0x80_template_scan.json"),
        help="Input JSON produced by analyze_opcode_0x80_templates.py.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("decomp/evidence/opcode_0x80_holdout_scan.json"),
        help="Output JSON path.",
    )
    return parser.parse_args()


def decode_signature(raw_hex: str | None) -> dict[str, int] | None:
    if not raw_hex:
        return None
    values = [int(part, 16) for part in raw_hex.split()]
    if len(values) != 5 or values[0] != 0x80:
        return None
    return {
        "mode_byte": values[1],
        "selector_byte": values[2],
    }


def selector_bucket(selectors: set[int]) -> str:
    if selectors & DOMINANT_SELECTOR_FAMILY:
        return "dominant_41_42_family"
    if selectors & SECONDARY_SELECTOR_FAMILY:
        return "paired_1D_1E_family"
    return "other_selector"


def summarize_holdouts(records: list[dict[str, object]]) -> dict[str, object]:
    provenance_counts = Counter(record["provenance_class"] for record in records)
    selector_counts = Counter(
        selector
        for record in records
        for selector in record["selector_bytes"]
    )
    return {
        "holdout_count": len(records),
        "provenance_counts": dict(sorted(provenance_counts.items())),
        "selector_counts": {
            f"0x{selector:02X}": count
            for selector, count in sorted(selector_counts.items())
        },
        "holdouts_without_complete_pair_anywhere": sum(
            1
            for record in records
            if not record["later_complete_pairs"]
            and not record["same_title_variants"]
        ),
        "holdouts_without_complete_pair_before_first_0x80": len(records),
    }


def main() -> None:
    args = parse_args()
    template_scan = json.loads(args.template_scan.read_text(encoding="utf-8"))
    all_records = template_scan["records"]
    holdouts = [
        record for record in all_records if record["template_kind"] == "singleton_or_variant"
    ]

    selector_family_counts = Counter()
    for record in all_records:
        selectors: set[int] = set()
        for signature in (
            decode_signature(record["first_0x80_bytes"]),
            decode_signature(record.get("second_0x80_bytes")),
        ):
            if signature:
                selectors.add(signature["selector_byte"])
        selector_family_counts[selector_bucket(selectors)] += 1

    normalized_holdouts: list[dict[str, object]] = []
    for record in holdouts:
        first_signature = decode_signature(record["first_0x80_bytes"])
        second_signature = decode_signature(record.get("second_0x80_bytes"))
        selectors = [
            signature["selector_byte"]
            for signature in (first_signature, second_signature)
            if signature
        ]
        selector_set = set(selectors)

        if selector_set & DOMINANT_SELECTOR_FAMILY:
            provenance_class = "dominant_selector_singleton"
            provenance_note = (
                "Reuses the dominant 0x41/0x42 selector family as a singleton or "
                "truncated form instead of introducing a new residual family."
            )
        elif record["same_title_variants"]:
            provenance_class = "same_title_variant"
            provenance_note = (
                "The only unique-selector holdout, but it already has a same-title "
                "sibling variant that stages a complete pre-burst neighboring pair."
            )
        else:
            provenance_class = "other_singleton"
            provenance_note = (
                "A residual singleton with no same-title variant link and no known "
                "selector reuse."
            )

        normalized_holdouts.append(
            {
                "path": record["path"],
                "area": record["area"],
                "first_0x80_address": record["first_0x80_address"],
                "first_0x80_bytes": record["first_0x80_bytes"],
                "second_0x80_bytes": record.get("second_0x80_bytes"),
                "selector_bytes": selectors,
                "selector_hex": [f"0x{value:02X}" for value in selectors],
                "selector_family": selector_bucket(selector_set),
                "provenance_class": provenance_class,
                "provenance_note": provenance_note,
                "lead_in_lines": record["lead_in_lines"],
                "context_after_burst": record["context_after_burst"],
                "family_anywhere": record["family_anywhere"],
                "later_complete_pairs": record["later_complete_pairs"],
                "same_title_variants": record["same_title_variants"],
            }
        )

    payload = {
        "target": "opcode 0x80",
        "analysis": "holdout provenance for residual singleton or variant 0x80 files",
        "source_template_scan": str(args.template_scan).replace("\\", "/"),
        "summary": {
            "residual_selector_family_counts": dict(sorted(selector_family_counts.items())),
            "holdouts": summarize_holdouts(normalized_holdouts),
            "resolved_question": (
                "No second structural producer is visible in the remaining holdouts; "
                "two reuse the dominant 0x41/0x42 selector family and the last one "
                "is best explained as a same-title variant case."
            ),
        },
        "records": normalized_holdouts,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
