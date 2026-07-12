# Strict Multiphase Fugacity Residual Refinement Implementation Plan

> **Source-faithful supersession (2026-07-12):** Preserve the exact
> fugacity-residual NLP as local correction and certification evidence. It does
> not replace direct total free-energy minimization as the defining Pereira
> HELD Stage III problem.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the #189 child that turns neutral generalized multiphase Stage III refinement into an exact derivative-backed fugacity-residual route so #261 can pass strict phase-equilibrium certification without relaxing its postsolve tolerances.

**Architecture:** Keep Stage II HELD candidate-set replay as the seed source, but add a separate private equality-residual NLP for multiphase certification instead of relying only on the thermodynamic Gibbs-objective route. The new route uses phase species amounts and phase volumes, enforces material balance, phase pressure consistency, and cross-phase reduced fugacity equality as explicit constraints, and supplies exact Jacobian and Lagrangian Hessian values through a reusable phase-equilibrium residual block. Public `neutral_multiphase_nonassoc` exposure remains closed; this child produces internal certification evidence and a dependency edge for #261.

**Tech Stack:** C++ native equilibrium core, provider CppAD phase-state ln-fugacity sensitivities, Ipopt exact-Hessian `NlpProblem`, pybind11 private diagnostics, pytest through `run_pytest.py`, `scripts/validation/check_generalized_phase_set.py`, GitHub issue mirrors under `docs/superpowers/issues`.

---

## Intake

- Direct planning approval: user selected `Strict residual child (Recommended)` for a new child under #189 and selected `Current branch` for saving the plan.
- Parent issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`
- Current related child: `https://github.com/ePC-SAFT/ePC-SAFT/issues/261`
- Source issue mirror: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source plan being unblocked: `docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-generalized-phase-set-certification-gate-plan.md`
- GFPE doctrine: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Backend: `Ipopt`
- Capability boundary: internal neutral generalized multiphase certification only.

## Current Evidence And Gap

#261 has already exposed the missing implementation seam. The current generalized route can consume Stage II candidate-set replay and drive Ipopt to strict solver convergence, but its postsolve can still reject with `chemical_potential_consistency` because the pairwise reduced fugacity norm is about `4.6e-3`, far above the #261 `1.0e-6` completion metric. Material balance, pressure consistency, phase distance, and exact-Hessian evidence can all look acceptable while phase-equilibrium equality still fails.

The root issue is architectural: `NeutralTwoPhaseEosProblem` optimizes the pressure-transformed Helmholtz objective with material and pressure constraints. It does not expose cross-phase reduced fugacity equality as an active equality constraint for an arbitrary requested phase count. The provider tree already has CppAD phase-state ln-fugacity sensitivity data, including first and second derivatives with respect to density and composition. This child routes that data into an equilibrium-owned amount/volume residual block and a square exact-derivative NLP:

```text
variables    = phase_count * (species_count + 1)
constraints  = species_count material balance
             + phase_count pressure consistency
             + (phase_count - 1) * species_count reduced fugacity equalities
```

For three liquid phases and three species, this gives 12 variables and 12 equality constraints.

## Planning Decisions

- Title for the child issue: `M4: add strict multiphase fugacity residual refinement`.
- This child is a prerequisite for #261 acceptance, not final public generalized multiphase admission.
- It must not weaken #261 tolerances, hide the fugacity residual, or accept a Gibbs-objective KKT solve as phase-equilibrium certification when the postsolve fugacity norm fails.
- It must use exact derivative paths only. The route is blocked until exact first and second derivatives of the reduced fugacity residuals are wired through the native NLP contract.
- It must leave `neutral_multiphase_nonassoc` absent from public route specs and production-exposed capability rows.
- It must update local and GitHub tracker state so #261 is clearly waiting on this residual-refinement prerequisite if the child is created before #261 is closed.

## Test-Complete Definition And Metrics

This plan is complete only when all of the following are true:

- A private route result helper can solve the symmetric ternary `liquid,liquid,liquid` case using the strict fugacity-residual NLP seeded from Stage II candidate-set replay.
- The route reports `solver_status == "success"`, `application_status == "solve_succeeded"`, exact Jacobian and exact Hessian evidence, no selected seed attempt ending in an iteration-limit status, and `public_route_admission == "closed"`.
- Postsolve reports `accepted is true`, `held_stage_iii_status == "ipopt_refinement_completed_current_route"`, `held_stage_iii_consumed_stage_ii_replay_metadata is true`, and `held_stage_iii_replay_seed_name == "held_stage_ii_dual_loop_candidate_set"`.
- Numeric metrics satisfy candidate mass-balance norm <= `1.0e-6`, material-balance norm <= `1.0e-8`, pressure consistency norm <= `1.0e-3 Pa`, reduced ln-fugacity consistency norm <= `1.0e-6`, positive phase distance, normalized phase compositions, and strictly positive phase fractions.
- The residual block contract test proves the square constraint count, sparse Jacobian structure, exact Lagrangian Hessian shape, transform-chain derivatives from amount/volume to density/composition, and positive-domain behavior for trace amounts.
- `scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete` exits zero only when it sees the strict residual route evidence.
- Docs and registries describe this as internal certification evidence and keep #189 open for final public admission.

## Acceptance Criteria

- [ ] A new #189 child issue and local mirror capture the strict residual-refinement prerequisite and its relationship to #261.
- [ ] A native phase-equilibrium residual block evaluates reduced fugacity equalities for arbitrary neutral phase counts using exact provider sensitivity data and amount/volume chain rules.
- [ ] A private `NlpProblem` solves the square multiphase fugacity-residual system with material balance, phase pressure consistency, and cross-phase reduced fugacity equality constraints.
- [ ] The route consumes Stage II candidate-set replay metadata, records Stage III residual-refinement metadata, and returns strict Ipopt/application success only when reduced fugacity equality passes the completion metric.
- [ ] Checker and native tests fail on missing residual-route evidence, missing exact derivative metadata, stale Gibbs-objective-only route evidence, public route exposure, collapsed phases, and residual norms above tolerance.
- [ ] #261 and #189 mirrors describe the dependency and remaining gates without claiming public generalized multiphase production exposure.

## Non-Goals

- No public `Equilibrium(route="neutral_multiphase_nonassoc")` route.
- No associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE admission.
- No change to M3 provider behavior beyond using existing provider sensitivity APIs from M4-owned equilibrium code.
- No tolerance relaxation for #261.
- No final closure of #189 from this child alone.

## File Map

- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/phase_equilibrium_residual_block.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/phase_equilibrium_residual_block.cpp`
- Create: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_phase_equilibrium_residual_block_contract.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/CMakeLists.txt`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`
- Modify: `scripts/validation/check_generalized_phase_set.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_completion_checker.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_checker.py`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify after issue creation: `docs/superpowers/issues/2026-06-15-m4-equilibrium-issue-0261-complete-generalized-phase-set-certification-gate.md`
- Create after issue creation: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-add-strict-multiphase-fugacity-residual-refinement.md`

## Tasks

### Task 1: Create The #189 Residual-Refinement Child

**Use Cases:**
- A tracker owner needs #261's current strict fugacity-residual failure represented as a real prerequisite instead of hidden inside a partially passing route-refinement PR.
- A worker needs a narrow AFK issue that owns exact residual-block derivatives and the square residual NLP.
- A reviewer needs #189 to stay open for final public admission while this child supplies internal certification evidence only.

