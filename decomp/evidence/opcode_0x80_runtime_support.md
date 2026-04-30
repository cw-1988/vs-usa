# opcode 0x80 Runtime Observation Support Note

## Scope

- Generated from `Pass 3 - Copy/patch reconciliation` on `2026-04-30 23:29:02Z`.
- Observation source: `decomp/evidence/opcode_0x80_runtime_observation.json`
- Baseline export: `decomp/evidence/inittbl_opcode_table.json`
- Runtime table address: `0x800F4C28`
- Reconstructed baseline blob: `decomp/evidence/opcode_0x80_runtime_expected_table.bin` (size `1024` bytes, sha256 `bf98e99d441e94b8bf4d421b59c5994c74b254adbd7736bede778ae0d905b844`)

## Snapshot Comparison

- Missing snapshot file for `after_init`: `decomp/evidence/opcode_0x80_runtime_after_init.bin` (Immediately after the INITBTL copy into 0x800F4C28)
- Missing snapshot file for `pre_dispatch`: `decomp/evidence/opcode_0x80_runtime_pre_dispatch.bin` (Late runtime state before any candidate 0x80-0x82 dispatch)

## Focus Opcode Summary

- No focus-opcode comparison rows were available.

## Planned Breakpoints

- `exec` breakpoint at `0x800BFBB8`: Recovered live runtime table reader
- `exec` breakpoint at `0x800B66E4`: Static stub target for 0x80-0x82
- `exec` breakpoint at `0x800BA2E0`: Competing sound-family candidate
- `write` breakpoint at `0x800F4C28-0x800F5027`: Detect post-init runtime rewrites of the copied table

## Breakpoint Hits

- No breakpoint hits were recorded in the observation JSON yet.

## Table Mutations

- No table mutation observations were recorded yet.

## Dispatch Observations

- No dispatch observations were recorded yet.

## Notes

