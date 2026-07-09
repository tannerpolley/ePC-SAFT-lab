---
issue: 374
title: "M4 PE: govern flash and multiphase certification"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/374
state: closed
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: null
backend: Ipopt
readiness: closed
release_target: equilibrium-0.x
source_spec: null
source_plan: null
afk_hitl: HITL
branch: null
last_synced: "2026-06-29"
---

# M4 PE: govern flash and multiphase certification

**Mirror Retention:** Keep
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/374
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
**AFK/HITL:** HITL
**Branch:** codex/m4-flash-multiphase-parent-closeout
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

## Flash/Multiphase Residual Ownership

This parent owns phase-set completeness, selected and rejected phase-candidate evidence, noncollapse checks, material reconstruction, phase amounts, pressure and transfer postsolve residuals, and solver route receipts for TP flash and generalized multiphase routes. LLE subtype evidence remains under #363 and its children. Boundary tracing, including bubble, dew, cloud, and shadow workflows, remains under #375.

## Acceptance Criteria

- [x] Flash/multiphase parent exists under the Phase Equilibrium parent.
- [x] Issue body identifies phase-set completeness and postsolve evidence as required.

## Resolution Evidence

- Branch: `codex/m4-flash-multiphase-parent-closeout`
- Parent proof: `gh issue view 374 --repo ePC-SAFT/ePC-SAFT --json parent,state,title` reports `state=OPEN`, parent `#361`, and title `M4 PE: unify phase-equilibrium certification contracts`.
- Residual ownership proof: this mirror assigns phase-set completeness, selected/rejected candidate evidence, noncollapse checks, material reconstruction, phase amounts, pressure and transfer postsolve residuals, and solver route receipts to #374 while keeping LLE subtype evidence under #363 and boundary tracing under #375.
- Flash/multiphase proof boundary: this closeout creates no new flash route admission, no release claim, and no M5 parameter-regression claim.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view this issue --json parent
