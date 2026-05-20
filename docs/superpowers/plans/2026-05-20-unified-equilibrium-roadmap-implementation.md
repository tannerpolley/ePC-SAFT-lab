# Unified Equilibrium Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the remaining `docs/roadmaps/unified_equilibrium_core_algorithm.md` gaps by extending the existing native Ipopt route, reactive residual, stability, certification, benchmark, and capability-evidence modules.

**Architecture:** This plan keeps one connected equilibrium implementation. It extends current route builders, typed public dispatch, pybind payloads, `native_results.py` certification, validation lanes, and `capabilities()` evidence instead of adding a parallel solver, Python optimizer loop, or staged fallback route.

**Tech Stack:** C++ native ePC-SAFT, pybind11, Ipopt TNLP adapter, CppAD/analytic derivatives, Python public API wrappers, pytest via `run_pytest.py` for package contracts, explicit analysis/benchmark scripts for paper validation, GoalBuddy for execution tracking.

---

## Dependency Mesh To Preserve

The implementation must keep these modules connected:

- Public API and dispatch:
  - `src/epcsaft/epcsaft.py`
  - `src/epcsaft/equilibrium.py`
  - `src/epcsaft/__init__.py`
- Python result/capability contracts:
  - `src/epcsaft/equilibrium_core/native_results.py`
  - `src/epcsaft/capability_evidence.py`
  - `src/epcsaft/runtime.py`
- Native Ipopt and route infrastructure:
  - `src/epcsaft/native/equilibrium_nlp/ipopt_adapter.h`
  - `src/epcsaft/native/equilibrium_nlp/stability_route_builders.h`
  - `src/epcsaft/native/equilibrium_nlp/stability_route_builders.cpp`
  - `src/epcsaft/native/equilibrium_nlp/route_builders.h`
  - `src/epcsaft/native/equilibrium_nlp/route_builders.cpp`
  - `src/epcsaft/native/equilibrium_nlp/route_metadata.h`
  - `src/epcsaft/native/equilibrium/reactive_phase_equilibrium_problem.cpp`
  - `src/epcsaft/native/epcsaft_equilibrium.h`
  - `src/epcsaft/bindings.cpp`
- Current executable evidence:
  - `tests/api/equilibrium/core/test_native_results.py`
  - `tests/native/equilibrium/test_native_route_diagnostics_contract.py`
  - `tests/native/equilibrium/test_route_metadata_contracts.py`
  - `tests/native/equilibrium/test_route_builders_stability.py`
  - `tests/native/equilibrium/test_chemical_equilibrium_native_api.py`
  - `tests/api/equilibrium/reactive/test_reactive_electrolyte_lle_coupled_solver.py`
  - `tests/api/reactive/test_reactive_phase_equilibrium_problem_routes_native.py`
  - `tests/api/runtime/test_runtime_capabilities_dependency_gates.py`

## Non-Negotiable Design Rules

- Do not add a Python production optimizer loop.
- Do not introduce a staged speciation fallback for `reactive_stability`.
- Do not create a separate public result family when an existing result shape can carry the evidence.
- Do not promote reactive LLE or reactive electrolyte LLE in `capabilities()` until executable benchmark proof passes.
- Keep `auto` Hessian behavior exact-or-loud for production native Ipopt routes.
- Treat route-builder convergence as insufficient unless shared postsolve certification accepts.
- Keep blocked scientific evidence as a failing or blocked benchmark/analysis lane, not as a pytest gate or capability claim.

## Task 1: Strengthen Shared Certification Shape

**Files:**
- Modify: `src/epcsaft/equilibrium_core/native_results.py`
- Test: `tests/api/equilibrium/core/test_native_results.py`

- [ ] **Step 1: Write failing tests for complete certification evidence**

Add tests that require `postsolve_certification` to report residual, constraint, physical-admissibility, phase-eligibility, and stability evidence without creating a new result object.

```python
def test_postsolve_certification_reports_all_evidence_families() -> None:
    diagnostics = native_results.with_postsolve_certification(
        {
            "accepted": True,
            "route_accepted": True,
            "postsolve_accepted": True,
            "residual_families": ["phase_equilibrium", "reaction_stationarity"],
            "constraint_families": ["conserved_balance", "phase_charge"],
            "phase_eligibility_mask_available": True,
            "density_recompute_relative_errors": [{"phase": "aq", "relative_error": 0.0}],
            "stability_certificate": {"accepted": True, "min_tpd": 0.0},
        }
    )

    summary = diagnostics["postsolve_certification"]
    assert summary["accepted"] is True
    assert summary["active_residuals_reported"] is True
    assert summary["hard_constraints_reported"] is True
    assert summary["physical_admissibility_reported"] is True
    assert summary["phase_eligibility_reported"] is True
    assert summary["stability_checked"] is True
```

- [ ] **Step 2: Run the failing test**

Run:

```powershell
uv run python run_pytest.py tests/api/equilibrium/core/test_native_results.py::test_postsolve_certification_reports_all_evidence_families -q
```

Expected: fails because `phase_eligibility_reported` is not present.

- [ ] **Step 3: Extend the existing summary helper**

Modify `_postsolve_certification_summary()` in `src/epcsaft/equilibrium_core/native_results.py`:

```python
phase_eligibility_reported = bool(
    diagnostics.get("phase_eligibility_mask_available", False)
    or diagnostics.get("phase_eligibility_mask")
)
```

Return:

```python
"phase_eligibility_reported": phase_eligibility_reported,
```

Do not add a new certification class.

- [ ] **Step 4: Run the certification tests**

Run:

```powershell
uv run python run_pytest.py tests/api/equilibrium/core/test_native_results.py -q
```

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add src/epcsaft/equilibrium_core/native_results.py tests/api/equilibrium/core/test_native_results.py
git commit -m "Strengthen shared equilibrium certification diagnostics"
```

## Task 2: Attach Certification Evidence To Existing Route Wrappers

**Files:**
- Modify: `src/epcsaft/equilibrium.py`
- Modify: `src/epcsaft/electrolyte_bubble.py`
- Test: `tests/api/equilibrium/core/test_vle.py`
- Test: `tests/api/equilibrium/core/test_lle.py`
- Test: `tests/api/equilibrium/electrolyte/test_electrolyte_bubble.py`
- Test: `tests/api/equilibrium/reactive/test_reactive_electrolyte_lle_coupled_solver.py`

- [ ] **Step 1: Write failing public-route diagnostics tests**

Add assertions to existing accepted-route tests that every accepted route exposes:

```python
cert = result.diagnostics["postsolve_certification"]
assert cert["route_accepted"] is True
assert cert["postsolve_accepted"] is True
assert cert["active_residuals_reported"] is True
assert cert["hard_constraints_reported"] is True
```

For routes that do not yet have a stability certificate, assert the honest status:

```python
assert cert["accepted"] is False
assert cert["status"] == "stability_not_checked"
```

For electrolyte LLE, assert the hard certificate:

```python
assert cert["accepted"] is True
assert cert["status"] == "accepted"
assert cert["stability_source"] == "tpdf_stability"
```

- [ ] **Step 2: Run the focused route tests**

Run:

```powershell
uv run python run_pytest.py tests/api/equilibrium/core/test_vle.py tests/api/equilibrium/core/test_lle.py tests/api/equilibrium/electrolyte/test_electrolyte_bubble.py tests/api/equilibrium/reactive/test_reactive_electrolyte_lle_coupled_solver.py -q
```

Expected: fails only where a wrapper has not preserved certification diagnostics.

- [ ] **Step 3: Reuse existing `native_route_diagnostics()` output**

In each route wrapper, make the result diagnostics come from `native_route_diagnostics(route)` or `with_postsolve_certification(diagnostics)` after route-specific diagnostics are added. Keep route-specific fields in the same dictionary.

Example pattern:

```python
diagnostics = native_route_diagnostics(route)
diagnostics.update(result.diagnostics)
diagnostics = with_postsolve_certification(diagnostics)
```

- [ ] **Step 4: Run focused route tests again**

Run the same command from Step 2.

Expected: pass.

- [ ] **Step 5: Commit**

```powershell
git add src/epcsaft/equilibrium.py src/epcsaft/electrolyte_bubble.py tests/api/equilibrium/core/test_vle.py tests/api/equilibrium/core/test_lle.py tests/api/equilibrium/electrolyte/test_electrolyte_bubble.py tests/api/equilibrium/reactive/test_reactive_electrolyte_lle_coupled_solver.py
git commit -m "Thread shared certification through equilibrium routes"
```

## Task 3: Add Reactive Stability Contract To Existing Stability Builders

**Files:**
- Modify: `src/epcsaft/native/equilibrium_nlp/stability_route_builders.h`
- Modify: `src/epcsaft/native/equilibrium_nlp/stability_route_builders.cpp`
- Modify: `src/epcsaft/native/equilibrium_nlp/route_metadata.h`
- Modify: `src/epcsaft/bindings.cpp`
- Test: `tests/native/equilibrium/test_route_metadata_contracts.py`
- Test: `tests/native/equilibrium/test_route_builders_stability.py`

- [ ] **Step 1: Write failing native contract tests**

Add a test that asks for a reactive stability contract through a new binding that lives beside existing stability bindings:

```python
def test_reactive_stability_tpd_contract_uses_existing_stability_shape() -> None:
    mix = _neutral_reactive_lle_mixture()
    contract = _core._native_reactive_stability_tpd_nlp_contract(
        mix._native,
        298.15,
        1.0e5,
        [0.5, 0.5],
        1,
        [1.0, 1.0],
        [1.0],
        1,
        [-1.0, 1.0],
        [0.0],
        "liq",
        "liq",
    )

    assert contract["problem_name"] == "reactive_stability_tpd"
    assert contract["derivative_backend"] in {"cppad_implicit", "cppad_explicit_density"}
    assert contract["balance_row_count"] == 1
    assert contract["reaction_count"] == 1
    assert contract["residual_families"] == ["reaction_stationarity", "stability_tpd"]
    assert contract["constraint_families"] == ["composition_sum", "pressure"]
