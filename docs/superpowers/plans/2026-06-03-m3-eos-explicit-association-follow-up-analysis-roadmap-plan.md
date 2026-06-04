# Explicit Association Follow-Up Analysis Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the explicit association toybox with topology-resolved, real-system, derivative-smoothness, property-residual, timing, water-parameter, and total-`ares` evidence lanes before any production EOS closure decision.

**Architecture:** Keep the work inside `analyses/package_validation/explicit_association_toybox` and add focused figure-owned workflows with analysis-local tests. Reuse the existing exact mass-action baseline, Huang/Radosz topology matrix, public source loader, and fixed-state provider residual path; issue #216 remains the source for hard-chain and dispersion scalar context. Each lane writes retained CSVs, plotted data, PNGs, and `.mpl.yaml` sidecars under figure-owned `output` folders.

**Tech Stack:** Python stdlib, NumPy, PyYAML, Matplotlib, pytest, existing toybox modules, optional provider API calls already used by the property residual lane; no SciPy dependency, provider C++, equilibrium package, regression package, or public API changes.

---

## Intake

- Source spec: `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-follow-up-analysis-roadmap.md`
- Base matrix spec: `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`
- Base matrix plan: `docs/superpowers/plans/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-plan.md`
- Related HC/dispersion issue: `docs/superpowers/issues/2026-06-03-m3-eos-issue-0216-add-hc-and-dispersion-context-to-the-explicit-association-toybox.md`
- Milestone linkage: `M3 - EOS`
- Package boundary: analysis-only, provider validation evidence under `analyses/package_validation/explicit_association_toybox/**`

## Required Development Skills

- Use `superpowers:test-driven-development` for each implementation task.
- Use `chemical-engineer` for topology, residual Helmholtz, property residual, and derivative-smoothness interpretation.
- Use `matplotlib-plotting` for every task that creates or revises a plot.
- Use `superpowers:verification-before-completion` before reporting implementation complete.

## Acceptance Criteria

- [ ] Topology heatmap outputs show closure error by topology and `rho * Delta`, with retained plotted data.
- [ ] Real-system mapping rows cover source-backed representative families: acids, alkanols, water, amines, and Gross/Sadowski associating binaries.
- [ ] Closure sensitivity outputs rank Picard count, damping, and diagonal-polish variants by error and timing.
- [ ] Derivative smoothness diagnostics report density, association-strength, and composition perturbation behavior for exact and approximate closures.
- [ ] Property residual outputs include pressure residual in MPa and compressibility-factor residuals alongside the existing relative pressure residual.
- [ ] Water-specific rows record the parameter source and diameter handling used by the analysis.
- [ ] Repeated timing summaries report median, interquartile range, minimum, and maximum for exact and closure evaluations.
- [ ] Total neutral `ares` context is included only through the issue #216 HC/dispersion lane or equivalent already-merged files.
- [ ] All new or updated figure workflows write retained CSV, plotted-data CSV, PNG, and `.mpl.yaml` sidecar files.
- [ ] Final implementation reporting renders every new or updated plot inline in chat and includes compact Markdown tables from retained data.
- [ ] No `packages/epcsaft/**`, `packages/epcsaft-equilibrium/**`, `packages/epcsaft-regression/**`, public API, dependency, or production EOS behavior changes are introduced.

## Non-Goals

- No provider runtime implementation of explicit closures.
- No equilibrium route validation, pressure-transformed objective assembly, or HELD work.
- No regression or parameter fitting workflow.
- No claim that analysis finite perturbation diagnostics are production exact derivatives.
- No new source data entered from paper AAD summaries as if they were raw measurement rows.
- No centralized gallery folder; keep all generated artifacts figure-owned.

## File Map

Create:

- `analyses/package_validation/explicit_association_toybox/config/closure_sensitivity.yaml`
- `analyses/package_validation/explicit_association_toybox/config/real_system_topology_map.yaml`
- `analyses/package_validation/explicit_association_toybox/config/water_parameter_cases.yaml`
- `analyses/package_validation/explicit_association_toybox/scripts/closure_sensitivity.py`
- `analyses/package_validation/explicit_association_toybox/scripts/derivative_smoothness.py`
- `analyses/package_validation/explicit_association_toybox/scripts/repeated_timing.py`
- `analyses/package_validation/explicit_association_toybox/scripts/real_system_topology_map.py`
- `analyses/package_validation/explicit_association_toybox/scripts/water_parameter_cases.py`
- `analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_closure_sensitivity.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_derivative_smoothness.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_real_system_topology_map.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_repeated_timing.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_water_parameter_cases.py`

Modify:

