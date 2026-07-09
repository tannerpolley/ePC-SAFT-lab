# Neutral LLE Stage II Replay Receipt Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve GitHub issue #365 by making the accepted neutral nonassociating LLE Stage III result honestly report whether it consumed the retained Stage II replay seed.

**Architecture:** Keep the existing native neutral LLE route and postsolve contract, but repair the validation contract so Stage III replay metadata is required only when the accepted seed attempt actually consumed the Stage II candidate pair. Preserve Stage II discovery diagnostics and make the focused package oracle fail first, then pass after the accepted-seed provenance checks prove the replay seed missed postsolve tolerance.

**Tech Stack:** Native C++ equilibrium route code, pybind result mapping, pytest package-level native diagnostics, Superpowers issue mirror workflow, GitHub issue #365.

---

## Intake

- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/365`
- Source Spec: `docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md`
- Source Issue: `docs/superpowers/issues/2026-06-29-m4-equilibrium-issue-0365-repair-neutral-stage-ii-replay-to-stage-iii-proof-receipt.md`
- Source Plan: `docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0365-neutral-lle-replay-receipt-plan.md`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/364`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Loop run: `.superpowers/runs/20260629T1800-m4-pe-loop`

## Outcome Proof

**Intent:** Fix the neutral LLE regression where Stage II replay metadata is retained but the accepted Stage III result can come from a different seed path, leaving replay-source fields empty or dishonest.
**Current Behavior:** The neutral LLE route runs deterministic seed attempts and records Stage III replay metadata only on the attempt whose `seed_name` is `held_stage_ii_dual_loop_candidate_pair`; the final accepted `best` result can be chosen from another accepted seed, so the public route can report Stage III complete without replay-consumption provenance.
**Expected Outcome:** The accepted neutral LLE Stage III result either is the Stage II replay-seed attempt and reports replay source, seed name, and candidate count, or it declines the replay-consumption claim while retaining the replay attempt and the accepted seed evidence.
**Target Output:** The focused oracle proves retained Stage II replay diagnostics, accepted Stage III current-route refinement, `seed_attempts[0]["seed_name"] == "held_stage_ii_dual_loop_candidate_pair"`, rejected replay-seed postsolve residual evidence, and accepted-seed residual evidence.
**Owner:** M4 equilibrium package owner.
**Interface:** `_native_equilibrium_selector_route_result` for `route="neutral_lle"`, `NeutralTwoPhaseEosRouteResult.postsolve`, `RouteSeedAttempt`, pybind route result mapping, package native diagnostics tests, and the #365 issue mirror.
**Cutover:** Replace final-result replay flags that can drift from the accepted seed path with provenance tied to the accepted seed attempt.
**Replaced Path:** A final accepted neutral LLE result reporting Stage III complete while Stage III replay-source fields are empty, copied from a non-replay seed, or set after the fact without accepted-seed evidence.
**Evidence:** Focused red/green pytest oracle, full `packages/epcsaft-equilibrium/tests` pass, mirror validation, GitHub issue update, and cleanup hook receipt.
**Acceptance Proof:** Acceptance is proven when current failing neutral LLE tests pass for the right reason: retained Stage II replay metadata remains present, the replay seed attempt is retained first, the accepted Stage III seed is tied to `route["seed_name"]`, replay-consumption metadata remains false when that accepted seed is not the replay seed, and per-attempt residuals show the replay seed missed postsolve tolerance while the accepted seed passed.
**Stop Criteria:** Stop if the accepted result cannot be scientifically tied to the Stage II candidate set without changing the route algorithm or falsifying metadata.
**Avoid:** Do not reduce assertions, set consumed-stage-II metadata after the fact, add solver flags, hide an alternate route, alter thermodynamic equations, refit parameters, broaden LLE capability claims, or count diagnostic-only success as production support.
**Risk:** The main risk is masking a route-selection problem with metadata. The fix must use accepted seed provenance and retain failed/nonaccepted attempts for diagnostics rather than manufacturing success fields.

## Implementation Boundaries

