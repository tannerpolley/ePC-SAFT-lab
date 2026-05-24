param(
    [ValidateSet("Configure", "Build")]
    [string]$Action = "Configure",
    [string]$Preset = "dev-native",
    [string]$Target = "",
    [ValidateRange(1, 256)]
    [int]$Parallel = 10
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
Set-Location $RepoRoot

function Resolve-RepoTool {
    param([Parameter(Mandatory = $true)][string]$Name)

    $toolName = if ($Name.EndsWith(".exe")) { $Name } else { "$Name.exe" }
    $toolPath = Join-Path $RepoRoot ".venv\Scripts\$toolName"
    if (Test-Path -LiteralPath $toolPath -PathType Leaf) {
        return (Resolve-Path -LiteralPath $toolPath).Path
    }
    throw "Required repo-local tool is missing: $toolPath. Run uv sync --no-install-project before CMake preset work."
}

function Assert-NoNinjaLock {
    $lockPath = Join-Path $RepoRoot "build\dev\.ninja_lock"
    if (Test-Path -LiteralPath $lockPath) {
        throw "Refusing CMake preset run because build\dev\.ninja_lock exists. Another native build may be active; run the Build Status Services entry before retrying."
    }
}

function Get-CmakeCacheValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $cachePath = Join-Path $RepoRoot "build\dev\CMakeCache.txt"
    if (-not (Test-Path -LiteralPath $cachePath -PathType Leaf)) {
        return $null
    }
    $escapedName = [Regex]::Escape($Name)
    foreach ($line in Get-Content -LiteralPath $cachePath -ErrorAction Stop) {
        if ($line -match "^$escapedName(:[^=]+)?=(.*)$") {
            return $Matches[2]
        }
    }
    return $null
}

function Assert-MsvcEnvironment {
    return "if not defined INCLUDE (echo Visual Studio developer environment did not set INCLUDE. & exit /b 42) && if not defined LIB (echo Visual Studio developer environment did not set LIB. & exit /b 42)"
}

function Resolve-VsDevCmd {
    $explicit = $env:EPCSAFT_VSDEVCMD
    if (-not [string]::IsNullOrWhiteSpace($explicit)) {
        if (Test-Path -LiteralPath $explicit -PathType Leaf) {
            return (Resolve-Path -LiteralPath $explicit).Path
        }
        throw "EPCSAFT_VSDEVCMD points to a missing file: $explicit"
    }

    $programFilesX86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
    if ([string]::IsNullOrWhiteSpace($programFilesX86)) {
        $programFilesX86 = "C:\Program Files (x86)"
    }

    $vswhere = Join-Path $programFilesX86 "Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path -LiteralPath $vswhere -PathType Leaf) {
        $vswhereArgs = @(
            "-latest",
            "-products",
            "*",
            "-requires",
            "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
            "-property",
            "installationPath"
        )
        $installationOutput = & $vswhere @vswhereArgs 2>$null
        if ($LASTEXITCODE -eq 0) {
            $installationPath = @($installationOutput) | Select-Object -First 1
            if (-not [string]::IsNullOrWhiteSpace($installationPath)) {
                $candidate = Join-Path $installationPath "Common7\Tools\VsDevCmd.bat"
                if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                    return (Resolve-Path -LiteralPath $candidate).Path
                }
            }
        }
    }

    $defaultPath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
    if (Test-Path -LiteralPath $defaultPath -PathType Leaf) {
        return (Resolve-Path -LiteralPath $defaultPath).Path
    }

    throw "MSVC CMake preset requires Visual Studio C++ tools, but VsDevCmd.bat was not found."
}

function ConvertTo-CmdArgument {
    param([Parameter(Mandatory = $true)][string]$Value)

    return '"' + ($Value -replace '"', '\"') + '"'
}

function Invoke-CMakeWithMsvc {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $cmakeCommand = (ConvertTo-CmdArgument $PythonExe) + " " + (ConvertTo-CmdArgument "-m") + " " + (ConvertTo-CmdArgument "cmake") + " " + (($Arguments | ForEach-Object { ConvertTo-CmdArgument $_ }) -join " ")
    $toolPathCommand = "set `"PATH=$RepoToolDir;%PATH%`""
    $envCheckCommand = Assert-MsvcEnvironment
    $command = "call `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul && $toolPathCommand && $envCheckCommand && $cmakeCommand"

    Write-Host "Running with Visual Studio developer environment: $cmakeCommand"
    & cmd.exe /d /s /c $command
    if ($LASTEXITCODE -eq 42) {
        throw "Visual Studio developer environment did not set INCLUDE/LIB. MSVC CMake builds would miss standard headers or link libraries."
    }
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function New-CmakeArguments {
    param([Parameter(Mandatory = $true)][string]$RequestedAction)

    switch ($RequestedAction) {
    "Configure" {
            @("--preset", $Preset, "-DCMAKE_MAKE_PROGRAM=$($NinjaExe.Replace('\', '/'))")
    }
    "Build" {
            $args = @("--build", "--preset", $Preset)
        if (-not [string]::IsNullOrWhiteSpace($Target)) {
            $args += @("--target", $Target)
        }
        $args += @("--parallel", $Parallel.ToString())
        $args
    }
    }
}

$PythonExe = Resolve-RepoTool "python"
$NinjaExe = Resolve-RepoTool "ninja"
$RepoToolDir = Split-Path -Parent $PythonExe
$VsDevCmd = Resolve-VsDevCmd
$env:PATH = "$RepoToolDir;$env:PATH"

Assert-NoNinjaLock

if ($Action -eq "Build") {
    $configuredNinja = Get-CmakeCacheValue "CMAKE_MAKE_PROGRAM"
    $canonicalNinja = $NinjaExe.Replace("\", "/")
    if ([string]::IsNullOrWhiteSpace($configuredNinja) -or $configuredNinja.Replace("\", "/") -ne $canonicalNinja) {
        Write-Host "Refreshing dev-native configure so CMAKE_MAKE_PROGRAM uses repo-local Ninja: $canonicalNinja"
        Invoke-CMakeWithMsvc (New-CmakeArguments "Configure")
    }
}

Invoke-CMakeWithMsvc (New-CmakeArguments $Action)
