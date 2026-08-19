param(
    [string]$OutputPath = (Join-Path (Split-Path -Parent $PSScriptRoot) 'dist\data-department-agent-skills.zip')
)

$ErrorActionPreference = 'Stop'
$suiteRoot = Split-Path -Parent $PSScriptRoot
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $pythonCommand) {
    throw 'Python is required to regenerate the canonical user documentation.'
}
& $pythonCommand.Source (Join-Path $suiteRoot 'tools\generate_user_docs.py')
if ($LASTEXITCODE -ne 0) {
    throw 'Canonical user documentation generation failed.'
}
$resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)
$outputDirectory = Split-Path -Parent $resolvedOutput
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null

foreach ($cache in Get-ChildItem -LiteralPath $suiteRoot -Directory -Recurse -Filter '__pycache__') {
    $resolvedCache = [System.IO.Path]::GetFullPath($cache.FullName)
    if (-not $resolvedCache.StartsWith([System.IO.Path]::GetFullPath($suiteRoot), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove cache outside suite root: $resolvedCache"
    }
    Remove-Item -LiteralPath $resolvedCache -Recurse -Force
}
Get-ChildItem -LiteralPath $suiteRoot -File -Recurse -Filter '*.pyc' | Remove-Item -Force

if (Test-Path -LiteralPath $resolvedOutput) {
    Remove-Item -LiteralPath $resolvedOutput -Force
}

$items = @(
    (Join-Path $suiteRoot 'README.md'),
    (Join-Path $suiteRoot 'skills'),
    (Join-Path $suiteRoot '.claude-plugin'),
    (Join-Path $suiteRoot 'tools'),
    (Join-Path $suiteRoot 'schemas'),
    (Join-Path $suiteRoot 'evaluations'),
    (Join-Path $suiteRoot 'suite-manifest.yaml'),
    (Join-Path $suiteRoot 'task-catalog.json'),
    (Join-Path $suiteRoot 'docs\skill-map.md'),
    (Join-Path $suiteRoot 'docs\source-integration-audit.md'),
    (Join-Path $suiteRoot 'docs\operating-guide.md'),
    (Join-Path $suiteRoot 'docs\lifecycle-operating-model.md'),
    (Join-Path $suiteRoot 'docs\capability-overview.md'),
    (Join-Path $suiteRoot 'docs\skill-and-task-catalog.md'),
    (Join-Path $suiteRoot 'docs\installation-and-usage.md'),
    (Join-Path $suiteRoot 'pyproject.toml')
)

Compress-Archive -LiteralPath $items -DestinationPath $resolvedOutput -CompressionLevel Optimal
Write-Output "Created $resolvedOutput"