```

- [ ] **Step 2: Run the failing contract test**

Run:

```powershell
uv run python run_pytest.py tests/native/equilibrium/test_route_builders_stability.py::test_reactive_stability_tpd_contract_uses_existing_stability_shape -q
```

Expected: fails because the binding does not exist.

- [ ] **Step 3: Extend existing C++ structs instead of adding a separate result family**

Add fields to `StabilityNlpContract` and `StabilityRouteResult`:

```cpp
int balance_row_count = 0;
int reaction_count = 0;
std::vector<std::string> residual_families;
std::vector<std::string> constraint_families;
std::vector<double> reaction_residuals;
std::vector<double> conserved_balance_residuals;
```

Keep these in `stability_route_builders.h`.

- [ ] **Step 4: Generalize `StabilityTpdProblem` with optional reactive data**

Add optional constructor inputs to `StabilityTpdProblem` for:

```cpp
int balance_rows;
std::vector<double> balance_matrix_row_major;
std::vector<double> total_vector;
int reaction_rows;
std::vector<double> reaction_stoichiometry_row_major;
std::vector<double> log_equilibrium_constants;
```

Use existing helpers from `reactive_phase_equilibrium_problem.cpp` where they already own residual semantics. If a helper is not externally visible, move the smallest reusable helper into an existing native header/source pair under `equilibrium_nlp`, then call it from both reactive phase equilibrium and reactive stability. Do not copy residual math.

- [ ] **Step 5: Add route metadata**

In `route_metadata.h`, add a stability metadata helper with existing `RouteMetadata`:

```cpp
inline RouteMetadata reactive_stability_tpd_route_metadata(bool has_charge_constraints) {
    RouteMetadata out = stability_tpd_route_metadata(has_charge_constraints);
    out.residual_families = {"reaction_stationarity", "stability_tpd"};
    out.constraint_families = has_charge_constraints
        ? std::vector<std::string>{"composition_sum", "phase_charge", "pressure"}
        : std::vector<std::string>{"composition_sum", "pressure"};
    return out;
}
```

If `stability_tpd_route_metadata` does not exist yet, add it for neutral/electrolyte stability first and then reuse it here.

- [ ] **Step 6: Add pybind contract binding**

In `bindings.cpp`, add `_native_reactive_stability_tpd_nlp_contract` beside `_native_neutral_stability_tpd_nlp_contract` and `_native_electrolyte_stability_tpd_nlp_contract`.

The dict output must reuse `stability_nlp_contract_to_dict()` after adding the new fields to that serializer.

- [ ] **Step 7: Run native contract tests**

Run:

```powershell
uv run python run_pytest.py tests/native/equilibrium/test_route_builders_stability.py::test_reactive_stability_tpd_contract_uses_existing_stability_shape tests/native/equilibrium/test_route_metadata_contracts.py -q
```

Expected: pass.

- [ ] **Step 8: Commit**

```powershell
git add src/epcsaft/native/equilibrium_nlp/stability_route_builders.h src/epcsaft/native/equilibrium_nlp/stability_route_builders.cpp src/epcsaft/native/equilibrium_nlp/route_metadata.h src/epcsaft/bindings.cpp tests/native/equilibrium/test_route_builders_stability.py tests/native/equilibrium/test_route_metadata_contracts.py
git commit -m "Add reactive stability native contract"
```

## Task 4: Implement Native Reactive Stability Route Result

**Files:**
- Modify: `src/epcsaft/native/equilibrium_nlp/stability_route_builders.h`
- Modify: `src/epcsaft/native/equilibrium_nlp/stability_route_builders.cpp`
- Modify: `src/epcsaft/bindings.cpp`
- Test: `tests/native/equilibrium/test_route_builders_stability.py`

- [ ] **Step 1: Write failing route-result test**

```python
def test_reactive_stability_tpd_route_result_uses_ipopt_and_exact_hessian() -> None:
    mix = _neutral_reactive_lle_mixture()
    payload = _core._native_reactive_stability_tpd_route_result(
        mix._native,
        298.15,
        1.0e5,
        [0.5, 0.5],
        1,
        [1.0, 1.0],
        [1.0],
        1,
        [-1.0, 1.0],
        [0.0],
        "liq",
        "liq",
        50,
        1.0e-8,
        0.0,
        "exact",
        10,
        1.0e-8,
        None,
        stability_tolerance=1.0e-8,
    )

    if not payload["compiled"]:
        assert payload["status"] == "ipopt_dependency_required"
        return

    assert payload["ran"] is True
    assert payload["problem_name"] == "reactive_stability_tpd"
    assert payload["hessian_approximation"] == "exact"
    assert payload["exact_hessian_available"] is True
    assert "reaction_stationarity" in payload["residual_families"]
