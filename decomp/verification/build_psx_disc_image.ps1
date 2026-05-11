[CmdletBinding()]
param(
    [string]$CleanBinPath = "Game Data/Vagrant Story (USA).bin",
    [string]$SourceTreePath = "Game Data",
    [string]$RoodReverseRoot = "_refs/rood-reverse",
    [string]$CacheDirectory = ".codex_tmp/psx-disc-rebuild",
    [string]$OutputDirectory = ".codex_tmp/psx-disc-rebuild/output",
    [string]$DiscCode = "SLUS-01040",
    [string]$OutputImageName = "Vagrant Story (USA) patched.bin",
    [string]$OutputCueName = "Vagrant Story (USA) patched.cue",
    [string]$ProjectXmlName = "Vagrant Story (USA) patched.xml",
    [string]$SummaryJsonName = "disc_rebuild_summary.json",
    [switch]$BuildMkpsxiso,
    [switch]$ForceRedumpTemplate,
    [switch]$UseDumpedSourceTree,
    [switch]$RequireCompleteSourceTree,
    [switch]$SkipDifferenceScan
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

    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $Path))
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

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Get-RelativeProjectPath {
    param(
        [Parameter(Mandatory = $true)][string]$BaseDirectory,
        [Parameter(Mandatory = $true)][string]$TargetPath
    )

    $basePath = [System.IO.Path]::GetFullPath($BaseDirectory)
    $targetPath = [System.IO.Path]::GetFullPath($TargetPath)

    if (-not $basePath.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $basePath = $basePath + [System.IO.Path]::DirectorySeparatorChar
    }

    $baseUri = [System.Uri]::new($basePath)
    $targetUri = [System.Uri]::new($targetPath)
    $relativeUri = $baseUri.MakeRelativeUri($targetUri)
    return [System.Uri]::UnescapeDataString($relativeUri.ToString()).Replace("\", "/")
}

function Ensure-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found in PATH."
    }
}

function Ensure-MkpsxisoToolchain {
    param([Parameter(Mandatory = $true)][string]$Root)

    $mkpsxisoExe = Join-Path $Root "tools/mkpsxiso/build/Release/mkpsxiso.exe"
    $dumpsxisoExe = Join-Path $Root "tools/mkpsxiso/build/Release/dumpsxiso.exe"

    if ((Test-Path -LiteralPath $mkpsxisoExe) -and (Test-Path -LiteralPath $dumpsxisoExe)) {
        return [pscustomobject]@{
            Mkpsxiso = $mkpsxisoExe
            Dumpsxiso = $dumpsxisoExe
        }
    }

    if (-not $BuildMkpsxiso) {
        throw "mkpsxiso binaries were not found under '$Root/tools/mkpsxiso/build/Release'. Re-run with -BuildMkpsxiso to build them."
    }

    Ensure-Command -Name "cmake"

    $mkpsxisoRoot = Join-Path $Root "tools/mkpsxiso"
    Assert-Exists -Path $mkpsxisoRoot -Label "mkpsxiso source tree"
    Assert-Exists -Path (Join-Path $mkpsxisoRoot "CMakeLists.txt") -Label "mkpsxiso CMakeLists.txt"

    Write-Host "Building mkpsxiso release binaries..."
    & cmake -S $mkpsxisoRoot -B (Join-Path $mkpsxisoRoot "build") --preset release
    if ($LASTEXITCODE -ne 0) {
        throw "cmake configure for mkpsxiso failed with exit code $LASTEXITCODE."
    }

    & cmake --build (Join-Path $mkpsxisoRoot "build") --config Release
    if ($LASTEXITCODE -ne 0) {
        throw "cmake build for mkpsxiso failed with exit code $LASTEXITCODE."
    }

    Assert-Exists -Path $mkpsxisoExe -Label "mkpsxiso.exe"
    Assert-Exists -Path $dumpsxisoExe -Label "dumpsxiso.exe"

    return [pscustomobject]@{
        Mkpsxiso = $mkpsxisoExe
        Dumpsxiso = $dumpsxisoExe
    }
}