- Automated PCSX-Redux cold-boot disc run against 'Game Data/Vagrant Story (USA).cue' reached startup Lua and produced decomp/evidence/opcode_0x80_runtime_automation_summary.json, but timed out before 0x800BFBB8. The filtered run recorded reader_hits=0, write_hits=0, ignored_pre_runtime_writes=256 from pc 0x00000600, and no valid after_init/pre_dispatch snapshots. (`2026-04-30T21:44:58Z`)
- Automated PCSX-Redux capture used input plan 'C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_input_plan.json'; prepared_path=C:\Users\Chris\Desktop\vs usa\.codex_tmp\pcsx-redux\opcode_0x80_input_plan-46ff105abb8c493798c4fdf06ede421e.tsv; pad=1/1; steps=6/6; description=Starter cold-boot fallback for Vagrant Story (USA) when no near-battle savestate is available. Tune the frame waits after the first real run; this scaffold is intentionally conservative and assumes memcard-backed menu resume. (`2026-04-30T22:56:27Z`)
- Automated PCSX-Redux capture summary; process_exit=0; summary_exit=2; frames=2710; write_hits=0; reader_hits=0; summary_json=C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_automation_summary.json (`2026-04-30T22:56:27Z`)
- Automated PCSX-Redux capture used input plan 'C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_input_plan.json'; prepared_path=C:\Users\Chris\Desktop\vs usa\.codex_tmp\pcsx-redux\opcode_0x80_input_plan-8a821277aa834c31b3b5dff10fa51bf9.tsv; pad=1/1; steps=6/6; description=Starter cold-boot fallback for Vagrant Story (USA) when no near-battle savestate is available. The wrapper now auto-extends timeout to cover the full plan plus slack; the current memcard-backed route completes all six scheduled steps but still does not reach the recovered runtime reader, so future edits should retune the route or menu assumptions rather than only adding more wait frames. (`2026-04-30T23:07:29Z`)
- Automated PCSX-Redux capture wrote 7 screen capture(s) under C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_frames. (`2026-04-30T23:07:29Z`)
- Automated PCSX-Redux capture summary; process_exit=0; summary_exit=2; frames=2710; write_hits=0; reader_hits=0; summary_json=C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_automation_summary.json (`2026-04-30T23:07:30Z`)
- Repo-local memcard probe now reports memcard1.mcd and memcard2.mcd as blank formatted cards (131072 bytes, 186 nonzero bytes each, highest nonzero offset 0x1FFF, no Vagrant Story title-id ASCII matches). The checked-in cold-boot route therefore should not assume a save-backed Continue/Load path unless a populated card artifact is added. (`2026-04-30T23:09:51Z`)
- Automated PCSX-Redux capture used input plan 'C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_input_plan.json'; prepared_path=C:\Users\Chris\Desktop\vs usa\.codex_tmp\pcsx-redux\opcode_0x80_input_plan-d1232c6fd0ab4b01969804d0cf2ce3b9.tsv; pad=1/1; steps=7/7; description=Starter cold-boot fallback for Vagrant Story (USA) when no near-battle savestate is available. The wrapper now auto-extends timeout to cover the full plan plus slack and can leave screen-capture breadcrumbs. Operator feedback indicates the earlier black screen corresponded to an intro video that needs a START skip, so this scaffold now front-loads repeated START presses before the old menu-confirm path. The repo-local memcards still probe as blank formatted cards, so future edits should replace the save-backed Continue/Load assumption or pair the route with a populated card artifact rather than only adding more wait frames. (`2026-04-30T23:12:01Z`)
- Automated PCSX-Redux capture wrote 8 screen capture(s) under C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_frames. (`2026-04-30T23:12:01Z`)
- Automated PCSX-Redux capture summary; process_exit=0; summary_exit=2; frames=2332; write_hits=0; reader_hits=0; summary_json=C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_automation_summary.json (`2026-04-30T23:12:01Z`)
- Automated PCSX-Redux capture used input plan 'C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_input_plan.json'; prepared_path=C:\Users\Chris\Desktop\vs usa\.codex_tmp\pcsx-redux\opcode_0x80_input_plan-d6393748382c4b869a5f5e98630733c5.tsv; pad=1/1; steps=9/9; description=Starter cold-boot fallback for Vagrant Story (USA) when no near-battle savestate is available. The wrapper now auto-extends timeout to cover the full plan plus slack and can leave screen-capture breadcrumbs. Latest visual checkpoints show the old menu inputs were still landing on publisher, Squaresoft, and opening-FMV screens, so this scaffold now keeps pulsing START through the intro chain before it attempts menu navigation. The repo-local memcards still probe as blank formatted cards, so future edits should replace the save-backed Continue/Load assumption or pair the route with a populated card artifact rather than only adding more wait frames. (`2026-04-30T23:14:12Z`)
- Automated PCSX-Redux capture wrote 10 screen capture(s) under C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_frames. (`2026-04-30T23:14:12Z`)
- Automated PCSX-Redux capture summary; process_exit=0; summary_exit=2; frames=2714; write_hits=0; reader_hits=0; summary_json=C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_automation_summary.json (`2026-04-30T23:14:12Z`)
- Automated PCSX-Redux capture used input plan 'C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_input_plan.json'; prepared_path=C:\Users\Chris\Desktop\vs usa\.codex_tmp\pcsx-redux\opcode_0x80_input_plan-6cadf0fb5a4f42f89e0d494c8f882973.tsv; pad=1/1; steps=10/10; description=Starter cold-boot fallback for Vagrant Story (USA) when no near-battle savestate is available. The wrapper now auto-extends timeout to cover the full plan plus slack and can leave screen-capture breadcrumbs. Latest visual checkpoints show the repeated START pulses can now reach the Vagrant Story title/logo, so this scaffold pauses menu navigation until after that title state and only then tries to open and drive the menu. The repo-local memcards still probe as blank formatted cards, so future edits should replace the save-backed Continue/Load assumption or pair the route with a populated card artifact rather than only adding more wait frames. (`2026-04-30T23:16:04Z`)
- Automated PCSX-Redux capture wrote 11 screen capture(s) under C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_frames. (`2026-04-30T23:16:05Z`)
- Automated PCSX-Redux capture summary; process_exit=0; summary_exit=2; frames=2962; write_hits=0; reader_hits=0; summary_json=C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_automation_summary.json (`2026-04-30T23:16:05Z`)
- Automated PCSX-Redux capture used input plan 'C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_input_plan.json'; prepared_path=C:\Users\Chris\Desktop\vs usa\.codex_tmp\pcsx-redux\opcode_0x80_input_plan-a46e8f17640d40f58fe003f10ef4eb1d.tsv; pad=1/1; steps=10/10; description=Starter cold-boot fallback for Vagrant Story (USA) when no near-battle savestate is available. The wrapper now auto-extends timeout to cover the full plan plus slack and can leave screen-capture breadcrumbs. Latest visual checkpoints show the repeated START pulses can now reach the Vagrant Story title/logo, so this scaffold pauses menu navigation until after that title state and only then tries to open and drive the menu. Operator follow-up also confirmed that this build uses PSX-style menu mapping where X cancels and O confirms, so the menu-confirm steps now use CIRCLE instead of CROSS. The repo-local memcards still probe as blank formatted cards, so future edits should replace the save-backed Continue/Load assumption or pair the route with a populated card artifact rather than only adding more wait frames. (`2026-04-30T23:17:34Z`)
- Automated PCSX-Redux capture wrote 11 screen capture(s) under C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_frames. (`2026-04-30T23:17:34Z`)
- Automated PCSX-Redux capture summary; process_exit=0; summary_exit=2; frames=2962; write_hits=0; reader_hits=0; summary_json=C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_automation_summary.json (`2026-04-30T23:17:34Z`)
- Updated cold-boot route now reaches the Vagrant Story title menu under the corrected PSX-style button mapping (X cancel, O confirm). Screen captures show step-08 on the title menu with Continue highlighted and step-10 on the Load / Memory Card slot 1 screen, but the run still records no runtime-table reader hit, no table-write hit, and no snapshots because the repo-local cards do not yet provide a usable path into live gameplay. (`2026-04-30T23:18:23Z`)
- Automated PCSX-Redux capture used input plan 'C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_input_plan.json'; prepared_path=C:\Users\Chris\Desktop\vs usa\.codex_tmp\pcsx-redux\opcode_0x80_input_plan-fac1eda172b8471587bf7d77ded020c0.tsv; pad=1/1; steps=10/10; description=Starter cold-boot fallback for Vagrant Story (USA) when no near-battle savestate is available. The wrapper now auto-extends timeout to cover the full plan plus slack and can leave screen-capture breadcrumbs. Latest visual checkpoints show the repeated START pulses can now reach the Vagrant Story title/logo, so this scaffold pauses menu navigation until after that title state and only then tries to open and drive the menu. Operator follow-up also confirmed that this build uses PSX-style menu mapping where X cancels and O confirms, so the menu-confirm steps now use CIRCLE instead of CROSS. The repo-local memcards still probe as blank formatted cards, so this revision drops the old Continue/Load branch and instead follows a title-menu New Game route: press CIRCLE on the default entry, wait roughly ten seconds, then press START twice with another ten-second gap to skip toward live player control. (`2026-04-30T23:29:01Z`)
- Automated PCSX-Redux capture wrote 11 screen capture(s) under C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_frames. (`2026-04-30T23:29:01Z`)
- Automated PCSX-Redux capture summary; process_exit=0; summary_exit=2; frames=4380; write_hits=0; reader_hits=0; summary_json=C:\Users\Chris\Desktop\vs usa\decomp\evidence\opcode_0x80_runtime_automation_summary.json (`2026-04-30T23:29:01Z`)

## Conclusion

Runtime observation packet is not finalized yet: no listed snapshot files were available for comparison.
