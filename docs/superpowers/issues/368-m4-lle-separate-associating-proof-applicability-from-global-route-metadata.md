# M4 LLE: separate associating proof applicability from global route metadata

**Mirror Retention:** retain
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/368
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0368-neutral-lle-proof-applicability-plan.md
**Branch:** codex/m4-lle-repair-neutral-stage-ii-replay-to-stage-iii-proof-receipt
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/368 using the local mirror and docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0368-neutral-lle-proof-applicability-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary
**Outcome Source:** docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0368-neutral-lle-proof-applicability-plan.md#outcome-proof
**Intent:** Repair the stale neutral LLE metadata contract by separating family proof-route inventory from request-specific proof applicability.
**Target Output:** Nonassociating requests do not fail exact-list assertions because associating proof routes exist, while associating requests retain their proof-route evidence.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Replace exact global proof-route list assertions with request-aware metadata contract checks.
**Replaced Path:** One neutral LLE activation proof_routes list treated as both global capability inventory and per-request proof receipt.
**Acceptance Proof:** Route metadata tests pass and both associating and nonassociating proof applicability are asserted.
**Stop Criteria:** Stop if runtime cannot distinguish associating from nonassociating request applicability.
**Avoid:** Do not delete associating proof-route evidence to satisfy old nonassociating tests.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Refactor metadata/tests so global route-family proof inventory and request-specific proof applicability are separate and enforced.

## Acceptance Criteria

- [x] Nonassociating neutral LLE request asserts its own proof applicability.
- [x] Associating LLE request asserts Gross 2002 proof applicability.
- [x] Activation capability inventory still lists admitted evidence honestly.

## Resolution Evidence

- Branch: `codex/m4-lle-repair-neutral-stage-ii-replay-to-stage-iii-proof-receipt`
- Native rebuild: `uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4` passed.
- Focused #368 oracle: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_route_metadata_contracts.py packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py -q` -> `37 passed in 6.09s`.
- Full package suite: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -q` -> `230 passed in 434.50s`.
- Plan validators: `validate-plan-task-use-cases.ps1` and `validate-plan-outcome-proof.ps1` passed for `docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0368-neutral-lle-proof-applicability-plan.md`.
- Docs validation: `uv run --no-sync python scripts\dev\validate_project.py docs` passed.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_route_metadata_contracts.py packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py -q
