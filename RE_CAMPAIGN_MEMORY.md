# RE Campaign Memory

## Campaign Goal

Build a verified opcode-to-handler map for the battle-script system before
promoting semantic names. The campaign stays opcode-first: finish table
ownership, copy/patch tracing, handler coverage, shared-handler clustering, and
contradiction tracking before turning tentative labels into decoder-facing
claims.

## Evidence Discipline

- The original binary plus runtime behavior are the ground truth.
- Artifacts under `decomp/` are the local evidence authority for this ledger.
- [`_refs/rood-reverse`](_refs/rood-reverse) is hint-only and may suggest
  targets, addresses, or candidate names.
- If a helper-repo clue matters to a target, convert it into a local export,
  proof packet, verification result, or runtime capture before citing it here
  as evidence.
- Helper provenance may be mentioned, but `Priority Targets`,
  `Known Conflicts`, and `Artifacts Index` should point first to local
  artifacts.

## Current Phase

Current phase: Pass 3 - Copy/patch reconciliation

## Status Legend

- `unstarted`
- `in_progress`
- `covered`
- `conflicted`
- `runtime_needed`
- `confirmed`

## Pass Plan

1. `Pass 0 - Bootstrap and inventory`
   - Goal: identify all opcode-table owners, known initializers, copy sites,
     and likely patch points.
   - Expected outputs:
     - master list of tables
     - overlay ownership notes
     - first artifact index entries
   - Exit condition: every known battle-script table has an owner and
     initializer note.
2. `Pass 1 - Table export coverage`
   - Goal: export binary-derived entries for every known relevant opcode table.
   - Expected outputs:
     - JSON table exports under `decomp/evidence`
     - wrapper scripts under `decomp/ghidra`
   - Exit condition: all targeted tables have reproducible exports with correct
     base-address notes.
3. `Pass 2 - Handler coverage and classification`
   - Goal: map every exported opcode to a handler address and classify unique
     handlers.
   - Expected outputs:
     - coverage report
     - shared-handler map
   - Exit condition: every opcode in scope has a handler mapping and
     provisional class.
4. `Pass 3 - Copy/patch reconciliation`
   - Goal: determine whether runtime tables are copied only once or patched
     later.
   - Expected outputs:
     - copy-site notes
     - patch-site notes
     - unresolved runtime-needed list
   - Exit condition: every conflict is labeled either `static_resolved` or
     `runtime_needed`.
5. `Pass 4 - Semantic proof packets`
   - Goal: produce focused proof packets only for the high-value or conflicted
     opcodes.
   - Expected outputs:
     - one markdown proof packet per disputed opcode family
     - linked binary exports and script examples
   - Exit condition: all priority targets have either `confirmed`,
     `tentative`, or `conflicted` status with explicit evidence.
6. `Pass 5 - Naming and decoder updates`
   - Goal: only after the earlier passes, promote safe names into
     `dump_mpd_script.py` and opcode notes.
   - Expected outputs:
     - decoder naming changes
     - conclusion-note updates
   - Exit condition: no name promotion lacks a proof-packet anchor.
7. `Pass 6 - Audit and maintenance`
   - Goal: keep the campaign from drifting.
   - Expected outputs:
     - contradiction audit
     - stale-artifact audit
     - missing-export audit
   - Exit condition: ledger and artifacts still agree.

## Priority Targets

