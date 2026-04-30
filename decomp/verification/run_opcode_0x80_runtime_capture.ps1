[CmdletBinding()]
param(
    [string]$PcsxReduxExe = "tools/pcsx-redux/pcsx-redux.exe",
    [string]$BiosPath = "tools/pcsx-redux/openbios.bin",
    [string]$IsoPath,
    [string]$ExePath,
    [string]$SaveStatePath,
    [switch]$UseNewestSaveState,
    [string[]]$SaveStateSearchRoots = @("decomp/evidence", ".codex_tmp", "."),
    [string[]]$SaveStatePatterns = @("*.p2s", "*.p2s.gz", "*.savestate", "*.savestate.gz", "*.state", "*.state.gz"),
    [switch]$KeepPreparedSaveState,
    [string]$Memcard1Path = "memcard1.mcd",
    [string]$Memcard2Path = "memcard2.mcd",
    [string]$LuaScript = "decomp/verification/pcsx_redux_opcode_0x80_capture.lua",
    [string]$ObservationPath = "decomp/evidence/opcode_0x80_runtime_observation.json",
    [string]$AfterInitPath = "decomp/evidence/opcode_0x80_runtime_after_init.bin",
    [string]$PreDispatchPath = "decomp/evidence/opcode_0x80_runtime_pre_dispatch.bin",
    [string]$SummaryPath = "decomp/evidence/opcode_0x80_runtime_automation_summary.json",
    [string]$TableAddress = "0x800F4C28",
    [string]$TableSize = "0x400",
    [string]$FocusOpcodes = "0x80,0x81,0x82",
    [string]$ReaderAddress = "0x800BFBB8",
    [string]$StubAddress = "0x800B66E4",
    [string]$CandidateAddress = "0x800BA2E0",
    [int]$IdleCycles = 200000,
    [int]$TimeoutFrames = 1800,
    [int]$PostReaderFrames = 180,
    [string]$MinWritePc = "0x80000000",
    [int]$SummaryWaitSeconds = 120,
    [switch]$QuitOnCandidateHit
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

function Resolve-RepoPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $resolved = Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue
    if ($resolved) {
        return $resolved.Path
    }

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    $absolute = Join-Path $RepoRoot $Path
    return [System.IO.Path]::GetFullPath($absolute)
}

function Assert-Exists {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Label not found: $Path"
    }
}

function Get-NewestSaveState {
    param(
        [Parameter(Mandatory = $true)][string[]]$SearchRoots,
        [Parameter(Mandatory = $true)][string[]]$Patterns
    )

    $matches = @()
    foreach ($root in $SearchRoots) {
        $resolvedRoot = Resolve-RepoPath -Path $root
        if (-not (Test-Path -LiteralPath $resolvedRoot)) {
            continue
        }

        foreach ($pattern in $Patterns) {
            $matches += Get-ChildItem -Path $resolvedRoot -Filter $pattern -File -Recurse -ErrorAction SilentlyContinue
        }
    }

    return $matches |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
}

function Test-GzipFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    $stream = [System.IO.File]::OpenRead($Path)
    try {
        if ($stream.Length -lt 2) {
            return $false
        }

        return ($stream.ReadByte() -eq 0x1f) -and ($stream.ReadByte() -eq 0x8b)
    } finally {
        $stream.Dispose()
    }
}

function Expand-GzipFile {
    param(
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$DestinationPath
    )

    Add-Type -AssemblyName System.IO.Compression

    $sourceStream = [System.IO.File]::OpenRead($SourcePath)
    try {
        $gzipStream = [System.IO.Compression.GzipStream]::new(
            $sourceStream,
            [System.IO.Compression.CompressionMode]::Decompress
        )
        try {
            $destinationStream = [System.IO.File]::Create($DestinationPath)
            try {
                $gzipStream.CopyTo($destinationStream)
            } finally {
                $destinationStream.Dispose()
            }
        } finally {
            $gzipStream.Dispose()
        }
    } finally {
        $sourceStream.Dispose()
    }
}

