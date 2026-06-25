# Electrolyte Charge-Neutral TPD Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the next #191 child issue by adding a native-backed, source-backed electrolyte charge-neutral TPD screening gate before full HELD2 phase discovery or public electrolyte route admission.

**Architecture:** This is an electrolyte stability evidence slice, not production electrolyte GFPE admission. The native equilibrium core adds a charge-neutral TPD screening entrypoint that projects chemical-potential differences onto the electroneutral subspace and only accepts charge-neutral trial compositions. A retained Python checker consumes #269 and #300 evidence, calls the new native diagnostic on the Khudaida electrolyte fixture, records finite TPD/candidate metrics, and keeps remaining HELD2 Stage II/III and public admission gates closed.

**Tech Stack:** C++ equilibrium native core, pybind11 bindings, Python validation checker, pytest contracts through `run_pytest.py`, M4 GitHub issue mirrors, M4 milestone docs.

---

## Intake

- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Plan: `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md`
- Prior Child Gate: `docs/superpowers/issues/2026-06-24-m4-equilibrium-issue-0300-add-electrolyte-held2-readiness-and-born-exactness-gate.md`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Direct planning approval: user requested `$superpowers-project:initiate-workflow resolve the next issue for milestone 4`; live M4 queue inspection showed #191 as the only open M4 issue and blocked by electrolyte TPD, HELD2 phase discovery, Stage III refinement, postsolve certification, and public admission.

## Outcome Proof

**Intent:** Replace the remaining "no electrolyte TPD evidence" blocker with a retained native-backed charge-neutral screening gate while leaving full HELD2 discovery and public electrolyte admission behind later proof gates.
**Current Behavior:** The native postsolve explicitly rejects neutral TPD certification for charged systems with `neutral_tpd_not_valid_for_charged_system`, and #300 leaves electrolyte TPD as a pending #191 gate.
**Expected Outcome:** A retained checker exits successfully only when #269 source evidence, #300 reduced-basis/Born readiness evidence, native charge-neutral TPD screening, finite candidate metrics, and closed public electrolyte route state all pass.
**Target Output:** `scripts/validation/check_electrolyte_tpd_gate.py --json --require-source-gate --require-held2-readiness --require-native-tpd --require-public-routes-closed --require-complete` returns `complete: true` with no blockers and reports finite `min_tpd`, candidate count, selected candidate count, and maximum candidate charge residual.
**Owner:** M4 equilibrium package owner.
**Interface:** Native `_native_electrolyte_tpd_phase_discovery` binding, retained validation checker JSON, pytest contracts, M4 issue mirror, and M4 milestone tracker.
**Cutover:** The new checker becomes the next #191 child proof oracle; #191 remains blocked by HELD2 dual phase discovery, Stage III electrolyte refinement, postsolve electrolyte phase-set certification, and public electrolyte route admission.
**Replaced Path:** The charged-system postsolve hole where neutral TPD is the only available certificate is displaced for validation by a charge-neutral electrolyte-specific TPD screening gate.
**Evidence:** Failing-then-passing pytest contract, checker JSON, plan validators, docs/mirror updates, GitHub issue/PR closure evidence, and cleanup proof.
**Acceptance Proof:** Acceptance is proven when the native binding produces charge-neutral finite candidate diagnostics for the source-backed Khudaida fixture, the checker has `complete: true`, public `electrolyte_lle` remains closed, and the issue PR closes the new child issue.
**Stop Criteria:** Stop if native pressure-root trial phases cannot be evaluated for the source fixture, if any candidate composition violates charge residual `1.0e-8`, if the gate opens public electrolyte routes, or if solving full HELD2 candidate discovery becomes necessary to satisfy the slice.
**Avoid:** Do not add public electrolyte routes, full HELD2 dual-loop discovery, Stage III route refinement, electrolyte postsolve admission, reactive routes, regression work, downstream study logic, or release claims.
**Risk:** A deterministic charge-neutral TPD screen can be mistaken for full HELD2; all user-facing evidence must identify it as a screening gate and name the remaining HELD2 blockers.

## Implementation Boundaries

