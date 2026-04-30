## Vagrant Story Script Opcode Conclusions

This note collects high-confidence opcode conclusions that appear to improve on the
current public table at Data Crystal:

- Source: <https://datacrystal.tcrf.net/wiki/Vagrant_Story/Script_Opcodes>

The goal is to keep this contribution set conservative: only names with a clear
code-path or script-usage proof are listed as confirmed. Anything still fuzzy
should stay tentative in upstream comments and PR text.

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

### Other confirmed names worth upstreaming

These were also validated locally and are stronger than the older public table:

- `0x2E -> ModelScale`
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
- `0xE4 -> ScreenEffectScaleTween`
- `0xE5 -> ScreenEffectColorTween`
- `0xE6 -> ScreenEffectOffsetTween`
- `0xE7 -> SetScreenEffectMode`
- `0xEB -> CameraNearClip`
- `0xEC -> CameraFarClip`
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

- Confidence: `Confirmed` at helper level, `Tentative` at script-friendly level

Current narrow:

- `0x64` goes straight to `func_80091998(arg0[1])`.
- That helper resolves a room geometry entry and clears flag `0x100`.
- `0x65` goes straight to `func_800919D8(arg0[1])`.
- That helper resolves the same kind of room geometry entry and sets flag
  `0x100`.
- The same flag is also initialised from room section `12`, so this is clearly a
  room-geometry state bit rather than an actor, camera, or sound control.

Best safe local names for tooling:

- `0x64 -> ClearRoomGeometryFlag100`
- `0x65 -> SetRoomGeometryFlag100`

Why not use show/hide yet:

- The exact gameplay meaning of geometry flag `0x100` still needs one more pass
  through the geometry consumers.
- That means older guesses like `0x64 = enable/show` and `0x65 = disable/hide`
  are still too aggressive.
- What is actually proven right now is the polarity of the bit operation:
  `0x64` clears the flag and `0x65` sets it.

### Still tentative

These are narrowed down, but should not be hard-renamed upstream without one
more proof pass:

- `0x7A`
- `0xE3`
- `0xED`
- `0xEF`

#### Opcode `0x7A`

- Confidence: `Strong`

Current narrow:

- It is part of the room audio subsystem, not a generic visual toggle.
- `vs_battle_roomData.section14` is the room `AKAO` section in the room header
  struct, so this handler is explicitly tied to room sound data.
- When `7A 01` succeeds, it saves the current persistent room ambient sound id
  and clears it via `func_800913BC(-1)`.
- When `7A 00` runs later, it restores that saved ambient sound id.
- In scripts it commonly brackets cutscene takeover and cleanup. `MAP001`,
  `MAP006`, `MAP062`, and `MAP138` are good local examples.

Best interpretation so far:

- `SuspendRoomAmbientSound`

Best safe local tooling name:

- `SetRoomAmbientSoundSuspended`

Why still tentative:

- Rooms with an actual AKAO section and rooms that fall back to the persistent
  ambient-sfx path do not behave through the exact same implementation path.
- So the subsystem identity is strong, but the final upstream name should still
  describe the shared user-facing effect rather than overfit one implementation
  detail.

#### Opcode `0xE3`

- Confidence: `Strong`

Current narrow:

- It uses the same tween machinery as `0xE2`, but writes to a different target.
- In scripts it lives much closer to the visual-effect block than to normal
  camera positioning commands.
- Nearby matched effect update code shows a separate cluster that pushes timed
  values into screen-effect state, color state, and `SCREFF2` parameters.
- All 6 currently decoded `E3` instances also end with a trailing `00` byte,
  matching the shared setup helper only using angle, wrap/easing, and duration.
- That makes it look like an effect-side angle control, not a basic camera
  move opcode.

Best interpretation so far:

- `ScreenEffectAngleTween`

Why still tentative:

- The consumer of `D_800F1A2C` is still hidden behind nonmatching code, so the
  user-facing feature name is not nailed down.

