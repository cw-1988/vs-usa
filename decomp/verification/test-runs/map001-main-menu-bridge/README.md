# MAP001 Main-Menu Bridge

This run folder preserves a two-pass `PCSX-Redux` handoff for the retail
`MAP001` intro route:

- `input-plan-01_create_init_main_menu.json`: cold-boots to the title menu,
  stops before `New Game`, and creates `save-states/init-main-menu.savestate`
- `input-plan-02_resume_map001_intro.json`: loads that savestate and continues
  the stripped `MAP001` listener-control route from `New Game`

Layout:

- `save-states/`: checked-in or newly created savestates for this run family
- `artifacts/`: wrapper-managed snapshots, summaries, and screenshots created
  during execution

Suggested wrapper shape:

```powershell
pwsh -File decomp/verification/run_opcode_0x80_runtime_capture.ps1 `
  -IsoPath "Game Data/Vagrant Story (USA).cue" `
  -RunDirectory "decomp/verification/test-runs/map001-main-menu-bridge" `
  -InputPlanPath "decomp/verification/test-runs/map001-main-menu-bridge/input-plan-01_create_init_main_menu.json"
```
