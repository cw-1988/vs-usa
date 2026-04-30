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
comparing exported RAM snapshots against a binary-derived baseline and by
driving the current `PCSX-Redux` CLI capture path instead of relying on a
human-driven debugger session by default.

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
- `pcsx_redux_opcode_0x80_capture.lua`: startup Lua automation for the current
  `0x80` runtime tie-breaker; it plants breakpoints, dumps the runtime table
  from emulator memory, records save-state load events, can replay a scripted
  pad-input plan through the documented `PCSX.SIO0.slots[*].pads[*]`
  overrides, and writes a compact summary JSON
- `run_opcode_0x80_runtime_capture.ps1`: wrapper that launches `PCSX-Redux`
  with the capture Lua, then folds the resulting dumps and summary back into
  the checked-in observation packet via the existing recorder/finalizer; it
  can also auto-pick the newest nearby savestate and inflate gzip-compressed
  UI savestates into a temporary raw file that `PCSX.loadSaveState(file)` can
  consume, and it can prepare a checked-in JSON input plan into a Lua-friendly
  schedule when cold-boot menu automation is the only available fallback

Official `PCSX-Redux` references for this automation path:

- CLI flags: <https://pcsx-redux.consoledev.net/cli_flags/>
- Lua basics: <https://pcsx-redux.consoledev.net/Lua/redux-basics/>
- Lua breakpoints: <https://pcsx-redux.consoledev.net/Lua/breakpoints/>
- Lua events: <https://pcsx-redux.consoledev.net/Lua/events/>
- Lua memory/registers: <https://pcsx-redux.consoledev.net/Lua/memory-and-registers/>
- MIPS API: <https://pcsx-redux.consoledev.net/mips_api/>

Recommended runtime handoff flow:

- keep a checked-in observation scaffold under `decomp/evidence` so the next
  `PCSX-Redux` CLI pass starts from planned breakpoints, expected dump paths,
  and a missing-snapshot checklist instead of a blank JSON file
- prefer `run_opcode_0x80_runtime_capture.ps1` as the default runtime capture
  path for the current `0x80` contradiction so breakpoint setup, RAM dumps, and
  observation-packet updates happen through one scripted flow
- when a nearer launch point exists, prefer passing `-SaveStatePath` or
  `-UseNewestSaveState` to that wrapper instead of cold-booting from disc
  again; the wrapper now handles the gzip-compressed savestates that the
  `PCSX-Redux` UI writes, searches the portable save directory next to
  `pcsx-redux.exe`, and stages compressed UI savestates into a raw temporary
  file for Lua
- if no near-battle savestate exists yet, tune
  `decomp/evidence/opcode_0x80_runtime_input_plan.json` and rerun the wrapper
  with `-UseDefaultInputPlan` or `-InputPlanPath <json>` so the same scripted
  flow can press through the menu path instead of falling back to a purely
  manual debugger session
- the wrapper now auto-extends timeout when a checked-in input plan would
  otherwise outlast the base frame budget, so a failed cold-boot run now says
  more about the route or menu state than about a hidden timeout mismatch
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
- use manual `PCSX-Redux` UI interaction only as fallback when the scripted
  CLI capture path cannot reach the target launch point or when a one-off
  exploratory breakpoint session is faster than extending the automation

## What To Catch Early

Good verification scripts should flag:

- binary exports produced with the wrong import base or wrong overlay
- local names that no longer match binary-derived table entries
- dispatch-table stubs that have nearby orphan candidates with stronger-looking
  behavior
- notes that claim `Confirmed` without a binary or runtime anchor

If a script cannot settle the question, it should still narrow the runtime ask.
The goal is not to avoid `PCSX-Redux`; it is to arrive at a scripted runtime
capture with one clear contradiction instead of a vague hunch.
