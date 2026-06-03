# Paper-Backed Association Closure Validation Matrix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a paper-backed explicit association validation matrix with Huang/Radosz topology reductions, repo-derivation closure comparisons, public saturation-data acquisition, and fixed-state provider property residuals.

**Architecture:** Extend the existing Python-only `analyses/package_validation/explicit_association_toybox` root instead of creating a new package or analysis package. Keep topology reductions, paper system manifests, public property source adapters, matrix runners, and figure scripts in focused analysis modules, with the exact implicit mass-action baseline as the common comparison arbiter. The property lane fetches public saturation data first, then computes fixed-state provider pressure/density residuals only for rows with available provider parameter payloads; it does not solve vapor-liquid equilibrium.

**Tech Stack:** Python stdlib `csv`, `html.parser`, `urllib.request`, NumPy, PyYAML, Matplotlib, pytest, existing `epcsaft.state.native_adapter.ePCSAFTMixture`; no SciPy, no provider C++, no equilibrium package.

---

## Intake

- Source spec: `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`
- Related derivation spec: `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
- Related toybox spec: `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-toybox-design.md`
- Related issues: `docs/superpowers/issues/2026-05-29-m3-eos-issue-0161-design-explicit-pc-saft-association-site-closures-for-eos-evaluation.md`, `docs/superpowers/issues/2026-06-03-m3-eos-issue-0216-add-hc-and-dispersion-context-to-the-explicit-association-toybox.md`
- Milestone: `M3 - EOS`
- Package boundary: analysis-only under `analyses/package_validation/explicit_association_toybox/**`, with provider API calls used only from analysis scripts.
- User decisions: first implementation should include the full property lane, and missing real data should be fetched from public sources before asking the user.
- Public source candidate verified during planning: NIST Chemistry WebBook thermophysical fluids page lists density and saturation-property data and includes methanol among selectable fluids.

## Acceptance Criteria

- [ ] Huang/Radosz Table VII topology reductions for `1`, `2A`, `2B`, `3A`, `3B`, `4A`, `4B`, and `4C` are implemented as topology reductions and verified against the generic exact mass-action baseline.
- [ ] Repo derivation closure families remain distinct: Closure A applies only to one-associating-component 2B, Closure B/C are full-matrix explicit approximations, and Closure D is diagnostic collapsed donor/acceptor mean field.
- [ ] Matrix rows include source formula family, source formula ID, derivation family, comparison role, topology gate, exactness claim, system metadata, site-fraction errors, mass-action residuals, association Helmholtz errors, elapsed times, speedup, and evidence band.
- [ ] Public saturation-data acquisition tries configured public sources first and writes retained source CSV plus source-status metadata when successful.
- [ ] Missing or blocked raw data are recorded in `data_request_manifest.csv` with `needs_user_source`, not replaced by paper AAD values.
- [ ] Fixed-state property residuals compare provider pressure at experimental saturated liquid density and provider liquid density at experimental saturation pressure for configured pure-component rows with provider parameter payloads.
- [ ] Property residual outputs are labeled `fixed_state_saturation_property_residual` and do not claim vapor-pressure prediction or equilibrium-route validation.
- [ ] Figure commands write retained plotted-data CSV, PNG, and `.mpl.yaml` sidecars under figure-owned `output/` folders.
- [ ] No `packages/epcsaft/**`, `packages/epcsaft-equilibrium/**`, `packages/epcsaft-regression/**`, SciPy dependency, or public API changes are introduced.

## Non-Goals

- No provider C++ implementation of explicit association closures.
- No public `epcsaft` API changes.
- No equilibrium saturation, bubble, dew, flash, LLE, or HELD route work.
- No regression or parameter fitting.
- No use of paper AAD values as raw validation data.
- No retained generated run payloads outside figure-owned `output/` folders.

## File Map

Create:

- `analyses/package_validation/explicit_association_toybox/config/paper_topologies.yaml`
- `analyses/package_validation/explicit_association_toybox/config/paper_systems.yaml`
- `analyses/package_validation/explicit_association_toybox/config/public_property_sources.yaml`
- `analyses/package_validation/explicit_association_toybox/shared/source/data_request_manifest.csv`
- `analyses/package_validation/explicit_association_toybox/scripts/topology_reductions.py`
- `analyses/package_validation/explicit_association_toybox/scripts/paper_systems.py`
- `analyses/package_validation/explicit_association_toybox/scripts/public_property_sources.py`
- `analyses/package_validation/explicit_association_toybox/scripts/fixed_state_property_residuals.py`
- `analyses/package_validation/explicit_association_toybox/scripts/run_topology_matrix.py`
- `analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_paper_systems.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_topology_reductions.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_topology_matrix_output.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_public_property_sources.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py`

Modify:

- `analyses/package_validation/explicit_association_toybox/README.md`
- `analyses/package_validation/explicit_association_toybox/analysis.yaml`
- `analyses/package_validation/explicit_association_toybox/config/closure_sweep.yaml`
- `analyses/package_validation/explicit_association_toybox/scripts/closure_models.py`
- `analyses/package_validation/explicit_association_toybox/scripts/metrics.py`
- `analyses/package_validation/explicit_association_toybox/scripts/run_grid.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`

## Task 1: Lock Paper Topology And System Manifests

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/config/paper_topologies.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/config/paper_systems.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/paper_systems.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_paper_systems.py`

- [ ] **Step 1: Write failing manifest schema tests**

Add tests that load `paper_topologies.yaml` and require the exact topology IDs `hr_1`, `hr_2a`, `hr_2b`, `hr_3a`, `hr_3b`, `hr_4a`, `hr_4b`, and `hr_4c`. Each topology must define `source_formula_family`, `source_formula_id`, `site_kind`, `active_pairs`, `exactness_claim`, and `derivation_relationship`.

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_paper_systems.py -q
```

Expected: FAIL because the files and loader do not exist.

- [ ] **Step 2: Create topology and paper-system configs**

Create `paper_topologies.yaml` with the Huang/Radosz Table VII reductions. Use zero-based site indices and symmetric active pairs. Use these active-pair patterns:

```yaml
topologies:
  hr_1:
    source_formula_family: huang_radosz_table_vii
    source_formula_id: "1"
    site_kind: [A]
    active_pairs: [[0, 0]]
    exactness_claim: exact_for_table_vii_topology
    derivation_relationship: topology_reduction
  hr_2a:
    source_formula_family: huang_radosz_table_vii
    source_formula_id: "2A"
    site_kind: [A, B]
    active_pairs: [[0, 0], [0, 1], [1, 0], [1, 1]]
    exactness_claim: exact_for_table_vii_topology
    derivation_relationship: topology_reduction
  hr_2b:
    source_formula_family: huang_radosz_table_vii
    source_formula_id: "2B"
    site_kind: [D, A]
    active_pairs: [[0, 1], [1, 0]]
    exactness_claim: exact_for_table_vii_topology
    derivation_relationship: closure_a_2b_when_one_associating_component
  hr_3a:
    source_formula_family: huang_radosz_table_vii
    source_formula_id: "3A"
    site_kind: [A, B, C]
    active_pairs: [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
    exactness_claim: exact_for_table_vii_topology
    derivation_relationship: topology_reduction
  hr_3b:
    source_formula_family: huang_radosz_table_vii
    source_formula_id: "3B"
    site_kind: [D, D, A]
    active_pairs: [[0, 2], [2, 0], [1, 2], [2, 1]]
    exactness_claim: exact_for_table_vii_topology
    derivation_relationship: topology_reduction
  hr_4a:
    source_formula_family: huang_radosz_table_vii
    source_formula_id: "4A"
    site_kind: [A, B, C, D]
    active_pairs: [[0, 0], [0, 1], [0, 2], [0, 3], [1, 0], [1, 1], [1, 2], [1, 3], [2, 0], [2, 1], [2, 2], [2, 3], [3, 0], [3, 1], [3, 2], [3, 3]]
    exactness_claim: exact_for_table_vii_topology
    derivation_relationship: topology_reduction
  hr_4b:
    source_formula_family: huang_radosz_table_vii
    source_formula_id: "4B"
    site_kind: [D, D, D, A]
    active_pairs: [[0, 3], [3, 0], [1, 3], [3, 1], [2, 3], [3, 2]]
    exactness_claim: exact_for_table_vii_topology
    derivation_relationship: topology_reduction
  hr_4c:
    source_formula_family: huang_radosz_table_vii
    source_formula_id: "4C"
    site_kind: [D, D, A, A]
    active_pairs: [[0, 2], [2, 0], [0, 3], [3, 0], [1, 2], [2, 1], [1, 3], [3, 1]]
    exactness_claim: exact_for_table_vii_topology
    derivation_relationship: topology_reduction
```

Create `paper_systems.yaml` with a first compact source-backed set:

```yaml
systems:
  hr_water_assigned_3b:
    source_paper: huang_radosz_1990
    component_names: [water]
    topology_id: hr_3b
    rigorous_topology: hr_4c
    assigned_topology: hr_3b
    property_data_status: public_source_candidate
  hr_methanol_assigned_2b:
    source_paper: huang_radosz_1990
    component_names: [methanol]
    topology_id: hr_2b
    rigorous_topology: hr_3b
    assigned_topology: hr_2b
    property_data_status: public_source_candidate
  gross_methanol_cyclohexane_2b:
    source_paper: gross_sadowski_2002
    component_names: [methanol, cyclohexane]
    topology_id: hr_2b
    rigorous_topology: hr_2b
    assigned_topology: hr_2b
    property_data_status: metadata_only
```

- [ ] **Step 3: Implement `paper_systems.py`**

Implement `load_paper_topologies(path: Path) -> dict[str, dict[str, object]]` and `load_paper_systems(path: Path) -> dict[str, dict[str, object]]`. Validate required keys, known topology references, and non-empty active pairs. Raise `ValueError` with the missing key name on invalid input.

- [ ] **Step 4: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_paper_systems.py -q
```

Expected: PASS.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/config/paper_topologies.yaml analyses/package_validation/explicit_association_toybox/config/paper_systems.yaml analyses/package_validation/explicit_association_toybox/scripts/paper_systems.py analyses/package_validation/explicit_association_toybox/tests/test_paper_systems.py
git commit -m "test: add association paper manifests"
```

## Task 2: Implement Huang/Radosz Topology Reductions

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/topology_reductions.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_topology_reductions.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/closure_models.py`

- [ ] **Step 1: Write failing exact-reduction tests**

Add tests that instantiate each topology from `paper_topologies.yaml`, build `AssociationSystem`, set `density = 0.2`, `composition = np.array([1.0])`, and `delta = system.delta_matrix(strength=3.0)`. For each `hr_*` reduction, compare `evaluate_topology_reduction(topology_id, density=density, x_assoc=system.x_assoc(composition), delta=delta)` against `solve_exact_site_fractions(...)` with `np.testing.assert_allclose(..., atol=1e-11, rtol=1e-11)`.

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_topology_reductions.py -q
```

Expected: FAIL because `topology_reductions.py` does not exist.

- [ ] **Step 2: Implement stable scalar helpers**

Create `topology_reductions.py` with stable helper functions:

```python
def _solve_equivalent_sites(site_count: int, rho_delta: float) -> float:
    if rho_delta == 0.0:
        return 1.0
    return 2.0 / (1.0 + (1.0 + 4.0 * site_count * rho_delta) ** 0.5)

def _solve_single_pair(rho_delta: float) -> float:
    if rho_delta == 0.0:
        return 1.0
    return 2.0 / (1.0 + (1.0 + 4.0 * rho_delta) ** 0.5)
```

Implement `evaluate_topology_reduction(...)` for:

- `hr_1`: one self-associating site, `X = _solve_single_pair(rho_delta)`.
- `hr_2a`: equivalent-site reduction with `site_count=2`.
- `hr_2b`: both sites use `_solve_single_pair(rho_delta)`.
- `hr_3a`: equivalent-site reduction with `site_count=3`.
- `hr_3b`: compute `x = (-(1.0 - r) + sqrt((1.0 + r)^2 + 4.0 * r)) / (4.0 * r)` with zero-strength limit `1.0`, then return `[x, x, 2.0 * x - 1.0]`.
- `hr_4a`: equivalent-site reduction with `site_count=4`.
- `hr_4b`: compute `x = (-(1.0 - 2.0 * r) + sqrt((1.0 + 2.0 * r)^2 + 4.0 * r)) / (6.0 * r)` with zero-strength limit `1.0`, then return `[x, x, x, 3.0 * x - 2.0]`.
- `hr_4c`: equivalent donor/acceptor-like reduction with `X = _solve_equivalent_sites(2, r)`.

Use `r = density * strength` only after checking that the active nonzero entries of `delta` are all equal within `np.allclose`. Raise `ValueError("Huang/Radosz topology reductions require a single nonzero association strength.")` when that gate fails.

- [ ] **Step 3: Add derivation metadata to closure results**

Extend `ClosureResult` in `closure_models.py` with:

```python
source_formula_family: str
source_formula_id: str
derivation_family: str
comparison_role: str
topology_gate: str
exactness_claim: str
```

Populate existing closures:

- `closure_2b_exact_reduction`: `source_formula_family="repo_derivation"`, `source_formula_id="closure_a"`, `derivation_family="closure_a_2b"`, `comparison_role="exact_topology_reduction"`, `topology_gate="matched"`, `exactness_claim="exact_mass_action"`.
- Picard variants: `derivation_family="closure_b_picard"` or `closure_c_picard_diagonal_newton`, `comparison_role="explicit_approximation"`, `exactness_claim="exact_for_approximate_model"`.
- Collapsed mean field: `derivation_family="closure_d_collapsed_mean_field"`, `comparison_role="diagnostic_collapse"`, `topology_gate="diagnostic_only"`, `exactness_claim="none"`.

- [ ] **Step 4: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_topology_reductions.py analyses/package_validation/explicit_association_toybox/tests/test_closure_a_exact_reduction.py -q
```

Expected: PASS.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/topology_reductions.py analyses/package_validation/explicit_association_toybox/scripts/closure_models.py analyses/package_validation/explicit_association_toybox/tests/test_topology_reductions.py analyses/package_validation/explicit_association_toybox/tests/test_closure_a_exact_reduction.py
git commit -m "feat: add Huang Radosz topology reductions"
```

## Task 3: Add The Topology Matrix Runner And Output Schema

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/run_topology_matrix.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_topology_matrix_output.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/metrics.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`

- [ ] **Step 1: Write failing matrix schema tests**

Add a test that runs `run_topology_matrix(output_path=tmp_path / "topology_matrix.csv", topology_ids=("hr_2b",), closure_names=("closure_2b_exact_reduction", "explicit_damped_picard_unroll_3"))` and asserts these columns exist:

```text
source_formula_family,source_formula_id,derivation_family,comparison_role,topology_gate,exactness_claim,system,topology_id,closure,max_abs_x_error,mass_residual_inf,assoc_helmholtz_abs_error,exact_elapsed_seconds,model_elapsed_seconds,speedup_ratio,evidence_band
```

Expected: FAIL because the runner does not exist.

- [ ] **Step 2: Implement matrix row metrics**

Modify `metrics.metric_row(...)` to include the six new metadata fields, rename `closure_elapsed_seconds` to `model_elapsed_seconds`, and add `exact_elapsed_seconds` plus `speedup_ratio = exact_elapsed_seconds / model_elapsed_seconds` when both are positive. Keep the existing closure-accuracy output compatible by preserving the original `closure_elapsed_seconds` column as a duplicate for one plan cycle, then remove it in the next cleanup issue if the matrix succeeds.

- [ ] **Step 3: Implement `run_topology_matrix.py`**

The runner should:

1. Load `paper_topologies.yaml`.
2. Build one pure `AssociationSystem` per topology with `component_count=1` and all sites belonging to component 0.
3. Use a compact default grid: `density_grid = [0.001, 0.01, 0.05, 0.1]`, `strength_grid = [0.1, 1.0, 10.0, 50.0]`, `composition = [1.0]`.
4. Time the exact baseline with `timed_closure(lambda: solve_exact_site_fractions(...))`.
5. Evaluate the matching topology reduction and the requested repo derivation closures.
6. Write retained CSV under `figures/topology_validation_matrix/output/topology_matrix.csv`.

- [ ] **Step 4: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_topology_matrix_output.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py -q
uv run python analyses/package_validation/explicit_association_toybox/scripts/run_topology_matrix.py
```

Expected: tests PASS and `analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/output/topology_matrix.csv` exists.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/run_topology_matrix.py analyses/package_validation/explicit_association_toybox/scripts/metrics.py analyses/package_validation/explicit_association_toybox/tests/test_topology_matrix_output.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/output/topology_matrix.csv
git commit -m "feat: add association topology matrix runner"
```

## Task 4: Add Matrix And Timing Figures

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/render_figure.py`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`
- Modify: `analyses/package_validation/explicit_association_toybox/README.md`

- [ ] **Step 1: Add figure commands**

Add `analysis.yaml` commands:

```yaml
  generate_topology_matrix: uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/generate_data.py
  render_topology_matrix: uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/render_figure.py
  generate_timing_pareto: uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/generate_data.py
  render_timing_pareto: uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/render_figure.py
```

- [ ] **Step 2: Implement topology matrix figure**

`generate_data.py` should call `run_topology_matrix()`. `render_figure.py` should read `topology_matrix.csv`, group by `topology_id` and `closure`, compute max `assoc_helmholtz_rel_error`, write `topology_validation_matrix_plotted_data.csv`, render `topology_validation_matrix.png`, and write `topology_validation_matrix.mpl.yaml`.

- [ ] **Step 3: Implement timing Pareto figure**

`generate_data.py` should reuse `run_topology_matrix()`. `render_figure.py` should read the same matrix CSV, write `timing_pareto_plotted_data.csv`, and render error versus speedup with one point per closure/topology pair.

- [ ] **Step 4: Verify and commit**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/render_figure.py
```

Expected: each figure output folder contains CSV, plotted-data CSV, PNG, and `.mpl.yaml`.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix analyses/package_validation/explicit_association_toybox/figures/timing_pareto analyses/package_validation/explicit_association_toybox/analysis.yaml analyses/package_validation/explicit_association_toybox/README.md
git commit -m "docs: add association topology matrix figures"
```

## Task 5: Add Public Saturation Data Fetching

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/config/public_property_sources.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/shared/source/data_request_manifest.csv`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/public_property_sources.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_public_property_sources.py`

- [ ] **Step 1: Write failing parser and manifest tests**

Use a saved inline HTML sample with one `<table>` containing `Temperature (K)`, `Pressure (MPa)`, `Density (mol/l)`, and `Phase`. Assert `parse_nist_saturation_html(...)` returns liquid rows with `T_K`, `p_sat_Pa`, `rho_sat_liq_mol_m3`, `phase`, and `source_url`.

Expected: FAIL because the parser does not exist.

- [ ] **Step 2: Create public source config**

Create `public_property_sources.yaml`:

```yaml
sources:
  nist_webbook_methanol:
    provider: nist_webbook_srd69
    component: methanol
    nist_id: C67561
    properties: [p_sat, rho_sat_liq]
    url_template: "https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID={nist_id}&Type=SatT&TUnit=K&PUnit=MPa&DUnit=mol%2Fl&HUnit=kJ%2Fmol&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm&RefState=DEF&Digits=5&TLow={t_low}&THigh={t_high}&TInc={t_inc}"
    t_low: 273.0
    t_high: 373.0
    t_inc: 10.0
  nist_webbook_water:
    provider: nist_webbook_srd69
    component: water
    nist_id: C7732185
    properties: [p_sat, rho_sat_liq]
    url_template: "https://webbook.nist.gov/cgi/fluid.cgi?Action=Load&ID={nist_id}&Type=SatT&TUnit=K&PUnit=MPa&DUnit=mol%2Fl&HUnit=kJ%2Fmol&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm&RefState=DEF&Digits=5&TLow={t_low}&THigh={t_high}&TInc={t_inc}"
    t_low: 283.0
    t_high: 373.0
    t_inc: 10.0
```

Create `data_request_manifest.csv` with headers:

```text
system_id,component,property,temperature_range,pressure_range,source_named_in_paper,repo_source_available,public_source_candidate,user_input_needed,status
```

- [ ] **Step 3: Implement public source module**

Implement:

- `nist_saturation_url(source: Mapping[str, object]) -> str`
- `parse_nist_saturation_html(html: str, source_url: str) -> list[dict[str, object]]`
- `fetch_nist_saturation(source: Mapping[str, object], *, allow_network: bool) -> list[dict[str, object]]`
- `write_public_property_csv(rows, output_path)`

When `allow_network=False`, raise `ValueError("public data fetch requires allow_network=True")`.

- [ ] **Step 4: Verify offline parser tests and live fetch command**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_public_property_sources.py -q
uv run python -m analyses.package_validation.explicit_association_toybox.scripts.public_property_sources --allow-network --output analyses/package_validation/explicit_association_toybox/shared/source/public_saturation_properties.csv
```

Expected: tests PASS and the live command writes `public_saturation_properties.csv` with at least one methanol and one water liquid row. When the NIST live request cannot reach the service or the page shape changes, commit the parser/tests and update `data_request_manifest.csv` statuses to `public_source_candidate` without committing partial fetched data.

- [ ] **Step 5: Commit**

```powershell
git add analyses/package_validation/explicit_association_toybox/config/public_property_sources.yaml analyses/package_validation/explicit_association_toybox/shared/source/data_request_manifest.csv analyses/package_validation/explicit_association_toybox/shared/source/public_saturation_properties.csv analyses/package_validation/explicit_association_toybox/scripts/public_property_sources.py analyses/package_validation/explicit_association_toybox/tests/test_public_property_sources.py
git commit -m "feat: add public saturation data inventory"
```

## Task 6: Add Fixed-State Provider Property Residuals

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/fixed_state_property_residuals.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py`
- Modify: `analyses/package_validation/explicit_association_toybox/config/paper_systems.yaml`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`

- [ ] **Step 1: Add provider parameter rows**

Extend `paper_systems.yaml` with provider parameter payloads for `methanol` and `water` using existing repo dataset conventions:

```yaml
provider_parameter_cases:
  methanol_gross_2002:
    species: [methanol]
    params:
      MW: [0.032042]
      m: [1.5255]
      s: [3.2300]
      e: [188.90]
      e_assoc: [2899.5]
      vol_a: [0.035176]
      assoc_scheme: [2B]
      z: [0.0]
      dielc: [32.7]
  water_epcsaft_revised:
    species: [water]
    params:
      MW: [0.01801528]
      m: [1.2047]
      s: [3.0]
      e: [353.95]
      e_assoc: [2425.7]
      vol_a: [0.04509]
      assoc_scheme: [2B]
      z: [0.0]
      dielc: [78.09]
```

The water row uses a simple fixed `s` only for the first fixed-state residual lane. A later plan can add temperature-dependent water sigma if the residual lane becomes validation evidence.

- [ ] **Step 2: Write failing residual tests**

Add tests using two synthetic public saturation rows:

```python
rows = [
    {"component": "methanol", "T_K": 293.15, "p_sat_Pa": 13000.0, "rho_sat_liq_mol_m3": 24600.0, "phase": "liquid"},
]
```

Assert `fixed_state_property_residual_rows(rows, provider_cases)` returns columns:

```text
component,T_K,p_sat_Pa,rho_sat_liq_mol_m3,pressure_from_density_Pa,pressure_residual_Pa,pressure_residual_rel,density_from_pressure_mol_m3,density_residual_mol_m3,density_residual_rel,property_workflow
```

Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement fixed-state residuals**

Implement `fixed_state_property_residual_rows(...)` using `ePCSAFTMixture.from_params`. For each source row:

1. Construct a pure mixture for the component.
2. Build a density-based liquid state with `rho=rho_sat_liq_mol_m3` and compute `pressure_from_density_Pa = state.pressure()`.
3. Build a pressure-based liquid state with `P=p_sat_Pa`, `phase="liq"`, and compute `density_from_pressure_mol_m3 = state.density()`.
4. Compute residuals and relative residuals.
5. Set `property_workflow="fixed_state_saturation_property_residual"`.

Catch `InputError` and `SolutionError` per row and write `status="failed"` plus `message`; do not substitute fake numeric defaults.

- [ ] **Step 4: Add property residual figure**

`property_residuals/scripts/generate_data.py` should read `shared/source/public_saturation_properties.csv`, compute residuals, and write `figures/property_residuals/output/property_residuals.csv`. `render_figure.py` should write plotted data and a PNG with component on the x-axis and absolute pressure/density relative residual panels.

- [ ] **Step 5: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py
```

Expected: tests PASS and property residual artifacts exist when public saturation source CSV exists. When the public source CSV is missing, the generate command must fail loudly with a message naming `shared/source/public_saturation_properties.csv`.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/fixed_state_property_residuals.py analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py analyses/package_validation/explicit_association_toybox/figures/property_residuals analyses/package_validation/explicit_association_toybox/config/paper_systems.yaml analyses/package_validation/explicit_association_toybox/analysis.yaml
git commit -m "feat: add fixed state property residual lane"
```

## Task 7: Final Documentation And Structure Validation

**Files:**
- Modify: `analyses/package_validation/explicit_association_toybox/README.md`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`
- Test: `tests/workflows/repo/test_project_structure.py`

- [ ] **Step 1: Update README boundaries**

Document these explicit boundaries:

- topology reductions are exact only under Huang/Radosz Table VII assumptions;
- Closure B/C derivatives remain exact derivatives of approximate closures;
- public saturation rows are source data, not package validation by themselves;
- fixed-state residuals are not vapor-pressure prediction and not equilibrium validation;
- missing proprietary data belongs in `shared/source/data_request_manifest.csv`.

- [ ] **Step 2: Run focused tests**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
```

Expected: PASS.

- [ ] **Step 3: Run figure commands**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py
```

Expected: retained CSV, plotted data, PNG, and `.mpl.yaml` sidecars exist for every figure folder.

- [ ] **Step 4: Run completion validation**

Run:

```powershell
uv run python scripts/dev/validate_project.py quick
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Expected: quick validation passes or any failure is triaged to the exact unrelated/pre-existing cause; cleanup reports no matching leftover Codex processes.

- [ ] **Step 5: Commit final docs and outputs**

```powershell
git add analyses/package_validation/explicit_association_toybox/README.md analyses/package_validation/explicit_association_toybox/analysis.yaml analyses/package_validation/explicit_association_toybox/figures
git commit -m "docs: document association validation matrix"
```

## Proof Oracle

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/render_figure.py
uv run python -m analyses.package_validation.explicit_association_toybox.scripts.public_property_sources --allow-network --output analyses/package_validation/explicit_association_toybox/shared/source/public_saturation_properties.csv
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py
uv run python scripts/dev/validate_project.py quick
```

## Risk And Dependency Notes

- NIST live fetch can fail because of network, service, or data-page changes. Tests must use offline parser fixtures; the live fetch command is proof evidence, not a unit-test dependency.
- The fixed-state residual lane uses provider pressure/density states only. It must not claim saturation prediction, phase equilibrium, or vapor pressure solving.
- The water provider row uses a fixed first-pass sigma. If water residuals are used as validation evidence, a later plan must source the temperature-dependent sigma expression from existing provider data.
- Existing issue #216 may add HC/dispersion context on a separate branch. Rebase before implementation and keep this matrix plan compatible with any new `ares_hc`, `ares_disp`, and total `ares` columns.
- When public data cannot be sourced for a target component, write `needs_user_source` in `data_request_manifest.csv` and stop property residual generation for that component.

## Required Development Skills

- Use `superpowers:test-driven-development` for implementation tasks.
- Use `chemical-engineer` when transcribing Huang/Radosz formulas and interpreting fixed-state property residuals.
- Use `superpowers:systematic-debugging` or `diagnose` if public fetch, provider density roots, or matrix validations fail unexpectedly.
- Use `superpowers:verification-before-completion` before claiming the issue complete.
