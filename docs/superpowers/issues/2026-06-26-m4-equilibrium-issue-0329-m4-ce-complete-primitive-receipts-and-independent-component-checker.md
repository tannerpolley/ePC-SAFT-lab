---
issue: 329
title: "M4 CE: complete primitive receipts and independent component checker"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/329
state: open
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: reactive
backend: Ipopt
readiness: "blocked"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission.md
source_plan: docs/superpowers/plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md
afk_hitl: HITL
branch: codex/issue-0329-m4-ce-complete-primitive-receipts-and-independent-component-checker
last_synced: "2026-07-10"
---

# M4 CE: complete primitive receipts and independent component checker

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/329
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md
**Plan Slice:** Tasks 1-3
**Package Owner:** `equilibrium`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:task
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
**Parent:** https://github.com/ePC-SAFT/ePC-SAFT/issues/321
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md#outcome-proof
**Intent:** Complete primitive standalone-CE receipts and an independent component reconstruction checker after #328.
**Owner:** M4 - Equilibrium / `equilibrium`.
**Plan Slice:** Tasks 1-3.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Complete primitive standalone-CE receipts and an independent component reconstruction checker after #328.

## Acceptance Criteria

- [ ] Deliver exactly `Tasks 1-3` within the `equilibrium` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/327
- https://github.com/ePC-SAFT/ePC-SAFT/issues/328

## Non-goals

- Work only in the owner and plan slice named above.
- Preserve current public route state unless this issue is a separately proven admission leaf.
- Keep provider serialization and retained paper artifacts in their M3/M6 owners.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <this mirror> --milestone-required
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
