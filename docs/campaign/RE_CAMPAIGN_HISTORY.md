# RE Campaign History

This archive keeps milestone buildup out of
[`../../RE_CAMPAIGN_MEMORY.md`](../../RE_CAMPAIGN_MEMORY.md) so the active
ledger stays focused on current state, conflicts, and handoff.

## Milestones

- `2026-05-01`: corrected the `0x80` runtime capture to dereference pointer
  slot `0x800F4C28`, added decoded-script handler probes plus selectable
  interpreter/dynarec launch modes, and turned the stripped `MAP001` `New
  Game` route into a real retail-runtime positive control with live reader and
  handler hits. Links:
  [`../../decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](../../decomp/verification/pcsx_redux_opcode_0x80_capture.lua),
  [`../../decomp/verification/run_opcode_0x80_runtime_capture.ps1`](../../decomp/verification/run_opcode_0x80_runtime_capture.ps1),
  [`../../decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json`](../../decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json),
  [`../../decomp/evidence/opcode_0x80_runtime_automation_summary.json`](../../decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`../../decomp/evidence/opcode_0x80_runtime_observation.json`](../../decomp/evidence/opcode_0x80_runtime_observation.json)
- `2026-05-01`: preserved a stronger cold-boot negative-control route for the
  `0x80` runtime contradiction by checking in the bat-control input plan and
  its no-hit runtime packet. Links:
  [`../../decomp/evidence/opcode_0x80_runtime_input_plan_bat_kill.json`](../../decomp/evidence/opcode_0x80_runtime_input_plan_bat_kill.json),
  [`../../decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md`](../../decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md),
  [`../../decomp/evidence/opcode_0x80_runtime_automation_summary.json`](../../decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`../../decomp/evidence/opcode_0x80_runtime_observation.json`](../../decomp/evidence/opcode_0x80_runtime_observation.json)
- `2026-05-01`: taught the `0x80` runtime capture flow to preserve frame-stamped
  input-plan step notes in the automation summary, making it easier to tell
  route drift from breakpoint silence on future reruns. Links:
  [`../../decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](../../decomp/verification/pcsx_redux_opcode_0x80_capture.lua),
  [`../../decomp/evidence/opcode_0x80_runtime_automation_summary.json`](../../decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`../../decomp/evidence/opcode_0x80_runtime_support.md`](../../decomp/evidence/opcode_0x80_runtime_support.md)
