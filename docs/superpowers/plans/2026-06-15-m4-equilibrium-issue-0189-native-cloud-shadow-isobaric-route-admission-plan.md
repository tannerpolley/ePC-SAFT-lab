# Native Cloud/Shadow Isobaric Route Admission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the next #189 child that proves checker-gated native cloud/shadow isobaric `T-x` route evidence from the retained Matsuda/NIST neutral LLE fixture without exposing public cloud/shadow `Equilibrium` route keys.

**Architecture:** Reuse the existing amount-volume neutral two-liquid NLP and derived-boundary checker instead of adding a separate phase-equilibrium path. The native work adds one internal cloud-temperature proof route that fixes pressure and parent-liquid composition, solves the boundary temperature and incipient second-liquid composition, and reports the incipient composition as the matched shadow phase. The Python checker compares that proof route to the retained source pair and keeps public route exposure closed until a later #189 public-admission child.

**Tech Stack:** C++ native equilibrium routes, pybind11 private bindings, `epcsaft-equilibrium` Python workflow internals, Ipopt exact-Hessian route solves, pytest through `run_pytest.py`, `scripts/validation/check_boundary_workflows.py`, Matsuda/NIST neutral LLE fixture data, Superpowers Project issue mirrors.

---

## Intake

- Direct planning approval: the user asked for `$superpowers-project:write-plan` for the next child under #189.
- Source issue mirror: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Source spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- GFPE doctrine: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Parent GitHub issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`
- Prior #189 children: #252 internal generalized phase-set diagnostics, #256 bubble/dew boundary trace evidence, #258 retained cloud/shadow source-data gate.
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Candidate child title: `M4: admit checker-gated native cloud/shadow isobaric route evidence`

## Planning Decisions

- Scope: source-backed isobaric `T-x` first. This child targets one cloud-temperature native proof route at `P = 101300 Pa` from the Matsuda/NIST fixture.
- Exposure: checker-gated internal evidence. This child must not add public `Equilibrium(route="cloud_temperature")`, `Equilibrium(route="cloud_point")`, or `Equilibrium(route="shadow_point")` route strings.
- Metrics: source fixture thresholds and route residual norms. Test-complete requires strict Ipopt convergence plus fixture threshold comparisons and retained source-data gate success.
- IntelliJ receipt: `ide_index_status` for `C:\Users\Tanner\Documents\Workspaces\Engineering\ePC-SAFT` reported `isDumbMode: false` and `isIndexing: false`. Bundled symbol search was attached to the parent workspace, so exact planning anchors below were verified with narrow repo reads.

## Verified Planning Facts

- Verified: `scripts/validation/check_boundary_workflows.py` already owns derived-boundary workflow checks and the retained cloud/shadow source-data gate.
- Verified: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_requests.py` exposes public route specs for bubble/dew, `flash`, `lle`, and `single_component_vle`, but no public cloud/shadow route spec.
- Verified: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp` implements `solve_neutral_bubble_t_eos_route` and `solve_neutral_dew_t_eos_route` through fixed-pressure temperature route helpers.
- Verified: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp` dispatches public production routes and rejects unsupported selector routes.
- Verified: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp` already exposes private native proof helpers such as `_native_equilibrium_selector_route_result`.
- Verified: `data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane/thresholds.json` contains `solver_max_iterations: 260`, `solver_tolerance: 1.0e-6`, `pressure_abs_Pa: 0.001`, `ln_fugacity_abs: 1.0e-6`, `phase_distance_min: 1.0e-6`, `composition_abs: 0.02`, and `source_temperature_pair_abs_K: 0.2`.
- Verified: `metadata.json` for the Matsuda fixture marks the case neutral, nonelectrolyte, nonreactive, nonassociating, source-backed, and scoped to the current `lle` utility route.
- Inference: the cleanest next #189 slice is a private proof route plus checker gate. Public route-key admission should remain a later child because #189 still has generalized phase-set completion and final public capability admission open.

## Test-Complete Definition And Metrics

This plan is test-complete only when all of the following are true:

- `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate` still exits zero and reports the retained source-data gate complete.
- `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route` exits zero for the Matsuda paired source branch.
- The route proof uses pressure `101300 Pa`, parent-liquid composition `[0.2000, 0.8000]`, expected shadow composition `[0.5497, 0.4503]`, and source temperature `293.895 K` from the paired branch row.
- The solved cloud temperature is within `0.2 K` of the retained paired source temperature.
- The solved shadow composition is within `0.02` mole fraction absolute error for each component against the retained paired source shadow branch.
- The route payload reports `solver_status == "success"`, `application_status == "solve_succeeded"`, exact Hessian evidence, no iteration-limit seed attempt, `pressure_consistency_norm <= 0.001 Pa`, `ln_fugacity_consistency_norm <= 1.0e-6`, `material_balance_norm <= 1.0e-8`, and `phase_distance >= 1.0e-6`.
- Public `Equilibrium` route construction still rejects cloud/shadow route strings, and the activation matrix still has no public cloud/shadow route keys.
- The M4 registry and GFPE doctrine distinguish checker-gated native route evidence from public route admission.

## Acceptance Criteria

- [ ] A private native cloud-temperature proof route solves the retained Matsuda isobaric cloud/shadow pair with strict Ipopt convergence and exact-Hessian diagnostics.
- [ ] The proof route fixes pressure and parent-liquid composition, solves boundary temperature, and reports incipient second-liquid composition as the matched shadow phase.
- [ ] The checker emits a route evidence payload with source fixture path, source row ids, solved temperature, source temperature error, solved shadow composition, shadow composition error, residual norms, solver statuses, seed attempts, and route trace metadata.
- [ ] The retained source-data gate from #258 remains green and remains separate from route-evidence completion.
- [ ] Public cloud/shadow route strings remain closed in `Equilibrium` and in the activation capability mirror.
- [ ] The M4 registry records checker-gated native cloud/shadow route evidence without final public admission.
- [ ] Existing bubble/dew boundary trace validation, neutral LLE showcase validation, and generalized registry tests remain green.
- [ ] #189 remains open after this child unless generalized phase-set completion and final public capability admission are separately proven.

## Non-Goals

- No public `Equilibrium` route key for cloud, shadow, VLLE, LLLE, associating, electrolyte, reactive, CE, or CPE work.
- No cloud-pressure `P-x` route in this child.
- No broad multi-row cloud/shadow validation campaign.
- No synthetic fixture creation.
- No closure of #189 from this child alone.
- No changes to associating, electrolyte, or reactive activation rows.

## File Map

- Create: `tests/native/contracts/test_cloud_shadow_route_admission_checker.py`
- Modify: `scripts/validation/check_boundary_workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Create after issue creation: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-checker-gated-native-cloud-shadow-isobaric-route-evidence.md`

## Tasks

### Task 1: Create The #189 Child Issue And Mirror

**Use Cases:**
- A worker needs a narrow AFK issue because #189 is still a HITL umbrella.
- A reviewer needs the issue to state that this is checker-gated native evidence, not public route exposure.
- The M4 milestone queue needs to show #258 closed and this child as the next source-backed route-evidence slice.

**Files:**
- Create: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-checker-gated-native-cloud-shadow-isobaric-route-evidence.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Confirm the starting state**

  Run:

  ```powershell
  git status --short --branch
  gh issue view 189 --json number,state,labels,milestone,url
  ```

  Expected: clean `main` or a clean `codex/` planning branch, #189 open, milestone `M4 - Equilibrium`, and label `status:ready`.

- [ ] **Step 2: Create one GitHub child issue from the Issue Creation Packet**

  Use the packet at the bottom of this plan. Assign milestone `M4 - Equilibrium` and labels:

  ```text
  enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, agent-ready, type:feature
  ```

  Expected: one new GitHub issue URL.

- [ ] **Step 3: Create the local issue mirror**

  Create `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-checker-gated-native-cloud-shadow-isobaric-route-evidence.md` with the actual issue number and URL. Include the parent #189 link, this plan path, the exact proof oracle, and the non-goals from this plan.

- [ ] **Step 4: Refresh the parent and milestone queue**

  Update the #189 mirror and M4 README so they name this child as the next AFK slice after #258. Keep #189 open and keep #190/#191 blocked by their own proof gates.

- [ ] **Step 5: Commit the tracker setup**

  Run:

  ```powershell
  git add docs/superpowers/issues docs/superpowers/milestones/M4-equilibrium/README.md
  git commit -m "Plan cloud shadow route evidence issue"
  ```

### Task 2: Add Red Checker Tests For Native Route Evidence

**Use Cases:**
- A route worker needs tests that fail while no native cloud-temperature proof route exists.
- A checker reviewer needs proof that the route payload separates source-data completion from native route-evidence completion.
- A capability reviewer needs tests that keep public route strings closed during this internal evidence child.

**Files:**
- Create: `tests/native/contracts/test_cloud_shadow_route_admission_checker.py`
- Modify: `tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py` only if shared fixture constants need to move into the new test file.
- Test: `scripts/validation/check_boundary_workflows.py`

- [ ] **Step 1: Add the missing-route red test**

  Add a test that calls `checker.evaluate_cloud_shadow_route_evidence(CASE_DIR, run_native=True)` and expects the current implementation to report a missing native proof route blocker such as `native_cloud_temperature_route_missing`.

- [ ] **Step 2: Add the route payload contract tests**

  Add tests that require the eventual payload to contain these fields:

  ```python
  {
      "complete",
      "status",
      "source_fixture",
      "route",
      "pressure_Pa",
      "parent_liquid_composition",
      "source_temperature_K",
      "solved_temperature_K",
      "temperature_abs_error_K",
      "source_shadow_composition",
      "solved_shadow_composition",
      "shadow_composition_abs_error",
      "residuals",
      "strict_convergence",
      "solver_status",
      "application_status",
      "seed_attempts",
      "route_trace",
      "public_route_admission",
  }
  ```

- [ ] **Step 3: Add closure tests for public route strings**

  Add tests asserting `Equilibrium(mixture, route="cloud_temperature", P=101300.0, x=[0.2, 0.8])` and `Equilibrium(mixture, route="shadow_point", P=101300.0, x=[0.2, 0.8])` raise `InputError` with route rejection text.

- [ ] **Step 4: Run the red tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_route_admission_checker.py -q
  ```

  Expected: failures caused by the missing `evaluate_cloud_shadow_route_evidence` function or missing native proof route blocker.