**Files To Create:** `scripts/validation/check_electrolyte_tpd_gate.py`, `tests/native/contracts/test_electrolyte_tpd_gate.py`, `docs/superpowers/issues/2026-06-24-m4-equilibrium-issue-0302-add-electrolyte-charge-neutral-tpd-gate.md`.
**Files To Modify:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`, `scripts/validation/check_electrolyte_held2_readiness.py`, `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`, and `docs/superpowers/milestones/M4-equilibrium/README.md`.
**Files To Avoid:** Public workflow route admission maps beyond closed-state assertions, regression package files, provider EOS implementation files, downstream repositories, generated build trees, and paper-validation figure assets.
**Source Of Truth:** M4 GFPE milestone doctrine, #191 source spec, #269 source fixture checker, #300 readiness checker, and native neutral TPD implementation patterns.
**Read Path:** Read source fixture and public route state through `check_electrolyte_gfpe_gate.py`; read #300 readiness through `check_electrolyte_held2_readiness.py`; read native pressure-root TPD mechanics from `two_phase_eos_route.cpp`.
**Write Path:** Write one native diagnostic entrypoint, one checker, one contract test module, one issue mirror, and M4 tracker updates.
**Integration Points:** `evaluate_unit_phase_block_at_pressure_root`, `NeutralPhaseDiscoveryResult`, pybind11 module registration, `_native.py` extension loading, checker CLI payload evaluation, and issue dependency sync.
**Migration Or Cutover:** The checker becomes the executable gate for the electrolyte TPD blocker; it does not modify public route selection.
**Replaced Path Handling:** Keep neutral TPD rejected for charged postsolve certification until an electrolyte postsolve certification issue lands; this issue only supplies the electrolyte-specific validation diagnostic.
**Acceptance Proof Gate:** The proof oracle commands below must pass before push, PR creation, merge, and issue close.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Next M4 issue | Live M4 queue plus #191 blocker text | Create the next child under #191 for electrolyte charge-neutral TPD screening. | Converts a blocked parent into a resolvable PR-sized issue. | No | M4 owner |
| Native versus Python ownership | Repo policy plus current neutral TPD implementation | Put TPD candidate evaluation in native C++ and use Python only as the retained validation/checker interface. | Keeps thermodynamic screening near pressure-root and gradient code. | No | M4 owner |
| Scope limit | #300 remaining gates | Prove deterministic charge-neutral TPD screening, not full HELD2 dual-loop discovery or route admission. | Prevents overclaiming while removing the closest blocker. | No | M4 owner |
| Test complete | Engineering metrics gate | Complete means checker JSON `complete: true`, finite native TPD candidates, max candidate charge residual <= `1.0e-8`, public electrolyte route closed, and targeted tests passing. | Gives numerical pass/fail criteria. | No | M4 owner |
| Public route state | GFPE capability doctrine | `electrolyte_lle` remains closed. | Protects capability claims. | No | M4 owner |
| Remaining HELD2 work | #191 acceptance | HELD2 dual phase discovery, Stage III refinement, postsolve certification, and public admission remain pending. | Keeps the parent issue blocked until route-quality proof exists. | No | M4 owner |

## Acceptance Criteria

- [ ] A GitHub child issue and local mirror exist for the electrolyte charge-neutral TPD gate and block #191.
- [ ] Native equilibrium exposes `_native_electrolyte_tpd_phase_discovery` with charge-neutral candidate screening for source-backed electrolyte compositions.
- [ ] Candidate TPD values are finite, candidate count is positive, selected candidate count is positive, and maximum candidate charge residual is <= `1.0e-8`.
- [ ] The retained checker consumes #269 source evidence and #300 readiness evidence before granting electrolyte TPD gate completion.
- [ ] The checker reports `readiness_only: true`, `full_held2_claimed: false`, and public electrolyte routes remain closed.
- [ ] #191 and M4 README show this child closed after merge and list the remaining HELD2/postsolve/public-admission blockers.

## Non-Goals

- No public `electrolyte_lle` route admission.
- No full HELD2 dual-loop or Stage III electrolyte route refinement.
- No charged-system postsolve certification cutover.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.
- No provider EOS rewrite.

## Tasks

### Task 1: Publish The Child Issue And Mirror

**Use Cases:**
- A milestone reviewer needs #191 blocked by a concrete issue rather than an unowned blocker phrase.
- A resolver needs a local issue mirror with acceptance criteria, proof oracle, and outcome summary.
- GitHub dependency readiness should be able to keep #191 blocked until this child closes.

**Files:**
- Create: `docs/superpowers/issues/2026-06-24-m4-equilibrium-issue-0302-add-electrolyte-charge-neutral-tpd-gate.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Create the GitHub issue in `M4 - Equilibrium` with ready labels and a body matching this plan.**
- [ ] **Step 2: Write the local mirror with Outcome Summary, proof oracle, and project merge metadata.**
- [ ] **Step 3: Add the GitHub dependency edge so #191 is blocked by this child.**
- [ ] **Step 4: Update the #191 mirror and M4 README to show this child as the active next gate.**

### Task 2: Write The Failing Native TPD Contract

**Use Cases:**
- A charged source fixture must fail the test suite until the native electrolyte TPD diagnostic exists.
- The test must prove charge-neutral candidates rather than accepting neutral TPD on charged compositions.
- Public electrolyte route closure must be asserted beside the new diagnostic.

**Files:**
- Create: `tests/native/contracts/test_electrolyte_tpd_gate.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`

- [ ] **Step 1: Add a test that imports `extension_native_core()` and asserts `_native_electrolyte_tpd_phase_discovery` exists.**
- [ ] **Step 2: Add a test that calls the future checker payload and asserts finite TPD metrics, charge residual <= `1.0e-8`, and closed public routes.**
- [ ] **Step 3: Run `uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_tpd_gate.py -q` and confirm the expected red failure.**

### Task 3: Implement Native Charge-Neutral TPD Screening

**Use Cases:**
- Native code must compute electrolyte TPD from pressure-root trial phase blocks, not from a hand-authored Python payload.
- Trial compositions must stay inside the electroneutral subspace for the electrolyte charge vector.
- The payload must preserve enough `NeutralPhaseDiscoveryResult` fields for later HELD2 Stage I/II work.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/_native_core.pyi`

- [ ] **Step 1: Add charge-neutral trial validation and projected electrochemical-potential TPD evaluation.**
- [ ] **Step 2: Add `evaluate_electrolyte_tpd_phase_discovery` using existing pressure-root phase-block evaluation and `NeutralPhaseDiscoveryResult`.**
- [ ] **Step 3: Bind the function as `_native_electrolyte_tpd_phase_discovery`.**
- [ ] **Step 4: Run the red test again and keep iterating until the native binding passes.**

### Task 4: Add The Retained Checker And Tracker Updates

**Use Cases:**
- The proof oracle must fail closed if #269 source evidence or #300 readiness evidence regresses.
- A future HELD2 worker needs a stable JSON payload with TPD metrics and remaining gates.
- The M4 tracker must show this as a prerequisite gate rather than public electrolyte support.
- The cutover evidence must replace the old charged-system neutral-TPD blocker with this electrolyte-specific checker while preserving later postsolve certification as a separate path.

**Files:**
- Create: `scripts/validation/check_electrolyte_tpd_gate.py`
- Modify: `scripts/validation/check_electrolyte_held2_readiness.py`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Implement `evaluate_tpd_gate` with `--require-source-gate`, `--require-held2-readiness`, `--require-native-tpd`, `--require-public-routes-closed`, and `--require-complete`.**
- [ ] **Step 2: Record finite `min_tpd`, candidate counts, selected counts, max candidate charge residual, phase kinds, and remaining HELD2 gates.**
- [ ] **Step 3: Update HELD2 readiness pending-gate text to move electrolyte deterministic TPD screening into ready prerequisites while leaving dual discovery and postsolve admission pending.**
- [ ] **Step 4: Update the M4 tracker and #191 mirror with this child and remaining blockers.**

### Task 5: Verify, Commit, PR, Merge, And Sync Main

**Use Cases:**
- The child issue must close through a PR with proof rather than local-only evidence.
- The repo must return to clean synced `main` after merge.
- Dependency readiness should keep #191 blocked only by the next real HELD2/postsolve/public-admission gates.

**Files:**
- Test: all files changed by Tasks 1-4.

- [ ] **Step 1: Run all proof oracle commands.**
- [ ] **Step 2: Run the repo cleanup hook.**
- [ ] **Step 3: Commit, push, open a PR that closes the new child issue, and merge it after clean premerge proof.**
- [ ] **Step 4: Sync local `main` and `origin/main`, remove the owned worktree/branch, and run dependency readiness sync.**

## Proof Oracle

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-task-use-cases.ps1 -PlanPath docs\superpowers\plans\2026-06-24-m4-equilibrium-issue-0302-electrolyte-charge-neutral-tpd-gate-plan.md
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate-plan-outcome-proof.ps1 -PlanPath docs\superpowers\plans\2026-06-24-m4-equilibrium-issue-0302-electrolyte-charge-neutral-tpd-gate-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python scripts/validation/check_electrolyte_tpd_gate.py --json --require-source-gate --require-held2-readiness --require-native-tpd --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_tpd_gate.py tests/native/contracts/test_electrolyte_held2_readiness_checker.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