- `analyses/package_validation/explicit_association_toybox/README.md`
- `analyses/package_validation/explicit_association_toybox/analysis.yaml`
- `analyses/package_validation/explicit_association_toybox/config/paper_systems.yaml`
- `analyses/package_validation/explicit_association_toybox/config/public_property_sources.yaml`
- `analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/scripts/fixed_state_property_residuals.py`
- `analyses/package_validation/explicit_association_toybox/scripts/run_topology_matrix.py`
- `analyses/package_validation/explicit_association_toybox/scripts/summarize_results.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`

## Task 1: Add Topology Error Heatmaps

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/render_figure.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/run_topology_matrix.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_topology_matrix.py`

- [ ] **Step 1: Write the failing heatmap-data contract test**

Add assertions to `test_topology_matrix.py` that the generated topology matrix rows contain:

```python
required = {
    "topology_id",
    "closure_name",
    "rho_delta",
    "ares_assoc_rel_error",
    "mass_action_residual_inf",
    "evidence_band",
}
```

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_topology_matrix.py -q
```

Expected result: fail if `rho_delta` is missing from current rows.

- [ ] **Step 2: Add `rho_delta` to topology-matrix rows**

Modify `run_topology_matrix.py` so each row records `rho_delta = density * association_strength_scale` or the existing scalar equivalent used to build the active `Delta` matrix. Keep the old columns unchanged.

- [ ] **Step 3: Add figure data generator**

Create `figures/topology_error_heatmaps/scripts/generate_data.py`. It should call the topology matrix runner, write:

```text
figures/topology_error_heatmaps/output/topology_error_heatmap.csv
```

with one row per `topology_id`, `closure_name`, and `rho_delta`.

- [ ] **Step 4: Add heatmap renderer**

Create `figures/topology_error_heatmaps/scripts/render_figure.py`. It should read the heatmap CSV, write:

```text
topology_error_heatmap_plotted_data.csv
topology_error_heatmap.png
topology_error_heatmap.mpl.yaml
```

Use log-scaled color for `ares_assoc_rel_error` and separate panels or grouped axes by closure family.

- [ ] **Step 5: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_topology_matrix.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/render_figure.py
```

Expected result: tests pass and all three heatmap output files are created.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox
git commit -m "feat: add association topology error heatmaps"
```

## Task 2: Add Real-System Topology Mapping

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/config/real_system_topology_map.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/real_system_topology_map.py`
- Modify: `analyses/package_validation/explicit_association_toybox/config/paper_systems.yaml`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_real_system_topology_map.py`

- [ ] **Step 1: Write failing mapping tests**

Create tests requiring mappings for at least:

```text
acid_1
alkanol_2b
water_3b_assigned_4c_rigorous
primary_amine_3b
secondary_amine_2b
gross_methanol_cyclohexane_2b
```

Each row must include `source_paper`, `component_family`, `assigned_topology`,
`rigorous_topology`, `parameter_source_status`, and `validation_role`.

- [ ] **Step 2: Create the YAML map**

Create `real_system_topology_map.yaml` with source-backed rows that connect
Huang/Radosz Table VIII families and Gross/Sadowski associating binary examples
to the topology IDs already present in `paper_topologies.yaml`.

- [ ] **Step 3: Implement loader and merge helper**

Implement `load_real_system_topology_map(path)` and
`expand_real_system_rows(topology_map, paper_systems)` in
`real_system_topology_map.py`. Raise `ValueError` when an assigned topology is
not present in the topology registry or when a row lacks source metadata.

- [ ] **Step 4: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_real_system_topology_map.py -q
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/config/real_system_topology_map.yaml analyses/package_validation/explicit_association_toybox/scripts/real_system_topology_map.py analyses/package_validation/explicit_association_toybox/tests/test_real_system_topology_map.py analyses/package_validation/explicit_association_toybox/config/paper_systems.yaml
git commit -m "feat: add real associating system topology map"
```

## Task 3: Add Closure Sensitivity Ranking

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/config/closure_sensitivity.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/closure_sensitivity.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/render_figure.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_closure_sensitivity.py`

- [ ] **Step 1: Write failing sensitivity tests**

Test that the candidate stress runner returns rows with:

```text
closure_name
picard_steps
damping
max_ares_assoc_rel_error
max_mass_action_residual_inf
median_elapsed_seconds
evidence_band
```

- [ ] **Step 2: Add sensitivity config**

Create a compact config for the active candidate:

```yaml
candidate:
  closure_name: damped_picard_7_05
  picard_steps: 7
  damping: 0.5
```

- [ ] **Step 3: Implement sensitivity runner**

Implement a runner that evaluates the active candidate on the existing topology
matrix cases and writes aggregate stress-grid results to:

```text
figures/closure_sensitivity/output/closure_sensitivity.csv
```

