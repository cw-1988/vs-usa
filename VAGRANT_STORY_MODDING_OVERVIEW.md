# Vagrant Story USA Modding Overview

This file is a working reference for the extracted USA disc contents in this folder.

It combines:

- direct observations from the local disc files
- practical reverse-engineering notes
- a few community references that help confirm the file roles

## Disc Layout

The root of the extracted disc looks like this:

- `BATTLE/`
- `BG/`
- `EFFECT/`
- `ENDING/`
- `EVENT/`
- `GIM/`
- `MAP/`
- `MENU/`
- `MOV/`
- `MUSIC/`
- `OBJ/`
- `SE/`
- `SMALL/`
- `SOUND/`
- `TITLE/`
- `DBGFNT.TIM`
- `SLUS_010.40`
- `SYSTEM.CNF`

There are 5161 files total in this extraction.

## High-Level Modding Map

If the goal is to make new maps, characters, events, or story scenes, the most important locations are:

- `SLUS_010.40`
- `BATTLE/BATTLE.PRG`
- `MAP/*.MPD`
- `MAP/*.ZND`
- `MAP/*.ZUD`
- `OBJ/*.SHP`
- `OBJ/*.SEQ`
- `OBJ/*.WEP`
- `EVENT/*.EVT`

The game appears to be heavily slot-based rather than fully dynamic.

Important counts from the extracted files:

- `MAP`: 512 `MPD` files
- `MAP`: 256 `ZND` files
- `MAP`: 455 `ZUD` files
- `EVENT`: 512 `EVT` files
- `OBJ`: 202 `SHP` files
- `OBJ`: 700 `SEQ` files
- `OBJ`: 127 `WEP` files

That strongly suggests the engine expects many resources by fixed index.

## What Each Major Format Seems To Do

### `SLUS_010.40`

This is the root PS-X executable.

Local observation:

- file header begins with `PS-X EXE`
- it is the main boot executable

Community notes indicate it contains:

- persistent core code and libraries
- the zone LBA table for `ZND` files
- global tables needed to locate major content

Implication for modding:

- if files move or expand, this EXE may need table updates

### `BATTLE/BATTLE.PRG`

This appears to be the main gameplay engine overlay.

Community documentation identifies `BATTLE.PRG` as the main engine executable used during runtime.

Implication for modding:

- script opcode handlers live here
- behavior changes beyond data swaps may require reversing this PRG

### `MAP/*.MPD`

These are single-room map data files.

Local observation:

- headers look like section pointer tables
- files vary in size widely
- some tiny entries look like stubs or empty slots

Community documentation says `MPD` stores:

- room geometry
- collision
- door data
- enemies
- treasure
- script section

This is the confirmed core file for room-specific event scripting.

### `MAP/*.ZND`

These are zone-level files.

Local observation:

- `ZONE001.ZND` starts with a structured header and pointer-like values
- some later `ZONE` files are tiny, almost empty placeholders

Community documentation says `ZND` stores:

- references to `MPD` rooms
- references to `ZUD` unit bundles
- textures used by the rooms in that zone

Implication for modding:

- rooms are grouped into zones
- to place custom rooms or enemy packages, `ZND` is part of the routing layer

### `MAP/*.ZUD`

These are zone unit data bundles.

Local observation:

- `Z001U00.ZUD` contains the `H01` model signature seen in `OBJ/*.SHP`

Community documentation says `ZUD` packages:

- one character `SHP`
- optional weapon `WEP`
- optional shield `WEP`
- common `SEQ`
- battle `SEQ`

Implication for modding:

- this is a strong target for making or swapping enemy and NPC packages

### `OBJ/*.SHP`

These appear to be base character model files.

Local observation:

- `OBJ/00.SHP` begins with `H01`
- structure looks model-like rather than script-like

Implication for modding:

- custom characters will likely involve editing or replacing `SHP`

### `OBJ/*.SEQ`

These appear to be animation sequence files.

Implication for modding:

- custom motions or remapped action sets likely depend on `SEQ`

