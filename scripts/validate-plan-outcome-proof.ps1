param(
    [string]$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path,
    [Parameter(Mandatory = $true)]
    [string]$PlanPath
)

$ErrorActionPreference = "Stop"

$OutcomeProofFields = @(
    "Intent",
    "Current Behavior",
    "Expected Outcome",
    "Target Output",
    "Owner",
    "Interface",
    "Cutover",
    "Replaced Path",
    "Evidence",
    "Acceptance Proof",
    "Stop Criteria",
    "Avoid",
    "Risk"
)

$ImplementationBoundaryFields = @(
    "Files To Create",
    "Files To Modify",
    "Files To Avoid",
    "Source Of Truth",
    "Read Path",
    "Write Path",
    "Integration Points",
    "Migration Or Cutover",
    "Replaced Path Handling",
    "Acceptance Proof Gate"
)

function Resolve-RepoPath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $rootFull = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Root).Path)
    if ([IO.Path]::IsPathRooted($Path)) {
        $candidate = [IO.Path]::GetFullPath($Path)
    } else {
        $candidate = [IO.Path]::GetFullPath((Join-Path $rootFull $Path))
    }
    if (-not $candidate.StartsWith($rootFull + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -and $candidate -ne $rootFull) {
        throw "plan path is outside repo root: $candidate"
    }
    $candidate
}

function Get-MarkdownSection {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Name
    )

    $escaped = [regex]::Escape($Name)
    $pattern = "(?ims)^\s{0,3}##\s+$escaped\s*$\r?\n(?<body>.*?)(?=^\s{0,3}##\s+|\z)"
    $match = [regex]::Match($Text, $pattern)
    if (-not $match.Success) {
        return $null
    }
    $match.Groups["body"].Value
}

function Get-OutcomeFieldValue {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Name
    )

    $escaped = [regex]::Escape($Name)
    $patterns = @(
        "(?im)^\s*\*\*$escaped\s*:\s*\*\*\s*(.+?)\s*$",
        "(?im)^\s*\*\*$escaped\*\*\s*:\s*(.+?)\s*$",
        "(?im)^\s*$escaped\s*:\s*(.+?)\s*$"
    )
    foreach ($pattern in $patterns) {
        $match = [regex]::Match($Text, $pattern)
        if ($match.Success) {
            return $match.Groups[1].Value.Trim()
        }
    }
    $null
}