- [ ] **Step 4: Render Pareto figure**

Render error versus elapsed time with closure labels. Retain:

```text
closure_sensitivity_plotted_data.csv
closure_sensitivity.png
closure_sensitivity.mpl.yaml
```

- [ ] **Step 5: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_closure_sensitivity.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/render_figure.py
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox
git commit -m "feat: rank explicit association closure sensitivity"
```

## Task 4: Add Derivative Smoothness Diagnostics

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/derivative_smoothness.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/render_figure.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_derivative_smoothness.py`

- [ ] **Step 1: Write failing smoothness tests**

Test that a small diagnostic case returns rows with:

```text
closure_name
perturbation_axis
base_value
step_size
first_derivative_left
first_derivative_right
derivative_jump_abs
relative_jump
smoothness_band
```

Use axes `density`, `association_strength_scale`, and `composition_component_0`
for a binary case.

- [ ] **Step 2: Implement perturbation evaluator**

Create helpers that evaluate `ares_assoc` at `x - h`, `x`, and `x + h` for the
selected scalar coordinate. Compute left and right slopes and the absolute
jump. Keep the function names analysis-specific:

```python
evaluate_density_smoothness(...)
evaluate_strength_smoothness(...)
evaluate_composition_smoothness(...)
```

- [ ] **Step 3: Add figure workflow**

Write:

```text
figures/derivative_smoothness/output/derivative_smoothness.csv
figures/derivative_smoothness/output/derivative_smoothness_plotted_data.csv
figures/derivative_smoothness/output/derivative_smoothness.png
figures/derivative_smoothness/output/derivative_smoothness.mpl.yaml
```

Use grouped bars or points by closure and perturbation axis.

- [ ] **Step 4: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_derivative_smoothness.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/render_figure.py
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox
git commit -m "feat: add association closure smoothness diagnostics"
```

## Task 5: Reframe Fixed-State Property Residuals

**Files:**
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/fixed_state_property_residuals.py`
- Modify: `analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py`
- Modify: `analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py`

- [ ] **Step 1: Write failing residual-column tests**

Require output columns:

```text
pressure_residual_pa
pressure_residual_mpa
pressure_residual_rel
z_experimental
z_provider
z_residual_abs
density_residual_abs
density_residual_rel
```

- [ ] **Step 2: Add MPa and `Z` residual calculations**

Compute:

```python
pressure_residual_mpa = pressure_residual_pa / 1_000_000.0
z_experimental = pressure_pa / (density_mol_m3 * GAS_CONSTANT * temperature_k)
z_provider = provider_pressure_pa / (density_mol_m3 * GAS_CONSTANT * temperature_k)
z_residual_abs = abs(z_provider - z_experimental)
```

Use the existing gas constant convention from the analysis or define a local
`GAS_CONSTANT = 8.31446261815324` in the analysis module.

- [ ] **Step 3: Update property residual plot**

Render pressure residual in MPa and `Z` residual in separate panels or a clear
two-axis figure. Retain plotted data with the new columns.

- [ ] **Step 4: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/fixed_state_property_residuals.py analyses/package_validation/explicit_association_toybox/figures/property_residuals analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py
git commit -m "feat: reframe fixed-state pressure residual diagnostics"
```

## Task 6: Add Water Parameter Cases

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/config/water_parameter_cases.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/water_parameter_cases.py`
- Modify: `analyses/package_validation/explicit_association_toybox/config/public_property_sources.yaml`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_water_parameter_cases.py`

- [ ] **Step 1: Write failing water-case tests**

Require water cases to record:

```text
case_id
topology_id
parameter_source
sigma_policy
temperature_range_k
property_source
comparison_role
```

- [ ] **Step 2: Add water parameter config**

Create at least two cases:

```yaml
cases:
  - case_id: water_assigned_3b_provider_default
    topology_id: hr_3b
    parameter_source: provider_default
    sigma_policy: provider_constant
    temperature_range_k: [273.18, 647.10]
    property_source: nist_webbook_public_saturation
    comparison_role: fixed_state_diagnostic
  - case_id: water_rigorous_4c_source_label_only
    topology_id: hr_4c
    parameter_source: source_label_only
    sigma_policy: source_metadata_required
    temperature_range_k: [273.18, 647.10]
    property_source: nist_webbook_public_saturation
    comparison_role: topology_reference
```

- [ ] **Step 3: Implement loader**

Implement `load_water_parameter_cases(path)` with schema validation and a helper
that links water cases to public property source rows.

- [ ] **Step 4: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_water_parameter_cases.py -q
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/config/water_parameter_cases.yaml analyses/package_validation/explicit_association_toybox/scripts/water_parameter_cases.py analyses/package_validation/explicit_association_toybox/tests/test_water_parameter_cases.py analyses/package_validation/explicit_association_toybox/config/public_property_sources.yaml
git commit -m "feat: add water parameter case metadata"
```

