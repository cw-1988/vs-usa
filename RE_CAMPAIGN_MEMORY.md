# RE Campaign Memory

## Next-Instance Starter Pack

Default read set for the next opcode/decomp pass:

- [`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md)
- [`docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md`](docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md)
- [`docs/workflows/DECOMPILATION_STRATEGY.md`](docs/workflows/DECOMPILATION_STRATEGY.md)
- [`docs/workflows/CLI_DECOMPILATION_WORKFLOW.md`](docs/workflows/CLI_DECOMPILATION_WORKFLOW.md)

If the next pass is continuing `0x80`, add:

- [`decomp/evidence/opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md)
- [`decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md`](decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md)
- [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json)
- [`decomp/evidence/opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json)
- [`decomp/evidence/opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md)

Optional background only:

- [`docs/campaign/RE_CAMPAIGN_HISTORY.md`](docs/campaign/RE_CAMPAIGN_HISTORY.md)
- [`docs/campaign/Opcode Decomp Campaign Plan.md`](docs/campaign/Opcode%20Decomp%20Campaign%20Plan.md)
- [`docs/campaign/ROOD_REVERSE_OPCODE_CONCLUSIONS.md`](docs/campaign/ROOD_REVERSE_OPCODE_CONCLUSIONS.md)

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
  `Known Conflicts`, and the campaign artifact index should point first to
  local artifacts.

## Current Phase

Current phase: Pass 3 - Copy/patch reconciliation

## Status Legend

- `unstarted`: no local artifact packet yet
- `in_progress`: static export or reconciliation work is active
- `covered`: table and handler coverage exist, but the contradiction is not
  reconciled yet
- `static_resolved`: Pass 3 closed the copy/patch question without needing
  more runtime evidence
- `runtime_needed`: static work narrowed the question, but runtime still has to
  break the tie
- `tentative`: the working interpretation is useful, but proof is still
  incomplete
