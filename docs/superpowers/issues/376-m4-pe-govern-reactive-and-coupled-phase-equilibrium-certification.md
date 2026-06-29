# M4 PE: govern reactive and coupled phase-equilibrium certification
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/376
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
**Intent:** Track reactive and coupled phase-equilibrium certification after standalone CE prerequisites.
**Target Output:** CPE work is represented as phase-equilibrium family governance without bypassing CE foundation gates.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Put CPE route claims behind standalone CE and transformed-species contract evidence.
**Replaced Path:** Reactive phase-equilibrium expectations scattered across CE, electrolyte, and phase-route issues.
**Acceptance Proof:** #331 or successor CPE issue is linked under this parent, and no CPE production claim bypasses CE.
**Stop Criteria:** Stop until standalone CE foundation and API/schema issues are resolved.
**Avoid:** Do not implement CPE before CE basis and result schema are governed.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Parent issue for reactive/coupled phase-equilibrium certification.

## Acceptance Criteria

- [ ] Reactive/CPE parent exists under the Phase Equilibrium parent.
- [ ] #331 is linked or cited as the current CPE prerequisite.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view 331 --json number,state,title,parent
