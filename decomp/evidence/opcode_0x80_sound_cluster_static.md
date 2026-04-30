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

## Local sound-side slices

`decomp/evidence/battle_0x80_sound_cluster_slices.json` shows:

- `0x800BA2E0` reading four argument bytes, indexing through a table at
  `0x800E9B34`, and calling `0x80045754`
- `0x800BA3E4` calling `0x80045DC0`
- `0x800BA404` indexing through the same `0x800E9B34` table and calling
  `0x80045D64`
- `0x800BA444` calling `0x80045DE0`
- `0x800BA470` calling `0x80045F64`

This is a dense local neighborhood of non-stub sound-shaped handlers
immediately adjacent to the `0x80-0x82` stub block.

## What this changes

- The nearby `0x800BA2E0` helper is no longer best treated as "maybe this is
  secretly the real `0x80` target."
- Local static layout makes it more plausible that `0x800BA2E0` belongs to the
  adjacent `0x83+` handler family, either as a helper or as part of the same
  sound-control block.
- The strongest local static claim for `0x80` still remains the copied
  `0x800B66E4` stub cluster at `0x80-0x82`.

## What remains unresolved

- This pass did not recover a direct caller xref from one of the visible
  `0x83+` entries to `0x800BA2E0`.
- This pass also did not identify the live consumer of `0x800F4C28`, so a
  later runtime patch or bypass path is still not ruled out.

## Current conclusion

- The competing sound evidence is weaker than before.
- The current static picture favors "`0x80-0x82` are real copied stubs, while
  the visible sound-control family begins at `0x83+`."
- The next best static step is still xref-level recovery for the runtime
  dispatch path or for callers of `0x800BA2E0`.
