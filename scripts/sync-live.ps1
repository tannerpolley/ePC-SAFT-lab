[CmdletBinding()]
param(
    [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"

$resolvedRoot = [IO.Path]::GetFullPath($RepoRoot)
$doctor = Join-Path $env:USERPROFILE ".agents\skills\project-doctor\scripts\audit-project.ps1"

if (-not (Test-Path -LiteralPath $doctor -PathType Leaf)) {
    throw "Project Doctor audit script is missing: $doctor"
}

pwsh.exe -NoProfile -ExecutionPolicy Bypass -File $doctor -RepoRoot $resolvedRoot -Mode GitHubAware
