# Vagrant Story USA Script RE Workspace

This project is a working reverse-engineering workspace for the USA release of **Vagrant Story**.

The current focus is the game's room and event scripting, especially the `MAP*.MPD` script sections. The goal is not just to rename files or tweak values, but to gradually identify the still-missing script opcodes and understand how they drive room logic, cutscenes, camera behavior, sound, loading, and transitions.

Long term, that should make it possible to build more ambitious custom content than simple numeric stat edits, including new event behavior and more meaningful map or scenario changes.

## What the project does

Right now the repo mainly provides:

- a batch script disassembler for `MAP*.MPD` files
- decoded text output grouped by area and room name
- room-name lookup support through `room_names.tsv`
- supporting research notes for opcode naming and room connectivity
- a second analysis script for scene and room graph work
- a documented `_refs` workspace for outside reverse-engineering repos

The main script is [`dump_mpd_script.py`](/c:/Users/Chris/Desktop/vs%20usa/dump_mpd_script.py). It reads the script section from each `MAP*.MPD`, decodes known opcodes into readable names where possible, preserves unknown ones, and writes text files into [`decoded_scripts`](/c:/Users/Chris/Desktop/vs%20usa/decoded_scripts).

That output is useful for:

- spotting repeated opcode patterns
- comparing similar rooms and cutscenes
- testing tentative opcode meanings
- identifying room transitions and script-controlled behavior

## Repository layout

- [`dump_mpd_script.py`](/c:/Users/Chris/Desktop/vs%20usa/dump_mpd_script.py): batch-disassembles `MAP*.MPD` script sections
- [`analyze_room_graph.py`](/c:/Users/Chris/Desktop/vs%20usa/analyze_room_graph.py): analyzes room and scene connectivity
- [`room_names.tsv`](/c:/Users/Chris/Desktop/vs%20usa/room_names.tsv): map, zone, area, and room name lookup table
- [`decoded_scripts`](/c:/Users/Chris/Desktop/vs%20usa/decoded_scripts): generated decoded script output
- [`ROOD_REVERSE_OPCODE_FINDINGS_2026-04-29.md`](/c:/Users/Chris/Desktop/vs%20usa/ROOD_REVERSE_OPCODE_FINDINGS_2026-04-29.md): opcode findings and naming notes
- [`ROOM_CONNECTION_FINDINGS_2026-04-29.md`](/c:/Users/Chris/Desktop/vs%20usa/ROOM_CONNECTION_FINDINGS_2026-04-29.md): room and scene connectivity notes
- [`VAGRANT_STORY_MODDING_OVERVIEW.md`](/c:/Users/Chris/Desktop/vs%20usa/VAGRANT_STORY_MODDING_OVERVIEW.md): higher-level notes on the extracted disc contents
- [`Game Data`](/c:/Users/Chris/Desktop/vs%20usa/Game%20Data): place the extracted USA disc contents here
- [`_refs/README.md`](/c:/Users/Chris/Desktop/vs%20usa/_refs/README.md): notes for external reference repos used alongside this workspace

## Tools and references

This workspace is not operating in isolation. Alongside the local Python scripts, it benefits from a few outside tools and reference projects.

### Local scripts in this repo

- [`dump_mpd_script.py`](/c:/Users/Chris/Desktop/vs%20usa/dump_mpd_script.py) for batch script extraction and readable opcode output
- [`analyze_room_graph.py`](/c:/Users/Chris/Desktop/vs%20usa/analyze_room_graph.py) for scene and room connectivity analysis

### External reference repos

- [`_refs/rood-reverse`](</c:/Users/Chris/Desktop/vs usa/_refs/rood-reverse>): local clone of the upstream `rood-reverse` Vagrant Story decompilation project when present
- upstream `rood-reverse`: <https://github.com/ser-pounce/rood-reverse>

`rood-reverse` is especially useful because it gives us a code-level view of the game engine, which helps turn guessed opcode names into verified behavior.

### Recommended companion tools

- `Ghidra`: best fit for understanding what opcode handlers actually do, because it combines disassembly, graphing, scripting, and decompilation
- `ghidra_psx_ldr`: helpful Ghidra extension for PS1 executables and PSYQ-flavored analysis workflows
- `Capstone`: still useful for lightweight scripted instruction decoding, bulk scans, and automation, but not ideal as the main environment for semantic reverse-engineering

### Useful decomp/modding pipeline tools

- `splat`: helpful if the work grows from script study into broader binary splitting and decomp project structure
- `m2c`: useful when you want a MIPS-focused decompiler pass on assembly outside a full interactive RE session
- `objdiff`: useful once we begin matching or rebuilding compiled objects
- `mkpsxiso`: useful later when the project reaches the point of rebuilding patched PlayStation disc images

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
