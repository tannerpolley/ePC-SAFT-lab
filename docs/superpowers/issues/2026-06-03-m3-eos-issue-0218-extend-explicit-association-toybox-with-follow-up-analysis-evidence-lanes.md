---
issue: 218
title: "Extend explicit association toybox with follow-up analysis evidence lanes"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/218"
state: "open"
milestone: "M3 - EOS"
project: "ePC-SAFT Roadmap"
package: "epcsaft"
capability: "explicit-association-toybox"
backend: null
readiness: "blocked"
source_spec: "docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-follow-up-analysis-roadmap.md"
source_plan: "docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-follow-up-analysis-roadmap-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0218-extend-explicit-association-toybox-with-follow-up-analysis-evidence-lanes
last_synced: "2026-06-03"
release_target: null
---

# Extend explicit association toybox with follow-up analysis evidence lanes

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/218
GitHub Milestone: M3 - EOS
Issue Type: task
Source Spec: docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-follow-up-analysis-roadmap.md
Source Plan: docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-follow-up-analysis-roadmap-plan.md
Classification: AFK
Labels: status:blocked, type:task, area:core, area:derivatives, validation
Goal Command: /goal Extend the explicit association toybox with topology heatmaps, real-system topology mapping, closure sensitivity rankings, derivative-smoothness diagnostics, fixed-state property residual reframing, water parameter cases, repeated timing, and total ares context once issue #216 has landed.
Execution Mode: Ask at runtime
Worktree Policy: Native Codex worktree thread first
Integration Policy: Worker PR reviewed by main thread
TDD Policy: Required
Parallelization Plan: None
Reviewer Role: Main thread orchestrator
Script Gate Mode: Safety only
Branch: codex/issue-0218-extend-explicit-association-toybox-with-follow-up-analysis-evidence-lanes
AFK/HITL: AFK

GitHub remains authoritative for state, labels, Project fields, dependencies,
comments, and PR linkage. This mirror exists so `project-resolve` can start
from the durable local source plan once the blocker is closed.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Extend the Python-only explicit association toybox under
`analyses/package_validation/explicit_association_toybox/**` with the follow-up
evidence lanes identified from the first matrix results:

- topology-resolved error heatmaps by topology and `rho * Delta`;
- real-system topology mapping for acids, alkanols, water, amines, and
  Gross/Sadowski associating binaries;
- closure sensitivity ranking across Picard count, damping, and diagonal
  polish;
- density, association-strength, and composition derivative-smoothness
  diagnostics;
- fixed-state pressure residual reframing with MPa and compressibility-factor
  residuals;
- water parameter cases that record source and diameter policy;
- repeated timing summaries with median/spread statistics;
- total neutral `ares` context through the issue #216 HC/dispersion lane.

This is an analysis evidence issue. It does not admit a production closure or
change package public behavior.

## Acceptance Criteria

- [ ] Topology heatmap outputs show closure error by topology and `rho * Delta`, with retained plotted data.
- [ ] Real-system mapping rows cover source-backed representative families: acids, alkanols, water, amines, and Gross/Sadowski associating binaries.
- [ ] Closure sensitivity outputs rank Picard count, damping, and diagonal-polish variants by error and timing.
- [ ] Derivative smoothness diagnostics report density, association-strength, and composition perturbation behavior for exact and approximate closures.
- [ ] Property residual outputs include pressure residual in MPa and compressibility-factor residuals alongside the existing relative pressure residual.
- [ ] Water-specific rows record the parameter source and diameter handling used by the analysis.
- [ ] Repeated timing summaries report median, interquartile range, minimum, and maximum for exact and closure evaluations.
- [ ] Total neutral `ares` context is included only through the issue #216 HC/dispersion lane or equivalent already-merged files.
- [ ] All new or updated figure workflows write retained CSV, plotted-data CSV, PNG, and `.mpl.yaml` sidecar files.
- [ ] Final implementation reporting renders every new or updated plot inline in chat and includes compact Markdown tables from retained data.
- [ ] No `packages/epcsaft/**`, `packages/epcsaft-equilibrium/**`, `packages/epcsaft-regression/**`, public API, dependency, or production EOS behavior changes are introduced.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/216

## Non-goals

- No provider runtime implementation of explicit closures.
- No equilibrium route validation, pressure-transformed objective assembly, or HELD work.
- No regression or parameter fitting workflow.
- No claim that analysis perturbation diagnostics are production exact derivatives.
- No raw validation data entered from paper AAD summaries.
- No centralized gallery folder; generated artifacts stay figure-owned.

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/render_figure.py`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Tracker Metadata

- Milestone: `M3 - EOS`
- Package: `epcsaft`
- Capability: `explicit-association-toybox`
- Backend: none
- Readiness: `blocked`
- AFK/HITL: `AFK`
- Blocked by: `#216`
- Release target: none
- Labels: `status:blocked, type:task, area:core, area:derivatives, validation`
