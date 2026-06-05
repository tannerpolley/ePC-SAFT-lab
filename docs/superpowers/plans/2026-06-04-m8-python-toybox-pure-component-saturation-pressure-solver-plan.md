# Pure-Component Saturation Pressure Solver For The Python Toybox Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a SciPy-backed pure-component saturation-pressure solver in the explicit-association toybox so model curves are true vapor-pressure predictions instead of fixed-state pressure residuals.

**Architecture:** Keep the solver, retained rows, plotted snapshots, and rendered figures inside the Python toybox analysis tree. Solve vapor and liquid density roots plus common saturation pressure using pressure equality and chemical-potential or fugacity equality for exact implicit association and Picard on the same solver path.

**Tech Stack:** Python, NumPy, SciPy, pandas/csv, Matplotlib, pytest.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver.md`
- Source Issue: `none`
- Source Plan: `docs/superpowers/plans/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver-plan.md`
- GitHub Issue: `none`
- Milestone: `M8 - Python Toybox`
- AFK/HITL: `HITL` because coexistence residual definitions and near-critical/root-failure labels need review before promotion.

## Dependencies

This is a root M8 toybox plan. It uses existing public saturation rows, toy PC-SAFT scalar terms, exact implicit association, and the retained Picard closure. It is not blocked by the M4 production route.

## Acceptance Criteria

- [ ] A pure-component SciPy saturation solver computes `P_sat`, vapor density, and liquid density from coexistence conditions rather than evaluating pressure only at experimental liquid density.
- [ ] Exact implicit association and Picard use the same saturation solver and differ only by the association closure.
- [ ] Retained data rows include reference vapor pressure, reference liquid density, model vapor pressure, model vapor/liquid density roots, residuals, solver status, iteration count, initial guess policy, parameter source, and source URL.
- [ ] Rendered figures use data markers for reference rows and dotted model curves for exact implicit and Picard.
- [ ] Solver failures are loud and classified; no fake density, pressure, or convergence defaults are written.
- [ ] No provider, equilibrium, benchmark, or public package API files are changed.

## Tasks

### Task 1: Coexistence Solver Contract

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/pure_saturation.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py`

- [ ] **Step 1: Write the failing tests**

Add tests for a pure-component solve result schema, pressure equality residuals,
chemical-potential or fugacity equality residuals, strict vapor density below
liquid density, and loud failure when a two-root bracket cannot be found.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py -q`

Expected before implementation: imports or solver functions are missing.

- [ ] **Step 3: Implement the minimal solver**

Implement a `PureSaturationResult` shape and `solve_pure_saturation(...)` using
SciPy. Use local variables such as `log_rho_v`, `log_rho_l`, and `log_p_sat`,
and residuals equivalent to `P_v - P_sat`, `P_l - P_sat`, and `mu_v - mu_l`.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py -q`

- [ ] **Step 5: Commit**

Stage only the solver and solver contract tests. Commit with:
`analysis: add toy pure saturation solver`

### Task 2: Exact-vs-Picard Saturation Data Generation

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/output/pure_saturation_validation.csv`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py`

- [ ] **Step 1: Write retained-row tests**

Assert that generated rows include `component`, `T_K`, `reference_p_sat_Pa`,
`reference_rho_liq_mol_m3`, `closure_name`, `model_p_sat_Pa`,
`model_rho_vap_mol_m3`, `model_rho_liq_mol_m3`, residuals, solver status,
iteration count, initial guess policy, parameter source, and source URL.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py -q`

Expected before generation: retained output path or required columns are
missing.

- [ ] **Step 3: Implement data generation**

Read `data/reference/pure_component/saturation_density/water_methanol_nist_saturation.csv`
and provider cases. Write
one reference row plus exact implicit and Picard model rows for each retained
pure associating compound/temperature case.

- [ ] **Step 4: Run generation and tests**

Run:
`uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py`

Then:
`uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py -q`

- [ ] **Step 5: Commit**

Stage the generation script, output CSV, and tests. Commit with:
`analysis: generate pure saturation validation rows`

### Task 3: Saturation Validation Figures

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/output/pure_saturation_validation_plotted_data.csv`
- Create: `analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/output/pure_saturation_validation.png`
- Create: `analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/output/pure_saturation_validation.svg`
- Create: `analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/output/pure_saturation_validation.mpl.yaml`

- [ ] **Step 1: Render the first figure**

Run:
`uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/render_figure.py`

Expected: reference data are markers and exact implicit/Picard are dotted
curves for vapor pressure and saturated liquid density.

- [ ] **Step 2: Inspect plotted data**

Run:
`uv run python -c "import pandas as pd; p='analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/output/pure_saturation_validation_plotted_data.csv'; print(pd.read_csv(p).groupby(['component','closure_name']).size())"`

Expected: each component has reference, exact implicit, and Picard plotted rows
or a loud solver-failure row retained outside the primary curve.

- [ ] **Step 3: Commit**

Stage only the figure lane files. Commit with:
`analysis: render pure saturation validation plots`

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/render_figure.py`
- `uv run python scripts/dev/validate_project.py quick`
