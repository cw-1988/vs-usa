param(
    [string]$BinaryPath = "Game Data/BATTLE/BATTLE.PRG",
    [string]$OutputPath = "decomp/evidence/battle_runtime_opcode_table_pointer_usage.json",
    [string]$BaseAddress = "0x80068800",
    [string]$TargetAddress = "0x800F4C28",
    [string]$SeedAddress = "0x800BFBB8",
    [int]$InstructionLimit = 160,
    [int]$BackwardWindow = 6,
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

. (Join-Path $PSScriptRoot "Invoke-GhidraHeadlessExport.ps1")

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "BATTLE" `
    -PostScript "TracePointerDerivedAccesses.java" `
    -PostScriptArguments @(
        $TargetAddress,
        $SeedAddress,
        "$InstructionLimit",
        "$BackwardWindow"
    ) `
    -ProjectRoot $ProjectRoot
