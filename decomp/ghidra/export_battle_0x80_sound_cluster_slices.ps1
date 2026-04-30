param(
    [string]$BinaryPath = "Game Data/BATTLE/BATTLE.PRG",
    [string]$OutputPath = "decomp/evidence/battle_0x80_sound_cluster_slices.json",
    [string]$BaseAddress = "0x80068800",
    [int]$InstructionCount = 16,
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

. (Join-Path $PSScriptRoot "Invoke-GhidraHeadlessExport.ps1")

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "BATTLE" `
    -PostScript "DumpInstructions.java" `
    -PostScriptArguments @(
        "0x800B66E4",
        "0x800BA2E0",
        "0x800BA3E4",
        "0x800BA404",
        "0x800BA444",
        "0x800BA470",
        "$InstructionCount"
    ) `
    -ProjectRoot $ProjectRoot
