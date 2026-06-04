# Equilibrium Relevance Probe For Picard Closure Error Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python-only objective, Jacobian, and Hessian probe that tests whether Picard closure error is dangerous for later equilibrium NLP work.

**Architecture:** Keep the probe inside the explicit association toybox and consume provider-like local EOS quantities. Do not create route APIs, Ipopt integrations, HELD/GFPE behavior, or M4 package code.

**Tech Stack:** Python, NumPy, optional analysis-only JAX, CSV, Matplotlib, pytest.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error.md`
- Source Issue: `none`
- Source Plan: `docs/superpowers/plans/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error-plan.md`
- GitHub Issue: `none`
- Milestone: `M8 - Python Toybox`
- AFK/HITL: `HITL` because the objective form and failure thresholds are scientific design choices.

## Dependencies

This plan should run after:

- `docs/superpowers/plans/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening-plan.md`
- `docs/superpowers/plans/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane-plan.md`

It should consume admission thresholds from
`docs/superpowers/plans/2026-06-04-m8-python-toybox-explicit-closure-admission-decision-plan.md`
when those thresholds already exist. If they do not exist, this plan must emit
`blocked_by_missing_derivative_baseline` or `needs_more_evidence` status rather
than manufacturing an equilibrium-readiness claim.

## Acceptance Criteria

- [ ] The probe uses neutral objective names such as `local_objective`, not bubble, dew, flash, LLE, HELD, or GFPE route names.
- [ ] Exact implicit and Picard objective values are compared for the same toybox cases.
- [ ] Gradient and Hessian error norms are retained with admission status bands.
- [ ] The probe reports blocked status when derivative baseline rows are missing.
- [ ] No provider, equilibrium, benchmark, or public API files are changed.

## Tasks

### Task 1: Local Objective Definition

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/quick_phase_equilibrium.py`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_quick_phase_equilibrium.py`

- [ ] **Step 1: Write failing objective tests**

Add tests for `reduced_chemical_potential`, `solve_pure_phase_pair`, and a
small objective row generator. Assert that no public route names appear in row
metadata.

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_quick_phase_equilibrium.py -q`

Expected before implementation: objective helpers missing.

- [ ] **Step 3: Implement the local objective probe**

Implement a pure analysis residual using pressure-like and reduced-chemical
potential-like quantities from `toy_property_eos.py`. Use status strings for
convergence, singular linearization, iteration limit, and invalid density
bounds.

- [ ] **Step 4: Run objective tests**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_quick_phase_equilibrium.py -q`

Expected: tests pass without route-name leakage.

- [ ] **Step 5: Commit**

Stage only objective probe files and commit with:
`analysis: add local equilibrium relevance probe`

### Task 2: Objective Derivative Error Rows

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/output/equilibrium_relevance_probe.csv`
- Create: `analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/output/equilibrium_relevance_probe_plotted_data.csv`
- Test: `analyses/package_validation/explicit_association_toybox/tests/test_quick_phase_equilibrium.py`

- [ ] **Step 1: Add output schema tests**

Assert retained rows include `objective_value_exact`,
`objective_value_picard`, `gradient_absolute_error_norm`,
`hessian_absolute_error_norm`, `picard_mass_action_residual_norm`, and
`admission_status`.

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_quick_phase_equilibrium.py -q`

Expected before row generation: output schema functions missing.

- [ ] **Step 3: Generate exact-vs-Picard rows**

Use derivative baseline outputs when present. When they are absent, emit rows
with `admission_status = blocked_by_missing_derivative_baseline` rather than
fake derivative values.

- [ ] **Step 4: Render probe figure**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/scripts/render_figure.py
```

Expected: a readable figure compares objective, gradient, and Hessian error
bands without route labels.

- [ ] **Step 5: Commit**

Stage only equilibrium relevance probe figure files and commit with:
`analysis: render Picard equilibrium relevance probe`

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_quick_phase_equilibrium.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/scripts/render_figure.py`
- `rg -n "bubble|dew|flash|LLE|HELD|GFPE" analyses/package_validation/explicit_association_toybox/scripts/quick_phase_equilibrium.py analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe`
