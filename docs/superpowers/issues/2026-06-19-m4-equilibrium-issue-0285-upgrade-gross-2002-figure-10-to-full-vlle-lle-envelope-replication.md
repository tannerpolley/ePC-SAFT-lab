---
issue: 285
title: "M4: upgrade Gross 2002 Figure 10 to full VLLE/LLE envelope replication"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/285"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "association"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md"
source_plan: "docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0285-gross-2002-figure-10-vlle-lle-envelope-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0285-gross-2002-figure-10-envelope-replication
last_synced: "2026-06-20"
---
# M4: upgrade Gross 2002 Figure 10 to full VLLE/LLE envelope replication

**Mirror Retention:** retain
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/285
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
**Source Plan:** docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0285-gross-2002-figure-10-vlle-lle-envelope-plan.md

**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** status:ready, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, native, docs
**Goal Command:** /goal Resolve this issue using docs/superpowers/plans/2026-06-20-m4-equilibrium-issue-0285-gross-2002-figure-10-vlle-lle-envelope-plan.md. Complete proof oracle: Figure 10 full water/1-pentanol VLLE/LLE envelope retained source data, model curve or envelope, paper-scale plot, score JSON, validation checker, docs validation, cleanup hook.
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

Upgrade Figure 10 from source-data plus diagnostic-sample stress gate to full water/1-pentanol isobaric VLLE/LLE envelope replication at 1.013 bar.

## Acceptance Criteria

- [ ] Retain or extend source data for water-rich, alcohol-rich, vapor, and VLLE branches with QA overlays.
- [ ] Generate PC-SAFT LLE/VLLE model envelope data across the plotted domain.
- [ ] Render a paper-scale T-x mirror plot matching the paper axes and branch roles.
- [ ] Require exact association derivative receipts, mass-action residuals, fresh-native proof, and the Gross 2002 two-site water caveat.
- [ ] Write score JSON per branch and require the Figure 10 score gate.

## Blocked by

- Missing source plan and route-prerequisite audit.

## Blocker Evidence

- This issue mirror still has `source_plan: null`, so it cannot be launched through the Superpowers worker route.
- Figure 10 full replication requires more than the existing diagnostic stress sample: it needs full water-rich, alcohol-rich, vapor, and VLLE envelope model evidence. Any missing public route admission must be split into a prerequisite issue before the figure-replication PR proceeds.

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

