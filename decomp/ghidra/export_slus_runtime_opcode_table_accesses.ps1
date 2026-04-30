param(
    [string]$BinaryPath = "Game Data/SLUS_010.40",
    [string]$OutputPath = "decomp/evidence/slus_runtime_opcode_table_accesses.json",
    [string]$BaseAddress = "0x8000F800",
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

& (Join-Path $PSScriptRoot "export_runtime_opcode_table_accesses.ps1") `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "SLUS_010_40" `
    -ProjectRoot $ProjectRoot
