---
issue: 221
title: "Harden Picard autodiff and exact implicit sensitivity baselines in Python toybox"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/221"
state: "open"
milestone: "M8 - Python Toybox"
project: "ePC-SAFT Roadmap"
package: "analysis"
capability: "explicit-association-toybox"
backend: "python"
readiness: "ready"
release_target: "future"
source_spec: "docs/superpowers/specs/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening.md"
source_plan: "docs/superpowers/plans/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening-plan.md"
afk_hitl: "AFK"
last_synced: "2026-06-04"
---

# Harden Picard autodiff and exact implicit sensitivity baselines in Python toybox

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/221
**GitHub Milestone:** M8 - Python Toybox
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening.md
**Source Plan:** docs/superpowers/plans/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening-plan.md
**Classification:** AFK
**Labels:** type:task, status:ready, agent-ready, validation, area:derivatives
**Goal Command:** /goal Resolve issue 221: harden the Python toybox Picard autodiff and exact implicit sensitivity baseline lane according to docs/superpowers/plans/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening-plan.md, preserving analysis-only scope and passing the listed proof oracle.
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

Build a Python-only derivative evidence lane comparing exact implicit
association sensitivities with JAX derivatives of the retained Picard reduced
model. Keep the work inside
`analyses/package_validation/explicit_association_toybox` and do not move logic
into provider, equilibrium, benchmark, or public API code.

## Acceptance Criteria

- [ ] Exact implicit first-derivative sensitivity rows exist for density, strength, and binary composition perturbations.
- [ ] JAX Picard rows exist for matching first and second derivative targets.
- [ ] Hessian agreement output reports exact implicit or finite-difference baselines against Picard JAX Hessian entries.
- [ ] Retained output rows include case id, closure, target, derivative order, exact value, Picard value, absolute error, relative error, backend, and baseline status.
- [ ] Analysis-local tests cover mass-action Jacobian shape, implicit sensitivity residuals, JAX derivative output schema, and Hessian agreement schema.
- [ ] No provider, equilibrium, benchmark, or public API files are changed.

## Blocked by

- None

## Non-goals

- No provider EOS implementation.
- No equilibrium package implementation.
- No benchmark promotion or public capability claim.

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_implicit_sensitivity.py analyses/package_validation/explicit_association_toybox/tests/test_jax_picard_derivatives.py analyses/package_validation/explicit_association_toybox/tests/test_hessian_agreement.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/render_figure.py`