- [ ] **Step 5: Commit the red tests**

  Run:

  ```powershell
  git add tests/native/contracts/test_cloud_shadow_route_admission_checker.py
  git commit -m "Add red cloud shadow route evidence tests"
  ```

### Task 3: Add The Private Native Cloud-Temperature Proof Route

**Use Cases:**
- The checker needs a private native route that fixes pressure and parent-liquid composition and solves the cloud temperature plus incipient second-liquid composition.
- The route result must reuse the existing neutral amount-volume NLP, exact derivative route substrate, Ipopt status fields, seed-attempt reporting, and residual diagnostics.
- A public API user must not see new cloud/shadow route strings from this internal proof route.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Test: `tests/native/contracts/test_cloud_shadow_route_admission_checker.py`

- [ ] **Step 1: Declare the native route function**

  In `two_phase_eos_route.h`, add a declaration shaped like the existing fixed-pressure temperature routes:

  ```cpp
  NeutralTwoPhaseEosRouteResult solve_neutral_cloud_t_eos_route(
      const add_args& args,
      double target_pressure,
      const std::vector<double>& parent_liquid_composition,
      const IpoptSolveOptions& options,
      double phase_total_tolerance,
      double pressure_tolerance,
      double chemical_potential_tolerance,
      double phase_distance_tolerance
  );
  ```

