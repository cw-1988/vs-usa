param(
    [string]$BinaryPath = "Game Data/BATTLE/BATTLE.PRG",
    [string]$OutputPath = "decomp/evidence/battle_sound_dispatch_table.json",
    [string]$BaseAddress = "0x80068800",
    [string]$TableAddress = "0x800E9F30",
    [int]$EntryCount = 8,
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

. (Join-Path $PSScriptRoot "Invoke-GhidraHeadlessExport.ps1")

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "BATTLE" `
    -PostScript "ExportFunctionTable.java" `
    -PostScriptArguments @(
        $TableAddress,
        "$EntryCount",
        "battle_sound_dispatch_table",
        "4"
    ) `
    -ProjectRoot $ProjectRoot