function Ensure-TemplateDump {
    param(
        [Parameter(Mandatory = $true)][string]$DumpsxisoExe,
        [Parameter(Mandatory = $true)][string]$CleanBin,
        [Parameter(Mandatory = $true)][string]$TemplateDirectory,
        [Parameter(Mandatory = $true)][string]$DiscCodeValue
    )

    $templateDumpDirectory = Join-Path $TemplateDirectory "dump"
    $templateXmlPath = Join-Path $TemplateDirectory "$DiscCodeValue.xml"
    $licensePath = Join-Path $templateDumpDirectory "license_data.dat"

    $needsDump = $ForceRedumpTemplate -or
        (-not (Test-Path -LiteralPath $templateXmlPath)) -or
        (-not (Test-Path -LiteralPath $licensePath))

    if ($needsDump) {
        Ensure-Directory -Path $TemplateDirectory
        if (Test-Path -LiteralPath $templateDumpDirectory) {
            Remove-Item -LiteralPath $templateDumpDirectory -Recurse -Force
        }

        Write-Host "Dumping clean disc image template from '$CleanBin'..."
        & $DumpsxisoExe -x $templateDumpDirectory -s $templateXmlPath $CleanBin
        if ($LASTEXITCODE -ne 0) {
            throw "dumpsxiso failed with exit code $LASTEXITCODE."
        }
    }

    Assert-Exists -Path $templateXmlPath -Label "template XML"
    Assert-Exists -Path $licensePath -Label "dumped license data"

    return [pscustomobject]@{
        TemplateXml = $templateXmlPath
        TemplateDumpDirectory = $templateDumpDirectory
        LicensePath = $licensePath
    }
}

