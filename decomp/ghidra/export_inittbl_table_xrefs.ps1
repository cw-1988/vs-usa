param(
    [string]$BinaryPath = "Game Data/BATTLE/INITBTL.PRG",
    [string]$OutputPath = "decomp/evidence/inittbl_opcode_table_xrefs.json",
    [string]$BaseAddress = "0x800F9800",
    [string]$TargetAddress = "0x800FAF7C",
    [int]$BeforeCount = 3,
    [int]$AfterCount = 8,
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

. (Join-Path $PSScriptRoot "Invoke-GhidraHeadlessExport.ps1")

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "INITBTL" `
    -PostScript "DumpXrefs.java" `
    -PostScriptArguments @(
        $TargetAddress,
        "$BeforeCount",
        "$AfterCount"
    ) `
    -ProjectRoot $ProjectRoot
