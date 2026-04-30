# Opcode `0x80` CLI Pass

## Inputs

- `Game Data/BATTLE/INITBTL.PRG`
- `Game Data/BATTLE/BATTLE.PRG`
- `Game Data/SLUS_010.40`
- `Game Data/TITLE/TITLE.PRG`
- `Game Data/BATTLE/SYSTEM.DAT`
- `decomp/ghidra/export_inittbl_opcode_table.ps1`
- `decomp/ghidra/export_inittbl_0x80_copy_slice.ps1`
- `decomp/ghidra/export_inittbl_system_dat_loader_slice.ps1`
- `decomp/ghidra/export_battle_0x80_sound_cluster_slices.ps1`
- `decomp/ghidra/export_runtime_opcode_table_accesses.ps1`
- `decomp/ghidra/export_inittbl_runtime_opcode_table_accesses.ps1`
- `decomp/ghidra/export_battle_runtime_opcode_table_accesses.ps1`
- `decomp/ghidra/export_slus_runtime_opcode_table_accesses.ps1`
- `decomp/ghidra/export_title_runtime_opcode_table_accesses.ps1`
- `decomp/ghidra/export_battle_runtime_opcode_table_pointer_usage.ps1`
- `decomp/ghidra/ExportFunctionTable.java`
- `decomp/ghidra/DumpInstructions.java`
- `decomp/ghidra/DumpXrefs.java`
- `decomp/ghidra/DumpAddressAccesses.java`
- `decomp/ghidra/TracePointerDerivedAccesses.java`
- `decomp/verification/scan_mips_address_accesses.py`
- `decomp/verification/compare_opcode_table_snapshots.py`
- `decomp/verification/record_runtime_observation.py`
- `decomp/verification/finalize_runtime_observation.py`

## Produced artifacts

- `decomp/evidence/inittbl_opcode_table.json`
- `decomp/evidence/inittbl_0x80_copy_slice.json`
- `decomp/evidence/inittbl_opcode_table_xrefs.json`
- `decomp/evidence/battle_0x80_handler_slices.json`
- `decomp/evidence/battle_sound_candidate_slice.json`
- `decomp/evidence/battle_sound_candidate_xrefs.json`
- `decomp/evidence/battle_sound_dispatch_table.json`
- `decomp/evidence/battle_0x80_sound_cluster_slices.json`
- `decomp/evidence/inittbl_runtime_opcode_table_accesses.json`
- `decomp/evidence/battle_runtime_opcode_table_accesses.json`
- `decomp/evidence/slus_runtime_opcode_table_accesses.json`
- `decomp/evidence/title_runtime_opcode_table_accesses.json`
- `decomp/evidence/battle_runtime_opcode_table_pointer_usage.json`
- `decomp/evidence/inittbl_system_dat_loader_slice.json`
- `decomp/evidence/system_dat_header_words.json`
- `decomp/evidence/runtime_opcode_table_binary_scan.json`
- `decomp/evidence/opcode_0x80_runtime_slot_access_static.md`
- `decomp/evidence/opcode_0x80_runtime_pointer_usage_static.md`
- `decomp/evidence/opcode_0x80_system_dat_static.md`
- `decomp/evidence/opcode_0x80_binary_address_scan.md`
- `decomp/evidence/opcode_0x80_runtime_capture_plan.md`
- `decomp/evidence/opcode_0x80_runtime_observation_template.json`
- `decomp/evidence/opcode_0x80_runtime_observation.json`
- `decomp/evidence/opcode_0x80_runtime_snapshot_compare.json`
- `decomp/evidence/opcode_0x80_runtime_support.md`
- `decomp/evidence/opcode_0x80_runtime_expected_table.bin`

## Packet structure

- This file is the top-level `0x80` proof packet.
- `opcode_0x80_copy_path_static.md` is the focused support note for the
  `0x800FAF7C -> 0x800F4C28` copy path.
- `opcode_0x80_sound_cluster_static.md` is the focused support note for the
  nearby `0x800BA2E0` sound-family interpretation.
- `opcode_0x80_runtime_slot_access_static.md` is the focused support note for
  direct absolute accesses to runtime slot `0x800F4C28` across the currently
  importable local executables with known base-address notes.
- `opcode_0x80_runtime_pointer_usage_static.md` is the focused support note
  for how the recovered `BATTLE.PRG` reader actually uses the copied table
  pointer after loading it from `0x800F4C28`.
- `opcode_0x80_system_dat_static.md` is the focused support note for why the
  locally loaded `SYSTEM.DAT` blob should no longer be treated as the main
  missing executable-overlay candidate in this pass.
- `opcode_0x80_binary_address_scan.md` is the focused support note for the raw
  packaged-binary heuristic scan that checks whether any other local
  `.PRG`/`.BIN` asset still builds the same absolute `0x800F4C28` access
  pattern.
- `opcode_0x80_runtime_capture_plan.md` is the focused support note for the
  runtime tie-breaker: exact watch addresses, expected dump points, and the
  compare-helper invocation for the copied table at `0x800F4C28`.
