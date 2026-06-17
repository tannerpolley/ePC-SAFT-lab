# Generalized Neutral Multiphase Admission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the final #189 child that admits the certified neutral generalized multiphase phase-set route through the public `Equilibrium(..., route="multiphase", ...)` API after #263 and #261 are merged.

**Architecture:** Promote the already certified internal `neutral_multiphase_nonassoc` family from declared-not-exposed evidence into a production-exposed public route only after the strict residual route and #261 completion checker pass. The public Python workflow remains constructor-configured, requires explicit `phase_kinds`, calls the strict native multiphase fugacity-residual route, and returns the existing `EquilibriumResult`/`EquilibriumPhase` dataclasses with arbitrary phase labels. Capability, registry, checker, and docs gates all move from "internal evidence only" to "public neutral multiphase admitted" without admitting associating, electrolyte, or reactive families.

**Tech Stack:** `epcsaft-equilibrium` Python workflow objects, generated activation matrix, C++ native equilibrium activation metadata, strict Ipopt/CppAD multiphase fugacity-residual route from #263, generalized phase-set checker from #261, pytest through `run_pytest.py`, M4 registry and issue mirrors.

---

## Intake

- Direct planning approval: user invoked `$superpowers-project:write-plan` for a new child under #189, selected `Final admission`, and selected public route key `multiphase`.
- Parent issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`
- Satisfied prerequisites: #263 strict multiphase fugacity-residual refinement and #261 generalized phase-set certification gate.
- Source issue mirror: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source prerequisite plan: `docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-generalized-phase-set-certification-gate-plan.md`
- Strict residual prerequisite plan: `docs/superpowers/plans/2026-06-16-m4-equilibrium-issue-0189-strict-multiphase-fugacity-residual-refinement-plan.md`
- GFPE doctrine: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Candidate child title: `M4: admit generalized neutral multiphase phase-set PE`

## Planning Decisions

- Public route key: `multiphase`.
- Public API shape: `Equilibrium(mixture, route="multiphase", T=..., P=..., z=..., phase_kinds=["liquid", "liquid", "liquid"]).solve(...)`.
- `phase_kinds` is required for `route="multiphase"` and rejected for existing fixed-shape routes.
- The first public admission proof is the neutral nonassociating `liquid,liquid,liquid` symmetric ternary case already used by the generalized phase-set checker. The API accepts explicit neutral phase-kind lists only when the native strict route and checker certify them.
- This child changes `neutral_multiphase_nonassoc` from `declared_not_exposed` to `production_exposed` and gives it public route `multiphase`.
- This child may close #189 only if #263 and #261 are both merged, the public route proof passes, the M4 registry row becomes production-backed, and associating/electrolyte/reactive remaining work stays tracked in #190/#191/#145.
- No public admission is allowed from diagnostic records alone, a Gibbs-objective-only route, stale native artifacts, or checker JSON that has not exercised the public `Equilibrium` API.

## Test-Complete Definition And Metrics

This plan is complete only when all of the following are true:

- #263 is closed and the strict residual route exists: `_native_neutral_multiphase_fugacity_residual_route_result` reports `route_refinement_kind == "strict_fugacity_residual"`, exact derivative evidence, and `ln_fugacity_consistency_norm <= 1.0e-6`.
- #261 is closed and `scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete` exits zero on a fresh native build.
- The new public route call returns three phases through `EquilibriumResult` with normalized compositions, positive phase fractions, immutable diagnostics, route `multiphase`, selector family `neutral_multiphase_nonassoc`, and postsolve certification accepted.
- Public-route metrics satisfy candidate mass-balance norm <= `1.0e-6`, material-balance norm <= `1.0e-8`, pressure consistency norm <= `1.0e-3 Pa`, reduced ln-fugacity consistency norm <= `1.0e-6`, positive phase distance, normalized phase compositions, strictly positive phase fractions, exact Hessian evidence, and no selected seed attempt ending in an iteration-limit status.
- `epcsaft_equilibrium.capabilities()` reports `multiphase` in `public_routes`, maps it to `neutral_multiphase_nonassoc`, includes `neutral_multiphase_nonassoc` in `production_families`, removes it from `declared_not_exposed_families`, and includes derivative evidence for the strict residual route.
- The M4 `PE-Generalized Multiphase` registry row records production exposure with the public proof command and does not keep an internal-only admission condition for neutral nonassociating multiphase.
- The final proof oracle below passes from the repo root after a fresh native build and cleanup hook.

## Acceptance Criteria

- [ ] The #189 child issue and local mirror define the final public admission gate and are ready after #261 internal certification merged.
- [ ] `Equilibrium` accepts `phase_kinds` for `route="multiphase"`, rejects missing or malformed `phase_kinds`, rejects associating and ionic mixtures, and rejects `phase_kinds` on existing fixed-shape public routes.
- [ ] `EQUILIBRIUM_ROUTE_SPECS`, workflow dispatch, and result conversion route public `multiphase` calls through the strict native multiphase fugacity-residual route.
- [ ] Activation metadata, generated Python mirror, capabilities, and derivative-evidence rows expose `neutral_multiphase_nonassoc` as production with public route `multiphase`.
- [ ] The generalized phase-set checker adds public-admission mode that requires public API proof instead of treating public route exposure as a blocker.
- [ ] API, activation, checker, registry, and docs tests prove the admitted route and prevent claims for associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE families.
- [ ] M4 registry, GFPE doctrine, M4 README, and #189 mirror record #189 completion while leaving #145/#190/#191 as separate future gates.

## Non-Goals

- No associating neutral LLE admission.
- No electrolyte LLE, HELD2.0, reactive LLE, reactive electrolyte LLE, CE, CPE, LLLE, or VLLE admission.
- No M3 provider or M5 regression implementation changes except using already exposed provider contracts from equilibrium-owned code.
- No relaxation of #261/#263 numerical metrics.
- No public route aliases beyond `multiphase`.
- No release publication or downstream integration proof.

## File Map

- Create after issue creation: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-admit-generalized-neutral-multiphase-phase-set-pe.md`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_requests.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/activation/activation_matrix.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_completion_checker.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_checker.py`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `scripts/validation/check_generalized_phase_set.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`

## Tasks

### Task 1: Create The Final #189 Admission Child

**Use Cases:**
- A tracker owner needs one final #189 child that becomes ready once #261 internal certification is merged.
- A worker needs the issue to distinguish public neutral multiphase admission from the already planned #263 strict route and #261 internal checker gates.
- A reviewer needs the issue body to say exactly why #145/#190/#191 remain separate after #189 closes.

**Files:**
- Create: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-admit-generalized-neutral-multiphase-phase-set-pe.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Confirm live dependency state**

  Run:

  ```powershell
  gh issue view 189 --repo ePC-SAFT/ePC-SAFT --json number,title,state,labels,milestone,url
  gh issue view 261 --repo ePC-SAFT/ePC-SAFT --json number,title,state,labels,milestone,url
  gh issue view 263 --repo ePC-SAFT/ePC-SAFT --json number,title,state,labels,milestone,url
  gh api /repos/ePC-SAFT/ePC-SAFT/issues/261/dependencies/blocked_by
  git status --short --branch
  ```

  Expected: #189 is open in `M4 - Equilibrium`; #261 and #263 are closed; this child is ready once its local mirror and source plan are committed.

- [ ] **Step 2: Create the GitHub child issue**

  Use the Issue Creation Packet in this plan. Apply milestone `M4 - Equilibrium`. Before #261 closes, apply labels:

  ```text
  enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
  ```

  After #261 closes, readiness sync should move it to `status:ready`; add `agent-ready` after the local mirror and source plan are committed.

- [ ] **Step 3: Add the native dependency edge**

  If #261 is still open, run:

  ```powershell
  $blocking = gh issue view 261 --repo ePC-SAFT/ePC-SAFT --json id --jq .id
  gh api -X POST /repos/ePC-SAFT/ePC-SAFT/issues/<new-issue-number>/dependencies/blocked_by -F issue_id=$blocking
  ```

- [ ] **Step 4: Create the local mirror**

  Create the mirror with the actual issue number, #189 parent URL, #261 dependency, this source plan path, the proof oracle, and the non-goals.

- [ ] **Step 5: Update queue context**

  Update #189 and the M4 README so the queue says: #263 strict residual route -> #261 internal certification -> this child final public neutral multiphase admission.

- [ ] **Step 6: Commit tracker setup**

  Run:

  ```powershell
  git add docs/superpowers/issues docs/superpowers/milestones/M4-equilibrium/README.md
  git commit -m "Create generalized neutral multiphase admission issue"
  ```

### Task 2: Add Red Public Admission API Tests

**Use Cases:**
- A package user needs to call one public generic route for certified neutral multiphase phase-set PE.
- A public API reviewer needs `phase_kinds` to be explicit so the route does not invent a hidden phase model.
- A package maintainer needs associating and ionic mixtures rejected before native dispatch.

**Files:**
- Modify: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_requests.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`

