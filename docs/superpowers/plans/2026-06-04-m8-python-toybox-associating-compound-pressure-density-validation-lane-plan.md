# Associating-Compound Pressure Density Validation Lane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an associating-compound pressure-density validation lane with honest reference points and exact-implicit versus Picard model curves.

**Architecture:** Keep reference data, model rows, plotted snapshots, and rendered figures inside the explicit association toybox analysis. Use a toy pressure-density coupling layer only for analysis evidence and root proof; do not change provider density or pressure code.

**Tech Stack:** Python, NumPy, pandas/csv, Matplotlib, pytest.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane.md`
- Source Issue: `none`
- Source Plan: `docs/superpowers/plans/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane-plan.md`
- GitHub Issue: `none`
- Milestone: `M8 - Python Toybox`
- AFK/HITL: `HITL` because data provenance and root-selection plots need review.

## Dependencies

This is a root M8 toybox plan. It has no prerequisite M8 plan. It should run
before any pressure-weighted equilibrium relevance probe and before the final
explicit closure admission decision.

## Acceptance Criteria

- [ ] Only associating compounds appear in primary validation figures.
- [ ] Exact implicit and Picard model curves are plotted as dotted lines with distinct colors.
- [ ] Reference data are plotted as data markers and snapshotted into retained plotted-data files.
- [ ] Density root results include root status, branch, residual, bracket policy, and pressure evaluation count.
- [ ] Vapor-pressure, saturated-liquid-density, and pressure-density style figures are readable and do not use bar plots as primary evidence.
- [ ] No provider, equilibrium, benchmark, or public API files are changed.

## Tasks

### Task 1: Reference Data And Property Coupling Inputs

**Files:**
- Modify: `analyses/package_validation/explicit_association_toybox/config/public_property_sources.yaml`
- Modify: `analyses/package_validation/explicit_association_toybox/config/paper_systems.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/docs/saturation_property_validation_lane.md`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_public_property_sources.py`

- [ ] **Step 1: Write the failing tests**

Add assertions that every primary validation row has an associating topology,
source id, temperature, pressure, liquid density, parameter source, and
non-empty compound name.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_public_property_sources.py -q`

Expected before input cleanup: missing source metadata or validation-role
fields fail.

- [ ] **Step 3: Curate associating-only input metadata**

Keep pure associating compounds such as methanol, water, acetic acid,
alkanols, and amines when source rows are available. Move nonassociating
compounds out of the primary validation role or label them as inert controls in
documentation only.

- [ ] **Step 4: Run source tests**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_public_property_sources.py -q`

Expected: all source metadata tests pass.

- [ ] **Step 5: Commit**

Stage only the data/config/docs/test files in this task and commit with:
`analysis: curate associating property validation sources`

### Task 2: Toy Pressure-Density Coupling And Density Roots

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/toy_property_eos.py`
- Modify: `analyses/package_validation/explicit_association_toybox/scripts/fixed_state_property_residuals.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_toy_property_eos.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py`

- [ ] **Step 1: Write the failing tests**

Add tests for pressure at a fixed density, liquid-density root status, finite
compressibility terms, and explicit failure when a density root cannot be
bracketed.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_toy_property_eos.py analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py -q`

Expected before implementation: root/coupling helpers missing.

- [ ] **Step 3: Implement toy coupling**

Implement `DensityRootResult`, `ToyPropertyResult`, `pressure_result_from_state`,
`compressibility_terms`, and `solve_liquid_density_root`. Record root status
strings and never silently substitute a fake density.

- [ ] **Step 4: Run coupling tests**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_toy_property_eos.py analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py -q`

Expected: all coupling tests pass.

- [ ] **Step 5: Commit**

Stage only toy property coupling files and commit with:
`analysis: add toy pressure density coupling`

### Task 3: Pressure-Density Validation Figures

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/output/pressure_density_validation.csv`
- Create: `analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/output/pressure_density_validation_plotted_data.csv`
- Create: `analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/output/pressure_density_validation.png`
- Create: `analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/output/pressure_density_validation.svg`

- [ ] **Step 1: Generate model rows**

Run: `uv run python analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/scripts/generate_data.py`

Expected: retained rows include `model_name`, `density_root_status`,
`root_branch`, `model_pressure`, `model_liquid_density`, and reference data.

- [ ] **Step 2: Render readable figures**

Run: `uv run python analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/scripts/render_figure.py`

Expected: data markers for reference rows and dotted lines for exact implicit
and Picard model curves.

- [ ] **Step 3: Inspect plotted data**

Run: `uv run python -c "import pandas as pd; p='analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/output/pressure_density_validation_plotted_data.csv'; print(pd.read_csv(p).groupby(['compound','model_name']).size())"`

Expected: every plotted compound has reference, exact implicit, and Picard
rows.

- [ ] **Step 4: Commit**

Stage the pressure-density validation figure lane and commit with:
`analysis: add associating pressure density validation plots`

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_public_property_sources.py analyses/package_validation/explicit_association_toybox/tests/test_toy_property_eos.py analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/scripts/render_figure.py`
