# Vagrant Story USA Decompilation Strategy

This note defines the local decompilation standard for this workspace.

For the campaign-state ledger and CLI-first implementation layer, also read
[`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md) and
[`CLI_DECOMPILATION_WORKFLOW.md`](CLI_DECOMPILATION_WORKFLOW.md).

The short version:

- `RE_CAMPAIGN_MEMORY.md` is the local campaign authority for in-progress state
- our decomp and evidence notes should be the authority for local conclusions
- the original binary plus runtime behavior are the ground truth
- [`_refs/rood-reverse`](_refs/rood-reverse) is a valuable helper decomp, not
  an authority by itself
- readable decompiled C is useful, but it is not enough unless it survives
  binary-level and runtime checks where confidence matters

## Core Principles

### 1. Binary first

The original game binaries are the ground truth.

Everything else is an interpretation layer:

- Ghidra function boundaries
- decompiler output
- local helper names
- `rood-reverse` source
- old notes and opcode tables

If those layers disagree, prefer the binary and runtime evidence over any
existing C source or notes.

### 2. Our decomp is the local authority

This workspace should gradually build its own standards-driven decompilation
record instead of inheriting authority from upstream helper repos.

That means:

- [`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md) tracks the current phase,
  priorities, unresolved conflicts, and handoff state for the next pass
- local notes should separate proven facts from borrowed ideas
- local opcode names should only become authoritative after independent
  verification
- local workflow docs should describe how to prove claims, not just how to
  browse previous work quickly

### 3. `rood-reverse` is a helper, not a final source

Use [`_refs/rood-reverse`](_refs/rood-reverse) for:

- candidate handler locations
- useful subsystem names
- rough function boundaries
- likely struct layouts
- dispatch-table leads
- prior naming work worth checking

Do not treat it as final proof by itself for:

- exact opcode-to-handler mapping
- final function boundaries
- definitive names
- claims that a handler is inert, complete, or matched enough to settle a
  dispute

### 4. Runtime beats plausible static theory

When a claim is important and static evidence conflicts, use `PCSX-Redux` to
observe what actually runs.

Typical examples:

- which function address an opcode really dispatches to
- whether a copied dispatch table is later patched in RAM
- whether an opcode reads a field the decompiled source seems to ignore
- whether two nearby helper candidates are both active or one is dead code

## Evidence Ladder

Use this rough priority order when deciding what to trust:

1. runtime trace in `PCSX-Redux`
2. raw table bytes or disassembly in `Ghidra`
3. verified function boundaries and xrefs in `Ghidra`
4. matched local or helper decompiled source that agrees with the binary
5. script-pattern clustering and decoded usage examples
6. historical notes, inherited names, or subsystem guesses

Lower evidence can suggest a theory. Higher evidence is needed to settle it.

## Required Checks For Disputed Opcode Work

Before promoting, downgrading, or rewriting an opcode meaning, check all of:

1. real script usage in [`decoded_scripts`](decoded_scripts)
2. the relevant dispatch table in source and, when important, in the binary
3. the current handler body
4. nearby orphan or unmatched helper candidates with similar argument shape
5. consumer paths or side effects
6. whether runtime agrees with the current static theory

If those checks disagree, the result is not `Confirmed`.
Document the contradiction instead.

## Function Status Model

When working on local decompilation, each function should be treated as one of:

- `matched`
- `nonmatching but identified`
- `orphan candidate`
- `unknown gap`

The most dangerous category for opcode work is `orphan candidate`:

- a function-shaped block exists
- it looks semantically meaningful
- but it is missing from headers, symbol maps, or dispatch notes

That is exactly the kind of mismatch that can make a table look settled when it
is not.

## What Counts As Rock-Solid Ground Truth

For a high-confidence opcode or helper conclusion, aim to collect a small proof
packet containing:

1. the opcode byte
2. the dispatch table address or table entry source
3. the resolved handler address
4. the function-boundary evidence
5. one or more real script examples
6. the main consumer or side-effect path
7. optional runtime trace if the area is disputed

If a claim cannot survive this packet, keep it tentative, and record the
conflict summary plus artifact links in
[`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md) instead of leaving the state
implicit.

## Ghidra Role

Use `Ghidra` for:

- raw dispatch tables
- function boundaries
- xrefs
- data layout
- gaps between named functions
- consumer tracing when decompiled source is incomplete

Do not treat decompiler output alone as ground truth.

When a helper decomp and `Ghidra` disagree, go back to:

- disassembly
- function starts and ends
- pointer tables
- literal data references

Practical caution:

- A correct-looking decompiler view can still be anchored to the wrong import
  base if the raw overlay was loaded incorrectly.
- For raw PS1 overlays, treat the `splat.yaml` base address as part of the
  ground-truth setup, not as an optional convenience.
- If the address setup is wrong, every downstream table check can look precise
  while still being false.

## PCSX-Redux Role

Use `PCSX-Redux` for:

- opcode dispatch breakpoints
- handler-address confirmation
- RAM watchpoints on copied function tables
- validation of side effects
- confirmation that a disputed static interpretation really occurs in play

If static and runtime disagree, the static model is incomplete.

## Completeness Audits We Should Eventually Maintain

The local decomp becomes more trustworthy when we can regularly audit:

- source functions missing from symbol maps
- symbol-map entries missing from source
- suspicious gaps between adjacent function addresses
- dispatch tables that reference stubs while nearby orphan candidates look
  meaningful
- claims marked `Confirmed` without a binary or runtime anchor

These audits can be manual at first and automated later.

The tracked home for that automation work is [`decomp`](decomp).

## Known Failure Modes To Guard Against

The most important recurring ways to fool ourselves are:

- raw-binary import drift: the overlay is loaded at the wrong base address, so
  table reads and function checks are offset while still looking consistent
- helper-decomp overtrust: a readable helper function gets treated as authority
  before binary mapping confirms it
- stub overpromotion: a dispatch-table hit to a real stub gets treated as the
  whole story before nearby orphan candidates are checked
- reconciliation gaps: a contradiction is noticed, but no proof packet is
  written, so the same uncertainty has to be rediscovered later

The fix for all four is the same: preserve the binary setup, export the facts,
record the conflict, and only then escalate to runtime if the conflict still
matters.

## Practical Working Model

Use this repo structure mentally:

- [`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md): campaign authority for
  in-progress state, target selection, and handoff memory
- local scripts and notes: current research workspace
- local decomp/evidence docs: emerging authority
- `Ghidra` project: binary truth and structure recovery
- `PCSX-Redux`: runtime truth
- [`_refs/rood-reverse`](_refs/rood-reverse): helper reference corpus

That lets us move fast without confusing borrowed confidence for proven local
truth.

## Default Rule

If a conclusion depends on trusting helper decompiled C more than the binary or
runtime, it is not ready to be treated as final local ground truth.
