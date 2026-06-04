---
issue: 227
title: "Add pure-component saturation pressure solver to Python toybox"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/227"
state: "open"
milestone: "M8 - Python Toybox"
project: "ePC-SAFT Roadmap"
package: "analysis"
capability: "property-validation"
backend: "python"
readiness: "ready"
release_target: "future"
source_spec: "docs/superpowers/specs/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver.md"
source_plan: "docs/superpowers/plans/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0227-add-pure-component-saturation-pressure-solver-to-python-toybox
last_synced: "2026-06-04"
---

# Add pure-component saturation pressure solver to Python toybox

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/227
**GitHub Milestone:** M8 - Python Toybox
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver.md
**Source Plan:** docs/superpowers/plans/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver-plan.md
**Branch:** codex/issue-0227-add-pure-component-saturation-pressure-solver-to-python-toybox
**AFK/HITL:** HITL
**Labels:** type:task, status:ready, ready-for-human, validation
**Goal Command:** None - HITL review required
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

Build a SciPy-backed pure-component saturation-pressure solver in the
explicit-association toybox so model curves are true vapor-pressure predictions
instead of fixed-state pressure residuals. Exact implicit association and
Picard must use the same coexistence solver path and differ only by the
association closure.

## Acceptance Criteria

- [ ] A pure-component SciPy saturation solver computes `P_sat`, vapor density, and liquid density from coexistence conditions rather than evaluating pressure only at experimental liquid density.
- [ ] Exact implicit association and Picard use the same saturation solver and differ only by the association closure.
- [ ] Retained data rows include reference vapor pressure, reference liquid density, model vapor pressure, model vapor/liquid density roots, residuals, solver status, iteration count, initial guess policy, parameter source, and source URL.
- [ ] Rendered figures use data markers for reference rows and dotted model curves for exact implicit and Picard.
- [ ] Solver failures are loud and classified; no fake density, pressure, or convergence defaults are written.
- [ ] No provider, equilibrium, benchmark, or public package API files are changed.

## Blocked by

- None

## Non-goals

- No provider API changes.
- No production equilibrium route changes.
- No new association closure candidates beyond the retained Picard closure.
- No fake saturation values or silent convergence defaults.

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/render_figure.py`
- `uv run python scripts/dev/validate_project.py quick`
