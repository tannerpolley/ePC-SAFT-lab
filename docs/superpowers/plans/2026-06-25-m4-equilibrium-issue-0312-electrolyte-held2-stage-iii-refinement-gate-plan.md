# Electrolyte HELD2 Stage III Reduced-Variable Refinement Gate Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #312 by turning the #306 HELD2
counterion-pair phase-discovery handoff into strict Stage III electrolyte
reduced-variable refinement evidence.

**Architecture:** This is a Stage III refinement gate, not postsolve
certification or public route admission. It consumes the #269 source gate, #300
reduced-basis/Born exactness gate, #302 charge-neutral TPD gate, and #306
HELD2 phase-discovery candidate set. The solver must work in reduced
electroneutral variables, retain exact reduced residual derivative receipts,
and leave postsolve certification plus public admission as later child gates.

**Tech Stack:** C++ equilibrium native core, pybind11 bindings, Python
validation checker, pytest contracts through `run_pytest.py`, M4 issue mirrors,
M4 benchmark registry, GitHub dependencies.

---

## Intake

- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/312`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Issue: `docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0312-add-electrolyte-held2-stage-iii-reduced-variable-refinement-gate.md`
- Source Plan: `docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md`
- Prior Child Gate: `docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0306-add-electrolyte-held2-counterion-pair-phase-discovery-gate.md`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`

## Outcome Proof

**Intent:** Convert #306 phase-discovery candidates into a retained Stage III
electrolyte refinement proof in reduced electroneutral coordinates.
**Current Behavior:** The retained #306 checker produces candidate and handoff
records, but no strict electrolyte reduced-variable phase-set refinement gate
has accepted the candidate set.
**Expected Outcome:** A retained checker exits successfully only when the
prerequisite gates pass and Stage III refinement consumes the #306 candidate set
with exact reduced residual derivative evidence, strict solver diagnostics, and
closed public electrolyte route state.
**Target Output:** `scripts/validation/check_electrolyte_stage_iii_refinement.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-native-stage-iii --require-public-routes-closed --require-complete` returns `complete: true`.
**Owner:** M4 equilibrium package owner.
**Interface:** Native reduced-variable Stage III diagnostic, retained checker
JSON, pytest contracts, M4 issue mirror, registry row, and M4 README.
**Cutover:** This checker becomes the #312 proof oracle and removes the Stage
III blocker from #191 after merge.
**Replaced Path:** HELD2 phase-discovery candidate evidence remains
prerequisite evidence and no longer stands in for a refined electrolyte
phase-set solve.
**Evidence:** Failing-then-passing native contract tests, checker JSON,
reduced residual derivative receipts, solver diagnostics, docs validation, and
GitHub issue/PR closure evidence.
**Acceptance Proof:** Acceptance is proven when the retained checker consumes
#269/#300/#302/#306, reports exact reduced residual Jacobian/Hessian evidence,
strict solver success, bounded finite phase compositions, no phase collapse, and
explicit pending postsolve/admission gates.
**Stop Criteria:** Stop if the reduced residual equations cannot be stated, if
raw single-ion equality appears as acceptance evidence, if Ipopt success is used
without physical diagnostics, or if public route admission is needed to satisfy
this gate.
**Avoid:** Do not add postsolve certification, public electrolyte routes,
reactive routes, regression work, downstream study logic, or release claims.
**Risk:** A converged nonlinear solve can be mistaken for physical acceptance;
this gate must report residual and solver evidence while leaving postsolve
certification separate.

## Implementation Boundaries

**Files To Create:** `scripts/validation/check_electrolyte_stage_iii_refinement.py`, `tests/native/contracts/test_electrolyte_stage_iii_refinement.py`.
**Files To Modify:** Native electrolyte equilibrium diagnostics and bindings in
`packages/epcsaft-equilibrium/**`, capability/registry evidence, the #191/#312
issue mirrors, and the M4 README.
**Files To Avoid:** Public route admission maps beyond closed-state assertions,
regression package files, downstream repositories, generated build trees, and
provider EOS internals unless a public provider contract receipt is consumed.
**Source Of Truth:** #191 source spec, M4 GFPE doctrine, #306 retained checker
payload, and the electrolyte methodology paper context already cited by #191.
**Read Path:** Consume #269 through `check_electrolyte_gfpe_gate.py`, #300
through `check_electrolyte_held2_readiness.py`, #302 through
`check_electrolyte_tpd_gate.py`, and #306 through
`check_electrolyte_held2_phase_discovery.py`.
**Write Path:** Write one Stage III checker, one contract test module, native
diagnostic support, capability/registry evidence rows, and tracker updates.
**Integration Points:** Reduced electroneutral variables, Ipopt route profile,
exact reduced residual derivatives, pybind11 registration, capability evidence,
and M4 registry evidence.
**Migration Or Cutover:** #191 remains blocked by #312 until this PR merges;
after merge, #313 becomes the next active blocker.
**Replaced Path Handling:** Keep #306 discovery evidence as prerequisite
handoff support; do not rewrite it into a route-quality certificate.
**Acceptance Proof Gate:** The proof oracle commands below must pass before
push, PR creation, merge, and issue close.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Next child | Live M4 queue plus #191 blocker state | #312 owns Stage III reduced-variable refinement. | Creates the next executable M4 child. | No | M4 owner |
| Coordinate basis | #306 handoff | Consume counterion-pair reduced coordinates. | Prevents raw charged-species equality from becoming the solve basis. | No | M4 owner |
| Acceptance boundary | M4 GFPE doctrine | Solver success is necessary but not postsolve certification. | Keeps #313 separate. | No | M4 owner |
| Public route state | #191 plan | Keep electrolyte public routes closed. | Avoids unsupported capability claims. | No | M4 owner |

