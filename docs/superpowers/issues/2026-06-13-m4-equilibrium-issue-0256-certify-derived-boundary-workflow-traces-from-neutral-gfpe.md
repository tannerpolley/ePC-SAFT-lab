---
issue: 256
title: "M4: certify derived boundary workflow traces from neutral GFPE"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/256"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md"
source_plan: "docs/superpowers/plans/2026-06-13-m4-equilibrium-issue-0189-boundary-workflow-trace-contracts-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0256-boundary-workflow-traces
last_synced: "2026-06-13"
---

# M4: certify derived boundary workflow traces from neutral GFPE

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/256
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md
**Source Plan:** docs/superpowers/plans/2026-06-13-m4-equilibrium-issue-0189-boundary-workflow-trace-contracts-plan.md
Branch: codex/issue-0256-boundary-workflow-traces
AFK/HITL: AFK
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, agent-ready, type:feature
**Goal Command:** /goal Resolve M4 issue #256 by certifying retained bubble/dew boundary workflow traces from neutral GFPE and strengthening generalized phase-set rejection diagnostics without public generalized multiphase admission.
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

Implement the next AFK slice under #189: certify current bubble/dew boundary
workflows as retained, inspectable degree-of-freedom swaps over the neutral
GFPE phase-NLP path, and strengthen generalized phase-set rejection diagnostics
without exposing a public generalized multiphase route.

## Acceptance Criteria

- [x] `check_boundary_workflows.py` emits a `boundary_trace` row for every requested current bubble/dew route point.
- [x] Boundary traces record route, workflow label, diagram target, known variables, free variables, solved boundary variable, fixed composition role, phase roles, source fixture, shared NLP/residual families, selector family, problem name, solver status, application status, strict convergence, and residual norms.
- [x] The checker fails when trace fields are missing, known/free variables are mismatched, residual families are absent, strict convergence fails, or any seed attempt hits the iteration limit.
- [x] `check_generalized_phase_set.py` distinguishes duplicate/collapsed, infeasible, lower-free-energy omitted, uncertified, and generic unselected rejected candidates with named blockers or rejection reasons.
- [x] `neutral_multiphase_nonassoc` remains absent from public routes and capabilities.
- [x] `PE-Generalized Multiphase` remains `planned_not_public`; docs and registry text do not claim public generalized multiphase, associating LLLE, electrolyte, or reactive support.

## Blocked By

- None. #252 closed through https://github.com/ePC-SAFT/ePC-SAFT/pull/255.

## Blocking

- https://github.com/ePC-SAFT/ePC-SAFT/issues/189

## Non-Goals

- No associating, electrolyte, reactive, CE, or CPE route admission.
- No public `neutral_multiphase_nonassoc` route exposure.
- No cloud/shadow route implementation in this issue.
- No synthetic VLLE fixture and no Pereira 2012 System III ePC-SAFT validation promotion.
- No closure of #189 unless all umbrella gates are separately proven.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
```

```powershell
uv run --no-sync python run_pytest.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
```

```powershell
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q
```

```powershell
uv run --no-sync python run_pytest.py --allow-long-equilibrium-tests packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py -q
```

```powershell
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete
```

```powershell
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
```

```powershell
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete
```

```powershell
uv run --no-sync python scripts/dev/validate_project.py docs
```

## GitHub Body Text

Implement the next AFK slice under #189: certify current bubble/dew boundary workflows as retained, inspectable degree-of-freedom swaps over the neutral GFPE phase-NLP path, and strengthen generalized phase-set rejection diagnostics without exposing a public generalized multiphase route.

Source plan:
docs/superpowers/plans/2026-06-13-m4-equilibrium-issue-0189-boundary-workflow-trace-contracts-plan.md

Parent:
#189

Goal:
Add retained boundary trace contracts for current executable bubble/dew route points and require generalized phase-set records to distinguish duplicate/collapsed, infeasible, lower-free-energy omitted, and uncertified rejected candidates.

Acceptance:
- `check_boundary_workflows.py` emits a `boundary_trace` row for every requested current bubble/dew route point.
- Boundary traces record route, workflow label, diagram target, known variables, free variables, solved boundary variable, fixed composition role, phase roles, source fixture, shared NLP/residual families, selector family, problem name, solver status, application status, strict convergence, and residual norms.
- The checker fails when trace fields are missing, known/free variables are mismatched, residual families are absent, strict convergence fails, or any seed attempt hits the iteration limit.
- `check_generalized_phase_set.py` distinguishes duplicate/collapsed, infeasible, lower-free-energy omitted, uncertified, and generic unselected rejected candidates with named blockers or rejection reasons.
- `neutral_multiphase_nonassoc` remains absent from public routes and capabilities.
- `PE-Generalized Multiphase` remains `planned_not_public`; docs and registry text do not claim public generalized multiphase, associating LLLE, electrolyte, or reactive support.

Non-goals:
- No associating, electrolyte, reactive, CE, or CPE route admission.
- No public `neutral_multiphase_nonassoc` route exposure.
- No cloud/shadow route implementation in this issue.
- No synthetic VLLE fixture and no Pereira 2012 System III ePC-SAFT validation promotion.
- No closure of #189 unless all umbrella gates are separately proven.

Proof oracle:
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q
uv run --no-sync python run_pytest.py --allow-long-equilibrium-tests packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs

## Resolution Evidence

All #256 proof commands passed on branch
`codex/issue-0256-boundary-workflow-traces`:

- `uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4`
- `uv run --no-sync python run_pytest.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q` -> 13 passed.
- `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q` -> 31 passed.
- `uv run --no-sync python run_pytest.py --allow-long-equilibrium-tests packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py -q` -> 1 passed.
- `uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete` -> complete, selected 3, rejected 3.
- `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only` -> contracts available.
- `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete` -> complete boundary route convergence, four accepted bubble/dew route points, complete boundary traces.
- `uv run --no-sync python scripts/dev/validate_project.py docs`

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `AFK`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