- [ ] **Step 1: Add constructor-shape tests**

  In `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`, add tests asserting:

  ```python
  equilibrium = equilibrium_module.Equilibrium(
      mixture,
      route="multiphase",
      T=200.0,
      P=1.0e6,
      z=[1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
      phase_kinds=["liquid", "liquid", "liquid"],
  )
  assert equilibrium.problem.route == "multiphase"
  assert equilibrium.problem.selector_route == "neutral_multiphase_nonassoc"
  assert equilibrium.problem.activation_key == "neutral_multiphase_nonassoc"
  assert equilibrium.problem.expected_phase_keys == ("liquid1", "liquid2", "liquid3")
  assert equilibrium.problem.fixed_specs["phase_kinds"] == ("liquid", "liquid", "liquid")
  ```

- [ ] **Step 2: Add input rejection tests**

  Add tests requiring `phase_kinds` for `route="multiphase"`, rejecting fewer than three phase kinds, rejecting unknown phase-kind strings, rejecting non-`z` compositions, rejecting `phase_kinds` for `flash`/`lle`, rejecting associating mixtures, and rejecting ionic mixtures.

- [ ] **Step 3: Add public solve test**

  Add an Ipopt-gated test calling:

  ```python
  result = equilibrium_module.Equilibrium(
      mixture,
      route="multiphase",
      T=200.0,
      P=1.0e6,
      z=[1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
      phase_kinds=["liquid", "liquid", "liquid"],
  ).solve(
      solver_options={
          "max_iterations": 320,
          "tolerance": 1.0e-8,
          "ipopt_iteration_history_limit": 12,
          "ipopt_acceptable_tolerance": 1.0e-8,
          "ipopt_constraint_violation_tolerance": 1.0e-8,
          "ipopt_dual_infeasibility_tolerance": 1.0e-8,
          "ipopt_complementarity_tolerance": 1.0e-8,
      }
  )
  ```

  Assert route `multiphase`, selector route `neutral_multiphase_nonassoc`, phase labels `["liquid1", "liquid2", "liquid3"]`, three positive phase fractions summing to one, normalized phase compositions, exact Hessian diagnostics, route kind `strict_fugacity_residual`, and postsolve `ln_fugacity_consistency_norm <= 1.0e-6`.