function Test-ConcreteValue {
    param(
        [Parameter(Mandatory = $true)][string]$Field,
        [AllowNull()][string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return [pscustomobject]@{ ok = $false; reason = "$Field is empty" }
    }
    $trimmed = $Value.Trim()
    if ($trimmed -match '^(tbd|none|n/a|na|not applicable|same as above|-)$') {
        return [pscustomobject]@{ ok = $false; reason = "$Field uses a generic value" }
    }
    if ($Field -eq "Acceptance Proof" -and $trimmed -match '^(tests?\s+pass(?:ed)?|unit tests?\s+pass(?:ed)?|lint\s+pass(?:ed)?|diff\s+reviewed)$') {
        return [pscustomobject]@{ ok = $false; reason = "Acceptance Proof must name target behavior, not only test status" }
    }
    [pscustomobject]@{ ok = $true; reason = "passed" }
}

function Test-Fields {
    param(
        [Parameter(Mandatory = $true)][string]$SectionText,
        [Parameter(Mandatory = $true)][string[]]$Fields,
        [Parameter(Mandatory = $true)][string]$SectionName
    )

    $values = [ordered]@{}
    foreach ($field in $Fields) {
        $value = Get-OutcomeFieldValue -Text $SectionText -Name $field
        $check = Test-ConcreteValue -Field $field -Value $value
        if (-not $check.ok) {
            return [pscustomobject]@{ ok = $false; reason = "$SectionName $($check.reason)"; fields = $values }
        }
        $values[$field] = $value
    }
    [pscustomobject]@{ ok = $true; reason = "passed"; fields = $values }
}

function Get-TaskUseCases {
    param([AllowEmptyString()][string[]]$Lines)

    $tasks = [System.Collections.Generic.List[object]]::new()
    for ($index = 0; $index -lt $Lines.Count; $index++) {
        $match = [regex]::Match($Lines[$index], '^\s{0,3}#{2,4}\s+Task\s+(?<number>\d+)\s*[:.-]\s*(?<title>.+?)\s*$')
        if ($match.Success) {
            $tasks.Add([pscustomobject]@{ number = [int]$match.Groups["number"].Value; title = $match.Groups["title"].Value; start = $index }) | Out-Null
        }
    }

    $useCases = [System.Collections.Generic.List[string]]::new()
    for ($taskIndex = 0; $taskIndex -lt $tasks.Count; $taskIndex++) {
        $start = $tasks[$taskIndex].start
        $end = if ($taskIndex + 1 -lt $tasks.Count) { $tasks[$taskIndex + 1].start } else { $Lines.Count }
        $block = @($Lines[$start..($end - 1)])
        $useCaseIndex = -1
        for ($lineIndex = 0; $lineIndex -lt $block.Count; $lineIndex++) {
            if ($block[$lineIndex] -match '^\s*\*\*Use Cases:\*\*\s*$') {
                $useCaseIndex = $lineIndex
                break
            }
        }
        if ($useCaseIndex -lt 0) {
            continue
        }
        for ($lineIndex = $useCaseIndex + 1; $lineIndex -lt $block.Count; $lineIndex++) {
            $line = [string]$block[$lineIndex]
            if ($line -match '^\s{0,3}#{1,6}\s+' -or $line -match '^\s*\*\*[^*]+:\*\*\s*$') {
                break
            }
            if ($line -match '^\s*[-*]\s+\S' -or $line -match '^\s*\d+\.\s+\S') {
                $useCases.Add($line.Trim()) | Out-Null
            }
        }
    }
    @($useCases)
}

function Test-TaskUseCaseOutcomeCoverage {
    param([Parameter(Mandatory = $true)][string]$Text)

    $lines = [string[]]($Text -split "\r?\n")
    $useCases = @(Get-TaskUseCases -Lines $lines)
    if ($useCases.Count -eq 0) {
        return [pscustomobject]@{ ok = $false; reason = "Task # Use Cases are required to cover outcome evidence and cutover" }
    }

    $combined = ($useCases -join "`n").ToLowerInvariant()
    $hasEvidence = $combined -match 'acceptance|evidence|proof|validator|visible|diagnostic|checker'
    $hasCutover = $combined -match 'cutover|displaced|migration|old path|duplicate|retire|replace|replaced|shared tracer'
    if (-not $hasEvidence -or -not $hasCutover) {
        return [pscustomobject]@{ ok = $false; reason = "Task # Use Cases must cover acceptance evidence and cutover or replaced path handling" }
    }
    [pscustomobject]@{ ok = $true; reason = "passed"; use_case_count = $useCases.Count }
}

try {
    $repoRootFull = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $RepoRoot).Path)
    $planFull = Resolve-RepoPath -Root $repoRootFull -Path $PlanPath
    if (-not (Test-Path -LiteralPath $planFull -PathType Leaf)) {
        throw "plan does not exist: $PlanPath"
    }

    $relativePlan = ([IO.Path]::GetRelativePath($repoRootFull, $planFull) -replace '\\', '/')
    if (-not $relativePlan.StartsWith("docs/superpowers/plans/", [StringComparison]::OrdinalIgnoreCase)) {
        throw "plan must be under docs/superpowers/plans: $relativePlan"
    }

    $text = Get-Content -LiteralPath $planFull -Raw
    $outcomeSection = Get-MarkdownSection -Text $text -Name "Outcome Proof"
    if ($null -eq $outcomeSection) {
        throw "missing ## Outcome Proof"
    }
    $outcome = Test-Fields -SectionText $outcomeSection -Fields $OutcomeProofFields -SectionName "Outcome Proof"
    if (-not $outcome.ok) {
        throw $outcome.reason
    }

    $boundarySection = Get-MarkdownSection -Text $text -Name "Implementation Boundaries"
    if ($null -eq $boundarySection) {
        throw "missing ## Implementation Boundaries"
    }
    $boundary = Test-Fields -SectionText $boundarySection -Fields $ImplementationBoundaryFields -SectionName "Implementation Boundaries"
    if (-not $boundary.ok) {
        throw $boundary.reason
    }

    $coverage = Test-TaskUseCaseOutcomeCoverage -Text $text
    if (-not $coverage.ok) {
        throw $coverage.reason
    }

    [pscustomobject]@{
        ok = $true
        phase = "plan-outcome-proof"
        plan_path = $relativePlan
        reason = "outcome proof passed"
        use_case_count = $coverage.use_case_count
        fields = [ordered]@{
            outcome_proof = $outcome.fields
            implementation_boundaries = $boundary.fields
        }
    } | ConvertTo-Json -Depth 8
} catch {
    [pscustomobject]@{
        ok = $false
        phase = "plan-outcome-proof"
        reason = $_.Exception.Message
    } | ConvertTo-Json -Depth 8
    exit 1
}
