---
issue: 431
title: "M0: characterize ownership and maintainability ratchets"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/431
state: open
milestone: "M0 - Governance"
project: "ePC-SAFT Roadmap"
package: governance
capability: workflow
backend: none
readiness: "ready"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets.md
source_plan: docs/superpowers/plans/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets-plan.md
afk_hitl: HITL
branch: codex/issue-0431-m0-characterize-ownership-and-maintainability-ratchets
last_synced: "2026-07-10"
---

# M0: characterize ownership and maintainability ratchets

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/431
**GitHub Milestone:** M0 - Governance
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets-plan.md
**Plan Slice:** Plan rollup; Tasks 1-3 execute through the two child leaves.
**Package Owner:** `governance`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** docs, validation, area:docs, type:task, status:ready
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
**Parent:** None
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets-plan.md#outcome-proof
**Intent:** Track one package-aware ownership index and measured structural ratchet without turning file size into an unmeasured style preference.
**Owner:** M0 - Governance / `governance`.
**Plan Slice:** Plan rollup; Tasks 1-3 execute through the two child leaves..
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Track one package-aware ownership index and measured structural ratchet without turning file size into an unmeasured style preference.

## Acceptance Criteria

- [ ] Keep this mirror and live issue as a non-executable rollup.
- [ ] Route implementation only through hydrated executable leaves.
- [ ] Keep subissue/dependency state synchronized with the source plans.
- [ ] Do not infer capability admission from rollup state.

## Blocked by

- None.

## Non-goals

- Work only in the owner and plan slice named above.
- Governance state must derive from measured local receipts and exact terminal leaves, not broad tracker status.
- Do not change package behavior or scientific capability state in this issue.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <this mirror> --milestone-required
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
