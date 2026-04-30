param(
    [string]$BinaryPath = "Game Data/BATTLE/INITBTL.PRG",
    [string]$OutputPath = "decomp/evidence/inittbl_0x80_copy_slice.json",
    [string]$BaseAddress = "0x800F9800",
    [string]$StartAddress = "0x800FAAAC",
    [int]$InstructionCount = 16,
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

. (Join-Path $PSScriptRoot "Invoke-GhidraHeadlessExport.ps1")

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "INITBTL" `
    -PostScript "DumpInstructions.java" `
    -PostScriptArguments @(
        $StartAddress,
        "$InstructionCount"
    ) `
    -ProjectRoot $ProjectRoot
