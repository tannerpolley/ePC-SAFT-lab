# Electrolyte HELD2 Readiness And Born Exactness Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve GitHub issue #300 by adding the next #191 electrolyte prerequisite gate: charge-neutral reduced-basis proof, exact Born SSM/DS derivative receipts, HELD2 readiness diagnostics, and closed public electrolyte route evidence.

**Architecture:** This is a readiness and prerequisite gate, not public electrolyte GFPE admission. The checker consumes the existing Khudaida closed-admission source gate, adds an exact reduced amount lift for the NaCl electrolyte basis, verifies CppAD-backed Born SSM/DS derivative receipts through the provider public state API, and records which HELD2/electrolyte route gates remain closed. Capability and registry evidence stay in M4 equilibrium scope and do not broaden public route keys.

**Tech Stack:** Python validation checker, pytest contracts through `run_pytest.py`, `epcsaft` public state derivative APIs, `epcsaft-equilibrium` capability metadata, M4 GFPE registry, GitHub issue mirrors.

---

## Intake

- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/300`
- Parent Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Source Issue: `docs/superpowers/issues/2026-06-24-m4-equilibrium-issue-0300-add-electrolyte-held2-readiness-and-born-exactness-gate.md`
- Source Plan: `docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0300-electrolyte-held2-readiness-born-exactness-gate-plan.md`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium` with provider derivative receipts consumed through public `epcsaft` APIs.

## Outcome Proof

**Intent:** Prove the next electrolyte GFPE prerequisite after #269 without claiming electrolyte production support.
**Current Behavior:** #269 proves Khudaida source parsing, explicit-ion expansion, native electrolyte/charge diagnostics, and closed public route state, but #191 still lacks a retained reduced-basis and exact Born SSM/DS readiness receipt for HELD2 planning.
**Expected Outcome:** A retained checker exits successfully only when source-backed electrolyte inputs pass #269, reduced electroneutral amount lifting is exact, CppAD Born SSM/DS derivative receipts are finite and active, HELD2 readiness is labeled as prerequisite-only, and public electrolyte routes remain closed.
**Target Output:** `scripts/validation/check_electrolyte_held2_readiness.py --json --require-source-gate --require-reduced-basis --require-born-ssm-ds --require-public-routes-closed --require-complete` returns `complete: true` with no blockers.
**Owner:** M4 equilibrium package owner.
**Interface:** Validation checker, M4 registry row, capability contract tests, and issue mirror evidence.
**Cutover:** The new checker becomes the #300 proof oracle and a prerequisite row under `PE-Electrolyte LLE/TP Flash`; #191 remains blocked until later electrolyte TPD, HELD2 dual discovery, postsolve certification, and public admission gates land.
**Replaced Path:** The old #191 parent direct plan cannot enter resolve execution because it fails the Task Use Cases validator; #300 supplies the next executable child path instead.
**Evidence:** Checker JSON, targeted pytest contracts, docs validation, GitHub dependency edge where #300 blocks #191.
**Acceptance Proof:** Acceptance is proven when the #300 proof oracle passes and the registry/capability tests still reject public `electrolyte_lle` exposure.
**Stop Criteria:** Stop if exact Born SSM/DS receipts are unavailable through public provider APIs, if reduced-basis charge closure is not exact for the source fixture, if route admission opens by accident, or if the implementation requires provider EOS rewrites outside this issue.
**Avoid:** Do not add public electrolyte routes, electrolyte TPD minimization, full HELD2 dual-loop discovery, reactive routes, regression work, or release claims.
**Risk:** The readiness gate can be misread as full HELD2; the checker and docs must state that electrolyte TPD, candidate discovery, postsolve certification, and public admission remain pending.

## Implementation Boundaries

