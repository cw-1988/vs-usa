param(
    [string]$BinaryPath = "Game Data/BATTLE/INITBTL.PRG",
    [string]$OutputPath = "decomp/evidence/inittbl_opcode_table.json",
    [string]$BaseAddress = "0x800F9800",
    [string]$TableAddress = "0x800FAF7C",
    [int]$EntryCount = 256,
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

. (Join-Path $PSScriptRoot "Invoke-GhidraHeadlessExport.ps1")

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "INITBTL" `
    -PostScript "ExportFunctionTable.java" `
    -PostScriptArguments @(
        $TableAddress,
        "$EntryCount",
        "INITBTL_opcode_table",
        "4"
    ) `
    -ProjectRoot $ProjectRoot
