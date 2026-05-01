# Opcode `0x80` Semantic Proof

## Goal

Turn the closed copy/patch contradiction into the safest local semantic claim
for `0x80` before any decoder-facing rename is considered.

## Structural floor that is now proven

1. `decomp/evidence/inittbl_opcode_table.json` exports:
   - `0x80 -> 0x800B66E4`
   - `0x81 -> 0x800B66E4`
   - `0x82 -> 0x800B66E4`
2. `decomp/evidence/battle_0x80_handler_slices.json` shows the target at
   `0x800B66E4` begins with only:

```text
800b66e4 jr ra
800b66e8 clear v0
```

3. `decomp/evidence/opcode_0x80_runtime_dispatch_static.md` and
   `decomp/evidence/opcode_0x80_runtime_support.md` now prove the live retail
   reader path:
   - resolve copied runtime table pointer slot `0x800F4C28 -> 0x801119F0`
   - reach `0x8007A36C -> 0x800BF850 -> 0x800BFBB8`
   - dispatch retail `0x80 -> 0x800B66E4` from the untouched `MAP001` intro

## Why the old rewrite theory no longer blocks interpretation

- The generated support note compares both checked snapshots against the
  reconstructed baseline and reports:
  - `after_init`: `256` matching entries, `0` changed entries
  - `pre_dispatch`: `256` matching entries, `0` changed entries
- The live write watchpoint over `0x801119F0-0x80111DEF` records `0` hits in
  that validated route.
- That is enough to retire the old "`0x80` must become something else later"
  branch for this checked retail path.

## Why the nearby sound candidate no longer rescues `SoundEffects0`

- `decomp/evidence/opcode_0x80_sound_cluster_static.md` anchors `0x800BA2E0`
  inside a separate local `BATTLE.PRG` sound subdispatch table rooted at
  `0x800E9F30`.
- That same local family contains the visible `0x83+` neighborhood, so the
  helper is no longer best treated as a hidden replacement handler for the
  copied `0x80` slot.
- Real script usage still places `0x80` near audio-looking moments, but that
  is now context evidence only, not handler-level proof for `0x80` itself.
  The same `MAP001` intro also contains overt sound-family setup opcodes such
  as `0x85`, `0x86`, `0x88`, `0x90`, and `0x92`.

## Safe current interpretation

- The safest local label is `Opcode80SharedStub`.
- That label is structural on purpose: it describes what the verified handler
  does without pretending the audible effect belongs to `0x80` itself.
- The widened shared-family audit now makes the same caution apply more
  broadly: `0x800B66E4` is a heterogeneous `INITBTL.PRG` stub family, not a
  uniquely audio-shaped `0x80` special case.
- `SoundEffects0` is now an overclaim for the opcode.
- The best current reading is that `0x80` reaches a shared return-zero stub,
  while the apparent sound behavior around those script sites comes from
  neighboring opcodes, previously armed sound state, or another subsystem that
  has not been locally tied to the `0x80` dispatch slot.

## Status

- `0x80` is now best carried as `tentative`, not `confirmed`.
- The copy/patch contradiction is closed.
- The remaining work is semantic cleanup and downstream naming discipline, not
  another runtime tie-breaker.

## What would still be needed for `confirmed`

- A local explanation that fully accounts for the surrounding audio-looking
  script moments without restoring a direct sound-effect meaning to `0x80`.
- A proof path that survives the widened family audit by tying those moments
  to neighboring sound-family behavior or another non-stub consumer path
  instead of treating `0x800B66E4` as uniquely meaningful.
- Or a new local proof that some other engine layer still treats the `0x80`
  opcode byte specially even though the validated runtime-table dispatch lands
  on the shared stub.
