## Vagrant Story Script Opcode Conclusions

This note collects high-confidence opcode conclusions that appear to improve on the
current public table at Data Crystal:

- Source: <https://datacrystal.tcrf.net/wiki/Vagrant_Story/Script_Opcodes>

The goal is to keep this contribution set conservative: only names with a clear
code-path or script-usage proof are listed as confirmed. Anything still fuzzy
should stay tentative in upstream comments and PR text.

Use [`OPCODE_BEHAVIOR_REFERENCE.md`](OPCODE_BEHAVIOR_REFERENCE.md) as the quick
lookup for the current local opcode table, parameter layouts, and unresolved
slots. This note is the longer evidence and confidence trail for the names that
matter enough to justify written conclusions.

### Confidence guide

Use this quick rubric when judging an opcode name:

- `Confirmed`: the handler body is readable and the behavior matches real script
  usage.
- `Strong`: the handler target is clear and the likely subsystem is clear, but
  one part of the user-facing meaning still needs proof.
- `Tentative`: the opcode has been narrowed down to a subsystem or helper path,
  but the final script-friendly name would still be guesswork.

For this note, `rood-reverse` is the better source for opcode work than Data
Crystal when a handler is actually decompiled. Data Crystal is still useful as a
legacy address table, but its names should be treated as historical notes until
the code body agrees.

### Current coverage snapshot

The current local decoder table in
[`dump_mpd_script.py`](dump_mpd_script.py) now covers all `256` opcode slots,
but only part of that table is meaningfully named:

- named locally: `85 / 256`
- still placeholder-named as `OpcodeXX`: `171 / 256`
- most complete block: `0xE0-0xEF` with `14` named and only `0xE8` / `0xEE`
  still unresolved
- completely unresolved block: `0xB0-0xBF`

The heaviest remaining unknown regions are:

- `0xA3-0xBF`
- `0xC5-0xCF`
- `0xD5-0xDF`
- `0xF7-0xFE`

There are also `22` placeholder entries whose current local size is still
`0x00`, so they remain unsafe targets for any confident rename or decoder
cleanup pass:

- `0x09`
- `0x8A-0x8E`
- `0xA7`
- `0xAB-0xAF`
- `0xB0`
- `0xC6`
- `0xCC-0xCF`
- `0xD6`
- `0xDC-0xDD`
- `0xEE`

### Still missing from the current local opcode list

Here, "missing" means the local decoder still exposes only a placeholder name
such as `Opcode41`, not merely that this note lacks a long write-up.

- `0x01-0x0F`
- `0x13-0x15`
- `0x1B-0x1F`
- `0x21`
- `0x25`
- `0x27`
- `0x2A-0x2D`
- `0x32`
- `0x34-0x37`
- `0x3C-0x3D`
- `0x3F`
- `0x41`
- `0x43`
- `0x45-0x48`
- `0x4B-0x4F`
- `0x51-0x53`
- `0x55-0x57`
- `0x59-0x63`
- `0x66-0x67`
- `0x6A-0x6C`
- `0x6E-0x6F`
- `0x71-0x73`
- `0x77`
- `0x7B`
- `0x7D-0x7F`
- `0x81-0x84`
- `0x87`
- `0x89-0x8F`
- `0x93-0x98`
- `0x9A-0x9C`
- `0x9F-0xA0`
- `0xA3-0xBF`
- `0xC3`
- `0xC5-0xCF`
- `0xD2-0xD3`
- `0xD5-0xDF`
- `0xE8`
- `0xEE`
- `0xF1-0xF3`
- `0xF7-0xFE`

### Documented local names still awaiting per-opcode proof write-ups

These names are already usable in the local decoder. What was missing here was
not the names themselves, but a short record of why they are currently
reasonable and what would still be needed before each one should be treated as
fully `Confirmed` in the same sense as the stronger entries below.

#### Dialog and splash-screen control

Current local names:

- `0x10 -> DialogShow`
- `0x11 -> DialogText`
- `0x12 -> DialogHide`
- `0x16 -> SplashScreenChoose`
- `0x17 -> SplashScreenLoad`
- `0x18 -> SplashScreenShow`
- `0x19 -> SplashScreenHide`
- `0x1A -> SplashScreenFadeIn`

Current narrow:

- `0x10-0x12` already decode cleanly as dialog id, text id, and dialog box
  control fields in the script dumper, so the dialog-family naming is on solid
  local footing.
