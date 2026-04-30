function Invoke-GhidraHeadlessExport {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BinaryPath,

        [Parameter(Mandatory = $true)]
        [string]$OutputPath,

        [Parameter(Mandatory = $true)]
        [string]$BaseAddress,

        [Parameter(Mandatory = $true)]
        [string]$BlockName,

        [Parameter(Mandatory = $true)]
        [string]$PostScript,

        [string[]]$PostScriptArguments = @(),
        [string]$ProjectRoot = ".codex_tmp/ghidra-scratch"
    )

    $repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\\..")
    $ghidraHeadless = Join-Path $repoRoot "tools\\ghidra_12.0.4_PUBLIC\\support\\analyzeHeadless.bat"
    $binary = Resolve-Path (Join-Path $repoRoot $BinaryPath)
    $output = Join-Path $repoRoot $OutputPath
    $outputDir = Split-Path -Parent $output
    $scriptPath = Resolve-Path $PSScriptRoot
    $postScriptPath = Join-Path $scriptPath $PostScript
    $projectDir = Join-Path $repoRoot $ProjectRoot
    $projectName = "vs-usa-cli-" + [guid]::NewGuid().ToString("N")

    if (!(Test-Path $ghidraHeadless)) {
        throw "Missing Ghidra headless launcher: $ghidraHeadless"
    }

    if (!(Test-Path $postScriptPath)) {
        throw "Missing post-script: $postScriptPath"
    }

    if (!(Test-Path $projectDir)) {
        New-Item -ItemType Directory -Path $projectDir | Out-Null
    }

    if ($outputDir -and !(Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }

    $invokeArgs = @(
        $projectDir
        $projectName
        "-import"
        $binary
        "-overwrite"
        "-loader"
        "BinaryLoader"
        "-loader-baseAddr"
        $BaseAddress
        "-loader-blockName"
        $BlockName
        "-processor"
        "PSX:LE:32:default"
        "-scriptPath"
        $scriptPath
        "-postScript"
        $PostScript
        $output
    ) + $PostScriptArguments + @(
        "-deleteProject"
    )

    & $ghidraHeadless @invokeArgs

    if ($LASTEXITCODE -ne 0) {
        throw "Ghidra headless export failed with exit code $LASTEXITCODE"
    }
}
