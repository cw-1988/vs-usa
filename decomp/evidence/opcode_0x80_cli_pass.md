# Opcode `0x80` CLI Pass

## Inputs

- `Game Data/BATTLE/INITBTL.PRG`
- `Game Data/BATTLE/BATTLE.PRG`
- `decomp/ghidra/export_inittbl_opcode_table.ps1`
- `decomp/ghidra/ExportFunctionTable.java`
- `decomp/ghidra/DumpInstructions.java`

## Produced artifacts

- `decomp/evidence/inittbl_opcode_table.json`
- `decomp/evidence/battle_0x80_handler_slices.json`
- `decomp/evidence/battle_sound_candidate_slice.json`

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

## Conflicting nearby evidence

- A separate code slice at `0x800BA2E0` shows a 4-byte argument consumer:

```text
800ba324 lbu v0,0x1(a3)
800ba328 lbu a1,0x2(a3)
800ba32c lbu a2,0x3(a3)
800ba330 lbu a3,0x4(a3)
800ba33c lw a0,0x0(v0)
800ba340 jal 0x80045754
```

- `_refs/rood-reverse/config/SLUS_010.40/symbol_addrs.txt` maps
  `0x80045754` to `vs_main_playSfx`.
- That makes `0x800BA2E0` a strong sound-playback candidate, but it does not
  appear as the static `0x80` table target in the binary export.

## Current conclusion

- `0x80` is still **conflicted**, not confirmed.
- The binary table proves the current dispatch slot is `0x800B66E4`.
- The nearby sound-shaped helper keeps `SoundEffects0` plausible as a working
  placeholder, but not proven enough to promote beyond tentative status.
