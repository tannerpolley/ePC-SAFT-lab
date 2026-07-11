---
issue: 436
title: "M1: record active Linux environment and receipt contract"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/436
state: open
milestone: "M1 - Packages"
project: "ePC-SAFT Roadmap"
package: build
capability: packaging
backend: native
readiness: "ready"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m1-local-linux-package-reproducibility.md
source_plan: docs/superpowers/plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md
afk_hitl: AFK
branch: codex/issue-0436-m1-record-active-linux-environment-and-receipt-contract
last_synced: "2026-07-10"
---

# M1: record active Linux environment and receipt contract

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/436
**GitHub Milestone:** M1 - Packages
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m1-local-linux-package-reproducibility.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md
**Plan Slice:** Task 1
**Package Owner:** `build`
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** packaging, validation, area:build, type:task, status:ready, agent-ready
**Goal Command:** /goal Resolve issue #436 by executing its exact source-plan slice and proof oracle.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree task first
**Integration Policy:** Main-thread review and local integration
**TDD Policy:** Required
**Parallelization Plan:** Only non-overlapping owner slices after dependencies pass
**Reviewer Role:** Independent reviewer plus main-thread integrator
**Script Gate Mode:** Safety plus proof oracle
**Sub-Issue Role:** leaf
**Executable:** true
**Parent:** https://github.com/ePC-SAFT/ePC-SAFT/issues/435
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md#outcome-proof
**Intent:** Define the strict current-host receipt, dirty-tree refusal, dependency identity, and independent receipt-validation contract.
**Owner:** M1 - Packages / `build`.
**Plan Slice:** Task 1.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Define the strict current-host receipt, dirty-tree refusal, dependency identity, and independent receipt-validation contract.

## Acceptance Criteria

- [ ] Deliver exactly `Task 1` within the `build` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

## Blocked by

- None.

## Non-goals

- Work only in the owner and plan slice named above.
- The receipt proves only the recorded Zorin/Python host and exact local artifacts; it is not a portability or distribution claim.
- Packaging proof must not change scientific capability metadata or weaken native smokes to import-only checks.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <this mirror> --milestone-required
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
