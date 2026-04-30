# Opcode `0x80` Runtime Capture Plan

## Goal

Break the remaining `0x80` contradiction with one runtime pass:

- prove whether the copied `0x400`-byte opcode table at `0x800F4C28` stays
  identical to the `INITBTL.PRG` export after init
- confirm which handler address actually executes if `0x80`, `0x81`, or `0x82`
  are ever dispatched live

Static evidence has already narrowed the question to runtime. This note is the
smallest capture plan that should settle it.

## Known anchors

- Runtime table slot: `0x800F4C28`
- Runtime table size: `0x400` bytes (`256 * 4`)
- Baseline export: `decomp/evidence/inittbl_opcode_table.json`
- Live runtime table reader: `FUN_800BFBB8`
- Reader address: `0x800BFBB8`
- Current static `0x80-0x82` target: `0x800B66E4`
- Nearby competing sound-family candidate: `0x800BA2E0`
- Visible neighboring sound-family handlers: `0x800BA35C`, `0x800BA39C`,
  `0x800BA3E4`, `0x800BA404`, `0x800BA444`, `0x800BA470`, `0x800BA494`

## What to capture

1. One raw dump of the table immediately after the init-time copy has happened.
2. One raw dump as late as practical before any candidate `0x80-0x82`
   dispatch.
3. Any later dump if a memory write breakpoint or read breakpoint suggests the
   table changed after the second capture.
4. The actual dispatch target address if execution reaches `0x800B66E4`,
   `0x800BA2E0`, or another rewritten slot for `0x80-0x82`.

## Default runtime path

The default runtime path for this contradiction is now automated
`PCSX-Redux` CLI capture, not manual debugger driving.

Use:

- `decomp/verification/pcsx_redux_opcode_0x80_capture.lua`
- `decomp/verification/run_opcode_0x80_runtime_capture.ps1`

The wrapper launches a scriptable `PCSX-Redux` build with startup Lua, plants
the known breakpoints, dumps the copied table directly from emulator memory,
and records the resulting snapshot paths plus a compact automation summary back
into `decomp/evidence/opcode_0x80_runtime_observation.json`. When no
near-battle savestate exists yet, the same wrapper can now translate a
checked-in JSON pad-input plan into a Lua replay schedule instead of leaving
the cold-boot fallback entirely manual.

The wrapper now also auto-raises the runtime timeout when an input plan would
otherwise outlast the base `1800`-frame default. That matters for the
checked-in cold-boot scaffold because the latest retunes are longer than the
first six-step starter plan and rely on visual checkpoints to prove progress.
The current blocker is no longer hidden timeout behavior: the route now reaches
the title menu and can open the `Load / Memory Card slot 1` screen, but it
still records no `0x800BFBB8` reader hit, no runtime-table write hit, and no
snapshots because the repo-local cards do not yet provide a usable path into
live gameplay.

Official `PCSX-Redux` docs that back this path:

- CLI launch surface used by the wrapper:
  <https://pcsx-redux.consoledev.net/cli_flags/>
- Lua runtime control, pads, and savestate APIs used or available to the
  capture script:
  <https://pcsx-redux.consoledev.net/Lua/redux-basics/>
- Lua execution and write breakpoints used by the capture script:
  <https://pcsx-redux.consoledev.net/Lua/breakpoints/>
- Lua events available for boot/savestate-aware scripting:
  <https://pcsx-redux.consoledev.net/Lua/events/>
- Lua memory and register access used for raw table dumps and PC filtering:
  <https://pcsx-redux.consoledev.net/Lua/memory-and-registers/>
- MIPS-side callback surface available if the runtime path later needs
  instrumented code or `pcsx_execSlot()`-style handshakes:
  <https://pcsx-redux.consoledev.net/mips_api/>

Recommended usage shape:

```powershell
pwsh -File decomp/verification/run_opcode_0x80_runtime_capture.ps1 `
  -IsoPath "<path-to-disc-image>"
```

When a nearer launch state exists, prefer resuming from that state instead of
repeating a cold boot. The wrapper now supports both explicit savestate paths
and "pick the newest nearby state" flow:

```powershell
pwsh -File decomp/verification/run_opcode_0x80_runtime_capture.ps1 `
  -IsoPath "Game Data/Vagrant Story (USA).cue" `
  -SaveStatePath "decomp/evidence/opcode_0x80_near_battle.p2s.gz"

pwsh -File decomp/verification/run_opcode_0x80_runtime_capture.ps1 `
  -IsoPath "Game Data/Vagrant Story (USA).cue" `
  -UseNewestSaveState
