# M4 PE: unify phase-equilibrium certification contracts
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/361
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
**Intent:** Create the parent tracker for one enforceable phase-equilibrium certification contract across production-exposed route families.
**Target Output:** The M4 roadmap shows a single parent for phase-equilibrium certification with family subtrees and a direct core-contract leaf.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Replace scattered family-only completion language with one parent hierarchy that owns shared PE certification.
**Replaced Path:** Ad hoc route-family completion claims without one parent contract.
**Acceptance Proof:** All approved child issues exist, #191 is nested under the electrolyte LLE subtree, and local mirrors/specs validate.
**Stop Criteria:** Stop if native sub-issue linking fails or if the tree duplicates an existing active parent.
**Avoid:** Do not close existing implementation issues or broaden capability claims from tracker creation alone.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Create and maintain the parent issue for the unified M4 phase-equilibrium certification hierarchy.

## Acceptance Criteria

- [ ] Native sub-issues include the core contract leaf and broad family parent issues.
- [ ] #191 is represented under the electrolyte LLE subtree.
- [ ] The parent body links the shared spec and issue-tree plan.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view this issue --json subIssues
- scripts/dev/validate_project.py docs