- [ ] **Step 2: Implement the route by reusing the fixed-pressure temperature helper**

  In `bubble_dew.cpp`, implement `solve_neutral_cloud_t_eos_route` by calling the fixed-pressure temperature route helper with parent liquid fixed as phase 0, second liquid as phase 1, problem name `neutral_cloud_t_eos`, and liquid-liquid phase roles. Preserve the exact derivative and route metadata already used by bubble/dew temperature routes.

- [ ] **Step 3: Add a private pybind proof helper**

  In `register_bindings.cpp`, add `_native_equilibrium_cloud_shadow_route_result`. It must accept native mixture, request payload with `pressure` and parent liquid `composition`, solver controls, tolerances, and Ipopt keyword controls. It must call `solve_neutral_cloud_t_eos_route`, convert the route result with `neutral_two_phase_eos_route_result_to_dict`, and attach private route metadata:

  ```text
  route = cloud_temperature
  selector_family = cloud_shadow_derived_routes
  problem_name = neutral_cloud_t_eos
  phase_labels = [parent_liquid, shadow_liquid]
  phase_roles = [parent_liquid, incipient_liquid]
  public_route_admission = closed
  ```

- [ ] **Step 4: Keep public selector dispatch closed**

  Do not add `cloud_temperature`, `cloud_point`, or `shadow_point` to `EQUILIBRIUM_ROUTE_SPECS`, `selector_family_for_route`, public `proof_routes`, or public `public_routes`.

