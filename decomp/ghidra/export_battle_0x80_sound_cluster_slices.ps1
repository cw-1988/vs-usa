param(
    [string]$BinaryPath = "Game Data/BATTLE/BATTLE.PRG",
    [string]$OutputPath = "decomp/evidence/battle_0x80_sound_cluster_slices.json",
    [string]$BaseAddress = "0x80068800",
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
    -loader-blockName BATTLE `
    -processor "PSX:LE:32:default" `
    -scriptPath $scriptPath `
    -postScript DumpInstructions.java `
        $output `
        0x800B66E4 `
        0x800BA2E0 `
        0x800BA3E4 `
        0x800BA404 `
        0x800BA444 `
        0x800BA470 `
        $InstructionCount `
    -deleteProject
