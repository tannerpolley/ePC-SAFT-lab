---
issue: 461
title: "M4 PE: admit neutral TP flash only after live source-backed proof"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/461
state: open
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: neutral_tp_flash
backend: Ipopt
readiness: "needs-design"
release_target: future
source_spec: docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
source_plan: docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
afk_hitl: HITL
branch: codex/issue-0461-m4-pe-admit-neutral-tp-flash-only-after-live-source-backed-proof
last_synced: "2026-07-10"
---

# M4 PE: admit neutral TP flash only after live source-backed proof

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/461
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
**Plan Slice:** Task 5; later design must create source, selector/refinement, evidence, and activation leaves.
**Package Owner:** `equilibrium`
**AFK/HITL:** HITL
**Classification:** HITL
**Labels:** enhancement, docs, validation, equilibrium, area:equilibrium, backend:ipopt, type:feature, status:needs-design
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
**Parent:** https://github.com/ePC-SAFT/ePC-SAFT/issues/361
**Project Membership:** Unverified because the active token lacks `read:project`; milestone/type/subissue/dependency state is live and verified.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md#outcome-proof
**Intent:** Non-executable admission rollup requiring a live source-backed TP-flash problem, selector-owned solve, canonical result acceptance, and explicit capability activation.
**Owner:** M4 - Equilibrium / `equilibrium`.
**Plan Slice:** Task 5; later design must create source, selector/refinement, evidence, and activation leaves..
**Proof:** The issue-specific acceptance criteria, dependency state, and source-plan oracle below are authoritative.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Separate user approval before any remote push or merge
**Merge Policy:** Follow the repository's issue-resolution and review policy
**Worktree Cleanup Policy:** Remove only task-owned scratch after verification
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Non-executable admission rollup requiring a live source-backed TP-flash problem, selector-owned solve, canonical result acceptance, and explicit capability activation.

## Acceptance Criteria

- [ ] Keep this mirror and live issue as a non-executable rollup.
- [ ] Route implementation only through hydrated executable leaves.
- [ ] Keep subissue/dependency state synchronized with the source plans.
- [ ] Do not infer capability admission from rollup state.
- [ ] Complete a separate source/route/evidence/activation design before creating executable leaves.

## Blocked by

- https://github.com/ePC-SAFT/ePC-SAFT/issues/444

## Non-goals

- Work only in the owner and plan slice named above.
- Preserve current public route state unless this issue is a separately proven admission leaf.
- Keep provider serialization and retained paper artifacts in their M3/M6 owners.
- Finite sampled candidates are local evidence and cannot establish globally complete phase discovery.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
uv run --no-sync python scripts/validate_issue_mirror.py --issue-file <this mirror> --milestone-required
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```
