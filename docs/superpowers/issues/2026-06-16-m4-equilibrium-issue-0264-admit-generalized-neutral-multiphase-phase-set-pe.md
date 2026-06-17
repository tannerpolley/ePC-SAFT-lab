---
issue: 264
title: "M4: admit generalized neutral multiphase phase-set PE"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/264"
state: "closed"
closed_at: "2026-06-17T13:15:47Z"
closing_pr: "https://github.com/ePC-SAFT/ePC-SAFT/pull/268"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "done"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md"
source_plan: "docs/superpowers/plans/2026-06-16-m4-equilibrium-issue-0189-generalized-neutral-multiphase-admission-plan.md"
afk_hitl: "AFK"
previously_blocked_by:
  - "https://github.com/ePC-SAFT/ePC-SAFT/issues/261"
branch: codex/issue-0264-admit-generalized-neutral-multiphase-phase-set-pe
last_synced: "2026-06-17"
---

# M4: admit generalized neutral multiphase phase-set PE

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/264
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md
**Source Plan:** docs/superpowers/plans/2026-06-16-m4-equilibrium-issue-0189-generalized-neutral-multiphase-admission-plan.md
**Classification:** AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/264 using docs/superpowers/issues/2026-06-16-m4-equilibrium-issue-0264-admit-generalized-neutral-multiphase-phase-set-pe.md and docs/superpowers/plans/2026-06-16-m4-equilibrium-issue-0189-generalized-neutral-multiphase-admission-plan.md. Complete proof oracle: issue acceptance criteria checked.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add the final #189 child that admits certified neutral generalized multiphase
phase-set PE through the public `Equilibrium(mixture, route="multiphase",
T=..., P=..., z=..., phase_kinds=[...]).solve()` workflow after #263 and #261
closed.

Closed through https://github.com/ePC-SAFT/ePC-SAFT/pull/268 on 2026-06-17.

## Parent And Dependencies

- Parent issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/189
- Previously blocked by: https://github.com/ePC-SAFT/ePC-SAFT/issues/261, closed through https://github.com/ePC-SAFT/ePC-SAFT/pull/266.
- Indirect prerequisite: https://github.com/ePC-SAFT/ePC-SAFT/issues/263
- Native GitHub dependency edge: #264's #261 blocker is satisfied because #261 is closed.

## Acceptance Criteria

- [x] Public `Equilibrium(..., route="multiphase", T=..., P=..., z=..., phase_kinds=[...]).solve()` is implemented for neutral nonassociating generalized multiphase PE.
- [x] Public route execution calls the strict multiphase fugacity-residual route from #263 and requires the #261 generalized phase-set certification metrics.
- [x] The public result reports route `multiphase`, selector family `neutral_multiphase_nonassoc`, three named phases for the proof case, normalized compositions, positive phase fractions, exact Hessian evidence, and accepted postsolve.
- [x] Completion metrics satisfy candidate mass-balance norm <= `1.0e-6`, material-balance norm <= `1.0e-8`, pressure consistency norm <= `1.0e-3 Pa`, ln-fugacity consistency norm <= `1.0e-6`, positive phase distance, normalized compositions, and strictly positive phase fractions.
- [x] `epcsaft_equilibrium.capabilities()` reports `multiphase` as a public production route mapped to `neutral_multiphase_nonassoc`.
- [x] The generalized phase-set checker has public-admission mode and passes with `--require-public-admission --require-complete`.
- [x] M4 registry, GFPE doctrine, M4 README, and #189 mirror record public neutral generalized multiphase admission.
- [x] #189 closes only after this child merges; #145/#190/#191 remain separate for associating/electrolyte/reactive follow-up.

## Implementation Evidence

- Public API proof: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::test_equilibrium_multiphase_route_returns_public_three_phase_result`.
- Capability proof: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`.
- Native strict residual proof: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`.
- Public-admission checker proof: `uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-public-admission --require-complete`.
- Scope boundary: neutral nonassociating multiphase only; #145/#190/#191 remain separate gates for associating, electrolyte, and reactive families.

## Blocked By

- None. #261 closed through https://github.com/ePC-SAFT/ePC-SAFT/pull/266 and supplied the internal generalized phase-set certification prerequisite.

## Non-goals

- No associating neutral LLE admission.
- No electrolyte LLE, HELD2.0, reactive LLE, reactive electrolyte LLE, CE, CPE, LLLE, or VLLE admission.
- No M3 provider or M5 regression implementation changes.
- No relaxation of #261/#263 numerical metrics.
- No release publication or downstream integration proof.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python run_pytest.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-public-admission --require-complete
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments,
labels, milestone, dependency edges, and project fields.
