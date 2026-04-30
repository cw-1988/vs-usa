param(
    [string]$BinaryPath = "Game Data/BATTLE/BATTLE.PRG",
    [string]$OutputPath = "decomp/evidence/battle_sound_candidate_xrefs.json",
    [string]$BaseAddress = "0x80068800",
    [string]$TargetAddress = "0x800BA2E0",
    [int]$BeforeCount = 1,
    [int]$AfterCount = 2,
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

. (Join-Path $PSScriptRoot "Invoke-GhidraHeadlessExport.ps1")

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "BATTLE" `
    -PostScript "DumpXrefs.java" `
    -PostScriptArguments @(
        $TargetAddress,
        "$BeforeCount",
        "$AfterCount"
    ) `
    -ProjectRoot $ProjectRoot
