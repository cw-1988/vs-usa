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
| `opcode 0x80` | `conflicted` | `INITBTL.PRG` static table `D_800FAF7C`, copied into runtime heap table `D_800F4C28` by `_initScriptFunctionTable()` | Static slot `0x800B66E4`; nearby `0x800BA2E0` now looks more like a helper inside the adjacent `0x83+` sound cluster than a direct `0x80` target | `SoundEffects0` placeholder only | Does any later runtime path rewrite or bypass the copied `D_800F4C28` entry, or does xref recovery show `0x800BA2E0` belongs only to the `0x83+` sound family? | `Pass 3 - Copy/patch reconciliation` | [`opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md), [`opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md), [`opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md), [`inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json), [`battle_0x80_handler_slices.json`](decomp/evidence/battle_0x80_handler_slices.json), [`battle_sound_candidate_slice.json`](decomp/evidence/battle_sound_candidate_slice.json) |

## Known Conflicts

### `0x80`: static stub entry vs nearby sound playback helper

- What static evidence says: `decomp/evidence/inittbl_opcode_table.json` maps
  `0x80 -> 0x800B66E4`, and
  `decomp/evidence/battle_0x80_handler_slices.json` shows a real binary stub
  (`jr ra; clear v0`). `0x81` and `0x82` also share that same target.
  `decomp/evidence/opcode_0x80_copy_path_static.md` now ties that export back
  to the local `INITBTL.PRG` symbol `D_800FAF7C` and shows
  `_initScriptFunctionTable()` copying the full table into runtime buffer
  `D_800F4C28` during battle bootstrap.
- What competing evidence says:
  `decomp/evidence/battle_sound_candidate_slice.json` shows `0x800BA2E0`
  consuming the same four argument bytes and calling `vs_main_playSfx`, so a
  nearby sound-family implementation still looks plausible. But
  `decomp/evidence/opcode_0x80_sound_cluster_static.md` now shows that the
  exported/source table already transitions from the `0x80-0x82` stub cluster
  into explicit sound-control handlers at `0x83+`, which weakens the idea that
  `0x800BA2E0` must be a hidden replacement for `0x80`.
- What is still missing: the live dispatch consumer for `D_800F4C28`, plus any
  later patch writer or bypass path that could swap `0x80-0x84` away from the
  copied `0x800B66E4` entries, or a direct caller xref that pins
  `0x800BA2E0` to one of the visible `0x83+` sound opcodes.
- Is runtime justified yet: not yet. Static ownership and the init-time copy
  are now confirmed, so the next step is still static patch/consumer tracing
  before using `PCSX-Redux` as a tie-breaker.

## Artifacts Index

### Table exports

- [`decomp/evidence/inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json)

### Handler slices

- [`decomp/evidence/battle_0x80_handler_slices.json`](decomp/evidence/battle_0x80_handler_slices.json)
- [`decomp/evidence/battle_sound_candidate_slice.json`](decomp/evidence/battle_sound_candidate_slice.json)

### Reconciliation reports

- [`decomp/evidence/opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md)
- [`decomp/evidence/opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md)

### Proof packets

- [`decomp/evidence/opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md)

## Session Handoff

- `last completed step`: showed that the table already enters a visible
  sound-control cluster at `0x83+`, making `0x800BA2E0` more likely to belong
  to adjacent sound opcodes than to a hidden rewrite of `0x80`
- `next recommended step`: recover xrefs for the runtime dispatch path or for
  callers of `func_800BA2E0` so the `0x80` conflict can be downgraded from
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
- `2026-04-30`: tied the exported `INITBTL.PRG` opcode table back to its local
  owner symbol and init-time heap copy path, narrowing the `0x80` conflict to
  later runtime patch/bypass behavior. Links:
  [`decomp/evidence/opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md),
  [`decomp/evidence/inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json),
  [`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c`](_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c),
  [`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/18.c`](_refs/rood-reverse/src/BATTLE/INITBTL.PRG/18.c)
- `2026-04-30`: showed that the copied `0x80-0x82` stub block is immediately
  followed by a visible `0x83+` sound-control cluster, weakening the idea that
  the nearby `vs_main_playSfx` helper is a hidden direct implementation of
  `0x80`. Links:
  [`decomp/evidence/opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md),
  [`decomp/evidence/inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json),
  [`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c`](_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c),
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c)
