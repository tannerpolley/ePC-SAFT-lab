---
issue: 216
title: "Add HC and dispersion context to the explicit association toybox"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/216"
state: "open"
milestone: "M3 - EOS"
project: "ePC-SAFT Roadmap"
package: "epcsaft"
capability: "explicit-association-toybox"
backend: null
readiness: "ready"
release_target: null
source_spec: "docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-toybox-design.md"
source_plan: "docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-toybox-hc-dispersion-extension-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0216-add-hc-and-dispersion-context-to-the-explicit-association-toybox
last_synced: "2026-06-03"
---

# Add HC and dispersion context to the explicit association toybox

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/216
GitHub Milestone: M3 - EOS
Issue Type: task
Source Spec: docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-toybox-design.md
Source Plan: docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-toybox-hc-dispersion-extension-plan.md
Classification: AFK
Labels: status:ready, agent-ready, type:task, area:core, validation
Goal Command: /goal Extend the explicit association toybox with fixed-state hard-chain and dispersion scalar residual Helmholtz context terms, total ares metrics, residual ares figure workflow, and proof checks.
Execution Mode: Ask at runtime
Worktree Policy: Native Codex worktree thread first
Integration Policy: Worker PR reviewed by main thread
TDD Policy: Required
Parallelization Plan: None
Reviewer Role: Main thread orchestrator
Script Gate Mode: Safety only
Branch: codex/issue-0216-add-hc-and-dispersion-context-to-the-explicit-association-toybox
AFK/HITL: AFK

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from the durable local source plan.

## Summary

Add the deliberately tiny neutral PC-SAFT scalar context requested by the
explicit association closure toybox plan. The toybox should accept fixed
temperature, density, composition, segment, sigma, epsilon, and optional `k_ij`
inputs; compute hard-chain and dispersion scalar residual Helmholtz terms; then
report total neutral `ares` exact/closure differences and timing evidence
beside the existing association-only closure metrics.

This stays under `analyses/package_validation/explicit_association_toybox/**`.
It is analysis code, not package runtime code.

This issue remains a narrow scalar-context slice. The broader drawing-board
validation direction is
`docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`,
which adds Huang/Radosz topology rows, real association scheme matrices, and a
staged property-data lane. Do not expand this issue into that whole matrix
without a separate plan/issue.

## Acceptance Criteria

- [ ] Add fixed-state neutral PC-SAFT input helpers for `T`, `rho`, `x`, `m`, `sigma`, `epsilon_over_k`, and optional `k_ij` under the explicit association toybox.
- [ ] Add source-backed scalar hard-chain helpers for `zeta_n`, `ares_hs`, and `ares_hc` using local equation docs as the formula source.
- [ ] Add source-backed scalar dispersion helpers for Gross-style polynomial coefficients, mixed dispersion moments, and `ares_disp` using local equation docs and provider constants as cross-reference.
- [ ] Extend the grid/metrics output with `ares_hc`, `ares_disp`, exact/closure association `ares`, total exact/closure `ares`, total absolute/relative error, exact solve time, closure time, and speedup ratio.
- [ ] Add a residual `ares` figure workflow that writes retained metrics, plotted data, PNG, and `.mpl.yaml` sidecar under `figures/residual_ares_error/output`.
- [ ] Keep HC and dispersion identical across exact and explicit association rows for the same state, so total `ares` error isolates association-closure error.
- [ ] Keep the work analysis-only: no SciPy dependency, no density solve, no provider runtime API, no native C++, no equilibrium package, and no regression package changes.

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py`
- `rg -n "import scipy|from scipy" analyses/package_validation/explicit_association_toybox packages tests scripts`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`

## Non-Goals And Boundaries

- No density solve or phase root selection.
- No pressure, fugacity, activity, chemical-potential, derivative, Jacobian, Hessian, equilibrium, regression, ionic, Born, dielectric, polar, or public package API work.
- No provider native cross-check as the primary Python formula baseline.
- No broad analysis folder migration.
- No full paper-backed topology matrix, real vapor-pressure/liquid-density
  parity workflow, or 2B/3B/4C production evidence claim.

## Tracker Metadata

- Milestone: `M3 - EOS`
- Package: `epcsaft`
- Capability: `explicit-association-toybox`
- Backend: none
- Readiness: `ready`
- AFK/HITL: `AFK`
- Release target: none
- Labels: `agent-ready, validation, area:core, status:ready, type:task`

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat
