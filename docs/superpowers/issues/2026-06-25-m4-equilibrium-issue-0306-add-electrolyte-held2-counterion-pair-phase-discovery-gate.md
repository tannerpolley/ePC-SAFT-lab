---
issue: 306
title: "M4: add electrolyte HELD2 counterion-pair phase-discovery gate"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/306"
state: "closed"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "closed"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
source_plan: "docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0306-electrolyte-held2-phase-discovery
last_synced: "2026-06-25"
---

# M4: add electrolyte HELD2 counterion-pair phase-discovery gate

**Mirror Retention:** retain
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/306
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md
**Classification:** AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/306 using docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0306-add-electrolyte-held2-counterion-pair-phase-discovery-gate.md and docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Auto Mode
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Current thread owns final PR review and merge
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md#outcome-proof
**Intent:** Replace the open HELD2 phase-discovery blocker with native diagnostics that use paper-derived reduced electroneutral coordinates.
**Target Output:** `scripts/validation/check_electrolyte_held2_phase_discovery.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-native-held2-discovery --require-public-routes-closed --require-complete` returns `complete: true` with full-rank counterion-pair, charge-neutral candidate, finite TPD, and mean-ionic bookkeeping evidence.
**Owner:** M4 equilibrium package owner.
**Interface:** Native `_native_electrolyte_held2_phase_discovery` binding, retained checker JSON, pytest contracts, M4 issue mirror, registry row, and M4 README.
**Cutover:** This checker becomes the #306 proof oracle; #191 remains blocked by #306 until it closes.
**Replaced Path:** The #302 charge-neutral TPD screen remains prerequisite seed evidence, but it no longer stands in for HELD2 phase discovery.
**Acceptance Proof:** Acceptance is proven when the native diagnostic records a full-rank `N_ch - 1` counterion-pair matrix, charge-neutral candidate rows, finite discovery metrics, mean-ionic residual bookkeeping, closed public route state, and explicit pending Stage III/postsolve/admission gates.
**Stop Criteria:** Stop if the counterion-pair matrix cannot be full rank, if candidate generation leaves the electroneutral subspace, if charged transfer equilibrium uses raw single-ion equality, or if public route admission is needed to satisfy this gate.
**Avoid:** Do not add Stage III electrolyte refinement, postsolve certification, public electrolyte routes, reactive routes, regression work, downstream study logic, or release claims.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add native HELD2 phase-discovery diagnostics in the reduced electroneutral
basis. The diagnostic must build and report the independent counterion-pair
matrix, generate charge-neutral candidate coordinates, record finite discovery
metrics, expose mean-ionic residual bookkeeping for later Stage III work, and
keep public electrolyte routes closed.

## Resolution Summary

The implementation adds native `_native_electrolyte_held2_phase_discovery`,
the retained `check_electrolyte_held2_phase_discovery.py` proof oracle, and
contract tests for single-salt, common-anion, and multivalent counterion-pair
matrices. The diagnostic consumes #269/#300/#302, reports full-rank
`N_ch - 1` counterion-pair matrices, charge-neutral lifted candidate rows,
finite reduced-TPD metrics, pair-based mean-ionic bookkeeping, and a Stage III
handoff record. Stage III refinement, postsolve certification, and public
electrolyte route admission remain separate #191 gates.

## Parent And Dependencies

- Parent issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Blocks: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- Blocked by: None.
- Prerequisite evidence consumed: #269, #300, and #302.

## Tightened Diagnostic Contract

The retained checker must require a native payload with these groups before it
can return `complete: true`:

- prerequisite gate receipts for #269, #300, and #302;
- charged species labels, charges, active charged indices, cation/anion
  indices, and feed ordering;
- counterion-pair labels, matrix, row sums, rank, expected rank `N_ch - 1`,
  rank tolerance, and transformed variable count;
- reduced-coordinate lift/back-lift residuals, per-phase charge residual
  maximum, composition-sum residual, and component nonnegativity margin;
- reduced TPD basis label, start counts, converged counts, selected candidate
  count, minimum TPD, duplicate-candidate distance, and candidate-to-feed
  distance;
- pair-based mean-ionic residual labels, values, scale, and maximum absolute
  residual with `bookkeeping_only_until_stage_iii` status;
- stage statuses showing phase discovery complete while Stage III refinement,
  postsolve certification, and public electrolyte route admission remain
  pending or closed as appropriate.

The checker must reject hardcoded NaCl-only evidence, missing multi-ion source
fixture evidence, raw single-ion charged-transfer equality as acceptance
evidence, incomplete prerequisite gates, and any premature Stage III,
postsolve, or public-admission completion claim.

## Required Contract Tests

- Single-salt Na+/Cl- rank and inverse-valence row construction.
- Common-anion Na+/K+/Cl- rank and pair-label construction using the local
  water + 1-butanol + NaCl + KCl Table 5 context.
- Multivalent K+/Cl-/Na+/SO4-- methodology example with sulfate coefficient
  `1/2` and matrix rank `3`.
- Reduced-coordinate lift and back-lift residual tests with charge residual <=
  `1.0e-10`.
- Checker-negative tests for incomplete #269/#300/#302 payloads, raw ion
  equality, and premature Stage III/postsolve/public-admission status.
- Closed public route tests for capabilities and registry evidence.

## Acceptance Criteria

- [x] A local mirror exists for #306 and #191 records #306 as closed dependency provenance after merge.
- [x] Native equilibrium exposes `_native_electrolyte_held2_phase_discovery`.
- [x] The native payload reports charged-species indices, charge vector,
  counterion-pair matrix, matrix rank, transformed-variable dimension, and
  charge-neutral lift/back-lift residuals.
- [x] The native payload satisfies the tightened diagnostic contract and emits
  a Stage III handoff record without claiming Stage III completion.
- [x] At least one NaCl source-backed fixture and one multi-ion or
  mixed-electrolyte source-backed preprocessor fixture exercise matrix
  construction.
- [x] The required contract tests cover single-salt, common-anion, and
  multivalent counterion-pair cases.
- [x] Candidate phase-discovery metrics are finite and include selected
  candidate count, minimum TPD, candidate charge residuals, and pending
  Stage III/postsolve/admission gates.
- [x] Mean-ionic residual bookkeeping exists for candidate phase sets.
- [x] Raw single-ion charged-transfer equality is rejected as acceptance
  evidence.
- [x] The retained checker consumes #269, #300, and #302 evidence before
  granting completion.
- [x] Capabilities and registry evidence keep public electrolyte routes closed.
- [x] #191 and M4 README show #306 closed after merge and list the remaining
  Stage III, postsolve, and public-admission blockers.

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python scripts/validation/check_electrolyte_held2_phase_discovery.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-native-held2-discovery --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_held2_phase_discovery.py tests/native/contracts/test_electrolyte_tpd_gate.py tests/native/contracts/test_electrolyte_held2_readiness_checker.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Non-Goals

- No public `electrolyte_lle` route admission.
- No Stage III electrolyte Ipopt refinement.
- No postsolve electrolyte phase-set certification cutover.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.
- No provider EOS rewrite.
