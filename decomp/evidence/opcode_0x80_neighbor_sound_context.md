# Opcode `0x80` Neighboring Sound Context

## Goal

Retire the historical `SoundEffects0` reading for positive script-context
reasons, not only because the verified runtime-table dispatch lands on the
shared return-zero stub at `0x800B66E4`.

## Scope note

The checked-in `decoded_scripts` corpus still prints legacy `SoundEffects0(...)`
text for `0x80` because many of those exports predate the local decoder rename
to `Opcode80SharedStub`.
This packet treats those rendered lines as historical script locations, not as
fresh naming proof.

## Corpus scan

A direct scan of the `decoded_scripts` corpus finds `127` files containing at
least one `0x80` line.
Among those same files:

- `88 / 127` co-host at least one explicit nearby sound-family opcode from
  `0x85`, `0x88`, `0x90`, `0x92`, `0x9D`, or `0x9E`
- `85 / 127` contain both the `0x85` `LoadSfxSlot` and `0x88` `SetCurrentSfx`
  pair
- `65 / 127` contain `0x90` or `0x92`
- `51 / 127` contain the `0x9D` `LoadSoundFileById` plus `0x9E`
  `ProcessSoundQueue` pair
- `49 / 127` contain all three categories together:
  `0x85/0x88`, `0x90/0x92`, and `0x9D/0x9E`

That is not direct consumer proof, but it does make the old "the sound must
come from `0x80` itself" reading less necessary.
Many audio-looking `0x80` scenes already live inside scripts that explicitly
prepare SFX slots, music slots, or sound-file queues through other opcodes.

## Representative scenes

### `MAP001` intro: explicit SFX setup before the first `0x80` burst

[`decoded_scripts/24-Unmapped/001-Unknown Room.txt`](../../decoded_scripts/24-Unmapped/001-Unknown%20Room.txt)
opens with `0x92` music playback at `0010`.
That same script then enters a nested helper block that performs:

- `00A2: 85 02 01` -> `LoadSfxSlot(2, 1)`
- `00A7: 88 01` -> `SetCurrentSfx(1)`

Only after that prepared-state setup does the intro reach its first `0x80`
cluster:

- `0155: 80 03 37 80 7F`
- `0170: 80 03 39 80 7F`
- `0177: 80 03 3A 80 7F`

The same room later repeats more `0x80` bursts around camera, model, and
cutscene timing beats, but the explicit SFX-selection work already happened
earlier in the same script.

### `MAP026` Gallows: queue, music-slot, and SFX-slot setup all exist without
needing `0x80` as the direct sound trigger

[`decoded_scripts/1-Wine Cellar/026-The Gallows.txt`](../../decoded_scripts/1-Wine%20Cellar/026-The%20Gallows.txt)
shows the strongest local script-side replacement story.

Early in the script it performs a complete sound-file and music bring-up:

- `0056: 9D 20` -> `LoadSoundFileById(32)`
- `0058: 9E` -> `ProcessSoundQueue()`
- `0059: 90 20 01` -> `LoadMusicSlot(32, 1)`
- `0062: 92 01 7F 00` -> `MusicPlay(...)`

The same file later does explicit SFX-slot preparation:

- `008C: 85 10 01` -> `LoadSfxSlot(16, 1)`
- `0091: 88 01` -> `SetCurrentSfx(1)`

Only after those steps do the script's repeated legacy-rendered `0x80` beats
start appearing:

- `00EB: 80 03 07 80 7F`
- `0106: 80 01 16 80 7F`
- `010B: 80 01 17 80 7F`
- `0153: 80 03 08 80 7F`
- `01C0: 80 03 08 80 7F`
- `0227: 80 03 09 80 7F`

The file then re-arms the direct file-queue path again at `028A-028E` through
another `9D` plus `9E` pair before later `0x80` beats at `02D5`, `036D`, and
`043B`.
That script no longer needs a direct `0x80` sound meaning to explain why the
scene sounds active.

### `MAP415` The Dark tempts Ashley: explicit queue-plus-music setup happens
up front, then `0x80` rides inside camera/effect beats

[`decoded_scripts/23-Great Cathedral/415-The Dark tempts Ashley.txt`](../../decoded_scripts/23-Great%20Cathedral/415-The%20Dark%20tempts%20Ashley.txt)
starts with a tight audio setup cluster:

- `0019: 9D AF` -> `LoadSoundFileById(175)`
- `001B: 9E` -> `ProcessSoundQueue()`
- `001C: 90 AF 01` -> `LoadMusicSlot(175, 1)`
- `0021: 92 01 7F 00` -> `MusicPlay(...)`

The first legacy-rendered `0x80` beat does not appear until `00A7`.
Later repeats at `017F`, `0221`, `02B3`, `0343`, `03D3`, `0483`, `0533`,
`05FB`, and `062B` all sit inside camera-roll, room-display, model-load, or
screen-effect staging rather than inside a fresh handler-level sound proof
path for `0x80`.

This same file also performs another explicit music-slot write at
`04A1: 90 B0 02` before more later `0x80` beats.
Again, the audio-looking scene already has stronger neighboring sound-family
opcodes available than the shared stub itself.

## Safe takeaway

- The best local explanation for many audio-looking `0x80` scenes is now
  contextual: scripts often co-host explicit SFX-slot, music-slot, or
  sound-file-queue setup opcodes that can prepare audible state before later
  `0x80` beats.
- That does not prove which one of those neighboring families is the final
  consumer for each scene.
- It does mean the old direct label `SoundEffects0` is no longer the least-bad
  explanation for representative script usage.
- `Opcode80SharedStub` remains the safest local name because the verified
  runtime-table dispatch is still structural, not semantic.

## Remaining gap

This packet narrows the semantic problem from "why do sound scenes use a stub?"
to "which already-proven neighboring sound path best explains each prepared
scene?"
The next proof step should trace the consumer relationship between:

- `0x9D` plus `0x9E` sound-file queueing
- `0x90` plus `0x92` music-slot playback
- `0x85` plus `0x88` SFX-slot selection

Until that tie-breaker is closed, `0x80` should stay on the structural label
`Opcode80SharedStub`.
