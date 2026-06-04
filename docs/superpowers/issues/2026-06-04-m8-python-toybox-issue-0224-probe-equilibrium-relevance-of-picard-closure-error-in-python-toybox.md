---
issue: 224
title: "Probe equilibrium relevance of Picard closure error in Python toybox"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/224"
state: "open"
milestone: "M8 - Python Toybox"
project: "ePC-SAFT Roadmap"
package: "analysis"
capability: "explicit-association-toybox"
backend: "python"
readiness: "ready"
release_target: "future"
source_spec: "docs/superpowers/specs/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error.md"
source_plan: "docs/superpowers/plans/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0224-probe-equilibrium-relevance-of-picard-closure-error-in-python-toybox
last_synced: "2026-06-04"
---

# Probe equilibrium relevance of Picard closure error in Python toybox

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/224
**GitHub Milestone:** M8 - Python Toybox
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error.md
**Source Plan:** docs/superpowers/plans/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error-plan.md
**Branch:** codex/issue-0224-probe-equilibrium-relevance-of-picard-closure-error-in-python-toybox
**AFK/HITL:** HITL
**Labels:** type:task, status:ready, ready-for-human, validation, area:equilibrium, area:derivatives, backend:ipopt
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

Build a Python-only objective, Jacobian, and Hessian probe that tests whether
Picard closure error is dangerous for later equilibrium NLP work while staying
out of `epcsaft-equilibrium` route APIs.

The probe may include a saturation-style residual solve that uses JAX for
residual Jacobians and objective gradient/Hessian diagnostics. Python Ipopt
binding availability should be attempted and retained as evidence; missing
bindings are a diagnostic status, not a reason to add substitute package routes.

## Acceptance Criteria

- [ ] The probe uses neutral objective names such as `local_objective`, not bubble, dew, flash, LLE, HELD, or GFPE route names.
- [ ] Exact implicit and Picard objective values are compared for the same toybox cases.
- [ ] Gradient and Hessian error norms are retained with admission status bands.
- [ ] The pure-component saturation toybox retains JAX residual Jacobian, objective gradient, Hessian diagnostic, optimizer backend, and Python-Ipopt availability fields.
- [ ] The probe reports blocked status when derivative baseline rows are missing.
- [ ] No provider, equilibrium, benchmark, or public API files are changed.

## Blocked by

- None

## Non-goals

- No `epcsaft-equilibrium` implementation.
- No production Ipopt integration, route API, HELD, GFPE, bubble, dew, flash, or LLE workflow.
- No provider EOS changes.

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_quick_phase_equilibrium.py -q`
- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_pure_saturation.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/render_figure.py`
- `rg -n "bubble|dew|flash|LLE|HELD|GFPE" analyses/package_validation/explicit_association_toybox/scripts/quick_phase_equilibrium.py analyses/package_validation/explicit_association_toybox/figures/equilibrium_relevance_probe`
