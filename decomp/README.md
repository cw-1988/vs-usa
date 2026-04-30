# Local Decomp Workspace

This folder is the tracked home for local decompilation support code and proof
artifacts.

Use it for:

- scripted `Ghidra` helpers
- verification and reconciliation scripts
- exported machine-readable evidence

Keep campaign state out of this folder. The cross-session memory and handoff
ledger lives at [`../RE_CAMPAIGN_MEMORY.md`](../RE_CAMPAIGN_MEMORY.md).

Keep large binary tools out of here.
Those stay under ignored [`tools`](../tools).

## Layout

- [`ghidra`](ghidra): `Ghidra`-side scripts or notes
- [`verification`](verification): local verification scripts
- [`evidence`](evidence): exported JSON or proof packets

That means:

- [`../RE_CAMPAIGN_MEMORY.md`](../RE_CAMPAIGN_MEMORY.md): campaign state,
  priorities, conflict summaries, and session handoff
- [`../docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md`](../docs/campaign/RE_CAMPAIGN_ARTIFACT_INDEX.md):
  grouped catalog of durable exports, proof packets, and verification helpers
- [`decomp`](.): implementation helpers and durable evidence artifacts

## Working Rule

This folder should support the standards in:

- [`../docs/workflows/DECOMPILATION_STRATEGY.md`](../docs/workflows/DECOMPILATION_STRATEGY.md)
- [`../docs/workflows/CLI_DECOMPILATION_WORKFLOW.md`](../docs/workflows/CLI_DECOMPILATION_WORKFLOW.md)

## Watch-Outs

Keep this area useful for the next pass, not just the current one:

- record the exact binary inputs and base addresses used for exports
- prefer small text artifacts that can be diffed and reread later
- if a result is conflicted, store both sides of the conflict instead of
  forcing a single winner too early
- treat helper-decomp names as provenance, not as proof
- if `_refs/rood-reverse` suggests an address or interpretation, create a
  local export or proof artifact here before promoting that claim
