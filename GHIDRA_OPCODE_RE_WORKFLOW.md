# Ghidra Opcode RE Workflow

This note is for the next opcode-reversing session so we can resume quickly
instead of re-learning the same setup and toolchain friction.

Current local context:

- workspace root: [`.`](.)
- local Ghidra install: [`tools/ghidra_12.0.4_PUBLIC`](tools/ghidra_12.0.4_PUBLIC)
- local Ghidra project: [`tools/ghidra-project`](tools/ghidra-project)
- game overlay of interest: [`Game Data/BATTLE/BATTLE.PRG`](Game%20Data/BATTLE/BATTLE.PRG)
- decomp reference checkout: [`_refs/rood-reverse`](_refs/rood-reverse)

## Short Version

If the goal is to reverse more script opcodes fast, the best workflow is:

1. Start from the opcode table and decoded script usage in
   [`dump_mpd_script.py`](dump_mpd_script.py)
   and [`decoded_scripts`](decoded_scripts).
2. Use [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c)
   as the main opcode-handler map.
3. Use
   [`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c`](_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c)
   as the exact opcode dispatch table when source order is ambiguous.
4. Use
   [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c)
   and [`146C.h`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h)
   for camera, room, audio, and effect consumers.
5. Use
   [`_refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt`](_refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt)
   when a function is referenced but not easy to locate by browsing alone.
6. Only drop into live Ghidra when the decomp leaves a real gap, especially for
   nonmatching consumers.

That is the path that produced useful progress. The time sink was trying to
force headless Ghidra automation before confirming the local project state.

## What Worked Best

### 1. Start from real script usage first

Before naming an opcode, find several real script contexts in
[`decoded_scripts`](decoded_scripts).

Why:

- repeated usage patterns immediately tell you whether an opcode behaves like
  flow control, camera staging, sound setup, mechanism control, or a visual
  effect pulse
- this keeps names script-friendly instead of overfitting internal field names

Useful examples from this session:

- `0x7A` repeatedly brackets cutscene takeover and cleanup in `MAP062` and
  `MAP138`
- `0xE2` clusters around camera setup and camera motion blocks
- `0xE3` appears inside a visual-effect block with nearby `E1/E4/E5/E6/E7`
  opcodes
- `0xED` and `0xEF` both appear in short repeated bursts, but they do not drive
  the same target path

### 2. Treat `4A0A8.c` as the opcode hub

The main file for script handler work is:

- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c)

This is where the most useful wins came from.

What to do there:

- search for the opcode byte or the handler function
- follow direct helper calls out of the handler
- then inspect where the written field gets consumed

Examples from this session:

- `0x7A` narrowed through `func_800BA108`
- `0xE2` and `0xE3` narrowed through `func_800BD444`
- the timed effect cluster narrowed through `func_800BDAB4` and nearby update
  code

### 2.5. Use `12AC.c` to prove the opcode-to-handler mapping

File:

- [`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c`](_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c)

Why it mattered:

- source order in `4A0A8.c` is not reliable enough by itself once multiple
  camera and effect helpers sit near each other
- the dispatch table gives the exact byte-to-handler mapping without needing to
  infer from nearby function order

Useful confirmed mappings from the current pass:

- `0xE1 -> func_800BB450`
- `0xE2 -> func_800BD444`
- `0xE3 -> func_800BD444`
- `0xE4/0xE5/0xE6/0xE7/0xED -> func_800BD6C4`
- `0xEA/0xEB/0xEC/0xEE/0xEF -> func_800BDC9C`

Important example:

- `0xE1` no longer needs to be inferred from script pattern alone because the
  table maps it directly to the wrapper that calls `func_8007DD50(arg0[1])`

### 3. Use `146C.h` more aggressively

This helped a lot more than expected.

File:

- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h)

Why it mattered:

- some formerly unknown camera fields are already partially named there
- the struct layout gives stronger evidence than old rough notes

Important example:

- `camera_t2` already exposes:
  - `position`
  - `lookAt`
  - `pitch`
  - `yaw`
  - `unk5C`
  - `unk60`
  - `farClip`

That made `0xE2` much stronger as a camera-angle-style tween because its target
is a separate camera field immediately after pitch/yaw, not a generic room or
actor value.

### 4. Use the decomp config as a symbol index

Useful file:

- [`_refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt`](_refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt)

This is handy when:

- a function name appears in decompiled code but you want confirmation that it
  really exists in the symbol map
- you want to search for nearby related functions by address family

Example:

- it confirmed `func_800BD444` and `func_800BE180` in the camera/effect handler
  area
