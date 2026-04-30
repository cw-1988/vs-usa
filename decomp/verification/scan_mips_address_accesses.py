#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REGISTER_NAMES = (
    "zero",
    "at",
    "v0",
    "v1",
    "a0",
    "a1",
    "a2",
    "a3",
    "t0",
    "t1",
    "t2",
    "t3",
    "t4",
    "t5",
    "t6",
    "t7",
    "s0",
    "s1",
    "s2",
    "s3",
    "s4",
    "s5",
    "s6",
    "s7",
    "t8",
    "t9",
    "k0",
    "k1",
    "gp",
    "sp",
    "fp",
    "ra",
)

READ_OPCODES = {
    0x20: "lb",
    0x21: "lh",
    0x22: "lwl",
    0x23: "lw",
    0x24: "lbu",
    0x25: "lhu",
    0x26: "lwr",
    0x30: "ll",
    0x32: "lwc2",
}

WRITE_OPCODES = {
    0x28: "sb",
    0x29: "sh",
    0x2A: "swl",
    0x2B: "sw",
    0x2E: "swr",
    0x38: "sc",
    0x3A: "swc2",
}

ACCESS_OPCODES = {**READ_OPCODES, **WRITE_OPCODES}


@dataclass(frozen=True)
class Instruction:
    opcode: int
    rs: int
    rt: int
    imm: int
    word: int


def parse_int(value: str) -> int:
    return int(str(value), 0)


def to_hex(value: int, digits: int = 8) -> str:
    return f"0x{value:0{digits}X}"


def decode_instruction(word: int) -> Instruction:
    return Instruction(
        opcode=(word >> 26) & 0x3F,
        rs=(word >> 21) & 0x1F,
        rt=(word >> 16) & 0x1F,
        imm=word & 0xFFFF,
        word=word,
    )


def format_instruction(instruction: Instruction) -> str:
    if instruction.opcode == 0x0F:
        return f"lui {REGISTER_NAMES[instruction.rt]},0x{instruction.imm:04X}"

    mnemonic = ACCESS_OPCODES.get(instruction.opcode)
    if mnemonic is not None:
        return (
            f"{mnemonic} {REGISTER_NAMES[instruction.rt]},"
            f"0x{instruction.imm:04X}({REGISTER_NAMES[instruction.rs]})"
        )

    return to_hex(instruction.word)


def classify_access(opcode: int) -> str | None:
    if opcode in READ_OPCODES:
        return "read"
    if opcode in WRITE_OPCODES:
        return "write"
    return None


def iter_target_files(paths: Iterable[Path], suffixes: set[str]) -> list[Path]:
    files: set[Path] = set()
    for raw_path in paths:
        path = raw_path.resolve()
        if path.is_file():
            if path.suffix.lower() in suffixes:
                files.add(path)
            continue

        if path.is_dir():
            for candidate in path.rglob("*"):
                if candidate.is_file() and candidate.suffix.lower() in suffixes:
                    files.add(candidate.resolve())

    return sorted(files)


def scan_file(path: Path, target: int, window: int, repo_root: Path) -> dict[str, object] | None:
    data = path.read_bytes()
    literal = target.to_bytes(4, "little", signed=False)
    literal_offsets: list[str] = []
    start = 0
    while True:
        offset = data.find(literal, start)
        if offset < 0:
            break
        literal_offsets.append(to_hex(offset))
        start = offset + 1

    target_upper = (target >> 16) & 0xFFFF
    target_lower = target & 0xFFFF
    words = len(data) // 4
    instruction_matches: list[dict[str, object]] = []

    decoded = [
        decode_instruction(int.from_bytes(data[index * 4 : index * 4 + 4], "little"))
        for index in range(words)
    ]

    for index, instruction in enumerate(decoded):
        if instruction.opcode != 0x0F or instruction.imm != target_upper:
            continue

        for distance in range(1, window + 1):
            next_index = index + distance
            if next_index >= len(decoded):
                break

            candidate = decoded[next_index]
            access_kind = classify_access(candidate.opcode)
            if access_kind is None:
                continue
            if candidate.rs != instruction.rt or candidate.imm != target_lower:
                continue

            instruction_matches.append(
                {
                    "lui_offset": to_hex(index * 4),
                    "lui_text": format_instruction(instruction),
                    "access_offset": to_hex(next_index * 4),
                    "access_text": format_instruction(candidate),
                    "access_kind": access_kind,
                    "base_register": REGISTER_NAMES[candidate.rs],
                    "target_register": REGISTER_NAMES[candidate.rt],
                    "distance_in_instructions": distance,
                }
            )

    if not literal_offsets and not instruction_matches:
        return None

    return {
        "file": path.relative_to(repo_root).as_posix(),
        "size_bytes": len(data),
        "raw_literal_offsets": literal_offsets,
        "instruction_pair_matches": instruction_matches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Heuristically scan raw MIPS binaries for absolute address accesses "
            "built as lui hi16(target) plus load/store low16(target)(reg)."
        )
    )
    parser.add_argument("target_address", help="Absolute address to scan for, e.g. 0x800F4C28.")
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Files or directories to scan recursively.",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=6,
        help="Maximum number of instructions between the lui and matching access.",
    )
    parser.add_argument(
        "--suffix",
        dest="suffixes",
        action="append",
        default=[".prg", ".bin", ".40"],
        help="File suffix to include when scanning directories. Repeatable.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root for stable relative paths in the output.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path. Defaults to stdout.",
    )
    args = parser.parse_args()

    target = parse_int(args.target_address) & 0xFFFFFFFF
    repo_root = args.repo_root.resolve()
    suffixes = {value.lower() for value in args.suffixes}
    files = iter_target_files(args.paths, suffixes)

    matches: list[dict[str, object]] = []
    for path in files:
        match = scan_file(path, target, args.window, repo_root)
        if match is not None:
            matches.append(match)

    payload = {
        "target_address": to_hex(target),
        "target_upper": to_hex((target >> 16) & 0xFFFF, digits=4),
        "target_lower": to_hex(target & 0xFFFF, digits=4),
        "window": args.window,
        "suffix_filters": sorted(suffixes),
        "scanned_paths": [str(path) for path in args.paths],
        "files_scanned": len(files),
        "matched_file_count": len(matches),
        "matched_files": matches,
    }

    text = json.dumps(payload, indent=2)
    if args.output is None:
        print(text)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text + "\n", encoding="utf-8")
    print(f"wrote scan report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
