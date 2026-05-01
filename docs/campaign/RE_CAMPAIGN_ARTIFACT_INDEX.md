# RE Campaign Artifact Index

This catalog keeps the durable artifact list out of
[`../../RE_CAMPAIGN_MEMORY.md`](../../RE_CAMPAIGN_MEMORY.md) so the ledger can
stay focused on campaign state, conflicts, and handoff.

Register new exports and packets here when a pass leaves behind durable local
evidence under `decomp/`.

## Table Exports

- [`../../decomp/evidence/inittbl_opcode_table.json`](../../decomp/evidence/inittbl_opcode_table.json)
- [`../../decomp/evidence/inittbl_opcode_table_xrefs.json`](../../decomp/evidence/inittbl_opcode_table_xrefs.json)
- [`../../decomp/evidence/battle_sound_candidate_xrefs.json`](../../decomp/evidence/battle_sound_candidate_xrefs.json)
- [`../../decomp/evidence/battle_sound_dispatch_table.json`](../../decomp/evidence/battle_sound_dispatch_table.json)
- [`../../decomp/evidence/battle_runtime_opcode_table_xrefs.json`](../../decomp/evidence/battle_runtime_opcode_table_xrefs.json)
- [`../../decomp/evidence/battle_runtime_reader_xrefs.json`](../../decomp/evidence/battle_runtime_reader_xrefs.json)
- [`../../decomp/evidence/battle_runtime_reader_caller_xrefs.json`](../../decomp/evidence/battle_runtime_reader_caller_xrefs.json)
- [`../../decomp/evidence/inittbl_runtime_opcode_table_accesses.json`](../../decomp/evidence/inittbl_runtime_opcode_table_accesses.json)
- [`../../decomp/evidence/battle_runtime_opcode_table_accesses.json`](../../decomp/evidence/battle_runtime_opcode_table_accesses.json)
- [`../../decomp/evidence/slus_runtime_opcode_table_accesses.json`](../../decomp/evidence/slus_runtime_opcode_table_accesses.json)
- [`../../decomp/evidence/title_runtime_opcode_table_accesses.json`](../../decomp/evidence/title_runtime_opcode_table_accesses.json)
- [`../../decomp/evidence/battle_runtime_opcode_table_pointer_usage.json`](../../decomp/evidence/battle_runtime_opcode_table_pointer_usage.json)
- [`../../decomp/evidence/inittbl_system_dat_loader_slice.json`](../../decomp/evidence/inittbl_system_dat_loader_slice.json)
- [`../../decomp/evidence/system_dat_header_words.json`](../../decomp/evidence/system_dat_header_words.json)
- [`../../decomp/evidence/runtime_opcode_table_binary_scan.json`](../../decomp/evidence/runtime_opcode_table_binary_scan.json)
- [`../../decomp/evidence/opcode_0x80_runtime_automation_summary.json`](../../decomp/evidence/opcode_0x80_runtime_automation_summary.json)
- [`../../decomp/evidence/opcode_0x80_runtime_snapshot_compare.json`](../../decomp/evidence/opcode_0x80_runtime_snapshot_compare.json)

## Handler Slices

- [`../../decomp/evidence/battle_0x80_handler_slices.json`](../../decomp/evidence/battle_0x80_handler_slices.json)
- [`../../decomp/evidence/battle_sound_candidate_slice.json`](../../decomp/evidence/battle_sound_candidate_slice.json)
- [`../../decomp/evidence/inittbl_0x80_copy_slice.json`](../../decomp/evidence/inittbl_0x80_copy_slice.json)
- [`../../decomp/evidence/battle_0x80_sound_cluster_slices.json`](../../decomp/evidence/battle_0x80_sound_cluster_slices.json)
- [`../../decomp/evidence/battle_runtime_reader_call_chain_slices.json`](../../decomp/evidence/battle_runtime_reader_call_chain_slices.json)
- [`../../decomp/evidence/battle_runtime_reader_caller_slice.json`](../../decomp/evidence/battle_runtime_reader_caller_slice.json)

## Reconciliation Reports

