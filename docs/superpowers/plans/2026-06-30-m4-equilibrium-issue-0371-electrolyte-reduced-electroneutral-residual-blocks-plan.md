# M4 Electrolyte Reduced Electroneutral Residual Blocks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make #371 enforce electrolyte reduced-electroneutral residual evidence through the shared phase-equilibrium certification contract.

**Architecture:** Reuse the existing public `electrolyte_lle` validation chain and attach a shared electrolyte certification payload to it. The payload is derived from retained public-route, Stage III, postsolve, and Born/SSM/DS evidence instead of adding fitted parameters or a separate solver path.

**Tech Stack:** Python validation scripts, `epcsaft-equilibrium` public `Equilibrium` API, pytest, GitHub issue mirrors, M4 registry YAML.

---

## Source

- GitHub issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/371
- Issue mirror: `docs/superpowers/issues/2026-06-30-m4-equilibrium-issue-0371-integrate-reduced-electroneutral-electrolyte-residual-blocks.md`
- Source spec: `docs/superpowers/specs/2026-06-29-m4-phase-equilibrium-unified-certification-contract.md`
- Parent plan: `docs/superpowers/plans/2026-06-29-m4-phase-equilibrium-unified-certification-issue-tree-plan.md`
- Milestone/package: M4, `packages/epcsaft-equilibrium`

## Outcome Proof

**Intent:** Attach electrolyte reduced-electroneutral residual equations and retained diagnostics to the shared PE certification contract.
**Current Behavior:** The public electrolyte checker proves public admission, HELD2 Stage I/II replay, Stage III refinement, postsolve certification, charge balance, transfer residuals, and exact reduced derivative receipts, but those fields are not exposed as one enforceable shared PE residual-block certificate.
**Expected Outcome:** Public electrolyte LLE evidence reports the shared PE contract plus charge, lift/back-lift, projected transfer, mean-ionic transfer, and active-block derivative diagnostics.
**Target Output:** `check_electrolyte_public_admission.py` and `check_electrolyte_held2_public_route_scenarios.py` both expose accepted electrolyte shared-certification evidence with empty blockers.
**Owner:** M4 equilibrium package owner.
**Interface:** Public validation scripts, package-level tests, native contract tests, M4 registry rows, and issue mirrors.
**Cutover:** Replace electrolyte-only checker success with shared-contract electrolyte residual certification for the admitted `electrolyte_lle` route.
**Replaced Path:** Evidence that proves electrolyte reduced residuals but does not publish the shared PE contract shape.
**Evidence:** Fresh focused pytest selectors, public admission checker JSON, scenario checker JSON, registry contract tests, docs validation, cleanup hook.
**Acceptance Proof:** The #371 proof oracle commands pass and the package selector includes real electrolyte HELD2 residual tests.
**Stop Criteria:** Stop if accepted rows cannot prove projected electrochemical or modified mean-ionic residuals without raw single-ion equality.
**Avoid:** Do not use raw single-ion chemical-potential equality as acceptance evidence. Do not add M5 parameter regression, release claims, downstream metrics, private-native-only proof, solver dodge flags, or diagnostic-only success.
**Risk:** The main risk is naming drift between Stage III/postsolve diagnostics and the new shared certification payload; owned by the M4 equilibrium package owner and blocked by explicit missing-field tests.

## Implementation Boundaries

