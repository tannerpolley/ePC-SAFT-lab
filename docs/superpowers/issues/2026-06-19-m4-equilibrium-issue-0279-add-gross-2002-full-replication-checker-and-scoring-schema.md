---
issue: 279
title: "M4: add Gross 2002 full-replication checker and scoring schema"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/279"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "association"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md"
source_plan: "docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0279-gross-2002-full-replication-checker-scoring-schema-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0279-gross-2002-full-replication-checker-scoring-schema
last_synced: "2026-06-19"
---
# M4: add Gross 2002 full-replication checker and scoring schema

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/279
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md
**Source Plan:** docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0279-gross-2002-full-replication-checker-scoring-schema-plan.md
**Classification:** AFK
**Labels:** agent-ready, status:ready, type:task, validation, equilibrium, area:equilibrium, backend:ipopt, native, docs
**Goal Command:** /goal Resolve this issue using docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md. Complete proof oracle: full-replication checker contract, scoring schema, source metadata schema, manifest upgrade, docs validation, cleanup hook.
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

Add the strict full-replication foundation for the Gross/Sadowski 2002 paper-validation campaign: manifest shape, source metadata contract, digitization QA overlay requirement, per-figure score schema, and executable checker gate.

## Acceptance Criteria

- [ ] Add a strict full-replication checker entry point.
- [ ] Add red contract tests proving accepted figures fail without source CSV, calibration metadata, QA overlay, model curve, rendered plot, sidecar, score JSON, and required derivative receipts.
- [ ] Add a full-replication manifest for Figures 1-10.
- [ ] Define score JSON fields for source count, model count, RMSE, max axis error, normalized score, branch coverage, derivative status, and pass/fail state.
- [ ] Define source metadata fields for provenance, axis calibration, units, series labels, uncertainty, and QA overlay path.
- [ ] Keep #275 association acceptance checker behavior intact.
- [ ] Update M4 docs to distinguish #275 acceptance from full curve-level paper replication.

## Blocked by

- None

## Non-goals

- No figure-specific model curve implementation beyond checker fixtures.
- No electrolyte, reactive, CE, CPE, or generalized phase-count admission.
- No broad associating-family capability claim.

## Proof Oracle

- uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-foundation
- uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete
  - Expected for #279 closeout: exits 2 with named full-replication blockers for planned figure records; this is the #286 final gate, not a #279 pass gate.
- uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
- uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py -q
- uv run --no-sync python scripts/dev/validate_project.py docs
- cleanup hook


## GitHub Body

The GitHub issue body mirrors this file and is authoritative for live comments, labels, milestone, dependency edges, issue type, and project fields.

