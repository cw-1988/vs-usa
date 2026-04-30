# Ghidra CLI Notes

Put tracked headless or scripted `Ghidra` helpers here.

Typical uses:

- export dispatch tables
- dump function ranges
- collect xrefs
- flag suspicious gaps or orphan candidates

The local binary tool install still lives under ignored `tools/`.

Current tracked entry points:

- [`ExportFunctionTable.java`](ExportFunctionTable.java): headless-safe JSON
  export for 4-byte function-pointer tables
- [`DumpInstructions.java`](DumpInstructions.java): headless-safe code-slice
  dump for one or more explicit addresses, useful when a disputed opcode needs
  binary-first instruction proof before runtime tracing
- [`export_function_table.py`](export_function_table.py): Python version kept
  for future `PyGhidra`-based flows
- [`export_inittbl_opcode_table.ps1`](export_inittbl_opcode_table.ps1):
  headless wrapper for `Game Data/BATTLE/INITBTL.PRG` and the current static
  opcode table candidate at `0x800FAF7C`
- [`export_inittbl_0x80_copy_slice.ps1`](export_inittbl_0x80_copy_slice.ps1):
  focused `INITBTL.PRG` instruction dump wrapper for the currently suspected
  init-time table copy routine near `0x800FAAAC`

Use these helpers to turn binary questions into local reproducible artifacts.
If `_refs/rood-reverse` suggests a location, that is only a lead; the evidence
should come back here as a tracked export.

Practical note:

- For quick instruction proof at known addresses, importing with
  `-loader BinaryLoader -loader-baseAddr ... -noanalysis` is usually enough and
  much faster than a full analysis pass.
