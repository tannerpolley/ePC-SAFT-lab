---
issue: 220
title: "Prove explicit association closure derivative and property propagation evidence"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/220"
state: "open"
milestone: "M3 - EOS"
project: "ePC-SAFT Roadmap"
package: "epcsaft"
capability: "explicit-association-analysis"
backend: "python"
readiness: "agent-ready"
release_target: null
source_spec: "docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence.md"
source_plan: "docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence-plan.md"
afk_hitl: "AFK"
branch: "codex/issue-0220-prove-explicit-association-closure-derivative-and-property-propagation-evidence"
last_synced: "2026-06-03"
---

# Prove explicit association closure derivative and property propagation evidence

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/220
**GitHub Milestone:** M3 - EOS
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence.md
**Source Plan:** docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence-plan.md
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** type:task, status:ready, agent-ready, area:core, area:derivatives, validation
**Goal Command:** /goal Implement GitHub issue 220 using docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence-plan.md; keep all work under analyses/package_validation/explicit_association_toybox; validate the proof oracle; report every new plot inline with retained-data tables.
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

Extend the Python-only explicit association toybox with one M3 analysis slice that compares exact implicit association against explicit closure candidates after propagation into local derivatives, pressure-like properties, chemical-potential-like sensitivities, fugacity-like proxies, water topology diagnostics, and a route-free local objective sensitivity diagnostic.

## Acceptance Criteria

- [ ] Amortized timing output retains exact implicit median elapsed time, exact implicit IQR, exact implicit iteration count, closure median elapsed time, closure IQR, and speedup by topology and site count.
- [ ] Derivative-agreement output compares exact implicit and explicit closures for `a_assoc`, pressure proxy, composition sensitivity, and chemical-potential-like or fugacity-like proxy targets.
- [ ] Asymmetric binary outputs include one associating plus one inert component, two associating components with cross association, unequal `Delta` strength, non-50/50 composition, and at least one water-like 3B/4C contrast row.
- [ ] Total EOS impact output ranks closures by `ares_assoc` error, total `ares` error, pressure proxy error, chemical-potential proxy error, fugacity proxy error, exact implicit timing, closure timing, and evidence band.
- [ ] Water fork output compares assigned `3B` and rigorous-label `4C` topology rows with pressure residual in MPa and `Z` residual, without presenting fixed-state diagnostics as VLE validation.
- [ ] Local objective sensitivity output reports exact and closure objective values, gradient max absolute error, Hessian-proxy max absolute error, exact implicit timing, closure timing, and evidence band.
- [ ] The collapsed donor/acceptor mean-field closure remains diagnostic-only in all new evidence bands unless a row is explicitly marked as a failure-mode diagnostic.
- [ ] Every new or updated figure workflow writes retained CSV, plotted-data CSV, PNG, and `.mpl.yaml` sidecar files under its figure-owned `output` folder.
- [ ] `analysis.yaml` and `README.md` list the new commands and state that this remains analysis-only toybox evidence.
- [ ] Final implementation reporting renders every new or updated plot inline with absolute filesystem paths and includes compact Markdown tables from retained data.
- [ ] No `packages/epcsaft/**`, `packages/epcsaft-equilibrium/**`, `packages/epcsaft-regression/**`, public API, native SDK, capability contract, or dependency file is changed.

## Blocked by

- None

## Non-goals

- No provider runtime implementation of explicit association closures.
- No public Python API change.
- No equilibrium route implementation, Ipopt work, HELD work, phase discovery, flash, bubble, dew, or LLE work.
- No regression package work.
- No claim that centered perturbation diagnostics are production exact derivatives.
- No source AAD summary values treated as raw validation data.
- No broad gallery folder; keep each figure's generated artifacts inside the figure-owned `output` folder.

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/render_figure.py`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## GitHub Body Text

This mirror is a close local copy of https://github.com/ePC-SAFT/ePC-SAFT/issues/220. The authoritative execution plan is `docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence-plan.md`.
