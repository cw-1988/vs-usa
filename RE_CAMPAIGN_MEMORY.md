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

Current phase: Pass 0 - Bootstrap and inventory

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
| `opcode 0x80` | `conflicted` | `INITBTL.PRG` static table at `0x800FAF7C`, copied into runtime slot `0x800F4C28` by the locally dumped init-time routine at `0x800FAAAC` | Static slot `0x800B66E4`; nearby `0x800BA2E0` and `0x800BA404+` form a local sound-shaped neighborhood, but not a direct exported `0x80` target | `SoundEffects0` placeholder only | Does any later runtime path rewrite or bypass the copied `0x800F4C28` entry, or can xref recovery pin `0x800BA2E0` to the visible `0x83+` neighborhood instead? | `Pass 3 - Copy/patch reconciliation` | [`opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md), [`opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md), [`opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md), [`inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json), [`inittbl_0x80_copy_slice.json`](decomp/evidence/inittbl_0x80_copy_slice.json), [`battle_0x80_handler_slices.json`](decomp/evidence/battle_0x80_handler_slices.json), [`battle_sound_candidate_slice.json`](decomp/evidence/battle_sound_candidate_slice.json), [`battle_0x80_sound_cluster_slices.json`](decomp/evidence/battle_0x80_sound_cluster_slices.json) |

## Known Conflicts

### `0x80`: static stub entry vs nearby sound playback helper

- What static evidence says: `decomp/evidence/inittbl_opcode_table.json` maps
  `0x80 -> 0x800B66E4`, and
  `decomp/evidence/battle_0x80_handler_slices.json` shows a real binary stub
  (`jr ra; clear v0`). `0x81` and `0x82` also share that same target.
  `decomp/evidence/inittbl_0x80_copy_slice.json` shows a local init-time
  routine allocating `0x400` bytes, storing the destination in `0x800F4C28`,
  and copying `0x400` bytes from `0x800FAF7C`, so the stubbed table state is
  also the proven initial runtime state.
- What competing evidence says:
  `decomp/evidence/battle_sound_candidate_slice.json` shows `0x800BA2E0`
  consuming the same four argument bytes and calling `0x80045754`, so a
  nearby sound-family implementation still looks plausible. But
  `decomp/evidence/opcode_0x80_sound_cluster_static.md` now shows that the
  exported table already transitions from the `0x80-0x82` stub cluster into a
  contiguous local sound-shaped handler family at `0x83+`, which weakens the
  idea that `0x800BA2E0` must be a hidden replacement for `0x80`.
- What is still missing: the live dispatch consumer for `0x800F4C28`, plus any
  later patch writer or bypass path that could swap `0x80-0x84` away from the
  copied `0x800B66E4` entries, or a direct caller xref that pins
  `0x800BA2E0` to the visible `0x83+` neighborhood.
- Is runtime justified yet: not yet. Local static evidence now proves the
  copied initial table state, so the next step is still xref/patch tracing
  before using `PCSX-Redux` as a tie-breaker.

## Artifacts Index

### Table exports

- [`decomp/evidence/inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json)
- [`decomp/evidence/inittbl_opcode_table_xrefs.json`](decomp/evidence/inittbl_opcode_table_xrefs.json)

### Handler slices

- [`decomp/evidence/battle_0x80_handler_slices.json`](decomp/evidence/battle_0x80_handler_slices.json)
- [`decomp/evidence/battle_sound_candidate_slice.json`](decomp/evidence/battle_sound_candidate_slice.json)
- [`decomp/evidence/inittbl_0x80_copy_slice.json`](decomp/evidence/inittbl_0x80_copy_slice.json)
- [`decomp/evidence/battle_0x80_sound_cluster_slices.json`](decomp/evidence/battle_0x80_sound_cluster_slices.json)

### Reconciliation reports

- [`decomp/evidence/opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md)
- [`decomp/evidence/opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md)

### Proof packets

- [`decomp/evidence/opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md)

## Session Handoff

- `last completed step`: rebuilt the `0x80` copy-path and sound-neighborhood
  notes from local binary exports and instruction dumps, without treating
  helper source as evidence authority
- `next recommended step`: recover xrefs for the runtime dispatch path or for
  callers of `0x800BA2E0` so the `0x80` conflict can be downgraded from
  "competing semantic candidate" to either "adjacent helper only" or
  `runtime_needed`
- `do not forget`: update this ledger before ending the next pass; no export,
  coverage note, or contradiction should live only in terminal output

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