### `OBJ/*.WEP`

These are weapon or shield model files.

Implication for modding:

- used standalone and also inside `ZUD` bundles

### `EVENT/*.EVT`

These are event-related binary files.

Local observation:

- there are 512 of them
- all are exactly 6144 bytes
- they are not identical
- `EVENT/0100.EVT` appears to be completely blank
- headers and body bytes look opcode-like rather than plain text

Important caution:

- I did not confirm a strong public format page for `EVT`
- they are clearly important, but less well nailed down here than `MPD`

Working hypothesis:

- `EVT` is likely a fixed-size event or cutscene container, table, or helper script resource

## How Scripting Appears To Work

The best-confirmed room scripting path is inside the `ScriptSection` of each `MPD` file.

This is not plaintext scripting. It appears to be bytecode interpreted by the game engine.

Community documentation for `MPD` script layout says the script section contains:

- script length
- pointers to dialog text and other sub-blocks
- script opcodes
- encoded dialog text

That matches the local binary patterns much better than a text-based script format would.

## Confirmed Script Opcode Direction

Community reverse-engineering notes identify the `MPD` script opcode system and place its handler tables in the US version of `BATTLE.PRG`.

Documented useful opcodes include:

- `0x10` `DialogShow`
- `0x11` `DialogText`
- `0x12` `DialogHide`
- `0x20` `ModelLoad`
- `0x22` `ModelAnimate`
- `0x26` `ModelPosition`
- `0x28` `ModelMoveTo`
- `0x38` `ModelLookAt`
- `0x3A` `ModelLoadAnimations`
- `0x44` `SetEngineMode`
- `0x54` `BattleOver`
- `0x58` `SetHeadsUpDisplayMode`
- `0x68` `LoadRoom`
- `0x69` `LoadScene`
- `0x6D` `DisplayRoom`
- `0x90` `MusicLoad`
- `0x92` `MusicPlay`
- `0xA2` `CameraZoomIn`
- `0xC0` `CameraDirection`
- `0xC1` `CameraSetAngle`
- `0xC2` `CameraLookAt`
- `0xD0` `CameraPosition`
- `0xD1` `SetCameraPosition`
- `0xD4` `CameraHeight`
- `0xE0` `CameraWait`
- `0xEA` `CameraZoom`
- `0xEC` `CameraZoomScalar`
- `0xF0` `Wait`
- `0xFF` `return`

Practical takeaway:

- cutscenes are very likely authored by sequencing opcodes for models, camera, audio, room changes, and dialog
- story work means editing `MPD` script bytecode and text, not just swapping textures

## Text Encoding Notes

Some text in overlays is plain enough to spot directly.

Example:

- `MENU/MAINMENU.PRG` visibly contains English UI strings like damage types and menu labels

Other text resources use a custom encoding.

Examples:

- `MENU/ITEMNAME.BIN`
- `MENU/ITEMHELP.BIN`
- `SMALL/MON.BIN`

Community table notes indicate Vagrant Story uses a custom text table with terminators and control bytes rather than ASCII.

Practical takeaway:

- dialog and item text extraction will need a table-driven decoder

## What Looks Promising For Expansion

Several files look like obvious empty or stub slots.

Examples seen locally:

- `EVENT/0100.EVT` is all zeroes
- `MAP/MAP511.MPD` is a tiny stub-like map file
- `MAP/ZONE071.ZND` is only 68 bytes and mostly empty

Community US LBA listings also show multiple tiny `ZONE` entries later in the index range.

Practical takeaway:

- creating fully brand-new dynamic content is harder
- repurposing unused or stub slots is likely the most practical path

## Likely Content Relationships

The most useful mental model right now is:

1. `SLUS_010.40` points to `ZND` zones
2. each `ZND` points to one or more `MPD` room files and zero or more `ZUD` bundles
3. each `MPD` contains room geometry plus room-local script data
4. each `ZUD` packages a character model and its gear/animations
5. `BATTLE.PRG` provides the code that interprets script opcodes

