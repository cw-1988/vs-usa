# Room Connection Findings

This note summarizes how room connectivity appears to work in Vagrant Story, including cross-zone transitions.

## Main Finding

There are at least two useful layers of room connectivity:

1. `MAP*.MPD` section `F`
   This is a local room cluster for the current playable area state.
   It is useful for detecting whether a room participates in a normal playable room set at all.
   It is not enough to recover the full world graph, because it misses many cross-zone transitions.

2. `SCEN*.ARM` scene data
   This is the layer that carries the broader world-map style connectivity, including links across zones.
   The scene payload contains per-room markers for ordinary doors and for "connecting maps".
   Those connecting-map markers are what bridge areas like Wine Cellar -> Catacombs.

The practical result is:

- Use `sectionF` plus `AreaName` to classify `RoomType=Cutscene` or `RoomType=Debug`
- Use `SCEN*.ARM` reachability to classify `RoomType=Playable`

## Why `sectionF` Alone Was Wrong

The first pass only used `MAP*.MPD` section `F`, which produced a small local graph around `MAP009`.
That was enough to connect rooms inside the starting Wine Cellar cluster, but it missed known cross-zone links.

Example:

- `MAP009` `Entrance to Darkness` is connected to `MAP028` `Hall of Sworn Revenge`
- a `sectionF`-only graph failed to show that
- the scene graph recovered from `SCEN*.ARM` does show it

So `sectionF` is real data, but it is not the full traversal graph.

## Where the Cross-Zone Link Lives

The MPD room section `B` contains a `sceneId`.

Relevant details:

- section index for MPD `sectionB`: `10`
- `sceneId` is read from `sectionB + 0x50`
- example values:
  - `MAP009` -> scene `1`
  - `MAP026` -> scene `1`
  - `MAP028` -> scene `2`
  - `MAP147` -> scene `28`
  - `MAP200` -> scene `26`
  - `MAP506` -> scene `0`

That `sceneId` is the bridge from a map to its `SCENxxx.ARM` file.

## `SCEN*.ARM` Layout Used By The Script

The current parser in [analyze_room_graph.py](/c:/Users/Chris/Desktop/vs usa/analyze_room_graph.py) uses this working model:

1. file header:
   - `u32 roomCount`

2. room table:
   - repeated `roomCount` times
   - struct format: `<IiHH>`
   - fields interpreted as:
     - unused/visited-like `int`
     - `room_len`
     - `zone_id`
     - `map_id`

3. concatenated room payloads:
   - each payload is read sequentially using `room_len`
   - the payload contains:
     - `vertex_count`
     - triangle count
     - quad count
     - line count group 1
     - line count group 2
     - marker count
     - marker entries

4. marker entries:
   - each marker is 4 bytes
   - interpreted as:
     - `vertex_index`
     - `target_scene_id`
     - `flags`
     - `door_id`

The important rule is:

- if `flags & 0x04` is set, that marker is a "connecting map" marker
- `target_scene_id` is then treated as a scene-level edge

This matches the menu code distinction between ordinary doors and "connecting maps".

## Example Cross-Zone Connections

Recovered examples from the scene files:

- `SCEN001` contains room `(zone=11, map=1)` with a connecting-map marker to scene `2`
  - this is the Wine Cellar side of the Catacombs transition
- `SCEN002` contains room `(zone=13, map=1)` with a connecting-map marker to scene `1`
  - this is the Catacombs side back to Wine Cellar

That is why:

- `MAP025` `The Hero's Winehall` is connected to the Catacombs scene
- `MAP026` `The Gallows` belongs to the same starting scene cluster
- `MAP028` `Hall of Sworn Revenge` is correctly reachable from `MAP009`

Other scene-level edges found in the current pass include:

