---
issue: 423
title: "Normalize align-project closed mirror and milestone page hygiene"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/423
state: closed
milestone: "M0 - Governance"
project: "ePC-SAFT Roadmap"
package: governance
capability: workflow
backend: none
readiness: closed
release_target: governance
source_spec: null
source_plan: null
afk_hitl: AFK
branch: null
last_synced: "2026-07-02"
---

# Normalize align-project closed mirror and milestone page hygiene

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/423
**GitHub Milestone:** M0 - Governance
**Issue Type:** Task
**Source Spec:** None
**Source Plan:** docs/superpowers/plans/2026-07-02-m0-align-project-legacy-hygiene-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Mirror Retention:** Keep
**Labels:** agent-ready, docs, area:docs, status:ready, type:task
**Goal Command:** /goal Resolve issue #423 by normalizing align-project closed mirror lifecycle evidence and reconciling milestone-page discovery without changing product code.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety plus proof oracle

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-02-m0-align-project-legacy-hygiene-plan.md#outcome-proof
**Intent:** Turn the remaining align-project findings after the Khudaida M6 hierarchy repair into one AFK governance repair.
**Target Output:** Parser-compatible closed mirror lifecycle evidence and milestone page discovery evidence for the remaining align-project findings.
**Owner:** M0 governance owns project workflow metadata, tracker hygiene, issue mirrors, and align-project audit compatibility.
**Interface:** `docs/superpowers/issues`, `docs/superpowers/milestones`, the historical GitHub tracker, and the align-project audit output.
**Cutover:** Keep the merged Khudaida M6 hierarchy as-is; route only the remaining legacy cleanup through this M0 issue.
**Replaced Path:** Opportunistic broad edits during unrelated issue work.
**Acceptance Proof:** The issue closes only when the GitHub-aware align audit has no blocking findings and no repairables for closed mirror lifecycle or milestone page discovery, with a clean worktree and docs validation.
**Stop Criteria:** Stop and revise if retention vocabulary is ambiguous, if closed mirrors should be deleted instead of retained, or if the milestone page finding requires a plugin/script contract change outside repo-owned docs.
**Avoid:** Do not alter product code, solver behavior, validation artifacts, issue close state, or milestone assignment while repairing workflow metadata. Do not mask a script-layout mismatch by duplicating canonical milestone truth.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Repair the remaining align-project governance findings from the PR #422
closeout audit: 52 legacy closed-mirror lifecycle findings and 9 milestone-page
findings, while keeping the Khudaida M6 hierarchy unchanged.

## Acceptance Criteria

- [ ] Run `align-project -Mode GitHubAware` and retain the before/after repairable counts.
- [ ] Classify the 52 closed-mirror lifecycle findings as retain or remove, with explicit evidence for any deletion.
- [ ] Make retained closed mirrors parser-compatible without changing issue close state.
- [ ] Reconcile the 9 milestone-page findings with the repo's `docs/superpowers/milestones/M*/README.md` layout, or stop with a precise script-contract blocker.
- [ ] Final GitHub-aware align audit has no repairables in `closed-mirror-lifecycle` or `milestone-membership`.
- [ ] Docs validation, changed mirror validation, `git diff --check`, and cleanup hook pass.

## Blocked by

- None.

## Non-goals

- No product code changes.
- No solver, validation-data, figure-artifact, package, or native build changes.
- No issue close-state changes.
- No duplicate canonical milestone source files merely to satisfy a scanner.

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File <align-project>\scripts\align-project.ps1 -RepoRoot . -Mode GitHubAware
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <changed mirror>
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-02-m0-align-project-legacy-hygiene-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-02-m0-align-project-legacy-hygiene-plan.md
uv run --no-sync python scripts\dev\validate_project.py docs
git diff --check
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body Text

This issue owns the remaining align-project hygiene findings after PR #422
merged the Khudaida M6 hierarchy repair. It should normalize retained closed
mirror lifecycle evidence and reconcile milestone-page discovery with the
repo's current milestone README layout without changing product code, issue
close state, or canonical milestone truth.
