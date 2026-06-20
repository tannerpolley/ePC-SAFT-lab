---
issue: 281
title: "M4: fully replicate Gross 2002 Figures 2-5 self-associating VLE curves"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/281"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "association"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md"
source_plan: "docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0281-gross-2002-figures-2-5-vle-curves-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0281-gross-2002-figures-2-5-vle-curves
last_synced: "2026-06-20"
---
# M4: fully replicate Gross 2002 Figures 2-5 self-associating VLE curves

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/281
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
**Source Plan:** docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0281-gross-2002-figures-2-5-vle-curves-plan.md
**Classification:** AFK
**Labels:** status:ready, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, native, docs
**Goal Command:** /goal Resolve this issue using docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0281-gross-2002-figures-2-5-vle-curves-plan.md after https://github.com/ePC-SAFT/ePC-SAFT/issues/280 is closed. Complete proof oracle: Figures 2-5 subcritical self-associating VLE curves retained source data, resolved Figure 2 identity, model curves, paper-scale plots, per-series score JSON, validation checker, docs validation, cleanup hook.
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

Replicate Figure 2 methanol identity case, Figure 3 1-propanol/ethylbenzene, Figure 4 1-pentanol/benzene, and Figure 5 propanol isomer/benzene VLE systems.

## Acceptance Criteria

- [ ] Resolve the Figure 2 methanol-isobutane caption versus methanol-isobutanol Table 2 identity before acceptance.
- [ ] Retain source data or calibrated digitization for Figures 2-5 with units, series labels, and QA overlays.
- [ ] Generate paper-axis VLE model curves for all required systems and series.
- [ ] Render paper-scale mirror plots for Figures 2-5.
- [ ] Write score JSON per figure and per series.
- [ ] Keep native route implementation work out of the figure-replication PR; split any discovered production-route gap into a prerequisite issue.

## Blocked by

- None

## Non-goals

- No electrolyte, reactive, CE, CPE, or generalized phase-count admission.
- No detached validation mirror outside analyses/paper_validation/2002_gross.
- No completion credit for diagnostic-only or unscored plot evidence.

## Proof Oracle

- uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
- uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-exact-association-hessian --require-fresh-native
- uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
- uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
- uv run --no-sync python scripts/dev/validate_project.py docs
- cleanup hook

Expected partial-campaign readout:

- uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native exits 2 until Figures 6-10 close.


## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments, labels, milestone, dependency edges, issue type, and project fields.

