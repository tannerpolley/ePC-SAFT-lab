[CmdletBinding()]
param()

$ErrorActionPreference = "SilentlyContinue"

function Test-TcpPortOpen {
    param(
        [string]$HostName = "127.0.0.1",
        [int]$Port = 29170,
        [int]$TimeoutMs = 250
    )

    try {
        $client = [System.Net.Sockets.TcpClient]::new()
        $iar = $client.BeginConnect($HostName, $Port, $null, $null)
        $success = $iar.AsyncWaitHandle.WaitOne($TimeoutMs, $false)
        if ($success) {
            $client.EndConnect($iar) | Out-Null
            $client.Close()
            return $true
        }
        $client.Close()
    } catch {}

    return $false
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$additionalContext = if (Test-TcpPortOpen) {
    "JetBrains MCP note: intellij-index appears reachable at 127.0.0.1:29170. For semantic ePC-SAFT code work, load `$jetbrains, call ide_index_status once with project_path=`"$repoRoot`", prefer IDE definitions/references/diagnostics/refactors, and fall back only when the task is simple docs/status work or the user approves fallback."
} else {
    "JetBrains MCP note: intellij-index was not reachable at 127.0.0.1:29170. For non-trivial ePC-SAFT code, build, native, test, refactor, debug, architecture, or validation work, ask the user to open or focus IntelliJ on this repo before using shell fallback."
}

@{
    continue = $true
    systemMessage = "ePC-SAFT SessionStart hook active."
    hookSpecificOutput = @{
        hookEventName = "SessionStart"
        additionalContext = $additionalContext
    }
} | ConvertTo-Json -Depth 5 -Compress
