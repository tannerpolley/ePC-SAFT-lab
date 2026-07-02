---
issue: 420
title: "M6: Paper validation campaign parent"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/420"
state: "open"
milestone: "M6 - Validation"
project: "ePC-SAFT Roadmap"
package: "benchmark"
capability: "paper-validation"
backend: Null
readiness: "ready"
release_target: "validation"
source_spec: "docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md"
source_plan: "docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md"
afk_hitl: "AFK"
branch: codex/m6-khudaida-validation-reorg
last_synced: "2026-07-02"
---

# M6: Paper validation campaign parent

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/420
**GitHub Milestone:** M6 - Validation
**Issue Type:** Task
**Sub-Issue Role:** parent
**Child Issues:** https://github.com/ePC-SAFT/ePC-SAFT/issues/421
**Source Spec:** docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md
**Source Plan:** docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
**Classification:** AFK
**Labels:** docs, validation, area:benchmark, status:ready, type:task
**Goal Command:** /goal Maintain the M6 paper validation campaign hierarchy.
**Execution Mode:** Parent tracking issue
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required for child implementation slices

## Outcome Summary

Track executable paper-validation campaigns that prove retained literature
artifacts, plots, statistics, provenance, and capability evidence.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Maintain the parent issue hierarchy for paper-validation campaigns and keep
child paper parents routed to M6 validation rather than implementation
milestones.

## Acceptance Criteria

- [ ] Paper-validation child parents use M6 milestone and validation labels.
- [ ] Native GitHub sub-issue hierarchy lists #421 as this parent issue's
  child.
- [ ] Child campaigns open M4 or M5 blockers when validation exposes solver or
  parameter defects.
- [ ] Local mirrors and GitHub issue hierarchy remain aligned.

## Blocked By

- None.

## Blocking

- #421

## Non-goals

- No solver implementation in this parent issue.
- No parameter regression in this parent issue.
- No broad capability claim without child evidence.

## Proof Oracle

```powershell
gh issue view 420 --json number,title,milestone,subIssues
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
```