- `0x16-0x1A` cluster as a separate overlay or splash-screen path rather than
  actor, room, or camera control, and their current verbs match the usual
  script ordering pattern of choose or load, then show, hide, or fade.
- `0x13-0x15` remain unresolved, so this block is only partially mapped.

What is still missing for `Confirmed`:

- A direct handler-by-handler decomp citation for the splash-screen verbs,
  especially the exact difference between `Choose`, `Load`, and `Show`.
- One proof pass that ties the fade opcode specifically to fade-in behavior and
  not a more generic overlay transition mode.

#### Core model staging

Current local names:

- `0x20 -> ModelLoad`
- `0x22 -> ModelAnimate`
- `0x23 -> ModelSetAnimations`
- `0x26 -> ModelPosition`
- `0x28 -> ModelMoveTo`
- `0x29 -> ModelMoveTo2`
- `0x2E -> ModelScale`
- `0x30 -> ModelLoadAnimationsEx`
- `0x31 -> ModelTint`
- `0x33 -> ModelRotate`
- `0x38 -> ModelLookAt`
- `0x39 -> ModelLookAtPosition`
- `0x3A -> ModelLoadAnimations`
- `0x3E -> ModelIlluminate`
- `0x42 -> ModelControlViaScript`
- `0x50 -> ModelControlViaBattleMode`
- `0x70 -> ModelColor`
- `0xC4 -> ModelAnimateObject`

Current narrow:

- The argument shapes already look like a coherent actor-model control family:
  actor ids, animation ids, position triples, rotation-like fields, look-at
  targets, and color or tint style parameters all show up where expected.
- Some names in this group are already stronger than the rest. `ModelScale`,
  `ModelTint`, and `ModelLookAtPosition` have enough local evidence to be worth
  upstreaming even before every neighboring model opcode gets a full write-up.
- The weaker names are the ones that still hide an important mode distinction
  behind generic wording, such as `ModelMoveTo` versus `ModelMoveTo2`,
  `ModelLoadAnimations` versus `ModelLoadAnimationsEx`, and the control wrappers
  around `0x42`, `0x50`, and `0xC4`.

What is still missing for `Confirmed`:

- Direct handler evidence for the alternate load, move, and animate variants so
  the local names can explain the difference instead of only naming the shared
  subsystem.
- One field-level pass for `0x3E`, `0x42`, `0x50`, `0x70`, and `0xC4` to decide
  whether the current names are precise enough or still slightly too generic.

#### Room loading and scene-display flow

Current local names:

- `0x68 -> LoadRoom`
- `0x69 -> LoadScene`
- `0x6D -> DisplayRoom`
- `0x74 -> LoadRoomSection10`
- `0x75 -> WaitForRoomSection10`
- `0x76 -> FreeRoomSection10`

Current narrow:

- `0x68` already formats as a zone-room destination pair in the dumper, which
  makes a room-loader interpretation much stronger than a generic file load.
- `0x6D` behaves like a display or activation step that appears after load or
  staging work rather than before it.
- `0x74-0x76` form a clean async trio by both naming and script position: load,
  then wait, then free.

What is still missing for `Confirmed`:

- A direct proof of the exact distinction between `LoadRoom` and `LoadScene`.
- One decomp-backed identification of what "section 10" actually contains so
  the section-10 names can eventually become more user-facing if warranted.

#### Core audio flow

Current local names:

- `0x80 -> SoundEffects0`
- `0x85 -> LoadSfxSlot`
- `0x86 -> FreeSfxSlot`
- `0x88 -> SetCurrentSfx`
- `0x90 -> LoadMusicSlot`
- `0x91 -> FreeMusic`
- `0x92 -> MusicPlay`
- `0x99 -> ClearMusicLoadSlot`
- `0x9D -> LoadSoundFileById`
- `0x9E -> ProcessSoundQueue`

Current narrow:

- This block already reads like a shared sound pipeline rather than unrelated
  opcodes: resource loads, slot selection, explicit frees, then queue or
  process steps.
- `0x80` is still unresolved, but not in a way that justifies a clean
  downgrade back to a generic placeholder. The static dispatch table currently
  routes `0x80` to `func_800B66E4`, whose matched body is only `return 0;`.
