# M4 CE: add EOS nonideality diagnostic matrix

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/402
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-robustness-followup-audit-findings.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,backend:cppad,validation
**Goal Command:** /goal Add EOS x-phi and x-gamma diagnostic matrix evidence without overstating MEA nonideality validation.
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
**Intent:** EOS nonideality evidence should cover both activity modes while clearly stating its capability boundary.
**Target Output:** Matrix evidence reports `eos_x_phi` and `eos_x_gamma` activity mode, derivative backend, continuation trace, status, exact failure class, and capability boundary.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Native EOS diagnostics tests, API diagnostics tests, and follow-up checker JSON.
**Cutover:** Explicit EOS diagnostic-matrix evidence replaces thin EOS activity claims.
**Replaced Path:** Ambiguous EOS support evidence is displaced by mode-by-mode proof and boundary reporting.
**Acceptance Proof:** Focused EOS/API tests and the follow-up checker prove both modes and avoid MEA-level nonideality claims.
**Stop Criteria:** Stop if completing this issue requires source-backed MEA EOS nonideality data.
**Avoid:** Do not claim literature MEA EOS nonideality validation in this tranche.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Keep current CE worktree until all loop issues finish
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 7 from the source plan: add EOS nonideality diagnostic matrix evidence for `eos_x_phi` and `eos_x_gamma`.

## Acceptance Criteria

- [ ] Focused EOS/API tests cover `eos_x_phi` and `eos_x_gamma` diagnostic matrix rows.
- [ ] Follow-up checker distinguishes synthetic EOS evidence from source-backed MEA nonideality validation.
- [ ] Final evidence includes derivative backend and exact proof or failure status.

## Resolution Evidence

- Native EOS tests cover `eos_x_phi` fugacity activity and `eos_x_gamma` activity coefficient paths with derivative backend evidence.
- The follow-up checker reports the explicit capability boundary `synthetic_eos_activity_diagnostics_not_literature_mea_nonideality`.
- The checker matrix records `cppad_implicit` for `eos_x_phi` and `cppad_implicit_activity_coefficient` for `eos_x_gamma`.
- Fresh proof: the combined focused pytest command passed with 44 tests.
- Fresh proof: `uv run --no-sync python scripts/validation/check_ce_robustness_followup.py --json --require-complete` returned `status=complete`, `blocker_count=0`, `finding_count=7`.

## Blocked by

- None

## Non-goals

- Duplicate MEA plot output.
- CPE, reactive LLE, or phase-equilibrium admission.
- Downstream application metrics.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-issue-mirror.ps1 -IssueFile docs/superpowers/issues/2026-06-30-m4-ce-issue-0402-eos-nonideality-diagnostic-matrix.md
- uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py -q
- uv run --no-sync python scripts/validation/check_ce_robustness_followup.py --json --require-complete
