[CmdletBinding()]
param(
    [string]$PcsxReduxExe = "tools/pcsx-redux/pcsx-redux.exe",
    [string]$BiosPath = "tools/pcsx-redux/openbios.bin",
    [ValidateSet("interpreter", "dynarec")][string]$CpuCore = "interpreter",
    [switch]$DisableDebugger,
    [string]$IsoPath,
    [string]$ExePath,
    [string]$SaveStatePath,
    [switch]$UseNewestSaveState,
    [string[]]$SaveStateSearchRoots = @("decomp/evidence", ".codex_tmp", "."),
    [string[]]$SaveStatePatterns = @("*.p2s", "*.p2s.gz", "*.savestate", "*.savestate.gz", "*.state", "*.state.gz"),
    [switch]$KeepPreparedSaveState,
    [string]$InputPlanPath,
    [switch]$UseDefaultInputPlan,
    [string]$DefaultInputPlanPath = "decomp/evidence/opcode_0x80_runtime_input_plan.json",
    [string]$DecodedScriptPath,
    [string]$Memcard1Path = "memcard1.mcd",
    [string]$Memcard2Path = "memcard2.mcd",
    [string]$LuaScript = "decomp/verification/pcsx_redux_opcode_0x80_capture.lua",
    [string]$ObservationPath = "decomp/evidence/opcode_0x80_runtime_observation.json",
    [string]$AfterInitPath = "decomp/evidence/opcode_0x80_runtime_after_init.bin",
    [string]$PreDispatchPath = "decomp/evidence/opcode_0x80_runtime_pre_dispatch.bin",
    [string]$SummaryPath = "decomp/evidence/opcode_0x80_runtime_automation_summary.json",
    [string]$ScreenshotDirectory = "decomp/evidence/opcode_0x80_runtime_frames",
    [string]$TableAddress = "0x800F4C28",
    [string]$TableSize = "0x400",
    [string]$FocusOpcodes = "0x80,0x81,0x82",
    [string]$ReaderAddress = "0x800BFBB8",
    [string]$ReaderCallerAddress = "0x800BF850",
    [string]$ReaderGrandcallerAddress = "0x8007A36C",
    [string]$StubAddress = "0x800B66E4",
    [string]$CandidateAddress = "0x800BA2E0",
    [int]$IdleCycles = 200000,
    [int]$TimeoutFrames = 1800,
    [int]$PostReaderFrames = 180,
    [int]$InputPlanTimeoutSlackFrames = 600,
    [int]$MinBreakpointFrame = 0,
    [string]$MinWritePc = "0x80000000",
    [int]$LaunchTimeoutSeconds = 180,
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

function Stop-ProcessTree {
    param([Parameter(Mandatory = $true)][int]$RootId)

    $queue = New-Object System.Collections.Generic.Queue[int]
    $allIds = New-Object System.Collections.Generic.List[int]
    $queue.Enqueue($RootId)

    while ($queue.Count -gt 0) {
        $currentId = $queue.Dequeue()
        $allIds.Add($currentId) | Out-Null

        $children = @(Get-CimInstance Win32_Process -Filter "ParentProcessId = $currentId" -ErrorAction SilentlyContinue)
        foreach ($child in $children) {
            if ($child.ProcessId -and ($allIds -notcontains [int]$child.ProcessId)) {
                $queue.Enqueue([int]$child.ProcessId)
            }
        }
    }

    foreach ($id in ($allIds | Sort-Object -Descending | Select-Object -Unique)) {
        Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
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

function Get-ObjectPropertyValue {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        $Default = $null
    )

    if ($null -eq $Object) {
        return $Default
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $Default
    }

    if ($null -eq $property.Value) {
        return $Default
    }

    return $property.Value
}

function Test-ObjectProperty {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name
    )

    if ($null -eq $Object) {
        return $false
    }

    return $null -ne $Object.PSObject.Properties[$Name]
}

function ConvertTo-NonNegativeInt {
    param(
        [Parameter(Mandatory = $true)]$Value,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $parsed = [int]$Value
    if ($parsed -lt 0) {
        throw "$Label must be >= 0."
    }

    return $parsed
}

function ConvertTo-PositiveInt {
    param(
        [Parameter(Mandatory = $true)]$Value,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $parsed = [int]$Value
    if ($parsed -lt 1) {
        throw "$Label must be >= 1."
    }

    return $parsed
}

function Prepare-InputPlan {
    param([Parameter(Mandatory = $true)][string]$Path)

    $resolvedPath = Resolve-RepoPath -Path $Path
    Assert-Exists -Path $resolvedPath -Label "Input plan"

    $plan = Get-Content -Raw -LiteralPath $resolvedPath | ConvertFrom-Json
    $steps = @(Get-ObjectPropertyValue -Object $plan -Name "steps" -Default @())
    if ($steps.Count -eq 0) {
        throw "Input plan '$resolvedPath' does not define any steps."
    }

    $description = [string](Get-ObjectPropertyValue -Object $plan -Name "description" -Default "")
    $padSlot = ConvertTo-PositiveInt -Value (Get-ObjectPropertyValue -Object $plan -Name "pad_slot" -Default 1) -Label "pad_slot"
    $padNumber = ConvertTo-PositiveInt -Value (Get-ObjectPropertyValue -Object $plan -Name "pad_number" -Default 1) -Label "pad_number"
    $initialDelayFrames = ConvertTo-NonNegativeInt -Value (Get-ObjectPropertyValue -Object $plan -Name "initial_delay_frames" -Default 0) -Label "initial_delay_frames"
    $analogMode = [bool](Get-ObjectPropertyValue -Object $plan -Name "analog_mode" -Default $false)

    $preparedDirectory = Join-Path $RepoRoot ".codex_tmp\pcsx-redux"
    New-Item -ItemType Directory -Force -Path $preparedDirectory | Out-Null

    $preparedPath = Join-Path $preparedDirectory ("opcode_0x80_input_plan-{0}.tsv" -f [Guid]::NewGuid().ToString("N"))
    $lines = New-Object System.Collections.Generic.List[string]
    $currentFrame = $initialDelayFrames
    $stepIndex = 0

    foreach ($step in $steps) {
        $stepIndex += 1
        $buttons = @(Get-ObjectPropertyValue -Object $step -Name "buttons" -Default @())
        if ($buttons.Count -eq 0) {
            throw "Input plan step $stepIndex has no buttons."
        }

        $buttonNames = @()
        foreach ($button in $buttons) {
            $buttonText = [string]$button
            if ([string]::IsNullOrWhiteSpace($buttonText)) {
                throw "Input plan step $stepIndex contains an empty button name."
            }
            $buttonNames += $buttonText.Trim().ToUpperInvariant()
        }

        $holdFrames = ConvertTo-NonNegativeInt -Value (Get-ObjectPropertyValue -Object $step -Name "hold_frames" -Default 8) -Label "hold_frames for step $stepIndex"
        if ($holdFrames -eq 0) {
            throw "Input plan step $stepIndex must hold at least one frame."
        }

        $waitFramesAfter = ConvertTo-NonNegativeInt -Value (Get-ObjectPropertyValue -Object $step -Name "wait_frames_after" -Default 30) -Label "wait_frames_after for step $stepIndex"
        $startFrame = if (Test-ObjectProperty -Object $step -Name "start_frame") {
            ConvertTo-NonNegativeInt -Value (Get-ObjectPropertyValue -Object $step -Name "start_frame") -Label "start_frame for step $stepIndex"
        } else {
            $currentFrame
        }

        $note = [string](Get-ObjectPropertyValue -Object $step -Name "note" -Default ("step {0}" -f $stepIndex))
        $note = $note -replace "\r?\n", " "
        $note = $note -replace "`t", " "

        $lines.Add(("{0}`t{1}`t{2}`t{3}" -f $startFrame, $holdFrames, ($buttonNames -join ","), $note))
        $currentFrame = $startFrame + $holdFrames + $waitFramesAfter
    }

    [System.IO.File]::WriteAllLines($preparedPath, $lines, [System.Text.Encoding]::ASCII)

    return [pscustomobject]@{
        SourcePath         = $resolvedPath
        PreparedPath       = $preparedPath
        Description        = $description
        PadSlot            = $padSlot
        PadNumber          = $padNumber
        AnalogMode         = $analogMode
        InitialDelayFrames = $initialDelayFrames
        StepCount          = $stepIndex
        FinalFrameAfterWaits = $currentFrame
    }
}

function Get-DecodedScriptOpcodes {
    param([Parameter(Mandatory = $true)][string]$Path)

    $resolvedPath = Resolve-RepoPath -Path $Path
    Assert-Exists -Path $resolvedPath -Label "Decoded script"

    $opcodeSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $pattern = '^\s*[0-9A-Fa-f]+:\s+([0-9A-Fa-f]{2})\b'

    foreach ($line in [System.IO.File]::ReadLines($resolvedPath)) {
        $match = [System.Text.RegularExpressions.Regex]::Match($line, $pattern)
        if ($match.Success) {
            [void]$opcodeSet.Add(("0x" + $match.Groups[1].Value.ToUpperInvariant()))
        }
    }

    if ($opcodeSet.Count -eq 0) {
        throw "Decoded script '$resolvedPath' did not yield any opcode bytes."
    }

    $opcodes = @($opcodeSet | Sort-Object)
    return [pscustomobject]@{
        SourcePath = $resolvedPath
        OpcodeCount = $opcodes.Count
        Opcodes = $opcodes
        OpcodeCsv = ($opcodes -join ",")
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
$screenshotDirectory = Resolve-RepoPath -Path $ScreenshotDirectory
$saveStatePath = $null
$saveStateInfo = $null
$inputPlanInfo = $null
$decodedScriptInfo = $null
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

if (-not [string]::IsNullOrWhiteSpace($InputPlanPath) -and $UseDefaultInputPlan) {
    throw "Pass either -InputPlanPath or -UseDefaultInputPlan, not both."
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

$effectiveSaveStateSearchRoots = @($SaveStateSearchRoots)
$pcsxReduxDirectory = Split-Path -Parent $pcsxReduxExe
if ($pcsxReduxDirectory -and ($effectiveSaveStateSearchRoots -notcontains $pcsxReduxDirectory)) {
    $effectiveSaveStateSearchRoots += $pcsxReduxDirectory
}

if ($UseNewestSaveState) {
    $discoveredSaveState = Get-NewestSaveState -SearchRoots $effectiveSaveStateSearchRoots -Patterns $SaveStatePatterns
    if (-not $discoveredSaveState) {
        $roots = $effectiveSaveStateSearchRoots -join ", "
        $patterns = $SaveStatePatterns -join ", "
        throw "No save state matched patterns [$patterns] under [$roots]."
    }
    $saveStateInfo = Prepare-SaveState -Path $discoveredSaveState.FullName
    $saveStatePath = $saveStateInfo.LoadPath
} elseif (-not [string]::IsNullOrWhiteSpace($SaveStatePath)) {
    $saveStateInfo = Prepare-SaveState -Path $SaveStatePath
    $saveStatePath = $saveStateInfo.LoadPath
}

if ($UseDefaultInputPlan) {
    $inputPlanInfo = Prepare-InputPlan -Path $DefaultInputPlanPath
} elseif (-not [string]::IsNullOrWhiteSpace($InputPlanPath)) {
    $inputPlanInfo = Prepare-InputPlan -Path $InputPlanPath
}

if (-not [string]::IsNullOrWhiteSpace($DecodedScriptPath)) {
    $decodedScriptInfo = Get-DecodedScriptOpcodes -Path $DecodedScriptPath
}

$effectiveTimeoutFrames = $TimeoutFrames
if ($inputPlanInfo) {
    $inputPlanDrivenTimeout = [Math]::Max(
        [int]$inputPlanInfo.FinalFrameAfterWaits + $PostReaderFrames,
        [int]$inputPlanInfo.FinalFrameAfterWaits + $InputPlanTimeoutSlackFrames
    )
    $effectiveTimeoutFrames = [Math]::Max($TimeoutFrames, $inputPlanDrivenTimeout)
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
New-Item -ItemType Directory -Force -Path $screenshotDirectory | Out-Null

Remove-Item -LiteralPath $afterInitPath, $preDispatchPath, $summaryPath -ErrorAction SilentlyContinue
Get-ChildItem -LiteralPath $screenshotDirectory -File -ErrorAction SilentlyContinue | Remove-Item -ErrorAction SilentlyContinue

$env:VS_OPCODE_TABLE_ADDRESS = $TableAddress
$env:VS_OPCODE_TABLE_SIZE = $TableSize
$env:VS_OPCODE_FOCUS_OPCODES = $FocusOpcodes
$env:VS_OPCODE_HANDLER_OPCODES = if ($decodedScriptInfo) { $decodedScriptInfo.OpcodeCsv } else { "" }
$env:VS_OPCODE_READER_ADDRESS = $ReaderAddress
$env:VS_OPCODE_READER_CALLER_ADDRESS = $ReaderCallerAddress
$env:VS_OPCODE_READER_GRANDCALLER_ADDRESS = $ReaderGrandcallerAddress
$env:VS_OPCODE_STUB_ADDRESS = $StubAddress
$env:VS_OPCODE_CANDIDATE_ADDRESS = $CandidateAddress
$env:VS_OPCODE_AFTER_INIT_PATH = $afterInitPath
$env:VS_OPCODE_PRE_DISPATCH_PATH = $preDispatchPath
$env:VS_OPCODE_AUTOMATION_SUMMARY_PATH = $summaryPath
$env:VS_OPCODE_IDLE_CYCLES = "$IdleCycles"
$env:VS_OPCODE_TIMEOUT_FRAMES = "$effectiveTimeoutFrames"
$env:VS_OPCODE_POST_READER_FRAMES = "$PostReaderFrames"
$env:VS_OPCODE_MIN_BREAKPOINT_FRAME = "$MinBreakpointFrame"
$env:VS_OPCODE_MIN_WRITE_PC = $MinWritePc
$env:VS_OPCODE_QUIT_ON_CANDIDATE_HIT = if ($QuitOnCandidateHit) { "1" } else { "0" }
$env:VS_OPCODE_SAVE_STATE_PATH = if ($saveStatePath) { $saveStatePath } else { "" }
$env:VS_OPCODE_SAVE_STATE_SOURCE_PATH = if ($saveStateInfo) { $saveStateInfo.SourcePath } else { "" }
$env:VS_OPCODE_SAVE_STATE_WAS_DECOMPRESSED = if ($saveStateInfo -and $saveStateInfo.WasDecompressed) { "1" } else { "0" }
$env:VS_OPCODE_INPUT_PLAN_PATH = if ($inputPlanInfo) { $inputPlanInfo.PreparedPath } else { "" }
$env:VS_OPCODE_INPUT_PLAN_SOURCE_PATH = if ($inputPlanInfo) { $inputPlanInfo.SourcePath } else { "" }
$env:VS_OPCODE_INPUT_PLAN_DESCRIPTION = if ($inputPlanInfo) { $inputPlanInfo.Description } else { "" }
$env:VS_OPCODE_INPUT_PLAN_PAD_SLOT = if ($inputPlanInfo) { "$($inputPlanInfo.PadSlot)" } else { "" }
$env:VS_OPCODE_INPUT_PLAN_PAD_NUMBER = if ($inputPlanInfo) { "$($inputPlanInfo.PadNumber)" } else { "" }
$env:VS_OPCODE_INPUT_PLAN_ANALOG_MODE = if ($inputPlanInfo -and $inputPlanInfo.AnalogMode) { "1" } else { "0" }
$env:VS_OPCODE_SCREENSHOT_DIR = $screenshotDirectory

$cpuCoreFlag = if ($CpuCore -eq "dynarec") { "-dynarec" } else { "-interpreter" }
$debuggerFlag = if ($DisableDebugger) { "-no-debugger" } else { "-debugger" }

$args = @(
    "-portable",
    "-testmode",
    "-run",
    "-fastboot",
    $cpuCoreFlag,
    $debuggerFlag,
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
Write-Host "Screenshot directory: $screenshotDirectory"
Write-Host "CPU core: $CpuCore"
Write-Host "Debugger: $(if ($DisableDebugger) { 'disabled' } else { 'enabled' })"
if ($saveStatePath) {
    Write-Host "Save state: $saveStatePath"
    if ($saveStateInfo.SourcePath -ne $saveStatePath) {
        Write-Host "Save state source: $($saveStateInfo.SourcePath)"
    }
    if ($saveStateInfo.WasDecompressed) {
        Write-Host "Prepared savestate: decompressed gzip payload for Lua loading."
    }
}
if ($inputPlanInfo) {
    Write-Host "Input plan source: $($inputPlanInfo.SourcePath)"
    Write-Host "Input plan steps: $($inputPlanInfo.StepCount)"
    Write-Host "Input plan final frame: $($inputPlanInfo.FinalFrameAfterWaits)"
    if ($effectiveTimeoutFrames -ne $TimeoutFrames) {
        Write-Host "Timeout frames raised from $TimeoutFrames to $effectiveTimeoutFrames to cover the input plan plus slack."
    }
}
if ($decodedScriptInfo) {
    Write-Host "Decoded script source: $($decodedScriptInfo.SourcePath)"
    Write-Host "Decoded script opcode count: $($decodedScriptInfo.OpcodeCount)"
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
    $launchDeadline = [DateTime]::UtcNow.AddSeconds($LaunchTimeoutSeconds)

    while (-not (Test-Path -LiteralPath $summaryPath) -and -not $process.HasExited) {
        if ([DateTime]::UtcNow -ge $launchDeadline) {
            Stop-ProcessTree -RootId $process.Id
            throw "PCSX-Redux did not produce a summary within $LaunchTimeoutSeconds seconds."
        }
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

$probeHits = @()
if ($summary.probe_hits) {
    foreach ($property in $summary.probe_hits.PSObject.Properties) {
        $probe = $property.Value
        if ($probe.hit_count -gt 0) {
            $probeHits += ("{0} x{1}" -f $property.Name, $probe.hit_count)
            Invoke-Recorder @(
                $observationPath,
                "add-breakpoint-hit",
                "--kind", "exec",
                "--address", $property.Name,
                "--hit-count", "$($probe.hit_count)",
                "--pc", $property.Name,
                "--note", "Automated PCSX-Redux capture hit upstream probe breakpoint '$($probe.label)'."
            )
        }
    }
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

$summaryInputPlan = Get-ObjectPropertyValue -Object $summary -Name "input_plan" -Default $null
if ($summaryInputPlan -and ((Get-ObjectPropertyValue -Object $summaryInputPlan -Name "step_count" -Default 0) -gt 0)) {
    $inputPlanNoteParts = @(
        "Automated PCSX-Redux capture used input plan '$($summaryInputPlan.source_path)'",
        "prepared_path=$($summaryInputPlan.prepared_path)",
        "pad=$($summaryInputPlan.pad_slot)/$($summaryInputPlan.pad_number)",
        "steps=$($summaryInputPlan.completed_steps)/$($summaryInputPlan.step_count)"
    )

    if ($summaryInputPlan.description) {
        $inputPlanNoteParts += ("description=" + $summaryInputPlan.description)
    }

    Invoke-Recorder @(
        $observationPath,
        "add-note",
        "--note", ($inputPlanNoteParts -join "; ")
    )
}

$summaryScreenCaptures = @(Get-ObjectPropertyValue -Object $summary -Name "screen_captures" -Default @())
if ($summaryScreenCaptures.Count -gt 0) {
    Invoke-Recorder @(
        $observationPath,
        "add-note",
        "--note", ("Automated PCSX-Redux capture wrote {0} screen capture(s) under {1}." -f $summaryScreenCaptures.Count, $screenshotDirectory)
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

$dispatchSummaries = @()
$summaryDispatchObservations = @(Get-ObjectPropertyValue -Object $summary -Name "dispatch_observations" -Default @())
foreach ($dispatch in $summaryDispatchObservations) {
    $opcode = [string](Get-ObjectPropertyValue -Object $dispatch -Name "opcode" -Default "")
    $handlerAddress = [string](Get-ObjectPropertyValue -Object $dispatch -Name "last_handler_address" -Default "")
    if ([string]::IsNullOrWhiteSpace($opcode) -or [string]::IsNullOrWhiteSpace($handlerAddress)) {
        continue
    }

    $hitCount = Get-ObjectPropertyValue -Object $dispatch -Name "hit_count" -Default 0
    $scriptPtr = [string](Get-ObjectPropertyValue -Object $dispatch -Name "first_script_ptr" -Default "")
    $rawBytes = [string](Get-ObjectPropertyValue -Object $dispatch -Name "sample_raw_bytes" -Default "")
    $noteParts = @("Automated PCSX-Redux reader dispatch sample")
    if (-not [string]::IsNullOrWhiteSpace($scriptPtr)) {
        $noteParts += ("script_ptr=" + $scriptPtr)
    }
    if (-not [string]::IsNullOrWhiteSpace($rawBytes)) {
        $noteParts += ("raw=" + $rawBytes)
    }

    Invoke-Recorder @(
        $observationPath,
        "add-dispatch",
        "--opcode", $opcode,
        "--handler-address", $handlerAddress,
        "--source-breakpoint", $ReaderAddress,
        "--note", (($noteParts -join "; ") + "; hit_count=" + $hitCount)
    )

    $dispatchSummaries += ("{0}->{1} x{2}" -f $opcode, $handlerAddress, $hitCount)
}

$handlerProbeHits = @()
$summaryHandlerProbeHits = Get-ObjectPropertyValue -Object $summary -Name "handler_probe_hits" -Default $null
if ($summaryHandlerProbeHits) {
    foreach ($property in $summaryHandlerProbeHits.PSObject.Properties) {
        $probe = $property.Value
        $opcodes = @()
        $probeOpcodes = Get-ObjectPropertyValue -Object $probe -Name "opcodes" -Default @()
        foreach ($opcode in $probeOpcodes) {
            $opcodes += [string]$opcode
        }

        if ((Get-ObjectPropertyValue -Object $probe -Name "hit_count" -Default 0) -gt 0) {
            $handlerProbeHits += ("{0} [{1}] x{2}" -f $property.Name, ($opcodes -join ","), $probe.hit_count)
            Invoke-Recorder @(
                $observationPath,
                "add-breakpoint-hit",
                "--kind", "exec",
                "--address", $property.Name,
                "--hit-count", "$($probe.hit_count)",
                "--pc", $property.Name,
                "--note", ("Automated PCSX-Redux script handler probe hit for opcode set [{0}]." -f ($opcodes -join ","))
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

$runtimeTableBase = [string](Get-ObjectPropertyValue -Object $summary -Name "runtime_table_base" -Default "")
if (-not [string]::IsNullOrWhiteSpace($runtimeTableBase)) {
    $noteParts += ("runtime_table_base=" + $runtimeTableBase)
}

if ($candidateHits.Count -gt 0) {
    $noteParts += ("candidate_hits=" + ($candidateHits -join ", "))
}

if ($probeHits.Count -gt 0) {
    $noteParts += ("probe_hits=" + ($probeHits -join ", "))
}

if ($handlerProbeHits.Count -gt 0) {
    $noteParts += ("handler_hits=" + ($handlerProbeHits -join ", "))
}

if ($snapshotSummaries.Count -gt 0) {
    $noteParts += ("focus_handlers=" + ($snapshotSummaries -join " | "))
}

if ($dispatchSummaries.Count -gt 0) {
    $noteParts += ("dispatches=" + ($dispatchSummaries -join " | "))
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

if ($saveStateInfo -and $saveStateInfo.PreparedPath -and -not $KeepPreparedSaveState) {
    Remove-Item -LiteralPath $saveStateInfo.PreparedPath -ErrorAction SilentlyContinue
}
if ($inputPlanInfo -and $inputPlanInfo.PreparedPath) {
    Remove-Item -LiteralPath $inputPlanInfo.PreparedPath -ErrorAction SilentlyContinue
}

Write-Host "Capture summary recorded in $summaryPath"
Write-Host "Observation packet refreshed at $observationPath"
