# Opcode `0x80` `SYSTEM.DAT` Loader Check

## Objective

Resolve whether `Game Data/BATTLE/SYSTEM.DAT` is a plausible late static code
overlay in the remaining `0x80` copy/patch contradiction, or whether the local
binary evidence instead anchors it as a data payload loaded by
`INITBTL.PRG`.

## Inputs

1. `decomp/evidence/inittbl_system_dat_loader_slice.json`
2. `decomp/evidence/system_dat_header_words.json`
3. `Game Data/BATTLE/SYSTEM.DAT`

## Method

- Dumped a local `INITBTL.PRG` instruction slice starting at `0x800F989C`,
  the `_loadSystemDat` entry identified during the current battle bootstrap
  pass.
- Compared the loader's first eight `lw`-driven offsets against the first
  eight little-endian dwords from the local `SYSTEM.DAT` file header.
- Checked whether the recovered control flow looks like executable-overlay
  setup or a plain data/image unpack path.

## Findings

1. `inittbl_system_dat_loader_slice.json` starts with:

   ```text
   800f98a0 lui a0,0x2
   800f98a4 ori a0,a0,0xe000
   800f98ac jal 0x80043e3c
   800f98b4 li a0,0x56b
   800f98b8 lui a1,0x2
   800f98bc ori a1,a1,0xe000
   800f98c4 jal 0x8004493c
   ```

   The function allocates `0x2E000` bytes, then loads file/LBA `0x56B` into
   that buffer before any header walks begin.

2. The same slice then repeatedly treats the loaded buffer as offset-indexed
   structured data, for example:

   ```text
   800f98cc lw v0,0x0(s0)
   800f98d4 addu v1,s0,v0
   800f98d8 lhu v0,0x0(v1)
   800f9904 jal 0x800288fc
   800f990c jal 0x80028650
   ```

   That pattern repeats for offsets at `0x0`, `0x4`, `0xC`, `0x10`, `0x14`,
   and `0x18`, with the loaded records consumed as rectangle/image arguments
   plus one additional payload call at `0x800CA9C0`.

3. `system_dat_header_words.json` shows the first eight dwords of the local
   file are:

   ```text
   0x00000020
   0x00007028
   0x0000E830
   0x0000E854
   0x0001085C
   0x00012864
   0x0001A86C
   0x0001AA70
   ```

   Those are monotonic in-file offsets, not an executable header or a table of
   code entry points.

4. The loader ends by freeing the buffer:

   ```text
   800f9a8c lw a0,0x1c(s0)
   800f9a90 jal 0x800ca9c0
   800f9a98 jal 0x80043c60
   800f9a9c _move a0,s0
   ```

   So the local static path loads `SYSTEM.DAT` as transient asset/config data,
   not as a long-lived imported executable with a code dispatch base.

## Interpretation

- The current local evidence does not support treating `SYSTEM.DAT` as a
  missing executable overlay candidate for the `0x80` runtime-slot rewrite
  question.
- `SYSTEM.DAT` is now locally anchored as a data blob whose header stores file
  offsets consumed by image/payload routines in `_loadSystemDat`.
- That removes one of the weaker speculative branches from the remaining
  contradiction and shifts the unresolved path toward:
  - some other code-bearing battle-adjacent binary not yet swept, if one
    exists
  - or a runtime-only/indirect table mutation path

## Conclusion

`SYSTEM.DAT` should no longer be treated as the primary unswept late static
code candidate in the `0x80` copy/patch campaign. The local binary evidence
shows it being loaded, parsed by offsets, consumed as asset/payload data, and
freed, which narrows the remaining `0x80` uncertainty without needing to
invent a fake import-base note for this file.
