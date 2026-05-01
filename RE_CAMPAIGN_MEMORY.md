# RE Campaign Memory

## Next-Instance Starter Pack

Default read set for the next opcode/decomp pass:

- [`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md)
- [`docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md`](docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md)
- [`docs/workflows/DECOMPILATION_STRATEGY.md`](docs/workflows/DECOMPILATION_STRATEGY.md)
- [`docs/workflows/CLI_DECOMPILATION_WORKFLOW.md`](docs/workflows/CLI_DECOMPILATION_WORKFLOW.md)

If the next pass is continuing `0x80`, add:

- [`decomp/evidence/opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md)
- [`decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json`](decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json)
- [`decoded_scripts/24-Unmapped/001-Unknown Room.txt`](decoded_scripts/24-Unmapped/001-Unknown%20Room.txt)
- [`decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md`](decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md)
- [`decomp/evidence/opcode_0x80_runtime_input_plan_bat_kill.json`](decomp/evidence/opcode_0x80_runtime_input_plan_bat_kill.json)
- [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json),,
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
| `opcode 0x80` | `runtime_needed` | `INITBTL.PRG` static table at `0x800FAF7C`, copied by the init-time routine at `0x800FAAAC` into pointer slot `0x800F4C28` and resolved live at `0x801119F0` during the validated `MAP001` intro pass | Initial slot `0x800B66E4` is a shared stub for `0x80-0x82`; former competing target `0x800BA2E0` is now locally anchored to the `BATTLE.PRG` sound subdispatch table at `0x800E9F30`; recovered reader `FUN_800BFBB8` dispatches through the copied runtime table via `jalr`, and the `MAP001` listener-control run now proves that chain is live on retail runtime | `SoundEffects0` placeholder only | Now that the live reader chain is proven and `0x80` still resolves to shared stub `0x800B66E4`, what later state, side table, or secondary callee gives `0x80` its real sound behavior without a copied-table rewrite? | `Pass 3 - Copy/patch reconciliation` | [`opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md), [`opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md), [`opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md), [`opcode_0x80_runtime_dispatch_static.md`](decomp/evidence/opcode_0x80_runtime_dispatch_static.md), [`opcode_0x80_runtime_slot_access_static.md`](decomp/evidence/opcode_0x80_runtime_slot_access_static.md), [`opcode_0x80_runtime_reader_call_chain_static.md`](decomp/evidence/opcode_0x80_runtime_reader_call_chain_static.md), [`opcode_0x80_binary_address_scan.md`](decomp/evidence/opcode_0x80_binary_address_scan.md), [`opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md), [`opcode_0x80_runtime_memcard_probe.md`](decomp/evidence/opcode_0x80_runtime_memcard_probe.md), [`opcode_0x80_runtime_bat_kill_negative.md`](decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md), [`opcode_0x80_runtime_input_plan_bat_kill.json`](decomp/evidence/opcode_0x80_runtime_input_plan_bat_kill.json), [`opcode_0x80_runtime_input_plan_map001_listener.json`](decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json), [`opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json), [`opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json), [`opcode_0x80_runtime_snapshot_compare.json`](decomp/evidence/opcode_0x80_runtime_snapshot_compare.json), [`opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md) |

## Known Conflicts

### `0x80`: copied initial stub vs possible later runtime rewrite/bypass

- What static evidence says:
  `inittbl_opcode_table.json` and `battle_0x80_handler_slices.json` still map
  `0x80-0x82` to the shared stub at `0x800B66E4`.
  `inittbl_0x80_copy_slice.json` proves the init-time copy from `0x800FAF7C`
  into runtime slot `0x800F4C28`, and
  `battle_runtime_opcode_table_xrefs.json` proves `FUN_800BFBB8` reads that
  runtime table and dispatches through it with `jalr`.
  `opcode_0x80_runtime_reader_call_chain_static.md` now narrows the same
  reader under one recovered caller chain:
  `0x8007A36C -> 0x800BF850 -> FUN_800BFBB8`, with the immediate caller also
  iterating a small pointer family rooted at `0x800F4C38`.
- What competing evidence says:
  The old alternative `0x800BA2E0` now fits a local `BATTLE.PRG` sound
  subdispatch table, not the hidden direct `0x80` handler. The remaining
  uncertainty is narrower: the table may still be patched indirectly after the
  verified init-time copy even though current direct-slot sweeps and pointer
  tracing have not recovered a rewrite path.
- What is still missing:
  A tighter local proof of what happens after the now-validated `0x80`
  dispatch lands on shared stub `0x800B66E4`. The active packet is
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
  no table-write hit, and no snapshots. The widened rerun now also armed probe
  breakpoints for `0x800BF850` and `0x8007A36C`, and those stayed silent too.
  The runtime summary now also preserves per-step input-plan start/complete
  notes with frame numbers, so route drift can be checked from one JSON packet
  before opening screenshot crumbs or retuning button timing again.
  The next decisive pass therefore needs either a nearer savestate or a wider
  trigger search beyond that recovered reader chain, not more blind proof that
  "gameplay happened."
  That `MAP001` listener-control proof now exists. The corrected runtime pass
  dereferences pointer slot `0x800F4C28`, resolves the live table at
  `0x801119F0`, hits `0x8007A36C -> 0x800BF850 -> 0x800BFBB8` repeatedly, and
  records `0x80 -> 0x800B66E4` dispatches directly from the retail intro
  script while also proving dozens of other `MAP001` opcode-family handlers.
  That closes the old "maybe the trigger plumbing is broken" branch. The live
  question is narrower now: why does `0x80` still map to the shared stub even
  though the surrounding script system is demonstrably active?
  No local artifact in this pass uses a custom `PRG`, patched executable, or
  custom ISO as a positive-control trigger source; if a future pass introduces
  one, keep that proof path labeled separately from retail-runtime evidence.
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

- `last completed step`: the latest automation pass added a checked-in
  two-stage savestate bridge under
  `decomp/verification/test-runs/map001-main-menu-bridge/`, then used it to
  prove a real `PCSX-Redux` sequencing quirk: loading the savestate during Lua
  startup made the restored title-menu frame look frozen even though
  `ExecutionFlow::SaveStateLoaded` fired, while deferring
  `PCSX.loadSaveState(...)` until `ExecutionFlow::ShellReached` restored a
  healthy resumed run. The clean resumed rerun now loads
  `save-states/init-main-menu.savestate`, waits `45` frames, presses
  `CIRCLE` at `New Game`, resolves the pointer-slot fix
  (`0x800F4C28 -> 0x801119F0`), hits the proven reader chain on the untouched
  intro (`0x8007A36C` and `0x800BF850` x`78`, `0x800BFBB8` x`76`), and still
  records retail `0x80 -> 0x800B66E4` dispatches with no post-init copied-table
  write hits.
- `next recommended step`: keep the `MAP001` listener route as the default
  positive-control regression and pivot the runtime work from "does the trigger
  chain work?" to "what makes `0x80` do real work after landing on the shared
  stub?" Preferred order for the next pass:
  1. rerun the validated `MAP001` route with
     `decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json`
     whenever the Lua/wrapper instrumentation changes, and include
     `decoded_scripts/24-Unmapped/001-Unknown Room.txt` so the handler-probe
     set stays grounded in the same intro script
  2. build or preserve a near-`0x80` savestate inside the `MAP001` intro so
     the next semantic pass can sit directly on the first `0x80` call instead
     of replaying the whole cold boot
  3. instrument outward from shared stub `0x800B66E4` and its immediate
     callers/side tables rather than treating `0x800BA2E0` as the hidden
     direct handler; the validated reader log now shows `0x80` itself still
     dispatching to the stub
  4. keep the bat-control route only as a negative-control regression, because
     it still proves that early free movement/combat is a poor proxy trigger
     for this contradiction
  5. use `-CpuCore dynarec -DisableDebugger` only for route smoke tests;
     breakpoint-driven proof still needs interpreter plus debugger, so the real
     speedup path for semantic work is a near-target savestate, not more full
     cold boots
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
  If the next pass uses the stripped `MAP001` listener-control route, label it
  explicitly as the positive-control baseline for retail runtime, not as a
  substitute for the later semantic pass on `0x80` itself.
  If a future validation pass uses a custom `PRG`, patched executable, or
  custom ISO as a positive control for the instrumentation, label that run
  explicitly as tooling proof rather than retail-runtime opcode proof.

## Completed Milestones

- Historical archive moved out of the active ledger on `2026-05-01`:
  [`docs/campaign/RE_CAMPAIGN_HISTORY.md`](docs/campaign/RE_CAMPAIGN_HISTORY.md)
- Artifact index moved out of the active ledger on `2026-05-01`:
  [`docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md`](docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md)
- `2026-05-01`: taught the `0x80` runtime capture to print trigger hits live
  in the `PCSX-Redux` console, then used a fresh `MAP001` rerun to expose and
  clear a blocking `Update configuration` modal before revalidating the retail
  intro baseline with `0x8007A36C/0x800BF850` probe hits, `0x800BFBB8` reader
  hits, and the expected `0x80 -> 0x800B66E4` dispatch samples. Links:
  [`decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](decomp/verification/pcsx_redux_opcode_0x80_capture.lua),
  [`decomp/verification/run_opcode_0x80_runtime_capture.ps1`](decomp/verification/run_opcode_0x80_runtime_capture.ps1),
  [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`decomp/evidence/opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json),
  [`decomp/evidence/opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md)