| target | current_status | table_owner | handler_owner | best_current_name | blocking_question | next_pass | evidence_links |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `opcode 0x80` | `runtime_needed` | `INITBTL.PRG` static table at `0x800FAF7C`, copied into runtime slot `0x800F4C28` by the locally dumped init-time routine at `0x800FAAAC` | Static slot `0x800B66E4`; former competing helper `0x800BA2E0` is now anchored to a local `BATTLE.PRG` sound subdispatch table at `0x800E9F30` with siblings `0x800BA35C/39C/3E4/404/444/470/494`; live `BATTLE.PRG` consumer `FUN_800BFBB8` now reads `0x800F4C28`, uses it only for pointer arithmetic plus one indexed table-entry read in the new local trace, and dispatches via `jalr`; widened direct-slot sweeps across `SLUS_010.40` and `TITLE.PRG` recover no additional accesses; local `_loadSystemDat` tracing now anchors `SYSTEM.DAT` as offset-indexed data payload rather than a missing executable overlay; raw packaged-binary scanning across `.PRG`/`.BIN`/`.40` files finds the same absolute `0x800F4C28` access pattern only in `INITBTL.PRG` and `BATTLE.PRG`; the next pass now has a concrete runtime capture note, a checked-in observation scaffold, and dump-vs-baseline compare/finalize helpers instead of an open-ended `PCSX-Redux` ask | `SoundEffects0` placeholder only | Do runtime dumps from `0x800F4C28` ever diverge from the binary baseline before candidate `0x80-0x82` dispatch, and if so which handler addresses replace the static `0x800B66E4` stub? | `Pass 3 - Copy/patch reconciliation` | [`opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md), [`opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md), [`opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md), [`opcode_0x80_runtime_dispatch_static.md`](decomp/evidence/opcode_0x80_runtime_dispatch_static.md), [`opcode_0x80_runtime_slot_access_static.md`](decomp/evidence/opcode_0x80_runtime_slot_access_static.md), [`opcode_0x80_runtime_pointer_usage_static.md`](decomp/evidence/opcode_0x80_runtime_pointer_usage_static.md), [`opcode_0x80_system_dat_static.md`](decomp/evidence/opcode_0x80_system_dat_static.md), [`opcode_0x80_binary_address_scan.md`](decomp/evidence/opcode_0x80_binary_address_scan.md), [`opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md), [`opcode_0x80_runtime_observation_template.json`](decomp/evidence/opcode_0x80_runtime_observation_template.json), [`opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json), [`opcode_0x80_runtime_snapshot_compare.json`](decomp/evidence/opcode_0x80_runtime_snapshot_compare.json), [`opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md), [`inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json), [`inittbl_0x80_copy_slice.json`](decomp/evidence/inittbl_0x80_copy_slice.json), [`inittbl_runtime_opcode_table_accesses.json`](decomp/evidence/inittbl_runtime_opcode_table_accesses.json), [`inittbl_system_dat_loader_slice.json`](decomp/evidence/inittbl_system_dat_loader_slice.json), [`system_dat_header_words.json`](decomp/evidence/system_dat_header_words.json), [`battle_0x80_handler_slices.json`](decomp/evidence/battle_0x80_handler_slices.json), [`battle_sound_candidate_slice.json`](decomp/evidence/battle_sound_candidate_slice.json), [`battle_sound_candidate_xrefs.json`](decomp/evidence/battle_sound_candidate_xrefs.json), [`battle_sound_dispatch_table.json`](decomp/evidence/battle_sound_dispatch_table.json), [`battle_0x80_sound_cluster_slices.json`](decomp/evidence/battle_0x80_sound_cluster_slices.json), [`battle_runtime_opcode_table_xrefs.json`](decomp/evidence/battle_runtime_opcode_table_xrefs.json), [`battle_runtime_opcode_table_accesses.json`](decomp/evidence/battle_runtime_opcode_table_accesses.json), [`battle_runtime_opcode_table_pointer_usage.json`](decomp/evidence/battle_runtime_opcode_table_pointer_usage.json), [`slus_runtime_opcode_table_accesses.json`](decomp/evidence/slus_runtime_opcode_table_accesses.json), [`title_runtime_opcode_table_accesses.json`](decomp/evidence/title_runtime_opcode_table_accesses.json), [`runtime_opcode_table_binary_scan.json`](decomp/evidence/runtime_opcode_table_binary_scan.json), [`compare_opcode_table_snapshots.py`](decomp/verification/compare_opcode_table_snapshots.py), [`finalize_runtime_observation.py`](decomp/verification/finalize_runtime_observation.py) |

## Known Conflicts

### `0x80`: copied initial stub vs possible later runtime rewrite/bypass

- What static evidence says: `decomp/evidence/inittbl_opcode_table.json` maps
  `0x80 -> 0x800B66E4`, and
  `decomp/evidence/battle_0x80_handler_slices.json` shows a real binary stub
  (`jr ra; clear v0`). `0x81` and `0x82` also share that same target.
  `decomp/evidence/inittbl_0x80_copy_slice.json` shows a local init-time
  routine allocating `0x400` bytes, storing the destination in `0x800F4C28`,
  and copying `0x400` bytes from `0x800FAF7C`, so the stubbed table state is
  also the proven initial runtime state. `decomp/evidence/battle_sound_candidate_xrefs.json`
  and `decomp/evidence/battle_sound_dispatch_table.json` now place
  `0x800BA2E0` into a local `BATTLE.PRG` eight-entry subdispatch table at
  `0x800E9F30`, alongside `0x800BA35C`, `0x800BA39C`, and the visible
  `0x800BA3E4+` sound-family neighborhood. `decomp/evidence/battle_runtime_opcode_table_xrefs.json`
  now recovers a direct local read xref in `FUN_800BFBB8` that loads
  `0x800F4C28`, indexes by the opcode byte, loads the pointed-to handler, and
  dispatches through `jalr`, proving a live consumer of the copied runtime
  table. `decomp/evidence/inittbl_runtime_opcode_table_accesses.json` and
  `decomp/evidence/battle_runtime_opcode_table_accesses.json` now add a direct
  absolute-slot access sweep across the two local battle executables, finding
  one init-time `INITBTL.PRG` write to `0x800F4C28` and one `BATTLE.PRG` read
  from it, with no additional direct slot accesses recovered in the widened
  local sweep across `INITBTL.PRG`, `BATTLE.PRG`, `SLUS_010.40`, and
  `TITLE.PRG`. `decomp/evidence/inittbl_system_dat_loader_slice.json` plus
  `decomp/evidence/system_dat_header_words.json` now also anchor
  `Game Data/BATTLE/SYSTEM.DAT` as a locally loaded offset/header data blob
  that is consumed and freed by `_loadSystemDat`, not as a recovered code
  overlay that still needs a `BinaryLoader` base note.
  `decomp/evidence/runtime_opcode_table_binary_scan.json` now adds a second
  static sweep layer across `356` packaged `.PRG`/`.BIN`/`.40` files,
  recovering the same `0x800F4C28` absolute access pattern only in
  `Game Data/BATTLE/INITBTL.PRG` and `Game Data/BATTLE/BATTLE.PRG`.
- What competing evidence says:
  There is no longer a strong static case that `0x800BA2E0` is the hidden
  direct `0x80` target, and the bypass half of the contradiction has now been
  weakened by the direct `0x800F4C28` consumer xref plus the absolute-slot
  access sweep. `decomp/evidence/battle_runtime_opcode_table_pointer_usage.json`
  now narrows the recovered local `BATTLE.PRG` reader even further: inside
  `FUN_800BFBB8`, the copied pointer is only used for pointer arithmetic plus
  one indexed table-entry read before `jalr`, with no recovered indirect
  write-back or tainted pointer-argument call. The remaining contradiction is
  therefore narrower still: some other unrecovered path could still mutate the
  copied `0x400`-byte table indirectly even if the currently recovered reader
  does not. The new raw packaged-binary scan also weakens the last obvious
  "some other local asset contains another direct absolute access" branch by
  finding no third match in the packaged corpus, including `Game Data/EFFECT`.
- What is still missing: any static or runtime evidence that the copied table
  contents themselves are patched after the verified init-time copy, plus any
  locally anchored proof of an indirect patch path that changes the copied
  table contents after init. The missing runtime capture now has a concrete
  local artifact path:
  `decomp/evidence/opcode_0x80_runtime_capture_plan.md`,
  `decomp/evidence/opcode_0x80_runtime_observation_template.json`,
  `decomp/evidence/opcode_0x80_runtime_observation.json`, and
  `decomp/verification/compare_opcode_table_snapshots.py` together define the
  dump points, compare step, result-recording format, and currently missing
  snapshot checklist.
- Is runtime justified yet: yes. The direct-slot rewrite question is now weak
  across every currently importable local executable with a known base note,
  the one recovered local reader has already been traced through without
  finding a write-back path, `SYSTEM.DAT` is locally narrowed to payload data
  rather than code, and the raw packaged-binary scan recovered no third file
  with the same absolute access pattern. `PCSX-Redux` is now the clean
  tie-breaker for whether the copied table contents themselves ever change at
  runtime.

## Artifacts Index

### Table exports

- [`decomp/evidence/inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json)
- [`decomp/evidence/inittbl_opcode_table_xrefs.json`](decomp/evidence/inittbl_opcode_table_xrefs.json)
- [`decomp/evidence/battle_sound_candidate_xrefs.json`](decomp/evidence/battle_sound_candidate_xrefs.json)
- [`decomp/evidence/battle_sound_dispatch_table.json`](decomp/evidence/battle_sound_dispatch_table.json)
- [`decomp/evidence/battle_runtime_opcode_table_xrefs.json`](decomp/evidence/battle_runtime_opcode_table_xrefs.json)
- [`decomp/evidence/inittbl_runtime_opcode_table_accesses.json`](decomp/evidence/inittbl_runtime_opcode_table_accesses.json)
- [`decomp/evidence/battle_runtime_opcode_table_accesses.json`](decomp/evidence/battle_runtime_opcode_table_accesses.json)
- [`decomp/evidence/slus_runtime_opcode_table_accesses.json`](decomp/evidence/slus_runtime_opcode_table_accesses.json)
- [`decomp/evidence/title_runtime_opcode_table_accesses.json`](decomp/evidence/title_runtime_opcode_table_accesses.json)
- [`decomp/evidence/battle_runtime_opcode_table_pointer_usage.json`](decomp/evidence/battle_runtime_opcode_table_pointer_usage.json)
- [`decomp/evidence/inittbl_system_dat_loader_slice.json`](decomp/evidence/inittbl_system_dat_loader_slice.json)
- [`decomp/evidence/system_dat_header_words.json`](decomp/evidence/system_dat_header_words.json)
- [`decomp/evidence/runtime_opcode_table_binary_scan.json`](decomp/evidence/runtime_opcode_table_binary_scan.json)
- [`decomp/verification/compare_opcode_table_snapshots.py`](decomp/verification/compare_opcode_table_snapshots.py)
- [`decomp/verification/finalize_runtime_observation.py`](decomp/verification/finalize_runtime_observation.py)
- [`decomp/evidence/opcode_0x80_runtime_snapshot_compare.json`](decomp/evidence/opcode_0x80_runtime_snapshot_compare.json)

