# Opcode `0x80` Runtime Memcard Probe

## Goal

Check whether the checked-in cold-boot fallback can reasonably assume a
memcard-backed `Continue` or `Load` route before spending more time retuning
menu timings.

## Method

- Probed the repo-root `memcard1.mcd` and `memcard2.mcd` files with:
  `python decomp/verification/probe_psx_memcards.py memcard1.mcd memcard2.mcd --output decomp/evidence/opcode_0x80_runtime_memcard_probe.json`
- Used a conservative heuristic:
  - standard PS1 card size (`131072` bytes)
  - very low nonzero-byte count
  - no obvious `VAGRANT`, `STORY`, `SLUS`, `SCUS`, `SLPS`, or `SQUARE`
    ASCII runs
  - no nonzero bytes beyond the first `0x2000` bytes of directory/header area

## Result

- `memcard1.mcd`: `131072` bytes, `186` nonzero bytes, highest nonzero offset
  `0x1FFF`, no target-title ASCII matches, heuristic verdict
  `looks_blank_formatted=true`
- `memcard2.mcd`: `131072` bytes, `186` nonzero bytes, highest nonzero offset
  `0x1FFF`, no target-title ASCII matches, heuristic verdict
  `looks_blank_formatted=true`

The full machine-readable output is in:

- [`opcode_0x80_runtime_memcard_probe.json`](opcode_0x80_runtime_memcard_probe.json)

## Interpretation

The current repo-local memcards look like blank formatted cards, not cards with
a nearby Vagrant Story save. That makes the existing fallback route's
memcard-backed menu assumption a poor default: even if the button timings are
correct, the route has no obvious save payload to resume from.

## Immediate implication

For the next runtime pass, prefer one of:

1. a real near-battle savestate via `-SaveStatePath` or `-UseNewestSaveState`
2. a populated memcard handoff artifact that proves the intended resume route
3. a replacement cold-boot plan that intentionally follows `New Game` until it
   earns a real save or checkpoint instead of depending on save-backed
   `Continue` or `Load`