**Files:**
- Create: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-add-strict-multiphase-fugacity-residual-refinement.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/issues/2026-06-15-m4-equilibrium-issue-0261-complete-generalized-phase-set-certification-gate.md`

- [ ] **Step 1: Confirm live tracker state**

  Run:

  ```powershell
  gh issue view 189 --repo ePC-SAFT/ePC-SAFT --json number,title,state,labels,milestone,url
  gh issue view 261 --repo ePC-SAFT/ePC-SAFT --json number,title,state,labels,milestone,url
  git status --short --branch
  ```

  Expected: #189 and #261 are open in `M4 - Equilibrium`; the branch contains only the current #261 implementation work plus deliberate planning files.

- [ ] **Step 2: Create the GitHub child**

  Use the Issue Creation Packet at the end of this plan. Apply milestone `M4 - Equilibrium` and labels:

  ```text
  enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature, agent-ready
  ```

- [ ] **Step 3: Create the local issue mirror**

  Create the mirror using the actual issue number, parent #189 link, #261 prerequisite relationship, this source plan path, acceptance criteria, proof oracle, and non-goals.

- [ ] **Step 4: Update #189 and #261 queue notes**

  Update #189 to list this child as the strict residual-refinement gate before #261 can claim generalized phase-set certification. Update #261 to name the child as the route-refinement prerequisite if #261 remains open.

- [ ] **Step 5: Commit tracker setup**

  Run:

  ```powershell
  git add docs/superpowers/issues
  git commit -m "Create strict multiphase residual refinement issue"
  ```

### Task 2: Add Residual Block Contract Tests

**Use Cases:**
- A native maintainer needs a focused test proving the phase-equilibrium residual block uses exact derivative metadata instead of route postsolve comparisons.
- A solver maintainer needs the square three-phase, three-species constraint count and sparse derivative shapes locked before the Ipopt route is added.
- A numerical reviewer needs positive-domain trace behavior covered because reduced fugacity residuals include `log(x_i)`.

**Files:**
- Create: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_phase_equilibrium_residual_block_contract.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Test: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/phase_equilibrium_residual_block.h`
- Test: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/phase_equilibrium_residual_block.cpp`

- [ ] **Step 1: Add the red native test file**

  Add a test that imports `extension_native_core()` and calls a private diagnostic helper named `_native_phase_equilibrium_residual_block_contract`.

  ```python
  def test_phase_equilibrium_residual_block_contract_reports_square_three_phase_layout() -> None:
      payload = _core._native_phase_equilibrium_residual_block_contract(
          mix._native,
          200.0,
          1.0e6,
          phase_amounts,
          volumes,
      )
      assert payload["phase_count"] == 3
      assert payload["species_count"] == 3
      assert payload["variable_count"] == 12
      assert payload["constraint_count"] == 6
      assert payload["residual_count"] == 6
      assert payload["full_square_constraint_count"] == 12
      assert payload["jacobian_backend"] in {"cppad_explicit_density", "cppad_explicit_density_implicit_association"}
      assert payload["hessian_backend"] in {"cppad_explicit_density", "cppad_explicit_density_implicit_association"}
      assert payload["exact_jacobian_available"] is True
      assert payload["exact_hessian_available"] is True
  ```

- [ ] **Step 2: Add chain-rule metric assertions**

  Assert that the diagnostic reports these non-empty derivative fields:

  ```text
  density_amount_jacobian
  composition_amount_jacobian
  reduced_fugacity_local_jacobian_shape
  reduced_fugacity_local_hessian_shape
  residual_jacobian_nonzero_count
  residual_hessian_nonzero_count
  ```

- [ ] **Step 3: Add positive-domain trace assertions**

  Add a case with one selected phase carrying a trace component above the route lower bound. Assert the residual block reports finite residuals, finite Jacobian values, and finite Hessian values.

- [ ] **Step 4: Run the red contract tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_phase_equilibrium_residual_block_contract.py -q
  ```

  Expected: the tests fail because the private diagnostic helper and residual block do not exist yet.