- [ ] **Step 4: Run red API tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py -q
  ```

  Expected: the new `multiphase` tests fail because `phase_kinds` and the public route are not wired.

- [ ] **Step 5: Commit red API tests**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/tests/api/test_equilibrium.py
  git commit -m "Add red public multiphase route tests"
  ```

### Task 3: Wire The Public `multiphase` Workflow

**Use Cases:**
- A user needs constructor validation, structure metadata, and solve behavior to use the same workflow object as existing routes.
- The workflow must call the strict residual route from #263, not the older thermodynamic-objective route.
- Public result conversion must support arbitrary phase counts without renaming the existing result dataclasses.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_requests.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`

- [ ] **Step 1: Extend `Equilibrium.__init__`**

  Add `phase_kinds: Sequence[str] | None = None` and pass it into `configure_equilibrium_problem`. Reject it for non-`multiphase` routes inside workflow validation.

- [ ] **Step 2: Add the route spec**

  Add `multiphase` to `EQUILIBRIUM_ROUTE_SPECS` with:

  ```python
  NativeSelectorRouteSpec(
      selector_route="neutral_multiphase_nonassoc",
      composition_key="z",
      composition_role="feed",
      requires_temperature=True,
      requires_pressure=True,
      knowns=("T", "P", "z", "phase_kinds"),
      unknowns=("phase_compositions", "phase_amounts", "phase_volumes"),
      problem_kind="neutral_multiphase_nonassoc",
      route_label="multiphase",
      selector_family="neutral_multiphase_nonassoc",
      phase_labels=(),
  )
  ```

- [ ] **Step 3: Normalize explicit phase kinds**

  Add a helper that accepts only non-empty strings from `{"liquid", "vapor"}`, requires at least three entries, and returns an immutable tuple. For the first admitted proof, tests must exercise `("liquid", "liquid", "liquid")`.

- [ ] **Step 4: Dispatch to the strict native route**

  In `_solve_selector_route`, branch on `problem.route == "multiphase"` and call a new helper that invokes `_native_neutral_multiphase_fugacity_residual_route_result` with the fixed specs, normalized phase kinds, and `neutral_two_phase_eos_tolerances`.

- [ ] **Step 5: Convert arbitrary phase payloads**

  Add `neutral_phase_payload_to_result` or rename the existing conversion helper so it accepts any positive phase count. Preserve existing two-phase callers while making the public multiphase route set `route="multiphase"`, `selector_route="neutral_multiphase_nonassoc"`, `problem_kind="neutral_multiphase_nonassoc"`, and feed composition `z`.

- [ ] **Step 6: Preserve result immutability and diagnostics**

  Ensure `EquilibriumResult.phase_labels`, `.phase_compositions`, `.phase_fractions`, `.z`, `.to_dict()`, and `.route_diagnostics` work for `liquid1`/`liquid2`/`liquid3`. Keep `.x`, `.y`, `.liquid_fraction`, and `.vapor_fraction` raising `AttributeError` for this route.

- [ ] **Step 7: Build and run API tests**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py -q
  ```

