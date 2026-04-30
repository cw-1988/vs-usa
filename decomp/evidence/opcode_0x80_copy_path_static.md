# Opcode `0x80` Copy-Path Static Notes

## Goal

Tighten the `0x80-0x84` contradiction by proving how the exported
`INITBTL.PRG` opcode table reaches runtime state before looking for any later
patch site.

## Local binary evidence

1. `decomp/evidence/inittbl_opcode_table.json` exports the `INITBTL.PRG`
   table at `0x800FAF7C` and shows `0x80 -> 0x800B66E4`.
2. `decomp/evidence/inittbl_0x80_copy_slice.json` captures the candidate
   init-time copy routine at `0x800FAAAC`.
3. That slice shows:

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

4. `0x8010:0x5084` resolves to `0x800FAF7C`, so the slice shows:
   - allocation of a `0x400` byte runtime buffer
   - storage of that buffer to runtime slot `0x800F4C28`
   - a `0x400` byte copy from the exported table at `0x800FAF7C`

## What this resolves

- The exported table at `0x800FAF7C` is not a detached binary artifact.
- Runtime battle state starts from a copied `0x400` byte table stored in
  `0x800F4C28`.
- The `0x80-0x82 -> 0x800B66E4` stub cluster is therefore the verified initial
  runtime state, not just a static export snapshot.

## What remains unresolved

- `decomp/evidence/inittbl_opcode_table_xrefs.json` did not recover a direct
  headless xref to `0x800FAF7C` under the current auto-analysis settings.
- No later static patch writer for `0x800F4C28` was identified in this pass.
- No direct live dispatch consumer of `0x800F4C28` was identified in this pass.

## Current conclusion

- Local binary evidence now proves the exported table, the runtime destination
  slot, and the init-time copy sequence.
- The contradiction has narrowed from "did the export pick the wrong slot?" to
  "does some later runtime path rewrite or bypass the copied `0x800F4C28`
  entry for `0x80-0x84`?"
- Runtime work is still not justified yet; the next static step is to recover
  the live dispatch consumer or a later patch path.