```

- [ ] **Step 2: Run the failing route-result test**

Run:

```powershell
uv run python run_pytest.py tests/native/equilibrium/test_route_builders_stability.py::test_reactive_stability_tpd_route_result_uses_ipopt_and_exact_hessian -q
```

Expected: fails because the binding does not exist.

- [ ] **Step 3: Implement `solve_reactive_stability_tpd_route` using existing Ipopt adapter**

Add this function to `stability_route_builders.h/.cpp`:

```cpp
StabilityRouteResult solve_reactive_stability_tpd_route(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition,
    int balance_rows,
    const std::vector<double>& balance_matrix_row_major,
    const std::vector<double>& total_vector,
    int reaction_rows,
    const std::vector<double>& reaction_stoichiometry_row_major,
    const std::vector<double>& log_equilibrium_constants,
    int parent_phase,
    int trial_phase,
    const IpoptSolveOptions& options,
    double stability_tolerance,
    const std::vector<double>& trial_initial_composition = {}
);
```

The implementation must call the same `solve_ipopt_nlp(problem, options)` path as neutral/electrolyte stability.

- [ ] **Step 4: Preserve seed attempt behavior**

Reuse `stability_seed_candidates()` and `RouteSeedAttempt` for reactive stability. Add reaction residual norms to the selected `StabilityRouteResult`, not to a separate side channel.

- [ ] **Step 5: Add pybind route-result binding**

In `bindings.cpp`, add `_native_reactive_stability_tpd_route_result` next to the existing stability route bindings and serialize through `stability_route_result_to_dict()`.

- [ ] **Step 6: Run native route-result tests**

Run:

```powershell
uv run python run_pytest.py tests/native/equilibrium/test_route_builders_stability.py::test_reactive_stability_tpd_route_result_uses_ipopt_and_exact_hessian tests/native/equilibrium/test_route_builders_stability.py::test_neutral_stability_tpd_route_uses_exact_hessian_when_requested tests/native/equilibrium/test_route_builders_stability.py::test_electrolyte_stability_tpd_route_uses_exact_hessian_when_requested -q
```

Expected: pass.

- [ ] **Step 7: Commit**

```powershell
git add src/epcsaft/native/equilibrium_nlp/stability_route_builders.h src/epcsaft/native/equilibrium_nlp/stability_route_builders.cpp src/epcsaft/bindings.cpp tests/native/equilibrium/test_route_builders_stability.py
git commit -m "Implement native reactive stability route"
```

## Task 5: Wire Public `reactive_stability` Through Existing Facade

**Files:**
- Modify: `src/epcsaft/epcsaft.py`
- Modify: `src/epcsaft/equilibrium.py`
- Modify: `src/epcsaft/capability_evidence.py`
- Test: `tests/native/equilibrium/test_chemical_equilibrium_native_api.py`
- Test: `tests/api/runtime/test_runtime_capabilities_dependency_gates.py`

- [ ] **Step 1: Convert current gate tests to public route tests**

Update `test_reactive_stability_requires_native_ipopt_stability_route_before_speciation` so it no longer expects the native route boundary gate when Ipopt is compiled:

```python
if not _core._native_ipopt_smoke()["compiled"]:
    with pytest.raises(epcsaft.InputError, match="reactive_stability requires a native Ipopt"):
        mix.equilibrium(...)
    return