- [ ] **Step 8: Commit public workflow wiring**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_requests.py packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_results.py packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py
  git commit -m "Expose public neutral multiphase route workflow"
  ```

### Task 4: Promote Activation And Capability Metadata

**Use Cases:**
- `capabilities()` must tell downstream users that `multiphase` is now a production route.
- Activation tests must fail if the family stays declared-not-exposed after public API proof exists.
- Derivative evidence must state the strict residual route and exact derivative source.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/activation/activation_matrix.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`

- [ ] **Step 1: Update native activation metadata**

  Change the `neutral_multiphase_nonassoc` row to:

  ```text
  production_exposed: true
  exposure_status: production_exposed
  proof_routes: strict_multiphase_fugacity_residual_route
  public_routes: multiphase
  constraint_families: material_balance, phase_pressure_consistency, phase_equilibrium
  ```

- [ ] **Step 2: Regenerate the Python activation mirror**

  Run the repo generator used by `test_generated_activation_mirror_matches_native_source_of_truth`. If the generator path has changed, inspect `scripts/dev` and use the current activation-generation command. Commit only the regenerated mirror and source activation metadata.

- [ ] **Step 3: Add capability section and derivative evidence**

  Add a `neutral_multiphase_nonassoc` capability block with entrypoint:

  ```text
  Equilibrium(mixture, route='multiphase', T=..., P=..., z=..., phase_kinds=[...]).solve()
  ```

  Add route derivative evidence with quantity `neutral_multiphase_nonassoc`, backend `cppad_explicit_density`, and test references to the public API and strict residual route tests.

- [ ] **Step 4: Update activation capability tests**

  Update expected production families, public route map, public route list, public routes by family, and derivative-evidence quantity set to include `multiphase`.

- [ ] **Step 5: Run activation tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
  ```

- [ ] **Step 6: Commit activation and capabilities**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/activation/activation_matrix.cpp packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py
  git commit -m "Admit neutral multiphase route capabilities"
  ```

### Task 5: Add Public Admission Checker Mode

**Use Cases:**
- The retained generalized phase-set checker must prove both internal certification and public API admission.
- A stale internal-only checker should fail once this child claims #189 completion.
- A reviewer needs a single JSON payload showing public route evidence and strict residual evidence together.

**Files:**
- Modify: `scripts/validation/check_generalized_phase_set.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_completion_checker.py`
- Modify: `tests/native/contracts/test_generalized_phase_set_checker.py`

- [ ] **Step 1: Add `--require-public-admission`**

  Extend the CLI with:

  ```text
  --require-public-admission
  ```

  In this mode, public route exposure is required and must map to `neutral_multiphase_nonassoc`.

- [ ] **Step 2: Add public API execution to checker output**

  When `--require-public-admission` is present, call `Equilibrium(..., route="multiphase", phase_kinds=[...]).solve(...)` after the strict native route check and record:

  ```text
  public_route: multiphase
  public_selector_family: neutral_multiphase_nonassoc
  public_phase_count
  public_phase_labels
  public_phase_fraction_sum
  public_postsolve_accepted
  public_ln_fugacity_consistency_norm
  public_exact_hessian_available
  ```

