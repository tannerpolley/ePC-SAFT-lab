param(
    [Parameter(Mandatory = $true)]
    [string]$IssueFile,
    [string]$RepoRoot = ".",
    [switch]$MilestoneRequired
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$resolvedRoot = (Resolve-Path -LiteralPath $RepoRoot -ErrorAction Stop).Path
$candidateIssuePath = if ([System.IO.Path]::IsPathRooted($IssueFile)) {
    $IssueFile
}
else {
    Join-Path $resolvedRoot $IssueFile
}
$resolvedIssue = (Resolve-Path -LiteralPath $candidateIssuePath -ErrorAction Stop).Path

$rootFull = [System.IO.Path]::GetFullPath($resolvedRoot).TrimEnd(
    [System.IO.Path]::DirectorySeparatorChar,
    [System.IO.Path]::AltDirectorySeparatorChar
)
$rootPrefix = "$rootFull$([System.IO.Path]::DirectorySeparatorChar)"
$issueFull = [System.IO.Path]::GetFullPath($resolvedIssue)
if ($issueFull -ne $rootFull -and -not $issueFull.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Issue mirror must be inside repo root: $IssueFile"
}

$relativePath = [System.IO.Path]::GetRelativePath($rootFull, $issueFull).Replace("\", "/")
$text = Get-Content -LiteralPath $issueFull -Raw -ErrorAction Stop
$errors = New-Object System.Collections.Generic.List[string]

function Add-MirrorError {
    param([Parameter(Mandatory = $true)][string]$Message)
    $errors.Add($Message)
}

function Get-MetadataValue {
    param([Parameter(Mandatory = $true)][string]$Name)

    $pattern = "(?m)^\*\*{0}:\*\*\s*(.+?)\s*$" -f [regex]::Escape($Name)
    $match = [regex]::Match($text, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value.Trim()
    }
    return $null
}

if ($relativePath -notmatch "^docs/superpowers/issues/.+\.md$") {
    Add-MirrorError "mirror must live under docs/superpowers/issues"
}

$fileIssueNumber = $null
$fileName = [System.IO.Path]::GetFileName($issueFull)
if ($fileName -match "issue-(\d{4})-") {
    $fileIssueNumber = [int]$Matches[1]
}
else {
    Add-MirrorError "filename must include issue-####"
}

$titleMatch = [regex]::Match($text, "(?m)^#\s+(.+?)\s*$")
$title = $null
if ($titleMatch.Success) {
    $title = $titleMatch.Groups[1].Value.Trim()
}
else {
    Add-MirrorError "mirror must start with an H1 title"
}

$requiredMetadata = @(
    "GitHub Issue",
    "GitHub Milestone",
    "Issue Type",
    "Source Spec",
    "Source Plan",
    "Classification",
    "Labels",
    "Goal Command",
    "Execution Mode",
    "Worktree Policy",
    "Integration Policy",
    "TDD Policy"
)
$metadata = [ordered]@{}
foreach ($name in $requiredMetadata) {
    $value = Get-MetadataValue $name
    $metadata[$name] = $value
    if ([string]::IsNullOrWhiteSpace($value)) {
        Add-MirrorError "missing metadata: $name"
    }
}

$issueNumber = $null
$issueUrl = $metadata["GitHub Issue"]
if (-not [string]::IsNullOrWhiteSpace($issueUrl)) {
    if ($issueUrl -match "^https://github\.com/ePC-SAFT/ePC-SAFT/issues/(\d+)$") {
        $issueNumber = [int]$Matches[1]
        if ($null -ne $fileIssueNumber -and $issueNumber -ne $fileIssueNumber) {
            Add-MirrorError "filename issue number does not match GitHub issue URL"
        }
    }
    else {
        Add-MirrorError "GitHub Issue metadata must use the canonical ePC-SAFT issue URL"
    }
}

if ($MilestoneRequired -and [string]::IsNullOrWhiteSpace($metadata["GitHub Milestone"])) {
    Add-MirrorError "GitHub Milestone metadata is required"
}

$labels = $metadata["Labels"]
if (-not [string]::IsNullOrWhiteSpace($labels)) {
    foreach ($requiredLabelPrefix in @("type:", "status:")) {
        if ($labels -notmatch "(^|,)\s*$([regex]::Escape($requiredLabelPrefix))") {
            Add-MirrorError "Labels metadata must include $requiredLabelPrefix"
        }
    }
}

foreach ($section in @("Outcome Summary", "Project Merge", "What To Build", "Acceptance Criteria", "Blocked by", "Non-goals", "Proof Oracle")) {
    if ($text -notmatch "(?m)^##\s+$([regex]::Escape($section))\s*$") {
        Add-MirrorError "missing section: $section"
    }
}

if ($text -notmatch "(?m)^-\s+\[\s\]\s+\S") {
    Add-MirrorError "Acceptance Criteria must include unchecked checklist items"
}

if ($text -notmatch "validate-plan-task-use-cases\.ps1") {
    Add-MirrorError "Proof Oracle must include validate-plan-task-use-cases.ps1"
}
if ($text -notmatch "validate-plan-outcome-proof\.ps1") {
    Add-MirrorError "Proof Oracle must include validate-plan-outcome-proof.ps1"
}

$result = [ordered]@{
    ok = ($errors.Count -eq 0)
    issue_file = $relativePath
    issue_number = $issueNumber
    title = $title
    error_count = $errors.Count
    errors = @($errors)
}

$result | ConvertTo-Json -Depth 4

if (-not $result.ok) {
    exit 1
}
