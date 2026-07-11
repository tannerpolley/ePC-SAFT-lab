---
issue: 193
title: "M5: traceable regression contract and scoped admission"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/193
state: open
milestone: "M5 - Regression"
project: "ePC-SAFT Roadmap"
package: regression
capability: regression
backend: Ceres
readiness: "ready"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m5-regression-traceable-native-problem-contract.md
source_plan: docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md
afk_hitl: HITL
branch: codex/issue-0193-m5-traceable-regression-contract-and-scoped-admission
last_synced: "2026-07-10"
---

# M5: traceable regression contract and scoped admission

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/193
**GitHub Milestone:** M5 - Regression
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m5-regression-traceable-native-problem-contract.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md
**Plan Slice:** Non-executable tracker for #445-#451
**Package Owner:** `regression`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** native, validation, regression, area:regression, backend:ceres, status:ready, type:task
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

**Outcome Source:** docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md#outcome-proof
**Intent:** Track the strict native regression contract and exactly scoped real-data admission leaves.
**Owner:** M5 - Regression / `regression`.
**Plan Slice:** Non-executable tracker for #445-#451.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Track the strict native regression contract and exactly scoped real-data admission leaves.

## Acceptance Criteria

- [ ] Keep this mirror and live issue as a non-executable rollup.
- [ ] Route implementation only through hydrated executable leaves.
- [ ] Keep subissue/dependency state synchronized with the source plans.
- [ ] Do not infer capability admission from rollup state.

## Blocked by

- None.

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
