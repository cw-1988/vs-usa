# Opcode `0x80` Bat-Kill Negative Runtime Control

Input artifact:

- [`opcode_0x80_runtime_input_plan_bat_kill.json`](opcode_0x80_runtime_input_plan_bat_kill.json)

Primary run:

- summary: [`opcode_0x80_runtime_automation_summary.json`](opcode_0x80_runtime_automation_summary.json)
- observation packet: [`opcode_0x80_runtime_observation.json`](opcode_0x80_runtime_observation.json)
- support log: [`opcode_0x80_runtime_support.md`](opcode_0x80_runtime_support.md)
- frame captures: [`opcode_0x80_runtime_frames`](opcode_0x80_runtime_frames)

Run facts from the latest preserved cold-boot pass:

- started `2026-05-01T00:50:05Z`
- finished `2026-05-01T00:51:26Z`
- `frame_count = 4886`
- `reader_hit_count = 0`
- `write_hit_count = 0`
- `candidate_hit_count = 0`
- no `after_init` or `pre_dispatch` snapshots

Observed route:

- cold boot reaches `New Game`
- two delayed `START` skips hand off to player control
- three `R1` taps rotate the camera toward the adjacent room
- held `UP` movement enters the next room
- three `CIRCLE` taps unsheathe, open the attack sphere, and attack

Why this matters:

- This is now a durable negative-control run for the active `0x80` runtime
  contradiction.
- It proves that early live gameplay, room transition, weapon unsheathe,
  attack-sphere open, and the first bat attack are still insufficient to trip
  the watched `0x800BFBB8` reader or the tracked table-write range.
- Future runtime passes should stop treating "gain control after the second
  intro skip" as a likely enough trigger by itself.

Recommended next move:

- keep this route as a regression/control path
- pivot the runtime tooling toward broader copied-table reader discovery or a
  nearer savestate for the exact cutscene/script moment under dispute