**Files To Create:** `scripts/validation/check_electrolyte_held2_readiness.py`, `tests/native/contracts/test_electrolyte_held2_readiness_checker.py`, and `docs/superpowers/issues/2026-06-24-m4-equilibrium-issue-0300-add-electrolyte-held2-readiness-and-born-exactness-gate.md`.
**Files To Modify:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`, `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`, `tests/native/contracts/test_generalized_equilibrium_registry.py`, `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml` and `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`, `docs/superpowers/milestones/M4-equilibrium/README.md`, and `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`.
**Files To Avoid:** Native C++ route admission files, public workflow route maps, regression package files, downstream repositories, and provider EOS implementation files unless an existing public derivative receipt cannot be consumed.
**Source Of Truth:** `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`, #191 source spec, #269 checker, and provider Born derivative tests.
**Read Path:** Read Khudaida data through `check_electrolyte_gfpe_gate.evaluate_case_dir`, provider derivative receipts through `ePCSAFTState` public methods, and route exposure state through `epcsaft_equilibrium.capabilities()`.
**Write Path:** Write one M4 checker, one contract test module, capability evidence rows, registry evidence rows, and tracker docs.
**Integration Points:** `scripts/validation/check_electrolyte_gfpe_gate.py`, `epcsaft.state.native_adapter.ePCSAFTState`, `epcsaft_equilibrium.capabilities()`, and `tests/native/contracts/test_generalized_equilibrium_registry.py`.
**Migration Or Cutover:** The #191 parent stays blocked by #300 until this PR merges; after merge, dependency sync can unblock #191 for the next child.
**Replaced Path Handling:** Do not execute the invalid #191 parent plan directly; keep its mirror updated to point at completed and pending child gates.
**Acceptance Proof Gate:** The proof oracle commands in this plan must pass before push, PR, merge, or issue close.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Route scope | User request plus #191 state | Create and resolve #300 as the next ready M4 child because #191 is a HITL parent with missing direct-plan gates. | Keeps the work PR-sized and honest. | No | M4 owner |
| Public route admission | GFPE doctrine | Keep `electrolyte_lle` closed. | Avoids unsupported capability claims. | No | M4 owner |
| Provider derivative ownership | Repo milestone policy | Consume public provider Born SSM/DS receipts but avoid provider implementation rewrites. | Keeps M4 work inside equilibrium scope. | No | M4 owner |
| HELD2 status | #191 acceptance | Record readiness only; electrolyte TPD, Stage I/II/III, and postsolve certification remain pending. | Prevents readiness evidence from being treated as full algorithm adoption. | No | M4 owner |
| Test complete | Write-plan metrics gate | Checker JSON, targeted pytest, and docs validation define completion. | Gives measurable pass/fail evidence. | No | M4 owner |

## Acceptance Criteria

- [ ] The #300 mirror and M4 README show #300 ready and #191 blocked by #300.
- [ ] `check_electrolyte_held2_readiness.py` consumes the #269 source gate and fails closed when source gate evidence is missing.
- [ ] The checker proves reduced NaCl amount lifting to explicit ions with charge residual <= `1.0e-10`.
- [ ] The checker consumes CppAD-backed Born SSM/DS derivative receipts with finite composition, fugacity, activity-parameter, `d_born`, and `f_solv` derivative arrays.
- [ ] The checker reports HELD2 readiness without claiming electrolyte TPD, dual phase discovery, Stage III refinement, postsolve certification, or public route admission.
- [ ] Capabilities and registry evidence distinguish this prerequisite from production electrolyte GFPE.

## Non-Goals

- No public `electrolyte_lle` route.
- No electrolyte TPD minimizer or HELD2 dual-loop implementation.
- No reactive, CE, CPE, regression, downstream, release, or publication claim.
- No provider EOS rewrite unless the existing public derivative receipt is proven unusable.

## Tasks

### Task 1: Add Tracker And Plan Evidence

**Use Cases:**
- A roadmap reviewer needs #191 blocked by a concrete child instead of a stale parent blocker list.
- A worker needs a source plan and issue mirror that pass resolve-issue validation.
- The old invalid #191 direct-plan path must be displaced by a child issue with concrete proof gates and no public admission claim.

**Files:**
- Create: `docs/superpowers/issues/2026-06-24-m4-equilibrium-issue-0300-add-electrolyte-held2-readiness-and-born-exactness-gate.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] **Step 1: Write #300 local mirror.**
- [ ] **Step 2: Update #191 mirror to show #300 as the active blocker.**
- [ ] **Step 3: Update the M4 README current plans, open queue, and queue guard.**
- [ ] **Step 4: Run `uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0300-electrolyte-held2-readiness-born-exactness-gate-plan.md`.**