- [ ] **Step 5: Run the red route tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_route_admission_checker.py -q
  ```

  Expected: native helper import succeeds, then tests fail only on missing checker comparison logic.

- [ ] **Step 6: Commit the native route helper**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp
  git commit -m "Add private cloud shadow route proof helper"
  ```

### Task 4: Wire The Checker-Gated Route Evidence

**Use Cases:**
- A reviewer needs a single JSON command that runs the native proof route against the retained paired source branch.
- A failed native solve must preserve named route blockers rather than weakening source-data completion.
- A future public-admission worker needs route evidence fields that can be promoted without changing their meaning.

**Files:**
- Modify: `scripts/validation/check_boundary_workflows.py`
- Test: `tests/native/contracts/test_cloud_shadow_route_admission_checker.py`
- Test: `tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py`

- [ ] **Step 1: Add route-evidence constants**

  Add constants for route name `cloud_temperature`, selector family `cloud_shadow_derived_routes`, problem name `neutral_cloud_t_eos`, expected pressure `101300.0`, expected parent branch `[0.2, 0.8]`, expected shadow branch `[0.5497, 0.4503]`, and expected source temperature `293.895`.

- [ ] **Step 2: Add `evaluate_cloud_shadow_route_evidence`**

  Implement `evaluate_cloud_shadow_route_evidence(case_dir: Path = DEFAULT_CLOUD_SHADOW_CASE_DIR, *, run_native: bool = False, debug: bool = False) -> dict[str, Any]`. It must first call `evaluate_cloud_shadow_gate(case_dir)` and report `source_gate_complete: false` if source-data blockers exist. When `run_native` is true, it must call `_core._native_equilibrium_cloud_shadow_route_result` with solver values from `thresholds.json`.

- [ ] **Step 3: Compute source comparison metrics**

  The function must report temperature absolute error, componentwise shadow-composition absolute errors, max shadow-composition absolute error, residual norms, strict convergence, and seed-attempt summary.

- [ ] **Step 4: Enforce test-complete metrics**

  The route-evidence payload is complete only when the source gate is complete, native route proof ran, strict convergence is true, temperature error is at most `source_temperature_pair_abs_K`, max shadow-composition error is at most `composition_abs`, residual norms satisfy fixture thresholds, phase distance is at least `phase_distance_min`, and public route admission remains closed.

- [ ] **Step 5: Add CLI flags**

  Add:

  ```text
  --run-cloud-shadow-route
  --require-cloud-shadow-route
  ```

  JSON output must include `cloud_shadow_route_evidence` when either flag is present. `--require-cloud-shadow-route` must return a nonzero exit code when route-evidence blockers exist.

