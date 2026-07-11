---
issue: 434
title: "M0: close Tasks 9-22 validation-correctness program"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/434
state: open
milestone: "M0 - Governance"
project: "ePC-SAFT Roadmap"
package: governance
capability: workflow
backend: none
readiness: "blocked"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m0-validation-correctness-program-closeout.md
source_plan: docs/superpowers/plans/2026-07-10-m0-validation-correctness-program-closeout-plan.md
afk_hitl: HITL
branch: codex/issue-0434-m0-close-tasks-9-22-validation-correctness-program
last_synced: "2026-07-10"
---

# M0: close Tasks 9-22 validation-correctness program

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/434
**GitHub Milestone:** M0 - Governance
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m0-validation-correctness-program-closeout.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m0-validation-correctness-program-closeout-plan.md
**Plan Slice:** Tasks 1-3
**Package Owner:** `governance`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** docs, validation, area:docs, type:task, status:blocked
**Goal Command:** None until prerequisites and explicit scheduling permit execution.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree task first
**Integration Policy:** Main-thread review and local integration
**TDD Policy:** Required
**Parallelization Plan:** Only non-overlapping owner slices after dependencies pass
**Reviewer Role:** Independent reviewer plus main-thread integrator
**Script Gate Mode:** Safety plus proof oracle
**Sub-Issue Role:** leaf
**Executable:** true
**Parent:** None
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-10-m0-validation-correctness-program-closeout-plan.md#outcome-proof
**Intent:** Assemble exact milestone receipts, run one integrated local proof, and retire the historical Tasks 9-22 queue without treating unrelated future paper campaigns as blockers.
**Owner:** M0 - Governance / `governance`.
**Plan Slice:** Tasks 1-3.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Assemble exact milestone receipts, run one integrated local proof, and retire the historical Tasks 9-22 queue without treating unrelated future paper campaigns as blockers.

## Acceptance Criteria

- [ ] Deliver exactly `Tasks 1-3` within the `governance` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/192
- https://github.com/ePC-SAFT/ePC-SAFT/issues/433
- https://github.com/ePC-SAFT/ePC-SAFT/issues/438
- https://github.com/ePC-SAFT/ePC-SAFT/issues/444
- https://github.com/ePC-SAFT/ePC-SAFT/issues/451
- https://github.com/ePC-SAFT/ePC-SAFT/issues/455
- https://github.com/ePC-SAFT/ePC-SAFT/issues/456
- https://github.com/ePC-SAFT/ePC-SAFT/issues/457
- https://github.com/ePC-SAFT/ePC-SAFT/issues/464
- https://github.com/ePC-SAFT/ePC-SAFT/issues/467

## Non-goals

- Work only in the owner and plan slice named above.
- Governance state must derive from measured local receipts and exact terminal leaves, not broad tracker status.
- Do not change package behavior or scientific capability state in this issue.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m0-validation-correctness-program-closeout-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m0-validation-correctness-program-closeout-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <this mirror> --milestone-required
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