function Prepare-SaveState {
    param([Parameter(Mandatory = $true)][string]$Path)

    $resolvedPath = Resolve-RepoPath -Path $Path
    Assert-Exists -Path $resolvedPath -Label "Save state"

    if (-not (Test-GzipFile -Path $resolvedPath)) {
        return [pscustomobject]@{
            SourcePath       = $resolvedPath
            LoadPath         = $resolvedPath
            PreparedPath     = $null
            WasDecompressed  = $false
        }
    }

    $preparedDirectory = Join-Path $RepoRoot ".codex_tmp\pcsx-redux"
    New-Item -ItemType Directory -Force -Path $preparedDirectory | Out-Null

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($resolvedPath)
    $preparedName = "{0}-{1}.savestate" -f $baseName, [Guid]::NewGuid().ToString("N")
    $preparedPath = Join-Path $preparedDirectory $preparedName
    Expand-GzipFile -SourcePath $resolvedPath -DestinationPath $preparedPath

    return [pscustomobject]@{
        SourcePath       = $resolvedPath
        LoadPath         = $preparedPath
        PreparedPath     = $preparedPath
        WasDecompressed  = $true
    }
}

function Invoke-Recorder {
    param([string[]]$Arguments)

    & python (Join-Path $RepoRoot "decomp/verification/record_runtime_observation.py") @Arguments
}

$pcsxReduxExe = Resolve-RepoPath -Path $PcsxReduxExe
$biosPath = Resolve-RepoPath -Path $BiosPath
$luaScript = Resolve-RepoPath -Path $LuaScript
$observationPath = Resolve-RepoPath -Path $ObservationPath
$afterInitPath = Resolve-RepoPath -Path $AfterInitPath
$preDispatchPath = Resolve-RepoPath -Path $PreDispatchPath
$summaryPath = Resolve-RepoPath -Path $SummaryPath
$saveStatePath = $null
$saveStateInfo = $null
$memcard1Path = $null
$memcard2Path = $null

Assert-Exists -Path $pcsxReduxExe -Label "PCSX-Redux executable"
Assert-Exists -Path $biosPath -Label "BIOS"
Assert-Exists -Path $luaScript -Label "Lua capture script"
Assert-Exists -Path $observationPath -Label "Runtime observation packet"

if ([string]::IsNullOrWhiteSpace($IsoPath) -and [string]::IsNullOrWhiteSpace($ExePath)) {
    throw "Pass either -IsoPath or -ExePath so PCSX-Redux has something to boot."
}

if (-not [string]::IsNullOrWhiteSpace($IsoPath) -and -not [string]::IsNullOrWhiteSpace($ExePath)) {
    throw "Pass only one of -IsoPath or -ExePath."
}

if (-not [string]::IsNullOrWhiteSpace($SaveStatePath) -and $UseNewestSaveState) {
    throw "Pass either -SaveStatePath or -UseNewestSaveState, not both."
}

$bootFlag = $null
$bootPath = $null
if (-not [string]::IsNullOrWhiteSpace($IsoPath)) {
    $bootFlag = "-iso"
    $bootPath = Resolve-RepoPath -Path $IsoPath
    Assert-Exists -Path $bootPath -Label "Disc image"
} else {
    $bootFlag = "-exe"
    $bootPath = Resolve-RepoPath -Path $ExePath
    Assert-Exists -Path $bootPath -Label "PS-X EXE"
}

if ($UseNewestSaveState) {
    $discoveredSaveState = Get-NewestSaveState -SearchRoots $SaveStateSearchRoots -Patterns $SaveStatePatterns
    if (-not $discoveredSaveState) {
        $roots = $SaveStateSearchRoots -join ", "
        $patterns = $SaveStatePatterns -join ", "
        throw "No save state matched patterns [$patterns] under [$roots]."
    }
    $saveStateInfo = Prepare-SaveState -Path $discoveredSaveState.FullName
    $saveStatePath = $saveStateInfo.LoadPath
} elseif (-not [string]::IsNullOrWhiteSpace($SaveStatePath)) {
    $saveStateInfo = Prepare-SaveState -Path $SaveStatePath
    $saveStatePath = $saveStateInfo.LoadPath
}

if (-not [string]::IsNullOrWhiteSpace($Memcard1Path)) {
    $candidateMemcard1Path = Resolve-RepoPath -Path $Memcard1Path
    if (Test-Path -LiteralPath $candidateMemcard1Path) {
        $memcard1Path = $candidateMemcard1Path
    }
}

if (-not [string]::IsNullOrWhiteSpace($Memcard2Path)) {
    $candidateMemcard2Path = Resolve-RepoPath -Path $Memcard2Path
    if (Test-Path -LiteralPath $candidateMemcard2Path) {
        $memcard2Path = $candidateMemcard2Path
    }
}

New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($afterInitPath)) | Out-Null
New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($preDispatchPath)) | Out-Null
New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($summaryPath)) | Out-Null

Remove-Item -LiteralPath $afterInitPath, $preDispatchPath, $summaryPath -ErrorAction SilentlyContinue

