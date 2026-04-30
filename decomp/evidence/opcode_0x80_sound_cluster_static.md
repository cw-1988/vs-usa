# Opcode `0x80` Sound-Cluster Static Notes

## Goal

Test whether the nearby `vs_main_playSfx` helper at `0x800BA2E0` is better
explained as part of the already-visible `0x83+` sound family than as a hidden
replacement for the copied `0x80` table entry.

## Static neighborhood

The exported `INITBTL.PRG` table shows this contiguous block:

- `0x80 -> 0x800B66E4`
- `0x81 -> 0x800B66E4`
- `0x82 -> 0x800B66E4`
- `0x83 -> 0x800BA3E4`
- `0x84 -> 0x800BA404`
- `0x85 -> 0x800BA444`
- `0x86 -> 0x800BA470`
- `0x87 -> 0x800BA494`
- `0x88 -> 0x800BA4B8`
- `0x89 -> 0x800BA4E8`

That same neighborhood is mirrored in
`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c`, where the static source
table steps from three `func_800B66E4` entries straight into:

- `func_800BA3E4`
- `func_800BA404`
- `vs_battle_script_loadSfxSlot`
- `vs_battle_script_freeSfxSlot`
- `vs_battle_script_freeSfx`
- `vs_battle_script_setCurrentSfx`
- `vs_battle_script_loadSoundFile`

## Recovered sound-side handlers

Recovered `BATTLE.PRG` source in `4A0A8.c` shows:

- `func_800BA2E0` calling `vs_main_playSfx(...)`
- `func_800BA3E4` calling `func_80045DC0()`
- `func_800BA404` calling `func_80045D64(...)`
- `vs_battle_script_loadSfxSlot`
- `vs_battle_script_freeSfxSlot`
- `vs_battle_script_freeSfx`
- `vs_battle_script_setCurrentSfx`
- `vs_battle_script_loadSoundFile`

This places a dense sound-control cluster immediately after the `0x80-0x82`
stub block.

## What this changes

- The nearby `0x800BA2E0` helper is no longer best treated as a generic
  "maybe this is really opcode 0x80" candidate.
- Static layout makes it more plausible that `0x800BA2E0` belongs to the
  adjacent `0x83+` sound-control neighborhood, either as a shared helper or as
  a body used by one of the nearby sound opcodes.
- The strongest static claim for `0x80` remains the copied `0x800B66E4` stub
  cluster at `0x80-0x82`.

## What remains unresolved

- This pass did not recover a direct caller xref from one of the `0x83+`
  handlers to `func_800BA2E0`.
- This pass also did not identify the live consumer of `D_800F4C28`, so a
  later runtime patch or bypass path is still not ruled out.

## Current conclusion

- The competing sound evidence is weaker than before.
- The current static picture favors "`0x80-0x82` are real copied stubs, while
  the visible sound family begins at `0x83+`."
- The next best static step is still xref-level recovery for the runtime
  dispatch path or for callers of `func_800BA2E0`.