- A CLI-first replay now proves that directly from the binary too:
  `decomp/evidence/inittbl_opcode_table.json` exports `0x80 -> 0x800B66E4`,
  and `decomp/evidence/battle_0x80_handler_slices.json` shows the handler
  opens with `jr ra` / `clear v0`.
- At the same time, the nearby unmatched helper `func_800BA2E0` in the same
  source file consumes the exact 4 argument bytes that `0x80` uses in scripts
  and calls `vs_main_playSfx(D_800E9B34[arg0[1]], arg0[2], arg0[3], arg0[4])`.
- The same CLI pass also captured that candidate at the instruction level in
  `decomp/evidence/battle_sound_candidate_slice.json`, including the
  `jal 0x80045754` call that `_refs/rood-reverse/config/SLUS_010.40/symbol_addrs.txt`
  names `vs_main_playSfx`.
- Real script usage still clusters like a sound cue rather than inert padding:
  `0x80` appears heavily in cutscene timing slots such as
  `80 03 1E 80 7F`, `80 03 19 80 7F`, and `80 03 30 7F 7F`, often between
  camera, wait, and display opcodes where an immediate effect cue would make
  sense.
- `LoadSoundFileById` and `ProcessSoundQueue` are especially strong locally
  because real scripts commonly pair `9D xx` with a later `9E`.
- `LoadSfxSlot`, `FreeSfxSlot`, `SetCurrentSfx`, `LoadMusicSlot`, and
  `ClearMusicLoadSlot` are all plausible and internally consistent names, but
  some still rest more on script ordering than on fully cited handler bodies.

What is still missing for `Confirmed`:

- A handler-level pass that separates pure resource management from immediate
  playback, especially for `0x80`, `0x88`, and `0x92`.
- One cleaner write-up of how the music-slot and sound-file-id paths interact,
  so `LoadMusicSlot` and `MusicPlay` can be documented with the same confidence
  now used for `LoadSoundFileById`.

#### Core camera flow outside the effect-heavy `E` range

Current local names:

- `0xA2 -> CameraZoomIn`
- `0xC0 -> CameraDirection`
- `0xC1 -> CameraSetAngle`
- `0xC2 -> CameraLookAt`
- `0xD0 -> CameraPosition`
- `0xD1 -> SetCameraPosition`
- `0xD4 -> CameraHeight`
- `0xE0 -> CameraWait`
- `0xEA -> CameraZoom`
- `0xEB -> CameraNearClip`
- `0xEC -> CameraFarClip`

Current narrow:

- The operand shapes and local formatting already separate this block from the
  screen-effect opcodes: position, look-at, direction, zoom, and clip-plane
  style fields dominate instead of color or oscillation parameters.
- `CameraZoom`, `CameraNearClip`, and `CameraFarClip` are among the cleaner
  local names because their formatter fields already decode into useful scalar
  values rather than opaque raw bytes.
- The weaker names are the ones where the noun is clear but the exact action is
  not yet locked down, such as whether `CameraSetAngle` and `SetCameraPosition`
  are immediate setters, mode selectors, or trigger bytes for previously staged
  camera state.

What is still missing for `Confirmed`:

- Direct consumer or handler proof for the single-byte control opcodes
  `0xA2`, `0xC1`, `0xD1`, and `0xE0`.
- One tighter pass on `0xC0`, `0xC2`, `0xD0`, and `0xD4` that names their
  fields more specifically than today's conservative direction, look-at,
  position, and height labels.

#### Script flow helpers

Current local names:

- `0xF0 -> Wait`
- `0xF4 -> ScriptCallSlotActive`
- `0xF5 -> ScriptCall`
- `0xF6 -> ScriptReturn`

Current narrow:

- This block is already clearly control-flow related rather than content
  staging. The local names match how the decoder treats the operands and how
  the opcodes appear in call or return style script regions.
- `Wait`, `ScriptCall`, and `ScriptReturn` are stronger than
  `ScriptCallSlotActive`, which still exposes the bookkeeping flavor of the
  implementation more than a settled player-facing verb.

What is still missing for `Confirmed`:

- A small helper-level proof write-up for the call-slot state checked or
  updated by `0xF4`.
- One explicit note on the target encoding used by `0xF5`, mainly so the local
  call naming can cite something more concrete than script-structure patterning.

### Confirmed improvements

#### Opcode `0x24`

- Data Crystal: unnamed (`800b77dc`)
- Confirmed name: `ActorSfxPanVolumeControl`
- Confidence: `Confirmed`

