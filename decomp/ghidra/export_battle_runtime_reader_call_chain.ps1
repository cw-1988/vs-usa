param(
    [string]$BinaryPath = "Game Data/BATTLE/BATTLE.PRG",
    [string]$BaseAddress = "0x80068800",
    [string]$ReaderAddress = "0x800BFBB8",
    [string]$ReaderCallerAddress = "0x800BF850",
    [string]$ReaderGrandcallerAddress = "0x8007A340",
    [string]$ReaderXrefsOutputPath = "decomp/evidence/battle_runtime_reader_xrefs.json",
    [string]$ReaderCallerXrefsOutputPath = "decomp/evidence/battle_runtime_reader_caller_xrefs.json",
    [string]$CallChainSlicesOutputPath = "decomp/evidence/battle_runtime_reader_call_chain_slices.json",
    [string]$ReaderCallerSliceOutputPath = "decomp/evidence/battle_runtime_reader_caller_slice.json",
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

. (Join-Path $PSScriptRoot "Invoke-GhidraHeadlessExport.ps1")

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $ReaderXrefsOutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "BATTLE" `
    -PostScript "DumpXrefs.java" `
    -PostScriptArguments @(
        $ReaderAddress,
        "4",
        "10"
    ) `
    -ProjectRoot $ProjectRoot

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $ReaderCallerXrefsOutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "BATTLE" `
    -PostScript "DumpXrefs.java" `
    -PostScriptArguments @(
        $ReaderCallerAddress,
        "4",
        "10"
    ) `
    -ProjectRoot $ProjectRoot

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $CallChainSlicesOutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "BATTLE" `
    -PostScript "DumpInstructions.java" `
    -PostScriptArguments @(
        $ReaderGrandcallerAddress,
        $ReaderCallerAddress,
        $ReaderAddress,
        "80"
    ) `
    -ProjectRoot $ProjectRoot

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $ReaderCallerSliceOutputPath `
    -BaseAddress $BaseAddress `
    -BlockName "BATTLE" `
    -PostScript "DumpInstructions.java" `
    -PostScriptArguments @(
        "0x800BF9A0",
        "96"
    ) `
    -ProjectRoot $ProjectRoot
