---
issue: 192
title: "M6: close GFPE registry, capability, and benchmark evidence"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/192
state: open
milestone: "M6 - Validation"
project: "ePC-SAFT Roadmap"
package: benchmark
capability: equilibrium
backend: Ipopt
readiness: "blocked"
release_target: future
source_spec: docs/superpowers/specs/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence.md
source_plan: docs/superpowers/plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md
afk_hitl: HITL
branch: codex/issue-0192-m6-close-gfpe-registry-capability-and-benchmark-evidence
last_synced: "2026-07-10"
---

# M6: close GFPE registry, capability, and benchmark evidence

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/192
**GitHub Milestone:** M6 - Validation
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence.md
**Source Plan:** docs/superpowers/plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md
**Plan Slice:** Tasks 1-3 (executable integration gate after #236/#455)
**Package Owner:** `benchmark`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** docs, validation, equilibrium, area:equilibrium, area:benchmark, backend:ipopt, status:blocked, type:task
**Goal Command:** None until prerequisites and explicit scheduling permit execution.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree task first
**Integration Policy:** Main-thread review and local integration
**TDD Policy:** Required
**Parallelization Plan:** Only non-overlapping owner slices after dependencies pass
**Reviewer Role:** Independent reviewer plus main-thread integrator
**Script Gate Mode:** Safety plus proof oracle
**Sub-Issue Role:** integration-gate
**Executable:** true
**Parent:** https://github.com/ePC-SAFT/ePC-SAFT/issues/194
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md#outcome-proof
**Intent:** Reconcile current public GFPE/capability registries with executable bubble/dew and scoped nonassociating hydrocarbon single-component VLE evidence.
**Owner:** M6 - Validation / `benchmark`.
**Plan Slice:** Tasks 1-3 (executable integration gate after #236/#455).
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Reconcile current public GFPE/capability registries with executable bubble/dew and scoped nonassociating hydrocarbon single-component VLE evidence.

## Acceptance Criteria

- [ ] Deliver exactly `Tasks 1-3 (executable integration gate after #236/#455)` within the `benchmark` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/188
- https://github.com/ePC-SAFT/ePC-SAFT/issues/189
- https://github.com/ePC-SAFT/ePC-SAFT/issues/190
- https://github.com/ePC-SAFT/ePC-SAFT/issues/191
- https://github.com/ePC-SAFT/ePC-SAFT/issues/236
- https://github.com/ePC-SAFT/ePC-SAFT/issues/455

## Non-goals

- Work only in the owner and plan slice named above.
- Treat package behavior and capability state as read-only inputs; route reproduced defects to the owning package issue.
- Use traceable source identities and current model receipts; do not fill missing inputs or relabel fitted values as literature.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-05-30-m6-validation-issue-0192-close-gfpe-registry-capability-and-benchmark-evidence-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <this mirror> --milestone-required
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
