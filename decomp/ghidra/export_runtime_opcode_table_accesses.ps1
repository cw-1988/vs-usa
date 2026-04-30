param(
    [Parameter(Mandatory = $true)]
    [string]$BinaryPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [Parameter(Mandatory = $true)]
    [string]$BaseAddress,

    [Parameter(Mandatory = $true)]
    [string]$BlockName,

    [string]$TargetAddress = "0x800F4C28",
    [int]$BackwardWindow = 6,
    [int]$BeforeCount = 5,
    [int]$AfterCount = 8,
    [string[]]$SeedAddresses = @(),
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

. (Join-Path $PSScriptRoot "Invoke-GhidraHeadlessExport.ps1")

$postScriptArguments = @(
    $TargetAddress
    "$BackwardWindow"
    "$BeforeCount"
    "$AfterCount"
) + $SeedAddresses

Invoke-GhidraHeadlessExport `
    -BinaryPath $BinaryPath `
    -OutputPath $OutputPath `
    -BaseAddress $BaseAddress `
    -BlockName $BlockName `
    -PostScript "DumpAddressAccesses.java" `
    -PostScriptArguments $postScriptArguments `
    -ProjectRoot $ProjectRoot
