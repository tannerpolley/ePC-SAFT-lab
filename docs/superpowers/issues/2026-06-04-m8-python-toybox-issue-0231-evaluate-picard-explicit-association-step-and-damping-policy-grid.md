---
issue: 231
title: "Evaluate Picard explicit association step and damping policy grid"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/231"
state: "open"
milestone: "M8 - Python Toybox"
project: "ePC-SAFT Roadmap"
package: "analysis"
capability: "explicit-association-toybox"
backend: "python"
readiness: "ready"
release_target: "future"
source_spec: "docs/superpowers/specs/2026-06-04-m8-python-toybox-picard-step-damping-policy-grid.md"
source_plan: "docs/superpowers/plans/2026-06-04-m8-python-toybox-picard-step-damping-policy-grid-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0231-evaluate-picard-step-damping-policy-grid
last_synced: "2026-06-04"
---

# Evaluate Picard explicit association step and damping policy grid

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/231
**GitHub Milestone:** M8 - Python Toybox
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-04-m8-python-toybox-picard-step-damping-policy-grid.md
**Source Plan:** docs/superpowers/plans/2026-06-04-m8-python-toybox-picard-step-damping-policy-grid-plan.md
**Classification:** AFK
**AFK/HITL:** AFK
**Branch:** codex/issue-0231-evaluate-picard-step-damping-policy-grid
**Labels:** type:task, status:ready, agent-ready, area:derivatives, backend:cppad, validation
**Goal Command:** /goal evaluate the Picard explicit association step/damping policy grid in the Python toybox and produce a CppAD stress-test handoff matrix
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

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

## Blocked by

- None

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
