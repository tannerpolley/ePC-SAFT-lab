---
issue: 432
title: "M0: define versioned ownership index and pure ratchet validator"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/432
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
afk_hitl: AFK
branch: codex/issue-0432-m0-define-versioned-ownership-index-and-pure-ratchet-validator
last_synced: "2026-07-10"
---

# M0: define versioned ownership index and pure ratchet validator

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/432
**GitHub Milestone:** M0 - Governance
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets-plan.md
**Plan Slice:** Task 1
**Package Owner:** `governance`
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** docs, validation, area:docs, type:task, status:ready, agent-ready
**Goal Command:** /goal Resolve issue #432 by executing its exact source-plan slice and proof oracle.
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
**Intent:** Define the inactive versioned ownership schema and deterministic local validator before any package baseline is activated.
**Owner:** M0 - Governance / `governance`.
**Plan Slice:** Task 1.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Define the inactive versioned ownership schema and deterministic local validator before any package baseline is activated.

## Acceptance Criteria

- [ ] Deliver exactly `Task 1` within the `governance` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

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
