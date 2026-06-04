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
last_synced: "2026-06-04"
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

Turn the toybox evidence into a clear admission decision that keeps Picard as
the only retained approximation candidate and blocks provider implementation
until property and derivative gates pass.

## Acceptance Criteria

- [ ] The toybox active closure registry retains exact implicit baselines, source topology reductions, exact 2B reduction, and seven-step Picard only.
- [ ] Obsolete diagonal-polish, collapsed-mean-field, and unrelated approximation families do not appear as runnable active closure lanes.
- [ ] A retained admission summary records each closure family, status, evidence basis, and provider-admission decision.
- [ ] Issue #161 docs are not marked implementation-ready unless the evidence gates pass.
- [ ] No provider, equilibrium, benchmark, or public API files are changed.

## Blocked by

- None

## Non-goals

- No provider implementation.
- No public API or capability claim.
- No new approximation family beyond the retained Picard candidate.

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_topology_reductions.py analyses/package_validation/explicit_association_toybox/tests/test_propagation_evidence.py analyses/package_validation/explicit_association_toybox/tests/test_admission_decision.py -q`
- `uv run python analyses/package_validation/explicit_association_toybox/scripts/admission_decision.py`
- `rg -n "collapsed|diagonal|mean_field|polish" analyses/package_validation/explicit_association_toybox/scripts analyses/package_validation/explicit_association_toybox/config`