function New-ProjectXml {
    param(
        [Parameter(Mandatory = $true)][string]$TemplateXmlPath,
        [Parameter(Mandatory = $true)][string]$GeneratedXmlPath,
        [Parameter(Mandatory = $true)][string]$SourceRootPath,
        [Parameter(Mandatory = $true)][string]$TemplateDumpRootPath,
        [Parameter(Mandatory = $true)][string]$LicensePath,
        [Parameter(Mandatory = $true)][string]$OutputImageFileName,
        [Parameter(Mandatory = $true)][string]$OutputCueFileName,
        [switch]$RequireCompleteSourceTree
    )

    $xmlDirectory = Split-Path -Parent $GeneratedXmlPath
    $sourceRootPath = [System.IO.Path]::GetFullPath($SourceRootPath)
    $templateDumpRootPath = [System.IO.Path]::GetFullPath($TemplateDumpRootPath)
    $licensePath = [System.IO.Path]::GetFullPath($LicensePath)
    $templateText = Get-Content -LiteralPath $TemplateXmlPath -Raw

    $templateText = [regex]::Replace(
        $templateText,
        'image_name="[^"]*"',
        ('image_name="{0}"' -f [System.Security.SecurityElement]::Escape($OutputImageFileName)),
        1
    )
    $templateText = [regex]::Replace(
        $templateText,
        'cue_sheet="[^"]*"',
        ('cue_sheet="{0}"' -f [System.Security.SecurityElement]::Escape($OutputCueFileName)),
        1
    )

    $licenseRelativePath = Get-RelativeProjectPath -BaseDirectory $xmlDirectory -TargetPath $licensePath
    $templateText = [regex]::Replace(
        $templateText,
        '(<license\b[^>]*\bfile=")[^"]+(")',
        ('$1{0}$2' -f $licenseRelativePath),
        1
    )

    $normalizedDumpPrefix = $templateDumpRootPath.Replace("\", "/").TrimEnd("/")
    $sourcePattern = 'source="([^"]+)"'
    $seenSourceEntries = New-Object System.Collections.Generic.HashSet[string]
    $fallbackEntries = New-Object System.Collections.Generic.List[string]
    $templatePreferredExtensions = @(".XA", ".STR")
    $sourceMatches = [regex]::Matches($templateText, $sourcePattern)
    foreach ($match in $sourceMatches) {
        $originalEntry = $match.Groups[0].Value
        if (-not $seenSourceEntries.Add($originalEntry)) {
            continue
        }

        $originalSourcePath = $match.Groups[1].Value.Replace("\", "/")
        $relativeInsideDump = $null
        if ($originalSourcePath.StartsWith("dump/", [System.StringComparison]::OrdinalIgnoreCase)) {
            $relativeInsideDump = $originalSourcePath.Substring(5)
        } elseif ($originalSourcePath.StartsWith($normalizedDumpPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            $relativeInsideDump = $originalSourcePath.Substring($normalizedDumpPrefix.Length).TrimStart("/")
        } else {
            continue
        }

        $relativeInsideDump = $relativeInsideDump.Replace("/", "\")
        $replacementPath = Join-Path $sourceRootPath $relativeInsideDump
        $templateDumpPath = Join-Path $templateDumpRootPath $relativeInsideDump
        $extension = [System.IO.Path]::GetExtension($relativeInsideDump).ToUpperInvariant()

        if ($templatePreferredExtensions -contains $extension) {
            $replacementPath = $templateDumpPath
            $fallbackEntries.Add($relativeInsideDump.Replace("\", "/")) | Out-Null
        } elseif (-not (Test-Path -LiteralPath $replacementPath)) {
            if ($RequireCompleteSourceTree) {
                throw "Project source target missing: $replacementPath"
            }

            $replacementPath = $templateDumpPath
            if (-not (Test-Path -LiteralPath $replacementPath)) {
                throw "Project source target missing in both source tree and template dump: $relativeInsideDump"
            }

            $fallbackEntries.Add($relativeInsideDump.Replace("\", "/")) | Out-Null
        }

        $replacementRelativePath = Get-RelativeProjectPath -BaseDirectory $xmlDirectory -TargetPath $replacementPath
        $replacementEntry = 'source="{0}"' -f $replacementRelativePath
        $templateText = $templateText.Replace($originalEntry, $replacementEntry)
    }

    Set-Content -LiteralPath $GeneratedXmlPath -Value $templateText -Encoding utf8

    return [pscustomobject]@{
        FallbackToTemplateSources = $fallbackEntries
    }
}

function Get-FirstByteDifferences {
    param(
        [Parameter(Mandatory = $true)][string]$LeftPath,
        [Parameter(Mandatory = $true)][string]$RightPath,
        [int]$Limit = 64
    )

    $leftInfo = Get-Item -LiteralPath $LeftPath
    $rightInfo = Get-Item -LiteralPath $RightPath
    $length = [Math]::Min($leftInfo.Length, $rightInfo.Length)
    $bufferSize = 1024 * 1024
    $offset = [int64]0
    $results = New-Object System.Collections.Generic.List[object]

    $leftStream = [System.IO.File]::Open($LeftPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
    try {
        $rightStream = [System.IO.File]::Open($RightPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        try {
            $leftBuffer = New-Object byte[] $bufferSize
            $rightBuffer = New-Object byte[] $bufferSize

            while ($offset -lt $length -and $results.Count -lt $Limit) {
                $bytesToRead = [Math]::Min($bufferSize, $length - $offset)
                $leftRead = $leftStream.Read($leftBuffer, 0, $bytesToRead)
                $rightRead = $rightStream.Read($rightBuffer, 0, $bytesToRead)

                if ($leftRead -ne $rightRead) {
                    throw "Stream length mismatch encountered while comparing files."
                }

                for ($i = 0; $i -lt $leftRead -and $results.Count -lt $Limit; $i++) {
                    if ($leftBuffer[$i] -ne $rightBuffer[$i]) {
                        $results.Add([pscustomobject]@{
                                offset_dec = $offset + $i
                                offset_hex = ("0x{0:X8}" -f ($offset + $i))
                                left_hex = ("0x{0:X2}" -f $leftBuffer[$i])
                                right_hex = ("0x{0:X2}" -f $rightBuffer[$i])
                            }) | Out-Null
                    }
                }

                $offset += $leftRead
            }
        } finally {
            $rightStream.Dispose()
        }
    } finally {
        $leftStream.Dispose()
    }

    if ($leftInfo.Length -ne $rightInfo.Length -and $results.Count -lt $Limit) {
        $results.Add([pscustomobject]@{
                offset_dec = $length
                offset_hex = ("0x{0:X8}" -f $length)
                left_hex = if ($leftInfo.Length -gt $rightInfo.Length) { "EOF+" } else { "EOF" }
                right_hex = if ($rightInfo.Length -gt $leftInfo.Length) { "EOF+" } else { "EOF" }
            }) | Out-Null
    }

    return $results
}

function Remove-IfExists {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Force
    }
}

$cleanBin = Resolve-RepoPath -Path $CleanBinPath
$sourceTree = Resolve-RepoPath -Path $SourceTreePath
$roodReverse = Resolve-RepoPath -Path $RoodReverseRoot
$cacheDirectory = Resolve-RepoPath -Path $CacheDirectory
$outputDirectory = Resolve-RepoPath -Path $OutputDirectory

Assert-Exists -Path $cleanBin -Label "clean retail BIN"
Assert-Exists -Path $sourceTree -Label "source tree"
Assert-Exists -Path $roodReverse -Label "rood-reverse root"

$toolchain = Ensure-MkpsxisoToolchain -Root $roodReverse

$templateDirectory = Join-Path $cacheDirectory "template"
$template = Ensure-TemplateDump `
    -DumpsxisoExe $toolchain.Dumpsxiso `
    -CleanBin $cleanBin `
    -TemplateDirectory $templateDirectory `
    -DiscCodeValue $DiscCode

$effectiveSourceTree = if ($UseDumpedSourceTree) {
    $template.TemplateDumpDirectory
} else {
    $sourceTree
}

Assert-Exists -Path $effectiveSourceTree -Label "effective source tree"

Ensure-Directory -Path $outputDirectory

$projectXmlPath = Join-Path $outputDirectory $ProjectXmlName
$outputImagePath = Join-Path $outputDirectory $OutputImageName
$outputCuePath = Join-Path $outputDirectory $OutputCueName
$summaryJsonPath = Join-Path $outputDirectory $SummaryJsonName

Remove-IfExists -Path $projectXmlPath
Remove-IfExists -Path $outputImagePath
Remove-IfExists -Path $outputCuePath
Remove-IfExists -Path $summaryJsonPath

Write-Host "Generating mkpsxiso project XML..."
$projectInfo = New-ProjectXml `
    -TemplateXmlPath $template.TemplateXml `
    -GeneratedXmlPath $projectXmlPath `
    -SourceRootPath $effectiveSourceTree `
    -TemplateDumpRootPath $template.TemplateDumpDirectory `
    -LicensePath $template.LicensePath `
    -OutputImageFileName $OutputImageName `
    -OutputCueFileName $OutputCueName `
    -RequireCompleteSourceTree:$RequireCompleteSourceTree

Write-Host "Rebuilding disc image..."
Push-Location $outputDirectory
try {
    & $toolchain.Mkpsxiso $projectXmlPath
    if ($LASTEXITCODE -ne 0) {
        throw "mkpsxiso failed with exit code $LASTEXITCODE."
    }
} finally {
    Pop-Location
}

Assert-Exists -Path $outputImagePath -Label "rebuilt BIN"
Assert-Exists -Path $outputCuePath -Label "rebuilt CUE"

$cleanHash = Get-FileHash -LiteralPath $cleanBin -Algorithm SHA256
$rebuiltHash = Get-FileHash -LiteralPath $outputImagePath -Algorithm SHA256
$cleanLength = (Get-Item -LiteralPath $cleanBin).Length
$rebuiltLength = (Get-Item -LiteralPath $outputImagePath).Length

$differenceSample = @()
if (-not $SkipDifferenceScan) {
    Write-Host "Scanning for first byte differences..."
    $differenceSample = @(Get-FirstByteDifferences -LeftPath $cleanBin -RightPath $outputImagePath -Limit 64)
}

$summary = [ordered]@{
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    repo_root = $RepoRoot
    clean_bin_path = $cleanBin
    source_tree_path = $effectiveSourceTree
    rood_reverse_root = $roodReverse
    template_xml_path = $template.TemplateXml
    generated_project_xml_path = $projectXmlPath
    output_bin_path = $outputImagePath
    output_cue_path = $outputCuePath
    clean_sha256 = $cleanHash.Hash
    rebuilt_sha256 = $rebuiltHash.Hash
    clean_size_bytes = $cleanLength
    rebuilt_size_bytes = $rebuiltLength
    hashes_match = ($cleanHash.Hash -eq $rebuiltHash.Hash)
    sizes_match = ($cleanLength -eq $rebuiltLength)
    difference_sample = $differenceSample
    source_tree_fallback_count = @($projectInfo.FallbackToTemplateSources).Count
    source_tree_fallbacks = @($projectInfo.FallbackToTemplateSources)
    notes = @(
        "The rebuilt image is generated from the mkpsxiso project template dumped from the clean BIN.",
        "license_data.dat is preserved from the dumpsxiso template cache because it is not present in the extracted Game Data tree.",
        "Streamed media files such as .XA and .STR currently stay on the clean template dump path because the local extracted tree is not mkpsxiso-ready for those assets.",
        "When a file is missing from the chosen source tree, the script falls back to the clean template dump unless -RequireCompleteSourceTree is set.",
        "A non-matching SHA256 on an otherwise successful rebuild means this workflow is a practical rebuild path, not a byte-perfect retail round-trip."
    )
}

$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryJsonPath -Encoding utf8

Write-Host ""
Write-Host "Disc rebuild complete."
Write-Host "  BIN:      $outputImagePath"
Write-Host "  CUE:      $outputCuePath"
Write-Host "  Summary:  $summaryJsonPath"
Write-Host "  Clean SHA256:   $($cleanHash.Hash)"
Write-Host "  Rebuilt SHA256: $($rebuiltHash.Hash)"
Write-Host "  Hash match:     $($summary.hashes_match)"
