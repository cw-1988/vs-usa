# Opcode `0x80` Sound-Cluster Static Notes

## Goal

Test whether the nearby helper at `0x800BA2E0` is better explained as part of
the already-visible `0x83+` sound neighborhood than as a hidden replacement
for the copied `0x80` table entry.

## Local static neighborhood

The exported `INITBTL.PRG` table shows this contiguous block:

- `0x80 -> 0x800B66E4`
- `0x81 -> 0x800B66E4`
- `0x82 -> 0x800B66E4`
- `0x83 -> 0x800BA3E4`
- `0x84 -> 0x800BA404`
- `0x85 -> 0x800BA444`
- `0x86 -> 0x800BA470`

That means the table already steps from the `0x80-0x82` stub cluster into a
different contiguous handler family at `0x83+`.

## Local direct xref and subdispatch table

`decomp/evidence/battle_sound_candidate_xrefs.json` now recovers a direct
local `BATTLE.PRG` data xref from `0x800E9F30 -> 0x800BA2E0`.

`decomp/evidence/battle_sound_dispatch_table.json` then exports the local
eight-entry function table rooted at `0x800E9F30`:

- `0x00 -> 0x800BA2E0`
- `0x01 -> 0x800BA35C`
- `0x02 -> 0x800BA39C`
- `0x03 -> 0x800BA3E4`
- `0x04 -> 0x800BA404`
- `0x05 -> 0x800BA444`
- `0x06 -> 0x800BA470`
- `0x07 -> 0x800BA494`

That table directly anchors `0x800BA2E0` inside the same local `BATTLE.PRG`
family as the visible `0x83+` handlers instead of leaving it as an orphan
candidate.

## Local sound-side slices

`decomp/evidence/battle_0x80_sound_cluster_slices.json` shows:

- `0x800BA2E0` reading four argument bytes, indexing through a table at
  `0x800E9B34`, and calling `0x80045754`
- `0x800BA35C` unpacking a halfword-like argument and calling
  `0x8007C8A4`
- `0x800BA39C` reading four argument bytes, indexing through the same
  `0x800E9B34` table, and calling `0x80045BFC`
- `0x800BA3E4` calling `0x80045DC0`
- `0x800BA404` indexing through the same `0x800E9B34` table and calling
  `0x80045D64`
- `0x800BA444` calling `0x80045DE0`
- `0x800BA470` calling `0x80045F64`
- `0x800BA494` calling `0x800460C0` and checking `0x800F4C2C`

This is a dense local neighborhood of non-stub sound-shaped handlers
immediately adjacent to the `0x80-0x82` stub block.

## What this changes

- The nearby `0x800BA2E0` helper is no longer best treated as "maybe this is
  secretly the real `0x80` target."
- Local static layout now does more than suggest adjacency: it places
  `0x800BA2E0` into a direct local `BATTLE.PRG` subdispatch table that also
  contains the visible `0x83+` handler family.
- The strongest local static claim for `0x80` still remains the copied
  `0x800B66E4` stub cluster at `0x80-0x82`.

## What remains unresolved

- This pass still did not identify the live consumer of `0x800F4C28`.
- This pass also did not identify a later static patch writer that rewrites the
  copied `0x80-0x84` slots before execution.

## Current conclusion

- The competing sound evidence is no longer a strong direct contradiction.
- The current static picture favors "`0x80-0x82` are real copied stubs, while
  `0x800BA2E0` belongs to a separate local sound subdispatch family that also
  contains the visible `0x83+` handlers."
- The next best static step is now the runtime-side one: recover the live
  dispatch consumer or a later patch path for `0x800F4C28`.
