# M4 CE: add extent/nullspace feasible initialization

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/388
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** task
**Source Spec:** docs/superpowers/specs/2026-06-30-m4-ce-convergence-robustness-hardening.md
**Source Plan:** docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
**Classification:** AFK
**Labels:** agent-ready,status:ready,type:task,area:equilibrium,equilibrium,solver,native,backend:ipopt,validation
**Goal Command:** /goal Add extent/nullspace feasible initialization as a CE-owned start path with conservation and positivity proof.
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
**Intent:** Add a second independent feasible-start path based on extents or conservation nullspace when max-min initialization is weak.
**Target Output:** Initializer diagnostics report conservation closure, positivity, rank status, selected candidate, and rejection reason.
**Owner:** M4 equilibrium package owner for packages/epcsaft-equilibrium.
**Interface:** CE feasible-initialization native helpers, initialization ladder, native bindings, and result diagnostics.
**Cutover:** A ranked initializer ladder replaces reliance on a single CE-owned initializer.
**Replaced Path:** Max-min-only initialization is displaced by max-min plus extent/nullspace candidates with proof diagnostics.
**Acceptance Proof:** Focused native tests prove full-rank, rank-deficient, charged, and tiny-feasible systems are initialized or rejected correctly.
**Stop Criteria:** Stop if rank ambiguity would be hidden or if the initializer cannot prove conservation closure before solve.
**Avoid:** Do not add source-oracle seeds, silent rank repair, or public initializer routes.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Inline run

## What To Build

Implement Task 6 from the source plan: extent/nullspace initialization and initializer-ladder diagnostics.

## Acceptance Criteria

- [ ] Native tests cover full-rank, rank-deficient, charged, and tiny-feasible systems.
- [ ] Diagnostics prove conservation closure and positivity before proof solve.
- [ ] The initializer ladder records each attempted initializer and selected seed.
- [ ] Ambiguous or infeasible rank cases fail loudly with a classified reason.

## Resolution Evidence

- Native feasible initialization now reports a ranked initializer ladder with `attempt_order`, `selected_initializer`, and per-attempt diagnostics for `max_min_feasible_interior` and `extent_nullspace_feasible`.
- The extent/nullspace attempt builds a deterministic positive candidate from independent conservation rows and pivot species, then proves full conservation closure before it can be accepted.
- Attempt diagnostics include conservation rank, rank status, positivity, conservation-closure status, balance residuals, selected amounts, and classified rejection reasons.
- Max-min remains the first selected initializer when it passes; the extent/nullspace path is available as an independent fallback and diagnostic attempt without exposing a public initializer route.
- The standalone CE checker now emits MEA initializer-ladder evidence and rejects missing selected-initializer, attempt-order, or extent/nullspace rank-status diagnostics.
- Focused red proof: `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_feasible_initialization.py -q` failed on missing `attempt_order` before implementation.
- Fresh proof: `uv run --no-sync python scripts/dev/build_epcsaft.py --build-only --parallel 10` passed.
- Fresh proof: `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_feasible_initialization.py -q` passed with 6 tests.
- Fresh proof: `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py -q` passed with 4 tests.
- Fresh proof: `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py -q` passed with 13 tests.
- Fresh proof: `uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete` returned status `complete` with no blockers.

## Blocked by

- None

## Non-goals

- Public initializer APIs.
- Hidden conservation repair.
- Replacing max-min initialization outright.

## Proof Oracle

- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
- Focused native initialization commands from Task 6 of the source plan.
