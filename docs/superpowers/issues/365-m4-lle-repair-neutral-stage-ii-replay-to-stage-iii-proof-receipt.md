# M4 LLE: repair neutral Stage II replay-to-Stage III proof receipt

**Mirror Retention:** retain
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/365
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0365-neutral-lle-replay-receipt-plan.md
**Branch:** codex/m4-lle-repair-neutral-stage-ii-replay-to-stage-iii-proof-receipt
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/365 using the local mirror and docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0365-neutral-lle-replay-receipt-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary
**Outcome Source:** docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0365-neutral-lle-replay-receipt-plan.md#outcome-proof
**Intent:** Fix the current neutral LLE regression where Stage II replay metadata is ready but the accepted Stage III result comes from another seed.
**Target Output:** The accepted neutral LLE result either consumes the Stage II replay candidate set with retained receipt evidence or declines the HELD replay claim honestly.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Replace final-result replay flags that can drift from the accepted seed path.
**Replaced Path:** A final accepted neutral LLE result reporting Stage III complete while Stage III replay-source fields are empty.
**Acceptance Proof:** The focused route-provenance oracle and full package suite pass with accepted-seed evidence, and retained diagnostics prove the accepted seed source.
**Stop Criteria:** Stop if the accepted result cannot be scientifically tied to the Stage II candidate set without changing the route algorithm.
**Avoid:** Do not reduce assertions or set consumed-stage-II metadata after the fact.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Repair the neutral nonassociating LLE route/test contract around Stage II candidate replay and Stage III accepted-result provenance.

## Acceptance Criteria

- [x] Stage II replay-ready diagnostics remain retained.
- [x] The accepted Stage III result reports the real seed/candidate provenance.
- [x] Current failing neutral LLE tests pass for the right reason.

## Resolution Evidence

- Branch: `codex/m4-lle-repair-neutral-stage-ii-replay-to-stage-iii-proof-receipt`
- Native rebuild: `uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4` passed.
- Focused #365 oracle: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py::test_neutral_lle_stage_iii_route_refinement_records_stage_ii_replay_seed packages\epcsaft-equilibrium\tests\native\results\test_neutral_lle_reference_values.py::test_neutral_lle_synthetic_binary_accepts_split_with_exact_hessian -q` -> `2 passed in 4.64s`.
- Full package suite: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -q` -> `230 passed in 434.50s`.
- Plan validators: `validate-plan-task-use-cases.ps1` and `validate-plan-outcome-proof.ps1` passed for `docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0365-neutral-lle-replay-receipt-plan.md`.
- Docs validation: `uv run --no-sync python scripts\dev\validate_project.py docs` passed.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py::test_neutral_lle_stage_iii_route_refinement_records_stage_ii_replay_seed packages\epcsaft-equilibrium\tests\native\results\test_neutral_lle_reference_values.py::test_neutral_lle_synthetic_binary_accepts_split_with_exact_hessian -q
- uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -q
