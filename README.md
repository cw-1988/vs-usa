# Vagrant Story USA Script RE Workspace

This project is a working reverse-engineering workspace for the USA release of **Vagrant Story**.

The current focus is the game's room and event scripting, especially the `MAP*.MPD` script sections. The goal is not just to rename files or tweak values, but to gradually identify the still-missing script opcodes and understand how they drive room logic, cutscenes, camera behavior, sound, loading, and transitions.

Long term, that should make it possible to build more ambitious custom content than simple numeric stat edits, including new event behavior and more meaningful map or scenario changes.

For substantial opcode or decomp work, start with
[`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md). It is the cross-session
campaign ledger and handoff entrypoint, and it should be read before
[`DECOMPILATION_STRATEGY.md`](DECOMPILATION_STRATEGY.md) and
[`CLI_DECOMPILATION_WORKFLOW.md`](CLI_DECOMPILATION_WORKFLOW.md) when choosing
the next opcode/decomp pass.

## What the project does

Right now the repo mainly provides:

- a batch script disassembler for `MAP*.MPD` files
- decoded text output grouped by area and room name
- room-name lookup support through `room_names.tsv`
- supporting research notes for opcode naming and room connectivity
- a second analysis script for scene and room graph work
- a documented `_refs` workspace for outside reverse-engineering repos

The main script is [`dump_mpd_script.py`](dump_mpd_script.py). It reads the script section from each `MAP*.MPD`, decodes known opcodes into readable names where possible, preserves unknown ones, and writes text files into [`decoded_scripts`](decoded_scripts).

That output is useful for:

- spotting repeated opcode patterns
- comparing similar rooms and cutscenes
- testing tentative opcode meanings
- identifying room transitions and script-controlled behavior

## Repository layout

- [`dump_mpd_script.py`](dump_mpd_script.py): batch-disassembles `MAP*.MPD` script sections
- [`analyze_room_graph.py`](analyze_room_graph.py): analyzes room and scene connectivity
- [`room_names.tsv`](room_names.tsv): map, zone, area, and room name lookup table
- [`decoded_scripts`](decoded_scripts): generated decoded script output
- [`RE_CAMPAIGN_MEMORY.md`](RE_CAMPAIGN_MEMORY.md): cross-session campaign
  memory and handoff ledger for opcode/decomp work
- [`ROOD_REVERSE_OPCODE_CONCLUSIONS.md`](ROOD_REVERSE_OPCODE_CONCLUSIONS.md): opcode conclusions and naming notes
- [`DECOMPILATION_STRATEGY.md`](DECOMPILATION_STRATEGY.md): local standards for
  binary-first decompilation and helper-decomp verification
- [`CLI_DECOMPILATION_WORKFLOW.md`](CLI_DECOMPILATION_WORKFLOW.md): CLI-first
  decomp workflow and when runtime should break ties
- [`ROOM_CONNECTION_FINDINGS.md`](ROOM_CONNECTION_FINDINGS.md): room and scene connectivity notes
- [`VAGRANT_STORY_MODDING_OVERVIEW.md`](VAGRANT_STORY_MODDING_OVERVIEW.md): higher-level notes on the extracted disc contents
- [`decomp`](decomp): tracked local decomp scripts, verification helpers, and
  machine-readable evidence
- [`Game Data`](Game%20Data): place the extracted USA disc contents here
- [`tools`](tools): local reverse-engineering tools and debugger builds kept outside version control
- [`_refs/README.md`](_refs/README.md): notes for external reference repos used alongside this workspace

## Tools and references

This workspace uses three layers of tooling: repo-local analysis scripts, local reverse-engineering tools under `tools/`, and optional reference repos under `_refs/`.

### In-repo scripts

- [`dump_mpd_script.py`](dump_mpd_script.py): batch script extraction and readable opcode output
- [`analyze_room_graph.py`](analyze_room_graph.py): scene and room connectivity analysis

### Local reverse-engineering toolchain

- [`tools/ghidra_12.0.4_PUBLIC`](tools/ghidra_12.0.4_PUBLIC): main static analysis environment, launched with [`ghidraRun.bat`](tools/ghidra_12.0.4_PUBLIC/ghidraRun.bat)
- `ghidra_psx_ldr`: installed into the local Ghidra setup to improve PlayStation-specific analysis
- [`tools/pcsx-redux`](tools/pcsx-redux): runtime debugger and scriptable
  capture build, launched with [`pcsx-redux.exe`](tools/pcsx-redux/pcsx-redux.exe)

In practice, `Ghidra` is where opcode handlers and control flow are studied,
while `PCSX-Redux` is used through scripted CLI capture to verify live
behavior and settle runtime contradictions. The `tools/` folder stays
Git-ignored because it holds large local binaries, extracted archives, and
working tool checkouts.

### Reference repos

- [`_refs/rood-reverse`](_refs/rood-reverse): optional local clone of the upstream Vagrant Story decompilation project
- upstream `rood-reverse`: <https://github.com/ser-pounce/rood-reverse>

`rood-reverse` is especially useful for matching guessed opcode behavior to
engine code and checking naming, function boundaries, and subsystem behavior.
It should still be treated as a helper reference repo rather than final local
ground truth; see [`DECOMPILATION_STRATEGY.md`](DECOMPILATION_STRATEGY.md).
When a helper clue matters to a pass result, convert it into a local
`decomp/` artifact before citing it as evidence.

### Optional companion tools

- `Capstone`: useful for lightweight scripted instruction decoding, bulk scans, and automation
- `splat`: useful if the work expands into broader binary splitting and decomp project structure
- `m2c`: useful for MIPS-focused decompiler passes outside a full interactive RE session
- `objdiff`: useful once matching or rebuilding compiled objects becomes important
- `mkpsxiso`: useful later if the project reaches patched PlayStation disc rebuilds

## How to use

### 1. Put the game data in place

Extract the **Vagrant Story USA** disc contents and place them under:

```text
Game Data/
```

At minimum, the current scripts expect folders like:

```text
Game Data/MAP
Game Data/SMALL
```

The `MAP` folder is needed for `MAP*.MPD`, and `SMALL` is used by the room graph analysis for `SCEN*.ARM`.

### 2. Decode all map scripts

Run:

```powershell
python dump_mpd_script.py "Game Data/MAP"
```

By default this writes decoded files to:

```text
decoded_scripts/
```

You can choose a different output folder with:

```powershell
python dump_mpd_script.py "Game Data/MAP" -o "decoded_scripts"
```

### 3. Review the decoded output

Each decoded file includes:

- the source `MAPxxx.MPD`
- area and room metadata when available
- the script header
- decoded opcode lines
- extracted dialog text

Known opcodes are rendered with better names where the current reverse-engineering work is confident. Unknown or still-uncertain opcodes are intentionally kept visible so they can be studied instead of hidden.

### 4. Analyze room connectivity

Run:

```powershell
python analyze_room_graph.py
```

This uses:

- `Game Data/MAP` for MPD files
- `Game Data/SMALL` for scene files
- `decoded_scripts` for decoded room metadata
- `room_names.tsv` for labels

To also write room classification back into the TSV:

```powershell
python analyze_room_graph.py --update-tsv
```

## Reverse-engineering goal

The main research goal is to keep shrinking the set of unknown or weakly named opcodes.

That matters because once opcode behavior is understood well enough, the project can move beyond:

- changing existing numbers
- swapping assets in fixed slots
- making only shallow data edits

and toward:

- understanding how room events are actually authored
- modifying cutscene and interaction flow more safely
- enabling more custom behavior in maps and scenarios
- eventually supporting richer custom content creation

## Current limitations

- This is a research workspace, not a polished modding toolkit yet.
- Some opcode names are still placeholders.
- A few opcode sizes are still marked as unsafe or unresolved.
- The scripts currently decode and analyze data, but they do not rebuild game files back into a patched disc image.

## Notes

- The scripts are written for Python 3.
- The repo is currently centered on the USA game data layout.
- If a decoded file only shows partial meaning for an opcode, that is expected; preserving uncertain data is part of the workflow.
- The current local toolchain is centered around Ghidra for static analysis and
  automated `PCSX-Redux` CLI capture for runtime verification.