result = mix.equilibrium(...)
assert result.problem_kind == "reactive_stability"
assert result.diagnostics["solver_backend"] == "ipopt"
assert result.diagnostics["postsolve_certification"]["stability_checked"] is True
```

- [ ] **Step 2: Run the failing public route test**

Run:

```powershell
uv run python run_pytest.py tests/native/equilibrium/test_chemical_equilibrium_native_api.py::test_reactive_stability_requires_native_ipopt_stability_route_before_speciation -q
```

Expected: fails at the old gate.

- [ ] **Step 3: Add Python helper that calls the native route**

In `src/epcsaft/equilibrium.py`, add a private helper that mirrors existing stability helpers:

```python
def _native_reactive_stability(
    mixture: Any,
    *,
    T: float,
    P: float,
    feed: np.ndarray,
    balance_matrix: np.ndarray,
    total_vector: np.ndarray,
    reactions: Sequence[Any],
    parent_phase: str,
    trial_phase: str,
    options: ReactiveSpeciationOptions,
) -> StabilityResult:
    ...
```

The helper must normalize diagnostics through `native_route_diagnostics(route)` and attach `stability_certificate`.

- [ ] **Step 4: Replace the public gate in `epcsaft.py`**

In the `kind_token in {"reactive_stability", "chemical_stability"}` branch, keep the existing input validation and replace `_raise_native_ipopt_stability_required("reactive_stability")` with a call to the helper from Step 3.

Do not call `chemical_equilibrium()` first.

- [ ] **Step 5: Add capability evidence only for the route existence**

Add an `IPOPT_EQUILIBRIUM_ROUTE_EVIDENCE` row for `reactive_stability` only after the native route test passes. Keep reactive LLE production status unchanged.

- [ ] **Step 6: Run focused public and capability tests**

Run:

```powershell
uv run python run_pytest.py tests/native/equilibrium/test_chemical_equilibrium_native_api.py tests/api/runtime/test_runtime_capabilities_dependency_gates.py -q
```

Expected: pass.

- [ ] **Step 7: Commit**

```powershell
git add src/epcsaft/epcsaft.py src/epcsaft/equilibrium.py src/epcsaft/capability_evidence.py tests/native/equilibrium/test_chemical_equilibrium_native_api.py tests/api/runtime/test_runtime_capabilities_dependency_gates.py
git commit -m "Expose native reactive stability route"
```

## Task 6: Make Reactive LLE Certification Use The Shared Stability Layer

**Files:**
- Modify: `src/epcsaft/equilibrium.py`
- Modify: `src/epcsaft/native/equilibrium_nlp/route_builders.h`
- Modify: `src/epcsaft/native/equilibrium_nlp/route_builders.cpp`
- Modify: `src/epcsaft/bindings.cpp`
- Test: `tests/api/equilibrium/reactive/test_reactive_electrolyte_lle_coupled_solver.py`
- Test: `tests/api/reactive/test_reactive_phase_equilibrium_problem_routes_native.py`

- [ ] **Step 1: Write failing certification tests for accepted reactive routes**

In the accepted native-route monkeypatch tests, assert:

```python
cert = result.diagnostics["postsolve_certification"]
assert cert["active_residuals_reported"] is True
assert cert["hard_constraints_reported"] is True
assert cert["phase_eligibility_reported"] is True
assert cert["stability_checked"] is True
```

Use monkeypatched `stability_certificate={"accepted": True, "min_tpd": 0.0}` payloads first.

- [ ] **Step 2: Run the failing tests**

Run:

```powershell
uv run python run_pytest.py tests/api/equilibrium/reactive/test_reactive_electrolyte_lle_coupled_solver.py tests/api/reactive/test_reactive_phase_equilibrium_problem_routes_native.py -q
```

Expected: fails because reactive route diagnostics do not carry stability certificate evidence.

- [ ] **Step 3: Reuse existing stability route builders for certificate generation**

After a reactive LLE route returns accepted phase amounts, call the appropriate stability route for each accepted final phase:

- neutral reactive LLE: `solve_neutral_stability_tpd_route`
- reactive electrolyte LLE: `solve_electrolyte_stability_tpd_route`
- phase-model reactive electrolyte LLE: use the phase model native mixture for each phase where available

Attach the aggregate as:

```python
diagnostics["stability_certificate"] = {
    "accepted": all(item["accepted"] for item in phase_certificates),
    "phase_certificates": phase_certificates,
    "minimum_min_tpd": min(item["min_tpd"] for item in phase_certificates),
}
diagnostics = with_postsolve_certification(diagnostics)
```

- [ ] **Step 4: Keep route acceptance honest**

If any phase certificate fails, raise:

```python
raise SolutionError("Native reactive phase route failed stability certification.", diagnostics)
```

- [ ] **Step 5: Run focused reactive route tests**

Run:

```powershell
uv run python run_pytest.py tests/api/equilibrium/reactive/test_reactive_electrolyte_lle_coupled_solver.py tests/api/reactive/test_reactive_phase_equilibrium_problem_routes_native.py -q
```

Expected: pass.

- [ ] **Step 6: Commit**

```powershell
git add src/epcsaft/equilibrium.py src/epcsaft/native/equilibrium_nlp/route_builders.h src/epcsaft/native/equilibrium_nlp/route_builders.cpp src/epcsaft/bindings.cpp tests/api/equilibrium/reactive/test_reactive_electrolyte_lle_coupled_solver.py tests/api/reactive/test_reactive_phase_equilibrium_problem_routes_native.py
git commit -m "Certify reactive phase route stability"
```

## Task 7: Keep Paper Validation Outside Pytest

**Files:**
- Modify: `src/epcsaft/capability_evidence.py`
- Modify: `run_pytest.py`
- Modify: `docs/pages/development_workflows.rst`
- Modify: `scripts/benchmarks/helpers/literature.py`
- Modify: `scripts/validation/equilibrium_core/confidence.py`
- Modify: analysis scripts under `analyses/paper_validation/native/2023_ascani/`
- Modify: analysis scripts under the Rezaee 2026 paper-validation directory discovered by `rg -n "Rezaee|reactive_electrolyte_lle" analyses tests scripts`

- [ ] **Step 1: Remove paper-validation pytest gates**

Remove pytest modules whose job is to validate a paper, reproduce a literature figure/table, or converge many feed lines. Pytest should keep generic package contracts only:

```powershell
rg -n "paper_validation|tests/regression/literature|tests/workflows/validation|tests/workflows/data_validation" tests src scripts docs
```

- [ ] **Step 2: Route equilibrium confidence to the trusted exact-Hessian ladder**

`--equilibrium-confidence` should run the known hydrocarbon bubble native Ipopt exact-Hessian solve and route diagnostics contracts, not Khudaida feed-line or paper-matrix tests:

```powershell
uv run python run_pytest.py --equilibrium-confidence -q
```

Expected: pass without invoking paper-validation tests.

- [ ] **Step 3: Keep benchmark inventory executable through scripts only**

Literature/paper benchmark rows may point to explicit analysis or benchmark scripts, but not to pytest files. A benchmark command should be visibly opt-in:

```powershell
uv run python scripts/benchmarks/benchmark_literature_suite.py --registry-only
uv run python analyses/paper_validation/<family>/scripts/run_all.py
```

Do not make `run_pytest.py`, `validate_project.py quick`, or named pytest slices run these paper scripts.

- [ ] **Step 4: Add input-audit payloads in existing analysis scripts**

For paper workflows, put input-contract evidence in the script payload itself:

```python
"input_audit": {
    "species_order": list(mix.species),
    "balance_rows_verified": True,
    "reaction_standard_states_verified": True,
    "phase_labels": phase_labels_from_result,
    "parameter_dataset": dataset_name,
    "public_api": 'mix.equilibrium(kind="reactive_electrolyte_lle")',
}
```

The script must derive these values from actual mixture/result objects, not duplicated constants.

- [ ] **Step 5: Run contract tests plus explicit benchmark inventory**

Run:

```powershell
uv run python run_pytest.py --equilibrium-confidence -q
uv run python run_pytest.py tests/workflows/repo/test_run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python scripts/benchmarks/benchmark_literature_suite.py --registry-only
```

Expected: pytest proves package wiring only; the benchmark command renders registry state without requiring paper convergence.

- [ ] **Step 6: Commit**

```powershell
git add src/epcsaft/capability_evidence.py run_pytest.py docs/pages/development_workflows.rst scripts/benchmarks/helpers/literature.py tests
git commit -m "Keep paper validation out of pytest"
```

## Task 8: Promote Reactive LLE Capabilities Only After Benchmark Proof

**Files:**
- Modify: `src/epcsaft/capability_evidence.py`
- Modify: `src/epcsaft/runtime.py`
- Test: `tests/api/runtime/test_runtime_capabilities_dependency_gates.py`
- Test: `tests/workflows/repo/test_run_pytest.py`

- [ ] **Step 1: Write failing capability promotion test**

Only add this expected production status after Task 7 has accepted proof:

```python
def test_reactive_phase_routes_are_capability_registered_after_benchmark_proof() -> None:
    capabilities = epcsaft.capabilities()
    assert capabilities["equilibrium"]["reactive_lle"]["production"] is True
    assert capabilities["equilibrium"]["reactive_electrolyte_lle"]["production"] is True
    route_evidence = capabilities["derivatives"]["equilibrium_route_evidence"]
    by_quantity = {row["quantity"]: row for row in route_evidence["rows"]}
    assert by_quantity["reactive_lle_and_reactive_electrolyte_lle"]["classification"] == "production_supported"
