# Opcode `0x80` Runtime-Slot Access Sweep

## Objective

Check the local battle executables for direct absolute accesses to
`0x800F4C28`, the runtime slot that holds the copied opcode table pointer, so
the remaining `0x80` conflict can move from "possible later direct rewrite" to
something narrower and explicit.

## Inputs

1. `decomp/evidence/inittbl_runtime_opcode_table_accesses.json`
2. `decomp/evidence/battle_runtime_opcode_table_accesses.json`
3. `decomp/evidence/inittbl_0x80_copy_slice.json`
4. `decomp/evidence/battle_runtime_opcode_table_xrefs.json`

## Method

- Added a local headless `Ghidra` helper that scans for reconstructed
  `lui reg, hi16(target)` plus `load/store low16(target)(reg)` pairs.
- Ran that sweep against the two executable files under `Game Data/BATTLE`:
  `INITBTL.PRG` and `BATTLE.PRG`.
- Used explicit disassembly seeds near the already-known copy and dispatch
  routines so the sweep would not depend only on auto-analysis coverage.

## Findings

1. `decomp/evidence/inittbl_runtime_opcode_table_accesses.json` recovered one
   direct write in `INITBTL.PRG`:

   ```text
   800faaf0 lui v0,0x800f
   800fab00 jal 0x800490b0
   800fab04 _sw a0,0x4c28(v0)
   ```

   This is the same init-time store already visible in the focused copy slice,
   but now captured by a reusable access-sweep artifact tied directly to the
   runtime slot address.

2. `decomp/evidence/battle_runtime_opcode_table_accesses.json` recovered one
   direct read in `BATTLE.PRG`:

   ```text
   800bfcf4 lui v1,0x800f
   800bfcfc lw v1,0x4c28(v1)
   800bfd10 jalr v0
   ```

   This matches the earlier local consumer note for `FUN_800BFBB8`.

3. The direct access sweep found no additional absolute-slot accesses to
   `0x800F4C28` in those two local battle executables.

## Interpretation

- The local direct-access picture is now:
  - one init-time `INITBTL.PRG` write of the copied table pointer into
    `0x800F4C28`
  - one `BATTLE.PRG` read that uses the stored pointer for opcode dispatch
- That means the earlier "maybe a later direct static writer rewrites the slot"
  concern is no longer supported by the currently traced local battle
  executables.

## Remaining Limits

- This sweep only answers direct absolute accesses to the slot address itself.
- It does not by itself rule out a later path that reads the pointer once and
  mutates the allocated `0x400`-byte table through that pointer.
- It also does not replace runtime if static tracing of possible indirect table
  mutation stalls.

## Conclusion

For the local battle executables currently in scope, `0x800F4C28` now has one
verified init-time writer and one verified runtime consumer, with no additional
direct slot rewrites recovered by the access sweep. The remaining `0x80`
uncertainty is narrower than before: any later change would need to come from
indirect mutation of the copied table contents or from a runtime-only effect,
not from another recovered absolute-slot write in `INITBTL.PRG` or
`BATTLE.PRG`.