Why:

- This opcode stores a little sound-control state on an actor.
- That stored state is later read by the sound code that decides where a sound
  should come from and how loud it should be.
- There is also a cleanup path that clears the same state again, which matches
  the idea of a temporary actor sound override rather than a one-shot trigger.

Current best script-level interpretation:

- `mode 0`: clear actor SFX spatial override state
- `mode 1`: set or pulse an override
- `mode 2`: set the default/basis used by later `mode 1` updates

The exact field names for the three control bytes may still deserve refinement,
but the subsystem identity is high-confidence.

#### Opcode `0x49`

- Data Crystal: unnamed (`800b8c54`)
- Confirmed name: `SetJumpBackCounter`
- Confidence: `Confirmed`

Why:

- The matched opcode dispatch table in
  [`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c`](_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c)
  maps `0x49` directly to the small readable handler now renamed
  `vs_battle_script_setJumpBackCounter`.
- That handler only does one thing: when the first script byte is not `0xFF`,
  it stores the second byte into a local counter-slot array at
  `D_800F4C10[arg0[1]]`.
- The paired opcode `0x4A` later decrements that same slot and uses it to
  decide whether to jump backward, which makes `0x49` the explicit counter-setup
  half of the pair rather than a generic flag or mode write.
- In decoded scripts, the only currently reachable counted form is
  `49 00 01`, which matches a one-iteration setup for the later `4A 00 ...`
  consumer. The repeated cathedral shake loops instead use the reserved
  `49 FF 00` scaffolding form before the unconditional `4A FF ...` back-jump.

Current best script-level interpretation:

- `49 ss cc`: store initial loop/jump-back count `cc` into counter slot `ss`
- `49 FF 00`: reserved unconditional form used alongside `4A FF ...`

#### Opcode `0x4A`

- Data Crystal: unnamed
- Confirmed name: `JumpBackIfCounter`
- Confidence: `Confirmed`

Why:

- The matched opcode dispatch table maps `0x4A` directly to the readable
  handler
  [`vs_battle_script_jumpBackIf`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c),
  now tightened to `vs_battle_script_jumpBackIfCounter` in the nested repo.
- When the first script byte is `0xFF`, the handler immediately returns
  `&arg0[-vs_battle_getShort(arg0 + 2)]`, which is an unconditional backward
  jump by the encoded 16-bit offset.
- Otherwise it pre-decrements `D_800F4C10[arg0[1]]` and only returns that same
  backward jump target while the decremented slot stays nonzero.
- Real script usage matches both forms. `MAP131`, `MAP133`, and `MAP413`
  repeatedly use `49 FF 00` plus `4A FF ...` to loop camera-oscillation beats,
  while `MAP318` and `MAP321` use the slot `0` form `49 00 01` / `4A 00 8A 00`
  as the counted variant.

Current best script-level interpretation:

- `4A FF ll hh`: unconditionally jump backward by `<h ll hh>` bytes
- `4A ss ll hh`: decrement counter slot `ss`, then jump backward by
  `<h ll hh>` while the result stays nonzero

#### Opcode `0x78`

- Data Crystal: unnamed (`800ba0e4`)
- Confirmed name: `EnableRoomMechanismUpdates`
- Confidence: `Confirmed`

Why:

- This opcode flips the room mechanism update loop on or off.
- In scripts it appears right where cutscenes take control away from normal room
  logic, then appears again when normal room behavior is handed back.
- It sits right next to the room mechanism control opcode, so it is clearly part
  of the same subsystem.

Important detail:

- The script byte is inverted by the handler, so `1` means disabled and `0`
  means enabled.

#### Opcode `0x79`

- Data Crystal: unnamed (`800ba194`)
- Confirmed name: `RoomMechanismControl`
- Confidence: `Confirmed`

Why:

- One sub-command tells the game to fire a room mechanism by id.
- The other sub-command flips that mechanism between enabled and disabled.
- The same code path is used by doors, locks, and other room objects, so this
  is not just a cutscene-only special case.

Current best script-level interpretation:

- `79 00 xx`: trigger room mechanism `xx`
- `79 01 xx`: toggle room mechanism `xx`

#### Opcode `0xE1`

- Data Crystal: unnamed
- Confirmed name: `SetScreenEffectEnabled`
- Confidence: `Confirmed`

Why:

- The matched opcode dispatch table in
  [`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c`](_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c)
  maps `0xE1` directly to `func_800BB450`.
- `func_800BB450` is a tiny wrapper that just calls `func_8007DD50(arg0[1])`.
- `func_8007DD50` flips the effect runtime between active and shutdown states
  and allocates the backing effect object when needed.
- In scripts, `E1 01` and `E1 00` consistently bracket the nearby effect setup
  and tween opcodes such as `E4`, `E5`, `E6`, `E7`, and `EF`.

Current best script-level interpretation:

- `E1 00`: disable the current screen effect block
- `E1 01`: enable the current screen effect block

#### Opcode `0xE2`

- Data Crystal: unnamed
- Confirmed name: `CameraRollTween`
- Confidence: `Confirmed`

Why:

- The matched opcode dispatch table maps `0xE2` into the shared
  `vs_battle_script_setupAngleTween` handler in
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c).
- The readable handler body switches on the opcode byte and routes `0xE2` into
  `D_800F4BA4->cameraAngleTween`.
- The matched apply side later commits that tween through
  `func_8007AC94(D_800F4BA4->cameraAngleTween.currentValue)`.
- `func_8007AC94` writes `_camera.t2.unk5C`, and the current
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h)
  layout now exposes named `pitch` and `yaw` fields immediately before that
  target. The paired getter masks the stored value with `& 0xFFF`, which fits
  the remaining camera-angle slot much better than a generic scalar.
- In `decoded_scripts`, all 291 sampled `E2` instances currently end with a
  trailing `00` byte, matching the handler only consuming angle, wrap/easing,
  and duration rather than a hidden selector or id field.
- Script usage clusters around camera staging beats and repeated resets back to
  angle `0`, which matches a camera roll control instead of room or actor
  state.

Current best script-level interpretation:

- `E2 aa bb we dd 00`: tween the camera roll angle to `<h aa bb>` with
  wrap/easing control `we` over `dd` ticks

#### Opcode `0xE3`

- Data Crystal: unnamed
- Confirmed name: `ScreenEffectAngleTween`
- Confidence: `Confirmed`

Why:

- The matched opcode dispatch table maps `0xE3` into the shared
  `vs_battle_script_setupAngleTween` handler in
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c).
- The readable handler body switches on the opcode byte and routes `0xE3` into
  `D_800F4BA4->screenEffectAngleTween`, not the camera tween slot used by
  `0xE2`.
- The matched apply side later commits that tween through
  `func_8007DDAC(D_800F4BA4->screenEffectAngleTween.currentValue)`.
- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c)
  shows `func_8007DDAC` as a dedicated persistent setter for the shared
  screen-effect angle scalar `D_800F1A2C`, and the ending-menu effect setup in
  [`_refs/rood-reverse/src/MENU/MENUF.PRG/3B8.c`](_refs/rood-reverse/src/MENU/MENUF.PRG/3B8.c)
  resets that same setter alongside the shared screen-effect scale, color, and
  offset state.
- A fresh local decode of `Game Data/MAP` currently finds 4 `E3` uses, all of
  them inside the same `E1`/`E4`/`E5`/`E6` effect staging cluster.
- The strongest sample is `MAP102`, which sets `E3 30 00 10 00 00` before
  enabling the effect block, then immediately runs `E3 00 00 11 32 00` to
  tween that angle back to zero over 50 ticks. That behavior fits an effect
  angle control much better than a camera move or generic scalar.
- All 4 currently decoded `E3` instances end with a trailing `00` byte,
  matching the shared setup helper only consuming angle, wrap/easing, and
  duration rather than a hidden selector field.

Current best script-level interpretation:

- `E3 aa bb we dd 00`: tween the active screen-effect angle to `<h aa bb>` with
  wrap/easing control `we` over `dd` ticks

#### Opcode `0xE4`

- Data Crystal: unnamed
- Confirmed name: `ScreenEffectScaleTween`
- Confidence: `Confirmed`

Why:

- The matched dispatch table maps `0xE4` into the shared screen-effect helper
  family, and the matched apply side in
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c)
  sends the corresponding tween output through `func_8007DDB8`.
- `func_8007DDB8` writes the two persistent screen-effect scale components in
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c),
  and the effect reset path restores those components to neutral `0x1000`,
  `0x1000`.
