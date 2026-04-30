# CLI-First Decompilation Workflow

This note describes how to do most local decompilation work from the command
line.

Use this together with
[`DECOMPILATION_STRATEGY.md`](DECOMPILATION_STRATEGY.md).

The goal is simple:

- do routine recovery, verification, and contradiction scans with CLI tools
- use `Ghidra` headless or scripted output as the main static-analysis engine
- treat `PCSX-Redux` as a conflict-breaker, not the default first step

## Principle

Prefer this evidence order for day-to-day work:

1. decoded script usage
2. binary-derived tables and function facts exported from `Ghidra`
3. local verification scripts
4. helper decomp comparison
5. `PCSX-Redux` only if the first four still disagree

## Local Tracked Workspace

Use the tracked [`decomp`](decomp) folder for local decompilation support code.

Recommended responsibilities:

- [`decomp/ghidra`](decomp/ghidra): scripts and notes for headless or scripted
  `Ghidra` work
- [`decomp/verification`](decomp/verification): Python verification scripts
  that compare local notes, exported tables, and helper sources
- [`decomp/evidence`](decomp/evidence): structured proof packets and exported
  machine-readable facts

Do not put large binary tool installs here. Keep those under ignored `tools/`.

## Default CLI Pipeline

### 1. Start from real script usage

Use the local decoder and generated output first:

- [`dump_mpd_script.py`](dump_mpd_script.py)
- [`decoded_scripts`](decoded_scripts)

Questions to answer before touching runtime:

- how many real rooms use the opcode?
- what repeated argument shapes appear?
- does the opcode cluster with camera, sound, room-load, or effect commands?
- do different rooms show the same reset or neutral pattern?

### 2. Export binary facts from `Ghidra`

Use `analyzeHeadless` or scripted `Ghidra` runs to export facts such as:

- dispatch table entries
- function start and end addresses
- xrefs for key globals and helpers
- gaps between adjacent named functions
- nearby orphan candidates around disputed handler ranges

These exports should be treated as the main static-analysis truth layer.

Important watch-outs:

- Raw PS1 overlay imports are not self-describing. If the file is not a
  `PS-X EXE`, set the `BinaryLoader` base address explicitly from the relevant
  `splat.yaml` instead of trusting the default import mapping.
- Keep the import base, table address, and file identity together in the same
  wrapper or proof packet. Many false contradictions are really address-mapping
  mistakes.
- Prefer headless-safe `GhidraScript` Java helpers for repeatable CLI passes.
  `PyGhidra`-style Python helpers may not be available under
  `analyzeHeadless`.
- If you already know the address you want to inspect, a `-noanalysis`
  instruction dump is often enough and much faster than a full auto-analysis
  pass.

### 3. Reconcile locally

Run local verification scripts against:

- binary-derived exports from `Ghidra`
- local decoder tables
- local notes
- helper decomp material

This is where we should catch:

- local names that no longer fit the binary mapping
- helper-decomp contradictions
- stub-table entries with nearby meaningful orphan handlers
- notes that overclaim current evidence

### 4. Escalate only if needed

If static evidence still conflicts after the reconciliation pass, then use
`PCSX-Redux` for:

- confirming the handler that actually executes
- checking whether a copied dispatch table is patched in RAM
- proving a disputed side effect
- deciding between two static candidates that both still look plausible

## When `PCSX-Redux` Is Not Needed

Do not jump to runtime first if the question can be answered by:

- a raw dispatch table export
- clear function-boundary recovery
- a reliable consumer path in static analysis
- a local contradiction scan that already resolves cleanly

Runtime should usually be the last major step, not the first.

## First CLI Targets

The first high-value tracked scripts should be:

1. `export_opcode_table`
2. `audit_function_coverage`
3. `opcode_reconcile`

Those three tools cover most of the static truth layer needed for script opcode
work.

## Suggested CLI Artifacts

### Opcode table export

Store as JSON under [`decomp/evidence`](decomp/evidence), for example:

```text
decomp/evidence/battle_opcode_table.json
```

Suggested fields:

- `overlay`
- `table_name`
- `table_address`
- `entries`
  - `opcode`
  - `handler_address`
  - `handler_name`

### Function coverage export

Suggested fields:

- `overlay`
- `functions`
  - `start`
  - `end`
  - `name`
  - `source`
- `gaps`
- `orphan_candidates`

### Opcode proof packet

Suggested fields:

- `opcode`
- `binary_handler`
- `helper_handler`
- `local_name`
- `script_examples`
- `consumer_notes`
- `status`
- `open_conflicts`

## Conflict States

Not every pass should end in a rename.

Use these outcomes deliberately:

- `confirmed`: binary and script evidence agree, and runtime is either
  unnecessary or already aligned
- `tentative`: the working name is still useful, but the proof packet does not
  settle it
- `conflicted`: strong static evidence disagrees and should be recorded before
  any runtime escalation

If a binary table says one thing and a nearby orphan helper says another, do
not collapse that into a fake clean answer. Preserve both in the proof packet.

## Escalation Rule

Escalate to `PCSX-Redux` only after all of these are true:

1. the loader/base-address mapping has been checked
2. the relevant binary table or code slice has been exported
3. local reconciliation still leaves a real contradiction
4. the contradiction matters to the final claim

## Practical Rule

If a disputed opcode cannot survive:

- script-pattern review
- `Ghidra` table export
- local reconciliation

then stop and use `PCSX-Redux` to break the tie.

If it does survive those three, runtime can often wait.
