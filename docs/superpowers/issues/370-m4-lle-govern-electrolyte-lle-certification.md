# M4 LLE: govern electrolyte LLE certification
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/370
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
**Classification:** HITL
**Labels:** enhancement, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:task
**Goal Command:** None; tracking parent issue.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary
**Outcome Source:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md#outcome-proof
**Intent:** Track electrolyte LLE under the shared contract with reduced-electroneutral residual blocks.
**Target Output:** #191 and its retained electrolyte HELD2 history sit under the electrolyte LLE subtree, and new leaves enforce shared residual semantics.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Make electrolyte LLE support claims require both shared PE contract fields and electrolyte reduced-basis residual evidence.
**Replaced Path:** Electrolyte HELD2 evidence that is not governed by a common PE contract parent.
**Acceptance Proof:** #191 is reparented under this issue and electrolyte shared-contract leaves pass.
**Stop Criteria:** Stop if #191 cannot be reparented without losing its child issue history.
**Avoid:** Do not rewrite electrolyte history or close #191 from hierarchy work alone.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Parent issue for electrolyte LLE certification and #191 subtree placement.

## Acceptance Criteria

- [ ] #191 is a native sub-issue of this parent.
- [ ] Electrolyte residual integration leaf exists.
- [ ] Closed electrolyte evidence remains traceable.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view this issue --json subIssues
- gh issue view 191 --json parent
