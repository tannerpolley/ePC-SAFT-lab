# M4 PE: govern boundary-route certification
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/375
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
**Intent:** Track bubble, dew, cloud, shadow, and branch-traced boundary workflows under the shared PE contract.
**Target Output:** Boundary routes have a parent for traced parent states, DOF swaps, branch provenance, and source-row tolerance evidence.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Make boundary-route claims consume the shared PE contract plus boundary residual/trace blocks.
**Replaced Path:** Boundary proof that is disconnected from parent phase-set certification.
**Acceptance Proof:** Future boundary leaves close with retained branch traces and shared contract fields.
**Stop Criteria:** Stop if source data require parameter regression rather than route validation.
**Avoid:** Do not report branch-traced diagnostics as production exposure unless public admission passes.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Parent issue for boundary-route certification.

## Acceptance Criteria

- [ ] Boundary parent exists under the Phase Equilibrium parent.
- [ ] Issue body covers bubble/dew/cloud/shadow and trace evidence.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view this issue --json parent
