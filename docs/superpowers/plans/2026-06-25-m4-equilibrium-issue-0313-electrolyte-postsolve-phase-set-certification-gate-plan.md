# Electrolyte Postsolve Phase-Set Certification Gate Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Resolve GitHub issue #313 by certifying the refined electrolyte phase
set after #312 Stage III refinement closes.

**Architecture:** This is the physical postsolve acceptance gate for
electrolyte GFPE. It consumes the Stage III reduced-variable solution and
certifies explicit-ion material reconstruction, per-phase charge balance,
neutral transfer, mean-ionic transfer, pressure consistency, phase amounts,
composition normalization, and domain margins. Public route admission remains
closed until #314.

**Tech Stack:** C++ equilibrium native core, pybind11 bindings, Python
validation checker, pytest contracts through `run_pytest.py`, M4 issue mirrors,
M4 benchmark registry, GitHub dependencies.

---

## Intake

- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/313`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Issue: `docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0313-add-electrolyte-postsolve-phase-set-certification-gate.md`
- Source Plan: `docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md`
- Prior Child Gate: `docs/superpowers/issues/2026-06-25-m4-equilibrium-issue-0312-add-electrolyte-held2-stage-iii-reduced-variable-refinement-gate.md`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`

## Outcome Proof

**Intent:** Convert Stage III electrolyte solver evidence into physical
postsolve phase-set certification.
**Current Behavior:** #312 is planned to prove strict reduced-variable Stage
III convergence; that is still not enough to admit a public electrolyte route.
**Expected Outcome:** A retained checker exits successfully only when #312 is
closed and the refined phase set passes material, charge, pressure, transfer,
amount, and domain diagnostics.
**Target Output:** `scripts/validation/check_electrolyte_postsolve_certification.py --json --require-stage-iii --require-postsolve-certification --require-public-routes-closed --require-complete` returns `complete: true`.
**Owner:** M4 equilibrium package owner.
**Interface:** Electrolyte postsolve payload, retained checker JSON, pytest
contracts, M4 issue mirror, registry row, and M4 README.
**Cutover:** This checker becomes the #313 proof oracle and removes the
postsolve blocker from #191 after merge.
**Replaced Path:** Stage III convergence-only evidence remains prerequisite
evidence and no longer stands in for physical electrolyte acceptance.
**Evidence:** Failing-then-passing postsolve tests, checker JSON, explicit-ion
material and charge receipts, transfer residual receipts, docs validation, and
GitHub issue/PR closure evidence.
**Acceptance Proof:** Acceptance is proven when postsolve certification
consumes #312, reports explicit-ion reconstruction, charge balance, neutral and
mean-ionic transfer residuals, pressure consistency, phase amounts, and domain
margins with closed public route state.
**Stop Criteria:** Stop if any physical certification family is absent or if a
public electrolyte route must be opened to satisfy this gate.
**Avoid:** Do not admit public electrolyte routes, add reactive routes,
regression work, downstream study logic, or release claims.
**Risk:** Postsolve acceptance can be weakened into a finite-variable check;
this gate must separate each physical diagnostic family.

## Implementation Boundaries

**Files To Create:** `scripts/validation/check_electrolyte_postsolve_certification.py`, `tests/native/contracts/test_electrolyte_postsolve_certification.py`.
**Files To Modify:** Native electrolyte postsolve diagnostics and bindings in
`packages/epcsaft-equilibrium/**`, capability/registry evidence, the #191/#313
issue mirrors, and the M4 README.
**Files To Avoid:** Public route admission maps beyond closed-state assertions,
regression package files, downstream repositories, generated build trees, and
provider EOS internals unless a public provider contract receipt is consumed.
**Source Of Truth:** #191 source spec, M4 GFPE doctrine, #312 Stage III proof,
and the electrolyte methodology paper context already cited by #191.
**Read Path:** Consume #312 through
`check_electrolyte_stage_iii_refinement.py`.
**Write Path:** Write one postsolve checker, one contract test module, native
postsolve diagnostic support, capability/registry evidence rows, and tracker
updates.
**Integration Points:** Explicit-ion reconstruction, charge residuals,
pressure residuals, neutral and mean-ionic transfer residuals, domain margins,
capability evidence, and M4 registry evidence.
**Migration Or Cutover:** #191 remains blocked by #313 until this PR merges;
after merge, #314 becomes the final blocker.
**Replaced Path Handling:** Keep #312 Stage III evidence as prerequisite
solver evidence; do not rewrite it into public admission evidence.
**Acceptance Proof Gate:** The proof oracle commands below must pass before
push, PR creation, merge, and issue close.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Next child after Stage III | #191 checkpoint sequence | #313 owns postsolve certification. | Keeps convergence separate from physical acceptance. | No | M4 owner |
| Certification families | Thermodynamic acceptance contract | Material, charge, transfer, pressure, phase, and domain diagnostics are separate. | Prevents one aggregate residual from hiding failed physics. | No | M4 owner |
| Public route state | #191 plan | Keep public electrolyte routes closed. | Reserves admission for #314. | No | M4 owner |