```

- [ ] **Step 2: Run the failing capability test**

Run:

```powershell
uv run python run_pytest.py tests/api/runtime/test_runtime_capabilities_dependency_gates.py::test_reactive_phase_routes_are_capability_registered_after_benchmark_proof -q
```

Expected: fails until the capability registry is updated.

- [ ] **Step 3: Update capability evidence**

Change the existing reactive route row in `EQUILIBRIUM_ROUTE_DERIVATIVE_EVIDENCE` from:

```python
"classification": "route_builder_supported_capability_pending",
```

to:

```python
"classification": "production_supported",
```

Add tests from Task 7 to the row's `tests` tuple.

- [ ] **Step 4: Register public equilibrium capability keys**

Add `reactive_lle` and `reactive_electrolyte_lle` entries only when Task 7 proof is accepted. They must include:

```python
"backend": "native_ipopt_equilibrium_nlp",
"production": True,
"requires": ["ipopt", "cppad"],
"proof": "literature_benchmark_and_postsolve_certification",
```

- [ ] **Step 5: Run capability and workflow registry tests**

Run:

```powershell
uv run python run_pytest.py tests/api/runtime/test_runtime_capabilities_dependency_gates.py tests/workflows/repo/test_run_pytest.py -q
```

Expected: pass.

- [ ] **Step 6: Commit**

```powershell
git add src/epcsaft/capability_evidence.py src/epcsaft/runtime.py tests/api/runtime/test_runtime_capabilities_dependency_gates.py tests/workflows/repo/test_run_pytest.py
git commit -m "Promote certified reactive phase capabilities"
```

## Task 9: Full Validation And Roadmap Closure

**Files:**
- Modify: `docs/roadmaps/unified_equilibrium_core_algorithm.md`
- Modify: `docs/roadmaps/FULL_ROADMAP.md` only if public completion language changes
- Modify: `docs/goals/unified-equilibrium-roadmap-implementation/state.yaml`

- [ ] **Step 1: Run focused native build if C++ changed**

Run:

```powershell
uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10
```

Expected: build succeeds and `_core` imports.

- [ ] **Step 2: Run native contracts**

Run:

```powershell
uv run python run_pytest.py --native-contracts -q
```

Expected: pass.

- [ ] **Step 3: Run equilibrium confidence lane**

Run:

```powershell
uv run python scripts/dev/validate_project.py confidence
```

Expected: pass. If it fails for a benchmark accuracy reason, do not update capability promotion.

- [ ] **Step 4: Run package boundary check**

Run:

```powershell
uv run python scripts/dev/build_dist.py
```

Expected: package boundary check succeeds.

- [ ] **Step 5: Run text gates**

Run:

```powershell
uv run python scripts/dev/check_text_gates.py
```

Expected: pass.

- [ ] **Step 6: Run cleanup hook**

Run:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Expected: no matching leftover Codex processes for this repo.

- [ ] **Step 7: Update roadmap language**

In `docs/roadmaps/unified_equilibrium_core_algorithm.md`, update only statements that have executable evidence. Preserve future-looking language for anything still not implemented.

- [ ] **Step 8: Commit**

```powershell
git add docs/roadmaps/unified_equilibrium_core_algorithm.md docs/roadmaps/FULL_ROADMAP.md docs/goals/unified-equilibrium-roadmap-implementation/state.yaml
git commit -m "Close unified equilibrium roadmap implementation"
```

## Self-Review

- Spec coverage: The plan covers shared certification, reactive stability, reactive LLE/electrolyte LLE benchmark proof, and capability evidence.
- Placeholder scan: The plan avoids open-ended placeholders and names concrete files, tests, commands, and expected outcomes.
- Type consistency: The plan reuses `StabilityNlpContract`, `StabilityRouteResult`, `ReactiveTwoPhaseEosRouteResult`, `RouteMetadata`, `native_route_diagnostics()`, and `capabilities()` rather than adding a parallel architecture.

## Execution Handoff

Plan complete. The matching GoalBuddy board is:

```text
docs/goals/unified-equilibrium-roadmap-implementation/state.yaml
```

Start execution with:

```text
/goal Follow docs/goals/unified-equilibrium-roadmap-implementation/goal.md.
```
