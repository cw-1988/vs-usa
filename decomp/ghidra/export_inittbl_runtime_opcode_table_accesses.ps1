param(
    [string]$BinaryPath = "Game Data/BATTLE/INITBTL.PRG",
    [string]$OutputPath = "decomp/evidence/inittbl_runtime_opcode_table_accesses.json",
    [string]$BaseAddress = "0x800F9800",
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

& (Join-Path $PSScriptRoot "export_runtime_opcode_table_accesses.ps1") `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "INITBTL" `
    -SeedAddresses @(
        "0x800FAAAC"
    ) `
    -ProjectRoot $ProjectRoot
