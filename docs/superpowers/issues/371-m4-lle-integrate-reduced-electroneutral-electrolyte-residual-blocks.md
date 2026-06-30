# M4 LLE: integrate reduced-electroneutral electrolyte residual blocks
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/371
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0371-electrolyte-reduced-electroneutral-residual-blocks-plan.md
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/371 using the local mirror and docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0371-electrolyte-reduced-electroneutral-residual-blocks-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only
**Branch:** codex/m4-electrolyte-lle-reduced-residual-contract

## Outcome Summary
**Outcome Source:** docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0371-electrolyte-reduced-electroneutral-residual-blocks-plan.md#outcome-proof
**Intent:** Attach electrolyte reduced-electroneutral residual equations and retained diagnostics to the shared certification contract.
**Target Output:** Public electrolyte LLE evidence reports the shared PE contract plus charge, lift/back-lift, projected transfer, mean-ionic, and active-block derivative diagnostics.
**Owner:** M4 equilibrium package owner.
**Interface:** GitHub native sub-issues, local issue mirrors, M4 spec/plan docs, validation checkers, and package-level route contracts.
**Cutover:** Replace electrolyte-only checker success with shared-contract electrolyte residual certification.
**Replaced Path:** Electrolyte route evidence that proves reduced residuals but not the common PE contract shape.
**Acceptance Proof:** Electrolyte public admission and scenario checkers pass while asserting shared contract fields.
**Stop Criteria:** Stop if accepted rows cannot prove projected electrochemical or modified mean-ionic residuals without raw single-ion equality.
**Avoid:** Do not use raw single-ion chemical-potential equality as acceptance evidence.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Add electrolyte residual-block assertions to the shared contract and public electrolyte LLE validation checks.

## Acceptance Criteria

- [ ] Reduced electroneutral basis and lift/back-lift residuals are retained.
- [ ] Projected electrochemical or mean-ionic transfer residuals pass.
- [ ] Born/SSM/DS active-block exactness is reported when enabled.

## Blocked by

- None.

## Non-goals

- No M5 parameter regression in this M4 tracker issue.
- No release claim.
- No downstream application metrics.
- No diagnostic-only success counted as production route support.

## Proof Oracle

- uv run --no-sync python scripts\validation\check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
- uv run --no-sync python scripts\validation\check_electrolyte_held2_public_route_scenarios.py --json --require-complete