**Files To Create:** `packages/epcsaft-equilibrium/tests/api/test_electrolyte_lle_reduced_residual_certification.py`
**Files To Modify:** `scripts/validation/check_electrolyte_public_admission.py`, `scripts/validation/check_electrolyte_held2_public_route_scenarios.py`, `tests/native/contracts/test_electrolyte_public_admission.py`, `packages/epcsaft-equilibrium/tests/native/diagnostics/test_electrolyte_held2_public_route.py`, `packages/epcsaft-equilibrium/tests/native/diagnostics/test_electrolyte_held2_public_route_scenarios.py`, `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml` and `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`, `docs/superpowers/milestones/M4-equilibrium/README.md`, `docs/superpowers/issues/2026-06-30-m4-equilibrium-issue-0371-integrate-reduced-electroneutral-electrolyte-residual-blocks.md`
**Files To Avoid:** M5 regression package files, EOS parameter bundle files, native solver fall-through toggles, release docs, downstream application repos.
**Source Of Truth:** #371 issue mirror, the unified PE certification spec, retained electrolyte public admission checker chain, and `Equilibrium(..., route="electrolyte_lle").solve()` diagnostics.
**Read Path:** Public checker payloads read retained source fixture, Stage III/postsolve diagnostics, capability activation, and retained derivative receipts.
**Write Path:** Public checker output gains `shared_certification`; scenario checker copies that evidence into public route scenario rows; registry/docs record only the accepted evidence.
**Integration Points:** `epcsaft_equilibrium.capabilities()["phase_equilibrium_certification"]`, public admission checker, scenario checker, package-level pytest selector, native contract tests, M4 registry.
**Migration Or Cutover:** Existing public admission success remains required, then shared electrolyte residual certification is added as a required acceptance block.
**Replaced Path Handling:** Tests must fail when the shared block is missing, when mean-ionic/projected residuals are absent, or when raw single-ion equality is marked as used.
**Acceptance Proof Gate:** Do not push or mark #371 complete until the proof oracle and package selector pass with nonzero collected tests.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Execute #371 next | User Looping Mode request and M4 issue order | Resolve #371 after neutral and associating LLE parent closeout | Keeps phase-equilibrium loop in issue-tree order | No | M4 equilibrium package owner |
| Residual acceptance basis | #371 Stop Criteria and unified PE spec | Use projected electrochemical or modified mean-ionic residuals, not raw single-ion equality | Prevents false electrolyte acceptance on unobservable single-ion quantities | No | M4 equilibrium package owner |
| Data source | #371 non-goals and retained public route evidence | Reuse retained Khudaida public-route diagnostic evidence; do not change parameters | Keeps issue in M4 validation/solver scope and avoids M5 regression work | No | M4 equilibrium package owner |
| Public route honesty | #371 Outcome Summary | Require `Equilibrium(..., route="electrolyte_lle")` public admission evidence | Prevents private-native-only completion | No | M4 equilibrium package owner |
| Test-complete definition | #371 proof oracle and repo validation policy | Focused package selector, public admission checker, scenario checker, registry contracts, docs validator, cleanup hook | Provides route, checker, registry, and documentation proof | No | M4 equilibrium package owner |

## Acceptance Criteria

- Reduced electroneutral basis and lift/back-lift residuals are retained in the shared certification payload.
- Projected electrochemical or modified mean-ionic transfer residuals pass within retained tolerances.
- Born/SSM/DS active-block exactness is reported when enabled.
- Raw single-ion equality is explicitly rejected as the acceptance condition.
- Scenario validation rows retain the same shared certification evidence for public electrolyte route rows.
- The M4 registry and #371 mirror reflect actual accepted behavior, with no broader generic electrolyte, reactive, CE/CPE, regression, or release claim.

## Non-Goals

- No M5 parameter regression.
- No release claim.
- No downstream application metrics.
- No generic electrolyte flash or reactive electrolyte LLE admission.
- No change to the retained Khudaida parameter bundle.

### Task 1: Add Failing Tests For Electrolyte Shared Certification

**Use Cases:**
- A maintainer can run the package selector and see real #371 tests collected for electrolyte HELD2 residual certification.
- A missing shared certification block fails before public electrolyte route success is counted.
- A payload that uses raw single-ion equality fails even if charge and pressure residuals are small.
- Scenario rows must preserve the shared residual evidence for public electrolyte route cases and replace the old electrolyte-only success path.

**Files:**
- Create: `packages/epcsaft-equilibrium/tests/api/test_electrolyte_lle_reduced_residual_certification.py`
- Modify: `tests/native/contracts/test_electrolyte_public_admission.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_electrolyte_held2_public_route.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_electrolyte_held2_public_route_scenarios.py`

- [ ] **Step 1: Write the package-level failing selector test**
  - Add assertions that `checker.evaluate_public_admission(... require_public_admission=True ...)` returns `shared_certification.status == "accepted"`, `family_residual_block == "electrolyte_lle"`, `raw_single_ion_equality_used is False`, and accepted residual sub-blocks for reduced basis, lift/back-lift, projected transfer, mean-ionic transfer, and active electrolyte block exactness.
- [ ] **Step 2: Write the native checker mutation tests**
  - Add mutation tests that remove `shared_certification` and that set `raw_single_ion_equality_used = True`; both must add deterministic blockers.
- [ ] **Step 3: Write the scenario propagation test**
  - Assert each public-route scenario row contains accepted `shared_certification` with the same residual-basis and raw-single-ion rejection fields.
- [ ] **Step 4: Run the red selector**
  - Command: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and residual" -q`
  - Expected before implementation: at least one collected test fails because `shared_certification` is missing.

### Task 2: Implement Shared Electrolyte Residual Certification Payload

**Use Cases:**
- The public electrolyte LLE checker reports the same high-level PE lifecycle as neutral and associating LLE evidence.
- Reduced charge-neutral variables are tied to lift/back-lift, charge, and projected transfer diagnostics.
- Active Born/SSM/DS exactness is retained from readiness/Stage III evidence instead of inferred from a capability claim.
- The checker blocks incomplete shared certification when `--require-public-admission` or `--require-complete` is used, completing the cutover from route-only success to shared residual certification.

**Files:**
- Modify: `scripts/validation/check_electrolyte_public_admission.py`
- Modify: `scripts/validation/check_electrolyte_held2_public_route_scenarios.py`

- [ ] **Step 1: Add a helper to build `shared_certification`**
  - Derive it from `public_admission`, `held2_phase_discovery`, `electrolyte_stage_iii_refinement`, `electrolyte_postsolve_certification`, and `held2_readiness_gate`.
  - Include route, selector family, variable model, family residual block, stage provenance, reduced-basis evidence, lift/back-lift residuals, charge residuals, projected transfer residuals, modified mean-ionic transfer residuals, active Born/SSM/DS exactness, exact reduced Jacobian/Hessian evidence, and `raw_single_ion_equality_used: false`.
- [ ] **Step 2: Add a validator for the shared payload**
  - Return deterministic blockers for missing route/family, missing reduced-basis evidence, missing lift/back-lift evidence, excessive charge residual, missing projected or mean-ionic transfer residual, missing active-block exactness, missing exact reduced derivatives, or raw single-ion equality use.
- [ ] **Step 3: Wire the validator into public admission acceptance**
  - Add `shared_certification` to full and minimal payloads.
  - Make `require_public_admission=True` block when shared certification is absent or rejected.
- [ ] **Step 4: Propagate the accepted block to scenario public-route artifacts**
  - Copy `shared_certification` into unstable, boundary, and phase-label scenario rows.
  - Keep neutral-limit rows free of charged residual-family claims.
- [ ] **Step 5: Run the green selector**
  - Command: `uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and residual" -q`
  - Expected after implementation: nonzero tests collected and all selected tests pass.

### Task 3: Update Registry, Mirror, And Proof Oracle Evidence

**Use Cases:**
- The M4 registry records that electrolyte LLE now satisfies the shared PE residual certification block for the retained public scope.
- The #371 mirror and milestone page no longer describe the issue as blocked after the PR lands.
- The retained validation commands prove the public package route, scenario ladder, registry contracts, and docs are coherent.
- The final issue state replaces the old tracker-only evidence path with source-backed shared-contract acceptance proof.

**Files:**
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml` and `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-06-30-m4-equilibrium-issue-0371-integrate-reduced-electroneutral-electrolyte-residual-blocks.md`

- [ ] **Step 1: Update registry result requirements**
  - Add `shared_phase_equilibrium_certification`, reduced-basis lift/back-lift, projected/mean-ionic residual, raw-single-ion rejection, and active-block exactness to the electrolyte public admission row.
- [ ] **Step 2: Update local issue mirror and milestone page**
  - Point #371 to this focused plan.
  - Mark the mirror execution fields ready before PR creation and complete only after proof passes.
- [ ] **Step 3: Run the #371 proof oracle**
  - `uv run --no-sync python scripts\validation\check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete`
  - `uv run --no-sync python scripts\validation\check_electrolyte_held2_public_route_scenarios.py --json --require-complete`
- [ ] **Step 4: Run cross-contract validation**
  - `uv run --no-sync python -m pytest tests\native\contracts\test_electrolyte_public_admission.py tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q`
  - `uv run --no-sync python scripts\dev\validate_project.py docs`
  - `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Proof Oracle

```powershell
uv run --no-sync python -m pytest packages\epcsaft-equilibrium\tests -k "electrolyte and held2 and residual" -q
uv run --no-sync python scripts\validation\check_electrolyte_public_admission.py --json --require-held2-stage-ii --require-stage-iii --require-postsolve-certification --require-public-admission --require-complete
uv run --no-sync python scripts\validation\check_electrolyte_held2_public_route_scenarios.py --json --require-complete
uv run --no-sync python -m pytest tests\native\contracts\test_electrolyte_public_admission.py tests\native\contracts\test_equilibrium_benchmark_registry.py tests\native\contracts\test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts\dev\validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
