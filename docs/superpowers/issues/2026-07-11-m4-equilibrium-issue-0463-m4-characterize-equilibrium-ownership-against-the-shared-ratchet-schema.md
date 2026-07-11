---
issue: 463
title: "M4: characterize equilibrium ownership against the shared ratchet schema"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/463
state: open
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: equilibrium
backend: Ipopt
readiness: "blocked"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m4-equilibrium-canonical-owner-decomposition.md
source_plan: docs/superpowers/plans/2026-07-10-m4-equilibrium-canonical-owner-decomposition-plan.md
afk_hitl: HITL
branch: codex/issue-0463-m4-characterize-equilibrium-ownership-against-the-shared-ratchet-schema
last_synced: "2026-07-10"
---

# M4: characterize equilibrium ownership against the shared ratchet schema

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/463
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m4-equilibrium-canonical-owner-decomposition.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m4-equilibrium-canonical-owner-decomposition-plan.md
**Plan Slice:** Task 1
**Package Owner:** `equilibrium`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** native, docs, validation, equilibrium, area:equilibrium, backend:ipopt, type:task, status:blocked
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
**Parent:** https://github.com/ePC-SAFT/ePC-SAFT/issues/462
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-10-m4-equilibrium-canonical-owner-decomposition-plan.md#outcome-proof
**Intent:** Characterize current M4 owners and admitted/internal routes against the inactive M0 schema without activating or editing the baseline index.
**Owner:** M4 - Equilibrium / `equilibrium`.
**Plan Slice:** Task 1.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Characterize current M4 owners and admitted/internal routes against the inactive M0 schema without activating or editing the baseline index.

## Acceptance Criteria

- [ ] Deliver exactly `Task 1` within the `equilibrium` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/432

## Non-goals

- Work only in the owner and plan slice named above.
- Preserve current public route state unless this issue is a separately proven admission leaf.
- Keep provider serialization and retained paper artifacts in their M3/M6 owners.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m4-equilibrium-canonical-owner-decomposition-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m4-equilibrium-canonical-owner-decomposition-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <this mirror> --milestone-required
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
