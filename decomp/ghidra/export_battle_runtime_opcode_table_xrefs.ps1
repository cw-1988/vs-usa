param(
    [string]$BinaryPath = "Game Data/BATTLE/BATTLE.PRG",
    [string]$OutputPath = "decomp/evidence/battle_runtime_opcode_table_xrefs.json",
    [string]$BaseAddress = "0x80068800",
    [string]$TargetAddress = "0x800F4C28",
    [int]$BeforeCount = 4,
    [int]$AfterCount = 8,
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
