# M4 LLE: integrate Gross 2002 associating LLE tolerance evidence
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/369
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/369 using the local mirror and docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary
**Outcome Source:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md#outcome-proof
**Intent:** Connect Gross 2002 associating LLE/VLLE validation evidence to the shared certification contract.
**Target Output:** Associating LLE accepted rows retain shared contract fields, active association derivative receipts, and declared data tolerance results.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Move Gross 2002 associating LLE evidence from standalone replication artifacts into shared PE contract gates.
**Replaced Path:** Associating paper-validation evidence that does not enforce the shared route certificate.
**Acceptance Proof:** Gross associating checker/tests prove shared contract rows without broadening unsupported associating surfaces.
**Stop Criteria:** Stop if source-backed tolerance cannot pass without M5 parameter regression.
**Avoid:** Do not tune parameters inside M4 validation to pass figure tolerance.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add shared-contract assertions to Gross 2002 associating LLE validation and route evidence.

## Acceptance Criteria

- [ ] Accepted Gross associating LLE rows include shared PE contract fields.
- [ ] Active association derivative receipts remain retained.
- [ ] Out-of-tolerance model gaps are split to M5 instead of hidden.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- uv run --no-sync python scripts\validation\check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
- uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "associating and lle and certification" -q
