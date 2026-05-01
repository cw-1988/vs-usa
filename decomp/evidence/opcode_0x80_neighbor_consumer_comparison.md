# Opcode `0x80` Neighbor Consumer Comparison

## Goal

Tighten the semantic cleanup around `0x80` by comparing the already-proven
neighboring sound families as prepared-state explanations for audio-looking
script scenes.

The question here is not whether `0x80` dispatches to the shared stub at
`0x800B66E4`; that structural point is already closed.
The question is which neighboring sound paths best explain the same scenes
without restoring a direct sound-effect meaning to `0x80`.

## Method

- Start from the checked-in `decoded_scripts` corpus and keep the legacy
  `SoundEffects0(...)` text only as a locator for historical `0x80` sites.
- For each file containing at least one legacy-rendered `0x80`, inspect only
  the opcodes before the first `0x80` in that file.
- Treat the three already-proven neighboring families as complete prepared
  states only when both members of the pair appear before the first `0x80`:
  - `0x85` plus `0x88`: `LoadSfxSlot` plus `SetCurrentSfx`
  - `0x90` plus `0x92`: `LoadMusicSlot` plus `MusicPlay`
  - `0x9D` plus `0x9E`: `LoadSoundFileById` plus `ProcessSoundQueue`
- When more than one complete pair exists before the first `0x80`, rank the
  local candidate by proximity:
  whichever pair has the latest opcode address before the first `0x80` gets
  treated as the closest prepared-state explanation for that opening burst.
- Keep representative mid-scene re-arms explicit when they change which
  neighboring family looks strongest later in the same scene.

The raw counts for this pass live in
[`opcode_0x80_neighbor_consumer_scan.json`](opcode_0x80_neighbor_consumer_scan.json).

## Corpus result

Across the `127` checked-in decoded-script files that still contain at least
one legacy-rendered `0x80` line:

- `85 / 127` already stage at least one complete neighboring sound pair before
  the first `0x80`
- `83 / 127` stage the `0x85/0x88` SFX-slot pair before the first `0x80`
- `44 / 127` stage the `0x9D/0x9E` sound-file queue pair before the first
  `0x80`
- `20 / 127` stage the `0x90/0x92` music-slot pair before the first `0x80`

The combination split before the first `0x80` is:

- `40` files: only the SFX-slot pair
- `24` files: the SFX-slot pair plus the sound-file queue pair
- `18` files: all three pairs
- `1` file: only the sound-file queue pair
- `1` file: the music-slot pair plus the sound-file queue pair
- `1` file: the music-slot pair plus the SFX-slot pair
- `42` files: no complete pair before the first `0x80`

When multiple complete pairs are present, the closest pair before the first
`0x80` breaks down as:

- `62` files: the `0x85/0x88` SFX-slot pair is closest
- `13` files: the `0x9D/0x9E` queue pair is closest
- `10` files: the `0x90/0x92` music-slot pair is closest

## Representative scenes

### `MAP001` intro: SFX-slot setup is the closest prepared state

[`decoded_scripts/24-Unmapped/001-Unknown Room.txt`](../../decoded_scripts/24-Unmapped/001-Unknown%20Room.txt)
stages:

- `0010: 92 03 7F 00` -> `MusicPlay(...)`
- `00A2: 85 02 01` -> `LoadSfxSlot(2, 1)`
- `00A7: 88 01` -> `SetCurrentSfx(1)`

The first legacy-rendered `0x80` burst does not arrive until:

- `0155: 80 03 37 80 7F`

That puts the last music-pair opcode `0x145` bytes earlier than the first
`0x80`, but the last SFX-pair opcode only `0xAE` bytes earlier.
For this checked intro route, the SFX-slot pair is the stronger local
prepared-state explanation than the earlier music bring-up.

### `MAP026` Gallows: first burst favors SFX, later bursts get a queue re-arm

[`decoded_scripts/1-Wine Cellar/026-The Gallows.txt`](../../decoded_scripts/1-Wine%20Cellar/026-The%20Gallows.txt)
stages all three neighboring families before the first `0x80`:

