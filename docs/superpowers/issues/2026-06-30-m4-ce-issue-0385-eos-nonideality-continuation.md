# M4 CE: add EOS nonideality continuation

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/385
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-convergence-robustness-hardening.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,backend:cppad,validation
**Goal Command:** /goal Add CE continuation from ideal mole-fraction activity to ePC-SAFT EOS-derived activity with final EOS proof.
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
**Intent:** Add an activity continuation path that stages nonideal CE from ideal activity to ePC-SAFT EOS-derived activity.
**Target Output:** Nonideal CE diagnostics show an activity lambda trace and accept only the final EOS-derived objective with CppAD-backed derivative evidence.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** CE objective provider, EOS activity context, standard-state validation, native diagnostics, and nonideal CE tests.
**Cutover:** Brittle direct-jump EOS activity solves gain a CE-owned continuation path while preserving final EOS proof.
**Replaced Path:** Direct nonideal proof attempts without activity staging are no longer the only nonideal path for hard points.
**Acceptance Proof:** Focused EOS activity tests prove the trace reaches full EOS activity and reports CppAD derivative evidence for the accepted result.
**Stop Criteria:** Stop if EOS activity derivative evidence is missing or if the path can accept an ideal staging result as final proof.
**Avoid:** Do not add toy gamma models, phase splitting, CPE admission, or provider API broadening.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 3 from the source plan: nonideality continuation from ideal activity to full ePC-SAFT EOS-derived activity.

## Acceptance Criteria

- [ ] Tests require an activity lambda trace from ideal activity to full EOS-derived activity.
- [ ] Final accepted results report full EOS activity, not ideal staging activity.
- [ ] Diagnostics include CppAD-backed derivative evidence for the nonideal objective.
- [ ] Ideal CE behavior and diagnostics remain stable.

## Blocked by

- None

## Non-goals

- Toy activity models.
- CPE or phase-equilibrium route work.
- Relaxed standard-state validation.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- Focused EOS activity and standard-state commands from Task 3 of the source plan.