### Handler slices

- [`decomp/evidence/battle_0x80_handler_slices.json`](decomp/evidence/battle_0x80_handler_slices.json)
- [`decomp/evidence/battle_sound_candidate_slice.json`](decomp/evidence/battle_sound_candidate_slice.json)
- [`decomp/evidence/inittbl_0x80_copy_slice.json`](decomp/evidence/inittbl_0x80_copy_slice.json)
- [`decomp/evidence/battle_0x80_sound_cluster_slices.json`](decomp/evidence/battle_0x80_sound_cluster_slices.json)

### Reconciliation reports

- [`decomp/evidence/opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md)
- [`decomp/evidence/opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md)
- [`decomp/evidence/opcode_0x80_runtime_dispatch_static.md`](decomp/evidence/opcode_0x80_runtime_dispatch_static.md)
- [`decomp/evidence/opcode_0x80_runtime_slot_access_static.md`](decomp/evidence/opcode_0x80_runtime_slot_access_static.md)
- [`decomp/evidence/opcode_0x80_runtime_pointer_usage_static.md`](decomp/evidence/opcode_0x80_runtime_pointer_usage_static.md)
- [`decomp/evidence/opcode_0x80_system_dat_static.md`](decomp/evidence/opcode_0x80_system_dat_static.md)
- [`decomp/evidence/opcode_0x80_binary_address_scan.md`](decomp/evidence/opcode_0x80_binary_address_scan.md)
- [`decomp/evidence/opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md)
- [`decomp/evidence/opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md)

