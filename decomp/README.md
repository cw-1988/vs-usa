# Local Decomp Workspace

This folder is the tracked home for local decompilation support code and proof
artifacts.

Use it for:

- scripted `Ghidra` helpers
- verification and reconciliation scripts
- exported machine-readable evidence

Keep large binary tools out of here.
Those stay under ignored [`tools`](../tools).

## Layout

- [`ghidra`](ghidra): `Ghidra`-side scripts or notes
- [`verification`](verification): local verification scripts
- [`evidence`](evidence): exported JSON or proof packets

## Working Rule

This folder should support the standards in:

- [`../DECOMPILATION_STRATEGY.md`](../DECOMPILATION_STRATEGY.md)
- [`../CLI_DECOMPILATION_WORKFLOW.md`](../CLI_DECOMPILATION_WORKFLOW.md)
