# Vagrant Story Opcode Behavior Reference

This reference mirrors the currently named entries in
[`dump_mpd_script.py`](dump_mpd_script.py).
It is meant as a quick lookup table, not a replacement for the longer
evidence notes in
[`ROOD_REVERSE_OPCODE_CONCLUSIONS.md`](ROOD_REVERSE_OPCODE_CONCLUSIONS.md).

- named locally: `85 / 256` opcode slots
- still placeholder-named: `171 / 256` opcode slots
- table below includes only the currently named entries; unresolved `OpcodeXX`
  slots are listed after it

| Opcode | Current name / behavior | Parameters (type) | Size | Short description |
| --- | --- | --- | --- | --- |
| `0x00` | `nop` | `none` | `0x01` | No-op placeholder; consumes one byte. |
| `0x10` | `DialogShow` | `idDlg: u8, style: u8, x: u8, unk0: u8, y: u8, w: u8, h: u8, raw: u8[3]` | `0x0B` | Dialog-system control. |
| `0x11` | `DialogText` | `idDlg: u8, idText: u8, raw: u8` | `0x04` | Dialog-system control. |
| `0x12` | `DialogHide` | `idDlg: u8` | `0x02` | Dialog-system control. |
| `0x16` | `SplashScreenChoose` | `raw: u8[3]` | `0x04` | Splash-screen or overlay control. |
| `0x17` | `SplashScreenLoad` | `raw: u8[5]` | `0x06` | Splash-screen or overlay control. |
| `0x18` | `SplashScreenShow` | `raw: u8[6]` | `0x07` | Splash-screen or overlay control. |
| `0x19` | `SplashScreenHide` | `none` | `0x01` | Splash-screen or overlay control. |
| `0x1A` | `SplashScreenFadeIn` | `none` | `0x01` | Splash-screen or overlay control. |
| `0x20` | `ModelLoad` | `idChr: u8, unk1: u8, idSHP: u8, raw: u8[5]` | `0x09` | Model or actor staging command. |
| `0x22` | `ModelAnimate` | `idChr: u8, unk1: u8, idAnim: u8, raw: u8[2]` | `0x06` | Model or actor staging command. |
| `0x23` | `ModelSetAnimations` | `raw: u8[4]` | `0x05` | Model or actor staging command. |
| `0x24` | `ActorSfxPanVolumeControl` | `idChr: u8, unk1: u8, mode: u8, pan: u8, volume: u8, duration: u8` | `0x07` | Actor-local sound panning and volume override control. |
| `0x26` | `ModelPosition` | `idChr: u8, unk1: u8, posX: i16, posY: i16, posZ: i16, rx: u8, raw: u8[2]` | `0x0C` | Model or actor staging command. |
| `0x28` | `ModelMoveTo` | `idChr: u8, x: i32, y: i32` | `0x0A` | Model or actor staging command. |
| `0x29` | `ModelMoveTo2` | `raw: u8[6]` | `0x07` | Model or actor staging command. |
| `0x2E` | `ModelScale` | `raw: u8[9]` | `0x0A` | Model or actor staging command. |
| `0x2F` | `ModeFree` | `mode: u8, raw: u8` | `0x03` | Switch engine or script mode using a small control byte. |
| `0x30` | `ModelLoadAnimationsEx` | `raw: u8[5]` | `0x06` | Model or actor staging command. |
| `0x31` | `ModelTint` | `raw: u8[5]` | `0x06` | Model or actor staging command. |
| `0x33` | `ModelRotate` | `raw: u8[10]` | `0x0B` | Model or actor staging command. |
| `0x38` | `ModelLookAt` | `raw: u8[5]` | `0x06` | Model or actor staging command. |
| `0x39` | `ModelLookAtPosition` | `raw: u8[9]` | `0x0A` | Model or actor staging command. |
| `0x3A` | `ModelLoadAnimations` | `raw: u8[3]` | `0x04` | Model or actor staging command. |
| `0x3B` | `WaitForFile` | `none` | `0x01` | Pause until an earlier async file load completes. |
| `0x3E` | `ModelIlluminate` | `raw: u8[9]` | `0x0A` | Model or actor staging command. |
| `0x40` | `JumpFwdIfFlag` | `flagModeHi: u8, flagLo: u8, compareValue: u8, jumpOffset: u16` | `0x06` | Script flow-control jump helper. |
| `0x42` | `ModelControlViaScript` | `raw: u8[2]` | `0x03` | Model or actor staging command. |
| `0x44` | `SetEngineMode` | `idMode: u8` | `0x02` | Set a global engine mode byte used by script flow. |
| `0x49` | `SetJumpBackCounter` | `counterSlot: u8, initialCount: u8` | `0x03` | Initialize a counter slot later consumed by the jump-back opcode. |
| `0x4A` | `JumpBackIfCounter` | `counterSlot: u8, jumpOffsetBack: u16` | `0x04` | Script flow-control jump helper. |
| `0x50` | `ModelControlViaBattleMode` | `raw: u8[3]` | `0x04` | Model or actor staging command. |
| `0x54` | `BattleOver` | `raw: u8[3]` | `0x04` | Battle-end control path used by battle-scripted scenes. |
| `0x58` | `SetHeadsUpDisplayMode` | `idMode: u8` | `0x02` | HUD visibility or mode control. |
| `0x64` | `RestoreRoomGeometry` | `idGeometry: u8` | `0x02` | Room loading, room display, or room-state control. |
| `0x65` | `SuppressRoomGeometry` | `idGeometry: u8` | `0x02` | Room loading, room display, or room-state control. |
| `0x68` | `LoadRoom` | `idZone: u8, idRoom: u8, raw: u8[7]` | `0x0A` | Room loading, room display, or room-state control. |
| `0x69` | `LoadScene` | `raw: u8[3]` | `0x04` | Scene-loading control. |
| `0x6D` | `DisplayRoom` | `raw: u8` | `0x02` | Room loading, room display, or room-state control. |
| `0x70` | `ModelColor` | `raw: u8[7]` | `0x08` | Model or actor staging command. |
| `0x74` | `LoadRoomSection10` | `raw: u8` | `0x02` | Room loading, room display, or room-state control. |
| `0x75` | `WaitForRoomSection10` | `none` | `0x01` | Room loading, room display, or room-state control. |
| `0x76` | `FreeRoomSection10` | `none` | `0x01` | Room loading, room display, or room-state control. |
| `0x78` | `EnableRoomMechanismUpdates` | `enabledRaw: u8` | `0x02` | Room mechanism update enable/disable control. |
| `0x79` | `RoomMechanismControl` | `action: u8, idMechanism: u8` | `0x03` | Trigger or toggle a room mechanism by id. |
| `0x7A` | `SetRoomAmbientSoundSuspended` | `suspended: u8` | `0x02` | Suspend or restore room ambient playback on the proven persistent-ambient path. |
| `0x7C` | `SetFirstPersonView` | `raw: u8` | `0x02` | Toggle or stage first-person camera/view mode. |
| `0x80` | `SoundEffects0` | `raw: u8[4]` | `0x05` | Tentative sound-family placeholder; direct dispatch and nearby handler evidence still disagree. |
| `0x85` | `LoadSfxSlot` | `slot: u8, idSfx: u8` | `0x03` | Audio resource or playback control. |
| `0x86` | `FreeSfxSlot` | `slot: u8` | `0x02` | Audio resource or playback control. |
| `0x88` | `SetCurrentSfx` | `idSfx: u8` | `0x02` | Audio resource or playback control. |
| `0x90` | `LoadMusicSlot` | `slot: u8, raw: u8` | `0x03` | Audio resource or playback control. |
| `0x91` | `FreeMusic` | `slot: u8` | `0x02` | Audio resource or playback control. |
| `0x92` | `MusicPlay` | `raw: u8[3]` | `0x04` | Audio resource or playback control. |
| `0x99` | `ClearMusicLoadSlot` | `slot: u8` | `0x02` | Audio resource or playback control. |
| `0x9D` | `LoadSoundFileById` | `idFile: u8` | `0x02` | Audio resource or playback control. |
| `0x9E` | `ProcessSoundQueue` | `none` | `0x01` | Flush or process queued sound work after load/setup commands. |
| `0xA1` | `SplashScreenEffects` | `mode: u8` | `0x02` | Apply a mode or effect toggle for the splash-screen subsystem. |
| `0xA2` | `CameraZoomIn` | `raw: u8` | `0x02` | Immediate small camera zoom helper; distinct from the timed `CameraZoom` opcode. |
| `0xC0` | `CameraDirection` | `raw: u8[6]` | `0x07` | Camera positioning, clipping, zoom, or tween control. |
| `0xC1` | `CameraSetAngle` | `none` | `0x01` | Camera positioning, clipping, zoom, or tween control. |
| `0xC2` | `CameraLookAt` | `raw: u8[2]` | `0x03` | Camera positioning, clipping, zoom, or tween control. |
| `0xC4` | `ModelAnimateObject` | `raw: u8[3]` | `0x04` | Model or actor staging command. |
| `0xD0` | `CameraPosition` | `raw: u8[6]` | `0x07` | Camera positioning, clipping, zoom, or tween control. |
| `0xD1` | `SetCameraPosition` | `none` | `0x01` | Camera positioning, clipping, zoom, or tween control. |
| `0xD4` | `CameraHeight` | `raw: u8[3]` | `0x04` | Camera positioning, clipping, zoom, or tween control. |
| `0xE0` | `CameraWait` | `raw: u8` | `0x02` | Block until active camera motion or tween work finishes. |
| `0xE1` | `SetScreenEffectEnabled` | `enabled: u8` | `0x02` | Shared screen-effect runtime control or tween setup. |
| `0xE2` | `CameraRollTween` | `angle: i16, wrapEasing: u8, duration: u8, reserved: u8` | `0x06` | Tween the camera roll angle. |
| `0xE3` | `ScreenEffectAngleTween` | `angle: i16, wrapEasing: u8, duration: u8, reserved: u8` | `0x06` | Tween the shared screen-effect angle. |
| `0xE4` | `ScreenEffectScaleTween` | `xScaleRaw: u8, yScaleRaw: u8, easing: u8, duration: u8` | `0x05` | Tween the shared screen-effect scale. |
| `0xE5` | `ScreenEffectColorTween` | `r: u8, g: u8, b: u8, easing: u8, duration: u8` | `0x06` | Tween the shared screen-effect color pair. |
| `0xE6` | `ScreenEffectOffsetTween` | `x: i8, y: i8, easing: u8, duration: u8` | `0x05` | Tween the shared screen-effect offset pair. |
| `0xE7` | `SetScreenEffectMode` | `mode: u8` | `0x02` | Set the current shared screen-effect mode. |
| `0xE9` | `RecenterCamera` | `facingSectorRaw: u8, distancePreset: u8` | `0x03` | Recenter the gameplay camera, optionally overriding facing or distance preset. |
| `0xEA` | `CameraZoom` | `projectionDistanceRaw: u8, easing: u8, duration: u8` | `0x04` | Timed camera zoom control. |
| `0xEB` | `CameraNearClip` | `nearClipRaw: u8, easing: u8, duration: u8` | `0x04` | Adjust the camera near clipping plane. |
| `0xEC` | `CameraFarClip` | `farClipRaw: u8, easing: u8, duration: u8` | `0x04` | Adjust the camera far clipping plane. |
| `0xED` | `ScreenEffectParamPairTween` | `param0Raw: u8, param1Signed: i8, easing: u8, duration: u8` | `0x05` | Tween a still-unnamed screen-effect parameter pair. |
| `0xEF` | `CameraOscillationControl` | `phaseRate: u8, amplitude: u8, controlWord: u16, duration: u8` | `0x06` | Start, refresh, or clear camera-relative oscillation slots. |
| `0xF0` | `Wait` | `frames: u8` | `0x02` | Delay script execution for the encoded tick count. |
| `0xF4` | `ScriptCallSlotActive` | `slot: u8` | `0x02` | Check or mark a script-call slot before sub-script dispatch. |
| `0xF5` | `ScriptCall` | `targetA: u8, targetB: u8, targetC: u8` | `0x04` | Call another script entry using the encoded target bytes. |
| `0xF6` | `ScriptReturn` | `slot: u8` | `0x02` | Return from a prior `ScriptCall` frame. |
| `0xFF` | `return` | `none` | `0x01` | End the current script block and return to caller flow. |

## Still Missing

These opcode slots still only have placeholder names in the local decoder:

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
