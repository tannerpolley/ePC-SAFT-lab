---
issue: 444
title: "M3: publish resolved-input SDK v1 and remove displaced serializers"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/444
state: open
milestone: "M3 - EOS"
project: "ePC-SAFT Roadmap"
package: core
capability: eos
backend: native
readiness: "blocked"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m3-eos-versioned-state-resolved-model-input.md
source_plan: docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md
afk_hitl: HITL
branch: codex/issue-0444-m3-publish-resolved-input-sdk-v1-and-remove-displaced-serializers
last_synced: "2026-07-10"
---

# M3: publish resolved-input SDK v1 and remove displaced serializers

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/444
**GitHub Milestone:** M3 - EOS
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m3-eos-versioned-state-resolved-model-input.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md
**Plan Slice:** Task 8, coordinated SDK cutover and deletion
**Package Owner:** `core`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** native, python-api, docs, validation, area:core, type:task, status:blocked
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
**Parent:** https://github.com/ePC-SAFT/ePC-SAFT/issues/439
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-10-m3-eos-versioned-state-resolved-model-input-plan.md#outcome-proof
**Intent:** Publish the versioned provider contract only after provider, equilibrium, and regression consumers are integrated, then delete superseded option files and serializers without compatibility shims.
**Owner:** M3 - EOS / `core`.
**Plan Slice:** Task 8, coordinated SDK cutover and deletion.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Publish the versioned provider contract only after provider, equilibrium, and regression consumers are integrated, then delete superseded option files and serializers without compatibility shims.

## Acceptance Criteria

- [ ] Deliver exactly `Task 8, coordinated SDK cutover and deletion` within the `core` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/442
- https://github.com/ePC-SAFT/ePC-SAFT/issues/443
- https://github.com/ePC-SAFT/ePC-SAFT/issues/447

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