- `0056: 9D 20` -> `LoadSoundFileById(32)`
- `0058: 9E` -> `ProcessSoundQueue()`
- `0059: 90 20 01` -> `LoadMusicSlot(32, 1)`
- `0062: 92 01 7F 00` -> `MusicPlay(...)`
- `008C: 85 10 01` -> `LoadSfxSlot(16, 1)`
- `0091: 88 01` -> `SetCurrentSfx(1)`

The first legacy-rendered `0x80` does not appear until:

- `00EB: 80 03 07 80 7F`

So the first burst sits closest to the SFX-slot pair:

- `0x0091 -> 0x00EB`: `0x5A`
- `0x0062 -> 0x00EB`: `0x89`
- `0x0058 -> 0x00EB`: `0x93`

But the scene later re-arms the queue path:

- `028A: 9D 20`
- `028E: 9E`
- `02D5: 80 03 0A 80 7F`

That later `0x028E -> 0x02D5` gap is only `0x47`, so the same file gives a
mixed consumer story: the opening burst aligns best with SFX-slot setup, while
later bursts can be explained by a fresher queue-based bring-up.

### `MAP415` The Dark tempts Ashley: no SFX pair, queue plus music carry the scene

[`decoded_scripts/23-Great Cathedral/415-The Dark tempts Ashley.txt`](../../decoded_scripts/23-Great%20Cathedral/415-The%20Dark%20tempts%20Ashley.txt)
has no `0x85/0x88` SFX pair before the sampled `0x80` bursts.
Instead it stages:

- `0019: 9D AF` -> `LoadSoundFileById(175)`
- `001B: 9E` -> `ProcessSoundQueue()`
- `001C: 90 AF 01` -> `LoadMusicSlot(175, 1)`
- `0021: 92 01 7F 00` -> `MusicPlay(...)`

The first legacy-rendered `0x80` then appears at:

- `00A7: 80 03 01 80 7F`

That leaves the two remaining candidates close together:

- `0x0021 -> 0x00A7`: `0x86`
- `0x001B -> 0x00A7`: `0x8C`

This scene therefore does not need `0x80` to be the direct sound trigger.
The better local reading is that the queue and music-slot paths already stage
the audio context up front, then `0x80` rides along with later camera and
screen-effect beats.

The same file later refreshes the music-slot side again:

- `04A1: 90 B0 02`
- `0533: 80 03 02 80 7F`

So this representative route keeps the music-family explanation alive even
after the opening queue bring-up.

## Safe takeaway

- The new first-burst comparison makes the semantic cleanup sharper than the
  earlier "same file" co-hosting scan.
- The default local explanation for audio-looking `0x80` scenes is now the
  already-proven neighboring families, not a hidden direct `0x80` sound role.
- The `0x85/0x88` SFX-slot path is the most common and closest complete
  prepared state before the first `0x80`.
- The `0x9D/0x9E` queue path matters too, especially in scenes like `MAP026`
  where later re-arms sit immediately before later `0x80` bursts.
- The `0x90/0x92` music path usually looks more like backdrop or sustained
  scene bring-up than the default first-burst consumer, but `MAP415` shows it
  can still be the closest surviving prepared state when no SFX pair is
  present.
- `Opcode80SharedStub` remains the safest name because the audio-looking
  moments are now better explained as scene-specific neighboring consumers.

## Remaining gap

This pass does not prove that every `0x80` scene is solved.
The main residual set is the `42` files where no complete neighboring pair
appears before the first `0x80`.

The next semantic pass should therefore focus on:

- whether those residual files rely on carried state from earlier script blocks
  or cross-script setup that the current single-file scan does not see
- how the `0x90/0x92` music-slot path and the `0x9D/0x9E` queue path divide
  responsibility in the non-SFX scenes

Until that residual set is explained, `0x80` should stay on the structural
label `Opcode80SharedStub`.
