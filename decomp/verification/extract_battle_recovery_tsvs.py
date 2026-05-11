#!/usr/bin/env python3
"""Extract battle recovery values from the packed skill table.

This script reads `Game Data/SLUS_010.40`, decodes the packed skill records,
and writes:

- `battle_recovery_values.tsv`
- `battle_recovery_default.tsv`
- `battle_recovery_spells.tsv`
- `battle_recovery_abilities.tsv`
- `battle_recovery_break_arts.tsv`
- `battle_recovery_items.tsv`
- `battle_recovery_traps.tsv`

The current packed record assumptions come from the ongoing RE work:
- skill table address: 0x8004B9DC
- record size: 52 bytes
- skill type: bits 1..3 of byte 2
- recovery value: signed byte 12
- display name: vsString at byte 28
"""

from __future__ import annotations

import csv
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SLUS_PATH = REPO_ROOT / "Game Data" / "SLUS_010.40"
VASTRING_ROOT = REPO_ROOT / "_refs" / "rood-reverse"

sys.path.insert(0, str(VASTRING_ROOT))
from tools.etc.vsString import decode  # type: ignore  # noqa: E402


SKILL_TABLE_ADDR = 0x8004B9DC
PSX_EXE_TEXT_OFFSET = 0x800
SKILL_RECORD_SIZE = 52


@dataclass(frozen=True)
class Row:
    skill_id: int
    name: str
    recovery_value: str
    notes: str = ""


CATEGORY_INFO = {
    1: ("Spell", "battle_recovery_spells.tsv"),
    2: ("Ability", "battle_recovery_abilities.tsv"),
    3: ("Break Art", "battle_recovery_break_arts.tsv"),
    5: ("Item", "battle_recovery_items.tsv"),
    6: ("Default / normal action", "battle_recovery_default.tsv"),
    7: ("Trap", "battle_recovery_traps.tsv"),
}


def signed_byte(value: int) -> int:
    return value - 256 if value > 127 else value


def clean_name(raw_name: str) -> str:
    name = re.sub(r"\|>\d+\|", " ", raw_name)
    name = re.sub(r"\|!\d+\|", " ", name)
    name = re.sub(r"\|[a-zA-Z#$][0-9]*\|", " ", name)
    return re.sub(r"\s+", " ", name).strip()


def read_skill_records(slush_path: Path) -> list[bytes]:
    exe = slush_path.read_bytes()
    load_addr = struct.unpack_from("<I", exe, 0x18)[0]
    table_offset = PSX_EXE_TEXT_OFFSET + (SKILL_TABLE_ADDR - load_addr)
    return [
        exe[table_offset + i * SKILL_RECORD_SIZE : table_offset + (i + 1) * SKILL_RECORD_SIZE]
        for i in range(256)
    ]


def category_type(record: bytes) -> int:
    return (record[2] >> 1) & 0x7


def build_rows(records: list[bytes]) -> dict[str, list[Row]]:
    rows_by_category: dict[str, list[Row]] = {
        category_name: [] for category_name, _ in CATEGORY_INFO.values()
    }

    for skill_id, record in enumerate(records):
        skill_type = category_type(record)
        if skill_type not in CATEGORY_INFO:
            continue

        category_name, _ = CATEGORY_INFO[skill_type]
        recovery_raw = signed_byte(record[12])
        raw_name = decode(record[28:])
        name = clean_name(raw_name)
        notes = ""

        if skill_type == 6:
            recovery_value = "weapon.unk10B + actor.unk956_2"
            notes = "Fallback path; skill table stores 0xFF here"
        elif skill_type == 5 and recovery_raw == -1:
            recovery_value = "0xFF"
            notes = (
                "Below the ID >= 54 cooldown gate; table says fallback but this add path "
                "does not run here"
            )
        else:
            recovery_value = str(recovery_raw)

        rows_by_category[category_name].append(
            Row(
                skill_id=skill_id,
                name=name,
                recovery_value=recovery_value,
                notes=notes,
            )
        )

    return rows_by_category


def write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def write_outputs(output_dir: Path, rows_by_category: dict[str, list[Row]]) -> None:
    combined_rows: list[list[str]] = []

    for skill_type in (6, 1, 2, 3, 5, 7):
        category_name, filename = CATEGORY_INFO[skill_type]
        category_rows = rows_by_category[category_name]

        split_rows = [
            [str(row.skill_id), row.name, row.recovery_value, row.notes] for row in category_rows
        ]
        write_tsv(
            output_dir / filename,
            ["SkillId", "Name", "RecoveryValue", "Notes"],
            split_rows,
        )

        combined_rows.extend(
            [
                [category_name, str(row.skill_id), row.name, row.recovery_value, row.notes]
                for row in category_rows
            ]
        )

    write_tsv(
        output_dir / "battle_recovery_values.tsv",
        ["Category", "SkillId", "Name", "RecoveryValue", "Notes"],
        combined_rows,
    )


def main() -> None:
    records = read_skill_records(SLUS_PATH)
    rows_by_category = build_rows(records)
    write_outputs(REPO_ROOT, rows_by_category)


if __name__ == "__main__":
    main()
