param(
    [string]$BinaryPath = "Game Data/BATTLE/INITBTL.PRG",
    [string]$OutputPath = "decomp/evidence/inittbl_runtime_opcode_table_accesses.json",
    [string]$BaseAddress = "0x800F9800",
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
    -BlockName "INITBTL" `
    -PostScript "DumpAddressAccesses.java" `
    -PostScriptArguments @(
        $TargetAddress,
        "$BackwardWindow",
        "$BeforeCount",
        "$AfterCount",
        "0x800FAAAC"
    ) `
    -ProjectRoot $ProjectRoot
