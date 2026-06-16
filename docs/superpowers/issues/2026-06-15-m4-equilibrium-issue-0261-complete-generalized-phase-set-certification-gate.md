---
issue: 261
title: "M4: complete generalized phase-set certification gate"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/261"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "blocked"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md"
source_plan: "docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-generalized-phase-set-certification-gate-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0261-complete-generalized-phase-set-certification-gate
blocked_by:
  - 263
last_synced: "2026-06-16"
---

# M4: complete generalized phase-set certification gate

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/261
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md
**Source Plan:** docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-generalized-phase-set-certification-gate-plan.md
**Classification:** AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/261 after #263 closes, using docs/superpowers/issues/2026-06-15-m4-equilibrium-issue-0261-complete-generalized-phase-set-certification-gate.md and docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-generalized-phase-set-certification-gate-plan.md. Complete proof oracle: issue acceptance criteria checked.
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

Convert the current internal neutral generalized phase-set diagnostic into a
route-refined generalized phase-set certification gate. The implementation must
prove Stage II candidate-set replay and strict Stage III Ipopt refinement for
requested neutral phase kinds `liquid,liquid,liquid`, while keeping public
`neutral_multiphase_nonassoc` route exposure closed.

## Acceptance Criteria

- [ ] Native generalized phase-set route refinement consumes Stage II candidate-set replay metadata for requested phase kinds `liquid,liquid,liquid`.
- [ ] Stage III Ipopt route refinement reports `solver_status == "success"`, `application_status == "solve_succeeded"`, exact Hessian evidence, accepted postsolve, and no iteration-limit selected seed attempt.
- [ ] The retained checker reports requested phase kinds/count, selected/rejected candidate counts, selected phase fractions, replay metadata, route-refinement status, residual norms, native freshness receipt, and public exposure status.
- [ ] Completion metrics satisfy candidate mass-balance norm <= `1.0e-6`, material-balance norm <= `1.0e-8`, pressure consistency norm <= `1.0e-3 Pa`, ln-fugacity consistency norm <= `1.0e-6`, positive phase distance, normalized compositions, and strictly positive phase fractions.
- [ ] Checker tests reject missing route refinement, missing replay metadata, hard-coded phase count, duplicate/collapsed phases, lower-free-energy rejected candidates, uncertified records, malformed records, and public route exposure.
- [ ] `neutral_multiphase_nonassoc` remains absent from public routes and production-exposed capability rows.
- [ ] M4 registry and GFPE doctrine record internal generalized certification evidence without final public production exposure.
- [ ] #189 remains open unless final public capability admission is separately proven.

## Blocked By

- https://github.com/ePC-SAFT/ePC-SAFT/issues/263 owns the strict multiphase fugacity-residual refinement prerequisite exposed during #261 execution.

## Previously blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/260 closed through https://github.com/ePC-SAFT/ePC-SAFT/pull/262.

## Non-goals

- No public `neutral_multiphase_nonassoc` route exposure.
- No associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE admission.
- No final public `PE-Generalized Multiphase` production exposure.
- No closure of #189 from this child alone if public admission remains unproven.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments,
labels, milestone, dependency edges, and project fields.

