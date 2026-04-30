# Opcode `0x80` Runtime-Dispatch Static Notes

## Goal

Recover the live `BATTLE.PRG` consumer of the copied runtime opcode table at
`0x800F4C28` before escalating to runtime tracing.

## Local binary evidence

1. `decomp/evidence/inittbl_0x80_copy_slice.json` already showed the init-time
   copy path storing a freshly allocated `0x400` byte buffer into
   `0x800F4C28` and copying the exported `INITBTL.PRG` table into it.
2. `decomp/evidence/battle_runtime_opcode_table_xrefs.json` now recovers a
   direct local `BATTLE.PRG` read xref from `0x800BFCFC`.
3. The xref window shows this dispatch shape:

```text
800bfcf8 lbu v0,0x0(s0)
800bfcfc lw v1,0x4c28(v1)
800bfd00 sll v0,v0,0x2
800bfd04 addu v0,v0,v1
800bfd08 lw v0,0x0(v0)
800bfd10 jalr v0
```

4. That sequence proves a live consumer path in `FUN_800BFBB8`:
   - read the opcode byte from the current script cursor
   - load the runtime table base from `0x800F4C28`
   - index by `opcode * 4`
   - fetch the handler pointer from the copied table
   - dispatch through that pointer with `jalr`

## What this resolves

- The copied table at `0x800F4C28` is not only an initialization artifact.
- Local static evidence now shows a direct `BATTLE.PRG` consumer that dispatches
  through the runtime table instead of bypassing it for `0x80-0x84`.
- The older "maybe some hidden sound-side helper is called directly instead"
  contradiction is narrowed again: the active consumer reads the runtime table
  slot first.

## What remains unresolved

- This pass did not recover a later static writer that rewrites `0x800F4C28`
  after the init-time copy.
- The current evidence therefore still stops short of proving that the copied
  `0x800B66E4` entry for `0x80` is never patched later.

## Current conclusion

- Local static evidence now covers the full path from exported `INITBTL.PRG`
  table to copied runtime buffer to live `BATTLE.PRG` dispatch consumer.
- The remaining static question for `0x80` is no longer "is there a consumer?"
  or "is there a bypass path?" but only "is there a later writer that mutates
  `0x800F4C28` before this consumer executes `0x80`?"
