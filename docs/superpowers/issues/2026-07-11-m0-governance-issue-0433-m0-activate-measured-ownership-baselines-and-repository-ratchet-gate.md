---
issue: 433
title: "M0: activate measured ownership baselines and repository ratchet gate"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/433
state: open
milestone: "M0 - Governance"
project: "ePC-SAFT Roadmap"
package: governance
capability: workflow
backend: none
readiness: "blocked"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets.md
source_plan: docs/superpowers/plans/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets-plan.md
afk_hitl: HITL
branch: codex/issue-0433-m0-activate-measured-ownership-baselines-and-repository-ratchet-gate
last_synced: "2026-07-10"
---

# M0: activate measured ownership baselines and repository ratchet gate

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/433
**GitHub Milestone:** M0 - Governance
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets-plan.md
**Plan Slice:** Tasks 2-3
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
**Parent:** https://github.com/ePC-SAFT/ePC-SAFT/issues/431
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets-plan.md#outcome-proof
**Intent:** Activate only measured package baselines, add repository enforcement, and preserve a pure offline validator plus a separate live-accountability reconciler.
**Owner:** M0 - Governance / `governance`.
**Plan Slice:** Tasks 2-3.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Activate only measured package baselines, add repository enforcement, and preserve a pure offline validator plus a separate live-accountability reconciler.

## Acceptance Criteria

- [ ] Deliver exactly `Tasks 2-3` within the `governance` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/444
- https://github.com/ePC-SAFT/ePC-SAFT/issues/449
- https://github.com/ePC-SAFT/ePC-SAFT/issues/463

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
