param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Project', 'User')]
    [string]$Scope,

    [string]$ProjectPath = (Get-Location).Path,

    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$suiteRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $suiteRoot 'skills'

if ($Scope -eq 'Project') {
    $resolvedProject = [System.IO.Path]::GetFullPath($ProjectPath)
    if (-not (Test-Path -LiteralPath $resolvedProject -PathType Container)) {
        throw "Project directory does not exist: $resolvedProject"
    }
    $targetRoot = Join-Path $resolvedProject '.claude\skills'
}
else {
    $targetRoot = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.claude\skills'
}

New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null

$installed = 0
foreach ($source in Get-ChildItem -LiteralPath $sourceRoot -Directory) {
    $target = Join-Path $targetRoot $source.Name
    if (Test-Path -LiteralPath $target) {
        if (-not $Force) {
            throw "Target already exists: $target. Re-run with -Force only after reviewing the target."
        }
        $resolvedTarget = [System.IO.Path]::GetFullPath($target)
        $resolvedRoot = [System.IO.Path]::GetFullPath($targetRoot)
        if (-not $resolvedTarget.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to replace path outside target root: $resolvedTarget"
        }
        Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
    }
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $source.FullName 'SKILL.md') -Destination $target
    foreach ($resourceName in @('references', 'assets', 'scripts')) {
        $resourcePath = Join-Path $source.FullName $resourceName
        if (Test-Path -LiteralPath $resourcePath -PathType Container) {
            Copy-Item -LiteralPath $resourcePath -Destination $target -Recurse
        }
    }
    $installed += 1
}

Write-Output "Installed $installed skills to $targetRoot"
