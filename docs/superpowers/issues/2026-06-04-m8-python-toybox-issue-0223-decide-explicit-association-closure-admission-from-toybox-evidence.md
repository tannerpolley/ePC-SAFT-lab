---
issue: 223
title: "Decide explicit association closure admission from toybox evidence"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/223"
state: "open"
milestone: "M8 - Python Toybox"
project: "ePC-SAFT Roadmap"
package: "analysis"
capability: "explicit-association-toybox"
backend: "python"
readiness: "ready"
release_target: "future"
source_spec: "docs/superpowers/specs/2026-06-04-m8-python-toybox-explicit-closure-admission-decision.md"
source_plan: "docs/superpowers/plans/2026-06-04-m8-python-toybox-explicit-closure-admission-decision-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0223-decide-explicit-association-closure-admission-from-toybox-evidence
last_synced: "2026-06-05"
---

# Decide explicit association closure admission from toybox evidence

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/223
**GitHub Milestone:** M8 - Python Toybox
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-04-m8-python-toybox-explicit-closure-admission-decision.md
**Source Plan:** docs/superpowers/plans/2026-06-04-m8-python-toybox-explicit-closure-admission-decision-plan.md
**Branch:** codex/issue-0223-decide-explicit-association-closure-admission-from-toybox-evidence
**AFK/HITL:** HITL
**Labels:** type:task, status:ready, ready-for-human, validation, area:core
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

Turn the toybox evidence into the final Picard admission packet needed to
recommend whether provider issue #161 should close, stay blocked, or become a
narrow M3 provider-admission issue. The packet must compare the same fixed
Picard policy grid against exact implicit mass-action using relative errors,
end-to-end simulation timing, solver/root status, and readable retained plots.

## Acceptance Criteria

- [ ] `evaluate_closure(...)`, pressure-density coupling, and pure-saturation solving accept every closure name in `PICARD_POLICY_GRID`.
- [ ] A retained final report CSV includes exact implicit baseline rows and all 25 Picard policies for each supported simulation case.
- [ ] Final report rows include relative-error columns for association Helmholtz, total residual Helmholtz proxy, pressure proxy, saturation pressure, vapor density, liquid density, selected derivatives, and selected Hessian/Jacobian diagnostics.
- [ ] Final report rows include closure-only and end-to-end simulation timing for exact implicit and Picard policies.
- [ ] Readable final plots use data markers, dotted exact-implicit curves, and dotted Picard curves; no bar plots are added.
- [ ] A Markdown decision memo recommends whether issue #161 should close without provider implementation, close as design-complete and open a narrow M3 provider-admission issue, or remain blocked by one named missing evidence item.
- [ ] Issue #161 docs are not marked provider-ready unless the final evidence gates pass and the memo explicitly recommends provider-admission follow-up.
- [ ] No provider, equilibrium, benchmark, or public API files are changed.

## Blocked by

- None

## Non-goals

- No provider implementation.
- No public API or capability claim.
- No new approximation family beyond fixed Picard policy settings.
- No automatic live #161 close or rewrite; produce the decision memo for human review.

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_picard_policy_grid.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py analyses/package_validation/explicit_association_toybox/tests/test_final_picard_admission_report.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_policy_grid/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/final_picard_admission_report/scripts/render_figure.py`
- `rg -n "collapsed|diagonal|mean_field|polish" analyses/package_validation/explicit_association_toybox/scripts analyses/package_validation/explicit_association_toybox/config`
- `uv run python scripts/dev/validate_project.py quick`