- [ ] **Step 3: Update checker blockers**

  In public-admission mode, fail on:

  ```text
  public_multiphase_route_missing
  public_multiphase_route_wrong_family
  public_multiphase_solve_failed
  public_multiphase_phase_count_mismatch
  public_multiphase_postsolve_not_accepted
  public_multiphase_exact_hessian_missing
  public_multiphase_ln_fugacity_norm_above_tolerance
  ```

  Remove the old public-exposure blocker from public-admission mode.

- [ ] **Step 4: Keep internal checker behavior explicit**

  Preserve a clear internal-check path for historical #252/#261 evidence when `--require-public-admission` is absent. Its output should state `admission_mode: internal_certification` or `admission_mode: public_admission` so future agents cannot confuse the modes.

- [ ] **Step 5: Run checker tests and admission command**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py -q
  uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-public-admission --require-complete
  ```

- [ ] **Step 6: Commit checker admission mode**

  Run:

  ```powershell
  git add scripts/validation/check_generalized_phase_set.py tests/native/contracts/test_generalized_phase_set_completion_checker.py tests/native/contracts/test_generalized_phase_set_checker.py
  git commit -m "Require public proof for multiphase admission"
  ```

### Task 6: Update Registry, GFPE Doctrine, And #189 Closure Evidence

**Use Cases:**
- M4 readers need the registry to show `PE-Generalized Multiphase` as admitted for neutral nonassociating public use.
- The doctrine must not leave stale internal-only language after `multiphase` is public.
- #189 needs exact closeout language that does not also close #145/#190/#191.

**Files:**
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-admit-generalized-neutral-multiphase-phase-set-pe.md`

- [ ] **Step 1: Add red registry expectations**

  Update tests to require `PE-Generalized Multiphase` to carry:

  ```text
  activation_status: production_public
  production_exposed: true
  public_routes: multiphase
  public_entrypoint: Equilibrium(mixture, route='multiphase', T=..., P=..., z=..., phase_kinds=[...]).solve()
  acceptance_checks: strict_multiphase_fugacity_residual_route, public_multiphase_route, exact_hessian_evidence, generalized_phase_set_public_admission_checker
  ```

- [ ] **Step 2: Update registry data**

  Update the `PE-Generalized Multiphase` row to cite the new public checker command and retain the source-backed prior evidence from #252/#256/#258/#260/#263/#261.

- [ ] **Step 3: Update GFPE doctrine**

  Replace internal-only neutral generalized multiphase language with a statement that neutral nonassociating public `multiphase` admission is supported by strict residual-route proof. Keep associating/electrolyte/reactive sections blocked on their own gates.

- [ ] **Step 4: Update M4 README and issue mirrors**

  Add retained evidence for:

  ```powershell
  uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-public-admission --require-complete
  ```

  Update #189 to state its neutral boundary/generalized phase-set scope is complete after this child, with #145/#190/#191 still owning associating/electrolyte follow-up.

- [ ] **Step 5: Run docs and registry checks**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
  uv run --no-sync python scripts/dev/validate_project.py docs
  ```

- [ ] **Step 6: Commit docs and registry admission evidence**

  Run:

  ```powershell
  git add tests/native/contracts/test_generalized_equilibrium_registry.py docs/superpowers/milestones/M4-equilibrium docs/superpowers/issues
  git commit -m "Record public generalized multiphase admission evidence"
  ```

### Task 7: Run Full Proof, Open PR, And Close #189 When Merged

**Use Cases:**
- A PR reviewer needs one proof set covering public API, activation, checker, registry, docs, native strict route, and prior #189 evidence.
- The merge owner needs dependency readiness to unblock downstream M4 children without stale local mirrors.
- The tracker needs #189 closed only after the public route is merged and local/origin mains are synced.

**Files:**
- Test: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`
- Test: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py`
- Test: `tests/native/contracts/test_generalized_phase_set_completion_checker.py`
- Test: `tests/native/contracts/test_generalized_phase_set_checker.py`
- Test: `tests/native/contracts/test_generalized_equilibrium_registry.py`

- [ ] **Step 1: Run the full proof oracle**

  Run every command in the Proof Oracle section below from the repo root.

- [ ] **Step 2: Record proof metrics**

  Record public route key, selector family, selected candidate count, phase labels, phase fractions, candidate mass-balance norm, material-balance norm, pressure norm, reduced ln-fugacity norm, phase distance, derivative backend, exact derivative booleans, native freshness receipt, and capabilities public-route map in the child mirror and PR body.

- [ ] **Step 3: Open the PR**

  PR title:

  ```text
  M4: admit generalized neutral multiphase phase-set PE
  ```

  PR body must name #189 and the child issue, state that #145/#190/#191 remain open, and include the full proof oracle.

- [ ] **Step 4: Merge and sync**

  After merge, sync local `main` and `origin/main`, run dependency readiness sync for the closed child, and update the local M4 mirror table if the workflow cannot push mirror changes.

- [ ] **Step 5: Close #189**

  Close #189 with a comment listing the merged children that satisfy its acceptance gates: #252, #256, #258, #260, #263, #261, and this child. State that associating/electrolyte/reactive adoption is tracked separately by #145/#190/#191.

## Proof Oracle

Run these commands from the repo root:

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

## Issue Creation Packet

Title:

```text
M4: admit generalized neutral multiphase phase-set PE
```

Body:

```markdown
## Summary

