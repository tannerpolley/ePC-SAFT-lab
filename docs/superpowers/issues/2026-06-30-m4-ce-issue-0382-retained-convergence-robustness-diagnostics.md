# M4 CE: add retained convergence robustness diagnostics

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/382
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-convergence-robustness-hardening.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Add retained machine-readable CE convergence robustness diagnostics without creating duplicate plot deliverables.
**Branch:** codex/m4-ce-generic-pope-homotopy-continuation
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Current thread owns PR
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md#outcome-proof
**Intent:** Add retained CSV/JSON diagnostics that make standalone CE convergence robustness measurable across hard MEA and synthetic stress points.
**Target Output:** Maintainers can inspect retained rows for stationarity, balance, seed source, activity path, stage count, final proof status, and failure class without relying on plots.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Retained CE diagnostics artifacts, CE checker output, and `ReactiveSpeciationResult.diagnostics`.
**Cutover:** Machine-readable robustness diagnostics become the proof surface for convergence claims.
**Replaced Path:** Plot-only inspection and one-off pointwise solver notes no longer count as robustness proof.
**Acceptance Proof:** Focused tests and the standalone CE checker require the retained diagnostics and prove strict metrics are present.
**Stop Criteria:** Stop if the implementation needs duplicate plot output or cannot tie diagnostics to final proof status.
**Avoid:** Do not add public routes, MEA-specific package APIs, or phase-equilibrium claims.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 1 from the source plan: retained CE robustness diagnostics for hard CE points, with checker coverage and no duplicate plot deliverables.

## Acceptance Criteria

- [ ] Retained diagnostics record stationarity, balance, seed source, activity model, stage count, final proof status, and failure class.
- [ ] Focused API or checker tests fail before the diagnostics exist and pass after implementation.
- [ ] Standalone CE checker requires the retained diagnostics for completion.
- [ ] The change does not add new plot artifacts unless the source plan is explicitly revised.

## Blocked by

- None

## Non-goals

- New public CE routes.
- CPE, reactive LLE, or phase-equilibrium admission.
- Downstream MEA application metrics.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- Focused tests and checker commands from Task 1 of the source plan.
