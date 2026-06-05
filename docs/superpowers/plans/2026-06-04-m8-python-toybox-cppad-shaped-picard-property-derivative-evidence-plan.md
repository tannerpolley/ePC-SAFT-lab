# CppAD-Shaped Picard Property And Derivative Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Python-only evidence lanes that compare retained Picard association behavior across property grids and C++/CppAD-shaped autodiff derivative blocks.

**Architecture:** Keep all work inside `analyses/package_validation/explicit_association_toybox`. Add a reusable case-matrix generator, one property/association evidence figure lane, and one derivative evidence figure lane that compares NumPy Picard, JAX Picard, and exact implicit baselines where available. The outputs remain analysis artifacts and do not change provider or equilibrium package behavior.

**Tech Stack:** Python, NumPy, SciPy for toybox solves, optional analysis-only JAX, pandas/csv, Matplotlib, pytest.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-04-m8-python-toybox-cppad-shaped-picard-property-derivative-evidence.md`
- Source Issue: `none`
- Source Plan: `docs/superpowers/plans/2026-06-04-m8-python-toybox-cppad-shaped-picard-property-derivative-evidence-plan.md`
- GitHub Issue: `none`
- Milestone: `M8 - Python Toybox`
- Package Ownership: `analysis`
- AFK/HITL: `HITL` because topology coverage, derivative tolerances, and CppAD relevance interpretation need review after first retained evidence.

## Dependencies

This plan builds on:

- `docs/superpowers/plans/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening-plan.md`
- `docs/superpowers/plans/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver-plan.md`
- `docs/superpowers/plans/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error-plan.md`

It should run before any new provider admission issue for explicit association
or any M4 issue that assumes Picard derivative quality.

## Acceptance Criteria

- [ ] A reusable association case matrix covers pure and mixture association schemes without reintroducing retired closure families.
- [ ] Property evidence rows compare exact implicit, Picard NumPy, and Picard JAX values for association energy, total residual Helmholtz proxy, pressure, density-root status, and fugacity-like proxies where available.
- [ ] Derivative evidence rows compare JAX Picard Jacobians, gradients, Hessians or Hessian-vector products against exact implicit sensitivity or finite-difference baselines where feasible.
- [ ] Local quadratic/trust-region model diagnostics report whether Picard curvature error would distort a Newton, SQP, or trust-region step in small objective proxies.
- [ ] Retained rows explicitly label JAX as a CppAD proxy, not CppAD proof.
- [ ] Figures use readable pressure/density/property curves with data points and dotted model lines, not bar plots.
- [ ] Tests cover schema, topology coverage, backend agreement, and derivative evidence sanity.
- [ ] No provider, equilibrium, regression, public API, or package dependency files are changed.

## Non-Goals

- No provider C++ or CppAD implementation.
- No production equilibrium route behavior.
- No benchmark admission.
- No Python Ipopt dependency requirement.
- No public API change.
- No old closure-family resurrection.

## Tasks

### Task 1: Association Case Matrix

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/association_case_matrix.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_association_case_matrix.py`

- [ ] **Step 1: Write the failing tests**

Add tests that require pure and mixture cases for:
`pure_nonassociating_control`, `pure_one_site`, `pure_2b_self`,
`pure_3b_or_4c_labeled`, `inert_plus_associating_binary`,
`two_self_associating_binary`, `cross_associating_binary`,
`asymmetric_donor_acceptor_binary`, and `water_like_topology_fork`.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_association_case_matrix.py -q
```

Expected before implementation: the case matrix module or required cases are
missing.

- [ ] **Step 3: Implement the case matrix**

Implement typed case dictionaries or dataclasses with explicit topology labels,
component-family labels, composition grids, density grids, temperature grids,
and association-strength matrices. Keep mathematically useful but
non-source-backed cases labeled as synthetic. Do not introduce any retired
closure-family names.

- [ ] **Step 4: Run the tests and verify they pass**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_association_case_matrix.py -q
```

- [ ] **Step 5: Commit**

Stage only this task's files and commit with:
`analysis: add Picard association case matrix`

### Task 2: Property And Association Evidence Lane

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/cppad_shaped_property_evidence.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/output/cppad_shaped_picard_property_evidence.csv`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_cppad_shaped_picard_property_evidence.py`

- [ ] **Step 1: Write the failing tests**

Add tests that assert retained output columns:
`case_id`, `topology_id`, `component_family`, `mixture_family`,
`temperature`, `density`, `composition`, `picard_backend`,
`association_helmholtz_exact`, `association_helmholtz_picard`,
`pressure_exact`, `pressure_picard`, `density_root_status`,
`mass_action_residual_norm`, `absolute_error`, and `relative_error`.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_cppad_shaped_picard_property_evidence.py -q
```

Expected before implementation: evidence generator functions are missing.

- [ ] **Step 3: Implement retained evidence rows**

Use the case matrix to evaluate exact implicit association, Picard NumPy, and
Picard JAX when the JAX import succeeds. Compare association Helmholtz energy,
total residual Helmholtz proxy when present, pressure proxy, fugacity-like proxy
when present, density root status, and mass-action residual norms. Record the
real import result plainly instead of substituting rows that did not run.

- [ ] **Step 4: Generate and render readable figures**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/scripts/render_figure.py
```