- [ ] **Step 5: Commit red tests**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/tests/native/diagnostics/test_phase_equilibrium_residual_block_contract.py
  git commit -m "Add red phase-equilibrium residual block tests"
  ```

### Task 3: Implement The Exact Phase-Equilibrium Residual Block

**Use Cases:**
- The strict multiphase route needs reduced fugacity equality values and derivatives for any neutral phase count with a reference phase.
- The residual block must transform provider density/composition sensitivities into phase amount/volume derivatives without numerical substitutes.
- A failed provider sensitivity evaluation must surface as a loud route error with the phase index, species count, and sensitivity message.

**Files:**
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/phase_equilibrium_residual_block.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/phase_equilibrium_residual_block.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/CMakeLists.txt`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`

- [ ] **Step 1: Define the result structure**

  Add a result shape with residuals, dense local derivatives, sparse global counts, and derivative labels:

  ```cpp
  struct PhaseEquilibriumResidualBlockResult {
      std::string block;
      std::string derivative_backend;
      int phase_count = 0;
      int species_count = 0;
      int variable_count = 0;
      int residual_count = 0;
      std::vector<double> reduced_ln_fugacity_values;
      std::vector<double> residuals;
      std::vector<double> jacobian_row_major;
      std::vector<double> hessian_tensor_row_major;
      std::vector<std::string> residual_names;
      bool exact_jacobian_available = false;
      bool exact_hessian_available = false;
  };
  ```

- [ ] **Step 2: Implement local amount/volume transform derivatives**

  For each phase, compute `N = sum_i n_i`, `rho = N / V`, and `x_i = n_i / N`. Use these chain-rule derivatives:

  ```text
  d rho / d n_j = 1 / V
  d rho / d V   = -N / V^2
  d x_i / d n_j = (delta_ij - x_i) / N
  d x_i / d V   = 0
  d2 rho / d n_j d V = -1 / V^2
  d2 rho / d V d V   = 2N / V^3
  d2 x_i / d n_j d n_k = (2x_i - delta_ij - delta_ik) / N^2
  ```

- [ ] **Step 3: Build reduced fugacity derivatives**

  For each species `i`, evaluate:

  ```text
  g_i = log(x_i) + ln_phi_i(T, rho, x)
  ```

  Use `phase_state_ln_fugacity_explicit_density_composition_sensitivity_cpp` for `ln_phi_i` derivatives. Add the ideal-mixing derivative terms:

  ```text
  d log(x_i) / d x_j = delta_ij / x_i
  d2 log(x_i) / d x_j d x_k = -delta_ij * delta_ik / x_i^2
  ```

- [ ] **Step 4: Assemble cross-phase residuals**

  Use phase 0 as the reference phase and create residuals:

  ```text
  r_(phase,species) = g_species(phase) - g_species(reference)
  ```

  Produce `(phase_count - 1) * species_count` residuals and dense global Jacobian/Hessian tensors over the amount/volume variable layout.

- [ ] **Step 5: Add the diagnostic binding**

  Expose `_native_phase_equilibrium_residual_block_contract` from `register_bindings.cpp`. Return residual count, square constraint count, derivative backends, shape fields, finite-value checks, and exact derivative booleans.

- [ ] **Step 6: Build and run the residual block tests**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_phase_equilibrium_residual_block_contract.py -q
  ```

- [ ] **Step 7: Commit the residual block**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/phase_equilibrium_residual_block.h packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/phase_equilibrium_residual_block.cpp packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/CMakeLists.txt packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp packages/epcsaft-equilibrium/tests/native/diagnostics/test_phase_equilibrium_residual_block_contract.py
  git commit -m "Add exact phase-equilibrium residual block"
  ```

### Task 4: Add The Strict Multiphase Residual NLP Route

**Use Cases:**
- #261 needs a Stage III refinement route that actively enforces reduced fugacity equality instead of discovering the failure only in postsolve.
- The route must stay private and consume Stage II candidate-set replay for the requested phase-kind list.
- The Ipopt adapter must receive exact Hessian values for all active pressure and reduced fugacity constraints.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`

- [ ] **Step 1: Add `NeutralMultiphaseFugacityResidualProblem`**

  Implement an `NlpProblem` that uses the existing amount/volume variable layout. Its objective is zero. Its constraints are material balance, phase pressure consistency, and the residual block's reduced fugacity equality rows.

- [ ] **Step 2: Implement sparse Jacobian structure**

  Preserve existing material and pressure sparsity. For each reduced fugacity row, include nonzeros for the reference phase local variables and the active phase local variables.

- [ ] **Step 3: Implement exact Lagrangian Hessian assembly**

  Reuse `LagrangianHessianAssembler`. Add pressure constraint Hessians from `EosPhaseSystemResult` and reduced fugacity residual Hessians from `PhaseEquilibriumResidualBlockResult`. Reject route construction if exact Hessian metadata is false.

- [ ] **Step 4: Add the route solver**

  Add a private function shaped like:

  ```cpp
  NeutralTwoPhaseEosRouteResult solve_neutral_multiphase_fugacity_residual_route(
      const add_args& args,
      double temperature,
      double target_pressure,
      const std::vector<double>& feed_composition,
      const std::vector<int>& phase_kinds,
      const IpoptSolveOptions& options,
      double material_tolerance,
      double pressure_tolerance,
      double ln_fugacity_tolerance,
      double phase_distance_tolerance
  );
  ```

  The function must call `evaluate_neutral_tpd_phase_discovery`, require Stage II candidate-set replay readiness, build the initial point from the selected candidate set, run the residual NLP with `held_refinement`, and then call postsolve certification.

