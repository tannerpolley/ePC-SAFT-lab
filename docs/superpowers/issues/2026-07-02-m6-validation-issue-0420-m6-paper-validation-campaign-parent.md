---
issue: 420
title: "M6: Paper validation campaign parent"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/420
state: open
milestone: "M6 - Validation"
project: "ePC-SAFT Roadmap"
package: benchmark
capability: validation
backend: none
readiness: "ready"
release_target: future
source_spec: docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md
source_plan: docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
afk_hitl: HITL
branch: codex/issue-0420-m6-paper-validation-campaign-parent
last_synced: "2026-07-10"
---

# M6: Paper validation campaign parent

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/420
**GitHub Milestone:** M6 - Validation
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters.md
**Source Plan:** docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
**Plan Slice:** Non-executable deferred paper-campaign tracker
**Package Owner:** `benchmark`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** docs, validation, area:benchmark, status:ready, type:task
**Goal Command:** None until prerequisites and explicit scheduling permit execution.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree task first
**Integration Policy:** Main-thread review and local integration
**TDD Policy:** Owned by executable child leaves
**Parallelization Plan:** Only non-overlapping owner slices after dependencies pass
**Reviewer Role:** Independent reviewer plus main-thread integrator
**Script Gate Mode:** Safety plus proof oracle
**Sub-Issue Role:** rollup
**Executable:** false
**Parent:** https://github.com/ePC-SAFT/ePC-SAFT/issues/194
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md#outcome-proof
**Intent:** Track deferred paper-validation campaigns separately from the exact Tasks 9-22 closeout leaves.
**Owner:** M6 - Validation / `benchmark`.
**Plan Slice:** Non-executable deferred paper-campaign tracker.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Track deferred paper-validation campaigns separately from the exact Tasks 9-22 closeout leaves.

## Acceptance Criteria

- [ ] Keep this mirror and live issue as a non-executable rollup.
- [ ] Route implementation only through hydrated executable leaves.
- [ ] Keep subissue/dependency state synchronized with the source plans.
- [ ] Do not infer capability admission from rollup state.

## Blocked by

- None.

## Non-goals

- Work only in the owner and plan slice named above.
- Treat package behavior and capability state as read-only inputs; route reproduced defects to the owning package issue.
- Use traceable source identities and current model receipts; do not fill missing inputs or relabel fitted values as literature.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-02-m6-khudaida-paper-validation-with-figiel-parameters-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <this mirror> --milestone-required
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
