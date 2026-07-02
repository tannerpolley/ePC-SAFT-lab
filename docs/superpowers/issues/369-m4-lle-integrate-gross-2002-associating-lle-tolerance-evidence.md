# M4 LLE: integrate Gross 2002 associating LLE tolerance evidence

**Mirror Retention:** retain
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/369
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0369-gross-2002-associating-lle-tolerance-evidence-plan.md
**Branch:** codex/m4-associating-lle-gross-tolerance-evidence
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/369 using the local mirror and docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0369-gross-2002-associating-lle-tolerance-evidence-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary
**Outcome Source:** docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0369-gross-2002-associating-lle-tolerance-evidence-plan.md#outcome-proof
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

- [x] Accepted Gross associating LLE rows include shared PE contract fields.
- [x] Active association derivative receipts remain retained.
- [x] Out-of-tolerance model gaps are split to M5 instead of hidden.

## Resolution Evidence

- Branch: `codex/m4-associating-lle-gross-tolerance-evidence`
- Baseline issue selector before this branch: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "associating and lle and certification" -q` -> `231 deselected`; no real package tests collected.
- Plan validators: `validate-plan-task-use-cases.ps1` -> `ok=true`, `task_count=3`; `validate-plan-outcome-proof.ps1` -> `ok=true`, `use_case_count=12`.
- Focused #369 selector after this branch: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "associating and lle and certification" -q` -> `2 passed, 231 deselected in 0.99s`.
- Checker and registry contracts: `uv run --no-sync python -m pytest tests\native\contracts\test_gross_2002_association_acceptance_checker.py tests\native\contracts\test_equilibrium_benchmark_registry.py -q` -> `22 passed in 1.63s`.
- Checker JSON: `uv run --no-sync python scripts\validation\check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native` -> `complete=True`, `shared_certification.status=accepted`, `blockers=[]`.
- Figure 8 source margins: source points `16 >= 16`; normalized plot score `9.9082422421564 >= 7`; branch coverage `1 >= 1`; mass-action residual `3.28626015289046e-14 <= 1e-08`; derivative status `verified_exact`.
- Figure 10 source margins: source points `24 >= 8`; normalized plot score `10 >= 7`; branch coverage `1 >= 1`; mass-action residual `2.22044604925031e-16 <= 1e-08`; derivative status `verified_exact`.
- Overlay gaps retained outside M4 route acceptance: Figure 8 overlay max abs `2.15931131017386 degC`, Figure 10 overlay max abs `94.9995491412937 degC`, both `regression_followup_not_m4_acceptance` and `counts_toward_completion=false`.
- Docs validation: `uv run --no-sync python scripts\dev\validate_project.py docs` -> passed.

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
