---
issue: 302
title: "M4: add electrolyte charge-neutral TPD gate"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/302"
state: "closed"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "closed"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
source_plan: "docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0302-electrolyte-charge-neutral-tpd-gate-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0302-electrolyte-tpd-gate
last_synced: "2026-06-25"
---

# M4: add electrolyte charge-neutral TPD gate

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/302
**Pull Request:** https://github.com/ePC-SAFT/ePC-SAFT/pull/303
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0302-electrolyte-charge-neutral-tpd-gate-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/302 using docs/superpowers/issues/2026-06-24-m4-equilibrium-issue-0302-add-electrolyte-charge-neutral-tpd-gate.md and docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0302-electrolyte-charge-neutral-tpd-gate-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Auto Mode
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Current thread owns PR
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0302-electrolyte-charge-neutral-tpd-gate-plan.md#outcome-proof
**Intent:** Replace the remaining electrolyte TPD evidence blocker with a retained native-backed charge-neutral screening gate while leaving full HELD2 discovery and public electrolyte admission behind later proof gates.
**Target Output:** `scripts/validation/check_electrolyte_tpd_gate.py --json --require-source-gate --require-held2-readiness --require-native-tpd --require-public-routes-closed --require-complete` returns `complete: true` with finite TPD and charge-neutral candidate metrics.
**Owner:** M4 equilibrium package owner.
**Interface:** Native `_native_electrolyte_tpd_phase_discovery` binding, retained validation checker JSON, pytest contracts, M4 issue mirror, and M4 milestone tracker.
**Cutover:** The new checker becomes the next #191 child proof oracle; #191 remains blocked by HELD2 dual phase discovery, Stage III electrolyte refinement, postsolve electrolyte phase-set certification, and public electrolyte route admission.
**Replaced Path:** The charged-system postsolve hole where neutral TPD is the only available certificate is displaced for validation by a charge-neutral electrolyte-specific TPD screening gate.
**Acceptance Proof:** Acceptance is proven when native diagnostics produce charge-neutral finite candidates for the source-backed Khudaida fixture, the checker has `complete: true`, public `electrolyte_lle` remains closed, and the PR closes this issue.
**Stop Criteria:** Stop if native pressure-root trial phases cannot be evaluated for the source fixture, if any candidate composition violates charge residual `1.0e-8`, if the gate opens public electrolyte routes, or if solving full HELD2 candidate discovery becomes necessary to satisfy this slice.
**Avoid:** Do not add public electrolyte routes, full HELD2 dual-loop discovery, Stage III route refinement, electrolyte postsolve admission, reactive routes, regression work, downstream study logic, or release claims.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add a native charge-neutral electrolyte TPD screening diagnostic and retained checker that consumes the #269 source gate and #300 HELD2 readiness gate before granting completion. Keep public electrolyte route admission closed.

## Parent And Dependencies

- Parent issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Blocks: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Blocked by: None.

## Acceptance Criteria

- [x] A GitHub child issue and local mirror exist for the electrolyte charge-neutral TPD gate and block #191.
- [x] Native equilibrium exposes `_native_electrolyte_tpd_phase_discovery` with charge-neutral candidate screening for source-backed electrolyte compositions.
- [x] Candidate TPD values are finite, candidate count is positive, selected candidate count is positive, and maximum candidate charge residual is <= `1.0e-8`.
- [x] The retained checker consumes #269 source evidence and #300 readiness evidence before granting electrolyte TPD gate completion.
- [x] The checker reports `readiness_only: true`, `full_held2_claimed: false`, and public electrolyte routes remain closed.
- [x] #191 and M4 README show this child closed after merge and list the remaining HELD2/postsolve/public-admission blockers.

## Resolution Evidence

The retained checker completes with `complete: true` and no blockers for the
source-backed Khudaida electrolyte LLE fixture. The native screening payload
reports:

- Native binding: `_native_electrolyte_tpd_phase_discovery`
- Screening backend: `charge_neutral_deterministic_tpd_candidate_screening`
- Candidate count: `3`
- Selected candidate count: `2`
- Candidate TPD values: `0.0`, `0.017850655639200044`, `-0.010922388988229025`
- Minimum TPD: `-0.010922388988229025`
- Maximum candidate charge residual: `0.0`
- Candidate mass-balance norm: `2.7755575615628914e-17`
- HELD2 status: `readiness_only: true`, `full_held2_claimed: false`
- Remaining gates: HELD2 dual phase discovery, Stage III electrolyte
  refinement, postsolve electrolyte phase-set certification, and public
  electrolyte route admission

The negative TPD candidate is retained as instability-screening evidence and a
source-backed candidate seed. It is not a full electrolyte phase split,
postsolve certificate, or public route admission.

## Non-Goals

- No public `electrolyte_lle` route admission.
- No full HELD2 dual-loop or Stage III electrolyte route refinement.
- No charged-system postsolve certification cutover.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.
- No provider EOS rewrite.

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-06-24-m4-equilibrium-issue-0302-electrolyte-charge-neutral-tpd-gate-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-06-24-m4-equilibrium-issue-0302-electrolyte-charge-neutral-tpd-gate-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python scripts/validation/check_electrolyte_tpd_gate.py --json --require-source-gate --require-held2-readiness --require-native-tpd --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_tpd_gate.py tests/native/contracts/test_electrolyte_held2_readiness_checker.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
