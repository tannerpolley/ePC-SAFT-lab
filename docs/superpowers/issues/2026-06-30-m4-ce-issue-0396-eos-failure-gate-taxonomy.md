# M4 CE: classify EOS activity failures by exact proof gate

**Mirror Retention:** retain
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/396
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-robustness-followup-audit-findings.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-robustness-followup-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Classify rejected EOS activity payloads by exact CE proof gate while preserving EOS context evidence.
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
**Intent:** EOS-context CE failures should report the exact failing proof gate, not only that EOS activity was active.
**Target Output:** Rejected EOS payloads retain activity context while reporting initialization, balance, stationarity, proof-corrector, or Ipopt failure classes.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** `ReactiveSpeciationResult.diagnostics`, CE native diagnostic payload adapter, and follow-up checker evidence.
**Cutover:** Exact proof-gate classes become the routing surface for EOS-context failures.
**Replaced Path:** The early generic EOS activity catch-all no longer masks the failing proof gate.
**Acceptance Proof:** Focused API tests and the follow-up checker prove exact EOS-context failure classes.
**Stop Criteria:** Stop if exact proof classification requires weakening final proof gates.
**Avoid:** Do not remove EOS context metadata or add new public solver routes.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Keep current CE worktree until all loop issues finish
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 1 from the source plan: reorder CE failure classification so exact proof gates outrank the EOS-context fallback while preserving EOS activity context.

## Acceptance Criteria

- [ ] EOS-context failures preserve activity context metadata.
- [ ] Focused API tests prove stationarity, balance, proof-corrector, initialization, and Ipopt-shaped payloads classify by exact gate.
- [ ] The follow-up checker consumes exact failure classes instead of a generic EOS catch-all.

## Resolution Evidence

- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py` now classifies initialization, balance, stationarity, proof-corrector, and Ipopt failures before the EOS-context fallback.
- EOS activity failures preserve `failure_context: eos_activity` while exact gates drive `failure_class`.
- Fresh proof: `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py tests/native/contracts/test_standalone_ce_gate.py tests/native/contracts/test_ce_robustness_followup_gate.py -q` passed with 44 tests.
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
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-issue-mirror.ps1 -IssueFile docs/superpowers/issues/2026-06-30-m4-ce-issue-0396-eos-failure-gate-taxonomy.md
- uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py -q
- uv run --no-sync python scripts/validation/check_ce_robustness_followup.py --json --require-complete
