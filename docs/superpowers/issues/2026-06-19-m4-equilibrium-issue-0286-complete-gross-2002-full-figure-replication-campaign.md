---
issue: 286
title: "M4: complete Gross 2002 full figure replication campaign"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/286"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "association"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md"
source_plan: null
afk_hitl: "AFK"
branch: codex/issue-0286-gross-2002-full-figure-replication-campaign
last_synced: "2026-06-20"
---
# M4: complete Gross 2002 full figure replication campaign

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/286
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
**Source Plan:** none
**Classification:** AFK
**Labels:** status:ready, type:feature, validation, equilibrium, area:equilibrium, backend:ipopt, native, docs
**Goal Command:** /goal Track completion of the Gross 2002 full figure replication issue set from docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md. Complete proof oracle: every child issue closed and the full-replication checker reports every Figure 1-10 accepted with retained curve-level evidence.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** Source plan packets
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Track and close the full Gross/Sadowski 2002 figure replication campaign. This issue is complete only when every figure from the paper has curve-level retained evidence and the strict full-replication checker accepts Figures 1-10.

## Child Issues

- https://github.com/ePC-SAFT/ePC-SAFT/issues/279
- https://github.com/ePC-SAFT/ePC-SAFT/issues/280
- https://github.com/ePC-SAFT/ePC-SAFT/issues/281
- https://github.com/ePC-SAFT/ePC-SAFT/issues/282
- https://github.com/ePC-SAFT/ePC-SAFT/issues/283
- https://github.com/ePC-SAFT/ePC-SAFT/issues/284
- https://github.com/ePC-SAFT/ePC-SAFT/issues/285

## Acceptance Criteria

- [ ] Foundation checker/scoring/schema issue is closed.
- [ ] Figure 1 pure-component density replication issue is closed.
- [ ] Figures 2-5 self-associating VLE replication issue is closed.
- [ ] Figures 6-7 supercritical-partner VLE replication issue is closed.
- [ ] Figure 8 LLE+VLE envelope upgrade issue is closed.
- [ ] Figure 9 cross-associating VLE replication issue is closed.
- [ ] Figure 10 VLLE/LLE envelope upgrade issue is closed.
- [ ] `check_gross_2002_full_replication.py --require-complete` reports every Figure 1-10 accepted with retained source, model, plot, sidecar, score, and derivative evidence as required.
- [ ] M4 docs clearly distinguish full Gross 2002 paper replication from #275 association acceptance.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/280
- https://github.com/ePC-SAFT/ePC-SAFT/issues/281
- https://github.com/ePC-SAFT/ePC-SAFT/issues/282
- https://github.com/ePC-SAFT/ePC-SAFT/issues/283
- https://github.com/ePC-SAFT/ePC-SAFT/issues/284
- https://github.com/ePC-SAFT/ePC-SAFT/issues/285

## Non-goals

- No electrolyte, reactive, CE, CPE, or generalized phase-count admission by itself.
- No claim that Gross 2002 proves all associating systems.

## Proof Oracle

- uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
- uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete --require-exact-association-hessian --require-fresh-native
- uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
- uv run --no-sync python scripts/dev/validate_project.py docs
- cleanup hook


## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments, labels, milestone, dependency edges, issue type, and project fields.