- `opcode_0x80_runtime_observation_template.json` is the structured handoff
  file for recording breakpoint hits, dump paths, and final runtime
  observations during that pass.
- `opcode_0x80_runtime_observation.json` is the checked-in scaffolded
  observation packet for the next runtime pass; it already carries the planned
  breakpoints, expected dump paths, and current missing-snapshot checklist.
- `record_runtime_observation.py` is the CLI helper for appending snapshot
  paths, breakpoint hits, dispatches, mutations, and notes into that checked-in
  packet during the runtime pass instead of hand-editing JSON; it can also
  import changed compare-report rows back into `table_mutations`.
- `opcode_0x80_runtime_snapshot_compare.json` is the generated compare report
  that currently records the missing dump files and should refresh in place
  once real RAM snapshots are added; it now also records the baseline export
  hash plus per-dump size/hash metadata for any compared snapshots.
- `opcode_0x80_runtime_support.md` is the generated runtime support note that
  now doubles as a ready-to-use runtime checklist because it includes the
  planned breakpoints, missing snapshot captures, and the reconstructed
  baseline blob metadata even before the dumps exist.
- `opcode_0x80_runtime_expected_table.bin` is the reconstructed binary-derived
  baseline table image that the compare/finalize helpers now refresh alongside
  the JSON report so a runtime pass has a stable byte-for-byte artifact to
  diff against.

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

- `battle_sound_candidate_slice.json` still shows `0x800BA2E0` consuming the
  same four-byte argument block as the visible sound family.
- `battle_sound_candidate_xrefs.json` now recovers a direct local data xref
  from `0x800E9F30 -> 0x800BA2E0`.
- `battle_sound_dispatch_table.json` then exports that `0x800E9F30` table as
  an eight-entry local `BATTLE.PRG` handler family containing `0x800BA2E0`,
  `0x800BA35C`, `0x800BA39C`, and the already-visible `0x800BA3E4+`
  neighborhood.
- `battle_0x80_sound_cluster_slices.json` now covers that fuller local family,
  which makes `0x800BA2E0` look like a member of a separate sound
  subdispatch block rather than a hidden replacement for the copied `0x80`
  slot.
- See `opcode_0x80_sound_cluster_static.md` for the local neighborhood case.

## Current conclusion

- `0x80` is now **runtime needed**, not confirmed.
- Local binary evidence now proves both the copied initial dispatch slot
  (`0x800B66E4`) and the init-time table copy into runtime slot `0x800F4C28`.
- A widened local access sweep of `INITBTL.PRG`, `BATTLE.PRG`,
  `SLUS_010.40`, and `TITLE.PRG` now finds one direct init-time write to
  `0x800F4C28`, one direct runtime read from it, and no additional recovered
  direct slot accesses in the other importable executables with known base
  notes.
- A local pointer-usage trace of the recovered `BATTLE.PRG` reader at
  `FUN_800BFBB8` now shows only pointer arithmetic plus one indexed table-entry
  read before `jalr`, with no recovered indirect write-back or tainted
  pointer-argument call in that local consumer.
- A local `INITBTL.PRG` loader slice plus the first eight dwords of the local
  `SYSTEM.DAT` file now show `SYSTEM.DAT` being loaded as offset-indexed
  asset/payload data and then freed, which weakens the old "`SYSTEM.DAT`
  might be the missing code overlay" branch.
- A raw packaged-binary heuristic scan across `356` local `.PRG`/`.BIN`/`.40`
  files now recovers the same absolute `0x800F4C28` access pattern in exactly
  two files, `INITBTL.PRG` and `BATTLE.PRG`, with no third match in the
  `EFFECT` plugin corpus or elsewhere in `Game Data`.
- The nearby sound-shaped helper keeps `SoundEffects0` plausible as a working
  placeholder, but the local static picture now favors "`0x80-0x82` are real
  copied stubs, while `0x800BA2E0` belongs to a separate local sound
  subdispatch family that also contains the visible `0x83+` handlers."
- The remaining unresolved question is no longer "is `0x800BA2E0` secretly the
  real `0x80` target?" or "is there another obvious packaged direct slot
  rewrite?" but "does any indirect path mutate the copied table contents behind
  `0x800F4C28` before dispatch?" Static evidence is now narrow enough that
  runtime is the clean next tie-breaker.
- The runtime follow-up is now concretely staged: capture the copied table
  after init and before candidate dispatch, compare those dumps against the
  binary baseline with
  `decomp/verification/compare_opcode_table_snapshots.py`, and record the
  breakpoint results in
  `decomp/evidence/opcode_0x80_runtime_observation.json` with
  `decomp/verification/record_runtime_observation.py`, then refresh the
  compare report and support note in place with
  `decomp/verification/finalize_runtime_observation.py --in-place`. If the
  focus opcodes changed, import those compare-report rows back into
  `table_mutations` with
  `decomp/verification/record_runtime_observation.py import-compare
  --replace-derived --finalize` so the explicit rewritten handlers live in the
  checked-in packet instead of only in the compare JSON.