- `2026-05-01`: added the checked-in no-savestate fallback for the `0x80`
  runtime tie-breaker by replaying a JSON pad-input plan and hardening the
  wrapper/Lua callbacks. Links:
  [`../../decomp/verification/run_opcode_0x80_runtime_capture.ps1`](../../decomp/verification/run_opcode_0x80_runtime_capture.ps1),
  [`../../decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](../../decomp/verification/pcsx_redux_opcode_0x80_capture.lua),
  [`../../decomp/evidence/opcode_0x80_runtime_input_plan.json`](../../decomp/evidence/opcode_0x80_runtime_input_plan.json),
  [`../../decomp/evidence/opcode_0x80_runtime_capture_plan.md`](../../decomp/evidence/opcode_0x80_runtime_capture_plan.md)
- `2026-04-30`: created the master campaign ledger and aligned the workflow
  docs around it. Links:
  [`../../README.md`](../../README.md),
  [`../workflows/AI_RE_PASS_WORKFLOW.md`](../workflows/AI_RE_PASS_WORKFLOW.md),
  [`../workflows/CLI_DECOMPILATION_WORKFLOW.md`](../workflows/CLI_DECOMPILATION_WORKFLOW.md),
  [`../workflows/DECOMPILATION_STRATEGY.md`](../workflows/DECOMPILATION_STRATEGY.md),
  [`../../decomp/README.md`](../../decomp/README.md)
- `2026-04-30`: indexed the first local `0x80` conflict packet into the
  campaign memory and rebuilt the copy-path and sound-neighborhood notes from
  local exports. Links:
  [`../../decomp/evidence/opcode_0x80_cli_pass.md`](../../decomp/evidence/opcode_0x80_cli_pass.md),
  [`../../decomp/evidence/opcode_0x80_copy_path_static.md`](../../decomp/evidence/opcode_0x80_copy_path_static.md),
  [`../../decomp/evidence/opcode_0x80_sound_cluster_static.md`](../../decomp/evidence/opcode_0x80_sound_cluster_static.md),
  [`../../decomp/evidence/inittbl_0x80_copy_slice.json`](../../decomp/evidence/inittbl_0x80_copy_slice.json)
- `2026-04-30`: recovered the local `BATTLE.PRG` sound subdispatch table and
  the live runtime-table consumer, then added direct-slot and pointer-usage
  sweeps to narrow the contradiction. Links:
  [`../../decomp/evidence/battle_sound_dispatch_table.json`](../../decomp/evidence/battle_sound_dispatch_table.json),
  [`../../decomp/evidence/battle_runtime_opcode_table_xrefs.json`](../../decomp/evidence/battle_runtime_opcode_table_xrefs.json),
  [`../../decomp/evidence/battle_runtime_opcode_table_accesses.json`](../../decomp/evidence/battle_runtime_opcode_table_accesses.json),
  [`../../decomp/evidence/battle_runtime_opcode_table_pointer_usage.json`](../../decomp/evidence/battle_runtime_opcode_table_pointer_usage.json)
- `2026-04-30`: widened the static reconciliation pass by scanning additional
  executables and narrowing `SYSTEM.DAT` from "possible overlay" to payload
  data. Links:
  [`../../decomp/evidence/slus_runtime_opcode_table_accesses.json`](../../decomp/evidence/slus_runtime_opcode_table_accesses.json),
  [`../../decomp/evidence/title_runtime_opcode_table_accesses.json`](../../decomp/evidence/title_runtime_opcode_table_accesses.json),
  [`../../decomp/evidence/inittbl_system_dat_loader_slice.json`](../../decomp/evidence/inittbl_system_dat_loader_slice.json),
  [`../../decomp/evidence/system_dat_header_words.json`](../../decomp/evidence/system_dat_header_words.json)
- `2026-04-30`: added a reusable raw-binary address scanner and used it to
  show that the packaged corpus only reproduces the known `INITBTL.PRG` write
  and `BATTLE.PRG` read, which promoted `0x80` to `runtime_needed`. Links:
  [`../../decomp/verification/scan_mips_address_accesses.py`](../../decomp/verification/scan_mips_address_accesses.py),
  [`../../decomp/evidence/runtime_opcode_table_binary_scan.json`](../../decomp/evidence/runtime_opcode_table_binary_scan.json),
  [`../../decomp/evidence/opcode_0x80_binary_address_scan.md`](../../decomp/evidence/opcode_0x80_binary_address_scan.md)
- `2026-04-30`: turned the `0x80` runtime tie-breaker into a checked-in packet
  with compare, recorder, and finalizer helpers plus expected baseline data and
  support notes. Links:
  [`../../decomp/verification/compare_opcode_table_snapshots.py`](../../decomp/verification/compare_opcode_table_snapshots.py),
  [`../../decomp/verification/record_runtime_observation.py`](../../decomp/verification/record_runtime_observation.py),
  [`../../decomp/verification/finalize_runtime_observation.py`](../../decomp/verification/finalize_runtime_observation.py),
  [`../../decomp/evidence/opcode_0x80_runtime_observation.json`](../../decomp/evidence/opcode_0x80_runtime_observation.json)
- `2026-04-30`: added the no-HITL-first `PCSX-Redux` startup Lua and wrapper,
  validated the cold-boot path against the local disc image, and then made the
  runtime flow savestate-ready for future battle-near captures. Links:
  [`../../decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](../../decomp/verification/pcsx_redux_opcode_0x80_capture.lua),
  [`../../decomp/verification/run_opcode_0x80_runtime_capture.ps1`](../../decomp/verification/run_opcode_0x80_runtime_capture.ps1),
  [`../../decomp/evidence/opcode_0x80_runtime_automation_summary.json`](../../decomp/evidence/opcode_0x80_runtime_automation_summary.json),
  [`../../decomp/evidence/opcode_0x80_runtime_support.md`](../../decomp/evidence/opcode_0x80_runtime_support.md)
