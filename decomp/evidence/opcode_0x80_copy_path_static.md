# Opcode `0x80` Copy-Path Static Notes

## Goal

Tighten the `0x80-0x84` contradiction by proving how the exported
`INITBTL.PRG` opcode table reaches runtime state before looking for any later
patch site.

## Static ownership chain

1. `_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c` defines the battle
   opcode table as the local static array `D_800FAF7C`.
2. That array contains the same `0x80 -> 0x800B66E4` mapping already exported
   in `decomp/evidence/inittbl_opcode_table.json`.
3. `_initScriptFunctionTable()` allocates a 0x400-byte runtime buffer in
   `D_800F4C28` and copies the entire 256-entry table into it with:

```c
D_800F4C28 = vs_main_allocHeap(0x400);
vs_main_memcpy(D_800F4C28, D_800FAF7C, 0x400);
```

4. `_refs/rood-reverse/src/BATTLE/INITBTL.PRG/18.c` calls
   `_initScriptFunctionTable()` from `func_800FA35C()`, which is the broader
   battle bootstrap path.

## What this resolves

- The exported table at `0x800FAF7C` is not just a detached binary artifact.
  It is compiled into `INITBTL.PRG` as `D_800FAF7C`.
- Runtime battle state starts from a heap copy of that exact table.
- The `0x80-0x82 -> 0x800B66E4` stub cluster is therefore the verified initial
  runtime state, not just a static export snapshot.

## What remains unresolved

- No static patch writer for `D_800F4C28` was identified in the current indexed
  sources during this pass.
- No direct static consumer/dispatcher of `D_800F4C28` surfaced in the current
  indexed sources either, so the exact live dispatch path still needs to be
  traced.
- Because of that, the nearby sound-shaped helper at `0x800BA2E0` remains only
  a competing semantic candidate, not a proven replacement for the copied
  `0x800B66E4` entry.

## Current conclusion

- Static analysis now proves the owner, initializer, and initial copy path for
  the battle opcode table.
- The contradiction has narrowed from "did the export pick the wrong slot?" to
  "does some later runtime path rewrite or bypass the copied `D_800F4C28`
  entry for `0x80-0x84`?"
- Runtime work is still not justified yet; the next static step is to find the
  live table consumer or any overlay-time patch writer.