**Files To Create:** `packages/epcsaft-equilibrium/tests/equilibrium_support/route_assertions.py`.
**Files To Modify:** `packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py`, `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`, `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`, `tests/native/contracts/test_generalized_equilibrium_registry.py`, `docs/superpowers/issues/2026-06-29-m4-equilibrium-issue-0365-repair-neutral-stage-ii-replay-to-stage-iii-proof-receipt.md`.
**Files To Avoid:** ePC-SAFT EOS equation files, regression package files, M5 parameter snapshots, electrolyte LLE routes, associating LLE routes, downstream analyses, and public release metadata.
**Source Of Truth:** #365 issue mirror, the shared phase-equilibrium certification spec, existing neutral LLE tests, and native route implementation in `two_phase_eos_route.cpp`.
**Read Path:** Read the Stage II discovery payload from `evaluate_neutral_tpd_phase_discovery`, the Stage III route result from `solve_activated_neutral_lle_eos_route`, and pybind dictionaries from `register_bindings.cpp`.
**Write Path:** Update only the validation contract, M4 registry wording, and issue mirror status/plan pointers, then validate through the public package route.
**Integration Points:** `neutral_two_phase_seed_candidates`, `solve_activated_neutral_lle_eos_route`, `neutral_seed_attempt_from_result`, `NeutralTwoPhaseEosPostsolve`, `_native_equilibrium_selector_route_result`, and the focused neutral LLE pytest oracle.
**Migration Or Cutover:** No API migration. The public route keeps the same keys, but their values become accepted-seed provenance instead of detached postsolve metadata.
**Replaced Path Handling:** Replace tests and registry wording that required Stage III replay consumption for every accepted neutral LLE result with accepted-seed provenance checks that reject false replay-consumption claims.
**Acceptance Proof Gate:** Do not push or open a PR until the focused #365 oracle and the full package test command pass or produce a precise source-backed blocker.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Scope owner | #365 mirror and M4 milestone policy | Work is limited to neutral nonassociating LLE route provenance in `packages/epcsaft-equilibrium`. | Keeps electrolyte, associating, EOS, and regression work out of this slice. | No | M4 owner |
| Scientific claim | Existing neutral LLE residual block | The thermodynamic acceptance equations do not change; only accepted-seed provenance changes. | Avoids altering fugacity, material-balance, pressure, or phase-distance math. | No | M4 owner |
| Test complete | #365 proof oracle | Focused two-test oracle plus full package suite are required. | Proves the exact regression and guards nearby public package behavior. | No | M4 owner |
| Metrics | Existing tests and tolerances | Stage II bound gap remains `<= 1.0e-6`; material balance `<= 1.0e-8`; pressure `<= 1.0e-3`; fugacity `<= 1.0e-6`; phase distance `>= 1.0e-6`; replay fields must match exact string keys. | Keeps numerical and metadata pass/fail criteria explicit. | No | M4 owner |
| Route selection | Focused red oracle | The current fixture tries the Stage II replay seed first, but that attempt misses the postsolve fugacity residual tolerance at `1.86e-6`; the later accepted seed passes at `6.75e-7`. | The fix must preserve an honest replay decline rather than forcing false replay-consumption metadata. | No | M4 owner |
| Branch strategy | Loop-controller selection | Use `codex/m4-lle-repair-neutral-stage-ii-replay-to-stage-iii-proof-receipt`. | Keeps plan repair and implementation isolated from `main`. | No | Main thread |
| Publish behavior | Resolve-issue policy | Push and open PR only after artifact review and native push permission. | Preserves the project merge gate. | No | Main thread |

## Test Complete Definition

Test complete for #365 means:

- `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py::test_neutral_lle_stage_iii_route_refinement_records_stage_ii_replay_seed packages\epcsaft-equilibrium\tests\native\results\test_neutral_lle_reference_values.py::test_neutral_lle_synthetic_binary_accepts_split_with_exact_hessian -q` passes from the public package route.
- `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -q` passes.
- Stage II replay diagnostics remain retained with `held_stage_ii_replay_ready is True`, source `stage_ii_dual_loop_selected_candidates`, seed `held_stage_ii_dual_loop_candidate_pair`, and retained candidate/rejected-candidate counts.
- The accepted Stage III route either reports `held_stage_iii_consumed_stage_ii_replay_metadata is True` with source `stage_ii_dual_loop_candidate_seed`, or reports `False` while retaining the rejected replay attempt and an accepted non-replay seed whose `phase_equilibrium_norm` is within tolerance.

## Acceptance Criteria Mapping

- Stage II replay-ready diagnostics remain retained: Tasks 1, 2, and 3.
- The accepted Stage III result reports the real seed/candidate provenance: Tasks 1 and 2.
- Current failing neutral LLE tests pass for the right reason: Tasks 1, 2, and 3.

## Non-Goals

- No M5 parameter regression.
- No EOS equation changes.
- No new LLE family admission.
- No electrolyte, associating, VLE, flash, boundary, or reactive route changes.
- No release claim.
- No downstream application metrics.

## Tasks

### Task 1: Reproduce The Replay Receipt Failure

**Use Cases:**
- A maintainer needs red-test proof that the accepted Stage III route can lose Stage II replay provenance.
- A package user needs the public `neutral_lle` route result to show whether the accepted result consumed the discovery candidate set.
- A recovery run must distinguish missing Ipopt support from a real provenance regression.

**Files:**
- Modify: none
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py`
- Test: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`

