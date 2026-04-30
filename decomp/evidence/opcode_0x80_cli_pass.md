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

- `battle_sound_candidate_slice.json` still keeps `0x800BA2E0` plausible as a
  sound-shaped candidate because it consumes the same four-byte argument block.
- `battle_0x80_sound_cluster_slices.json` also shows the exported table already
  moving into a visible contiguous sound-family neighborhood at `0x83+`.
- That weakens the idea that `0x800BA2E0` must be a hidden replacement for the
  copied `0x80` slot, but it does not fully rule it out.
- See `opcode_0x80_sound_cluster_static.md` for the local neighborhood case.

## Current conclusion

- `0x80` is still **conflicted**, not confirmed.
- Local binary evidence now proves both the copied initial dispatch slot
  (`0x800B66E4`) and the init-time table copy into runtime slot `0x800F4C28`.
- The nearby sound-shaped helper keeps `SoundEffects0` plausible as a working
  placeholder, but the local static picture currently favors "`0x80-0x82` are
  real copied stubs, while the visible sound-control family begins at `0x83+`."