- A direct non-script caller in
  [`_refs/rood-reverse/src/MENU/MENUF.PRG/3B8.c`](_refs/rood-reverse/src/MENU/MENUF.PRG/3B8.c)
  uses the same setter with values like `0x1029` and `0x107A` before enabling
  the effect runtime, which matches a scale preset rather than ids or flags.
- In decoded scripts, `E4 20 20` repeatedly lands on neutral `4096, 4096`,
  while nearby values like `1F`, `21`, and `23` make small in/out adjustments.

Current best script-level interpretation:

- `E4 xx yy ee dd`: tween the active screen effect scale on two axes

#### Opcode `0xE6`

- Data Crystal: unnamed
- Confirmed name: `ScreenEffectOffsetTween`
- Confidence: `Confirmed`

Why:

- The same matched apply path in
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c)
  routes the `0xE6` tween state through `func_8007DDF8`.
- `func_8007DDF8` stores the persistent screen-effect offset vector in
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c),
  and the effect reset path zeros that state.
- Script operands are explicitly treated as signed bytes in the local decoder
  and show up in small ranges such as `-3`, `-1`, `0`, `1`, `2`, and `4`,
  which fits an offset control much better than ids, colors, or mode flags.
- Real script sequences frequently push a small offset and then ease back to
  `0, 0`, for example in `MAP017`, `MAP026`, `MAP131`, and `MAP145`.

Current best script-level interpretation:

- `E6 xx yy ee dd`: tween the active screen effect offset on two axes

#### Opcode `0xE9`

- Data Crystal: unnamed
- Confirmed name: `RecenterCamera`
- Confidence: `Confirmed`

Why:

- The matched opcode dispatch table in
  [`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c`](_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c)
  maps `0xE9` directly to `func_800BB3BC`.
- `func_800BB3BC` converts the first script byte into either a preserved-facing
  sentinel (`0xFF -> -1`) or an 8-way facing override through `((arg0[1] + 4)
  & 7)`, converts script `0` in the second byte into a preserved-distance
  sentinel, and passes both through `func_800BC1CC`.
- `func_800BC1CC` rebuilds the target camera look-at and camera-position pair
  through `vs_battle_initialiseCameraFromSpherical`, copies those targets into
  the live camera state, and starts the camera tween helpers based on the
  transition distance.
- The matched `vs_battle_initialiseCameraFromSpherical` body in
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c)
  shows the optional override behavior clearly: `mode 1` forces distance
  `0x600`, `mode 2` forces distance `0x900`, and `-1` preserves the current
  spherical camera state.
- Real script usage matches that behavior. Most instances are the handback form
  `E9 FF 00`, used when cutscenes or first-person beats return the camera to
  normal spherical control, while rarer setup forms such as `E9 03 01`,
  `E9 04 02`, and `E9 04 00` appear where scripts want a specific facing sector
  or distance preset before the recenter.

Current best script-level interpretation:

- `E9 FF 00`: recenter the camera from the current spherical gameplay state
- `E9 xx 00`: recenter the camera and override the 8-way facing sector first
- `E9 xx 01`: recenter the camera with the short-distance (`0x600`) preset
- `E9 xx 02`: recenter the camera with the long-distance (`0x900`) preset

#### Opcode `0xEF`

- Data Crystal: unnamed
- Confirmed name: `CameraOscillationControl`
- Confidence: `Confirmed`

Why:

- Raw handler recovery in `func_800BDC9C` shows `0xEF` is not a plain one-shot
  setter. When the second script byte is zero, it immediately clears both local
  oscillation slots and returns.
- When that second byte is nonzero, the same handler allocates or reuses one of
  two small slot records, storing a phase-rate byte, an amplitude byte, a
  control word, and a duration for the slot updater to consume.
- The recovered slot updater in `func_800BE01C` feeds the first byte into the
  phase term of an `rsin` call and multiplies the second byte into the output
  amplitude, which is much stronger than the older generic `scalar0/scalar1`
  reading.
- The matched consumer in `func_800BE180` reads the low control byte as routing
  and axis-multiplier bits, then rotates the resulting short vectors into
  camera-relative offsets that are added to both `cameraLookAt` and
  `cameraPos`.
- Script usage matches the split behavior: long timed bursts like `MAP131`,
  `MAP132`, and `MAP136` set up oscillation, while repeated forms such as
  `EF 01 00 57 00 01` and `EF 50 00 47 00 01` appear at cleanup beats where a
  clear-all control makes better sense than a zero-amplitude init.