- [ ] **Step 5: Expose a private result binding**

  Add `_native_neutral_multiphase_fugacity_residual_route_result`. Return `route_refinement_kind: "strict_fugacity_residual"`, requested phase kinds/count, selected seed attempt statuses, derivative backend labels, exact derivative booleans, and `public_route_admission: "closed"`.

- [ ] **Step 6: Update the #261 native diagnostic test**

  In `test_internal_multiphase_activation_contracts.py`, call the strict residual route for the symmetric ternary case and assert:

  ```python
  assert payload["route_refinement_kind"] == "strict_fugacity_residual"
  assert payload["solver_status"] == "success"
  assert payload["application_status"] == "solve_succeeded"
  assert payload["accepted"] is True
  assert payload["exact_hessian_available"] is True
  assert payload["postsolve"]["ln_fugacity_consistency_norm"] <= 1.0e-6
  assert payload["postsolve"]["held_stage_iii_consumed_stage_ii_replay_metadata"] is True
  assert payload["public_route_admission"] == "closed"
  ```

- [ ] **Step 7: Build and run the native route tests**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_phase_equilibrium_residual_block_contract.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q
  ```

- [ ] **Step 8: Commit the route**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py
  git commit -m "Add strict multiphase fugacity residual route"
  ```

### Task 5: Wire Checker Completion To The Strict Route

**Use Cases:**
- The retained #261 checker needs to distinguish strict fugacity-residual route evidence from a Gibbs-objective route that still fails postsolve.
- A reviewer needs JSON output that names the route kind, residual derivative backend, and exact derivative gate.
- Public route exposure must remain a completion blocker.

**Files:**
- Modify: `scripts/validation/check_generalized_phase_set.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_completion_checker.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_checker.py`

- [ ] **Step 1: Extend completion payload expectations**

  Require `route_refinement_kind == "strict_fugacity_residual"` when `--require-route-refinement` and `--require-complete` are both supplied.

- [ ] **Step 2: Add blocker tests**

  Add payload tests for these blockers:

  ```text
  strict_fugacity_residual_route_missing
  residual_derivative_metadata_missing
  residual_exact_hessian_missing
  stage_iii_ln_fugacity_norm_above_tolerance
  gibbs_objective_only_route_not_certifying
  ```

- [ ] **Step 3: Route native execution through the new binding**

  When `--run-route-refinement` is supplied for at least three phase kinds, call `_native_neutral_multiphase_fugacity_residual_route_result`. Keep the previous diagnostic payload path for record-shape checks when route refinement is not requested.

- [ ] **Step 4: Preserve public closure and native freshness**

  Include the native freshness receipt in the strict route payload and keep `neutral_multiphase_public_route_exposed` as a hard blocker.

- [ ] **Step 5: Run checker tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
  uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete
  ```

- [ ] **Step 6: Commit checker wiring**

  Run:

  ```powershell
  git add scripts/validation/check_generalized_phase_set.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py
  git commit -m "Gate generalized completion on strict residual refinement"
  ```

### Task 6: Record Internal Evidence And Close The Dependency Loop

**Use Cases:**
- #189 needs to show that strict internal residual refinement is complete while final public admission remains open.
- #261 needs a clear next action after this child merges: rerun its generalized phase-set completion proof using the strict route evidence.
- Milestone readers need the difference between diagnostic phase-set records, Gibbs-objective route refinement, and strict residual-route certification.

**Files:**
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/issues/2026-06-15-m4-equilibrium-issue-0261-complete-generalized-phase-set-certification-gate.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`

- [ ] **Step 1: Update GFPE doctrine**

  Add a short note under `PE-Generalized Multiphase` that strict internal Stage III completion now requires the fugacity-residual route, not only a thermodynamic objective route.

- [ ] **Step 2: Update registry evidence**

  Record internal evidence fields for:

  ```text
  strict_multiphase_fugacity_residual_route
  exact_reduced_fugacity_residual_derivatives
  stage_ii_candidate_set_replay_consumed
  public_route_admission_closed
  ```

- [ ] **Step 3: Update issue mirrors**

  Update the new child mirror with proof metrics. Update #189 with the completed child and remaining final public-admission gate. Update #261 so its next execution route is the strict residual checker proof.

