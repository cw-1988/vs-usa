param(
    [string]$BinaryPath = "Game Data/TITLE/TITLE.PRG",
    [string]$OutputPath = "decomp/evidence/title_runtime_opcode_table_accesses.json",
    [string]$BaseAddress = "0x80068800",
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

& (Join-Path $PSScriptRoot "export_runtime_opcode_table_accesses.ps1") `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "TITLE" `
    -ProjectRoot $ProjectRoot
