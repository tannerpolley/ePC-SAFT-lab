---
issue: 284
title: "M4: fully replicate Gross 2002 Figure 9 cross-associating VLE curve"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/284"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "association"
backend: "Ipopt"
readiness: "blocked"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md"
source_plan: null
afk_hitl: "AFK"
branch: codex/issue-0284-gross-2002-figure-9-vle-curve
last_synced: "2026-06-20"
---
# M4: fully replicate Gross 2002 Figure 9 cross-associating VLE curve

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/284
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
**Source Plan:** none
**Classification:** AFK
**Labels:** status:blocked, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, native, docs
**Goal Command:** /goal Resolve this issue using docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md after https://github.com/ePC-SAFT/ePC-SAFT/issues/292 is closed. Complete proof oracle: Figure 9 methanol/1-octanol cross-associating VLE curve retained source data, model curve or envelope, paper-scale plot, score JSON, validation checker, docs validation, cleanup hook.
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

Replicate the isobaric methanol/1-octanol VLE T-x plot at 1.013 bar and exercise cross-association combining rules.

## Acceptance Criteria

- [ ] Retain source data or calibrated digitization for Figure 9 with temperature and composition units.
- [ ] Generate PC-SAFT VLE model curve with Gross 2002 Table 1/2 parameters.
- [ ] Render a paper-scale T-x mirror plot.
- [ ] Record exact association derivative diagnostics for the cross-associating solve.
- [ ] Write score JSON and require the Figure 9 score gate.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/292

## Blocker Evidence

- Figure 9 full replication is a cross-associating isobaric VLE curve at 1.013 bar.
- The public source-backed associating VLE admission required to generate model curves belongs to #292, not to the Figure 9 artifact PR.

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

