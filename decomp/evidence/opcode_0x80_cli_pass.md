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

- The local `INITBTL.PRG` slice at `0x800FAAAC` shows the init-time allocator
  sequence for the battle script runtime:

```text
800faadc li a0,0x400
800faae4 jal 0x80043ec4
800faaec move a0,v0
800faaf4 lui a1,0x8010
800faaf8 addiu a1,a1,-0x5084
800faafc li a2,0x400
800fab00 jal 0x800490b0
800fab04 sw a0,0x4c28(v0)
```

- `0x8010:0x5084` resolves to `0x800FAF7C`, so the same routine allocates a
  `0x400` byte buffer, stores it to runtime slot `0x800F4C28`, and copies
  `0x400` bytes from the exported opcode table at `0x800FAF7C`.
- The current headless xref dump for `0x800FAF7C` came back empty, so this pass
  relies on the binary instruction slice rather than an auto-recovered data xref.

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

- The same local sound-neighborhood dump shows that the table already moves
  from the `0x80-0x82` stub cluster into a contiguous block of non-stub
  handlers at `0x83+`, including:

```text
0x83 -> 0x800BA3E4 -> jal 0x80045dc0
0x84 -> 0x800BA404 -> jal 0x80045d64
0x85 -> 0x800BA444 -> jal 0x80045de0
0x86 -> 0x800BA470 -> jal 0x80045f64
```

- That makes `0x800BA2E0` a strong nearby sound-family helper candidate, but
  it still does not appear as the static `0x80` table target in the binary
  export.

## Current conclusion

- `0x80` is still **conflicted**, not confirmed.
- Local binary evidence now proves both the copied initial dispatch slot
  (`0x800B66E4`) and the init-time table copy into runtime slot `0x800F4C28`.
- The nearby sound-shaped helper keeps `SoundEffects0` plausible as a working
  placeholder, but the local static picture currently favors "`0x80-0x82` are
  real copied stubs, while the visible sound-control family begins at `0x83+`."