$env:VS_OPCODE_TABLE_ADDRESS = $TableAddress
$env:VS_OPCODE_TABLE_SIZE = $TableSize
$env:VS_OPCODE_FOCUS_OPCODES = $FocusOpcodes
$env:VS_OPCODE_READER_ADDRESS = $ReaderAddress
$env:VS_OPCODE_STUB_ADDRESS = $StubAddress
$env:VS_OPCODE_CANDIDATE_ADDRESS = $CandidateAddress
$env:VS_OPCODE_AFTER_INIT_PATH = $afterInitPath
$env:VS_OPCODE_PRE_DISPATCH_PATH = $preDispatchPath
$env:VS_OPCODE_AUTOMATION_SUMMARY_PATH = $summaryPath
$env:VS_OPCODE_IDLE_CYCLES = "$IdleCycles"
$env:VS_OPCODE_TIMEOUT_FRAMES = "$TimeoutFrames"
$env:VS_OPCODE_POST_READER_FRAMES = "$PostReaderFrames"
$env:VS_OPCODE_MIN_WRITE_PC = $MinWritePc
$env:VS_OPCODE_QUIT_ON_CANDIDATE_HIT = if ($QuitOnCandidateHit) { "1" } else { "0" }
$env:VS_OPCODE_SAVE_STATE_PATH = if ($saveStatePath) { $saveStatePath } else { "" }
$env:VS_OPCODE_SAVE_STATE_SOURCE_PATH = if ($saveStateInfo) { $saveStateInfo.SourcePath } else { "" }
$env:VS_OPCODE_SAVE_STATE_WAS_DECOMPRESSED = if ($saveStateInfo -and $saveStateInfo.WasDecompressed) { "1" } else { "0" }

$args = @(
    "-portable",
    "-testmode",
    "-run",
    "-fastboot",
    "-interpreter",
    "-debugger",
    "-bios", $biosPath,
    $bootFlag, $bootPath,
    "-dofile", $luaScript,
    "-stdout",
    "-lua_stdout"
)

if ($memcard1Path) {
    $args += @("-memcard1", $memcard1Path)
}

if ($memcard2Path) {
    $args += @("-memcard2", $memcard2Path)
}

Write-Host "Launching PCSX-Redux automated capture..."
Write-Host "Executable: $pcsxReduxExe"
Write-Host "Boot source: $bootPath"
Write-Host "Summary path: $summaryPath"
if ($saveStatePath) {
    Write-Host "Save state: $saveStatePath"
    if ($saveStateInfo.SourcePath -ne $saveStatePath) {
        Write-Host "Save state source: $($saveStateInfo.SourcePath)"
    }
    if ($saveStateInfo.WasDecompressed) {
        Write-Host "Prepared savestate: decompressed gzip payload for Lua loading."
    }
}
if ($memcard1Path) {
    Write-Host "Memcard1: $memcard1Path"
}
if ($memcard2Path) {
    Write-Host "Memcard2: $memcard2Path"
}

$processExitCode = $null
try {
    $process = Start-Process -FilePath $pcsxReduxExe -ArgumentList $args -PassThru

    while (-not (Test-Path -LiteralPath $summaryPath) -and -not $process.HasExited) {
        Start-Sleep -Milliseconds 500
        $process.Refresh()
    }

    if ($process.HasExited) {
        $processExitCode = $process.ExitCode
    } else {
        $processExitCode = 0
    }
} catch {
    Write-Warning ("Start-Process failed; falling back to direct launch semantics. " + $_.Exception.Message)
    & $pcsxReduxExe @args
    $lastExitCodeVariable = Get-Variable -Name LASTEXITCODE -ErrorAction SilentlyContinue
    $processExitCode = if ($lastExitCodeVariable) { [int]$lastExitCodeVariable.Value } else { 0 }
} finally {
    if ($saveStateInfo -and $saveStateInfo.PreparedPath -and -not $KeepPreparedSaveState) {
        Remove-Item -LiteralPath $saveStateInfo.PreparedPath -ErrorAction SilentlyContinue
    }
}

if (-not (Test-Path -LiteralPath $summaryPath)) {
    $deadline = [DateTime]::UtcNow.AddSeconds($SummaryWaitSeconds)
    while ((-not (Test-Path -LiteralPath $summaryPath)) -and ([DateTime]::UtcNow -lt $deadline)) {
        Start-Sleep -Milliseconds 500
    }
}

if (-not (Test-Path -LiteralPath $summaryPath)) {
    throw "Automation summary was not created. If you are using the GUI build, try the official Windows CLI build from PCSX-Redux."
}

$summary = Get-Content -Raw -LiteralPath $summaryPath | ConvertFrom-Json

