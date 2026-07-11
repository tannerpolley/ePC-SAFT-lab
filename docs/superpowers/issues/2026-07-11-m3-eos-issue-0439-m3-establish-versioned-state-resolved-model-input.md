---
issue: 439
title: "M3: establish versioned state-resolved model input"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/439
state: open
milestone: "M3 - EOS"
project: "ePC-SAFT Roadmap"
package: core
capability: eos
backend: native
readiness: "ready"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m3-eos-versioned-state-resolved-model-input.md
source_plan: docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md
afk_hitl: HITL
branch: codex/issue-0439-m3-establish-versioned-state-resolved-model-input
last_synced: "2026-07-10"
---

# M3: establish versioned state-resolved model input

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/439
**GitHub Milestone:** M3 - EOS
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m3-eos-versioned-state-resolved-model-input.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md
**Plan Slice:** Plan rollup; Tasks 1-8 execute through provider leaves plus milestone-owned consumers.
**Package Owner:** `core`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** native, python-api, validation, area:core, type:task, status:ready
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

**Outcome Source:** docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md#outcome-proof
**Intent:** Track the incompatible provider cutover from permissive options and duplicate serializers to one strict versioned, state-resolved native-input graph.
**Owner:** M3 - EOS / `core`.
**Plan Slice:** Plan rollup; Tasks 1-8 execute through provider leaves plus milestone-owned consumers..
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Track the incompatible provider cutover from permissive options and duplicate serializers to one strict versioned, state-resolved native-input graph.

## Acceptance Criteria

- [ ] Keep this mirror and live issue as a non-executable rollup.
- [ ] Route implementation only through hydrated executable leaves.
- [ ] Keep subissue/dependency state synchronized with the source plans.
- [ ] Do not infer capability admission from rollup state.

## Blocked by

- None.

## Non-goals

- Work only in the owner and plan slice named above.
- Reject incomplete configuration; add no inferred defaults, compatibility serializers, or alternate payload owners.
- M4/M5 consumers and paper-bundle repairs remain in their milestone-owned issues.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <this mirror> --milestone-required
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
