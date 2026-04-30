# CLI-First Decompilation Workflow

This note describes how to do most local decompilation work from the command
line.

Use this together with
[`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md) and
[`DECOMPILATION_STRATEGY.md`](DECOMPILATION_STRATEGY.md).

The goal is simple:

- do routine recovery, verification, and contradiction scans with CLI tools
- use `Ghidra` headless or scripted output as the main static-analysis engine
- treat `PCSX-Redux` CLI automation as the runtime conflict-breaker, not the
  default first step

`RE_CAMPAIGN_MEMORY.md` is the campaign-state authority for these passes:

- choose the target from `Priority Targets` or `Session Handoff`
- register every new export, coverage output, proof packet, or contradiction in
  the ledger before ending the pass
- keep conflict-state tracking in the ledger instead of scattering it across
  ad-hoc notes

## Principle

Prefer this evidence order for day-to-day work:

1. decoded script usage
2. binary-derived tables and function facts exported from `Ghidra`
3. local verification scripts
4. helper decomp comparison
5. automated `PCSX-Redux` CLI capture only if the first four still disagree

Helper comparison means lead generation and sanity checking, not final
authority. When a helper-repo clue matters, turn it into a local export,
instruction dump, xref artifact, or runtime capture before treating it as
evidence.

## Local Tracked Workspace

Use the tracked [`decomp`](decomp) folder for local decompilation support code.

Recommended responsibilities:

- [`decomp/ghidra`](decomp/ghidra): scripts and notes for headless or scripted
  `Ghidra` work
- [`decomp/verification`](decomp/verification): Python verification scripts
  that compare local notes, exported tables, and helper sources
- [`decomp/evidence`](decomp/evidence): structured proof packets and exported
  machine-readable facts

Keep the split intentional:

- [`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md): campaign state, priorities,
  conflict summaries, artifact links, and handoff memory
- [`decomp`](decomp): implementation helpers, exported evidence, and
  reconciliation outputs

Do not put large binary tool installs here. Keep those under ignored `tools/`.

## Default CLI Pipeline

### 0. Anchor the pass in the ledger

Before exporting anything, read [`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md)
and decide:

- which target or handoff step this pass is serving
- which pass from `Pass Plan` is active
- which artifact you are about to produce

If the planned work is not visible in the ledger, add or update the relevant
target before the pass drifts.

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

But the output artifact should still anchor itself in local reproducible data.
Do not let a contradiction note or proof packet rest mainly on helper C when a
local `Ghidra` export can be produced.

This is where we should catch:

- local names that no longer fit the binary mapping
- helper-decomp contradictions
- stub-table entries with nearby meaningful orphan handlers
- notes that overclaim current evidence

### 4. Escalate only if needed

If static evidence still conflicts after the reconciliation pass, then use the
scripted `PCSX-Redux` runtime path for:

- confirming the handler that actually executes
- checking whether a copied dispatch table is patched in RAM
- proving a disputed side effect
- deciding between two static candidates that both still look plausible

For the active `0x80` contradiction, the default runtime wrapper is:

- [`decomp/verification/run_opcode_0x80_runtime_capture.ps1`](decomp/verification/run_opcode_0x80_runtime_capture.ps1)

Use manual emulator interaction only if the scripted capture path cannot reach
the required state yet.

## When Runtime Is Not Needed

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

Register the finished export under `Artifacts Index -> Table exports` in
[`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md).

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

Register the finished export under `Artifacts Index -> Reconciliation reports`
or a coverage-oriented artifact entry in
[`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md).

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

Register the proof packet under `Artifacts Index -> Proof packets`, then update
the matching target row and any relevant conflict entry in
[`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md).

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
not collapse that into a fake clean answer. Preserve both in the proof packet
and summarize the contradiction in `RE_CAMPAIGN_MEMORY.md`.

If the nearby helper comes from `_refs/rood-reverse`, cite it as a competing
lead, then convert the important part into local binary-facing evidence before
promoting or downgrading a name.

## Escalation Rule

Escalate to automated `PCSX-Redux` CLI capture only after all of these are
true:

1. the loader/base-address mapping has been checked
2. the relevant binary table or code slice has been exported
3. local reconciliation still leaves a real contradiction
4. the contradiction matters to the final claim

## Practical Rule

If a disputed opcode cannot survive:

- script-pattern review
- `Ghidra` table export
- local reconciliation

then stop and use scripted `PCSX-Redux` capture to break the tie.

If it does survive those three, runtime can often wait.