Expected: retained CSV, plotted-data CSV, PNG, SVG, and MPL sidecar under
`figures/cppad_shaped_picard_property_evidence/output`. Figures use point data
and dotted model curves; no bar plots.

- [ ] **Step 5: Commit**

Stage only this lane's files and commit with:
`analysis: add CppAD-shaped Picard property evidence`

### Task 3: Derivative Evidence Lane

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/cppad_shaped_derivative_evidence.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/output/cppad_shaped_picard_derivative_evidence.csv`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_cppad_shaped_picard_derivative_evidence.py`

- [ ] **Step 1: Write the failing tests**

Add tests that assert retained output columns:
`case_id`, `topology_id`, `target`, `variable_block`, `derivative_order`,
`backend`, `exact_implicit_value`, `picard_numpy_value`, `picard_jax_value`,
`absolute_error`, `relative_error`, `autodiff_status`, `cppad_relevance_note`,
and `admission_band`.

- [ ] **Step 2: Run the tests and verify the expected failure**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_cppad_shaped_picard_derivative_evidence.py -q
```

Expected before implementation: derivative evidence module or retained columns
are missing.

- [ ] **Step 3: Implement JAX derivative evidence**

Evaluate JAX Jacobians, gradients, Hessians, and selected Hessian-vector
products for small fixed variable blocks. Targets should include `a_assoc`,
total residual Helmholtz proxy, pressure proxy, saturation residuals, fugacity
or chemical-potential-like composition proxies, and association-strength
parameters. Compare against exact implicit sensitivity rows or centered
finite-difference exact implicit baselines when analytic second derivatives
are not present.

Also compute a small local quadratic model error for selected objective
proxies:

```text
m(p) = f(x) + g(x)^T p + 1/2 p^T H(x) p
```

Compare the exact-implicit and Picard-JAX quadratic predictions for identical
trial steps. Keep this as a curvature diagnostic for future Newton, SQP, or
trust-region behavior; do not introduce a production trust-region solver.

- [ ] **Step 4: Generate and render derivative figures**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/scripts/render_figure.py
```

Expected: retained CSV, plotted-data CSV, PNG, SVG, and MPL sidecar under
`figures/cppad_shaped_picard_derivative_evidence/output`. Figures separate
value, first-derivative, and Hessian evidence instead of hiding everything in
one aggregate score. The Hessian panel should include local quadratic model
error when that diagnostic is generated.

- [ ] **Step 5: Commit**

Stage only this lane's files and commit with:
`analysis: add CppAD-shaped Picard derivative evidence`

### Task 4: Summary And Admission Interpretation

**Files:**
- Modify: `analyses/package_validation/explicit_association_toybox/README.md`
- Modify: `docs/superpowers/specs/2026-06-04-m8-python-toybox-explicit-closure-admission-decision.md`
- Modify: `docs/superpowers/plans/2026-06-04-m8-python-toybox-explicit-closure-admission-decision-plan.md`

- [ ] **Step 1: Summarize retained evidence**

Add a compact analysis summary that separates property agreement, derivative
agreement, backend agreement, and CppAD relevance risk.

- [ ] **Step 2: Update admission inputs**

Link the new property and derivative evidence lanes into the explicit closure
admission decision materials. Preserve the rule that M8 evidence cannot by
itself create provider capability claims.

- [ ] **Step 3: Validate docs and analysis layout**

Run:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
```

- [ ] **Step 4: Commit**

Stage only summary and admission-linking docs and commit with:
`docs: summarize CppAD-shaped Picard evidence`

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_association_case_matrix.py analyses/package_validation/explicit_association_toybox/tests/test_cppad_shaped_picard_property_evidence.py analyses/package_validation/explicit_association_toybox/tests/test_cppad_shaped_picard_derivative_evidence.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/scripts/render_figure.py`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_package_extension_boundary.py -q`
- `uv run python scripts/dev/validate_project.py quick`

## Risk Notes

- JAX agreement is not CppAD proof. The retained rows must say this directly so
  later agents do not cite M8 as production derivative evidence.
- Full Hessians can become noisy or expensive. Prefer selected full Hessians for
  small cases and Hessian-vector products for larger variable blocks.
- Trust-region wording is diagnostic only. It explains why curvature quality
  matters for future optimization, not a decision to add a trust-region solver
  to the toybox or packages.
- Topology coverage must stay honest. Synthetic topology cases are useful for
  math stress but cannot be presented as source-backed compound validation.
- Iteration-count or damping sensitivity rows can help diagnose the fixed-point
  reduction, but they must not be framed as separate closure candidates.