- [`../../decomp/evidence/opcode_0x80_copy_path_static.md`](../../decomp/evidence/opcode_0x80_copy_path_static.md)
- [`../../decomp/evidence/opcode_0x80_sound_cluster_static.md`](../../decomp/evidence/opcode_0x80_sound_cluster_static.md)
- [`../../decomp/evidence/opcode_0x80_runtime_dispatch_static.md`](../../decomp/evidence/opcode_0x80_runtime_dispatch_static.md)
- [`../../decomp/evidence/opcode_0x80_runtime_slot_access_static.md`](../../decomp/evidence/opcode_0x80_runtime_slot_access_static.md)
- [`../../decomp/evidence/opcode_0x80_runtime_pointer_usage_static.md`](../../decomp/evidence/opcode_0x80_runtime_pointer_usage_static.md)
- [`../../decomp/evidence/opcode_0x80_runtime_reader_call_chain_static.md`](../../decomp/evidence/opcode_0x80_runtime_reader_call_chain_static.md)
- [`../../decomp/evidence/opcode_0x80_system_dat_static.md`](../../decomp/evidence/opcode_0x80_system_dat_static.md)
- [`../../decomp/evidence/opcode_0x80_binary_address_scan.md`](../../decomp/evidence/opcode_0x80_binary_address_scan.md)
- [`../../decomp/evidence/opcode_0x80_runtime_capture_plan.md`](../../decomp/evidence/opcode_0x80_runtime_capture_plan.md)
- [`../../decomp/evidence/opcode_0x80_runtime_input_plan.json`](../../decomp/evidence/opcode_0x80_runtime_input_plan.json)
- [`../../decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json`](../../decomp/evidence/opcode_0x80_runtime_input_plan_map001_listener.json)
- [`../../decomp/evidence/opcode_0x80_runtime_input_plan_bat_kill.json`](../../decomp/evidence/opcode_0x80_runtime_input_plan_bat_kill.json)
- [`../../decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md`](../../decomp/evidence/opcode_0x80_runtime_bat_kill_negative.md)
- [`../../decomp/evidence/opcode_0x80_runtime_memcard_probe.md`](../../decomp/evidence/opcode_0x80_runtime_memcard_probe.md)
- [`../../decomp/evidence/opcode_0x80_runtime_memcard_probe.json`](../../decomp/evidence/opcode_0x80_runtime_memcard_probe.json)
- [`../../decomp/evidence/opcode_0x80_runtime_support.md`](../../decomp/evidence/opcode_0x80_runtime_support.md)
- [`../../decomp/evidence/opcode_0x80_runtime_automation_summary.json`](../../decomp/evidence/opcode_0x80_runtime_automation_summary.json)
- [`../../decomp/evidence/opcode_0x80_runtime_expected_table.bin`](../../decomp/evidence/opcode_0x80_runtime_expected_table.bin)

## Proof Packets

- [`../../decomp/evidence/opcode_0x80_cli_pass.md`](../../decomp/evidence/opcode_0x80_cli_pass.md)
- [`../../decomp/evidence/opcode_0x80_semantic_proof.md`](../../decomp/evidence/opcode_0x80_semantic_proof.md)
- [`../../decomp/evidence/opcode_0x80_neighbor_sound_context.md`](../../decomp/evidence/opcode_0x80_neighbor_sound_context.md)
- [`../../decomp/evidence/opcode_0x80_neighbor_consumer_comparison.md`](../../decomp/evidence/opcode_0x80_neighbor_consumer_comparison.md)
- [`../../decomp/evidence/opcode_0x80_neighbor_consumer_scan.json`](../../decomp/evidence/opcode_0x80_neighbor_consumer_scan.json)
- [`../../decomp/evidence/opcode_0x80_residual_context.md`](../../decomp/evidence/opcode_0x80_residual_context.md)
- [`../../decomp/evidence/opcode_0x80_residual_scan.json`](../../decomp/evidence/opcode_0x80_residual_scan.json)
- [`../../decomp/evidence/opcode_0x80_shared_stub_family_audit.md`](../../decomp/evidence/opcode_0x80_shared_stub_family_audit.md)
- [`../../decomp/evidence/opcode_0x80_runtime_observation_template.json`](../../decomp/evidence/opcode_0x80_runtime_observation_template.json)
- [`../../decomp/evidence/opcode_0x80_runtime_observation.json`](../../decomp/evidence/opcode_0x80_runtime_observation.json)
- [`../../decomp/evidence/opcode_0x80_runtime_snapshot_compare.json`](../../decomp/evidence/opcode_0x80_runtime_snapshot_compare.json)

## Verification Helpers

- [`../../decomp/verification/compare_opcode_table_snapshots.py`](../../decomp/verification/compare_opcode_table_snapshots.py)
- [`../../decomp/verification/record_runtime_observation.py`](../../decomp/verification/record_runtime_observation.py)
- [`../../decomp/verification/finalize_runtime_observation.py`](../../decomp/verification/finalize_runtime_observation.py)
- [`../../decomp/verification/analyze_opcode_0x80_residuals.py`](../../decomp/verification/analyze_opcode_0x80_residuals.py)
- [`../../decomp/verification/pcsx_redux_opcode_0x80_capture.lua`](../../decomp/verification/pcsx_redux_opcode_0x80_capture.lua)
- [`../../decomp/verification/run_opcode_0x80_runtime_capture.ps1`](../../decomp/verification/run_opcode_0x80_runtime_capture.ps1)
- [`../../decomp/verification/probe_psx_memcards.py`](../../decomp/verification/probe_psx_memcards.py)
