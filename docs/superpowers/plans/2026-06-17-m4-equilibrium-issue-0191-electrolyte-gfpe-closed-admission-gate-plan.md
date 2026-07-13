# Electrolyte GFPE Closed-Admission Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the first #191 child that turns the Khudaida electrolyte LLE fixture into an executable source-data and native-diagnostic gate while keeping electrolyte public route admission closed.

**Architecture:** This is a gate-first #191 slice, not public electrolyte route admission. The work validates the source fixture, repairs the analysis-owned Khudaida parameter-bundle execution path, adds a checker that proves source-data parsing, explicit-ion expansion, native electrolyte/charge diagnostics, and closed public route state, then records the result in the M4 registry and tracker. Full electrolyte GFPE admission remains behind exact Born/SSM/DS Hessian, electrolyte TPD, HELD2 algorithm discovery, and postsolve certification gates.

**Tech Stack:** `epcsaft-equilibrium`, native C++ electrolyte/charge blocks exposed through `_native`, paper-validation parameter bundles, `scripts/validation` checker patterns, pytest through `run_pytest.py`, M4 benchmark registry, GitHub issue mirrors.

---

## Intake

- Parent issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
- Parent issue mirror: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Rejected parent plan for direct execution: `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md`
- Parent plan validator receipt: fails Task # Use Cases gate with 3 missing use-case blocks.
- GFPE doctrine: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- M4 algorithm/admission registry: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml`
- M6 evidence registry: `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`
- Source fixture: `data/reference/equilibrium_benchmarks/electrolyte_lle/water_ethanol_isobutanol_nacl`
- Analysis parameter bundle: `analyses/paper_validation/2026_khudaida/parameters`
- User scope decision: `Gate First` for #191 child planning.

## Verified Planning Facts

- Verified: `electrolyte_lle` is present in the native activation matrix with `production_exposed: false`, no public routes, and no proof routes.
- Verified: the Khudaida fixture has `feed_compositions.csv`, `experimental_tielines.csv`, `metadata.json`, `thresholds.json`, and source notes.
- Verified: `metadata.json` names species `["H2O", "Ethanol", "Butanol", "Na+", "Cl-"]`, formula species `["H2O", "Ethanol", "Isobutanol", "NaCl"]`, and pressure `100000.0 Pa`.
- Verified: string dataset lookup with `ePCSAFTMixture.from_dataset("2026_Khudaida", ...)` is closed; available packaged datasets are empty in the current source checkout.
- Verified: path-based `ePCSAFTMixture.from_dataset(paper_validation_parameter_path("2026_Khudaida"), ...)` reaches the analysis bundle but currently raises on stale generated keys `mixed_ion_dispersion`, `mixed_ion_dispersion_applied`, and `mixed_ion_dispersion_sources`.
- Inference: the first safe #191 child should make the source-backed electrolyte fixture executable and add a closed-admission checker before any public electrolyte route key is introduced.
- Unknown: route-level electrolyte LLE numerical performance, because no electrolyte GFPE route admission exists yet.

## Planning Decisions

- This child creates a new issue under #191, tentatively titled `M4: add electrolyte GFPE closed-admission source gate`.
- This child may touch `analyses/paper_validation/2026_khudaida/parameters/**` and `scripts/data/**` only to make the already referenced Khudaida paper-validation bundle executable by existing source-checkout validation.
- This child must not register `2026_Khudaida` as a packaged public provider dataset. Public provider dataset registration is separate M3/M6 work.
- This child must not add a public `electrolyte_lle` route, proof route, or production family.
- The checker will report `complete: true` only for source-data readiness, parameter-bundle execution, native electrolyte/charge diagnostics, and closed public route state. It will separately report that full electrolyte GFPE admission remains pending.
- The HELD acronym here refers to the algorithm, not the Held author family.

## Test-Complete Definition And Metrics

This plan is complete only when all of the following pass from the repo root:

- `uv run --no-sync python scripts/validation/check_electrolyte_gfpe_gate.py --json --require-source-data --require-parameter-bundle --require-native-diagnostics --require-public-routes-closed --require-complete`
- `uv run --no-sync python scripts/run_pytest.py tests/native/contracts/test_electrolyte_gfpe_gate_checker.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py`
- `uv run --no-sync python scripts/data/curate_paper_validation_parameters.py`
- `uv run --no-sync python scripts/dev/validate_project.py quick`

Numerical and structural pass metrics:

- Every parsed Khudaida feed row and tie-line phase row has finite nonnegative composition entries and row sum within `1.0e-10` on the formula basis.
- Formula-basis NaCl rows expand to explicit ions as `[x_water, x_ethanol, x_isobutanol, x_nacl, x_nacl] / (1 + x_nacl)`.
- Expanded explicit-ion rows have absolute charge balance <= `1.0e-8`.
- Khudaida parameter bundle path construction succeeds through `paper_validation_parameter_path("2026_Khudaida")`.
- Native electrolyte contribution diagnostics are active for the first expanded feed row, return finite ion, Born, electrolyte, and total residual Helmholtz terms, and report phase-charge residual <= `1.0e-8`.
- Native phase-system diagnostics append one charge-balance row per phase and expose analytic charge-balance Jacobian rows.
- `epcsaft_equilibrium.capabilities()` and native activation metadata keep `electrolyte_lle` out of `public_routes`, `production_families`, and route derivative evidence.
- Registry evidence for `PE-Electrolyte LLE/TP Flash` records this checker as a closed-admission prerequisite only; it does not set production exposure.

## Acceptance Criteria

- [ ] A new #191 child issue and local mirror define the closed-admission source gate.
- [ ] Khudaida source fixture parsing, explicit-ion expansion, and charge-balance checks are executable through a retained checker.
- [ ] The Khudaida paper-validation parameter bundle can construct a native mixture through the existing path-based analysis bundle route.
- [ ] Native electrolyte contribution and phase-charge diagnostics are exercised on source-backed Khudaida inputs.
- [ ] Capability and activation tests prove electrolyte public route admission remains closed.
- [ ] M4 registry and README record the new gate without claiming full electrolyte GFPE, HELD2, or public electrolyte LLE support.

## Non-Goals

- No public `electrolyte_lle`, electrolyte TP flash, reactive, or associating route admission.
- No packaged public provider dataset registration for `2026_Khudaida`.
- No route-level electrolyte NLP, electrolyte TPD, HELD2 candidate generation, or postsolve electrolyte phase-set certification.
- No changes to neutral, associating, reactive, regression, or release capability claims.
- No synthetic fixture can satisfy the source-backed Khudaida gate.

## File Map

- Create: `docs/superpowers/issues/<date>-m4-equilibrium-issue-<number>-add-electrolyte-gfpe-closed-admission-source-gate.md`
- Create: `scripts/validation/check_electrolyte_gfpe_gate.py`
- Create: `tests/native/contracts/test_electrolyte_gfpe_gate_checker.py`
- Modify: `analyses/paper_validation/2026_khudaida/parameters/user_options.json`
- Modify: `scripts/data/curate_paper_validation_parameters.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml` and `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`

## Tasks

### Task 1: Create The #191 Child Tracker Slice

**Use Cases:**
- A roadmap owner needs #191 broken into a ready PR-sized child because the parent plan fails the task-use-case validator.
- A worker needs a child issue that starts electrolyte work without claiming public electrolyte route admission.
- A reviewer needs GitHub and local mirrors to say exactly which #191 evidence remains pending after this child.

**Files:**
- Create: `docs/superpowers/issues/<date>-m4-equilibrium-issue-<number>-add-electrolyte-gfpe-closed-admission-source-gate.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Confirm parent state**

  Run:

  ```powershell
  gh issue view 191 --repo ePC-SAFT/ePC-SAFT --json number,title,state,labels,milestone,url,projectItems
  git status --short --branch
  ```

  Expected: #191 is open, labeled `status:ready`, assigned to `M4 - Equilibrium`, and local `main` is clean before creating child tracker files.

- [ ] **Step 2: Create the GitHub child issue**

  Use this issue title:

  ```text
  M4: add electrolyte GFPE closed-admission source gate
  ```

  Use this body:

  ```markdown
  ## Parent

  Parent: #191

  ## Goal

  Prove the first executable electrolyte GFPE gate by validating the Khudaida source fixture, explicit-ion expansion, source parameter-bundle execution, native electrolyte/charge diagnostics, and closed public route state.

  ## Acceptance criteria

  - Khudaida source fixture rows parse, normalize, and expand formula-basis NaCl to explicit Na+ and Cl- rows with charge balance <= 1.0e-8.
  - `paper_validation_parameter_path("2026_Khudaida")` can construct a native mixture for at least one expanded Khudaida feed row.
  - Native electrolyte contribution and phase-charge diagnostics run on source-backed Khudaida inputs and return finite active electrolyte terms.
  - `electrolyte_lle` remains absent from public routes, production families, proof routes, and route derivative evidence.
  - M4 registry and README record this as a closed-admission prerequisite, not public electrolyte GFPE admission.

  ## Non-goals

  - No public electrolyte route admission.
  - No packaged provider dataset registration.
  - No electrolyte TPD, HELD2 candidate generation, or route postsolve certification.

  ## Proof oracle

  - `uv run --no-sync python scripts/validation/check_electrolyte_gfpe_gate.py --json --require-source-data --require-parameter-bundle --require-native-diagnostics --require-public-routes-closed --require-complete`
  - `uv run --no-sync python scripts/run_pytest.py tests/native/contracts/test_electrolyte_gfpe_gate_checker.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py`
  - `uv run --no-sync python scripts/data/curate_paper_validation_parameters.py`
  - `uv run --no-sync python scripts/dev/validate_project.py quick`
  ```

  Apply labels:

  ```text
  enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
  ```

- [ ] **Step 3: Create the local mirror**

  Create the mirror under `docs/superpowers/issues/` using the issue number returned by GitHub. Set:

  ```yaml
  milestone: "M4 - Equilibrium"
  package: "equilibrium"
  capability: "electrolyte"
  backend: "Ipopt"
  readiness: "ready"
  source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
  source_plan: "docs/superpowers/plans/2026-06-17-m4-equilibrium-issue-0191-electrolyte-gfpe-closed-admission-gate-plan.md"
  afk_hitl: "HITL"
  ```

- [ ] **Step 4: Link the child in #191 and M4 README**

  Add a #191 queue note saying this child proves source fixture and closed-admission readiness only. Add the child to the M4 README open issue table after #191 or in the queue guard after the child is created.

- [ ] **Step 5: Commit tracker setup**

  Run:

  ```powershell
  git add docs/superpowers/issues docs/superpowers/milestones/M4-equilibrium/README.md docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
  git commit -m "Create electrolyte GFPE gate issue"
  ```

### Task 2: Add The Red Checker Contract

**Use Cases:**
- A worker needs the checker output schema before writing validation code.
- A CI or local proof run needs `--require-complete` to fail loudly when source data, native diagnostics, or closed-route checks are missing.
- A reviewer needs the checker to distinguish this gate from full electrolyte GFPE admission.

**Files:**
- Create: `tests/native/contracts/test_electrolyte_gfpe_gate_checker.py`
- Create: `scripts/validation/check_electrolyte_gfpe_gate.py`

- [ ] **Step 1: Add schema tests**

  Create `tests/native/contracts/test_electrolyte_gfpe_gate_checker.py` with tests that import `evaluate_payload` from the new checker and assert this complete payload passes:

  ```python
  payload = {
      "source_data": {
          "fixture": "khudaida_2026",
          "feed_row_count": 1,
          "tie_line_phase_row_count": 2,
          "formula_rows_normalized": True,
          "explicit_ion_rows_charge_balanced": True,
          "max_abs_charge_balance": 0.0,
      },
      "parameter_bundle": {
          "dataset": "2026_Khudaida",
          "path_resolves": True,
          "native_mixture_constructed": True,
      },
      "native_diagnostics": {
          "electrolyte_contribution_active": True,
          "finite_electrolyte_terms": True,
          "phase_charge_rows_present": True,
          "phase_charge_jacobian_present": True,
          "phase_charge_residual_norm": 0.0,
      },
      "public_route_state": {
          "electrolyte_lle_public_routes": [],
          "electrolyte_lle_proof_routes": [],
          "electrolyte_lle_production_exposed": False,
          "electrolyte_in_public_routes": False,
          "electrolyte_in_derivative_evidence": False,
      },
      "held2_status": {
          "full_held2_claimed": False,
          "pending_gates": ["electrolyte_tpd", "held2_stage_discovery", "charge_and_electrochemical_certification"],
      },
  }
  assert evaluate_payload(payload)["complete"] is True
  assert evaluate_payload(payload)["blockers"] == []
  ```

- [ ] **Step 2: Add blocker tests**

  Add parametrized tests that mutate one field at a time and expect these blockers:

  ```text
  missing_source_data
  source_rows_not_charge_balanced
  parameter_bundle_not_executable
  missing_native_electrolyte_diagnostics
  electrolyte_public_route_open
  full_held2_claimed_by_gate
  ```

- [ ] **Step 3: Add CLI red test**

  Add a subprocess test:

  ```powershell
  uv run --no-sync python scripts/validation/check_electrolyte_gfpe_gate.py --json --require-complete
  ```

  Expected before implementation: nonzero exit with JSON containing at least one blocker instead of an import error or missing-file error.

### Task 3: Implement Source Fixture And Parameter-Bundle Gate

**Use Cases:**
- A validation run needs to prove Khudaida CSV rows are source-backed, normalized, and charge-balanced after explicit-ion expansion.
- A numerical worker needs one callable source-backed electrolyte mixture before writing route-level electrolyte residuals.
- A maintainer needs paper-validation bundle validation to catch runtime-option drift that the current curation script misses.

**Files:**
- Create: `scripts/validation/check_electrolyte_gfpe_gate.py`
- Modify: `analyses/paper_validation/2026_khudaida/parameters/user_options.json`
- Modify: `scripts/data/curate_paper_validation_parameters.py`

- [ ] **Step 1: Implement explicit-ion expansion**

  In the checker, implement:

  ```python
  def expand_nacl_formula_row(row: Mapping[str, str], *, prefix: str = "x_") -> list[float]:
      water = float(row[f"{prefix}water_total"] if f"{prefix}water_total" in row else row["x_water"])
      ethanol = float(row[f"{prefix}ethanol_total"] if f"{prefix}ethanol_total" in row else row["x_ethanol"])
      butanol = float(row[f"{prefix}isobutanol_total"] if f"{prefix}isobutanol_total" in row else row["x_isobutanol"])
      nacl = float(row[f"{prefix}nacl_total"] if f"{prefix}nacl_total" in row else row["x_nacl"])
      denominator = 1.0 + nacl
      return [water / denominator, ethanol / denominator, butanol / denominator, nacl / denominator, nacl / denominator]
  ```

  The implementation may split feed and tie-line helpers if the final code is clearer, but it must keep the same formula.

- [ ] **Step 2: Validate source files**

  Read `metadata.json`, `thresholds.json`, `feed_compositions.csv`, and `experimental_tielines.csv`. Require species, pressure, thresholds, feed rows, organic rows, and aqueous rows. Compute formula-basis row sums and explicit-ion charge balances with charges `[0.0, 0.0, 0.0, 1.0, -1.0]`.

- [ ] **Step 3: Repair Khudaida user options**

  Replace stale runtime-option leakage in `analyses/paper_validation/2026_khudaida/parameters/user_options.json` with the current public model-options shape only. Keep the existing Born model intent:

  ```json
  {
    "elec_model": {
      "differential_mode": "autodiff",
      "relative_permittivity_rule": "empirical",
      "born_model": {
        "enabled": true,
        "born_diameter_rule": "fitted",
        "solvation_shell_model": true,
        "dielectric_saturation": true
      }
    }
  }
  ```

  After the edit, this command must construct a mixture rather than raising on `mixed_ion_dispersion*` keys:

  ```powershell
  uv run --no-sync python -c "import csv; from scripts.data.paper_validation_parameters import paper_validation_parameter_path; from epcsaft.state.native_adapter import ePCSAFTMixture; row=next(csv.DictReader(open('data/reference/equilibrium_benchmarks/electrolyte_lle/water_ethanol_isobutanol_nacl/feed_compositions.csv', newline=''))); xs=float(row['x_nacl_total']); x=[float(row['x_water_total'])/(1+xs), float(row['x_ethanol_total'])/(1+xs), float(row['x_isobutanol_total'])/(1+xs), xs/(1+xs), xs/(1+xs)]; mix=ePCSAFTMixture.from_dataset(paper_validation_parameter_path('2026_Khudaida'), species=['H2O','Ethanol','Butanol','Na+','Cl-'], x=x, T=float(row['temperature_K'])); print(mix.species)"
  ```

- [ ] **Step 4: Extend parameter-bundle curation**

  Update `scripts/data/curate_paper_validation_parameters.py` so it validates that each bundle's canonical user options can pass the same runtime option normalization used by `ParameterSource`/`ePCSAFTMixture.from_dataset`.

- [ ] **Step 5: Commit source gate repair**

  Run:

  ```powershell
  git add scripts/validation/check_electrolyte_gfpe_gate.py analyses/paper_validation/2026_khudaida/parameters/user_options.json scripts/data/curate_paper_validation_parameters.py
  git commit -m "Add executable Khudaida electrolyte source gate"
  ```

### Task 4: Add Native Electrolyte Diagnostics To The Gate

**Use Cases:**
- A #191 worker needs proof that source-backed electrolyte inputs reach native electrolyte terms before route admission work starts.
- A route reviewer needs charge-balance rows and Jacobian evidence to exist independently of optimizer success.
- A future HELD2 worker needs a diagnostic payload that separates electrolyte term activity from phase-discovery claims.

**Files:**
- Modify: `scripts/validation/check_electrolyte_gfpe_gate.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py`

- [ ] **Step 1: Add source-backed native smoke**

  In the checker, construct the first Khudaida feed row with:

  ```python
  from scripts.data.paper_validation_parameters import paper_validation_parameter_path
  from epcsaft.state.native_adapter import ePCSAFTMixture

  mixture = ePCSAFTMixture.from_dataset(
      paper_validation_parameter_path("2026_Khudaida"),
      species=["H2O", "Ethanol", "Butanol", "Na+", "Cl-"],
      x=expanded_feed,
      T=temperature,
  )
  ```

  Evaluate `_native_electrolyte_contribution_block` at a finite positive density and require active electrolyte terms and finite residual Helmholtz contributions.

- [ ] **Step 2: Add phase-charge diagnostic check**

  Build two phase rows from the first organic and aqueous tie-line pair after explicit-ion expansion. Call `_native_eos_phase_system` with charges `[0.0, 0.0, 0.0, 1.0, -1.0]`. Require one charge-balance row per phase, finite residuals, residual norm <= `1.0e-8`, and nonempty analytic Jacobian entries in the ion columns.

- [ ] **Step 3: Harden native block tests**

  Add one test in `packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py` that imports the Khudaida source fixture helper from the checker and asserts native electrolyte diagnostics on the same first-row smoke case. Keep the existing synthetic/Ascani-style tests because they cover lower-level block behavior.

- [ ] **Step 4: Commit native diagnostic gate**

  Run:

  ```powershell
  git add scripts/validation/check_electrolyte_gfpe_gate.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py tests/native/contracts/test_electrolyte_gfpe_gate_checker.py
  git commit -m "Gate electrolyte diagnostics on Khudaida fixture"
  ```

### Task 5: Record Closed Public Route State In Capabilities And Registry

**Use Cases:**
- A user inspecting capabilities needs to see that electrolyte source diagnostics exist without seeing a public electrolyte route.
- A roadmap reviewer needs #191 evidence distinguished from #190 associating work and #192 benchmark closure.
- A future route-admission PR needs the registry to show which prerequisite gate already passed.

**Files:**
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml` and `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`

- [ ] **Step 1: Add capability closed-route assertions**

  Extend `test_activation_capabilities.py` so it asserts the electrolyte family row has:

  ```python
  assert electrolyte["key"] == "electrolyte_lle"
  assert electrolyte["production_exposed"] is False
  assert electrolyte["public_routes"] == []
  assert electrolyte["proof_routes"] == []
  assert "electrolyte_lle" not in capabilities["public_routes"]
  assert "electrolyte_lle" not in capabilities["production_families"]
  ```

- [ ] **Step 2: Add registry evidence row**

  In the `PE-Electrolyte LLE/TP Flash` registry row, add closed-admission evidence with command:

  ```text
  uv run --no-sync python scripts/validation/check_electrolyte_gfpe_gate.py --json --require-source-data --require-parameter-bundle --require-native-diagnostics --require-public-routes-closed --require-complete
  ```

  Set result requirement to source fixture parsed, explicit ions charge-balanced, path-based Khudaida parameter bundle constructs a native mixture, native electrolyte/charge diagnostics pass, public electrolyte routes remain closed.

- [ ] **Step 3: Add registry tests**

  Extend `test_generalized_equilibrium_registry.py` to require the new evidence row and to assert `production_exposed` remains false for `PE-Electrolyte LLE/TP Flash`.

- [ ] **Step 4: Update M4 README and #191 mirror**

  Add a queue guard note that this child closes only source-data and diagnostic readiness for electrolyte GFPE. Explicitly leave electrolyte TPD, HELD2 phase discovery, exact Born/SSM/DS Hessian, and public route admission pending.

- [ ] **Step 5: Commit docs and registry**

  Run:

  ```powershell
  git add packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml docs/superpowers/milestones/M4-equilibrium/README.md docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
  git commit -m "Record electrolyte GFPE source gate evidence"
  ```

### Task 6: Validate And Prepare The Child PR

**Use Cases:**
- A merge reviewer needs proof that the child gate is complete and the route remains closed.
- A future #191 worker needs exact remaining blockers after this first child merges.
- The repo needs cleanup and tracker state aligned before handoff.

**Files:**
- Test: all files changed by Tasks 1-5.

- [ ] **Step 1: Run proof oracle**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_electrolyte_gfpe_gate.py --json --require-source-data --require-parameter-bundle --require-native-diagnostics --require-public-routes-closed --require-complete
  uv run --no-sync python scripts/run_pytest.py tests/native/contracts/test_electrolyte_gfpe_gate_checker.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py
  uv run --no-sync python scripts/data/curate_paper_validation_parameters.py
  uv run --no-sync python scripts/dev/validate_project.py quick
  ```

- [ ] **Step 2: Run cleanup hook**

  Run:

  ```powershell
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  ```

- [ ] **Step 3: Confirm public routes remain closed**

  Run:

  ```powershell
  uv run --no-sync python -c "import epcsaft_equilibrium as e; c=e.capabilities(); print(c['public_routes']); print(c['activation_matrix']['declared_not_exposed_families'])"
  ```

  Expected: output includes current neutral public routes and declared closed families including `electrolyte_lle`; it does not include a public electrolyte route.

- [ ] **Step 4: Prepare PR summary**

  The PR summary must include:

  ```markdown
  Closes #<child-number>

  This adds the first #191 child gate. It proves Khudaida source fixture parsing, explicit-ion charge balance, path-based paper-validation parameter bundle execution, native electrolyte/charge diagnostics, and closed public route state.

  It does not admit electrolyte GFPE, HELD2 phase discovery, electrolyte TPD, or public electrolyte LLE.
  ```

## Proof Oracle

```powershell
uv run --no-sync python scripts/validation/check_electrolyte_gfpe_gate.py --json --require-source-data --require-parameter-bundle --require-native-diagnostics --require-public-routes-closed --require-complete
uv run --no-sync python scripts/run_pytest.py tests/native/contracts/test_electrolyte_gfpe_gate_checker.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py
uv run --no-sync python scripts/data/curate_paper_validation_parameters.py
uv run --no-sync python scripts/dev/validate_project.py quick
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Recommended Next Route

Run `$superpowers-project:create-issues` from this saved plan, create one child issue, then resolve that child before attempting direct `resolve-issue 191`.
