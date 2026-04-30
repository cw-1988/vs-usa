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
- [`DumpAddressAccesses.java`](DumpAddressAccesses.java): headless-safe scan for
  reconstructed MIPS `lui` + load/store pairs targeting one exact address,
  useful when normal xrefs miss direct slot reads or writes
- [`TracePointerDerivedAccesses.java`](TracePointerDerivedAccesses.java):
  headless-safe trace of how a recovered pointer read is used inside a
  function, useful for checking whether a runtime table pointer is only read,
  passed onward, or written through indirectly
- [`export_function_table.py`](export_function_table.py): Python version kept
  for future `PyGhidra`-based flows
- [`Invoke-GhidraHeadlessExport.ps1`](Invoke-GhidraHeadlessExport.ps1):
  shared headless-launch helper so the task-specific wrappers only declare
  binary inputs, base addresses, and export targets
- [`export_inittbl_opcode_table.ps1`](export_inittbl_opcode_table.ps1):
  headless wrapper for `Game Data/BATTLE/INITBTL.PRG` and the current static
  opcode table candidate at `0x800FAF7C`
- [`export_inittbl_0x80_copy_slice.ps1`](export_inittbl_0x80_copy_slice.ps1):
  focused `INITBTL.PRG` instruction dump wrapper for the currently suspected
  init-time table copy routine near `0x800FAAAC`
- [`export_inittbl_runtime_opcode_table_accesses.ps1`](export_inittbl_runtime_opcode_table_accesses.ps1):
  focused `INITBTL.PRG` access sweep for direct reads/writes of runtime slot
  `0x800F4C28`
- [`export_battle_runtime_opcode_table_accesses.ps1`](export_battle_runtime_opcode_table_accesses.ps1):
  focused `BATTLE.PRG` access sweep for direct reads/writes of runtime slot
  `0x800F4C28`
- [`export_runtime_opcode_table_accesses.ps1`](export_runtime_opcode_table_accesses.ps1):
  shared wrapper for direct reads/writes of runtime slot `0x800F4C28` across
  any imported executable with a known base address
- [`export_slus_runtime_opcode_table_accesses.ps1`](export_slus_runtime_opcode_table_accesses.ps1):
  `SLUS_010.40` access sweep for direct reads/writes of runtime slot
  `0x800F4C28`, using the locally reproducible `0x8000F800` binary-loader base
  that maps file offset `0x800` to VRAM `0x80010000`
- [`export_title_runtime_opcode_table_accesses.ps1`](export_title_runtime_opcode_table_accesses.ps1):
  `TITLE.PRG` access sweep for direct reads/writes of runtime slot `0x800F4C28`
- [`export_battle_runtime_opcode_table_pointer_usage.ps1`](export_battle_runtime_opcode_table_pointer_usage.ps1):
  focused `BATTLE.PRG` pointer-usage trace for the recovered
  `FUN_800BFBB8 -> 0x800F4C28` runtime-table reader

Use these helpers to turn binary questions into local reproducible artifacts.
If `_refs/rood-reverse` suggests a location, that is only a lead; the evidence
should come back here as a tracked export.

Practical note:

- For quick instruction proof at known addresses, importing with
  `-loader BinaryLoader -loader-baseAddr ... -noanalysis` is usually enough and
  much faster than a full analysis pass.
- If a wrapper grows beyond "declare target-specific arguments and call the
  shared helper," factor the repeated launch logic back into the helper instead
  of cloning another full script body.
