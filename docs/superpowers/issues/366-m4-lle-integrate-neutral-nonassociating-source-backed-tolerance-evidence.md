# M4 LLE: integrate neutral nonassociating source-backed tolerance evidence
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/366
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/366 using the local mirror and docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary
**Outcome Source:** docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md#outcome-proof
**Intent:** Connect neutral nonassociating LLE source-backed data tolerance evidence to the shared certification contract.
**Target Output:** The neutral source-backed LLE showcase validates through the same shared certification shape used by production routes.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Move neutral nonassociating source-backed acceptance from isolated showcase evidence into shared PE contract evidence.
**Replaced Path:** Source-backed neutral LLE artifacts that do not prove the shared contract.
**Acceptance Proof:** The neutral source-backed checker/test records shared contract fields and declared tolerance margins.
**Stop Criteria:** Stop if retained source data or fitted-parameter provenance is missing.
**Avoid:** Do not hide new fitted parameters inside the route-validation path.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Update the neutral nonassociating source-backed LLE checker/tests to assert the shared contract and retained tolerance evidence.

## Acceptance Criteria

- [ ] Source-backed neutral LLE rows retain data provenance and tolerance margins.
- [ ] Shared certification fields are present for accepted rows.
- [ ] Any fitted parameters remain explicitly provenance-tagged.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "neutral and lle and source" -q
- uv run --no-sync python scripts\dev\validate_project.py docs