Current best script-level interpretation:

- `EF rr 00 cc CC dd`: clear both active camera oscillation slots
- `EF rr aa cc CC dd`: start or refresh a camera-relative oscillation with
  phase rate `rr`, amplitude `aa`, control word `0xCCcc`, and duration `dd`

Important detail:

- The opcode label is now strong enough to confirm the camera oscillation
  subsystem and the control/setup split, but the exact player-facing meaning of
  each high-byte waveform mode is still worth future recovery work.

### Other confirmed names worth upstreaming

These were also validated locally and are stronger than the older public table:

- `0x2E -> ModelScale`
- `0x49 -> SetJumpBackCounter`
- `0x4A -> JumpBackIfCounter`
- `0x31 -> ModelTint`
- `0x39 -> ModelLookAtPosition`
- `0x74 -> LoadRoomSection10`
- `0x75 -> WaitForRoomSection10`
- `0x76 -> FreeRoomSection10`
- `0x7C -> SetFirstPersonView`
- `0x85 -> LoadSfxSlot`
- `0x86 -> FreeSfxSlot`
- `0x88 -> SetCurrentSfx`
- `0x90 -> LoadMusicSlot`
- `0x91 -> FreeMusic`
- `0x99 -> ClearMusicLoadSlot`
- `0x9D -> LoadSoundFileById`
- `0x9E -> ProcessSoundQueue`
- `0xE2 -> CameraRollTween`
- `0xE3 -> ScreenEffectAngleTween`
- `0xE4 -> ScreenEffectScaleTween`
- `0xE5 -> ScreenEffectColorTween`
- `0xE6 -> ScreenEffectOffsetTween`
- `0xE9 -> RecenterCamera`
- `0xE7 -> SetScreenEffectMode`
- `0xEB -> CameraNearClip`
- `0xEC -> CameraFarClip`
- `0xEF -> CameraOscillationControl`
- `0xF4 -> ScriptCallSlotActive`
- `0xF5 -> ScriptCall`
- `0xF6 -> ScriptReturn`

#### Note on opcode `0x9D`

The `2` suffix is not justified anymore.

Why:

- This opcode directly tells the sound system which sound file id to load.
- A different older opcode reaches the same loader indirectly through the
  current music slot, so there really are two load styles here.
- In real scripts, `9D xx` is usually followed by `9E`, and the same `xx` often
  shows up later as the music-load slot id. That fits a direct “queue this sound
  file id” interpretation much better than a pitch control.

Current best local rename:

- `0x9D -> LoadSoundFileById`

That keeps the important distinction from the older helper-backed sound-file
loader while making it explicit that the script operand is the file id.

### Confirmed helper-level behavior

These are worth tightening locally even if the final script-friendly name should
stay a little conservative.

#### Opcodes `0x64` and `0x65`

- Confidence: `Confirmed` at helper level, `Strong` for conservative local
  tooling names, still not `Confirmed` for an upstream script-facing rename

Current narrow:

- `0x64` goes straight to `func_80091998(arg0[1])`.
- That helper resolves a room geometry entry and clears flag `0x100`.
- `0x65` goes straight to `func_800919D8(arg0[1])`.
- That helper resolves the same kind of room geometry entry and sets flag
  `0x100`.
- The same flag is also initialised from room section `12`, so this is clearly a
  room-geometry state bit rather than an actor, camera, or sound control.
- The matched section-12 helper `func_8008E224` in
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c)
  writes the same one-bit state and mirrors it into the linked geometry entry,
  which ties these opcodes to built-in room-object staging rather than an
  isolated debug flag.
- Real script usage now gives a stronger script-facing pattern than the older
  raw flag names. `0x65` clusters heavily around room-display and cutscene
  staging beats, often just before `DisplayRoom`, camera setup, or first-person
  framing, while the same geometry ids are later restored with `0x64`.
