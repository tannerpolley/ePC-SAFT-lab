# Evaluate Picard explicit association step and damping policy grid Implementation Plan

**Source:** https://github.com/ePC-SAFT/ePC-SAFT/issues/231
**Source Spec:** docs/superpowers/specs/2026-06-04-m8-python-toybox-picard-step-damping-policy-grid.md

## Goal

Evaluate fixed-depth damped Picard association policies in the Python-only toybox across step counts and damping values, then produce retained evidence and a C++/CppAD stress-test handoff matrix. The closure must remain a deterministic unrolled expression selected before evaluation starts; it must not become an adaptive solve.

## Scope

- Work only under `analyses/package_validation/explicit_association_toybox/**` plus the local M8 issue/plan artifacts needed for this issue.
- Use exact implicit mass action as the baseline for site fractions, residuals, property proxies, derivative targets, timing, and handoff tolerances.
- Treat step count and damping as Picard policy settings, not new approximation families.
- Do not change provider, equilibrium, regression, public API, or package capability behavior.

## Implementation Tasks

### Task 1: Deterministic Picard Policy API

- Add a small immutable Picard policy value with fixed `step_count` and `damping`.
- Keep the existing retained `PICARD7_CLOSURE` path behavior-compatible.
- Expose a policy grid with step counts `3`, `5`, `7`, `9`, `11` and damping values `0.35`, `0.5`, `0.65`, `0.8`, `1.0`.
- Ensure evaluation receives the policy before computing site fractions and performs a fixed unrolled loop.

### Task 2: Policy Grid Evidence Rows

- Add a script that evaluates every policy against representative case-matrix rows.
- Include cases covering pure/self association, `2B`, `3B`, `4C`, water-like strong association, cross-association/asymmetric binaries, mixed topologies, and association strength variation.
- Retain rows with at least:
  - case id and topology;
  - step count and damping;
  - exact implicit iteration count;
  - site-fraction error;
  - mass-action residual norm;
  - `a_assoc` absolute/relative error;
  - pressure/proxy/property error;
  - derivative and Hessian/Jacobian error summaries where available;
  - median runtime;
  - graph-depth or evaluation-cost proxy;
  - Pareto band.

### Task 3: Ranking And Handoff Matrix

- Rank rows by Pareto behavior, not one scalar score.
- Produce candidate policy labels for fast, balanced, and high-accuracy lanes when the evidence supports them.
- Emit a C++/CppAD handoff CSV or Markdown matrix with case names, variables, expected derivative orders, tolerances, and failure modes.

### Task 4: Render Evidence

- Add or update readable plot artifacts showing direct policy comparisons.
- Follow repo plotting rules: no bar plots when line/point comparisons are clearer, readable labels, retained plotted-data CSVs, and honest captions.
- Include exact implicit baseline rows in retained data and summarize retained data in chat/handoff.

### Task 5: Validation

- Add focused tests for policy-grid construction, deterministic policy evaluation, retained schema, and generated handoff matrix.
- Run the issue proof oracle and `validate_project.py quick`.

## Issue Metadata

**GitHub Milestone:** M8 - Python Toybox
**Issue Type:** task
**Classification:** AFK
**Labels:** type:task, status:ready, agent-ready, area:derivatives, backend:cppad, validation
**Goal Command:** /goal evaluate the Picard explicit association step/damping policy grid in the Python toybox and produce a CppAD stress-test handoff matrix

## What To Build

Extend the Python-only explicit-association toybox so the Picard closure is tested as a deterministic model-option policy family rather than one fixed `7` step, `lambda = 0.5` variant.

The key design rule is that the Picard step count and damping value are selected before evaluation starts. The traced/evaluated expression must remain a fixed finite unrolled computation, not an adaptive convergence loop with runtime branches.

Test the policy grid across association types and accuracy requirements so the project can decide when lower depth, such as `5` steps, is acceptable and when higher depth, such as `9` or `11` steps, is worth the extra autodiff cost.

## Acceptance Criteria

- [ ] The toybox exposes deterministic Picard policy options for fixed step count and damping value, selected before any evaluation begins.
- [ ] The retained grid covers step counts `3`, `5`, `7`, `9`, and `11` and damping values including at least `0.35`, `0.5`, `0.65`, `0.8`, and `1.0`, unless the implementation records a source-backed reason to adjust the grid.
- [ ] The grid includes exact implicit association as the timing, residual, property, and derivative baseline.
- [ ] The cases cover weak/self-association, moderate `2B`/`3B`/`4C`, strong water-like association, asymmetric binary/cross-association behavior, and varied association-strength or binary parameters such as `k_hb` and `l_ij` where the toybox supports them.
- [ ] Metrics include site-fraction error, mass-action residual, `a_assoc` error, total-EOS/property propagation error, pressure-density behavior, first-derivative agreement, Hessian/Jacobian agreement, median runtime, and an autodiff graph-depth or evaluation-cost proxy.
- [ ] Results are ranked by Pareto behavior, not a single scalar score, and identify candidate policies such as fast, balanced, and high-accuracy modes.
- [ ] The work produces a reusable C++ CppAD stress-test handoff matrix naming cases, variables, expected derivative orders, tolerances, and failure modes, without changing provider EOS implementation in this issue.
- [ ] Updated plots follow the repo plotting rules: readable axes, direct data/line comparisons where useful, retained data tables, and no unsupported model-fit claims.

## Non-goals

- No provider EOS implementation or public API change.
- No equilibrium package implementation.
- No adaptive convergence branch inside the Picard closure expression.
- No promotion of Picard to provider production support from toybox evidence alone.
- No release-quality validation claim; this is exploratory M8 evidence that can feed later M3/M4/M6 issues.

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_association_case_matrix.py analyses/package_validation/explicit_association_toybox/tests/test_amortized_timing.py analyses/package_validation/explicit_association_toybox/tests/test_jax_picard_derivatives.py analyses/package_validation/explicit_association_toybox/tests/test_hessian_agreement.py analyses/package_validation/explicit_association_toybox/tests/test_cppad_shaped_picard_derivative_evidence.py analyses/package_validation/explicit_association_toybox/tests/test_cppad_shaped_picard_property_evidence.py -q`
- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/scripts/association_case_matrix.py`
- `uv run python analyses/package_validation/explicit_association_toybox/scripts/amortized_timing.py`
- `uv run python analyses/package_validation/explicit_association_toybox/scripts/jax_picard_derivatives.py`
- `uv run python analyses/package_validation/explicit_association_toybox/scripts/hessian_agreement.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_policy_grid/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_policy_grid/scripts/render_figure.py`
- `uv run python scripts/dev/validate_project.py quick`

## Verification

Run the proof oracle recorded in the hydrated issue mirror.