- `conflicted`: strong evidence still disagrees and must stay explicit
- `confirmed`: binary and, when needed, runtime evidence agree strongly enough
  to promote the claim

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
| `opcode 0x80` | `runtime_needed` | `INITBTL.PRG` static table at `0x800FAF7C`, copied by the init-time routine at `0x800FAAAC` into runtime slot `0x800F4C28` | Initial slot `0x800B66E4` is a shared stub for `0x80-0x82`; former competing target `0x800BA2E0` is now locally anchored to the `BATTLE.PRG` sound subdispatch table at `0x800E9F30`; recovered reader `FUN_800BFBB8` dispatches through the copied runtime table via `jalr` | `SoundEffects0` placeholder only | Do runtime dumps from `0x800F4C28` ever diverge from the binary baseline before `0x80-0x82` dispatch, and if not, which later reader or rewrite site actually governs the disputed live behavior? | `Pass 3 - Copy/patch reconciliation` | [`opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md), [`opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md), [`opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md), [`opcode_0x80_runtime_dispatch_static.md`](decomp/evidence/opcode_0x80_runtime_dispatch_static.md), [`opcode_0x80_runtime_slot_access_static.md`](decomp/evidence/opcode_0x80_runtime_slot_access_static.md), [`opcode_0x80_binary_address_scan.md`](decomp/evidence/opcode_0x80_binary_address_scan.md), [`opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md), [`opcode_0x80_runtime_memcard_probe.md`](decomp/evidence/opcode_0x80_runtime_memcard_probe.md), [`opcode_0x80_runtime_bat_kill_negative.md`](decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md), [`opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json), [`opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json), [`opcode_0x80_runtime_snapshot_compare.json`](decomp/evidence/opcode_0x80_runtime_snapshot_compare.json), [`opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md) |

## Known Conflicts

### `0x80`: copied initial stub vs possible later runtime rewrite/bypass

- What static evidence says:
  `inittbl_opcode_table.json` and `battle_0x80_handler_slices.json` still map
  `0x80-0x82` to the shared stub at `0x800B66E4`.
  `inittbl_0x80_copy_slice.json` proves the init-time copy from `0x800FAF7C`
  into runtime slot `0x800F4C28`, and
  `battle_runtime_opcode_table_xrefs.json` proves `FUN_800BFBB8` reads that
  runtime table and dispatches through it with `jalr`.
- What competing evidence says:
  The old alternative `0x800BA2E0` now fits a local `BATTLE.PRG` sound
  subdispatch table, not the hidden direct `0x80` handler. The remaining
  uncertainty is narrower: the table may still be patched indirectly after the
  verified init-time copy even though current direct-slot sweeps and pointer
  tracing have not recovered a rewrite path.
- What is still missing:
  A runtime snapshot that proves whether the copied table contents ever diverge
  from the binary baseline before `0x80-0x82` dispatch. The active packet is
  anchored by
  [`opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md),
  [`opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json),
  [`opcode_0x80_runtime_expected_table.bin`](decomp/evidence/opcode_0x80_runtime_expected_table.bin),
  and
  [`compare_opcode_table_snapshots.py`](decomp/verification/compare_opcode_table_snapshots.py).
  The cold-boot automation is now far enough along to prove real route facts:
  the retuned input plan plus corrected `O` confirm / `X` cancel mapping reach
  the title menu, highlight `Continue`, and open the `Load / Memory Card slot
  1` screen. But the repo-local cards still probe as blank formatted cards, so
  this particular `Load` branch is now a confirmed dead end rather than a
  plausible entry into live gameplay. The remaining runtime blocker is
  therefore the lack of a usable gameplay-entry artifact such as a savestate
  or populated card, not wrapper timing or intro navigation. The latest
  checked-in rerun also encoded a title-menu `New Game` branch instead of the
  dead `Continue/Load` path: it confirms `CIRCLE`, waits roughly ten seconds,
  then sends two delayed `START` skips as control-handoff probes. That pass
  extended the timeout to `4380` frames and still recorded no
  `0x800BFBB8` reader hit, no table-write hit, and no snapshots, so the
  old blank-card branch is no longer the live question. The preserved
  bat-control follow-up went farther: it reached player control, rotated into
  the adjacent room, unsheathed, opened the attack sphere, and attacked the
  first bat, yet still recorded no `0x800BFBB8` reader hit, no candidate hit,
  no table-write hit, and no snapshots. The next decisive pass therefore needs
  either a nearer savestate or broader reader/trigger discovery, not more
  blind proof that "gameplay happened."
  If both tracked snapshots still match the baseline and the table write
  watchpoint stays quiet, this contradiction can be downgraded to
  `static_resolved` and carried forward into `Pass 4`. If the next widened
  runtime pass still finds no copied-table reads or rewrites around the real
  target moment, then the working assumption that `FUN_800BFBB8` is the
  decisive live reader for this contradiction should be reopened explicitly in
  the notes rather than protected by more cold-boot route churn.
- Is runtime justified yet:
  Yes. Static sweeps have narrowed the contradiction enough that `PCSX-Redux`
  is now the clean tie-breaker.

## Campaign Artifact Index

The durable artifact catalog now lives in
[`docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md`](docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md).

Use this ledger for:

- current target summaries
- current conflicts and blocking questions
- handoff instructions for the next pass

Use the artifact index for:

- grouped export lists
- proof-packet registration
- reconciliation report lookup
- reusable verification helper entrypoints

## Session Handoff

- `last completed step`: the no-savestate `PCSX-Redux` fallback is now
  instrumented enough to leave screenshot checkpoints, and the latest retunes
  proved that `START` pushes through the intro chain, this build uses `O`
  confirm / `X` cancel, and the checked-in route can reach live player control
  from a `New Game` cold boot. The newest preserved retune rotated into the
  adjacent room, unsheathed, opened the attack sphere, and attacked the first
  bat, then timed out at `4886` frames with no `0x800BFBB8` reader hit, no
  candidate hit, no table-write hit, and no snapshots. That makes the bat-kill
  route a useful negative control rather than just another failed timing pass:
  early live gameplay, room transition, and the first combat exchange still do
  not exercise the watched runtime reader.
- `next recommended step`: keep the preserved bat-control route as a
  regression/control artifact, but stop spending passes on blind cold-boot
  timing tweaks alone. Preferred order for the next runtime pass:
  1. run `decomp/verification/run_opcode_0x80_runtime_capture.ps1` with a
     near-battle or target-cutscene savestate (`-UseNewestSaveState` or
     `-SaveStatePath`)
  2. if no savestate exists yet, pivot the Lua capture toward broader copied
     table reader discovery or later script/cutscene triggers instead of
     assuming `0x800BFBB8` should fire as soon as player control or the first
     bat encounter begins
  3. use the bat-control route only as a regression check after instrumentation
     changes, because it already proved that early live gameplay is a weak
     trigger for this contradiction
  4. if the widened pass still stays silent, record which copied-table reader,
     script family, or cutscene hook becomes the next candidate before trying
     another cold-boot timing retune
  Once a run reaches a real reader or rewrite site, capture `after_init` and
  `pre_dispatch`, then run
  `decomp/verification/finalize_runtime_observation.py --in-place`. If the
  compare report shows `0x80-0x82` rewrites, immediately import those rows with
  `record_runtime_observation.py import-compare --replace-derived --finalize`.
  If both snapshots match the baseline and no rewrite evidence appears, relabel
  the `0x80` conflict as `static_resolved` and advance the target to
  `Pass 4 - Semantic proof packets`.
- `do not forget`: keep raw dumps, compare reports, and useful frame captures
  under `decomp/evidence`, preserve the original savestate or tuned input-plan
  JSON as the handoff artifact, and use the compare-import helper instead of
  hand-editing mutation rows. If rewrites do appear, keep `Pass 3` active until
  the replacement handlers are anchored with local evidence rather than leaving
  the result as a compare-only observation. For the cold-boot fallback
  specifically, preserve which menu path, button mapping, and card assumptions
  were actually tested so the next pass does not retry a known dead branch.

## Completed Milestones

- Historical archive moved out of the active ledger on `2026-05-01`:
  [`docs/campaign/RE_CAMPAIGN_HISTORY.md`](docs/campaign/RE_CAMPAIGN_HISTORY.md)
- Artifact index moved out of the active ledger on `2026-05-01`:
  [`docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md`](docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md)
- `2026-05-01`: added a checked-in no-savestate fallback for the `0x80`
  runtime tie-breaker. Links:
  [`decomp/verification/run_opcode_0x80_runtime_capture.ps1`](decomp/verification/run_opcode_0x80_runtime_capture.ps1),
  [`decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](decomp/verification/pcsx_redux_opcode_0x80_capture.lua),
  [`decomp/evidence/opcode_0x80_runtime_input_plan.json`](decomp/evidence/opcode_0x80_runtime_input_plan.json)