- it exposes `_opcodeFunctionTable`, which is the easiest way to anchor the
  `INITBTL` dispatch table by address or symbol search

## Proven Local Workflow

### Step 1. Find unresolved names in the local decoder

Open:

- [`dump_mpd_script.py`](dump_mpd_script.py)
- [`ROOD_REVERSE_OPCODE_CONCLUSIONS.md`](ROOD_REVERSE_OPCODE_CONCLUSIONS.md)

The fastest pattern is:

- look for placeholder names like `OpcodeXX`
- compare that against the conclusions note to see whether the opcode is truly
  unresolved or just not yet renamed locally

### Step 2. Pull sample script contexts

Use the decoded scripts to gather multiple contexts before opening more code.

Good quick approach:

```powershell
rg -n "Opcode7A|SetScreenEffectEnabled|CameraRollTween|ScreenEffectAngleTween|ScreenEffectScaleTween|ScreenEffectColorTween|ScreenEffectOffsetTween|ScreenEffectParamPairTween|CameraOscillationInit|OpcodeEF" decoded_scripts
```

If the current local names differ, search by raw opcode byte or the old name.

For `0xEF`, do not stop at one example. Pull several rooms and compare the full
five-byte argument pattern, especially repeated control-word pairs like
`0x0067/0x005B` or `0x0193/0x019B`.

### Step 3. Find the handler in `4A0A8.c`

Good search terms:

- the opcode hex value if it appears in a switch
- helper names called from the handler
- known field setters called after the handler updates state
- `_opcodeFunctionTable` when the handler identity itself is still uncertain

Useful commands:

```powershell
rg -n "_opcodeFunctionTable|func_800BB450|func_800BD444|func_800BD6C4|func_800BDC9C" _refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c _refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt
rg -n "0x7A|0xE2|0xE3|0xED|0xEF|func_8007AC94|func_8007DDAC|func_8007DDB8|func_8007DDD4|func_8007DDF8|vs_screff2_setParamPair|func_800BE180" _refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c _refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c
```

### Step 4. Follow the consumer, not just the setter

This was the key difference between a vague subsystem guess and a useful name.

Examples:

- `func_8007AC94(arg0)` writes `_camera.t2.unk5C`
- `func_8007DDAC(arg0)` writes `D_800F1A2C`
- `vs_screff2_setParamPair(param0, param1)` writes two persistent parameters in
  `SCREFF2.PRG`
- `func_800BE180` advances two waveform slots whose outputs are rotated into
  camera-relative offsets and added to `cameraLookAt` and `cameraPos`

That consumer-side tracing is what separated:

- `camera-side angle tween`
from
- `screen-effect-side angle tween`

### Step 5. Rename locally only when the script-facing meaning is honest

Local decoder names do not need to wait for upstream-perfect certainty, but they
should still be honest.

Good examples from this session:

- `SetRoomAmbientSoundSuspended`
- `CameraRollTween`
- `ScreenEffectAngleTween`
- `CameraOscillationInit`

What stayed conservative:

- `0xEF` now uses the local decoder name `CameraOscillationInit`, but it is
  still not hard-renamed upstream because the exact control-word layout and
  final player-facing label are not nailed down yet

## Ghidra Setup Notes

### Installed local pieces

Main install:

- [`tools/ghidra_12.0.4_PUBLIC`](tools/ghidra_12.0.4_PUBLIC)

Project:

- [`tools/ghidra-project`](tools/ghidra-project)

PSX loader extension:

- `ghidra_psx_ldr`

Important extension location:

- `C:\Users\Chris\AppData\Roaming\ghidra\ghidra_12.0.4_PUBLIC\Extensions\ghidra_psx_ldr`

Important loader fact:

- the extension loader name is `PSX Executables Loader`

The extension source zip includes:

- `psx/PsxLoader.java`

That file confirms the loader name and that it uses PSX language id:

- `PSX:LE:32:default`

### What the local Ghidra project looked like

Current files:

- [`tools/ghidra-project/Vagrant Story USA.gpr`](tools/ghidra-project/Vagrant%20Story%20USA.gpr)
- [`tools/ghidra-project/Vagrant Story USA.rep`](tools/ghidra-project/Vagrant%20Story%20USA.rep)
- [`tools/ghidra-project/Vagrant Story USA.lock`](tools/ghidra-project/Vagrant%20Story%20USA.lock)

Important caution:

- the project had a lock file during this session
- headless opening of the live project failed with a lock error

## Ghidra Walls Hit This Session

### 1. Headless open failed on the live project because of the lock

Command style attempted:

```powershell
tools\ghidra_12.0.4_PUBLIC\support\analyzeHeadless.bat ...
```

Observed problem:

- `Unable to lock project`

Practical takeaway:

- do not start by poking the live project headlessly
- either open the project interactively in Ghidra, or copy the project to a
  scratch location first

### 2. Copying the project avoided the lock, but `-process BATTLE.PRG` still failed

After copying the project and removing copied lock files, headless access got
past the lock but then failed with:

- `Requested project program file(s) not found: BATTLE.PRG`

Practical takeaway:

- the copied project was not immediately usable as a drop-in headless target for
  `-process BATTLE.PRG`
- do not assume the local project already contains a program object with the
  exact expected name

### 3. Headless automation was a worse first step than source + grep

This is the biggest lesson.

For opcode naming specifically:

- `rood-reverse` source plus `rg` plus decoded script samples got us real
  progress fast
- headless Ghidra burned time before we even reached the actual code question

So the next session should only push harder on headless scripting if the source
walk truly bottoms out.

## Best Ghidra Strategy Next Time

### Preferred path

1. Open the local Ghidra GUI project manually.
2. Confirm the exact imported program names inside the project before trying any
   headless `-process` use.
3. If the GUI project is awkward, import `Game Data/BATTLE/BATTLE.PRG` into a
   fresh scratch project using the PSX loader rather than debugging the old
   project structure first.
4. Use Ghidra mainly for:
   - xrefs to still-unnamed globals
   - browsing nonmatching consumers
   - checking data layout when decompiled source is partial

### If creating a fresh scratch project

Use:

- loader: `PSX Executables Loader`
- language: `PSX:LE:32:default`

Priority target:

- `Game Data/BATTLE/BATTLE.PRG`

Then immediately locate:

- the opcode handler area around the `4A0A8.c` address family
- camera/effect consumers around the `146C.c` address family

## Known Useful RE Anchors

### Main handler file

- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c)

### Main consumer file

- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c)

### Effect-side helper

- [`_refs/rood-reverse/src/GIM/SCREFF2.PRG/0.c`](_refs/rood-reverse/src/GIM/SCREFF2.PRG/0.c)

### Best current examples

- `0x7A`: room ambient sound suspend/restore around cutscene control
- `0xE2`: camera-side angle tween writing `_camera.t2.unk5C`
- `0xE3`: effect-side angle tween writing `D_800F1A2C`
- `0xED`: direct two-parameter `SCREFF2` tween feeding
  `vs_screff2_setParamPair`
- `0xEF`: camera-relative oscillation init feeding two waveform slots through
  `func_800BE180`

## Good Starting Queries Next Session

Use these first:

```powershell
rg -n "_opcodeFunctionTable|func_800BB450|func_800BD444|func_800BD6C4|func_800BDC9C" _refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c _refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt
rg -n "0x7A|0xE2|0xE3|0xED|0xEF" _refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c
rg -n "func_8007AC94|func_8007DDAC|func_8007DDB8|func_8007DDD4|func_8007DDF8|vs_screff2_setParamPair|func_800BE180|unk5C|D_800F1A2C" _refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c _refs/rood-reverse/src/GIM/SCREFF2.PRG/0.c _refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c
rg -n "Opcode7A|SetScreenEffectEnabled|ScreenEffectScaleTween|ScreenEffectColorTween|ScreenEffectOffsetTween|ScreenEffectParamPairTween|CameraOscillationInit|OpcodeEF|CameraRollTween|ScreenEffectAngleTween" decoded_scripts
```

If looking for the next best unknown after this session, inspect nearby `E`-range
handlers as a group instead of singly:

- `E1`
- `E4`
- `E5`
- `E6`
- `E7`
- `ED`
- `EF`

Those clearly participate in one effect subsystem.

## Suggested Next Targets

Most promising:

1. Recover the exact control-word layout behind `0xEF`, especially slot and
   envelope selection.
2. Confirm whether `0xE6` is best described as effect offset, drift, or some
   more specific render-space term.
3. Use Ghidra xrefs to identify the real user-facing meaning of `D_800F1A2C`
   and the two `SCREFF2` parameter fields fed by `0xED`.

Nice follow-up:

1. Add comments in the `rood-reverse` reference checkout around the handler and
   consumer code.
2. Keep the local decoder and conclusions note synchronized as confidence improves.

## Session Reminder

Do not begin by fighting headless Ghidra again unless there is a concrete reason.

The fastest route is:

- decoded script pattern
- matched handler
- matched consumer
- only then Ghidra for the remaining unnamed field
