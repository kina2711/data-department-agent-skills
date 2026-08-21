param(
    [string]$OutputPath = (Join-Path (Split-Path -Parent $PSScriptRoot) 'dist\data-department-claude-plugin-v3.7.0.zip')
)

$ErrorActionPreference = 'Stop'
$suiteRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$distRoot = [System.IO.Path]::GetFullPath((Join-Path $suiteRoot 'dist'))
$stageRoot = [System.IO.Path]::GetFullPath((Join-Path $distRoot 'claude-plugin\data-department-agent-skills'))
$resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)

if (-not $stageRoot.StartsWith($distRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to stage outside dist: $stageRoot"
}
if (-not $resolvedOutput.StartsWith($distRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Claude release output must remain inside dist: $resolvedOutput"
}

if (Test-Path -LiteralPath $stageRoot) {
    Remove-Item -LiteralPath $stageRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $stageRoot -Force | Out-Null

$pluginTarget = Join-Path $stageRoot '.claude-plugin'
New-Item -ItemType Directory -Path $pluginTarget -Force | Out-Null
# Only plugin.json is staged: marketplace.json describes the repository, and copying it here
# would make Claude Code validate the release as a marketplace instead of as a plugin.
Copy-Item -LiteralPath (Join-Path $suiteRoot '.claude-plugin\plugin.json') -Destination $pluginTarget

foreach ($component in @('commands', 'hooks')) {
    $componentSource = Join-Path $suiteRoot $component
    if (-not (Test-Path -LiteralPath $componentSource -PathType Container)) {
        throw "Plugin component directory is missing: $componentSource"
    }
    Copy-Item -LiteralPath $componentSource -Destination $stageRoot -Recurse
}

$skillsTarget = Join-Path $stageRoot 'skills'
New-Item -ItemType Directory -Path $skillsTarget -Force | Out-Null
foreach ($source in Get-ChildItem -LiteralPath (Join-Path $suiteRoot 'skills') -Directory | Sort-Object Name) {
    $target = Join-Path $skillsTarget $source.Name
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $source.FullName 'SKILL.md') -Destination $target
    foreach ($resourceName in @('references', 'assets', 'scripts')) {
        $resourcePath = Join-Path $source.FullName $resourceName
        if (Test-Path -LiteralPath $resourcePath -PathType Container) {
            Copy-Item -LiteralPath $resourcePath -Destination $target -Recurse
        }
    }
}

foreach ($cache in Get-ChildItem -LiteralPath $skillsTarget -Directory -Recurse -Filter '__pycache__') {
    $resolvedCache = [System.IO.Path]::GetFullPath($cache.FullName)
    if (-not $resolvedCache.StartsWith($skillsTarget, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove cache outside staged skills: $resolvedCache"
    }
    Remove-Item -LiteralPath $resolvedCache -Recurse -Force
}
Get-ChildItem -LiteralPath $skillsTarget -File -Recurse -Filter '*.pyc' | Remove-Item -Force

foreach ($cache in Get-ChildItem -LiteralPath $stageRoot -Directory -Recurse -Filter '__pycache__') {
    $resolvedCache = [System.IO.Path]::GetFullPath($cache.FullName)
    if (-not $resolvedCache.StartsWith($stageRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove cache outside the staged plugin: $resolvedCache"
    }
    Remove-Item -LiteralPath $resolvedCache -Recurse -Force
}
Get-ChildItem -LiteralPath $stageRoot -File -Recurse -Filter '*.pyc' | Remove-Item -Force

$claudeCommand = Get-Command claude -ErrorAction SilentlyContinue
if ($null -eq $claudeCommand) {
    throw 'Claude Code CLI is required to validate the native plugin release.'
}
& $claudeCommand.Source plugin validate --strict $stageRoot
if ($LASTEXITCODE -ne 0) {
    throw 'Claude Code strict plugin validation failed.'
}

$outputDirectory = Split-Path -Parent $resolvedOutput
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
if (Test-Path -LiteralPath $resolvedOutput) {
    Remove-Item -LiteralPath $resolvedOutput -Force
}
$archiveItems = @(
    (Join-Path $stageRoot '.claude-plugin'),
    (Join-Path $stageRoot 'skills'),
    (Join-Path $stageRoot 'commands'),
    (Join-Path $stageRoot 'hooks')
)
Compress-Archive -LiteralPath $archiveItems -DestinationPath $resolvedOutput -CompressionLevel Optimal

$skillCount = (Get-ChildItem -LiteralPath $skillsTarget -Directory).Count
$commandCount = (Get-ChildItem -LiteralPath (Join-Path $stageRoot 'commands') -File -Filter '*.md').Count
Write-Output "Created Claude-native plugin: $resolvedOutput"
Write-Output "Validated skills: $skillCount"
Write-Output "Bundled commands: $commandCount"
Write-Output "Development load: claude --plugin-dir `"$stageRoot`""
