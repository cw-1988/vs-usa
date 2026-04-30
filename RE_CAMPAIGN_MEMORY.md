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
| `opcode 0x80` | `in_progress` | `INITBTL.PRG` static table at `0x800FAF7C`, copied into runtime slot `0x800F4C28` by the locally dumped init-time routine at `0x800FAAAC` | Static slot `0x800B66E4`; former competing helper `0x800BA2E0` is now anchored to a local `BATTLE.PRG` sound subdispatch table at `0x800E9F30` with siblings `0x800BA35C/39C/3E4/404/444/470/494`; live `BATTLE.PRG` consumer `FUN_800BFBB8` now reads `0x800F4C28`, uses it only for pointer arithmetic plus one indexed table-entry read in the new local trace, and dispatches via `jalr` | `SoundEffects0` placeholder only | With the one recovered `BATTLE.PRG` reader now traced through to an indexed read and `jalr`, does any other unrecovered path outside the currently swept local battle executables still patch the copied table later? | `Pass 3 - Copy/patch reconciliation` | [`opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md), [`opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md), [`opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md), [`opcode_0x80_runtime_dispatch_static.md`](decomp/evidence/opcode_0x80_runtime_dispatch_static.md), [`opcode_0x80_runtime_slot_access_static.md`](decomp/evidence/opcode_0x80_runtime_slot_access_static.md), [`opcode_0x80_runtime_pointer_usage_static.md`](decomp/evidence/opcode_0x80_runtime_pointer_usage_static.md), [`inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json), [`inittbl_0x80_copy_slice.json`](decomp/evidence/inittbl_0x80_copy_slice.json), [`inittbl_runtime_opcode_table_accesses.json`](decomp/evidence/inittbl_runtime_opcode_table_accesses.json), [`battle_0x80_handler_slices.json`](decomp/evidence/battle_0x80_handler_slices.json), [`battle_sound_candidate_slice.json`](decomp/evidence/battle_sound_candidate_slice.json), [`battle_sound_candidate_xrefs.json`](decomp/evidence/battle_sound_candidate_xrefs.json), [`battle_sound_dispatch_table.json`](decomp/evidence/battle_sound_dispatch_table.json), [`battle_0x80_sound_cluster_slices.json`](decomp/evidence/battle_0x80_sound_cluster_slices.json), [`battle_runtime_opcode_table_xrefs.json`](decomp/evidence/battle_runtime_opcode_table_xrefs.json), [`battle_runtime_opcode_table_accesses.json`](decomp/evidence/battle_runtime_opcode_table_accesses.json), [`battle_runtime_opcode_table_pointer_usage.json`](decomp/evidence/battle_runtime_opcode_table_pointer_usage.json) |

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
  from it, with no additional direct slot accesses recovered in that local
  sweep.
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
  does not.
- What is still missing: any static or runtime evidence that the copied table
  contents themselves are patched after the verified init-time copy, rather
  than only the slot being read and dispatched through by the currently
  recovered local consumer.
- Is runtime justified yet: not yet. The direct-slot rewrite question is now
  much weaker, and the one recovered local reader has now been traced through
  without finding a write-back path, so the next static step is widening the
  sweep to any additional local battle-adjacent executables or readers before
  using `PCSX-Redux` as a late tie-breaker.

## Artifacts Index

### Table exports

- [`decomp/evidence/inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json)
- [`decomp/evidence/inittbl_opcode_table_xrefs.json`](decomp/evidence/inittbl_opcode_table_xrefs.json)
- [`decomp/evidence/battle_sound_candidate_xrefs.json`](decomp/evidence/battle_sound_candidate_xrefs.json)
- [`decomp/evidence/battle_sound_dispatch_table.json`](decomp/evidence/battle_sound_dispatch_table.json)
- [`decomp/evidence/battle_runtime_opcode_table_xrefs.json`](decomp/evidence/battle_runtime_opcode_table_xrefs.json)
- [`decomp/evidence/inittbl_runtime_opcode_table_accesses.json`](decomp/evidence/inittbl_runtime_opcode_table_accesses.json)
- [`decomp/evidence/battle_runtime_opcode_table_accesses.json`](decomp/evidence/battle_runtime_opcode_table_accesses.json)
- [`decomp/evidence/battle_runtime_opcode_table_pointer_usage.json`](decomp/evidence/battle_runtime_opcode_table_pointer_usage.json)

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

### Proof packets

- [`decomp/evidence/opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md)

## Session Handoff

- `last completed step`: added a reusable pointer-derived access tracer, then
  ran it on the recovered `BATTLE.PRG` reader at `FUN_800BFBB8` to show that
  the copied table pointer from `0x800F4C28` is only used for pointer
  arithmetic plus one indexed read before `jalr`, with no recovered indirect
  write-back in that local consumer
- `next recommended step`: widen the slot/pointer sweep to any additional
  local battle-adjacent executables or overlays that could still mutate the
  copied table after init, because the currently recovered writer/reader pair
  inside `INITBTL.PRG` and `BATTLE.PRG` no longer supplies a static patch path
- `do not forget`: update this ledger before ending the next pass; no export,
  coverage note, or contradiction should live only in terminal output; keep
  runtime as a late tie-breaker only after indirect patch tracing around the
  copied table stalls

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