### Proof packets

- [`decomp/evidence/opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md)
- [`decomp/evidence/opcode_0x80_runtime_observation_template.json`](decomp/evidence/opcode_0x80_runtime_observation_template.json)
- [`decomp/evidence/opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json)

## Session Handoff

- `last completed step`: upgraded the reusable runtime-observation finalizer so
  partial packets now render planned breakpoints plus missing dump captures,
  then checked in a scaffolded
  `decomp/evidence/opcode_0x80_runtime_observation.json` with aligned compare
  report and runtime support note for the next `PCSX-Redux` pass
- `next recommended step`: run the capture plan in
  `decomp/evidence/opcode_0x80_runtime_capture_plan.md`, export at least an
  `after_init` and `pre_dispatch` dump from `0x800F4C28`, compare them with
  `decomp/verification/finalize_runtime_observation.py --in-place`, and record
  the breakpoint hits plus any dispatch targets in
  `decomp/evidence/opcode_0x80_runtime_observation.json`
- `do not forget`: store the raw dump files and the compare report under
  `decomp/evidence`; if the table changes, capture the rewritten handler
  addresses for `0x80-0x82` explicitly rather than summarizing them only in
  prose, keep the generated runtime support note linked alongside the updated
  observation JSON, and refresh the scaffolded compare/support files instead of
  creating parallel ad-hoc notes

