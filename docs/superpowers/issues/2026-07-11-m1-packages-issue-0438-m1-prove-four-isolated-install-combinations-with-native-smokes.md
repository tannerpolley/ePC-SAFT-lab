---
issue: 438
title: "M1: prove four isolated install combinations with native smokes"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/438
state: open
milestone: "M1 - Packages"
project: "ePC-SAFT Roadmap"
package: build
capability: packaging
backend: native
readiness: "blocked"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m1-local-linux-package-reproducibility.md
source_plan: docs/superpowers/plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md
afk_hitl: HITL
branch: codex/issue-0438-m1-prove-four-isolated-install-combinations-with-native-smokes
last_synced: "2026-07-10"
---

# M1: prove four isolated install combinations with native smokes

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/438
**GitHub Milestone:** M1 - Packages
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-07-10-m1-local-linux-package-reproducibility.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md
**Plan Slice:** Tasks 3-5
**Package Owner:** `build`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** packaging, native, validation, area:build, type:task, status:blocked
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
**Parent:** https://github.com/ePC-SAFT/ePC-SAFT/issues/435
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-10-m1-local-linux-package-reproducibility-plan.md#outcome-proof
**Intent:** Install exact local wheels into four external environments, run native smokes, verify every installed module's ELF closure, cut over docs/callers, and validate the one-run receipt.
**Owner:** M1 - Packages / `build`.
**Plan Slice:** Tasks 3-5.
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Install exact local wheels into four external environments, run native smokes, verify every installed module's ELF closure, cut over docs/callers, and validate the one-run receipt.

## Acceptance Criteria

- [ ] Deliver exactly `Tasks 3-5` within the `build` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/437
- https://github.com/ePC-SAFT/ePC-SAFT/issues/444
- https://github.com/ePC-SAFT/ePC-SAFT/issues/449

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