- `2026-05-01`: taught the `0x80` runtime wrapper to auto-extend timeout for
  checked-in input plans, then verified that the starter cold-boot route now
  completes all six scheduled pad steps but still fails to reach the recovered
  runtime reader or produce snapshots. Links:
  [`decomp/verification/run_opcode_0x80_runtime_capture.ps1`](decomp/verification/run_opcode_0x80_runtime_capture.ps1),
  [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`decomp/evidence/opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json),
  [`decomp/evidence/opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md)
- `2026-05-01`: added route-debug screenshots and a memcard probe for the `0x80`
  runtime path, then used them to prove that the cold-boot scaffold can reach
  the title menu and `Load / Memory Card slot 1` under `O` confirm / `X`
  cancel, but still cannot enter gameplay because the repo-local cards are
  blank. Links:
  [`decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](decomp/verification/pcsx_redux_opcode_0x80_capture.lua),
  [`decomp/verification/run_opcode_0x80_runtime_capture.ps1`](decomp/verification/run_opcode_0x80_runtime_capture.ps1),
  [`decomp/verification/probe_psx_memcards.py`](decomp/verification/probe_psx_memcards.py),
  [`decomp/evidence/opcode_0x80_runtime_input_plan.json`](decomp/evidence/opcode_0x80_runtime_input_plan.json),
  [`decomp/evidence/opcode_0x80_runtime_memcard_probe.md`](decomp/evidence/opcode_0x80_runtime_memcard_probe.md),
  [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json)
- `2026-05-01`: retuned the checked-in no-savestate scaffold away from the
  blank-card `Continue/Load` branch and into a title-menu `New Game` route
  anchored by `CIRCLE`, wait `~10s`, `START`, wait `~10s`, `START`; the rerun
  extended to `4380` frames but still did not reach `0x800BFBB8`, any
  candidate handler, or a table-write hit. Links:
  [`decomp/evidence/opcode_0x80_runtime_input_plan.json`](decomp/evidence/opcode_0x80_runtime_input_plan.json),
  [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`decomp/evidence/opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json),
  [`decomp/evidence/opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md)
- `2026-05-01`: preserved a cold-boot negative-control route that reaches
  player control, enters the adjacent room, opens the attack sphere, and
  attacks the first bat, then verified that this wider gameplay sample still
  records no `0x800BFBB8` reader hit, no table-write hit, and no snapshots.
  Links:
  [`decomp/evidence/opcode_0x80_runtime_input_plan_bat_kill.json`](decomp/evidence/opcode_0x80_runtime_input_plan_bat_kill.json),
  [`decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md`](decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md),
  [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`decomp/evidence/opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json)
- `2026-04-30`: made the automated `PCSX-Redux` runtime path savestate-ready
  and validated the scripted capture path against the local disc image. Links:
  [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`decomp/evidence/opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json),
  [`decomp/evidence/opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md)
- `2026-04-30`: narrowed the `0x80` contradiction to a runtime-only tie-breaker
  by proving the init-time copy path, the live runtime-table reader, the sound
  subdispatch cluster, and the lack of extra direct-slot matches in the packaged
  corpus. Links:
  [`decomp/evidence/opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md),
  [`decomp/evidence/opcode_0x80_runtime_dispatch_static.md`](decomp/evidence/opcode_0x80_runtime_dispatch_static.md),
  [`decomp/evidence/opcode_0x80_binary_address_scan.md`](decomp/evidence/opcode_0x80_binary_address_scan.md)
- `2026-04-30`: created the campaign ledger and aligned the workflow docs
  around it. Links:
  [`README.md`](README.md),
  [`docs/workflows/AI_RE_PASS_WORKFLOW.md`](docs/workflows/AI_RE_PASS_WORKFLOW.md),
  [`docs/workflows/CLI_DECOMPILATION_WORKFLOW.md`](docs/workflows/CLI_DECOMPILATION_WORKFLOW.md),
  [`docs/workflows/DECOMPILATION_STRATEGY.md`](docs/workflows/DECOMPILATION_STRATEGY.md),
  [`decomp/README.md`](decomp/README.md)