```

When no savestate is available yet, tune the checked-in starter plan and use
the same wrapper to replay a conservative title/menu sequence through the
documented `PCSX.SIO0.slots[*].pads[*]` override API:

```powershell
pwsh -File decomp/verification/run_opcode_0x80_runtime_capture.ps1 `
  -IsoPath "Game Data/Vagrant Story (USA).cue" `
  -UseDefaultInputPlan
```

The default scaffold lives at:

- `decomp/evidence/opcode_0x80_runtime_input_plan.json`
- `decomp/evidence/opcode_0x80_runtime_memcard_probe.md`

That JSON is intentionally a starter plan, not proof. Keep it checked in,
tune the frame waits as real runs reveal the actual menu timing, and prefer a
near-battle savestate again as soon as one exists. If no save-bearing card is
available, the next cold-boot branch should be `New Game` far enough to earn a
real save or checkpoint, not more retries of the blank-card `Load` path.

Current cold-boot status:

- the wrapper now emits per-step screen-capture artifacts under
  `decomp/evidence/opcode_0x80_runtime_frames/`, and the latest captures are
  informative enough to show the route reaching the title logo, the title
  menu, and the `Load / Memory Card slot 1` screen
- corrected PSX-style menu mapping matters here: this build uses `O` confirm /
  `X` cancel, and the checked-in input plan now reflects that
- the repo-local `memcard1.mcd` and `memcard2.mcd` probe as blank formatted
  cards in `decomp/evidence/opcode_0x80_runtime_memcard_probe.json`
- that means the current `Load` route is now a confirmed dead branch for this
  workspace, not a promising gameplay-entry path
- the next fallback edit should therefore target a `New Game`-to-save route or
  a savestate-bearing handoff artifact, not more retries of the blank-card
  `Load` path

Savestate-specific behavior:

- `-SaveStatePath` accepts either a raw savestate payload or a
  gzip-compressed `PCSX-Redux` UI savestate.
- `-UseNewestSaveState` searches `decomp/evidence`, `.codex_tmp`, and repo
  root plus the portable save directory next to `pcsx-redux.exe` for the
  newest `*.p2s`, `*.p2s.gz`, `*.savestate`, `*.savestate.gz`, `*.state`, or
  `*.state.gz` file.
- gzip-compressed savestates are staged into `.codex_tmp/pcsx-redux/` before
  launch so Lua can feed an uncompressed file to `PCSX.loadSaveState(file)`.
- the Lua capture script now records the savestate-load event and captures the
  earliest `after_init` fallback snapshot from the restored runtime state if a
  reader hit has not happened yet.
- `-UseDefaultInputPlan` loads the checked-in
  `decomp/evidence/opcode_0x80_runtime_input_plan.json` scaffold.
- `-InputPlanPath` accepts a custom JSON plan with sequential button steps, so
  pad/menu automation can still run through the wrapper when the fallback path
  needs different timing or a different menu route.

Expected outputs:

- `decomp/evidence/opcode_0x80_runtime_after_init.bin`
- `decomp/evidence/opcode_0x80_runtime_pre_dispatch.bin`
- `decomp/evidence/opcode_0x80_runtime_automation_summary.json`
- optional replay metadata for `decomp/evidence/opcode_0x80_runtime_input_plan.json`
  inside the automation summary and observation packet notes
- refreshed `decomp/evidence/opcode_0x80_runtime_observation.json`
- refreshed compare/support artifacts through the existing finalize flow

Operational assumptions:

- use a scriptable `PCSX-Redux` CLI-capable build
- run with the interpreter core plus debugger support
- keep the output files under `decomp/evidence`
- let the wrapper and recorder/finalizer own the observation packet updates
- if a savestate is used, keep the original `.p2s` or `.gz` file as the
  durable handoff artifact; the staged raw payload under `.codex_tmp` is only
  a temporary loader aid

## Manual fallback checklist

If the automated CLI path is blocked for a specific run, fall back to the
manual debugger procedure below.

1. Enable the debugger features needed for execution and memory breakpoints.
2. Open the memory editor at `0x800F4C28`.
3. Create a memory write breakpoint that covers `0x800F4C28` through
   `0x800F5027`.
4. Create a memory read breakpoint on the same range if you want an earlier
   stop when the runtime reader first consumes the copied table.
5. Add execution breakpoints at:
   - `0x800BFBB8`
   - `0x800B66E4`
   - `0x800BA2E0`
6. When the init copy has completed, export `0x400` bytes from the memory
   editor to a raw file such as:
   - `decomp/evidence/opcode_0x80_runtime_after_init.bin`
7. When the late runtime state is reached, export the same `0x400` bytes again,
   for example:
   - `decomp/evidence/opcode_0x80_runtime_pre_dispatch.bin`
8. If the table changes later, export another raw file at the mutation point.
9. Record the breakpoint hits and dump paths in
   `decomp/evidence/opcode_0x80_runtime_observation.json`.

Use the recorder helper instead of hand-editing the JSON during the runtime
pass. Examples:

```powershell
python decomp/verification/record_runtime_observation.py `
  decomp/evidence/opcode_0x80_runtime_observation.json `
  set-snapshot `
  --label after_init `
  --path decomp/evidence/opcode_0x80_runtime_after_init.bin `
  --finalize `
  --allow-missing-snapshots

