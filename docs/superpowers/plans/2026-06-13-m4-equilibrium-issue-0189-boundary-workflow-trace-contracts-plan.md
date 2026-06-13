# Boundary Workflow Trace Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the next AFK child under #189 by proving that current bubble/dew boundary workflows are retained, inspectable degree-of-freedom swaps over the certified neutral GFPE phase-NLP path, while strengthening #252 generalized phase-set records so omitted, duplicate/collapsed, infeasible, lower-free-energy, and uncertified candidates remain separately diagnosable.
**Architecture:** Keep the work inside `packages/epcsaft-equilibrium` and M4 docs. Reuse the existing selector route payloads, `check_boundary_workflows.py`, `check_generalized_phase_set.py`, and #252 `phase_set_records` evidence. Boundary workflows stay derived subworkflows under `derived_subworkflows`; `neutral_multiphase_nonassoc` stays internal and `PE-Generalized Multiphase` stays `planned_not_public`.
**Tech Stack:** Python, C++/pybind11, Ipopt-backed native equilibrium contracts, pytest through `run_pytest.py`, retained validation checkers under `scripts/validation`, GitHub Issues native dependency API, and local Superpowers Project mirrors under `docs/superpowers`.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Parent GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`
- Prior child result: #252 closed through #255 with internal neutral generalized phase-set record diagnostics and `scripts/validation/check_generalized_phase_set.py --json --require-complete`.
- Milestone: `M4 - Equilibrium`
- Package: `packages/epcsaft-equilibrium`
- Backend: `Ipopt`
- Capability: `lle`
- Candidate child title: `M4: certify derived boundary workflow traces from neutral GFPE`
- Queue status: #189 remains the HITL umbrella; this plan defines the next AFK child.

## Verified Planning Facts

- Verified: `scripts/validation/check_boundary_workflows.py` already exposes cheap derived-workflow contracts and opt-in current route solves for `bubble_pressure`, `bubble_temperature`, `dew_pressure`, and `dew_temperature`.
- Verified: boundary route points currently report strict convergence, solved boundary variable, fixed composition role, seed attempts, iteration history, and residual norms, but they do not yet expose a first-class trace proving the GFPE degree-of-freedom swap contract.
- Verified: `scripts/validation/check_generalized_phase_set.py` already proves #252's internal neutral three-candidate phase-set records, selected/rejected rows, mass-balance feasibility, noncollapsed selected compositions, and no public `neutral_multiphase_nonassoc` exposure.
- Verified: current generalized phase-set rejection reasons include duplicate/collapsed and generic unselected states, but #189 still requires distinct diagnostics for lower-free-energy omitted candidates and uncertified phase sets.
- Verified: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md` says boundary workflow validation must use the source-backed ePC-SAFT-compatible neutral TP flash mixture and must not invent a synthetic VLLE fixture.
- Inference: the next closest child should certify boundary workflow traceability first, while using the #252 checker as a prerequisite and extending rejection semantics where trace certification depends on phase-set completeness.

## Acceptance Criteria

- [ ] A retained boundary trace schema exists for every current executable bubble/dew route point requested by `check_boundary_workflows.py`.
- [ ] Each trace records route, workflow label, diagram target, known variables, free variables, solved boundary variable, fixed composition role, phase roles, source fixture, shared NLP/residual families, selector family, problem name, solver status, application status, strict convergence, and residual norms.
- [ ] Boundary traces prove the route is a derived degree-of-freedom swap over the same neutral amount-volume phase-NLP contract used by certified GFPE work, rather than a standalone special-case success.
- [ ] The checker fails closed when a boundary route point is missing the trace, has mismatched known/free variables, omits residual families, fails strict convergence, or has an iteration-limit seed attempt.
- [ ] The generalized phase-set checker distinguishes duplicate/collapsed, infeasible, lower-free-energy omitted, uncertified, and generic unselected rejected candidates with named blockers or rejection reasons.
- [ ] No public route or capability surface exposes `neutral_multiphase_nonassoc`.
- [ ] `PE-Generalized Multiphase` remains `planned_not_public`; docs and registry text must say this child advances boundary traceability and rejection diagnostics, not final public generalized multiphase admission.

## Non-Goals

- No associating, electrolyte, reactive, CE, or CPE route admission.
- No public `neutral_multiphase_nonassoc` route exposure.
- No cloud/shadow route implementation in this child; only their contract rows may remain planned derived subworkflows.
- No synthetic VLLE fixture and no Pereira 2012 System III ePC-SAFT validation promotion.
- No closure of #189 unless every umbrella gate in the source issue is separately complete.
- No compatibility wrappers, legacy alternate routes, or silent defaults for missing trace fields.

