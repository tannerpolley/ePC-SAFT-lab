param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath
)

$ErrorActionPreference = "Stop"

$resolved = Resolve-Path -LiteralPath $PlanPath -ErrorAction Stop
$content = Get-Content -LiteralPath $resolved.Path -Raw

$taskPattern = [regex]'(?ms)^### Task\s+\d+:.+?(?=^### Task\s+\d+:|^##\s+Proof Oracle|^##\s+Issue Creation Packet|^##\s+Risk Notes|\z)'
$tasks = $taskPattern.Matches($content)

$missing = New-Object System.Collections.Generic.List[string]

foreach ($task in $tasks) {
    $text = $task.Value
    $header = ($text -split "`n", 2)[0].Trim()
    $useIndex = $text.IndexOf("**Use Cases:**")
    $filesIndex = $text.IndexOf("**Files:**")
    if ($useIndex -lt 0 -or $filesIndex -lt 0 -or $useIndex -gt $filesIndex) {
        $missing.Add($header)
        continue
    }

    $useCaseBlock = $text.Substring($useIndex, $filesIndex - $useIndex)
    if ($useCaseBlock -notmatch '(?m)^-\s+\S') {
        $missing.Add($header)
    }
}

$result = [ordered]@{
    ok = ($tasks.Count -gt 0 -and $missing.Count -eq 0)
    plan_path = $resolved.Path
    task_count = $tasks.Count
    missing_use_case_count = $missing.Count
    missing_use_case_tasks = @($missing)
}

$result | ConvertTo-Json -Depth 4

if (-not $result.ok) {
    exit 1
}
