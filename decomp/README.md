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
  priorities, conflict summaries, artifact links, and session handoff
- [`decomp`](.): implementation helpers and durable evidence artifacts

## Working Rule

This folder should support the standards in:

- [`../DECOMPILATION_STRATEGY.md`](../DECOMPILATION_STRATEGY.md)
- [`../CLI_DECOMPILATION_WORKFLOW.md`](../CLI_DECOMPILATION_WORKFLOW.md)

## Watch-Outs

Keep this area useful for the next pass, not just the current one:

- record the exact binary inputs and base addresses used for exports
- prefer small text artifacts that can be diffed and reread later
- if a result is conflicted, store both sides of the conflict instead of
  forcing a single winner too early
- treat helper-decomp names as provenance, not as proof
