---
issue: 328
title: "M4 CE: design standalone speciation public API and result schema"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/328
state: open
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: reactive
backend: Ipopt
readiness: "ready"
release_target: future
source_spec: docs/superpowers/specs/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission.md
source_plan: docs/superpowers/plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md
afk_hitl: AFK
branch: codex/issue-0328-m4-ce-design-standalone-speciation-public-api-and-result-schema
last_synced: "2026-07-10"
---

# M4 CE: design standalone speciation public API and result schema

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/328
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission.md
**Source Plan:** docs/superpowers/plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md
**Plan Slice:** Task 4 (execute first)
**Package Owner:** `equilibrium`
**AFK/HITL:** AFK
**Classification:** AFK
**Labels:** enhancement, agent-ready, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve issue #328 by executing its exact source-plan slice and proof oracle.
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
**Intent:** Implement the typed standalone-CE constructor request and deterministic result schema required by the generic checker.
**Owner:** M4 - Equilibrium / `equilibrium`.
**Plan Slice:** Task 4 (execute first).
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Implement the typed standalone-CE constructor request and deterministic result schema required by the generic checker.

## Acceptance Criteria

- [ ] Deliver exactly `Task 4 (execute first)` within the `equilibrium` owner boundary.
- [ ] Satisfy the issue body acceptance criteria and all native dependency prerequisites.
- [ ] Run both plan validators and every slice-specific proof command.
- [ ] Synchronize the live issue, local mirror, milestone page, and dependency readiness before handoff.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/325

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
