---
issue: 446
title: "M5: compile explicit controls and fitted parameters from resolved input"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/446
state: open
milestone: "M5 - Regression"
project: "ePC-SAFT Roadmap"
package: regression
capability: regression
backend: Ceres
readiness: "blocked"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m5-regression-traceable-native-problem-contract.md
source_plan: docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md
afk_hitl: HITL
branch: codex/issue-0446-m5-compile-explicit-controls-and-fitted-parameters-from-resolved-input
last_synced: "2026-07-10"
---

# M5: compile explicit controls and fitted parameters from resolved input

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/446
**GitHub Milestone:** M5 - Regression
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m5-regression-traceable-native-problem-contract.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md
**Plan Slice:** Task 2
**Package Owner:** `regression`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** native, regression, validation, area:regression, backend:ceres, type:task, status:blocked
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
**Parent:** https://github.com/ePC-SAFT/ePC-SAFT/issues/193
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md#outcome-proof
**Intent:** Compile fitted parameters, bounds, exact target rows, and every accepted public control from the M3 resolved input; reject any control that cannot affect effective native Ceres behavior.
**Owner:** M5 - Regression / `regression`.
**Plan Slice:** Task 2.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Compile fitted parameters, bounds, exact target rows, and every accepted public control from the M3 resolved input; reject any control that cannot affect effective native Ceres behavior.

## Acceptance Criteria

- [ ] Deliver exactly `Task 2` within the `regression` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/441
- https://github.com/ePC-SAFT/ePC-SAFT/issues/445

## Non-goals

- Work only in the owner and plan slice named above.
- Every accepted control, weight, and scale must affect the compiled native problem or be rejected before dispatch.
- Component/backend tests alone cannot admit a regression workflow; M6 owns retained real-data evidence.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <this mirror> --milestone-required
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
