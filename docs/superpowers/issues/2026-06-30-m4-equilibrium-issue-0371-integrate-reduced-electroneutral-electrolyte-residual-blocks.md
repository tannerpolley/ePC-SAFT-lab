---
issue: 371
title: "M4 LLE: integrate reduced-electroneutral electrolyte residual blocks"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/371
state: closed
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: null
backend: Ipopt
readiness: closed
release_target: equilibrium-0.x
source_spec: null
source_plan: null
afk_hitl: AFK
branch: null
last_synced: "2026-06-30"
---

# M4 LLE: integrate reduced-electroneutral electrolyte residual blocks

**Mirror Retention:** Keep
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/371
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0371-electrolyte-reduced-electroneutral-residual-blocks-plan.md
**AFK/HITL:** AFK
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

- [x] Reduced electroneutral basis and lift/back-lift residuals are retained.
- [x] Projected electrochemical or mean-ionic transfer residuals pass.
- [x] Born/SSM/DS active-block exactness is reported when enabled.

## Resolution Evidence

- Branch: `codex/m4-electrolyte-lle-reduced-residual-contract`
- Plan validators: `validate_plan_task_use_cases.py` -> `ok=true`, `task_count=3`; `validate_plan_outcome_proof.py` -> `ok=true`, `use_case_count=12`.
- Focused #371 selector before implementation: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and residual" -q` -> `2 failed, 233 deselected`; both failures were expected `KeyError: 'shared_certification'`.
- Focused #371 selector after implementation: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and residual" -q` -> `2 passed, 233 deselected in 135.53s`.
- Public admission proof: `uv run --no-sync python scripts\validation\check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete` -> `complete=true`, `blockers=[]`, `shared_certification.status=accepted`, `shared_certification.validation_blockers=[]`.
- Shared electrolyte residuals retained: reduced basis `counterion_pair_transformed_variables`, lift/back-lift charge residual `0.0`, lift/back-lift round-trip residual `0.0`, phase charge residual `0.0`, projected charged transfer `mean_ionic_counterion_pairs`, `raw_single_ion_equality_used=false`.
- Projected/mean-ionic residual proof: `projected_transfer.enforced_in_solver=true`, equation families include `mean_ionic_transfer`, mean-ionic residual `4.104478534827649e-08 <= 1.0e-4`.
- Active-block exactness proof: Born/SSM/DS exactness `accepted`, exact reduced Jacobian `true`, exact reduced Hessian `true`, route Hessian backend `cppad_phase_system_projected_electrolyte_residuals`.
- Scenario proof: `uv run --no-sync python scripts\validation\check_electrolyte_held2_public_route_scenarios.py --json --require-complete` -> `complete=true`, `blockers=[]`, `accepted_scenario_count=7`; public-route scenario rows carry accepted `shared_certification`.
- Checker and registry contracts: `uv run --no-sync python -m pytest tests\native\contracts\test_electrolyte_public_admission.py tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q` -> `39 passed in 93.06s`.
- Docs validation: `uv run --no-sync python scripts\dev\validate_project.py docs` -> `build succeeded`.

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
