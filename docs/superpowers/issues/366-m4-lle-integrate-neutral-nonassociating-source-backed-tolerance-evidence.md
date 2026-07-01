# M4 LLE: integrate neutral nonassociating source-backed tolerance evidence
**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/366
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0366-neutral-lle-source-backed-tolerance-evidence-plan.md
**Branch:** codex/m4-lle-neutral-source-backed-tolerance-evidence
**Classification:** AFK
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Goal Command:** /goal Resolve https://github.com/ePC-SAFT/ePC-SAFT/issues/366 using the local mirror and docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0366-neutral-lle-source-backed-tolerance-evidence-plan.md. Complete proof oracle: issue acceptance criteria checked and PR merged.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary
**Outcome Source:** docs/superpowers/plans/2026-06-30-m4-equilibrium-issue-0366-neutral-lle-source-backed-tolerance-evidence-plan.md#outcome-proof
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

- [x] Source-backed neutral LLE rows retain data provenance and tolerance margins.
- [x] Shared certification fields are present for accepted rows.
- [x] Any fitted parameters remain explicitly provenance-tagged.

## Resolution Evidence

- Branch: `codex/m4-lle-neutral-source-backed-tolerance-evidence`
- Plan validators: `validate-plan-task-use-cases.ps1` -> `ok=true`, `task_count=3`; `validate-plan-outcome-proof.ps1` -> `ok=true`, `use_case_count=12`.
- Focused #366 selector: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "neutral and lle and source" -q` -> `2 passed, 229 deselected in 7.38s`.
- Checker and registry contracts: `uv run --no-sync python -m pytest tests\native\contracts\test_neutral_lle_showcase_checker.py tests\native\contracts\test_equilibrium_benchmark_registry.py -q` -> `21 passed in 3.65s`.
- Checker JSON: `uv run --no-sync python scripts\validation\check_neutral_lle_showcase.py --json --require-complete` -> `complete=True`, `shared_certification.status=accepted`, `shared_certification.validation_blockers=[]`.
- Retained margins: composition `0.009933966384422677 <= 0.02`; phase fraction `0.025057997076718908 <= 0.03`; material balance `0.0 <= 1e-08`; pressure `7.473863661289215e-08 <= 0.001`; ln fugacity `7.474095342629994e-09 <= 1e-06`; phase distance `0.3472340466846786 >= 1e-06`.
- Source provenance: `source_data.status=source_backed`, `binary_interaction.status=source_fitted`, `k_ij=0.0662`.
- Docs validation: `uv run --no-sync python scripts\dev\validate_project.py docs` -> passed.

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
