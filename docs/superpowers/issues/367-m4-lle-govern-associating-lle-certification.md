# M4 LLE: govern associating LLE certification

**Mirror Retention:** retain
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/367
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
**Branch:** codex/m4-associating-lle-parent-closeout
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
**Intent:** Track associating LLE under the shared contract with association-aware residual and derivative evidence.
**Target Output:** Associating LLE validation uses active association terms, request-specific proof applicability, and source-backed tolerance evidence.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Replace route-family metadata ambiguity with request-specific associating proof receipts.
**Replaced Path:** Global neutral LLE proof-route lists interpreted as request-specific proof usage.
**Acceptance Proof:** Associating LLE leaves pass and nonassociating requests no longer fail because associating proof metadata was added globally.
**Stop Criteria:** Stop if association terms or derivative receipts cannot be traced for accepted associating rows.
**Avoid:** Do not treat associating systems as neutral nonassociating systems with renamed metadata.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Parent issue for associating LLE certification.

## Acceptance Criteria

- [x] Associating metadata and Gross tolerance leaves exist.
- [x] Association derivative and data-tolerance evidence are required for associating claims.

## Resolution Evidence

- Branch: `codex/m4-associating-lle-parent-closeout`
- Sub-issue proof: `gh issue view 367 --repo ePC-SAFT/ePC-SAFT --json subIssues` reports exactly two sub-issues, #368 and #369, both `CLOSED`.
- #368 closed by PR #379 with request-specific associating proof applicability separated from global route-family proof metadata.
- #369 closed by PR #383 with Gross 2002 Figure 8 and Figure 10 source margins retained, shared `neutral_lle` certification accepted, exact association derivative receipts retained, and literature-overlay gaps marked outside M4 route acceptance.
- Associating proof boundary: #368/#369 evidence stays scoped to retained Gross/Sadowski 2002 associating proof rows and does not broaden electrolyte, reactive, CE/CPE, generalized phase-set, or M5 regression claims.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view this issue --json subIssues
