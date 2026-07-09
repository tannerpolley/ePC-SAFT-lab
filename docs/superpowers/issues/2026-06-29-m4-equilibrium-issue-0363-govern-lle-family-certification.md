---
issue: 363
title: "M4 PE: govern LLE family certification"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/363
state: open
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: null
backend: Ipopt
readiness: blocked
release_target: equilibrium-0.x
source_spec: docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
source_plan: docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
afk_hitl: HITL
branch: codex/issue-0363-govern-lle-family-certification
last_synced: "2026-06-29"
---

# M4 PE: govern LLE family certification
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/363
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Task
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
**AFK/HITL:** HITL
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
**Intent:** Track all LLE-specific certification blocks under the shared phase-equilibrium contract.
**Target Output:** Neutral, associating, electrolyte, and reactive-electrolyte LLE each have their own parent and PR-sized leaf issues.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Make LLE support claims flow through the shared contract plus LLE residual blocks.
**Replaced Path:** Independent LLE validation lanes with inconsistent acceptance semantics.
**Acceptance Proof:** All detailed LLE parent issues exist and accepted LLE routes pass family-specific residual gates.
**Stop Criteria:** Stop if an LLE subtype cannot be assigned to a concrete parent without changing its scientific meaning.
**Avoid:** Do not collapse electrolyte or associating residuals into neutral molecular fugacity checks.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Parent issue for LLE family contract governance.

## Acceptance Criteria

- [ ] Detailed LLE parents exist for neutral nonassociating, associating, electrolyte, and reactive electrolyte LLE.
- [ ] Each LLE detail parent links at least one executable leaf or an explicit blocker.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- gh issue view this issue --json subIssues
