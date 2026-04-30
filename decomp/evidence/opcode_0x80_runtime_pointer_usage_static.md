# Opcode `0x80` Runtime Pointer-Usage Notes

## Question

After the local `BATTLE.PRG` reader at `FUN_800BFBB8` loads the copied opcode
table pointer from `0x800F4C28`, does it ever store through that pointer or
hand it to another callee that could patch the copied table indirectly?

## Evidence used

1. `decomp/evidence/battle_runtime_opcode_table_accesses.json`
2. `decomp/evidence/battle_runtime_opcode_table_xrefs.json`
3. `decomp/evidence/battle_runtime_opcode_table_pointer_usage.json`

## Static trace

`battle_runtime_opcode_table_pointer_usage.json` starts at local function entry
`0x800BFBB8`, recovers the direct slot read at `0x800BFCFC`, then traces the
derived pointer uses that follow inside the same recovered function body:

```text
800bfcfc lw v1,0x4c28(v1)
800bfd04 addu v0,v0,v1
800bfd08 lw v0,0x0(v0)
800bfd10 jalr v0
```

The derived-usage artifact reports only:

- one `pointer_arithmetic` step at `0x800BFD04`
- one `derived_read` at `0x800BFD08`

It does **not** report:

- any `derived_write`
- any `call_with_tainted_args`

## Conclusion

Within the currently recovered local `BATTLE.PRG` consumer,
`0x800F4C28` is used only to form an indexed table-entry read before `jalr`
dispatch. This pass did not recover an indirect write-back into the copied
opcode table and did not recover the copied table pointer being handed to a
callee from that reader.

## Remaining gap

- This still covers only the currently recovered direct local reader in
  `BATTLE.PRG`.
- It does not yet prove that some other overlay, unrecovered reader, or
  runtime-only path never mutates the copied buffer later.
- The static contradiction is now narrower: within the four currently swept
  local executables that have reproducible base-address notes, the copied table
  has an init-time writer, a runtime reader, no additional direct slot access
  in `SLUS_010.40` or `TITLE.PRG`, and no recovered traced indirect mutation
  path in the one recovered local reader.
