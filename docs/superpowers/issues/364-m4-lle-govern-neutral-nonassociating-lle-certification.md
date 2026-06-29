# M4 LLE: govern neutral nonassociating LLE certification
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/364
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
**Intent:** Track neutral nonassociating LLE under the shared contract.
**Target Output:** Neutral nonassociating LLE has replay, postsolve, source-backed tolerance, and capability evidence separated into executable leaves.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Replace synthetic or route-local neutral LLE proof with shared-contract neutral molecular residual evidence.
**Replaced Path:** Neutral LLE acceptance that is not tied to the shared production-route certification shape.
**Acceptance Proof:** Neutral nonassociating LLE leaves pass and the full package suite no longer fails on replay receipt semantics.
**Stop Criteria:** Stop if the current accepted route cannot be tied to its claimed discovery source.
**Avoid:** Do not set replay booleans true without proving the accepted result consumed the replayed candidate set.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Parent issue for neutral nonassociating LLE certification.

## Acceptance Criteria

- [ ] Replay-receipt and source-backed tolerance leaves exist.
- [ ] Neutral LLE proof avoids associating or electrolyte-specific residual assumptions.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view this issue --json subIssues
