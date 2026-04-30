# RE Campaign Memory

## Campaign Goal

Build a verified opcode-to-handler map for the battle-script system before
promoting semantic names. The campaign stays opcode-first: finish table
ownership, copy/patch tracing, handler coverage, shared-handler clustering, and
contradiction tracking before turning tentative labels into decoder-facing
claims.

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
| `opcode 0x80` | `conflicted` | `INITBTL.PRG` battle opcode table export at `0x800FAF7C` | Static slot `0x800B66E4` vs nearby sound-shaped helper `0x800BA2E0` in `BATTLE.PRG` | `SoundEffects0` placeholder only | Is `0x80` a real stubbed slot, or does a copied runtime table later patch this family to a sound handler? | `Pass 3 - Copy/patch reconciliation` | [`opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md), [`inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json), [`battle_0x80_handler_slices.json`](decomp/evidence/battle_0x80_handler_slices.json), [`battle_sound_candidate_slice.json`](decomp/evidence/battle_sound_candidate_slice.json) |

## Known Conflicts

### `0x80`: static stub entry vs nearby sound playback helper

- What static evidence says: `decomp/evidence/inittbl_opcode_table.json` maps
  `0x80 -> 0x800B66E4`, and
  `decomp/evidence/battle_0x80_handler_slices.json` shows a real binary stub
  (`jr ra; clear v0`). `0x81` and `0x82` also share that same target.
- What competing evidence says:
  `decomp/evidence/battle_sound_candidate_slice.json` shows `0x800BA2E0`
  consuming the same four argument bytes and calling `vs_main_playSfx`, so a
  nearby sound-family implementation still looks plausible.
- What is still missing: table ownership and copy/patch tracing from the
  exported `INITBTL.PRG` table into the live runtime dispatch path for the
  `0x80-0x84` family.
- Is runtime justified yet: not yet. Finish static copy-site and patch-site
  tracing first, then use `PCSX-Redux` only if the contradiction survives that
  pass.

## Artifacts Index

### Table exports

- [`decomp/evidence/inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json)

### Handler slices

- [`decomp/evidence/battle_0x80_handler_slices.json`](decomp/evidence/battle_0x80_handler_slices.json)
- [`decomp/evidence/battle_sound_candidate_slice.json`](decomp/evidence/battle_sound_candidate_slice.json)

### Reconciliation reports

- None yet.

### Proof packets

- [`decomp/evidence/opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md)

## Session Handoff

- `last completed step`: registered the existing `0x80` static conflict and its
  CLI artifacts in the master campaign ledger
- `next recommended step`: finish Pass 0 inventory for every known
  battle-script table owner and initializer, then trace the copy/patch path
  that could affect the `0x80-0x84` family
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
