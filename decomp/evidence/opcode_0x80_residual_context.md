# Opcode `0x80` Residual Context Scan

## Goal

Tighten the remaining semantic cleanup around `0x80` after the first-burst
neighboring-consumer comparison.

The earlier pass explained the majority case: `85` of the `127`
legacy-rendered `0x80` files already stage a complete neighboring sound pair
before the first `0x80`.
This pass focuses only on the residual `42` files that do not.

## Method

- Scan the checked-in `decoded_scripts` corpus for each file whose first
  opcode `0x80` appears before any complete in-file `0x85/0x88`,
  `0x90/0x92`, or `0x9D/0x9E` pair.
- Record whether any sound-family opcodes appear before that first `0x80`,
  whether any complete pair appears later in the same file, and whether the
  residual files cluster around repeated `0x80` byte patterns or surrounding
  opcode bundles.
- Cross-check same-title room variants within the same area so obvious
  alternate-state scripts do not get mistaken for fresh direct-sound evidence.

The raw packet for this pass lives in
[`opcode_0x80_residual_scan.json`](opcode_0x80_residual_scan.json), generated
by
[`../verification/analyze_opcode_0x80_residuals.py`](../verification/analyze_opcode_0x80_residuals.py).

## Corpus result

Across the `42` residual files:

- `42 / 42` contain no sound-family opcode at all before the first `0x80`
- `38 / 42` contain no `0x85-0x9E` sound-family opcode anywhere in the file
- only `2 / 42` later grow a complete pair in the same file:
  `MAP290` later stages all three neighboring families, and `MAP334` later
  stages the SFX and queue pairs

That immediately changes the burden of proof.
Most of the residual set is no longer "audio-looking but missing the pair";
it is "no local sound-family evidence exists in the file at all."

## Dominant residual clusters

### `36 / 42`: repeated `0x41/0x42` opener bundle

The dominant residual pattern is the duplicated pair:

- `80 01 41 80 7F`
- immediately followed by `80 01 42 80 7F`

This exact two-line burst appears in `36` of the `42` residual files.

Its surrounding context also clusters heavily:

- `28` files use the same three-opcode lead-in:
  `DialogHide(0)` -> `Opcode14(0)` -> `SetHeadsUpDisplayMode(1)`
- `21` files then continue with the same immediate follow-up:
  second `0x80` -> `Opcode45(...)` -> `ModelControlViaScript(...)`

Representative files:

- [`../../decoded_scripts/1-Wine Cellar/018-The Reckoning Room.txt`](../../decoded_scripts/1-Wine%20Cellar/018-The%20Reckoning%20Room.txt)
- [`../../decoded_scripts/11-Iron Maiden B1/360-The Cauldron.txt`](../../decoded_scripts/11-Iron%20Maiden%20B1/360-The%20Cauldron.txt)
- [`../../decoded_scripts/22-Iron Maiden B2/382-The Eunics' Lot.txt`](../../decoded_scripts/22-Iron%20Maiden%20B2/382-The%20Eunics'%20Lot.txt)

These repeated opener bundles look much more like shared cutscene or room-entry
scaffolding than like unique proof that `0x80` itself is the direct sound
consumer.

### `3 / 42`: repeated `0x1D/0x1E` microcluster

Three residual files instead use:

- `80 01 1D 80 7F`
- immediately followed by `80 01 1E 80 7F`

Representative files:

- [`../../decoded_scripts/2-Catacombs/029-The Last Blessing.txt`](../../decoded_scripts/2-Catacombs/029-The%20Last%20Blessing.txt)
- [`../../decoded_scripts/6-Abandoned Mines B1/271-The Passion of Lovers.txt`](../../decoded_scripts/6-Abandoned%20Mines%20B1/271-The%20Passion%20of%20Lovers.txt)
- [`../../decoded_scripts/6-Abandoned Mines B1/272-The Hall of Hope.txt`](../../decoded_scripts/6-Abandoned%20Mines%20B1/272-The%20Hall%20of%20Hope.txt)

This smaller cluster again arrives with no neighboring sound-family setup
beforehand, which makes it a second residual template family rather than a new
sound-path rescue.

### `3 / 42`: one-off residuals

Only three residual files fall outside those two repeated template groups:

- [`../../decoded_scripts/1-Wine Cellar/021-Room of Rotten Grapes.txt`](../../decoded_scripts/1-Wine%20Cellar/021-Room%20of%20Rotten%20Grapes.txt)
- [`../../decoded_scripts/1-Wine Cellar/022-Chamber of Fear (after the quake).txt`](../../decoded_scripts/1-Wine%20Cellar/022-Chamber%20of%20Fear%20(after%20the%20quake).txt)
- [`../../decoded_scripts/1-Wine Cellar/025-The Hero's Winehall.txt`](../../decoded_scripts/1-Wine%20Cellar/025-The%20Hero's%20Winehall.txt)

Even these one-offs still do not stage any complete sound pair before the
first `0x80`.

## Variant and carry-over hints

Only two residual files currently have same-title sibling variants in the same
area that *do* stage a complete pair before their own first `0x80`:

- [`022-Chamber of Fear (after the quake)`](../../decoded_scripts/1-Wine%20Cellar/022-Chamber%20of%20Fear%20(after%20the%20quake).txt)
  versus
  [`017-Chamber of Fear`](../../decoded_scripts/1-Wine%20Cellar/017-Chamber%20of%20Fear.txt)
- [`408-The Gallows (Mino Zombie, new chest)`](../../decoded_scripts/1-Wine%20Cellar/408-The%20Gallows%20(Mino%20Zombie,%20new%20chest).txt)
  versus
  [`026-The Gallows`](../../decoded_scripts/1-Wine%20Cellar/026-The%20Gallows.txt)

Those are the clearest carry-over or alternate-state candidates in the current
residual set.
They are exceptions, not the dominant pattern.

## Later same-file exceptions

Only two residual files later stage complete neighboring pairs in the same
file after the first `0x80`:

- [`290-Dining in Darkness`](../../decoded_scripts/14-Abandoned%20Mines%20B2/290-Dining%20in%20Darkness.txt)
  later reaches the SFX, music, and queue pairs
- [`334-Torture Without End`](../../decoded_scripts/18-Limestone%20Quarry/334-Torture%20Without%20End.txt)
  later reaches the SFX and queue pairs

These later same-file re-arms matter for scene-local explanation, but they do
not restore a direct sound role for the *opening* residual burst itself.

## Safe takeaway

- The residual set is now much less sound-facing than the earlier
  "42 unexplained files" framing suggested.
- Most residual files do not merely lack a *complete* pair before the first
  `0x80`; they lack any local sound-family setup at all.
- The dominant evidence is now shared template reuse:
  a `36`-file `0x41/0x42` opener family and a `3`-file `0x1D/0x1E`
  microcluster.
- The best remaining open question is no longer "which sound pair explains all
  `42` files?" but rather "why do these shared opener templates still include
  the stubbed `0x80` burst at all?"

Until that template-level meaning is better understood, `Opcode80SharedStub`
remains the safest local name, and the residual set should no longer be treated
as strong positive evidence for the retired direct-sound label.
