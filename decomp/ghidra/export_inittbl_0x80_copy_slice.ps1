param(
    [string]$BinaryPath = "Game Data/BATTLE/INITBTL.PRG",
    [string]$OutputPath = "decomp/evidence/inittbl_0x80_copy_slice.json",
    [string]$BaseAddress = "0x800F9800",
    [string]$StartAddress = "0x800FAAAC",
    [int]$InstructionCount = 16,
    [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
)

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\\..")
$ghidraHeadless = Join-Path $repoRoot "tools\\ghidra_12.0.4_PUBLIC\\support\\analyzeHeadless.bat"
$binary = Resolve-Path (Join-Path $repoRoot $BinaryPath)
$output = Join-Path $repoRoot $OutputPath
$scriptPath = Resolve-Path $PSScriptRoot
$projectDir = Join-Path $repoRoot $ProjectRoot
$projectName = "vs-usa-cli-" + [guid]::NewGuid().ToString("N")

if (!(Test-Path $projectDir)) {
    New-Item -ItemType Directory -Path $projectDir | Out-Null
}

& $ghidraHeadless `
    $projectDir `
    $projectName `
    -import $binary `
    -overwrite `
    -loader BinaryLoader `
    -loader-baseAddr $BaseAddress `
    -loader-blockName INITBTL `
    -processor "PSX:LE:32:default" `
    -scriptPath $scriptPath `
    -postScript DumpInstructions.java $output $StartAddress $InstructionCount `
    -deleteProject
