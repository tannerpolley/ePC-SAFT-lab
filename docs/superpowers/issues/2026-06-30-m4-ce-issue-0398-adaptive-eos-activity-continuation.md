# M4 CE: add adaptive EOS activity continuation

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/398
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-robustness-followup-audit-findings.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,backend:cppad,validation
**Goal Command:** /goal Replace the fixed EOS activity continuation ladder with an adaptive controller that records accepted and rejected steps.
**Branch:** codex/m4-ce-generic-pope-homotopy-continuation
**Execution Mode:** Looping Mode
**Worktree Policy:** Current CE worktree
**Integration Policy:** Current thread owns PR
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety and proof

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md#outcome-proof
**Intent:** EOS activity continuation should adapt to rejected steps while preserving easy-case behavior.
**Target Output:** Diagnostics expose accepted and rejected activity steps, min step, max stage, and final full-EOS proof evidence.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Native CE continuation result payloads, pybind diagnostics, and EOS activity tests.
**Cutover:** Adaptive controller evidence replaces fixed-grid robustness assumptions.
**Replaced Path:** The hard-coded three-point activity grid no longer defines the only continuation behavior.
**Acceptance Proof:** Focused native EOS tests prove easy-case trace preservation and rejected-step recovery evidence.
**Stop Criteria:** Stop if adaptive continuation would accept an intermediate activity state as final proof.
**Avoid:** Do not weaken final EOS proof or broaden provider APIs.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Keep current CE worktree until all loop issues finish
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 3 from the source plan: add adaptive EOS activity continuation with accepted/rejected trace evidence.

## Acceptance Criteria

- [ ] Easy EOS cases still show the normal 0.0 -> 0.5 -> 1.0 trace when it succeeds.
- [ ] Hard EOS cases can record rejected steps and recovered accepted steps.
- [ ] Native EOS activity tests prove final full-EOS proof evidence remains strict.

## Resolution Evidence

- Native EOS activity continuation now uses `adaptive_bisection` with `minimum_step=0.125` and `maximum_stage_count=20`.
- Continuation diagnostics expose `accepted_activity_steps` and `rejected_activity_steps`; the easy `eos_x_gamma` case preserves `[0.0, 0.5, 1.0]` with no rejected steps.
- Fresh proof: `uv run --no-sync python scripts/dev/build_epcsaft.py --build-only --parallel 10` completed and native import passed after the C++ changes.
- Fresh proof: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py` passed inside the 44-test combined focused run.

## Blocked by

- None

## Non-goals

- Duplicate MEA plot output.
- CPE, reactive LLE, or phase-equilibrium admission.
- Downstream application metrics.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-issue-mirror.ps1 -IssueFile docs/superpowers/issues/2026-06-30-m4-ce-issue-0398-adaptive-eos-activity-continuation.md
- uv run --no-sync python scripts/dev/build_epcsaft.py --build-only --parallel 10
- uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py -q
