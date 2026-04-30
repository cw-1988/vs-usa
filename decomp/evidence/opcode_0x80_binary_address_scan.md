# Opcode `0x80` Raw Binary Address Scan

## Objective

Test whether any local packaged `.PRG` or `.BIN` asset outside the already
imported executables still shows a static `0x800F4C28` access pattern, so the
remaining `0x80` contradiction can distinguish "missing local code path" from
"runtime-only tie-breaker needed."

## Inputs

1. `decomp/verification/scan_mips_address_accesses.py`
2. `decomp/evidence/runtime_opcode_table_binary_scan.json`
3. `decomp/evidence/opcode_0x80_runtime_slot_access_static.md`
4. `decomp/evidence/opcode_0x80_runtime_pointer_usage_static.md`

## Method

- Added a local raw-binary verification script that scans files for two
  signals:
  - direct little-endian dword literals for the target address
  - MIPS instruction-pair heuristics of the form
    `lui reg, hi16(target)` followed within six instructions by
    `load/store low16(target)(reg)`
- Ran that scan against the local packaged code/data corpus under `Game Data`
  with suffix filters `.PRG`, `.BIN`, and `.40`.
- Kept the target fixed at `0x800F4C28`, the runtime slot that stores the
  copied opcode-table pointer.

## Findings

1. `decomp/evidence/runtime_opcode_table_binary_scan.json` scanned `356`
   packaged files and recovered matches in exactly two of them:
   - `Game Data/BATTLE/INITBTL.PRG`
   - `Game Data/BATTLE/BATTLE.PRG`

2. The recovered instruction-pair matches are the already-known access sites:

   ```text
   Game Data/BATTLE/INITBTL.PRG
   0x000012F0 lui v0,0x800F
   0x00001304 sw a0,0x4C28(v0)

   Game Data/BATTLE/BATTLE.PRG
   0x00057514 lui v1,0x800F
   0x0005751C lw v1,0x4C28(v1)
   ```

3. The scan recovered zero raw little-endian dword literals for `0x800F4C28`
   anywhere in the packaged `.PRG`/`.BIN`/`.40` set.

4. No `Game Data/EFFECT/*.BIN`, no other `Game Data/*/*.PRG`, and no
   `Game Data/SLUS_010.40` match the target-address heuristic.

## Interpretation

- This does not prove that no other battle-adjacent code can touch the copied
  table; a relocatable blob could compute the address another way, or an
  already-known reader could mutate the table indirectly after loading the
  pointer.
- It does prove something narrower and still useful: across the local packaged
  binary set, no additional file currently advertises the same static absolute
  `0x800F4C28` access pattern beyond the two already-known `INITBTL.PRG` and
  `BATTLE.PRG` sites.
- That meaningfully weakens the remaining "some other still-packaged binary is
  the missing direct static path" branch, including the obvious
  battle-adjacent `EFFECT` plugin corpus.

## Conclusion

The local static search now has two independent layers pointing to the same
shape:

- the imported-executable `Ghidra` sweep finds one init-time writer and one
  runtime reader for `0x800F4C28`
- the raw packaged-binary heuristic sweep finds no third file that even
  constructs the same absolute address pattern

That leaves the unresolved `0x80` question in a tighter state than before:
if the copied opcode table is still rewritten later, the remaining branch is
now more plausibly an indirect mutation path or a runtime-only effect than a
simple unrecovered packaged binary with another obvious absolute-slot access.