### Task 2: Write The Failing Readiness Checker Contract

**Use Cases:**
- The checker must reject incomplete source, reduced-basis, Born, HELD2, or route-closure evidence before implementation code is trusted.
- A future HELD2 worker needs a stable JSON schema separating readiness from algorithm completion.
- Acceptance evidence must include cutover protection so a public electrolyte route cannot open silently.

**Files:**
- Create: `tests/native/contracts/test_electrolyte_held2_readiness_checker.py`
- Create: `scripts/validation/check_electrolyte_held2_readiness.py`

- [ ] **Step 1: Add tests for `evaluate_payload` complete and blocker cases.**
- [ ] **Step 2: Add a CLI test that expects incomplete evidence to fail before implementation.**
- [ ] **Step 3: Run `uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_held2_readiness_checker.py -q` and confirm the expected red failure.**

### Task 3: Implement Reduced-Basis And Born SSM/DS Evidence

**Use Cases:**
- The source-backed NaCl fixture must have an exact reduced amount lift before HELD2 can use charge-neutral variables.
- The Born SSM/DS derivative receipt must be real provider output, not a hand-authored payload.
- The checker must carry evidence fields that a later electrolyte TPD/HELD2 issue can consume.

**Files:**
- Create: `scripts/validation/check_electrolyte_held2_readiness.py`

- [ ] **Step 1: Consume `check_electrolyte_gfpe_gate.evaluate_case_dir` with all #269 requirements enabled.**
- [ ] **Step 2: Add reduced amount basis matrix rows for `H2O`, `Ethanol`, `Butanol`, and `NaCl` lifted to `H2O`, `Ethanol`, `Butanol`, `Na+`, and `Cl-`.**
- [ ] **Step 3: Build a source-backed liquid electrolyte state and collect `composition_derivative_residual_helmholtz`, `ln_fugacity_composition_derivative_result`, `activity_parameter_derivative_result`, and `born_parameter_derivatives`.**
- [ ] **Step 4: Mark HELD2 readiness complete only for source gate, reduced basis, exact Born SSM/DS receipts, and closed routes.**

### Task 4: Record Capability And Registry Evidence

**Use Cases:**
- A package user must not see public electrolyte support after this gate.
- A milestone reviewer needs a retained prerequisite row for the electrolyte family.
- The old #191 parent path must show what remains after #300 closes.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `tests/native/contracts/test_generalized_equilibrium_registry.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml` and `docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md`

- [ ] **Step 1: Add a non-production derivative evidence row for electrolyte HELD2 readiness.**
- [ ] **Step 2: Assert capability rows still keep `electrolyte_lle` out of public routes and production families.**
- [ ] **Step 3: Add a registry evidence row under `PE-Electrolyte LLE/TP Flash`.**
- [ ] **Step 4: Update docs and mirrors with #300 evidence and remaining #191 blockers.**

### Task 5: Validate, Commit, PR, And Merge

**Use Cases:**
- A merge reviewer needs exact proof that #300 is complete and #191 remains honestly blocked by later gates.
- The repo must not retain stale generated process state or orphaned worktree changes after merge.
- Dependency sync should unblock or relabel parent issue state only when GitHub blockers are closed.

**Files:**
- Test: all files changed by Tasks 1-4.

- [ ] **Step 1: Run the #300 proof oracle commands.**
- [ ] **Step 2: Run the repo cleanup hook.**
- [ ] **Step 3: Commit, push, open a PR that closes #300, merge it when checks pass, and sync local `main` with `origin/main`.**
- [ ] **Step 4: Run dependency readiness sync for #300 and report the next #191 blocker.**

## Proof Oracle

```powershell
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0300-electrolyte-held2-readiness-born-exactness-gate-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-24-m4-equilibrium-issue-0300-electrolyte-held2-readiness-born-exactness-gate-plan.md
uv run --no-sync python scripts/validation/check_electrolyte_held2_readiness.py --json --require-source-gate --require-reduced-basis --require-born-ssm-ds --require-public-routes-closed --require-complete
uv run --no-sync python run_pytest.py tests/native/contracts/test_electrolyte_held2_readiness_checker.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_equilibrium_registry.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py -q
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```
