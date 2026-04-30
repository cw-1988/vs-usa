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
into `decomp/evidence/opcode_0x80_runtime_observation.json`.

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

Expected outputs:

- `decomp/evidence/opcode_0x80_runtime_after_init.bin`
- `decomp/evidence/opcode_0x80_runtime_pre_dispatch.bin`
- `decomp/evidence/opcode_0x80_runtime_automation_summary.json`
- refreshed `decomp/evidence/opcode_0x80_runtime_observation.json`
- refreshed compare/support artifacts through the existing finalize flow

Operational assumptions:

- use a scriptable `PCSX-Redux` CLI-capable build
- run with the interpreter core plus debugger support
- keep the output files under `decomp/evidence`
- let the wrapper and recorder/finalizer own the observation packet updates

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