#### Opcode `0xED`

- Confidence: `Strong`

Current narrow:

- This opcode, not `0xEF`, is the direct path that feeds
  `func_800F9BC0(arg0, arg1)` in `SCREFF2.PRG`.
- The first script byte is promoted with `<< 6`, the second is treated as a
  signed byte, and the last two bytes behave like easing and duration.
- That makes it a two-parameter effect tween rather than general logic flow.

Best safe local tooling name:

- `ScreenEffectParamPairTween`

Why still tentative:

- The two destination fields in `SCREFF2` are still unnamed, so the exact
  player-visible feature behind the pair has not been nailed down yet.

#### Opcode `0xEF`

- Confidence: `Strong`

Current narrow:

- It behaves like part of the same visual-effect cluster as the nearby `E`-range
  opcodes, but its consumer path is camera-side rather than `SCREFF2`-side.
- Raw handler work now shows that `0xEF` allocates or reuses one of two small
  waveform slots that are advanced by `func_800BE180`.
- The recovered updater logic in `func_800BE01C` shows those slots evaluating a
  sine-driven oscillation over a bounded duration instead of writing one direct
  target value.
- The active slot outputs are then converted from short vectors into
  camera-relative offsets and added to both `cameraLookAt` and `cameraPos` in
  the main effect update path.
- In scripts it shows up in short timed bursts around zoom, effect, and camera
  staging beats, which fits transient camera oscillation much better than logic
  flow or a generic scalar setter.

Best interpretation so far:

- It initializes camera-relative oscillation state rather than a plain screen
  parameter.

Best safe local tooling name:

- `CameraOscillationInit`

Why still not upstream-safe:

- The exact control-word bit layout still needs handler recovery, especially the
  pieces that choose slot, routing, and envelope behavior.
- The final player-facing label may still deserve a more specific term such as
  shake, wobble, or pulse once the remaining nonmatching code is recovered.

Observed local argument patterns worth carrying forward:

- The last byte behaves like a duration input and commonly matches the timing
  rhythm of nearby waits or cutscene beats.
- The middle word behaves like a reusable control word more than a plain scalar.
  Common local values include `0x0047`, `0x0057`, `0x005B`, `0x0065`,
  `0x0067`, `0x0097`, and `0x01A7`.
- The first two bytes behave like small scalar parameters. They are often
  pulsed in alternating pairs or stepped sequences rather than treated as ids.
  The local decoder still renders them conservatively as `scalar0` and
  `scalar1` to preserve that structure without overclaiming their final role.

Useful script examples:

- `MAP223`: `EF 08 08 66 00 06`, `EF 08 04 66 00 06`,
  `EF 08 02 66 00 06`, `EF 08 01 66 00 06`
  This looks like a stepped scalar sweep while the control word stays fixed at
  `0x0066`.
- `MAP069`: `EF 01 32 67 00 07`, `EF 02 32 5B 00 07`,
  `EF 02 19 67 00 07`, `EF 04 17 5B 00 07`
  This looks like alternating paired setup rather than a one-shot direct field
  write.
- `MAP131` to `MAP136`: repeated pairs such as `0x0193` and `0x019B`
  reinforce the idea that the 16-bit word is a reusable effect-control input.
- `MAP136`: `EF 05 0E 9B 00 08`, `EF 05 0E 93 00 08`, and
  `EF 34 06 93 00 78`
  These runs fit the recovered oscillation model well: the control word changes
  while the scalar pair can stay fixed, and long-duration setups favour a
  `frequency plus amplitude` style reading over a one-shot direct write.

### Suggested upstream patch shape

Keep the contribution in small pieces:

1. Add comments around the matched handlers in `4A0A8.c` and `146C.c`.
2. Rename script-decoder mnemonics in local tooling and include evidence in PR
   text.
3. Keep speculative opcodes out of the first PR.
