# M4 PE: govern VLE family certification
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/373
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
**Branch:** codex/m4-vle-family-parent-closeout
**Classification:** HITL
**Labels:** enhancement, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:task
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
**Intent:** Track VLE-specific certification under the shared phase-equilibrium contract.
**Target Output:** VLE routes have a parent for vapor-liquid transfer, saturation, exact-Hessian, and data-tolerance evidence.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Make VLE route claims consume the shared PE contract plus VLE residual block.
**Replaced Path:** VLE route-specific proof without a common PE contract parent.
**Acceptance Proof:** Future VLE leaves close against the shared contract without weakening existing Gross/pure-component evidence.
**Stop Criteria:** Stop if a VLE route is actually a boundary workflow and belongs under boundary-route governance.
**Avoid:** Do not conflate VLE boundary tracing with generic TP flash.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Parent issue for VLE family certification.

## VLE Residual Ownership

This parent owns vapor-liquid transfer residuals, saturation consistency, exact-Hessian route receipts, and source-backed VLE data-tolerance evidence. Boundary-route tracing, including bubble and dew workflows, remains under #375. Generic TP flash and multiphase phase-set completeness remain under #374.

## Acceptance Criteria

- [x] VLE parent exists under the Phase Equilibrium parent.
- [x] Issue body defines VLE residual ownership and non-goals.

## Resolution Evidence

- Branch: `codex/m4-vle-family-parent-closeout`
- Parent proof: `gh issue view 373 --repo ePC-SAFT/ePC-SAFT --json parent,state,title` reports `state=OPEN`, parent `#361`, and title `M4 PE: unify phase-equilibrium certification contracts`.
- Residual ownership proof: this mirror assigns vapor-liquid transfer, saturation consistency, exact-Hessian route receipts, and source-backed VLE data tolerance to #373 while keeping boundary tracing under #375 and flash/multiphase phase-set completeness under #374.
- VLE proof boundary: this closeout creates no new VLE route admission, no release claim, and no M5 parameter-regression claim.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view this issue --json parent