- In the current decoded room set, the same geometry ids are toggled by both
  opcodes in 39 files, including
  [`decoded_scripts/1-Wine Cellar/009-Entrance to Darkness.txt`](decoded_scripts/1-Wine%20Cellar/009-Entrance%20to%20Darkness.txt),
  [`decoded_scripts/1-Wine Cellar/013-Smokebarrel Stair.txt`](decoded_scripts/1-Wine%20Cellar/013-Smokebarrel%20Stair.txt),
  and
  [`decoded_scripts/10-The Keep/124-The Warrior's Rest.txt`](decoded_scripts/10-The%20Keep/124-The%20Warrior's%20Rest.txt).
- A broad script scan currently finds `0x65` within six lines of
  `DisplayRoom` 611 times, versus 47 for `0x64`, which fits a temporary
  suppression/setup role better than a permanent state write.

Best safe local names for tooling:

- `0x64 -> RestoreRoomGeometry`
- `0x65 -> SuppressRoomGeometry`

Why this wording stays conservative:

- The exact render or collision consumer behind geometry flag `0x100` still
  needs one more decomp pass.
- That means a harder claim like `ShowRoomGeometry`/`HideRoomGeometry` could
  still be slightly too specific.
- `Restore`/`Suppress` captures the proven script pattern without pretending the
  remaining implementation details are fully locked down.

### Still tentative

These are narrowed down, but should not be hard-renamed upstream without one
more proof pass:

- `0x7A`
- `0xED`

#### Opcode `0x7A`

- Confidence: `Strong`

Current narrow:

- The matched opcode dispatch table routes `0x7A` directly to the readable
  handler body now named
  [`vs_battle_script_setRoomAmbientSoundSuspended`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c).
- When the script byte is nonzero, that handler latches a local "suspended"
  state and, if `func_8008E470()` passes, grabs the current ambient sound id
  through `func_800913BC(-1)` and clears playback by swapping in `-1`.
- When the script byte returns to zero, the same handler restores the saved
  ambient sound id through `func_800913BC(savedId)` and clears the latched
  suspended state.
- The sound helper in
  [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/2842C.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/2842C.c)
  confirms `func_800913BC` is the persistent ambient-id swap path.
- Real script usage still matches the user-facing idea: decoded rooms such as
  `MAP138`, `MAP062`, `MAP001`, and `MAP006` use `7A 01` near cutscene
  takeover beats and `7A 00` when normal room behavior is restored.

Best safe local tooling name:

- `SetRoomAmbientSoundSuspended`

Current best script-level interpretation:

- `7A 01`: suspend the current room ambient sound, saving the previous id when
  this room uses the persistent ambient-id path
- `7A 00`: restore that saved ambient sound id when the same path is active

Why still not confirmed:

- The save/restore behavior proven so far is scoped to the persistent
  ambient-id path behind `func_800913BC`.
- The room audio code also has a separate AKAO-backed `section14` path, and the
  opcode handler gates its swap/restore work through `func_8008E470()`.
- That means the shared user-facing effect is strongly suggested, but the
  current proof does not yet justify a broad unconditional confirmed rename.

#### Opcode `0xED`

- Confidence: `Strong`

Current narrow:

- This opcode, not `0xEF`, is the direct path that feeds
  `vs_screff2_setParamPair(param0, param1)` in `SCREFF2.PRG`.
- The first script byte is promoted with `<< 6` before entering the SCREFF2
  setter, which proves it is a 12-bit fixed-point parameter rather than a
  plain flag or id byte.
- A fresh full decode of `Game Data/MAP` finds 10 currently reachable script
  uses across 4 rooms. Every one of those rooms resets with `ED 40 00 00 00`,
  i.e. `0x40 << 6 = 4096`, while the other observed first-parameter values
  stay nearby at `3712`, `4672`, `4928`, `5056`, and `5120`.
- The second script byte is treated as a signed byte, and the last two bytes
  behave like easing and duration.
- That makes it a two-parameter effect tween rather than general logic flow.

Best safe local tooling name:

- `ScreenEffectParamPairTween`

Best safe local tooling rendering:

- `param0Fixed12=<byte << 6>` with `4096` as the currently proven neutral/reset
  value
- `param1Signed=<s8>`

Why still tentative:

- The two destination fields in `SCREFF2` are still unnamed, so the exact
  player-visible feature behind the pair has not been nailed down yet.
- The first field is narrow enough to treat as a fixed-point parameter with a
  stable neutral/reset form, but the current evidence still does not prove the
  exact visual meaning of either destination field.

### Suggested upstream patch shape

Keep the contribution in small pieces:

1. Add comments around the matched handlers in `4A0A8.c` and `146C.c`.
2. Rename script-decoder mnemonics in local tooling and include evidence in PR
   text.
3. Keep speculative opcodes out of the first PR.