## Required Contract Tests

- `test_stage_iii_consumes_held2_candidate_set`: the accepted Stage III seed
  provenance points to #306 candidate handoff records.
- `test_reduced_residual_shape_and_scaling`: variables, equations, scaling,
  bounds, and phase labels are reported.
- `test_exact_reduced_derivatives_reported`: Jacobian and Hessian receipts are
  retained for the reduced residual system.
- `test_stage_iii_solver_diagnostics_are_strict`: Ipopt and application
  statuses, residual norms, active-bound diagnostics, and finite compositions
  are present.
- `test_stage_iii_rejects_phase_collapse`: collapsed or duplicate phase
  compositions cannot complete the gate.
- `test_stage_iii_rejects_raw_single_ion_equality`: raw single-ion transfer
  equality cannot be used as electrolyte acceptance evidence.
- `test_public_electrolyte_routes_stay_closed`: capability and registry
  evidence keep public electrolyte routes closed.

## Acceptance Criteria

- [ ] The checker consumes #269, #300, #302, and #306 evidence.
- [ ] Stage III refinement consumes the #306 candidate set without regenerating
  unproven candidates.
- [ ] The reduced electroneutral residual system reports variables, equations,
  scaling, bounds, seed provenance, and selected phase labels.
- [ ] Exact reduced residual Jacobian and Hessian receipts are retained.
- [ ] Solver diagnostics report Ipopt status, application status, residual
  norms, active-bound diagnostics, and finite phase compositions.
- [ ] Negative tests reject missing prerequisites, raw single-ion equality,
  phase-collapsed solutions, and premature postsolve/public-admission status.
- [ ] Capabilities and registry evidence keep public electrolyte routes closed.
- [ ] #191 and the M4 README name #313 and #314 as the remaining gates after
  this issue closes.

## Non-Goals

- No public electrolyte route admission.
- No postsolve certification cutover.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.

## Tasks

### Task 1: Define The Stage III Refinement Contract

**Use Cases:**

- A worker needs exact residual variables, equations, scaling, and diagnostics
  before implementing solver code.
- A reviewer needs to distinguish Stage III convergence from postsolve
  physical certification.

**Files:**

- `scripts/validation/check_electrolyte_stage_iii_refinement.py`
- `tests/native/contracts/test_electrolyte_stage_iii_refinement.py`

- [ ] Add negative tests for missing #269/#300/#302/#306 prerequisites.
- [ ] Add contract tests for reduced residual shape, scaling, and derivative
  receipts.
- [ ] Add checker blockers for postsolve/public-admission status marked
  complete under #312.

### Task 2: Add Native Stage III Diagnostics

**Use Cases:**

- A reduced candidate set from #306 needs strict Ipopt refinement in the same
  electroneutral coordinate basis.
- A checker needs finite numeric receipts for residuals, bounds, and solver
  statuses.

**Files:**

- `packages/epcsaft-equilibrium/**`
- `scripts/validation/check_electrolyte_stage_iii_refinement.py`

- [ ] Add the native diagnostic or route-internal payload for Stage III.
- [ ] Bind the diagnostic to Python when needed by the checker.
- [ ] Retain exact reduced residual derivative metadata.

### Task 3: Keep Capability Claims Closed

**Use Cases:**

- A user must not see public electrolyte route support before postsolve
  certification and admission.
- M4 docs must show the next blocker after #312 closes.
- The acceptance evidence must show the cutover from #306 phase-discovery
  handoff evidence to #312 Stage III refinement proof without replacing
  postsolve certification.

**Files:**

- `docs/superpowers/milestones/M4-equilibrium/README.md`
- `docs/superpowers/issues/**`
- `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml` and `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`

- [ ] Update registry evidence for Stage III closed/public-route state.
- [ ] Update #191 and #312 mirrors after merge.
- [ ] Keep #313 as the next blocker.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0312-electrolyte-held2-stage-iii-refinement-gate-plan.md
uv run --no-sync python scripts/validation/check_electrolyte_stage_iii_refinement.py --json --require-source-gate --require-readiness-gate --require-tpd-gate --require-held2-discovery --require-native-stage-iii --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_stage_iii_refinement.py tests/native/contracts/test_electrolyte_held2_phase_discovery.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
