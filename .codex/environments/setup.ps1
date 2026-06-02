param(
    [ValidateSet("Setup", "Smoke", "ProviderNative", "EquilibriumNative", "RegressionNative", "FullNative", "Sync", "IntelliJ", "Build", "Doctor", "DoctorFull")]
    [string]$Step = "Setup"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

function Resolve-UvCommand {
    $command = Get-Command uv -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }
    $localUv = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
    if (Test-Path -LiteralPath $localUv) {
        return $localUv
    }
    throw "uv is required for this repo workflow. Install uv, then rerun setup."
}

$uv = Resolve-UvCommand
$bootstrapStep = $Step.ToLowerInvariant()

& $uv sync --no-install-project
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& $uv run --no-sync python scripts/dev/bootstrap.py --step $bootstrapStep
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
