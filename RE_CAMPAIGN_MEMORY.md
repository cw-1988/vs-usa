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

Current phase: Pass 5 - Naming and decoder updates

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
| `opcode 0x80` | `tentative` | `INITBTL.PRG` static table at `0x800FAF7C`, copied by the init-time routine at `0x800FAAAC` into pointer slot `0x800F4C28` and resolved live at `0x801119F0`; checked `after_init` and `pre_dispatch` snapshots still match that copied baseline byte-for-byte | Initial slot `0x800B66E4` is a shared return-zero stub reused by a widened `30`-opcode `INITBTL.PRG` family that includes named dialog, model, room, battle-end, and music-looking members as well as `0x80-0x82`; former competing target `0x800BA2E0` is now locally anchored to the separate `BATTLE.PRG` sound subdispatch table at `0x800E9F30`; recovered reader `FUN_800BFBB8` dispatches through the copied runtime table via `jalr`, and the validated `MAP001` listener-control run logs retail `0x10`, `0x13`, `0x44`, and `0x80` landing on `0x800B66E4` with no post-init table-write hits | `Opcode80SharedStub` | Now that the widened `0x800B66E4` family is explicit, which neighboring opcodes or prepared-state paths explain the audio-looking `0x80` script sites well enough to retire the historical sound label everywhere? | `Pass 5 - Naming and decoder updates` | [`opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md), [`opcode_0x80_semantic_proof.md`](decomp/evidence/opcode_0x80_semantic_proof.md), [`opcode_0x80_neighbor_sound_context.md`](decomp/evidence/opcode_0x80_neighbor_sound_context.md), [`opcode_0x80_shared_stub_family_audit.md`](decomp/evidence/opcode_0x80_shared_stub_family_audit.md), [`opcode_0x80_copy_path_static.md`](decomp/evidence/opcode_0x80_copy_path_static.md), [`opcode_0x80_sound_cluster_static.md`](decomp/evidence/opcode_0x80_sound_cluster_static.md), [`opcode_0x80_runtime_dispatch_static.md`](decomp/evidence/opcode_0x80_runtime_dispatch_static.md), [`opcode_0x80_runtime_slot_access_static.md`](decomp/evidence/opcode_0x80_runtime_slot_access_static.md), [`opcode_0x80_runtime_reader_call_chain_static.md`](decomp/evidence/opcode_0x80_runtime_reader_call_chain_static.md), [`opcode_0x80_binary_address_scan.md`](decomp/evidence/opcode_0x80_binary_address_scan.md), [`opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md), [`opcode_0x80_runtime_memcard_probe.md`](decomp/evidence/opcode_0x80_runtime_memcard_probe.md), [`opcode_0x80_runtime_bat_kill_negative.md`](decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md), [`opcode_0x80_runtime_input_plan_bat_kill.json`](decomp/evidence/opcode_0x80_runtime_input_plan_bat_kill.json), [`opcode_0x80_runtime_input_plan_map001_listener.json`](decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json), [`opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json), [`opcode_0x80_runtime_observation.json`](decomp/evidence/opcode_0x80_runtime_observation.json), [`opcode_0x80_runtime_snapshot_compare.json`](decomp/evidence/opcode_0x80_runtime_snapshot_compare.json), [`opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md) |

## Known Conflicts

### `0x80`: historical sound label vs verified shared stub

- What static and runtime evidence now agree on:
  `inittbl_opcode_table.json` and `battle_0x80_handler_slices.json` still map
  `0x80-0x82` to the shared stub at `0x800B66E4`, whose first two
  instructions are only `jr ra` / `clear v0`.
  `inittbl_0x80_copy_slice.json` proves the init-time copy from `0x800FAF7C`
  into runtime slot `0x800F4C28`, and
  `battle_runtime_opcode_table_xrefs.json` proves `FUN_800BFBB8` reads that
  runtime table and dispatches through it with `jalr`.
  The validated `MAP001` listener-control pass then resolves the live table at
  `0x801119F0`, repeatedly hits
  `0x8007A36C -> 0x800BF850 -> 0x800BFBB8`, and records retail
  `0x80 -> 0x800B66E4` dispatches directly from the untouched intro script.
  `opcode_0x80_runtime_support.md` now compares both checked snapshots against
  the reconstructed baseline and reports `256` matching entries and `0`
  changed entries for both `after_init` and `pre_dispatch`, while the live
  write watchpoint over `0x801119F0-0x80111DEF` stays quiet.
