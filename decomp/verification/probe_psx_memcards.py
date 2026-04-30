#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


DEFAULT_KEYWORDS = (
    "VAGRANT",
    "STORY",
    "SLUS",
    "SCUS",
    "SLPS",
    "SQUARE",
)


def find_ascii_runs(data: bytes, min_length: int = 4) -> list[str]:
    runs: list[str] = []
    current = bytearray()
    for byte in data:
        if 32 <= byte <= 126:
            current.append(byte)
            continue
        if len(current) >= min_length:
            runs.append(current.decode("ascii", errors="ignore"))
        current = bytearray()
    if len(current) >= min_length:
        runs.append(current.decode("ascii", errors="ignore"))
    return runs


def unique_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def summarize_card(path: Path, keywords: tuple[str, ...]) -> dict[str, object]:
    data = path.read_bytes()
    nonzero_offsets = [index for index, byte in enumerate(data) if byte != 0]
    ascii_runs = find_ascii_runs(data)

    keyword_matches: list[str] = []
    for run in ascii_runs:
        upper = run.upper()
        if any(keyword in upper for keyword in keywords):
            keyword_matches.append(run)

    matches = unique_preserve_order(keyword_matches)
    highest_nonzero_offset = nonzero_offsets[-1] if nonzero_offsets else None
    blank_formatted_heuristic = (
        len(data) == 131072
        and len(nonzero_offsets) <= 256
        and highest_nonzero_offset is not None
        and highest_nonzero_offset < 0x2000
        and len(matches) == 0
    )

    return {
        "path": str(path),
        "size_bytes": len(data),
        "nonzero_byte_count": len(nonzero_offsets),
        "highest_nonzero_offset": (
            f"0x{highest_nonzero_offset:04X}" if highest_nonzero_offset is not None else None
        ),
        "ascii_match_count": len(matches),
        "ascii_matches": matches[:32],
        "looks_blank_formatted": blank_formatted_heuristic,
    }


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit a lightweight heuristic summary of one or more PS1 memory card files "
            "for runtime-capture route planning."
        )
    )
    parser.add_argument("cards", nargs="+", type=Path, help="Memory card file(s) to inspect.")
    parser.add_argument(
        "--keyword",
        action="append",
        default=[],
        help="Additional ASCII keyword to search for inside card payloads.",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    keywords = tuple(DEFAULT_KEYWORDS + tuple(args.keyword))
    reports = [summarize_card(card.resolve(), keywords) for card in args.cards]
    payload = {
        "keywords": list(keywords),
        "cards": reports,
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
