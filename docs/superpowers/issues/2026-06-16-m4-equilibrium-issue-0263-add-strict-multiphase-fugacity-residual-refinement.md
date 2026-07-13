---
issue: 263
title: "M4: add strict multiphase fugacity residual refinement"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/263
state: closed
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: lle
backend: Ipopt
readiness: closed
release_target: equilibrium-0.x
source_spec: null
source_plan: null
afk_hitl: AFK
branch: null
last_synced: "2026-07-12"
---

**Source-faithful historical classification (2026-07-12):** Preserve this closed issue as component history only. Stage 1 doctrine supersedes any classification of sampled-candidate replay as a completed Pereira Stage II upper/lower loop or of current-route/local residual refinement as canonical Stage III. The retained work does not establish Pereira HELD parity, global phase-set completeness, or public route admission.

# M4: add strict multiphase fugacity residual refinement

**Mirror Retention:** Keep

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/263
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md
**Source Plan:** docs/superpowers/plans/2026-06-16-m4-equilibrium-issue-0189-strict-multiphase-fugacity-residual-refinement-plan.md
**Classification:** AFK
AFK/HITL: AFK
**Labels:** enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/263 using docs/superpowers/issues/2026-06-16-m4-equilibrium-issue-0263-add-strict-multiphase-fugacity-residual-refinement.md and docs/superpowers/plans/2026-06-16-m4-equilibrium-issue-0189-strict-multiphase-fugacity-residual-refinement-plan.md. Complete proof oracle: issue acceptance criteria checked.
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
**Merged PR:** https://github.com/ePC-SAFT/ePC-SAFT/pull/265
**Closed At:** 2026-06-16T22:04:22Z

## What To Build

Add the #189 child that turns generalized neutral multiphase Stage III
refinement into an exact derivative-backed fugacity-residual route. This is the
prerequisite exposed by #261: a Gibbs-objective route can converge while the
reduced ln-fugacity norm still fails strict phase-equilibrium certification.

## Parent And Dependency

- Parent issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/189
- Blocking: https://github.com/ePC-SAFT/ePC-SAFT/issues/261

## Acceptance Criteria

- [x] A native phase-equilibrium residual block evaluates reduced fugacity equalities for arbitrary neutral phase counts using exact provider sensitivity data and amount/volume chain rules.
- [x] A private `NlpProblem` solves the square multiphase fugacity-residual system with material balance, phase pressure consistency, and cross-phase reduced fugacity equality constraints.
- [x] The route consumes Stage II candidate-set replay metadata and reports Stage III residual-refinement metadata.
- [x] The strict route reports Ipopt `success`, application `solve_succeeded`, exact derivative evidence, accepted postsolve, and reduced ln-fugacity consistency norm <= `1.0e-6`.
- [x] Checker and native tests reject missing strict residual-route evidence, missing exact derivative metadata, stale Gibbs-objective-only route evidence, public route exposure, collapsed phases, and residual norms above tolerance.
- [x] #189 remains open for final public generalized multiphase admission, and #261 is rerouted to use this strict proof after the child merges.

## Implementation Evidence

- Strict route binding: `_native_neutral_multiphase_fugacity_residual_route_result`.
- Route kind: `strict_fugacity_residual`.
- Hessian backend: `cppad_phase_system_plus_reduced_fugacity_residual`.
- Residual derivative backend: `cppad_explicit_density`.
- Stage III replay seed: `held_stage_ii_dual_loop_candidate_set`.
- Public admission: `closed`.
- Live checker proof: `uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete` returned `complete: true`, `blockers: []`, `selected_candidate_count: 3`, and `route_refinement_kind: strict_fugacity_residual`.

## Blocked By

- None.

## Non-Goals

- No public `neutral_multiphase_nonassoc` route exposure.
- No associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE admission.
- No tolerance relaxation for #261.
- No final closure of #189 from this child alone.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_phase_equilibrium_residual_block_contract.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_phase_discovery.py --json --include-route-refinement --require-complete
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments,
labels, milestone, dependency edges, and project fields.
