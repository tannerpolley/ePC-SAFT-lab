# Neutral LLE Proof Applicability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve GitHub issue #368 by separating neutral LLE family proof-route inventory from request-specific proof applicability.

**Architecture:** Keep the native activation matrix as the capability inventory and add selector-contract evidence for proof routes applicable to the current request. Nonassociating neutral LLE requests report the nonassociating proof route; source-backed Gross/Sadowski associating LLE requests report their associating proof route. The global activation row remains unchanged so admitted family evidence is not hidden.

**Tech Stack:** Native C++ selector contract, pybind result mapping, pytest native diagnostics, Superpowers issue mirror workflow, GitHub issue #368.

---

## Intake

- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/368`
- Source Spec: `docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md`
- Source Issue: `docs/superpowers/issues/2026-06-29-m4-equilibrium-issue-0368-separate-associating-proof-applicability-from-global-route-metadata.md`
- Source Plan: `docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0368-neutral-lle-proof-applicability-plan.md`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/367`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Loop run: `.superpowers/runs/20260629T1800-m4-pe-loop`

## Outcome Proof

**Intent:** Repair the stale neutral LLE metadata contract where one `activation.proof_routes` list was treated as both global route-family inventory and per-request proof receipt.
**Current Behavior:** A nonassociating neutral LLE selector contract returns a global `activation.proof_routes` list that also includes the associating Gross/Sadowski proof route, causing request-level exact-list checks to fail for the wrong reason.
**Expected Outcome:** The selector contract exposes request-specific `applicable_proof_routes` while preserving the full activation inventory in `activation.proof_routes`.
**Target Output:** Nonassociating requests report only `neutral_lle_binary_nonassociating_ipopt_exact_hessian` as applicable. Source-backed associating LLE requests report the Gross/Sadowski associating route as applicable. The activation matrix still lists admitted neutral LLE evidence.
**Owner:** M4 equilibrium package owner.
**Interface:** `SelectorContract`, `_native_equilibrium_selector_contract`, `_native_equilibrium_selector_route_result`, `activation.proof_routes`, and package native diagnostics tests.
**Cutover:** Replace tests that interpret family inventory as request-specific proof applicability with tests against `applicable_proof_routes`.
**Replaced Path:** Exact-list assertions on global `activation.proof_routes` for one request shape.
**Evidence:** Focused #368 pytest oracle, full `packages/epcsaft-equilibrium/tests` pass, mirror validation, GitHub issue update, and cleanup hook receipt.
**Acceptance Proof:** Acceptance is proven when route metadata tests pass and assert all three facts: nonassociating applicability is narrow, associating applicability is retained, and activation inventory remains honest.
**Stop Criteria:** Stop if the native selector cannot distinguish nonassociating from source-backed associating LLE requests.
**Avoid:** Do not delete associating proof-route evidence from the activation matrix, add solver flags, broaden public route claims, or weaken associating admission provenance checks.
**Risk:** The main risk is hiding admitted associating evidence to satisfy one nonassociating assertion. The fix must add a request-specific receipt instead.

## Implementation Boundaries

**Files To Create:** This plan only.
**Files To Modify:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.h`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`, `packages/epcsaft-equilibrium/tests/native/diagnostics/test_route_metadata_contracts.py`, and this issue mirror.
**Files To Avoid:** ePC-SAFT EOS equation files, M5 regression assets, electrolyte LLE routes, and activation-matrix proof-route inventory unless a separate issue requests inventory expansion.
**Source Of Truth:** #368 issue mirror, shared phase-equilibrium certification spec, native selector input classification, and existing Gross/Sadowski associating LLE admission checks.
**Read Path:** Read `classify_selector_input`, `evaluate_parameter_readiness`, `SelectorContract`, `selector_contract_to_dict`, and `apply_selector_metadata`.
**Write Path:** Add `SelectorContract.applicable_proof_routes`, populate it from input classification and parameter readiness, expose it through pybind dictionaries, and assert it in tests.
**Integration Points:** `ProblemFamilyActivation.proof_routes`, `SelectorParameterReadiness.associating_admission_proof_route`, and `_native_equilibrium_selector_contract`.
**Migration Or Cutover:** No removal of existing keys. The new `applicable_proof_routes` key is additive and clarifies the distinction from global activation inventory.
**Replaced Path Handling:** Replace request-level exact-list assertions on `activation.proof_routes` with explicit checks for both `activation.proof_routes` and `applicable_proof_routes`.
**Acceptance Proof Gate:** Do not push or open a PR until the focused #368 oracle and the full package test command pass or produce a precise source-backed blocker.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Inventory vs applicability | #368 mirror | Keep `activation.proof_routes` as family inventory and add `applicable_proof_routes` for the request. | Prevents hiding associating evidence while fixing nonassociating metadata checks. | No | M4 owner |
| Associating gate | Existing Gross/Sadowski readiness logic | Use `associating_admission_proof_route` only when the source-backed admission proof is present. | Keeps associating admission narrow and source-backed. | No | M4 owner |
| Nonassociating receipt | Selector input classification | Use `classification.nonassociating` to choose the nonassociating route proof. | Makes nonassociating request proof independent of associating inventory. | No | M4 owner |
| Native API shape | Pybind selector contract | Add a new additive key instead of changing `activation.proof_routes`. | Avoids breaking global capability inventory consumers. | No | M4 owner |
| Test complete | #368 proof oracle | Focused route-metadata/core tests plus full package suite. | Proves request applicability and nearby selector behavior. | No | M4 owner |

## Test Complete Definition

Test complete for #368 means:

- `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_route_metadata_contracts.py packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py -q` passes.
- `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -q` passes.
- Nonassociating `neutral_lle` selector contracts expose `applicable_proof_routes == ["neutral_lle_binary_nonassociating_ipopt_exact_hessian"]`.
- Source-backed Gross/Sadowski associating `neutral_lle` selector contracts expose `applicable_proof_routes == ["associating_neutral_lle_gross_2002_public_exact_hessian"]`.
- Both request shapes preserve `activation.proof_routes` as the global neutral LLE proof-route inventory.

## Acceptance Criteria Mapping

- Nonassociating neutral LLE request asserts its own proof applicability: Tasks 1 and 2.
- Associating LLE request asserts Gross 2002 proof applicability: Tasks 1 and 2.
- Activation capability inventory still lists admitted evidence honestly: Tasks 1, 2, and 3.

## Non-Goals

- No M5 parameter regression.
- No EOS equation changes.
- No new LLE family admission.
- No electrolyte, VLE, flash, boundary, or reactive route changes.
- No release claim.
- No downstream application metrics.

## Tasks

### Task 1: Reproduce The Metadata Failure

**Use Cases:**
- A maintainer needs a red-test proof that nonassociating requests are incorrectly checked against the global proof inventory.
- A package user needs the selector contract to show the proof route applicable to the current request.
- A future associating LLE admission must not disappear from the global inventory when nonassociating tests run.

**Files:**
- Modify: none
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_route_metadata_contracts.py`
- Test: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py`

- [ ] **Step 1: Run the focused #368 oracle before implementation.**

  ```powershell
  uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_route_metadata_contracts.py packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py -q
  ```

  Expected before implementation: failure where the nonassociating request expects only the nonassociating proof but receives the global neutral LLE inventory.

### Task 2: Add Request-Specific Proof Applicability

**Use Cases:**
- Nonassociating neutral LLE requests should report only the nonassociating proof route as applicable.
- Source-backed associating LLE requests should report their Gross/Sadowski proof route as applicable.
- Global capability inventory consumers should still see the full `activation.proof_routes` list.
- This cutover replaces the old path where one list carried two meanings.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_route_metadata_contracts.py`

- [ ] **Step 1: Add the additive selector-contract field.**

  Add `applicable_proof_routes` to `SelectorContract`, populate it after request shape, readiness, and input classification have been accepted, and expose it in pybind selector-contract and route-result dictionaries.

- [ ] **Step 2: Preserve global inventory.**

  Leave `ProblemFamilyActivation.proof_routes` unchanged for neutral LLE so admitted nonassociating and source-backed associating evidence remain visible.

- [ ] **Step 3: Assert both request shapes.**

  Update metadata tests to assert the nonassociating applicable route, the associating applicable route, and the unchanged activation inventory.

### Task 3: Validate And Publish Evidence

**Use Cases:**
- The package route must prove the metadata fix beyond a single assertion.
- The local and GitHub issue text must point at this executable implementation plan, not the replaced hierarchy-only issue-tree plan.
- A future maintainer must be able to rerun the proof oracle from the issue mirror as acceptance evidence.

**Files:**
- Modify: `docs/superpowers/issues/2026-06-29-m4-equilibrium-issue-0368-separate-associating-proof-applicability-from-global-route-metadata.md`
- Modify: GitHub issue `https://github.com/ePC-SAFT/ePC-SAFT/issues/368`

- [ ] **Step 1: Rebuild the native extension after the C++ change.**

  ```powershell
  uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
  ```

- [ ] **Step 2: Run the focused #368 oracle.**

  ```powershell
  uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_route_metadata_contracts.py packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py -q
  ```

- [ ] **Step 3: Run the full package suite.**

  ```powershell
  uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -q
  ```

- [ ] **Step 4: Validate the implementation plan.**

  ```powershell
  uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0368-neutral-lle-proof-applicability-plan.md
  uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0368-neutral-lle-proof-applicability-plan.md
  ```

- [ ] **Step 5: Update #368 mirror and GitHub body.**

  Ensure the source plan path, branch, labels/status, proof oracle, and retained validation evidence match the implemented behavior.

## Proof Oracle

```powershell
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0368-neutral-lle-proof-applicability-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0368-neutral-lle-proof-applicability-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests\native\diagnostics\test_route_metadata_contracts.py packages\epcsaft-equilibrium\tests\native\diagnostics\test_selector_core_contracts.py -q
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -q
uv run --no-sync python scripts\dev\validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