## Completed Milestones

- `2026-04-30`: added the master campaign ledger and aligned the main workflow
  docs around it. Links: [`README.md`](README.md),
  [`AI_RE_PASS_WORKFLOW.md`](AI_RE_PASS_WORKFLOW.md),
  [`CLI_DECOMPILATION_WORKFLOW.md`](CLI_DECOMPILATION_WORKFLOW.md),
  [`DECOMPILATION_STRATEGY.md`](DECOMPILATION_STRATEGY.md),
  [`decomp/README.md`](decomp/README.md)
- `2026-04-30`: indexed the current `0x80` static conflict packet into the
  campaign memory. Links:
  [`decomp/evidence/opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md),
  [`decomp/evidence/inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json),
  [`decomp/evidence/battle_0x80_handler_slices.json`](decomp/evidence/battle_0x80_handler_slices.json),
  [`decomp/evidence/battle_sound_candidate_slice.json`](decomp/evidence/battle_sound_candidate_slice.json)
- `2026-04-30`: rebuilt the `0x80` copy-path and sound-neighborhood notes from
  local `Ghidra` exports and instruction dumps, keeping `_refs/rood-reverse`
  in hint-only role. Links:
  [`decomp/evidence/opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md),
  [`decomp/evidence/opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md),
  [`decomp/evidence/inittbl_0x80_copy_slice.json`](decomp/evidence/inittbl_0x80_copy_slice.json),
  [`decomp/evidence/battle_0x80_sound_cluster_slices.json`](decomp/evidence/battle_0x80_sound_cluster_slices.json)
- `2026-04-30`: recovered a direct local xref from `0x800E9F30` to
  `0x800BA2E0`, exported the surrounding eight-entry `BATTLE.PRG`
  sound-dispatch table, and expanded the local sound-family slice set. Links:
  [`decomp/evidence/battle_sound_candidate_xrefs.json`](decomp/evidence/battle_sound_candidate_xrefs.json),
  [`decomp/evidence/battle_sound_dispatch_table.json`](decomp/evidence/battle_sound_dispatch_table.json),
  [`decomp/evidence/battle_0x80_sound_cluster_slices.json`](decomp/evidence/battle_0x80_sound_cluster_slices.json)
- `2026-04-30`: recovered a direct local `BATTLE.PRG` consumer for
  `0x800F4C28`, proving that the copied runtime opcode table is read, indexed
  by opcode byte, and dispatched through `jalr` before any runtime-only claims.
  Links:
  [`decomp/evidence/battle_runtime_opcode_table_xrefs.json`](decomp/evidence/battle_runtime_opcode_table_xrefs.json),
  [`decomp/evidence/opcode_0x80_runtime_dispatch_static.md`](decomp/evidence/opcode_0x80_runtime_dispatch_static.md)
- `2026-04-30`: added a reusable local direct-address access sweep, then used
  it to recover the `INITBTL.PRG` write to `0x800F4C28`, the `BATTLE.PRG` read
  from it, and the absence of any other recovered direct slot accesses in those
  two battle executables. Links:
  [`decomp/evidence/inittbl_runtime_opcode_table_accesses.json`](decomp/evidence/inittbl_runtime_opcode_table_accesses.json),
  [`decomp/evidence/battle_runtime_opcode_table_accesses.json`](decomp/evidence/battle_runtime_opcode_table_accesses.json),
  [`decomp/evidence/opcode_0x80_runtime_slot_access_static.md`](decomp/evidence/opcode_0x80_runtime_slot_access_static.md)
- `2026-04-30`: added a reusable pointer-derived access tracer, then used it
  on `FUN_800BFBB8` to show that the recovered local `BATTLE.PRG` reader only
  performs pointer arithmetic plus one indexed table-entry read from the copied
  runtime opcode table before `jalr`, with no recovered indirect write-back in
  that consumer. Links:
  [`decomp/evidence/battle_runtime_opcode_table_pointer_usage.json`](decomp/evidence/battle_runtime_opcode_table_pointer_usage.json),
  [`decomp/evidence/opcode_0x80_runtime_pointer_usage_static.md`](decomp/evidence/opcode_0x80_runtime_pointer_usage_static.md)