- [ ] **Step 4: Run docs validation**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/validate_project.py docs
  ```

- [ ] **Step 5: Commit docs and registry evidence**

  Run:

  ```powershell
  git add docs/superpowers/issues docs/superpowers/milestones/M4-equilibrium
  git commit -m "Record strict multiphase residual refinement evidence"
  ```

### Task 7: Run Proof Oracle And Prepare Merge

**Use Cases:**
- A PR reviewer needs one command set proving exact residual derivatives, strict residual route success, checker completion, public closure, and docs consistency.
- The closeout must preserve #189 as open until final public capability admission is separately planned and proven.
- The branch must be clean enough for the next #261 attempt to start from a synced main branch after merge.

**Files:**
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_phase_equilibrium_residual_block_contract.py`
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`
- Test: `tests/native/contracts/test_generalized_phase_set_completion_checker.py`
- Test: `tests/native/contracts/test_generalized_phase_set_checker.py`
- Test: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`

- [ ] **Step 1: Run the full proof oracle**

  Run:

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

- [ ] **Step 2: Record proof metrics**

  Record route kind, selected candidate count, phase fractions, candidate mass-balance norm, material-balance norm, pressure norm, reduced ln-fugacity norm, phase distance, derivative backends, exact derivative booleans, native freshness receipt, and public exposure status in the issue mirror.

- [ ] **Step 3: Open the PR**

  Use a PR title matching the child issue title and state that this PR supplies an internal prerequisite for #261, not public generalized multiphase admission.

- [ ] **Step 4: Merge and sync**

  After review approval and green proof, merge the PR, sync local `main` and `origin/main`, update mirrors, and reroute #261 to resume on the strict residual proof.

## Proof Oracle

Run these commands from the repo root:

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

## Issue Creation Packet

Title:

```text
M4: add strict multiphase fugacity residual refinement
```

Body:

```markdown
## Summary

Add the #189 child that turns generalized neutral multiphase Stage III refinement into an exact derivative-backed fugacity-residual route. This is the prerequisite exposed by #261: a Gibbs-objective route can converge while the reduced ln-fugacity norm still fails strict phase-equilibrium certification.

## Parent And Dependency

- Parent issue: #189
- Related child waiting on this gate: #261
- Source plan: `docs/superpowers/plans/2026-06-16-m4-equilibrium-issue-0189-strict-multiphase-fugacity-residual-refinement-plan.md`
- Package: `packages/epcsaft-equilibrium`
- Milestone: `M4 - Equilibrium`

## Acceptance Criteria

- [ ] A native phase-equilibrium residual block evaluates reduced fugacity equalities for arbitrary neutral phase counts using exact provider sensitivity data and amount/volume chain rules.
- [ ] A private `NlpProblem` solves the square multiphase fugacity-residual system with material balance, phase pressure consistency, and cross-phase reduced fugacity equality constraints.
- [ ] The route consumes Stage II candidate-set replay metadata and reports Stage III residual-refinement metadata.
- [ ] The strict route reports Ipopt `success`, application `solve_succeeded`, exact derivative evidence, accepted postsolve, and reduced ln-fugacity consistency norm <= `1.0e-6`.
- [ ] Checker and native tests reject missing strict residual-route evidence, missing exact derivative metadata, stale Gibbs-objective-only route evidence, public route exposure, collapsed phases, and residual norms above tolerance.
- [ ] #189 remains open for final public generalized multiphase admission, and #261 is rerouted to use this strict proof after the child merges.

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

## Non-Goals

- No public `neutral_multiphase_nonassoc` route exposure.
- No associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE admission.
- No tolerance relaxation for #261.
- No final closure of #189 from this child alone.
```

Labels:

```text
enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature, agent-ready
```

Milestone:

```text
M4 - Equilibrium
```

## Risk And Dependency Notes

- Risk: the provider sensitivity API returns derivatives in density/composition variables, while the route variables are amounts and volumes. Mitigation: the residual block owns explicit first and second chain-rule transform tests.
- Risk: adding fugacity equality constraints changes the route from a constrained objective minimization to a square equality solve. Mitigation: keep the route private, return `route_refinement_kind: "strict_fugacity_residual"`, and use it only as internal certification evidence until final public admission is planned.
- Risk: #261 already has partial uncommitted implementation work in the current checkout. Mitigation: commit this plan separately, and when implementing the child, start from a clean branch or clean Codex app worktree after deciding how to preserve the current #261 work.