That means:

- a story scene probably starts in an `MPD`
- that `MPD` script loads models, animations, camera actions, and dialog
- the models themselves may come through `ZUD` bundles or indexed object resources

## What Is Realistic To Attempt

### Most realistic first projects

- replace an existing room with custom geometry
- alter room scripts in an existing `MPD`
- swap enemy or NPC packages through `ZUD`
- change dialog text once the text table is decoded
- reuse an empty `EVT`, `MPD`, or `ZND` slot

### Harder but still plausible

- make a custom multi-room area by reassigning zone and room relationships
- import/export models and animations through community tooling
- rebuild disc images while preserving or updating LBA tables correctly

### Much harder

- expand beyond the engine's expected slot counts
- add truly new systems without reversing engine code
- freely move files around without patching all table references

## Suggested Modding Workflow

If starting from scratch, a practical path would be:

1. choose one existing room to study
2. identify its `ZND -> MPD -> ZUD` relationship
3. dump the `MPD` script section into readable opcodes
4. decode that room's dialog block with the Vagrant Story text table
5. confirm how the scene loads models, camera, and room transitions
6. repurpose one empty or low-value slot for experiments
7. only after that, handle disc rebuild and LBA correction

## Good Local Targets To Inspect Next

- `SLUS_010.40`
- `BATTLE/BATTLE.PRG`
- `MAP/MAP000.MPD`
- `MAP/MAP511.MPD`
- `MAP/ZONE001.ZND`
- `MAP/ZONE071.ZND`
- `MAP/Z001U00.ZUD`
- `OBJ/00.SHP`
- `EVENT/0000.EVT`
- `EVENT/0100.EVT`
- `MENU/ITEMNAME.BIN`
- `SMALL/MON.BIN`

## Tooling Notes

One promising public toolchain is the Blender addon here:

- https://github.com/korobetski/blender-vagrant-story

Its README says it supports or is working toward:

- `WEP` import/export
- `SHP` import
- `SEQ` import
- `ZUD` import
- `MPD` import

This is especially useful if the goal is map and character editing rather than pure hex work.

## External References

These were used to confirm format roles and engine behavior:

- Data Crystal file format hub: https://datacrystal.tcrf.net/wiki/Vagrant_Story/File_formats
- Data Crystal `MPD` format: https://datacrystal.tcrf.net/wiki/Vagrant_Story/MPD_files
- Data Crystal `ZND` format: https://datacrystal.tcrf.net/wiki/Vagrant_Story/ZND_files
- Data Crystal `ZUD` format: https://datacrystal.tcrf.net/wiki/Vagrant_Story/ZUD_files
- Data Crystal script opcodes: https://datacrystal.tcrf.net/wiki/Vagrant_Story/Script_Opcodes
- Data Crystal level data overview: https://datacrystal.tcrf.net/wiki/Vagrant_Story/Level_data
- Data Crystal executables notes: https://datacrystal.tcrf.net/wiki/Vagrant_Story/Executables
- Data Crystal US LBA list: https://datacrystal.tcrf.net/wiki/Vagrant_Story/SLUS_LBA_List
- Blender addon repo: https://github.com/korobetski/blender-vagrant-story

## Current Best Summary

If the main question is "where do I edit scripting for new story and scenes?", the best answer right now is:

- start with `MAP/*.MPD`
- focus on the `ScriptSection`
- decode its opcodes and text table
- treat `EVENT/*.EVT` as important but secondary until its format is better understood

If the main question is "where do I edit maps and characters?", then:

- rooms live in `MPD`
- zone grouping and textures live in `ZND`
- enemy/NPC packages live in `ZUD`
- base models and animations live in `OBJ` as `SHP`, `SEQ`, and `WEP`

## Best Next Step

The most useful next automation would be a small dumper that:

- parses an `MPD` header
- extracts the `ScriptSection`
- prints opcode bytes in readable form
- finds the dialog text pointer table
- decodes strings using the Vagrant Story text table

That would turn the current high-level map into something directly editable.
