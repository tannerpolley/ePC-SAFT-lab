---
issue: 283
title: "M4: upgrade Gross 2002 Figure 8 to full LLE+VLE envelope replication"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/283"
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
branch: codex/issue-0283-gross-2002-figure-8-envelope-replication
last_synced: "2026-06-19"
---
# M4: upgrade Gross 2002 Figure 8 to full LLE+VLE envelope replication

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/283
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
**Source Plan:** none
**Classification:** AFK
**Labels:** status:blocked, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, native, docs
**Goal Command:** /goal Resolve this issue using docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md after https://github.com/ePC-SAFT/ePC-SAFT/issues/279 is closed. Complete proof oracle: Figure 8 full methanol/cyclohexane LLE+VLE envelope retained source data, model curve or envelope, paper-scale plot, score JSON, validation checker, docs validation, cleanup hook.
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

Upgrade Figure 8 from selected LLE source-pair acceptance evidence to full isobaric LLE+VLE T-x envelope replication at 1.013 bar.

## Acceptance Criteria

- [ ] Retain or extend source data for both LLE and VLE branches with QA overlays.
- [ ] Generate PC-SAFT LLE and VLE envelope model data across the plotted domain.
- [ ] Render a paper-scale T-x mirror plot with source branches and model envelope.
- [ ] Require exact association derivative receipts, mass-action residuals, and fresh-native proof.
- [ ] Write score JSON for branch coverage, branch error, azeotrope/plait-region behavior, and pass/fail state.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/279

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