- [ ] **Step 1: Run the focused #365 oracle before implementation.**

  ```powershell
  uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py::test_neutral_lle_stage_iii_route_refinement_records_stage_ii_replay_seed packages\epcsaft-equilibrium\tests\native\results\test_neutral_lle_reference_values.py::test_neutral_lle_synthetic_binary_accepts_split_with_exact_hessian -q
  ```

  Expected before implementation: failure on the replay provenance assertions, or skip only if native Ipopt is not compiled. A skip is not a #365 pass.

- [ ] **Step 2: Record the failing fields.**

  Capture the first failing assertion and the observed values for `route["seed_attempts"][0]["seed_name"]`, `postsolve["held_stage_iii_consumed_stage_ii_replay_metadata"]`, `postsolve["held_stage_iii_replay_source"]`, and `postsolve["held_stage_iii_replay_seed_name"]`.

### Task 2: Repair Accepted-Seed Replay Provenance Validation

**Use Cases:**
- When the Stage II dual-loop replay seed is accepted, the public route should retain replay-source metadata.
- When another seed is the only accepted route, the public route should not claim Stage III consumed the Stage II replay seed and tests must prove why.
- Failed or rejected attempts should remain in `seed_attempts` for diagnostics without overwriting the accepted route receipt.
- This cutover replaces the old path where final-route metadata could drift from the seed attempt that actually produced the accepted result.

**Files:**
- Create: `packages/epcsaft-equilibrium/tests/equilibrium_support/route_assertions.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py`
- Test: `packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py`

- [ ] **Step 1: Inspect the attempt ordering and best-result selection.**

  Read `solve_activated_neutral_lle_eos_route`, especially the `seeds` loop, `run_attempt`, the `kHeldStageIIDualLoopSeedName` metadata block, and `best.seed_attempts = attempts`.

- [ ] **Step 2: Replace the over-strict replay-consumption assertions.**

  Add a focused helper asserting both valid branches of the accepted-seed contract:

  ```text
  if accepted_seed == "held_stage_ii_dual_loop_candidate_pair":
      require replay-consumption metadata
  else:
      require replay metadata to remain false/empty
      require replay attempt postsolve_rejected with phase_equilibrium_norm > 1.0e-6
      require accepted attempt phase_equilibrium_norm <= 1.0e-6
  ```

- [ ] **Step 3: Preserve diagnostic attempts.**

  Assert all attempted seeds remain in `seed_attempts`, the replay attempt remains at index `0`, and `route["seed_name"]` matches the accepted attempt.

- [ ] **Step 4: Re-run the focused oracle.**

  ```powershell
  uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py::test_neutral_lle_stage_iii_route_refinement_records_stage_ii_replay_seed packages\epcsaft-equilibrium\tests\native\results\test_neutral_lle_reference_values.py::test_neutral_lle_synthetic_binary_accepts_split_with_exact_hessian -q
  ```

  Expected after implementation: both tests pass and report real tests, not zero collection.

### Task 3: Validate The Public Package Route And Mirror

**Use Cases:**
- The package route must prove the fix beyond one focused assertion.
- The local and GitHub issue text must point at this executable implementation plan, not the replaced hierarchy-only issue-tree plan.
- A future maintainer must be able to rerun the proof oracle from the issue mirror as acceptance evidence.

**Files:**
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `docs/superpowers/issues/2026-06-29-m4-equilibrium-issue-0365-repair-neutral-stage-ii-replay-to-stage-iii-proof-receipt.md`
- Modify: GitHub issue `https://github.com/ePC-SAFT/ePC-SAFT/issues/365`

- [ ] **Step 1: Update M4 registry wording.**

  Replace neutral LLE wording that says the current route consumes Stage II replay with wording that says the route records accepted-seed provenance and declines replay consumption when the replay seed misses postsolve tolerance.

- [ ] **Step 2: Run the full package suite.**

  ```powershell
  uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -q
  ```

  Expected: all package tests pass or a precise unrelated blocker is documented before PR handoff.

- [ ] **Step 3: Validate the implementation plan.**

  ```powershell
  uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0365-neutral-lle-replay-receipt-plan.md
  uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0365-neutral-lle-replay-receipt-plan.md
  ```

- [ ] **Step 4: Update #365 mirror and GitHub body.**

  Ensure the source plan path, branch, labels/status, and proof oracle in the local mirror and GitHub body match this plan and the actual validation evidence.

- [ ] **Step 5: Run docs validation and cleanup.**

  ```powershell
  uv run --no-sync python scripts\dev\validate_project.py docs
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  ```

## Proof Oracle

```powershell
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0365-neutral-lle-replay-receipt-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0365-neutral-lle-replay-receipt-plan.md
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py::test_neutral_lle_stage_iii_route_refinement_records_stage_ii_replay_seed packages\epcsaft-equilibrium\tests\native\results\test_neutral_lle_reference_values.py::test_neutral_lle_synthetic_binary_accepts_split_with_exact_hessian -q
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -q
uv run --no-sync python scripts\dev\validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
