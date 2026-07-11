---
issue: 445
title: "M5: require strict target and source contracts"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/445
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
afk_hitl: AFK
branch: codex/issue-0445-m5-require-strict-target-and-source-contracts
last_synced: "2026-07-10"
---

# M5: require strict target and source contracts

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/445
**GitHub Milestone:** M5 - Regression
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m5-regression-traceable-native-problem-contract.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md
**Plan Slice:** Task 1
**Package Owner:** `regression`
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** regression, validation, area:regression, backend:ceres, agent-ready, type:task, status:ready
**Goal Command:** /goal Resolve issue #445 by executing its exact source-plan slice and proof oracle.
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
**Intent:** Replace loose regression target mappings with strict observation/source records whose units, scales, weights, and provenance are explicit and reject unknown fields.
**Owner:** M5 - Regression / `regression`.
**Plan Slice:** Task 1.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Replace loose regression target mappings with strict observation/source records whose units, scales, weights, and provenance are explicit and reject unknown fields.

## Acceptance Criteria

- [ ] Deliver exactly `Task 1` within the `regression` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

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
