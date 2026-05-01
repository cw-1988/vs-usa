#!/usr/bin/env python3
"""Audit minority scene-local consumer paths around opcode 0x80."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


LINE_RE = re.compile(
    r"^([0-9A-Fa-f]{4}):\s+((?:[0-9A-Fa-f]{2}\s+){0,15}[0-9A-Fa-f]{2})"
)
PAIR_DEFS = {
    "sfx_pair": (0x85, 0x88),
    "music_pair": (0x90, 0x92),
    "queue_pair": (0x9D, 0x9E),
}
SOUND_OPCODES = {0x85, 0x86, 0x88, 0x90, 0x92, 0x99, 0x9D, 0x9E}
TARGET_SCENES = [
    {
        "scene_id": "MAP290",
        "path": "decoded_scripts/14-Abandoned Mines B2/290-Dining in Darkness.txt",
        "scene_class": "template_then_later_consumer",
        "focus": (
            "Dominant 0x41/0x42 opener with no prior sound-family setup, then later "
            "0x80 bursts wrapped by explicit neighboring SFX, queue, and music state."
        ),
    },
    {
        "scene_id": "MAP334",
        "path": "decoded_scripts/18-Limestone Quarry/334-Torture Without End.txt",
        "scene_class": "template_then_later_consumer",
        "focus": (
            "Dominant 0x41/0x42 opener followed almost immediately by neighboring SFX "
            "and queue/music staging before later 0x80 bursts."
        ),
    },
    {
        "scene_id": "MAP415",
        "path": "decoded_scripts/23-Great Cathedral/415-The Dark tempts Ashley.txt",
        "scene_class": "queue_plus_music_scene",
        "focus": (
            "Minority case with no in-file SFX pair before sampled 0x80 bursts; the "
            "file instead stages queue-plus-music state up front and later refreshes "
            "the music-slot side again."
        ),
    },
    {
        "scene_id": "MAP026",
        "path": "decoded_scripts/1-Wine Cellar/026-The Gallows.txt",
        "scene_class": "same_title_base_scene",
        "focus": (
            "Base Gallows scene that stages complete queue, music, and SFX preparation "
            "before the first 0x80 burst."
        ),
    },
    {
        "scene_id": "MAP408",
        "path": "decoded_scripts/1-Wine Cellar/408-The Gallows (Mino Zombie, new chest).txt",
        "scene_class": "same_title_variant_scene",
        "focus": (
            "Same-title variant that keeps only the inert 0x41/0x42 scaffold with no "
            "neighboring sound-family opcode anywhere in the file."
        ),
    },
]


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
            "Audit the minority scene-local neighboring-consumer paths that still "
            "matter after opcode 0x80 was confirmed as a shared stub."
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
        default=Path("decomp/evidence/opcode_0x80_consumer_path_scan.json"),
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


def complete_pairs(lines: list[ParsedLine]) -> list[str]:
    present = {line.opcode for line in lines}
    return [
        pair_name
        for pair_name, members in PAIR_DEFS.items()
        if set(members).issubset(present)
    ]


def sound_lines(lines: list[ParsedLine]) -> list[str]:
    return [line.text for line in lines if line.opcode in SOUND_OPCODES]


def burst_windows(parsed: list[ParsedLine]) -> list[dict[str, object]]:
    burst_indices = [index for index, line in enumerate(parsed) if line.opcode == 0x80]
    windows: list[dict[str, object]] = []
    for position, burst_index in enumerate(burst_indices):
        burst = parsed[burst_index]
        previous_index = burst_indices[position - 1] if position > 0 else -1
        next_index = burst_indices[position + 1] if position + 1 < len(burst_indices) else len(parsed)
        before_segment = parsed[previous_index + 1 : burst_index]
        after_segment = parsed[burst_index + 1 : next_index]
        windows.append(
            {
                "burst_number": position + 1,
                "address": f"0x{burst.address:04X}",
                "raw_hex": burst.raw_hex,
                "sound_ops_since_previous_0x80": sound_lines(before_segment),
                "complete_pairs_since_previous_0x80": complete_pairs(before_segment),
                "sound_ops_until_next_0x80": sound_lines(after_segment),
                "complete_pairs_until_next_0x80": complete_pairs(after_segment),
                "immediate_context_before": [
                    line.text for line in parsed[max(0, burst_index - 3) : burst_index]
                ],
                "immediate_context_after": [
                    line.text for line in parsed[burst_index + 1 : min(len(parsed), burst_index + 4)]
                ],
            }
        )
    return windows


def summarize_records(records: list[dict[str, object]]) -> dict[str, object]:
    class_counts = Counter(record["scene_class"] for record in records)
    first_bursts_without_sound_ops = sum(
        1 for record in records if not record["bursts"][0]["sound_ops_since_previous_0x80"]
    )
    records_with_later_pairs = sum(
        1 for record in records if any(burst["complete_pairs_since_previous_0x80"] for burst in record["bursts"][1:])
    )
    return {
        "scene_count": len(records),
        "scene_class_counts": dict(sorted(class_counts.items())),
        "first_bursts_without_neighboring_sound_ops": first_bursts_without_sound_ops,
        "records_with_later_explicit_pair_staging": records_with_later_pairs,
        "resolved_question": (
            "The minority scenes still split between structural opener reuse, "
            "neighboring SFX or queue/music staging, and same-title variant "
            "divergence; none of them require a direct opcode 0x80 consumer."
        ),
    }


def build_record(repo_root: Path, decoded_root: Path, config: dict[str, str]) -> dict[str, object]:
    script_path = repo_root / config["path"]
    parsed = parse_script(script_path)
    bursts = burst_windows(parsed)
    first_burst = bursts[0]
    all_sound_lines = sound_lines(parsed)

    return {
        "scene_id": config["scene_id"],
        "scene_class": config["scene_class"],
        "path": script_path.relative_to(repo_root).as_posix(),
        "area": script_path.parent.name,
        "focus": config["focus"],
        "burst_count": len(bursts),
        "first_burst": {
            "address": first_burst["address"],
            "raw_hex": first_burst["raw_hex"],
            "sound_ops_before_first_0x80": first_burst["sound_ops_since_previous_0x80"],
            "complete_pairs_before_first_0x80": first_burst["complete_pairs_since_previous_0x80"],
            "sound_ops_after_first_0x80_until_next_0x80": first_burst["sound_ops_until_next_0x80"],
            "complete_pairs_after_first_0x80_until_next_0x80": first_burst["complete_pairs_until_next_0x80"],
            "immediate_context_before": first_burst["immediate_context_before"],
            "immediate_context_after": first_burst["immediate_context_after"],
        },
        "bursts": bursts,
        "all_sound_family_lines": all_sound_lines,
        "complete_pairs_anywhere_in_file": complete_pairs([line for line in parsed if line.opcode in SOUND_OPCODES]),
    }


def main() -> None:
    args = parse_args()
    repo_root = Path.cwd().resolve()
    decoded_root = (repo_root / args.decoded_root).resolve()
    if not decoded_root.exists():
        raise FileNotFoundError(decoded_root)

    records = [
        build_record(repo_root, decoded_root, config)
        for config in TARGET_SCENES
    ]

    gallows_base = next(record for record in records if record["scene_id"] == "MAP026")
    gallows_variant = next(record for record in records if record["scene_id"] == "MAP408")

    payload = {
        "target": "opcode 0x80",
        "analysis": "minority scene-local neighboring-consumer audit after opcode 0x80 confirmation",
        "decoded_root": str(args.decoded_root).replace("\\", "/"),
        "summary": summarize_records(records),
        "gallows_variant_contrast": {
            "base_scene": gallows_base["path"],
            "variant_scene": gallows_variant["path"],
            "base_pairs_before_first_0x80": gallows_base["first_burst"]["complete_pairs_before_first_0x80"],
            "variant_pairs_before_first_0x80": gallows_variant["first_burst"]["complete_pairs_before_first_0x80"],
            "base_sound_family_line_count": len(gallows_base["all_sound_family_lines"]),
            "variant_sound_family_line_count": len(gallows_variant["all_sound_family_lines"]),
        },
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