## Test-Complete Definition

The child is test-complete only when a fresh equilibrium build plus focused tests prove:

- `check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete` returns `complete: true` and emits accepted trace rows for all four current bubble/dew routes.
- Every accepted boundary trace has `solver_status == "success"`, `application_status == "solve_succeeded"`, no `max_iterations_exceeded` seed attempts, positive solved boundary value, and finite residual norms.
- Every accepted boundary trace maps to the expected DOF contract:
  - `bubble_pressure`: knowns `T, x`; free variables `P, y, phase_volumes`.
  - `bubble_temperature`: knowns `P, x`; free variables `T, y, phase_volumes`.
  - `dew_pressure`: knowns `T, y`; free variables `P, x, phase_volumes`.
  - `dew_temperature`: knowns `P, y`; free variables `T, x, phase_volumes`.
- `check_generalized_phase_set.py --json --require-complete` remains green and its contract tests fail on missing lower-free-energy omitted candidate diagnostics and uncertified candidate rows.
- M4 docs preserve the capability boundary: internal diagnostic and derived-boundary evidence only.

## Tasks

### Task 1: Preflight And Child Issue Split

**Use Cases:**

- When #189 is ready but still spans multiple proof families, an AFK worker needs a narrow child issue rather than the umbrella.
- When #252 is already closed, the next child should consume its retained checker and avoid repeating internal phase-set record work.
- When the implementation starts from a worktree, it should have explicit package, milestone, and capability boundaries before touching native code.

**Files:**