## Required Contract Tests

- `test_postsolve_requires_stage_iii_gate`: the checker rejects missing #312
  evidence.
- `test_explicit_ion_reconstruction_closes`: reduced variables reconstruct
  explicit ions within retained tolerances.
- `test_phase_charge_balance_closes`: every certified phase has accepted charge
  residuals.
- `test_transfer_residual_families_are_separate`: neutral transfer and
  mean-ionic transfer residuals are reported separately.
- `test_pressure_and_phase_amounts_are_certified`: pressure consistency,
  positive phase amounts, normalized compositions, and domain margins are
  retained.
- `test_postsolve_rejects_public_admission_status`: public admission cannot be
  marked complete under #313.
- `test_public_electrolyte_routes_stay_closed`: capability and registry
  evidence keep public electrolyte routes closed.

## Acceptance Criteria

- [ ] The checker consumes the closed #312 Stage III refinement gate.
- [ ] Explicit-ion material reconstruction closes to a retained tolerance from
  the reduced electroneutral solution.
- [ ] Per-phase and total charge residuals are retained and accepted.
- [ ] Neutral transfer and mean-ionic transfer residuals are reported
  separately with documented conventions.
- [ ] Pressure consistency, phase amounts, composition normalization,
  nonnegativity margins, and domain margins are retained.
- [ ] Negative tests reject Stage III-only results, phase-collapsed results,
  charge-imbalanced phases, missing transfer diagnostics, and premature
  public-admission status.
- [ ] Capabilities and registry evidence keep public electrolyte routes closed.
- [ ] #191 and the M4 README name #314 as the only remaining M4 electrolyte
  gate after this issue closes.

## Non-Goals

- No public electrolyte route admission.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.

## Tasks

### Task 1: Define The Postsolve Certification Payload

**Use Cases:**

- A reviewer needs physical acceptance diagnostics beyond solver status.
- A later public admission issue needs a single certification receipt.

**Files:**

- `scripts/validation/check_electrolyte_postsolve_certification.py`
- `tests/native/contracts/test_electrolyte_postsolve_certification.py`

- [ ] Add missing-prerequisite tests for #312.
- [ ] Add certification-family tests for material, charge, transfer, pressure,
  phase, and domain diagnostics.
- [ ] Add negative tests for public-admission status under #313.

### Task 2: Add Postsolve Diagnostics

**Use Cases:**

- The refined reduced solution must map back to a physically accepted
  explicit-ion phase set.
- The checker needs retained tolerances and residuals for every diagnostic
  family.

**Files:**

- `packages/epcsaft-equilibrium/**`
- `scripts/validation/check_electrolyte_postsolve_certification.py`

- [ ] Add explicit-ion reconstruction diagnostics.
- [ ] Add charge, transfer, pressure, amount, and domain diagnostics.
- [ ] Retain tolerance and acceptance metadata.

### Task 3: Preserve Public Capability Boundaries

**Use Cases:**

- A user must not see public electrolyte route support before #314.
- M4 docs must show the final blocker after #313 closes.
- The acceptance evidence must show the cutover from #312 Stage III solver
  proof to #313 postsolve certification without replacing public admission.

**Files:**

- `docs/superpowers/milestones/M4-equilibrium/README.md`
- `docs/superpowers/issues/**`
- `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-benchmark-registry.yaml`

- [ ] Update registry evidence for postsolve certified/route closed state.
- [ ] Update #191 and #313 mirrors after merge.
- [ ] Keep #314 as the final blocker.

## Proof Oracle

```powershell
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0313-electrolyte-postsolve-phase-set-certification-gate-plan.md
uv run --no-sync python scripts/validation/check_electrolyte_postsolve_certification.py --json --require-stage-iii --require-postsolve-certification --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_postsolve_certification.py tests/native/contracts/test_electrolyte_stage_iii_refinement.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
