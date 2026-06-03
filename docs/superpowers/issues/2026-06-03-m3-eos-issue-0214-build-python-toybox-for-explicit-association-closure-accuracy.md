---
issue: 214
title: "Build Python toybox for explicit association closure accuracy"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/214"
state: "open"
milestone: "M3 - EOS"
project: "ePC-SAFT Roadmap"
package: "core"
capability: "eos"
backend: "analytic"
readiness: "ready"
release_target: "future"
source_spec: "docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-toybox-design.md"
source_plan: "docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-toybox-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0214-explicit-association-toybox
last_synced: "2026-06-03"
---

# Build Python toybox for explicit association closure accuracy

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/214
**GitHub Milestone:** M3 - EOS
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-toybox-design.md
**Source Plan:** docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-toybox-plan.md
**Classification:** AFK
**Labels:** type:task, status:ready, agent-ready, area:core, area:derivatives, validation
**Goal Command:** /goal Resolve issue 214 by building the Python-only explicit association closure toybox from the linked M3 plan, with NumPy-only analysis code, focused tests, retained analysis outputs, and no provider/equilibrium/regression behavior changes.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only
**Branch:** codex/issue-0214-explicit-association-toybox

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Build a source-controlled Python-only package-validation toybox under
`analyses/package_validation/explicit_association_toybox` that compares
explicit PC-SAFT association closures against an independent exact mass-action
baseline across EOS diagnostic grids.

## Supplemental Context

- Source spec: `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-toybox-design.md`
- Source plan: `docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-toybox-plan.md`
- The first implementation defers any SciPy policy exception and stays
  NumPy-only.

## Acceptance Criteria

- [ ] `analyses/package_validation/explicit_association_toybox/README.md` and `analysis.yaml` document the analysis purpose, commands, outputs, and analysis-only boundary.
- [ ] The toybox implements an independent Python exact mass-action baseline with residual diagnostics, site-fraction bounds, and explicit failure on nonconvergence.
- [ ] Closure evaluators cover one-component 2B exact reduction, full-matrix Picard unroll, damped Picard unroll, Picard plus diagonal polish, and collapsed donor/acceptor mean field.
- [ ] Tests prove Closure A matches the exact baseline for its declared 2B topology and that approximate closures produce bounded labeled outputs on controlled systems.
- [ ] Metrics report site-fraction error, mass-action residual norm, association Helmholtz error, association compressibility contribution error, association residual chemical-potential contribution error, association fugacity contribution error, runtime, and evidence band.
- [ ] Grid generation writes retained CSV summaries under figure-owned `output/` folders and generated run payloads under ignored `output/runs/`.
- [ ] Figure rendering produces at least one accuracy summary figure and a plotted-data CSV from retained generated data.
- [ ] No provider C++, public API, equilibrium, regression, or package dependency behavior changes.
- [ ] Structure tests continue to enforce analysis layout and no unscoped SciPy imports.

## Proof Oracle

- `rg -n "import scipy|from scipy" analyses/package_validation/explicit_association_toybox packages tests scripts`
- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Non-Goals And Boundaries

- No provider C++ implementation paths for explicit association closures.
- No public `epcsaft` API changes.
- No equilibrium route prototypes.
- No Gross/Sadowski paper snapshots in this first implementation.
- No SciPy in committed analysis runtime code.
- No exact PC-SAFT production claim from approximate closures.

## Tracker Metadata

- Milestone: `M3 - EOS`
- Package: `core`
- Capability: `eos`
- Backend: `analytic`
- Readiness: `ready`
- AFK/HITL: `AFK`
- Release target: `future`
- Labels: `type:task, status:ready, agent-ready, area:core, area:derivatives, validation`