- `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- `docs/superpowers/milestones/M4-equilibrium/README.md`
- `docs/superpowers/plans/2026-06-13-m4-equilibrium-issue-0189-boundary-workflow-trace-contracts-plan.md`

- [ ] Confirm `git status --short --branch` is clean before starting implementation.
- [ ] Confirm #252 and PR #255 are closed and merged.
- [ ] Create one child issue from the Issue Creation Packet below and link it as a child or tracked dependency of #189.
- [ ] Keep #189 open and ready; do not move #190/#191 from blocked unless their own proof gates are complete.
- [ ] Commit checkpoint after local issue mirror and M4 README updates.

### Task 2: Add Failing Boundary Trace Contract Tests

**Use Cases:**

- When a boundary route point converges, tests should prove why it is a GFPE-derived boundary workflow, not only that Ipopt returned success.
- When a route's known/free variable mapping is wrong, the test should fail before any docs can claim a valid `P-x` or `T-x` boundary point.
- When a seed attempt hits the iteration limit, strict boundary completion should fail even if another seed produced a finite point.

**Files:**

- `tests/native/contracts/test_boundary_workflow_checker.py`
- `packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py`
- `packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py`
- `scripts/validation/check_boundary_workflows.py`

- [ ] Add checker-unit tests for a complete synthetic boundary trace payload.
- [ ] Add checker-unit tests that reject missing trace fields, mismatched known/free variables, mismatched composition role, missing residual families, non-finite solved boundary values, and iteration-limit seed attempts.
- [ ] Add selector/native diagnostic assertions that current bubble/dew selector contracts expose enough metadata to populate the trace without guessing.
- [ ] Add a narrow result-level assertion that the hydrocarbon workbook bubble/dew report includes trace metadata for route, problem name, selector family, knowns, unknowns, and phase roles.
- [ ] Run the new tests first and confirm they fail for missing trace support before implementation.
- [ ] Commit checkpoint after the red tests are in place.

### Task 3: Implement Boundary Trace Payloads And Checker Gates

**Use Cases:**

- When `check_boundary_workflows.py` runs a current route point, it should emit a stable machine-readable trace row that downstream docs and issue closeout can cite.
- When native diagnostics already carry selector family, problem name, variable model, residual families, constraint families, phase roles, and postsolve residuals, the checker should copy those fields directly instead of reconstructing them from prose.
- When route solves are not requested, `--contracts-only` should still report the planned derived workflow contracts without claiming executable trace completion.

**Files:**

- `scripts/validation/check_boundary_workflows.py`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/results/route_result_bridge.h`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`

- [ ] Add a `boundary_trace` row to each route point returned by `check_boundary_workflows.py`.
- [ ] Populate the trace from existing route payload fields where present: `selector_family`, `problem_name`, `variable_model`, `density_backend`, `residual_families`, `constraint_families`, `phase_labels`, `phase_roles`, `phase_amounts`, `phase_volumes`, and `postsolve`.
- [ ] Extend native result bindings only where route payload fields are genuinely missing; preserve loud C++ size and validity checks.
- [ ] Require trace schema version, route, workflow label, diagram target, known/free variables, fixed composition role, solved boundary variable, source fixture, strict convergence, seed summary, and residual norms.
- [ ] Keep `--contracts-only` cheap and non-executable: it may report trace schema availability, but it must not mark route points complete without requested route solves.
- [ ] Commit checkpoint after boundary trace payloads and checker gates pass focused tests.

### Task 4: Strengthen Phase-Set Rejection Semantics

**Use Cases:**

- When a candidate duplicates or collapses into an accepted phase, the rejected record should say that explicitly.
- When a candidate is omitted despite a lower free-energy or TPD objective than the accepted set can justify, the checker should flag the phase set as incomplete rather than accepting a generic unselected reason.
- When the phase set is uncertified or mass-balance incomplete, selected and rejected records should carry that certification status so #189 cannot close from an optimizer-only solution.

**Files:**

- `scripts/validation/check_generalized_phase_set.py`
- `tests/native/contracts/test_generalized_phase_set_checker.py`
- `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`

- [ ] Add checker tests for distinct rejected candidate reasons: `duplicate_or_collapsed`, infeasible feasibility status, `phase_set_not_certified`, and lower-free-energy omitted candidate.
- [ ] Teach `evaluate_payload()` to produce named blockers for lower-free-energy omitted rows and uncertified records instead of accepting a generic rejection reason.
- [ ] If native candidate metadata cannot prove a lower-free-energy omission, fail the checker with a missing-evidence blocker rather than inventing a classification.
- [ ] Extend binding helpers only where candidate objective, TPD, rank, selected flag, feasibility status, or phase-set certification evidence is missing from rows.
- [ ] Keep `check_generalized_phase_set.py --json --require-complete` green on the current #252 internal neutral three-phase fixture after the stricter semantics are added.
- [ ] Commit checkpoint after generalized phase-set checker and native diagnostic tests pass.

### Task 5: Update M4 Docs, Registry, And Issue Mirror

**Use Cases:**

- When someone reads the M4 milestone README, they should see that boundary trace evidence is the next #189 slice after #252.
- When registry rows mention bubble/dew completion, they should cite retained trace/checker evidence rather than public-route success.
- When #189 remains open, docs should state the remaining gates clearly instead of implying the umbrella is closed.

**Files:**

- `docs/superpowers/milestones/M4-equilibrium/README.md`
- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- New local mirror for the child issue under `docs/superpowers/issues/`

- [ ] Add the new child issue mirror and link it to #189.
- [ ] Add this plan to the M4 Current Plans table.
- [ ] Update the derived-boundary section to cite the new trace payload shape and retained checker command.
- [ ] Update registry `derived_subworkflows` acceptance evidence to require `boundary_trace` fields, not only strict convergence.
- [ ] Update #189 progress notes to say #252 completed internal phase-set records and this child owns boundary trace certification plus stricter omitted-candidate diagnostics.
- [ ] Commit checkpoint after docs and mirror updates.

### Task 6: Full Validation And Closeout

**Use Cases:**

- When a PR claims this child issue is resolved, reviewers need one proof oracle that exercises build freshness, boundary trace evidence, generalized phase-set rejection semantics, docs, and cleanup.
- When validation fails because native Ipopt is missing or route convergence is incomplete, closeout should preserve the blocker instead of weakening acceptance.
- When the child closes, #189 should advance but remain open unless all source acceptance gates are complete.

**Files:**

- `scripts/validation/check_boundary_workflows.py`
- `scripts/validation/check_generalized_phase_set.py`
- `docs/superpowers/issues/*.md`
- `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] Run the Proof Oracle below from the repo root.
- [ ] Capture JSON outputs for boundary and generalized phase-set checkers in the PR or issue comment.
- [ ] Close only the new child issue if every acceptance criterion passes.
- [ ] Add a #189 progress comment naming remaining umbrella work: cloud/shadow route derivation if still planned, final generalized phase-set exposure gates, associating LLLE separation, and downstream #190/#191 proof gates.
- [ ] Run the repo cleanup hook before final handoff.
- [ ] Commit checkpoint for closeout mirror updates after merge if local issue status changes.

## Proof Oracle

Run these commands from the repo root:

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Issue Creation Packet

Create one AFK child issue from this plan.

**Title:** `M4: certify derived boundary workflow traces from neutral GFPE`

**Type:** `Feature`

**Milestone:** `M4 - Equilibrium`

**Labels:** `enhancement`, `native`, `solver`, `docs`, `validation`, `equilibrium`, `area:equilibrium`, `backend:ipopt`, `status:ready`, `agent-ready`, `type:feature`

**Body:**

```markdown
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
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
```