- `2026-04-30`: refactored the runtime-slot access sweep into a reusable
  wrapper, then widened the direct `0x800F4C28` scan to `SLUS_010.40` and
  `TITLE.PRG`; both extra imports recovered zero additional direct accesses,
  further narrowing the static rewrite question outside the battle overlays.
  Links:
  [`decomp/ghidra/export_runtime_opcode_table_accesses.ps1`](decomp/ghidra/export_runtime_opcode_table_accesses.ps1),
  [`decomp/evidence/slus_runtime_opcode_table_accesses.json`](decomp/evidence/slus_runtime_opcode_table_accesses.json),
  [`decomp/evidence/title_runtime_opcode_table_accesses.json`](decomp/evidence/title_runtime_opcode_table_accesses.json),
  [`decomp/evidence/opcode_0x80_runtime_slot_access_static.md`](decomp/evidence/opcode_0x80_runtime_slot_access_static.md)
- `2026-04-30`: added a focused local `_loadSystemDat` export and header-word
  note for `Game Data/BATTLE/SYSTEM.DAT`, narrowing that file from "possible
  missing overlay" to offset-indexed payload data and removing it as the main
  unswept static code branch in the `0x80` contradiction. Links:
  [`decomp/ghidra/export_inittbl_system_dat_loader_slice.ps1`](decomp/ghidra/export_inittbl_system_dat_loader_slice.ps1),
  [`decomp/evidence/inittbl_system_dat_loader_slice.json`](decomp/evidence/inittbl_system_dat_loader_slice.json),
  [`decomp/evidence/system_dat_header_words.json`](decomp/evidence/system_dat_header_words.json),
  [`decomp/evidence/opcode_0x80_system_dat_static.md`](decomp/evidence/opcode_0x80_system_dat_static.md)
- `2026-04-30`: added a reusable raw-binary MIPS address-access scanner and
  used it to sweep the packaged `.PRG`/`.BIN`/`.40` corpus for
  `0x800F4C28`; the scan recovered only the already-known `INITBTL.PRG` write
  and `BATTLE.PRG` read, which is enough to promote `0x80` from
  `in_progress` to `runtime_needed`. Links:
  [`decomp/verification/scan_mips_address_accesses.py`](decomp/verification/scan_mips_address_accesses.py),
  [`decomp/evidence/runtime_opcode_table_binary_scan.json`](decomp/evidence/runtime_opcode_table_binary_scan.json),
  [`decomp/evidence/opcode_0x80_binary_address_scan.md`](decomp/evidence/opcode_0x80_binary_address_scan.md),
  [`decomp/evidence/opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md)
- `2026-04-30`: turned the `0x80` runtime tie-breaker into a concrete local
  pass by adding a dump-vs-baseline compare helper, a focused runtime capture
  plan, and a structured observation template for the next `PCSX-Redux`
  session. Links:
  [`decomp/verification/compare_opcode_table_snapshots.py`](decomp/verification/compare_opcode_table_snapshots.py),
  [`decomp/evidence/opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md),
  [`decomp/evidence/opcode_0x80_runtime_observation_template.json`](decomp/evidence/opcode_0x80_runtime_observation_template.json)
- `2026-04-30`: added a reusable runtime-observation finalizer so a filled
  `PCSX-Redux` capture packet now auto-generates the compare report, support
  note, and updated observation JSON in one step. Links:
  [`decomp/verification/finalize_runtime_observation.py`](decomp/verification/finalize_runtime_observation.py),
  [`decomp/evidence/opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md),
  [`decomp/evidence/opcode_0x80_runtime_observation_template.json`](decomp/evidence/opcode_0x80_runtime_observation_template.json)
- `2026-04-30`: turned the `0x80` runtime handoff into a checked-in scaffold
  packet by generating a missing-snapshot compare report, a breakpoint-ready
  support note, and a fill-in-place observation JSON for the next runtime
  pass. Links:
  [`decomp/evidence/opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json),
  [`decomp/evidence/opcode_0x80_runtime_snapshot_compare.json`](decomp/evidence/opcode_0x80_runtime_snapshot_compare.json),
  [`decomp/evidence/opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md),
  [`decomp/verification/finalize_runtime_observation.py`](decomp/verification/finalize_runtime_observation.py)