- What that rules out:
  The old copy/patch contradiction is now closed for the checked route.
  Local evidence no longer supports a post-init rewrite of the copied `0x80`
  slot before the validated intro dispatch.
  The former competing helper `0x800BA2E0` also no longer survives as a hidden
  direct `0x80` target because `opcode_0x80_sound_cluster_static.md` anchors
  it inside a separate local `BATTLE.PRG` sound subdispatch table rooted at
  `0x800E9F30` alongside the visible `0x83+` family.
- What the safe semantic floor is:
  The strongest local interpretation is now structural, not audio-facing:
  treat `0x80` as `Opcode80SharedStub`, a shared return-zero dispatch slot
  reused by `0x80-0x82` and several other opcode IDs.
  The widened family audit now makes that lack of uniqueness explicit:
  the same `INITBTL.PRG` table slot also covers named dialog, model,
  engine-mode, room, battle-end, and music-looking members such as `0x10`,
  `0x11`, `0x22`, `0x44`, `0x54`, `0x69`, `0x6D`, and `0x92`.
  That means table membership alone is not direct user-facing proof for any
  member of the cluster.
  `SoundEffects0` is now an overclaim for the opcode itself.
  Any audible effect near `0x80` script sites must currently be attributed to
  neighboring opcodes, previously prepared state, or some other subsystem not
  proven to dispatch from `0x80`.
- What still remains open:
  The main remaining question is not table ownership but semantic cleanup:
  why content authors still placed `0x80` in sound-looking cutscene moments,
  and whether those moments can be reassigned cleanly to nearby confirmed
  sound-family behavior without inventing a new direct role for the stubbed
  opcode.
  The new neighboring-context packet now gives that cleanup a stronger
  script-side foothold: `88` of the `127` decoded-script files that contain
  `0x80` also co-host explicit `0x85`, `0x88`, `0x90`, `0x92`, `0x9D`, or
  `0x9E` sound-family neighbors, and representative scenes such as `MAP001`,
  `MAP026`, and `MAP415` arm those neighboring paths before later `0x80`
  bursts.
  What still stays open is which one of those prepared-state families is the
  decisive consumer for each scene.
- Is runtime justified yet:
  Not for the copy/patch tie-breaker.
  Keep the validated `MAP001` listener route only as a regression path when
  runtime instrumentation changes or a new semantic hypothesis needs live
  checking.

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

- `last completed step`: the `Pass 5` neighboring-sound context packet for
  `0x80` is now checked in.
  The validated `MAP001` listener-control route and shared-family audit had
  already closed the direct-handler question.
  The new packet
  [`opcode_0x80_neighbor_sound_context.md`](decomp/evidence/opcode_0x80_neighbor_sound_context.md)
  adds the positive script-side explanation the handoff asked for:
  many representative audio-looking `0x80` scenes already co-host explicit
  `0x85`, `0x88`, `0x90`, `0x92`, `0x9D`, and `0x9E` setup, so the historical
  sound label is no longer the least-bad explanation for those moments.
- `next recommended step`: keep `0x80` as a `Pass 5` semantic cleanup target,
  not a runtime blocker. Preferred order for the next pass:
  1. use the shared-family audit plus the neighboring-context packet as naming
     constraints:
     do not treat `0x800B66E4` table membership as standalone proof for
     `0x80`, `0x10`, `0x11`, `0x22`, `0x69`, `0x6D`, `0x92`, or any other
     member of the widened cluster, and do not treat script-side co-location
     alone as proof that `0x80` is itself the direct sound trigger
  2. focus the next semantic pass on the consumer relationship between the
     already-proven neighboring sound families:
     compare how `0x9D` plus `0x9E` queueing, `0x90` plus `0x92` music-slot
     playback, and `0x85` plus `0x88` SFX-slot selection account for the same
     representative `MAP001`, `MAP026`, and `MAP415` scenes
  3. if a new semantic theory needs live checking, rerun the validated
     `MAP001` listener route with
     `decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json`
     so the probe set stays grounded in the same retail intro script
  4. keep the bat-control route only as a negative-control regression, because
     it still proves that early free movement/combat is a poor proxy trigger
     for the intro-side `0x80` question
- `do not forget`: preserve the distinction between structural proof and
  semantic speculation.
  `0x800B66E4` is proven; a direct sound-effect meaning for `0x80` is not.
  Keep the raw dumps, compare report, and savestate bridge artifacts registered
  under `decomp/evidence`, and label any future custom-`PRG` or patched-ISO
  validation as tooling proof rather than retail-runtime opcode proof.