- [ ] **Step 6: Run checker tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_route_admission_checker.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py -q
  uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
  ```

- [ ] **Step 7: Commit the checker route evidence**

  Run:

  ```powershell
  git add scripts/validation/check_boundary_workflows.py tests/native/contracts/test_cloud_shadow_route_admission_checker.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py
  git commit -m "Add cloud shadow route evidence checker"
  ```

### Task 5: Preserve Public Closure And Activation Evidence

**Use Cases:**
- Public users must not see cloud/shadow route strings until final #189 public admission is separately approved.
- Capability and activation mirrors must show native evidence without claiming public cloud/shadow support.
- Existing public bubble/dew and LLE route behavior must remain unchanged.

**Files:**
- Modify: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`
- Test: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Test: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`

- [ ] **Step 1: Add public-closure API tests**

  In `test_equilibrium.py`, add a parametrized test proving `cloud_temperature`, `cloud_point`, `shadow_point`, and `shadow_temperature` are rejected by public `Equilibrium` construction.

- [ ] **Step 2: Add a non-public activation evidence row only if needed by registry checks**

  If docs/tests require a native evidence row, add `cloud_shadow_derived_routes` to `activation_matrix.h` with `production_exposed = false`, empty `public_routes`, and proof route name `neutral_cloud_temperature_matsuda_ipopt_exact_hessian`. Regenerate or update `equilibrium_activation.py` from the repo generator instead of hand-editing generated structure when the generator is available.

- [ ] **Step 3: Keep public selector dispatch closed**

  Run tests proving `selector_family_for_route` still rejects cloud/shadow route names through public selector dispatch. If a direct C++ test seam is not present, assert rejection through Python `Equilibrium`.

- [ ] **Step 4: Run activation and API checks**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
  ```

- [ ] **Step 5: Commit public closure evidence**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py
  git commit -m "Preserve public cloud shadow route closure"
  ```

### Task 6: Update Registry, GFPE Doctrine, And Parent Progress

**Use Cases:**
- The M4 registry needs to show that cloud/shadow have checker-gated native evidence, while final public admission remains open.
- Future workers need the exact command and metrics that prove native route evidence.
- #189 needs progress notes that name the remaining umbrella gates without closing the umbrella early.

**Files:**
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-checker-gated-native-cloud-shadow-isobaric-route-evidence.md`

- [ ] **Step 1: Update registry acceptance checks**

  Add registry checks such as `checker_gated_native_cloud_temperature_route`, `matched_shadow_composition_evidence`, `source_temperature_tolerance`, `strict_ipopt_convergence`, and `public_route_admission_closed`.

- [ ] **Step 2: Update registry tests**

  Update `test_generalized_equilibrium_registry.py` so cloud/shadow rows require the new route-evidence checks and still reject public runtime route claims.

- [ ] **Step 3: Update GFPE doctrine**

  Add the exact command:

  ```powershell
  uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
  ```

  State that the command proves one checker-gated native isobaric cloud/shadow point and still does not expose public cloud/shadow route keys.

- [ ] **Step 4: Update M4 README and #189 mirror**

  Add retained evidence for this child and state the remaining #189 gates: generalized phase-set completion and final public capability admission.

- [ ] **Step 5: Run registry and docs checks**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
  uv run --no-sync python scripts/dev/validate_project.py docs
  ```

- [ ] **Step 6: Commit docs and registry evidence**

  Run:

  ```powershell
  git add docs/superpowers/milestones/M4-equilibrium docs/superpowers/issues tests/native/contracts/test_generalized_equilibrium_registry.py
  git commit -m "Document cloud shadow route evidence gate"
  ```

### Task 7: Final Proof Oracle And Closeout

**Use Cases:**
- A PR reviewer needs one proof oracle proving native route evidence, source-data retention, public closure, and no regression in prior #189 children.
- A tracker reviewer needs #189 to remain open with a clear remaining-gate list.
- If native build freshness is stale, closeout must fail loudly and require a rebuild receipt before merge.

**Files:**
- Modify: `docs/superpowers/issues/<yyyy-mm-dd>-m4-equilibrium-issue-<number>-checker-gated-native-cloud-shadow-isobaric-route-evidence.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Run the full proof oracle**

  Run every command in the Proof Oracle section below.

- [ ] **Step 2: Capture route metrics in the child issue mirror**

  Record solved temperature, source temperature, temperature error, solved shadow composition, source shadow composition, max composition error, residual norms, solver status, application status, and native build freshness receipt.

- [ ] **Step 3: Confirm public route closure**

  Confirm public cloud/shadow route strings still fail through the public API tests and that no capability page claims public cloud/shadow support.

- [ ] **Step 4: Add #189 progress comment**

  Comment on #189 that this child proves one checker-gated isobaric native cloud/shadow route point and leaves generalized phase-set completion plus public admission open.