- `1 <-> 2`
- `2 <-> 3`
- `3 <-> 28`
- `4 <-> 22`
- `4 <-> 28`
- `5 <-> 19`
- `5 <-> 29`
- `6 <-> 7`
- `6 <-> 19`
- `7 <-> 30`
- `8 <-> 9`
- `9 <-> 10`
- `9 <-> 30`
- `10 <-> 11`
- `11 <-> 12`
- `13 <-> 21`
- `14 <-> 19`
- `15 <-> 16`
- `15 <-> 21`
- `16 <-> 17`
- `17 <-> 21`
- `18 <-> 3`
- `18 <-> 22`
- `19 <-> 24`
- `19 <-> 26`
- `19 <-> 28`
- `19 <-> 30`
- `20 <-> 25`
- `20 <-> 30`
- `21 <-> 23`
- `21 <-> 29`
- `22 <-> 28`
- `23 <-> 26`
- `23 <-> 28`
- `23 <-> 29`
- `24 <-> 27`
- `24 <-> 29`
- `25 <-> 30`

## Special Case: Scene `0`

Scene `0` behaves like a special bucket, not a normal playable area graph node.

Important consequence:

- do not traverse `target_scene_id = 0` as a normal world edge

If scene `0` is treated as a real node, it incorrectly pulls in a large set of unrelated maps, including debug and oddball maps.

In the current script:

- scene ids are only traversed when `1 <= scene_id <= 31`
- this keeps `MAP506` isolated

## Current Classification Rules

### `RoomType=Cutscene`

A map is currently marked `RoomType=Cutscene` when:

- `sectionF` room count is `0`
- and `AreaName != Debug`

This works well for disconnected story/cutscene rooms such as:

- `MAP023`
- `MAP211`
- `MAP100` to `MAP104`
- `MAP131` to `MAP138`
- `MAP172`
- `MAP178`
- `MAP212` to `MAP214`
- `MAP413` to `MAP415`

### `RoomType=Playable`

A map is currently marked `RoomType=Playable` when:

- it is not `RoomType=Cutscene`
- it belongs to a scene reachable from `MAP009`'s scene
- reachability is computed through `SCEN*.ARM` connecting-map edges

### `RoomType=Debug`

A map is currently marked `RoomType=Debug` when:

- `AreaName = Debug`

## Current Results

With `MAP009` as the root:

- start map: `MAP009` `Entrance to Darkness`
- start scene: `1`
- reachable playable scenes: `31`
- reachable playable maps: `365`
- disconnected non-cutscene map: only `MAP506`

Important spot checks:

- `MAP025` -> connected
- `MAP026` -> connected
- `MAP028` -> connected
- `MAP023` -> cutscene-only, not connected
- `MAP211` -> cutscene-only, not connected
- `MAP506` -> not cutscene-only, but isolated and not connected

## Files To Look At

- [analyze_room_graph.py](/c:/Users/Chris/Desktop/vs usa/analyze_room_graph.py)
- [room_names.tsv](/c:/Users/Chris/Desktop/vs usa/room_names.tsv)
- [_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h](/c:/Users/Chris/Desktop/vs usa/_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h)
- [_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c](/c:/Users/Chris/Desktop/vs usa/_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c)
- [_refs/rood-reverse/src/MENU/MENU5.PRG/4D8.c](/c:/Users/Chris/Desktop/vs usa/_refs/rood-reverse/src/MENU/MENU5.PRG/4D8.c)
- `Game Data/MAP/MAP*.MPD`
- `Game Data/SMALL/SCEN*.ARM`

## Re-run

```powershell
python analyze_room_graph.py
python analyze_room_graph.py --update-tsv
```

## Short Version

If the question is "how are rooms connected even across zones?", the most useful answer so far is:

- MPD `sectionF` gives local playable room membership
- MPD `sectionB.sceneId` assigns each map to a scene
- `SCEN*.ARM` markers with `flags & 0x04` encode scene-to-scene "connecting map" edges
- those scene edges are the missing cross-zone graph
