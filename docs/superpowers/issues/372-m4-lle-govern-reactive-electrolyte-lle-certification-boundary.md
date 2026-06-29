# M4 LLE: govern reactive electrolyte LLE certification boundary
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/372
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
**Intent:** Define the boundary for future reactive electrolyte LLE without admitting it before CE/CPE prerequisites pass.
**Target Output:** Reactive electrolyte LLE is visible in the hierarchy as planned/blocked work, not as an accidental electrolyte LLE capability claim.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Route reactive electrolyte LLE through CE/CPE prerequisites before any production exposure.
**Replaced Path:** Implicit reactive electrolyte LLE expectations hidden inside electrolyte LLE issue bodies.
**Acceptance Proof:** The issue records blockers and no public reactive electrolyte LLE capability claim exists.
**Stop Criteria:** Stop until standalone CE and CPE contracts provide the required transformed-species basis.
**Avoid:** Do not implement reactive electrolyte LLE in this tracker issue.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Parent issue for reactive electrolyte LLE boundary and prerequisites.

## Acceptance Criteria

- [ ] The issue links CE/CPE prerequisites.
- [ ] Capability registries keep reactive electrolyte LLE planned or closed.
- [ ] No implementation leaf is marked AFK until prerequisites are satisfied.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view 331 --json number,state,title