python decomp/verification/record_runtime_observation.py `
  decomp/evidence/opcode_0x80_runtime_observation.json `
  add-breakpoint-hit `
  --kind exec `
  --address 0x800BFBB8 `
  --pc 0x800BFBB8 `
  --note "reader reached before candidate dispatch" `
  --finalize `
  --allow-missing-snapshots

python decomp/verification/record_runtime_observation.py `
  decomp/evidence/opcode_0x80_runtime_observation.json `
  add-dispatch `
  --opcode 0x80 `
  --handler-address 0x800B66E4 `
  --source-breakpoint 0x800B66E4 `
  --note "dispatch stayed on the copied stub target" `
  --finalize `
  --allow-missing-snapshots
```

## Checked-in scaffold

This repo now keeps a partially finalized observation scaffold at:

- `decomp/evidence/opcode_0x80_runtime_observation.json`

It already records the planned breakpoints, expected dump paths, and the
current "missing snapshot" state, so the next runtime pass can update that
file directly instead of starting from a blank template.

The same JSON also names the helper scripts:

- `record_helper`: `decomp/verification/record_runtime_observation.py`
- `finalize_helper`: `decomp/verification/finalize_runtime_observation.py`
- `expected_bin_path`: `decomp/evidence/opcode_0x80_runtime_expected_table.bin`

The finalize helper now also reconstructs the binary-derived baseline pointer
table into that `expected_bin_path` artifact and records its size/hash in the
compare report, so the runtime pass has a checked-in byte-for-byte baseline to
diff against in addition to the JSON export.

If the scaffold ever needs to be regenerated from the untouched template, use:

```powershell
python decomp/verification/finalize_runtime_observation.py `
  decomp/evidence/opcode_0x80_runtime_observation_template.json `
  --allow-missing-snapshots `
  --output-observation decomp/evidence/opcode_0x80_runtime_observation.json
```

## Compare the dumps

Use the runtime snapshot helper to reconstruct the binary baseline and compare
the RAM captures:

```powershell
python decomp/verification/compare_opcode_table_snapshots.py `
  decomp/evidence/inittbl_opcode_table.json `
  decomp/evidence/opcode_0x80_runtime_after_init.bin `
  decomp/evidence/opcode_0x80_runtime_pre_dispatch.bin `
  --label after_init `
  --label pre_dispatch `
  --focus-opcode 0x80 `
  --focus-opcode 0x81 `
  --focus-opcode 0x82 `
  --write-expected-bin decomp/evidence/opcode_runtime_expected_table.bin `
  --output decomp/evidence/opcode_0x80_runtime_snapshot_compare.json
```

Then finalize the observation packet so the compare report, support note,
reconstructed baseline blob, and updated JSON all agree:

```powershell
python decomp/verification/finalize_runtime_observation.py `
  decomp/evidence/opcode_0x80_runtime_observation.json `
  --in-place
```

If one snapshot is still missing and you only want a partial handoff artifact,
add `--allow-missing-snapshots`.

If the compare report shows changed handlers for the focus opcodes, import
those rows back into the checked-in observation packet so the mutation section
is explicit instead of living only inside the compare JSON:

```powershell
python decomp/verification/record_runtime_observation.py `
  decomp/evidence/opcode_0x80_runtime_observation.json `
  import-compare `
  --replace-derived `
  --finalize
```

Add `--include-non-focus` if the runtime pass needs every changed opcode row,
not just the changed `0x80-0x82` focus entries.

## Exit conditions

The contradiction is statically resolved enough to treat runtime as decisive if
one of these happens:

- both dumps match the baseline export exactly, especially `0x80-0x82`
- a later dump shows changed handlers for `0x80-0x82`
- execution reaches a handler that proves the table was rewritten or bypassed

## Result handling

If the table never changes and dispatch still lands on `0x800B66E4`, the next
pass can safely narrow `SoundEffects0` further or retire it as an overclaim.

If the table changes or dispatch reaches a different handler, store:

- the raw dump(s)
- the comparison report
- the filled observation template
- the generated runtime support note
- imported `table_mutations` rows in the checked-in observation packet when
  the compare report changes the focus opcodes
- one short runtime support note summarizing the decisive hit

Then update `RE_CAMPAIGN_MEMORY.md` before ending the pass.