- `2026-05-01`: added a checked-in `MAP001` main-menu savestate bridge and
  fixed the resumed-pass freeze by deferring `PCSX.loadSaveState(...)` until
  `ExecutionFlow::ShellReached` instead of calling it during Lua startup.
  Links:
  [`decomp/verification/test-runs/map001-main-menu-bridge/README.md`](decomp/verification/test-runs/map001-main-menu-bridge/README.md),
  [`decomp/verification/test-runs/map001-main-menu-bridge/input-plan-01_create_init_main_menu.json`](decomp/verification/test-runs/map001-main-menu-bridge/input-plan-01_create_init_main_menu.json),
  [`decomp/verification/test-runs/map001-main-menu-bridge/input-plan-02_resume_map001_intro.json`](decomp/verification/test-runs/map001-main-menu-bridge/input-plan-02_resume_map001_intro.json),
  [`decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](decomp/verification/pcsx_redux_opcode_0x80_capture.lua),
  [`decomp/verification/run_opcode_0x80_runtime_capture.ps1`](decomp/verification/run_opcode_0x80_runtime_capture.ps1)
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
- `2026-05-01`: traced the recovered runtime reader upward through
  `0x800BF850` and `0x8007A36C`, then widened the automated bat-control rerun
  with those probe breakpoints and verified that early gameplay still does not
  enter the recovered reader chain. Links:
  [`decomp/evidence/opcode_0x80_runtime_reader_call_chain_static.md`](decomp/evidence/opcode_0x80_runtime_reader_call_chain_static.md),
  [`decomp/evidence/battle_runtime_reader_xrefs.json`](decomp/evidence/battle_runtime_reader_xrefs.json),
  [`decomp/evidence/battle_runtime_reader_caller_xrefs.json`](decomp/evidence/battle_runtime_reader_caller_xrefs.json),
  [`decomp/evidence/battle_runtime_reader_call_chain_slices.json`](decomp/evidence/battle_runtime_reader_call_chain_slices.json),
  [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json)
- `2026-05-01`: taught the `0x80` runtime capture Lua to log each input-plan
  step start/completion to the console and preserved those frame-stamped notes
  in the automation summary JSON, so future cold-boot regressions can tell
  route drift from breakpoint silence faster. Links:
  [`decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](decomp/verification/pcsx_redux_opcode_0x80_capture.lua),
  [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json)
- `2026-05-01`: corrected the `0x80` runtime capture to treat `0x800F4C28` as
  a pointer slot, added decoded-script handler probes plus selectable
  interpreter/dynarec launch modes, and validated the full retail `MAP001`
  listener-control path with `1049` reader hits and direct `0x80 -> 0x800B66E4`
  dispatch samples. Links:
  [`decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](decomp/verification/pcsx_redux_opcode_0x80_capture.lua),
  [`decomp/verification/run_opcode_0x80_runtime_capture.ps1`](decomp/verification/run_opcode_0x80_runtime_capture.ps1),
  [`decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json`](decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json),
  [`decomp/evidence/opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`decomp/evidence/opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json),
  [`decomp/evidence/opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md)
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
