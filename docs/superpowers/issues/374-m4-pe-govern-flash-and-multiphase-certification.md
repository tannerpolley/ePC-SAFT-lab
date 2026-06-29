# M4 PE: govern flash and multiphase certification
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/374
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
**Intent:** Track TP flash and generalized multiphase certification under the shared PE contract.
**Target Output:** Flash/multiphase routes have a parent for phase-set completeness, selected/rejected candidates, and postsolve evidence.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Make flash and multiphase claims consume the shared PE contract plus phase-set residual blocks.
**Replaced Path:** Flash/multiphase validation that can pass without candidate completeness or noncollapse evidence.
**Acceptance Proof:** Future flash/multiphase leaves close against shared certification tests.
**Stop Criteria:** Stop if a route is an LLE subtype and belongs under LLE governance.
**Avoid:** Do not accept converged Ipopt states without phase-set certification.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Parent issue for flash and multiphase certification.

## Acceptance Criteria

- [ ] Flash/multiphase parent exists under the Phase Equilibrium parent.
- [ ] Issue body identifies phase-set completeness and postsolve evidence as required.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view this issue --json parent
