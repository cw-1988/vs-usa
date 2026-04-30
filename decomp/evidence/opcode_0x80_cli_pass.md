# Opcode `0x80` CLI Pass

## Inputs

- `Game Data/BATTLE/INITBTL.PRG`
- `Game Data/BATTLE/BATTLE.PRG`
- `decomp/ghidra/export_inittbl_opcode_table.ps1`
- `decomp/ghidra/export_inittbl_0x80_copy_slice.ps1`
- `decomp/ghidra/export_battle_0x80_sound_cluster_slices.ps1`
- `decomp/ghidra/ExportFunctionTable.java`
- `decomp/ghidra/DumpInstructions.java`
- `decomp/ghidra/DumpXrefs.java`

## Produced artifacts

- `decomp/evidence/inittbl_opcode_table.json`
- `decomp/evidence/inittbl_0x80_copy_slice.json`
- `decomp/evidence/inittbl_opcode_table_xrefs.json`
- `decomp/evidence/battle_0x80_handler_slices.json`
- `decomp/evidence/battle_sound_candidate_slice.json`
- `decomp/evidence/battle_sound_candidate_xrefs.json`
- `decomp/evidence/battle_sound_dispatch_table.json`
- `decomp/evidence/battle_0x80_sound_cluster_slices.json`

## Packet structure

- This file is the top-level `0x80` proof packet.
- `opcode_0x80_copy_path_static.md` is the focused support note for the
  `0x800FAF7C -> 0x800F4C28` copy path.
- `opcode_0x80_sound_cluster_static.md` is the focused support note for the
  nearby `0x800BA2E0` sound-family interpretation.

## Static findings

- The binary-derived `INITBTL.PRG` opcode table export places `0x80` at
  `0x800B66E4`.
- `0x81` and `0x82` also point to `0x800B66E4`.
- `0x83` and `0x84` move on to different handlers (`0x800BA3E4`,
  `0x800BA404`), so the `0x80-0x82` cluster is a real repeated target rather
  than an export error.
- The code slice starting at `0x800B66E4` begins with:

```text
800b66e4 jr ra
800b66e8 clear v0
```

- That is a real binary stub, not just a decompiler artifact.

## Copy-path findings

- `inittbl_0x80_copy_slice.json` proves that the exported table at `0x800FAF7C`
  is copied into runtime slot `0x800F4C28` during init.
- `inittbl_opcode_table_xrefs.json` is still empty under the current headless
  analysis settings, so the copy-path claim currently rests on the local
  instruction slice rather than an auto-recovered xref.
- See `opcode_0x80_copy_path_static.md` for the exact copy-sequence argument.

## Conflicting nearby evidence

- `battle_sound_candidate_slice.json` still shows `0x800BA2E0` consuming the
  same four-byte argument block as the visible sound family.
- `battle_sound_candidate_xrefs.json` now recovers a direct local data xref
  from `0x800E9F30 -> 0x800BA2E0`.
- `battle_sound_dispatch_table.json` then exports that `0x800E9F30` table as
  an eight-entry local `BATTLE.PRG` handler family containing `0x800BA2E0`,
  `0x800BA35C`, `0x800BA39C`, and the already-visible `0x800BA3E4+`
  neighborhood.
- `battle_0x80_sound_cluster_slices.json` now covers that fuller local family,
  which makes `0x800BA2E0` look like a member of a separate sound
  subdispatch block rather than a hidden replacement for the copied `0x80`
  slot.
- See `opcode_0x80_sound_cluster_static.md` for the local neighborhood case.

## Current conclusion

- `0x80` is still **in progress**, not confirmed.
- Local binary evidence now proves both the copied initial dispatch slot
  (`0x800B66E4`) and the init-time table copy into runtime slot `0x800F4C28`.
- The nearby sound-shaped helper keeps `SoundEffects0` plausible as a working
  placeholder, but the local static picture now favors "`0x80-0x82` are real
  copied stubs, while `0x800BA2E0` belongs to a separate local sound
  subdispatch family that also contains the visible `0x83+` handlers."
- The remaining unresolved question is no longer "is `0x800BA2E0` secretly the
  real `0x80` target?" but "does any later runtime path rewrite or bypass the
  copied `0x800F4C28` slot before dispatch?"
