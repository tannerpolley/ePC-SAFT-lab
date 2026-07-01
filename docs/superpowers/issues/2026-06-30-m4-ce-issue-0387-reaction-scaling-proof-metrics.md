# M4 CE: improve reaction scaling and proof metrics

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/387
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-convergence-robustness-hardening.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Improve CE reaction scaling and diagnostics while preserving strict unscaled proof metrics.
**Branch:** codex/m4-ce-generic-pope-homotopy-continuation
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Current thread owns PR
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md#outcome-proof
**Intent:** Improve solver conditioning for hard reaction sets while keeping final physical stationarity and balance gates strict.
**Target Output:** Diagnostics report reaction scaling factors, scaled solver residuals, and unscaled physical proof norms.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** Native CE reaction basis, scaling diagnostics, proof metrics, and checker thresholds.
**Cutover:** Scaling fixes conditioning pressure instead of weakening stationarity tolerances.
**Replaced Path:** Tolerance pressure and opaque reaction residual scaling are replaced by explicit solver scaling plus physical proof metrics.
**Acceptance Proof:** Focused tests cover badly scaled reactions and prove accepted results satisfy unchanged unscaled stationarity and balance gates.
**Stop Criteria:** Stop if scaling changes the physical proof definition or hides large unscaled residuals.
**Avoid:** Do not relax acceptance tolerances, change reaction chemistry, or add public scaling knobs.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 5 from the source plan: reaction scaling and proof metric diagnostics that improve conditioning without weakening proof.

## Acceptance Criteria

- [ ] Tests cover badly scaled `ln_K`, tiny species, and near-dependent reaction rows.
- [ ] Diagnostics include scaling factors plus scaled and unscaled stationarity.
- [ ] Accepted proof uses unchanged physical stationarity and balance thresholds.
- [ ] Checker output stays strict and interpretable.

## Resolution Evidence

- Native CE results now expose `proof_metrics` with `reaction_scaling_factors`, `reaction_row_norms`, min/max scaling, `reaction_basis_condition_estimate`, `scaled_reaction_stationarity_inf_norm`, and `unscaled_reaction_stationarity_inf_norm`.
- Physical proof-corrector rows are scaled with the same reaction factors for residuals and Jacobian rows, while accepted proof still gates on unchanged unscaled `reaction_stationarity_inf_norm` and `balance_inf_norm`.
- Public `ReactiveSpeciationResult.diagnostics` preserves `proof_metrics` from the native payload.
- The standalone CE checker now emits proof metrics in the single-solution, oracle, and MEA evidence JSON and rejects missing or mismatched unscaled stationarity metrics.
- Focused red proof: `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py::test_ce_proof_reports_reaction_scaling_for_large_log_k_tiny_species packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py::test_ce_proof_reports_near_dependent_reaction_basis_conditioning -q` failed on missing `proof_metrics` before implementation.
- Fresh proof: `uv run --no-sync python scripts/dev/build_epcsaft.py --build-only --parallel 10` passed.
- Fresh proof: `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py -q` passed with 4 tests.
- Fresh proof: `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py -q` passed with 13 tests.
- Fresh proof: `uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete` returned status `complete` with no blockers.

## Blocked by

- None

## Non-goals

- Looser tolerances.
- Public scaling controls.
- Chemistry-specific special cases.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- Focused native/checker commands from Task 5 of the source plan.