## Task 7: Add Repeated Timing Harness

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/repeated_timing.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/render_figure.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_repeated_timing.py`

- [ ] **Step 1: Write failing timing tests**

Test that `summarize_repeated_timings` reports:

```text
closure_name
repeat_count
elapsed_median_seconds
elapsed_iqr_seconds
elapsed_min_seconds
elapsed_max_seconds
speedup_median
```

Use a tiny deterministic fake timing input for the unit test.

- [ ] **Step 2: Implement timing helper**

Implement repeated evaluation over a small configured subset of topology cases.
Use `time.perf_counter()` and default to a small repeat count suitable for
routine runs. Record exact baseline timing and closure timing separately.

- [ ] **Step 3: Add timing repeatability figure**

Write:

```text
figures/timing_repeatability/output/timing_repeatability.csv
figures/timing_repeatability/output/timing_repeatability_plotted_data.csv
figures/timing_repeatability/output/timing_repeatability.png
figures/timing_repeatability/output/timing_repeatability.mpl.yaml
```

- [ ] **Step 4: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_repeated_timing.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/render_figure.py
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox
git commit -m "feat: add repeated association closure timing"
```

## Task 8: Integrate Total `ares` Context From Issue 216

**Files:**
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/summarize_results.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`
- Modify: `analyses/package_validation/explicit_association_toybox/README.md`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`

- [ ] **Step 1: Check whether issue #216 has landed**

Run:

```powershell
Test-Path analyses/package_validation/explicit_association_toybox/scripts/hard_chain.py
Test-Path analyses/package_validation/explicit_association_toybox/scripts/dispersion.py
Test-Path analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py
```

Expected result: all return `True` before this task continues. If any return
`False`, resolve issue #216 first and return to this task after those files
exist.

- [ ] **Step 2: Write schema tests for total `ares` summaries**

Require retained summary rows to carry:

```text
ares_hc
ares_disp
ares_total_exact
ares_total_closure
ares_total_abs_error
ares_total_rel_error
```

- [ ] **Step 3: Add total `ares` columns to follow-up summaries**

Modify `summarize_results.py` so topology, sensitivity, and timing summaries
preserve total `ares` columns when the upstream figure CSV includes them.
Do not synthesize hard-chain or dispersion values in this task.

- [ ] **Step 4: Update README and analysis command index**

Add the new figure commands to `README.md` and `analysis.yaml` under the same
figure-owned command pattern already used by the toybox.

- [ ] **Step 5: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/summarize_results.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py analyses/package_validation/explicit_association_toybox/README.md analyses/package_validation/explicit_association_toybox/analysis.yaml
git commit -m "feat: carry total ares context through association summaries"
```

## Task 9: Final Documentation, Plot Review, And Validation

**Files:**
- Modify: `analyses/package_validation/explicit_association_toybox/README.md`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`

- [ ] **Step 1: Run all analysis tests**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
```

Expected result: all analysis-local tests pass.

- [ ] **Step 2: Regenerate every retained figure touched by this plan**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/render_figure.py
```

Expected result: each command exits successfully and retained PNG/CSV/YAML
outputs exist in the matching figure-owned `output` folder.

- [ ] **Step 3: Run repo structure and quick validation**

Run:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python scripts/dev/validate_project.py quick
```

Expected result: both commands pass.

- [ ] **Step 4: Run cleanup hook**

Run:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Expected result: no task-owned stale processes remain.

- [ ] **Step 5: Report plots and findings in chat**

In the completion response, render each new or updated PNG with absolute
filesystem paths and include compact Markdown tables from the retained plotted
data. Summarize the actual findings from the generated data, not only which
files changed.

- [ ] **Step 6: Commit final docs/index updates**

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/README.md analyses/package_validation/explicit_association_toybox/analysis.yaml
git commit -m "docs: document association follow-up analysis outputs"
```

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/render_figure.py`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Risk And Dependency Notes

- Task 8 depends on issue #216 or equivalent HC/dispersion files being present.
- Derivative smoothness diagnostics are analysis perturbation checks only. They should guide future production derivative discussions, not replace provider exact-derivative evidence.
- Timing evidence is Python-analysis evidence. It should be reported as comparative toybox timing, not provider runtime performance.
- Property residuals are fixed-state diagnostics and must not be described as VLE or vapor-pressure solving evidence.
- New plot completion reports must include actual rendered images and real tables in chat because root `AGENTS.md` now requires that for updated analysis plots.
