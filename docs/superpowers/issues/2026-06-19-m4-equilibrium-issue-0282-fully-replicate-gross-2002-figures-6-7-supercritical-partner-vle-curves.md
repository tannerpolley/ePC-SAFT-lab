---
issue: 282
title: "M4: fully replicate Gross 2002 Figures 6-7 supercritical-partner VLE curves"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/282"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "association"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md"
source_plan: "docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0282-gross-2002-figures-6-7-supercritical-vle-curves-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0282-gross-2002-figures-6-7-vle-curves
last_synced: "2026-06-20"
---
# M4: fully replicate Gross 2002 Figures 6-7 supercritical-partner VLE curves

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/282
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
**Source Plan:** docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0282-gross-2002-figures-6-7-supercritical-vle-curves-plan.md

**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** status:ready, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, native, docs
**Goal Command:** /goal Resolve this issue using docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0282-gross-2002-figures-6-7-supercritical-vle-curves-plan.md after https://github.com/ePC-SAFT/ePC-SAFT/issues/292 is closed. Complete proof oracle: Figures 6-7 supercritical-partner VLE curves retained source data, model curve or envelope through existing public routes only, paper-scale plot, score JSON, validation checker, no package/native implementation edits, docs validation, cleanup hook.
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

Replicate the four-temperature VLE figures for 1-butanol/n-butane and ethanol/n-butane, including the paper caveat around butane critical behavior.

## Acceptance Criteria

- [ ] Retain source data or calibrated digitization for every temperature series in Figures 6 and 7.
- [ ] Generate matching PC-SAFT VLE model curves for all temperature series.
- [ ] Render paper-scale mirror plots with series labels matching the paper.
- [ ] Write score JSON per temperature series and figure.
- [ ] Record the supercritical-partner caveat and keep capability text evidence-scoped.
- [ ] Keep `packages/**`, C++/header, CMake, and package-local test changes out of this figure-replication PR; split any discovered production-route gap into a prerequisite issue.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/292

## Blocker Evidence

- #282 worker retained Figure 6 source data and checker gates, then stopped model generation because the public `bubble_pressure` route rejects the source-backed 1-butanol/n-butane associating VLE input.
- The discovered route gap belongs to #292, not to this figure-replication PR. #282 must resume only after #292 lands and must still keep `packages/**`, native C++/header, CMake, and package-local test changes out of its branch.

## Non-goals

- No electrolyte, reactive, CE, CPE, or generalized phase-count admission.
- No detached validation mirror outside analyses/paper_validation/2002_gross.
- No completion credit for diagnostic-only or unscored plot evidence.

## Proof Oracle

- uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
- uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native
- uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
- uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
- uv run --no-sync python scripts/dev/validate_project.py docs
- cleanup hook


## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments, labels, milestone, dependency edges, issue type, and project fields.

