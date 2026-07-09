# Shared Production Route Certification Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve GitHub issue #362 by making every production-exposed phase-equilibrium route map to one shared certification contract with retained capability evidence.

**Architecture:** Keep the native activation matrix as the route-family source of truth and add a Python certification normalizer that combines activation rows, public route mapping, and capability evidence rows into one package-visible payload. Expose the payload through `epcsaft_equilibrium.capabilities()` and validate it with package contract tests so production claims fail closed when proof metadata is missing or when planned/private rows publish routes.

**Tech Stack:** Python package contract module, generated activation mirror, native pybind activation metadata, pytest package contracts, M4 registry contract tests, GitHub issue mirror workflow.

---

## Intake

- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/362`
- Source Spec: `docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md`
- Source Issue: `docs/superpowers/issues/2026-06-29-m4-equilibrium-issue-0362-implement-shared-production-route-certification-contract.md`
- Source Plan: `docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0362-shared-production-route-certification-contract-plan.md`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/361`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Auto Mode authorization: `.superpowers/runs/20260629T2245-m4-pe-auto-362/auto-mode-authorization.json`

## Outcome Proof

**Intent:** Implement the first executable shared contract that every production-exposed phase-equilibrium route must satisfy before capability text can claim support.
**Current Behavior:** Activation rows, route specs, and derivative evidence rows are checked in separate places, so a future route can overclaim support by updating one surface without satisfying one shared certification shape.
**Expected Outcome:** `epcsaft_equilibrium.capabilities()["phase_equilibrium_certification"]` exposes a schema-versioned contract for every production route family and planned/private families remain declared without public routes.
**Target Output:** `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "certification and phase and equilibrium" -q` runs real tests that fail if any production-exposed route lacks required activation fields, public route mapping, proof routes, residual families, derivative policy, or production evidence.
**Owner:** M4 equilibrium package owner.
**Interface:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/phase_equilibrium_certification.py`, `epcsaft_equilibrium.capabilities()`, package contract tests, M4 registry tests, and the #362 issue mirror.
**Cutover:** Production-route acceptance moves from route-specific assertions only to the shared certification payload emitted by capabilities, while route-specific validators remain as evidence producers.
**Replaced Path:** Isolated route tests or registry rows that can pass while omitting shared discovery, postsolve, residual, derivative, or capability-evidence metadata.
**Evidence:** Focused package pytest selector, existing native registry contract tests, issue mirror validation, updated GitHub issue body, and cleanup proof.
**Acceptance Proof:** Acceptance is proven when the shared certification payload covers all production-exposed public routes, planned/private families publish no public route, and mutation tests reject capability evidence that names unsupported public routes or production rows without proof evidence.
**Stop Criteria:** Stop if the package route inventory cannot distinguish production-exposed, planned/private, diagnostic, and prerequisite-only evidence rows without changing the scientific scope of existing routes.
**Avoid:** Do not admit new route families, fit new parameters, broaden electrolyte scope, add solver dodge flags, or count prerequisite-only diagnostics as production-route support.
**Risk:** The main risk is turning a documentation contract into another loose payload; the implementation must validate itself during capability construction and keep negative tests for overclaim cases.

## Implementation Boundaries

**Files To Create:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/phase_equilibrium_certification.py`, `packages/epcsaft-equilibrium/tests/contracts/test_phase_equilibrium_certification_contract.py`.
**Files To Modify:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/__init__.py`, `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`, `tests/native/contracts/test_generalized_equilibrium_registry.py`, `docs/superpowers/issues/2026-06-29-m4-equilibrium-issue-0362-implement-shared-production-route-certification-contract.md`.
**Files To Avoid:** Provider EOS internals, regression package files, downstream repositories, native solver equations, generated activation mirror except through its generator, and release metadata.
**Source Of Truth:** Native activation matrix mirrored in `equilibrium_activation.py`, `EQUILIBRIUM_ROUTE_DERIVATIVE_EVIDENCE`, #362 source spec, and the M4 GFPE registry.
**Read Path:** Read activation rows, public route family map, and derivative/capability evidence rows from `capabilities.py` data already used by the public package surface.
**Write Path:** Write one normalizer/validator module, expose its schema from capabilities, add package contract tests, add one registry cross-check, and update #362 mirror/GitHub text to the executable plan.
**Integration Points:** `public_routes_by_family()`, `public_route_family_map()`, `EQUILIBRIUM_ROUTE_DERIVATIVE_EVIDENCE`, `epcsaft_equilibrium.capabilities()`, package contract tests, native registry contract tests, and GitHub #362.
**Migration Or Cutover:** Capabilities gains `phase_equilibrium_certification` without changing route solver behavior; the shared payload becomes the first gate that future PE route-family issues must satisfy.
**Replaced Path Handling:** Keep existing route validators and registry tests, but add shared checks so future route-specific tests cannot be the only acceptance surface for production support.
**Acceptance Proof Gate:** The proof oracle commands in this plan must pass before push, PR creation, merge, #362 closure, and any downstream issue unblocking.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Scope owner | #362 mirror and M4 milestone policy | Implement only the M4 `epcsaft-equilibrium` production-route certification contract. | Keeps M3 EOS, M5 regression, release, and downstream work outside this PR. | No | M4 owner |
| Certification source | Repo activation/capability layout | Native activation rows stay the source of truth; Python normalizes them with capability evidence. | Avoids duplicating route truth and keeps generated activation metadata authoritative. | No | M4 owner |
| Public interface | #362 acceptance criteria | Emit the shared contract from `epcsaft_equilibrium.capabilities()`. | Gives users and tests one package-visible certification payload. | No | M4 owner |
| Planned/private handling | Source spec enforcement policy | Planned/private families remain declared and fail if they publish public routes or production evidence. | Prevents fake production claims while preserving future-route planning rows. | No | M4 owner |
| Test complete | #362 proof oracle | Focused package selector plus registry contract tests are the pass/fail proof. | Ensures the requested selector collects real tests and registry/capability claims stay coupled. | No | M4 owner |
| Scientific metrics | Chemical-engineer equilibrium guidance | This issue enforces residual-family and evidence presence; numerical tolerance validation stays in the route-family evidence producers. | Avoids refitting or changing thermodynamic equations inside the shared-contract slice. | No | M4 owner |
| Auto Mode routing | User authorization ledger | Continue through direct inline issue resolution and bounded merge only if proof stays inside #362 scope. | Keeps autonomy bounded to one ready issue. | No | Main thread |

## Test Complete Definition

Test complete for #362 means all production-exposed rows have a shared certification record with:

- non-empty public route mapping;
- non-empty proof routes;
- non-empty variable model and density backend;
- residual and constraint family metadata;
- exact derivative requirement metadata;
- postsolve or TPD certification metadata;
- at least one production-supported evidence row mapped to the selector family;
- planned/private rows with no public routes and no production-supported public evidence.

Numerical residual tolerances are enforced by existing route-family validators. This issue validates that the route-family residual blocks are named, mapped, and evidence-coupled so future tolerance issues have a common contract to target.

## Acceptance Criteria Mapping

- Production-exposed routes emit or map to one shared certification shape: Tasks 1, 2, and 4.
- Planned/private routes remain declared without fake production support: Tasks 1, 2, and 4.
- Registry/capability tests fail if support claims outpace evidence: Tasks 2, 3, and 4.

## Non-Goals

- No new route-family admission.
- No parameter regression.
- No native solver equation changes.
- No broad electrolyte, reactive, CE, CPE, or release claim.
- No downstream application metrics.

## Tasks

### Task 1: Write The Shared Certification Tests

**Use Cases:**
- A package user inspecting `capabilities()` needs one visible phase-equilibrium certification payload for every production route.
- A maintainer changing a production activation row needs package tests to fail when proof routes, residual families, derivative policy, or capability evidence are missing.
- A future planned/private route must stay declared without public routes; this is the cutover evidence that replaces route-specific-only acceptance.

**Files:**
- Create: `packages/epcsaft-equilibrium/tests/contracts/test_phase_equilibrium_certification_contract.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`

- [ ] **Step 1: Add failing tests for the shared payload.**

  Add tests named with the selector words `certification`, `phase`, and `equilibrium` so the #362 proof oracle collects them:

  ```python
  def test_certification_phase_equilibrium_payload_covers_all_public_routes() -> None:
      payload = epcsaft_equilibrium.capabilities()["phase_equilibrium_certification"]
      public_routes = epcsaft_equilibrium.capabilities()["public_routes"]
      certified = sorted(
          route
          for contract in payload["production_route_contracts"]
          for route in contract["public_routes"]
      )
      assert certified == public_routes
  ```

- [ ] **Step 2: Add negative tests for overclaims.**

  Build mutated payloads that publish `reactive_lle` as a public route and that remove production evidence from `neutral_lle`; assert `validate_phase_equilibrium_certification_contracts(...)` returns named blockers.

- [ ] **Step 3: Run the focused selector and verify it fails before implementation.**

  Run: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "certification and phase and equilibrium" -q`

  Expected before implementation: at least one collected test fails because `phase_equilibrium_certification` is absent.

### Task 2: Implement The Certification Normalizer

**Use Cases:**
- A production route family needs one schema-versioned contract assembled from activation metadata and evidence rows.
- Prerequisite-only diagnostics for electrolyte HELD stages must remain visible without being counted as production support.
- The shared validator must provide acceptance evidence and cutover protection by rejecting route support claims that outpace evidence.

**Files:**
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/phase_equilibrium_certification.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/__init__.py`

- [ ] **Step 1: Add the contract module with typed helper functions.**

  Implement these public helpers:

  ```python
  def phase_equilibrium_certification_contracts(
      *,
      activation: Mapping[str, object],
      route_derivative_evidence: Mapping[str, object],
  ) -> dict[str, object]:
      ...

  def validate_phase_equilibrium_certification_contracts(
      payload: Mapping[str, object],
  ) -> tuple[str, ...]:
      ...
  ```

- [ ] **Step 2: Build production route contracts from activation rows.**

  Each production contract must include `selector_family`, `display_name`, `public_routes`, `proof_routes`, `residual_families`, `constraint_families`, `variable_model`, `density_backend`, `derivative_requirement`, `stability_prelayer`, `postsolve_certification`, `evidence_rows`, `production_evidence_quantities`, and `family_residual_block`.

- [ ] **Step 3: Validate planned/private rows.**

  The validator must return blockers when a non-production row publishes `public_routes`, when production rows lack proof/evidence fields, or when a production-supported evidence row names a selector family that is not production exposed.

- [ ] **Step 4: Expose the contract from capabilities.**

  Add `phase_equilibrium_certification` to the capability payload and raise a `RuntimeError` if validation returns blockers during capability construction.

- [ ] **Step 5: Export the helper functions from `epcsaft_equilibrium.__init__`.**

  Add `phase_equilibrium_certification_contracts` and `validate_phase_equilibrium_certification_contracts` to `__all__`.

### Task 3: Add Registry Coupling Coverage

**Use Cases:**
- Registry tests need to fail when a registry production row claims public utility routes without admission evidence.
- Capability tests need to fail when the package exposes a public route that is missing from the shared certification payload.
- This preserves acceptance evidence without moving route-family numerical validation into the #362 shared-contract slice.

**Files:**
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`

- [ ] **Step 1: Add registry production-row evidence assertions.**

  In `test_generalized_equilibrium_registry.py`, assert every registry `production_exposed: true` PE family row has non-empty `existing_public_utility_routes`, non-empty `admission_evidence`, and each admission evidence row has `command`, `scope`, and `result_requirement`.

- [ ] **Step 2: Add capability coupling assertions.**

  In `test_activation_capabilities.py`, assert `phase_equilibrium_certification["public_route_family_map"]` equals the activation route-family map and that `production_route_contracts` cover the same families as `production_families`.

- [ ] **Step 3: Run the package and registry tests.**

  Run: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "certification and phase and equilibrium" -q`

  Run: `uv run --no-sync python -m pytest tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q`

### Task 4: Update #362 Mirrors And Validate The Plan Route

**Use Cases:**
- The local mirror and GitHub body must point to this executable plan instead of the issue-tree plan.
- The proof oracle must show the focused selector runs real tests and the replaced route-specific-only path is guarded by shared certification.
- Auto Mode closeout needs exact validation evidence before push, PR, merge, or issue closure.

**Files:**
- Modify: `docs/superpowers/issues/2026-06-29-m4-equilibrium-issue-0362-implement-shared-production-route-certification-contract.md`
- Modify: GitHub issue `https://github.com/ePC-SAFT/ePC-SAFT/issues/362`

- [ ] **Step 1: Update source plan pointers.**

  Replace the issue-tree plan path with `docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0362-shared-production-route-certification-contract-plan.md` in the mirror and GitHub body.

- [ ] **Step 2: Validate the plan and mirror.**

  Run:

  ```powershell
  uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0362-shared-production-route-certification-contract-plan.md
  uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0362-shared-production-route-certification-contract-plan.md
  ```

- [ ] **Step 3: Run the full #362 proof oracle and cleanup hook.**

  Run the proof oracle commands below, then run the repo cleanup hook before PR-ready handoff.

## Proof Oracle

```powershell
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0362-shared-production-route-certification-contract-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-29-m4-equilibrium-issue-0362-shared-production-route-certification-contract-plan.md
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "certification and phase and equilibrium" -q
uv run --no-sync python -m pytest tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts\dev\validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
