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
    (Join-Path $suiteRoot 'DATA_DEPARTMENT_SKILL_MAP.md'),
    (Join-Path $suiteRoot 'SOURCE_INTEGRATION_AUDIT.md'),
    (Join-Path $suiteRoot 'OPERATING_GUIDE.md'),
    (Join-Path $suiteRoot 'LIFECYCLE_OPERATING_MODEL.md'),
    (Join-Path $suiteRoot '01_HUONG_DAN_IMPORT_CLAUDE_SKILL.md'),
    (Join-Path $suiteRoot '02_TONG_QUAN_NANG_LUC_DATA_DEPARTMENT_SKILLS.md'),
    (Join-Path $suiteRoot '01_CHI_TIET_TOAN_BO_SKILL_VA_TASK.md'),
    (Join-Path $suiteRoot '02_HUONG_DAN_IMPORT_VA_SU_DUNG_CLAUDE.md'),
    (Join-Path $suiteRoot 'pyproject.toml')
)

Compress-Archive -LiteralPath $items -DestinationPath $resolvedOutput -CompressionLevel Optimal
Write-Output "Created $resolvedOutput"
