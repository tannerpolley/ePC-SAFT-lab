# M4 CE: strengthen final proof corrector for reaction stationarity

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/384
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-convergence-robustness-hardening.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Strengthen CE final proof correction so feasible hard points pass strict reaction-stationarity gates or fail with proof diagnostics.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Current thread owns PR
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md#outcome-proof
**Intent:** Add a final proof-correction path that improves strict reaction stationarity after feasibility and homotopy have produced a candidate.
**Target Output:** Accepted CE results report unscaled physical reaction stationarity and balance below strict gates, with correction attempts visible in diagnostics.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Native CE proof solve, CE diagnostics payload, and focused native/API stationarity tests.
**Cutover:** Final acceptance depends on corrected true-objective proof, not on a feasible intermediate stage.
**Replaced Path:** One-shot proof solves that leave feasible candidates above the stationarity gate are displaced by correction plus strict rejection.
**Acceptance Proof:** A regression that previously failed the reaction-stationarity gate passes after correction, or fails with the explicit correction failure class.
**Stop Criteria:** Stop if the correction requires relaxing stationarity tolerances or accepting an intermediate homotopy stage.
**Avoid:** Do not hide correction failure, weaken proof thresholds, or add public solver strategy routes.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 2 from the source plan: a strict final proof corrector for reaction stationarity with diagnostics and regression tests.

## Acceptance Criteria

- [ ] A focused failing regression captures a feasible CE point that misses stationarity before correction.
- [ ] Final accepted results come only from the true final objective.
- [ ] Diagnostics include correction attempts, final stationarity, final balance, and rejection reason.
- [ ] Strict stationarity and balance thresholds are not weakened.

## Blocked by

- None

## Non-goals

- New public Pope, homotopy, or corrector routes.
- Plot generation.
- CPE or phase-equilibrium admission.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- Focused native/API commands from Task 2 of the source plan.
