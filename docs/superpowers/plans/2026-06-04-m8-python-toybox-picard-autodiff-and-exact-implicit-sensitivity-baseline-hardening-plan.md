# Picard Autodiff And Exact Implicit Sensitivity Baseline Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python-only derivative evidence lane comparing exact implicit association sensitivities with JAX derivatives of the retained Picard reduced model.

**Architecture:** Keep the work inside `analyses/package_validation/explicit_association_toybox`. Implement exact implicit first-derivative baselines, JAX Picard first/second derivatives, and Hessian agreement summaries as analysis scripts with figure-local retained outputs. Do not move any logic into package source.

**Tech Stack:** Python, NumPy, optional analysis-only JAX, pandas/csv, Matplotlib, pytest.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening.md`
- Source Issue: `none`
- Source Plan: `docs/superpowers/plans/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening-plan.md`
- GitHub Issue: `none`
- Milestone: `M8 - Python Toybox`
- AFK/HITL: `HITL` because JAX dependency policy and derivative tolerances may need review after first evidence.

## Dependencies

This is a root M8 toybox plan. It has no prerequisite M8 plan. It should run
before the explicit closure admission decision plan and before the equilibrium
relevance probe plan.

## Acceptance Criteria

- [ ] Exact implicit first-derivative sensitivity rows exist for density, strength, and binary composition perturbations.
- [ ] JAX Picard rows exist for matching first and second derivative targets.
- [ ] Hessian agreement output reports exact implicit or finite-difference baselines against Picard JAX Hessian entries.
- [ ] Retained output rows include case id, closure, target, derivative order, exact value, Picard value, absolute error, relative error, backend, and baseline status.
- [ ] Analysis-local tests cover mass-action Jacobian shape, implicit sensitivity residuals, JAX derivative output schema, and Hessian agreement schema.
- [ ] No provider, equilibrium, benchmark, or public API files are changed.

## Tasks

### Task 1: Exact Implicit Sensitivity Baseline

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/implicit_sensitivity.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_implicit_sensitivity.py`

- [ ] **Step 1: Write the failing tests**

Add tests for `mass_action_jacobian`, density sensitivity, strength sensitivity, and binary composition sensitivity. Include one assertion that `mass_action_residual_inf <= 1e-10` for the solved baseline.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_implicit_sensitivity.py -q`

Expected before implementation: imports or functions missing.

- [ ] **Step 3: Implement exact first-derivative helpers**

Implement `ImplicitSensitivityResult`, `mass_action_jacobian`, `exact_density_sensitivity`, `exact_strength_sensitivity`, and `exact_binary_composition_sensitivity`. Use `np.linalg.solve` on the residual Jacobian and fail loudly for non-finite density, strength, composition, or shape mismatches.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_implicit_sensitivity.py -q`

Expected after implementation: all tests pass.

- [ ] **Step 5: Commit**

Stage only the two files in this task and commit with: `analysis: add implicit association sensitivity baseline`

### Task 2: JAX Picard Derivative Lane

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/jax_picard_derivatives.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/output/jax_picard_derivatives.csv`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_jax_picard_derivatives.py`

- [ ] **Step 1: Write the failing tests**

Add tests that call `run_jax_picard_derivative_cases()` and assert retained columns:
`case_id`, `closure_name`, `target`, `derivative_order`, `exact_implicit_value`,
`picard_jax_value`, `abs_error`, `rel_error`, `autodiff_backend`, and
`exact_baseline`.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_jax_picard_derivatives.py -q`

Expected before implementation: JAX lane functions missing.

- [ ] **Step 3: Implement JAX derivative generation**

Implement JAX x64 Picard scalar evaluation and derivative rows for density,
strength, density-density, density-strength, strength-strength, and binary
composition targets when the system has two components. Raise a clear
`ModuleNotFoundError` that says `JAX is required for the autodiff lane` when
JAX is unavailable.

- [ ] **Step 4: Generate retained rows and render the figure**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/scripts/render_figure.py
```

Expected: CSV, plotted-data CSV, PNG, SVG, and PDF LaTeX artifact are written under
`figures/jax_picard_derivatives/output`.

- [ ] **Step 5: Commit**

Stage only this lane's script, test, and figure output files and commit with:
`analysis: add JAX Picard derivative lane`

### Task 3: Hessian Agreement Lane

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/hessian_agreement.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/render_figure.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_hessian_agreement.py`

- [ ] **Step 1: Write the failing tests**

Add tests that verify Hessian rows contain `target_pair`,
`exact_hessian_value`, `picard_jax_hessian_value`, `absolute_error`,
`relative_error`, and `baseline_status`.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_hessian_agreement.py -q`

Expected before implementation: Hessian helpers missing.

- [ ] **Step 3: Implement Hessian comparison**

Implement a small centered finite-difference exact baseline for second
derivatives when an analytic implicit second derivative is not present. Record
the baseline as `centered_finite_difference_exact_implicit` and include the
finite-difference step in each row.

- [ ] **Step 4: Generate and render**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/render_figure.py
```

Expected: retained Hessian rows and a readable error figure are produced.

- [ ] **Step 5: Commit**

Stage only Hessian lane files and commit with:
`analysis: compare Picard Hessians to exact baseline`

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_implicit_sensitivity.py analyses/package_validation/explicit_association_toybox/tests/test_jax_picard_derivatives.py analyses/package_validation/explicit_association_toybox/tests/test_hessian_agreement.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/render_figure.py`
