# Verification Scripts

This folder holds local scripts that compare:

- binary-derived exports
- local decoder tables
- local notes
- helper decomp findings

These scripts should make contradictions visible before we need runtime.

They can also do lighter-weight raw binary sweeps when a full `Ghidra` import
would be premature, such as checking whether any packaged file still contains a
specific absolute MIPS address-access pattern.

When runtime is finally justified, this folder can still narrow the ask by
comparing exported RAM snapshots against a binary-derived baseline instead of
leaving the runtime pass as a purely manual judgment call.

Current runtime-pass helpers:

- `compare_opcode_table_snapshots.py`: compares raw RAM dumps of a copied
  opcode table against a binary-derived export baseline and can emit a
  reconstructed baseline blob plus file metadata for the compared artifacts
- `record_runtime_observation.py`: appends snapshot paths, breakpoint hits,
  dispatches, mutations, and free-form notes into a checked-in runtime
  observation packet without hand-editing the JSON; it can also import changed
  opcode rows from a generated compare report back into `table_mutations`
- `finalize_runtime_observation.py`: validates a filled runtime observation
  packet, writes the compare report, and emits a short support note that is
  ready to link from the campaign ledger

Recommended runtime handoff flow:

- keep a checked-in observation scaffold under `decomp/evidence` so the next
  `PCSX-Redux` pass starts from planned breakpoints, expected dump paths, and a
  missing-snapshot checklist instead of a blank JSON file
- let `finalize_runtime_observation.py` refresh the reconstructed baseline blob
  and compare-report hashes in place, so the handoff packet preserves concrete
  byte-level artifacts even before live dumps exist
- record each dump path, breakpoint hit, dispatch, or mutation into that
  checked-in JSON with `record_runtime_observation.py` as the runtime pass
  progresses instead of leaving those facts in emulator UI state or terminal
  history
- rerun `finalize_runtime_observation.py --allow-missing-snapshots` whenever
  the scaffold changes so the compare report and support note stay aligned with
  the observation packet even before the real dumps exist
- once dumps and breakpoint notes are recorded, rerun the same helper without
  changing the artifact layout so the packet graduates from scaffold to runtime
  evidence in place
- if the compare report shows rewritten handlers that should be called out
  explicitly, import those changed rows back into the observation packet with
  `record_runtime_observation.py import-compare --replace-derived --finalize`
  so the `table_mutations` section and generated support note stay in sync

## What To Catch Early

Good verification scripts should flag:

- binary exports produced with the wrong import base or wrong overlay
- local names that no longer match binary-derived table entries
- dispatch-table stubs that have nearby orphan candidates with stronger-looking
  behavior
- notes that claim `Confirmed` without a binary or runtime anchor

If a script cannot settle the question, it should still narrow the runtime ask.
The goal is not always to avoid `PCSX-Redux`; it is to arrive there with one
clear contradiction instead of a vague hunch.