- [ ] **Step 5: Run the cleanup hook**

  Run:

  ```powershell
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  ```

- [ ] **Step 6: Commit final mirror evidence**

  Run:

  ```powershell
  git add docs/superpowers/issues docs/superpowers/milestones/M4-equilibrium/README.md
  git commit -m "Record cloud shadow route evidence closeout"
  ```

## Proof Oracle

Run these commands from the repo root:

```powershell
uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_route_admission_checker.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

If native files change, include the repo-supported native build refresh command recorded by the current validation checker before running the proof oracle. The route proof is incomplete without a fresh native receipt naming the current git commit and imported native module path.

## Issue Creation Packet

Create one AFK child issue from this plan.

Title:

```text
M4: admit checker-gated native cloud/shadow isobaric route evidence
```

Body:

```markdown
## Summary

Add the next #189 child after #258: prove one checker-gated native isobaric cloud/shadow route point from the retained Matsuda/NIST perfluorohexane + hexane neutral LLE fixture. This issue converts the existing cloud/shadow source-data gate into native route evidence while keeping public cloud/shadow route keys closed.

## Parent

- Parent issue: #189
- Source plan: `docs/superpowers/plans/2026-06-15-m4-equilibrium-issue-0189-native-cloud-shadow-isobaric-route-admission-plan.md`
- Prior children: #252 internal generalized phase-set diagnostics; #256 bubble/dew boundary traces; #258 retained cloud/shadow source-data gate.

## Acceptance Criteria

- [ ] A private native cloud-temperature proof route solves the retained Matsuda paired branch at 101300 Pa with strict Ipopt convergence and exact-Hessian diagnostics.
- [ ] The route fixes parent-liquid composition `[0.2000, 0.8000]`, solves the boundary temperature, and reports matched shadow composition against `[0.5497, 0.4503]`.
- [ ] The checker reports solved/source temperature, temperature error, solved/source shadow composition, composition error, route residuals, seed attempts, solver status, application status, native receipt, and route trace metadata.
- [ ] The route proof satisfies source fixture metrics: temperature error <= 0.2 K, max shadow-composition error <= 0.02, material-balance residual <= 1.0e-8, pressure residual <= 0.001 Pa, ln-fugacity residual <= 1.0e-6, and phase distance >= 1.0e-6.
- [ ] The retained source-data gate from #258 remains green.
- [ ] Public cloud/shadow route strings remain closed in `Equilibrium` and activation/capability mirrors.
- [ ] Existing bubble/dew boundary trace validation, neutral LLE showcase validation, and registry tests remain green.
- [ ] #189 remains open after this child unless generalized phase-set completion and final public capability admission are separately proven.

## Proof Oracle

```powershell
uv run --no-sync python run_pytest.py tests/native/contracts/test_cloud_shadow_route_admission_checker.py tests/native/contracts/test_cloud_shadow_boundary_gate_checker.py tests/native/contracts/test_boundary_workflow_checker.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --contracts-only
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate
uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route
uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py --case-dir data/reference/equilibrium_benchmarks/neutral_lle/matsuda_2011_pfhexane_hexane --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Non-Goals

- No public cloud/shadow route key exposure.
- No cloud-pressure route in this issue.
- No associating, electrolyte, reactive, CE, CPE, LLLE, or VLLE admission.
- No closure of #189 from this child alone.
```

Labels:

```text
enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, agent-ready, type:feature
```

Milestone:

```text
M4 - Equilibrium
```

## Risk And Dependency Notes

- Risk: the phrase route admission can be misread as public API exposure. Mitigation: this plan consistently requires checker-gated internal evidence and explicit public route closure tests.
- Risk: the native route may need seed work beyond the existing bubble/dew temperature helper because this is a liquid-liquid boundary, not a vapor-liquid boundary. Mitigation: Task 3 keeps the route private and Task 4 fails with named route blockers until strict convergence and source metrics pass.
- Risk: generated activation mirrors can drift if edited by hand. Mitigation: use the existing generator when changing activation rows; otherwise leave generated mirrors untouched and prove public route closure through API tests.
- Dependency: native build freshness matters. A passing Python checker that imports an old native module is not completion evidence.