## Completed Milestones

- `2026-05-01`: completed the `Pass 5` neighboring-sound context packet for
  `0x80`.
  A direct decoded-script scan now shows that `88` of the `127` files
  containing legacy-rendered `0x80` lines also co-host at least one explicit
  sound-family neighbor from `0x85`, `0x88`, `0x90`, `0x92`, `0x9D`, or
  `0x9E`, with `49` files containing all three prepared-state categories:
  `0x85/0x88`, `0x90/0x92`, and `0x9D/0x9E`.
  Representative scenes such as `MAP001`, `MAP026`, and `MAP415` now show
  those neighboring sound opcodes arming SFX slots, music slots, or
  sound-file queues before later `0x80` bursts.
  This does not prove the final consumer yet, but it retires the old
  `SoundEffects0` label for a stronger positive reason than "the handler is a
  stub."
  Links:
  [`opcode_0x80_neighbor_sound_context.md`](decomp/evidence/opcode_0x80_neighbor_sound_context.md),
  [`decoded_scripts/24-Unmapped/001-Unknown Room.txt`](decoded_scripts/24-Unmapped/001-Unknown%20Room.txt),
  [`decoded_scripts/1-Wine Cellar/026-The Gallows.txt`](decoded_scripts/1-Wine%20Cellar/026-The%20Gallows.txt),
  [`decoded_scripts/23-Great Cathedral/415-The Dark tempts Ashley.txt`](decoded_scripts/23-Great%20Cathedral/415-The%20Dark%20tempts%20Ashley.txt)
- `2026-05-01`: completed the widened `0x800B66E4` shared-stub family audit
  for `0x80`.
  The binary-derived `INITBTL.PRG` table now explicitly shows `30` opcode
  slots sharing that return-zero stub, including named dialog, model, room,
  battle-end, and music-looking members, and the validated retail `MAP001`
  route directly samples non-`0x80` members (`0x10`, `0x13`, and `0x44`)
  hitting the same live stub.
  This closes the last "maybe `0x80` is uniquely sound-special" table-reading
  angle and moves the next cleanup step toward neighboring-opcode or
  prepared-state explanation instead of more table ownership work.
  Links:
  [`opcode_0x80_shared_stub_family_audit.md`](decomp/evidence/opcode_0x80_shared_stub_family_audit.md),
  [`inittbl_opcode_table.json`](decomp/evidence/inittbl_opcode_table.json),
  [`opcode_0x80_runtime_automation_summary.json`](decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`opcode_0x80_semantic_proof.md`](decomp/evidence/opcode_0x80_semantic_proof.md)
- `2026-05-01`: completed the first `Pass 5` naming cleanup for `0x80` by
  retiring the direct `SoundEffects0` claim in the forward-facing decoder row,
  behavior reference row, and future `MAP001` listener-plan description while
  preserving the structural `Opcode80SharedStub` wording. This same audit also
  confirmed that the shared return-zero stub at `0x800B66E4` reaches a much
  wider opcode family than `0x80-0x82`, so later naming cleanup should start
  from that family-wide proof question instead of assuming `0x80` is unique.
  Links:
  [`dump_mpd_script.py`](dump_mpd_script.py),
  [`docs/campaign/OPCODE_BEHAVIOR_REFERENCE.md`](docs/campaign/OPCODE_BEHAVIOR_REFERENCE.md),
  [`decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json`](decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json),
  [`decomp/evidence/opcode_0x80_runtime_capture_plan.md`](decomp/evidence/opcode_0x80_runtime_capture_plan.md)
- `2026-05-01`: closed `0x80` `Pass 3` with the checked `MAP001` runtime
  packet, then promoted the target into a `Pass 4` semantic proof that retires
  the old direct-sound reading in favor of the safer shared-stub
  interpretation. Links:
  [`decomp/evidence/opcode_0x80_cli_pass.md`](decomp/evidence/opcode_0x80_cli_pass.md),
  [`decomp/evidence/opcode_0x80_semantic_proof.md`](decomp/evidence/opcode_0x80_semantic_proof.md),
  [`decomp/evidence/opcode_0x80_runtime_support.md`](decomp/evidence/opcode_0x80_runtime_support.md),
  [`decomp/evidence/opcode_0x80_runtime_snapshot_compare.json`](decomp/evidence/opcode_0x80_runtime_snapshot_compare.json)
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