Add the final #189 child that admits certified neutral generalized multiphase phase-set PE through the public `Equilibrium(mixture, route="multiphase", T=..., P=..., z=..., phase_kinds=[...]).solve()` workflow after #263 and #261 closed.

## Parent And Dependencies

- Parent issue: #189
- Previously blocked by: #261 until generalized phase-set certification merged.
- Indirect prerequisite: #263 strict multiphase fugacity-residual refinement.
- Source plan: `docs/superpowers/plans/2026-06-16-m4-equilibrium-issue-0189-generalized-neutral-multiphase-admission-plan.md`
- Package: `packages/epcsaft-equilibrium`
- Milestone: `M4 - Equilibrium`

## Acceptance Criteria

- [ ] Public `Equilibrium(..., route="multiphase", T=..., P=..., z=..., phase_kinds=[...]).solve()` is implemented for neutral nonassociating generalized multiphase PE.
- [ ] Public route execution calls the strict multiphase fugacity-residual route from #263 and requires the #261 generalized phase-set certification metrics.
- [ ] The public result reports route `multiphase`, selector family `neutral_multiphase_nonassoc`, three named phases for the proof case, normalized compositions, positive phase fractions, exact Hessian evidence, and accepted postsolve.
- [ ] Completion metrics satisfy candidate mass-balance norm <= `1.0e-6`, material-balance norm <= `1.0e-8`, pressure consistency norm <= `1.0e-3 Pa`, ln-fugacity consistency norm <= `1.0e-6`, positive phase distance, normalized compositions, and strictly positive phase fractions.
- [ ] `epcsaft_equilibrium.capabilities()` reports `multiphase` as a public production route mapped to `neutral_multiphase_nonassoc`.
- [ ] The generalized phase-set checker has public-admission mode and passes with `--require-public-admission --require-complete`.
- [ ] M4 registry, GFPE doctrine, M4 README, and #189 mirror record public neutral generalized multiphase admission.
- [ ] #189 closes only after this child merges; #145/#190/#191 remain separate for associating/electrolyte/reactive follow-up.

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

## Non-Goals

- No associating neutral LLE admission.
- No electrolyte LLE, HELD2.0, reactive LLE, reactive electrolyte LLE, CE, CPE, LLLE, or VLLE admission.
- No M3 provider or M5 regression implementation changes.
- No relaxation of #261/#263 numerical metrics.
- No release publication or downstream integration proof.
```

Labels before #261 closes:

```text
enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
```

Labels after #261 closes and the local mirror exists:

```text
enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
```

Milestone:

```text
M4 - Equilibrium
```

## Risk And Dependency Notes

- Risk: #263 or #261 may still change field names before this child starts. Mitigation: Task 1 requires live tracker and mirror review before issue creation, and Task 5 updates checker mode from the merged payload shape.
- Risk: public route admission can overstate scope. Mitigation: capabilities and docs must say neutral, nonreactive, non-electrolyte, nonassociating generalized multiphase only; #145/#190/#191 remain open.
- Risk: `multiphase` could be called with unsupported explicit phase-kind lists. Mitigation: the public workflow requires explicit `phase_kinds`, validates names and count, and surfaces native certification failure through `SolutionError` with diagnostics.
- Risk: existing helper names still say two-phase. Mitigation: Task 3 introduces or renames public conversion helpers at the workflow boundary where arbitrary phase counts are returned, without a broad native file rename.
