param(
    [string]$BinaryPath = "Game Data/BATTLE/BATTLE.PRG",
    [string]$OutputPath = "decomp/evidence/battle_runtime_opcode_table_accesses.json",
    [string]$BaseAddress = "0x80068800",
    [string]$TargetAddress = "0x800F4C28",
    [int]$BackwardWindow = 6,
    [int]$BeforeCount = 5,
    [int]$AfterCount = 8,
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

. (Join-Path $PSScriptRoot "Invoke-GhidraHeadlessExport.ps1")

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "BATTLE" `
    -PostScript "DumpAddressAccesses.java" `
    -PostScriptArguments @(
        $TargetAddress,
        "$BackwardWindow",
        "$BeforeCount",
        "$AfterCount",
        "0x800BFBB8"
    ) `
    -ProjectRoot $ProjectRoot
