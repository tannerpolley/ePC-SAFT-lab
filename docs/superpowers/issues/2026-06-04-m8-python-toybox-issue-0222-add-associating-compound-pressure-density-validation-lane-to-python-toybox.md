---
issue: 222
title: "Add associating-compound pressure-density validation lane to Python toybox"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/222"
state: "open"
milestone: "M8 - Python Toybox"
project: "ePC-SAFT Roadmap"
package: "analysis"
capability: "explicit-association-toybox"
backend: "python"
readiness: "needs design"
release_target: "future"
source_spec: "docs/superpowers/specs/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane.md"
source_plan: "docs/superpowers/plans/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane-plan.md"
afk_hitl: "HITL"
last_synced: "2026-06-04"
---

# Add associating-compound pressure-density validation lane to Python toybox

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/222
**GitHub Milestone:** M8 - Python Toybox
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane.md
**Source Plan:** docs/superpowers/plans/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane-plan.md
**Classification:** HITL
**Labels:** type:task, status:needs-design, ready-for-human, validation, area:benchmark
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

Build an associating-compound pressure-density validation lane with honest
reference data points and exact-implicit versus Picard model curves. Use
toybox-only pressure-density coupling and root evidence; do not change provider
pressure, density, or equilibrium code.

## Acceptance Criteria

- [ ] Only associating compounds appear in primary validation figures.
- [ ] Exact implicit and Picard model curves are plotted as dotted lines with distinct colors.
- [ ] Reference data are plotted as data markers and snapshotted into retained plotted-data files.
- [ ] Density root results include root status, branch, residual, bracket policy, and pressure evaluation count.
- [ ] Vapor-pressure, saturated-liquid-density, and pressure-density style figures are readable and do not use bar plots as primary evidence.
- [ ] No provider, equilibrium, benchmark, or public API files are changed.

## Blocked by

- None

## Non-goals

- No provider pressure-density solver changes.
- No benchmark promotion.
- No nonassociating compounds in primary validation figures.

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_public_property_sources.py analyses/package_validation/explicit_association_toybox/tests/test_toy_property_eos.py analyses/package_validation/explicit_association_toybox/tests/test_fixed_state_property_residuals.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pressure_density_validation/scripts/render_figure.py`