if (Test-Path -LiteralPath $afterInitPath) {
    Invoke-Recorder @(
        $observationPath,
        "set-snapshot",
        "--label", "after_init",
        "--path", $afterInitPath,
        "--capture-point", "Automated PCSX-Redux capture after opcode-table writes settled."
    )
}

if (Test-Path -LiteralPath $preDispatchPath) {
    Invoke-Recorder @(
        $observationPath,
        "set-snapshot",
        "--label", "pre_dispatch",
        "--path", $preDispatchPath,
        "--capture-point", "Automated PCSX-Redux capture at the runtime opcode reader."
    )
}

if ($summary.write_hit_count -gt 0) {
    Invoke-Recorder @(
        $observationPath,
        "add-breakpoint-hit",
        "--kind", "write",
        "--address-range", "0x800F4C28-0x800F5027",
        "--hit-count", "$($summary.write_hit_count)",
        "--note", "Automated PCSX-Redux capture observed runtime opcode-table writes."
    )
}

if ($summary.reader_hit_count -gt 0) {
    Invoke-Recorder @(
        $observationPath,
        "add-breakpoint-hit",
        "--kind", "exec",
        "--address", $ReaderAddress,
        "--hit-count", "$($summary.reader_hit_count)",
        "--pc", $ReaderAddress,
        "--note", "Automated PCSX-Redux capture reached the recovered runtime opcode reader."
    )
}

if ($saveStateInfo) {
    $note = if ($saveStateInfo.WasDecompressed) {
        "Automated PCSX-Redux capture loaded savestate source '$($saveStateInfo.SourcePath)' after inflating its gzip-compressed UI payload to a temporary raw file for PCSX.loadSaveState(file)."
    } else {
        "Automated PCSX-Redux capture loaded savestate '$($saveStateInfo.SourcePath)' directly."
    }

    Invoke-Recorder @(
        $observationPath,
        "add-note",
        "--note", $note
    )
}

$candidateHits = @()
if ($summary.candidate_hits) {
    foreach ($property in $summary.candidate_hits.PSObject.Properties) {
        $candidate = $property.Value
        if ($candidate.hit_count -gt 0) {
            $candidateHits += ("{0} x{1}" -f $property.Name, $candidate.hit_count)
            Invoke-Recorder @(
                $observationPath,
                "add-breakpoint-hit",
                "--kind", "exec",
                "--address", $property.Name,
                "--hit-count", "$($candidate.hit_count)",
                "--pc", $property.Name,
                "--note", "Automated PCSX-Redux capture hit candidate handler breakpoint '$($candidate.label)'."
            )
        }
    }
}

$snapshotSummaries = @()
if ($summary.snapshots) {
    foreach ($labelProperty in $summary.snapshots.PSObject.Properties) {
        $snapshot = $labelProperty.Value
        if ($snapshot.focus_handlers) {
            $pairs = @()
            foreach ($entryProperty in $snapshot.focus_handlers.PSObject.Properties) {
                $pairs += ("{0}->{1}" -f $entryProperty.Name, $entryProperty.Value)
            }
            if ($pairs.Count -gt 0) {
                $snapshotSummaries += ("{0}: {1}" -f $labelProperty.Name, ($pairs -join ", "))
            }
        }
    }
}

$noteParts = @(
    "Automated PCSX-Redux capture summary",
    "process_exit=$processExitCode",
    "summary_exit=$($summary.exit_code)",
    "frames=$($summary.frame_count)",
    "write_hits=$($summary.write_hit_count)",
    "reader_hits=$($summary.reader_hit_count)"
)

if ($candidateHits.Count -gt 0) {
    $noteParts += ("candidate_hits=" + ($candidateHits -join ", "))
}

if ($snapshotSummaries.Count -gt 0) {
    $noteParts += ("focus_handlers=" + ($snapshotSummaries -join " | "))
}

$noteParts += "summary_json=$summaryPath"

Invoke-Recorder @(
    $observationPath,
    "add-note",
    "--note", ($noteParts -join "; ")
)

& python (Join-Path $RepoRoot "decomp/verification/finalize_runtime_observation.py") $observationPath "--in-place" "--allow-missing-snapshots"

if ((Test-Path -LiteralPath $afterInitPath) -and (Test-Path -LiteralPath $preDispatchPath)) {
    Invoke-Recorder @(
        $observationPath,
        "import-compare",
        "--replace-derived",
        "--finalize"
    )
}

Write-Host "Capture summary recorded in $summaryPath"
Write-Host "Observation packet refreshed at $observationPath"
