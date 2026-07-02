# M4 CE: add assistance summary diagnostics

**Mirror Retention:** retain
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/399
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-robustness-followup-audit-findings.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Expose how assisted each CE solve was as a compact diagnostics object.
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
**Intent:** Users should be able to tell how assisted a CE solve was from one stable diagnostic summary.
**Target Output:** `assistance_summary` reports level, mechanisms, seed source, final proof source, stage counts, corrector use, and escalation status.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Public CE result diagnostics and follow-up checker evidence.
**Cutover:** Status displays and reviews consume `assistance_summary` instead of manually combining scattered fields.
**Replaced Path:** Manual assistance inference from seed, homotopy, correction, and activity diagnostics is displaced by one summary contract.
**Acceptance Proof:** Focused API tests prove direct, caller-seed fallback, homotopy/corrector, and EOS activity summaries.
**Stop Criteria:** Stop if a summary value would imply success without final proof evidence.
**Avoid:** Do not remove detailed diagnostics that are still useful for root cause analysis.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Keep current CE worktree until all loop issues finish
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 4 from the source plan: add first-class assistance summary diagnostics.

## Acceptance Criteria

- [ ] Direct, caller-seed fallback, homotopy/corrector, and EOS activity paths each report a stable assistance summary.
- [ ] Detailed diagnostics remain available for root-cause analysis.
- [ ] Focused API tests no longer need to infer assistance from scattered fields.

## Resolution Evidence

- Public CE diagnostics now include `assistance_summary` with level, mechanisms, seed source, final proof source, stage counts, corrector use, caller-seed escalation status, activity model, and activity derivative backend.
- Focused API tests cover direct, caller-seed-escalated, proof-corrected, and EOS activity-assisted summaries.
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
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-issue-mirror.ps1 -IssueFile docs/superpowers/issues/2026-06-30-m4-ce-issue-0399-assistance-summary-diagnostics.md
- uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py -q
- uv run --no-sync python scripts/validation/check_ce_robustness_followup.py --json --require-complete
