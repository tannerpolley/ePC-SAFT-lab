# Associating GFPE Exact-Derivative Admission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve GitHub issue #190 by admitting the narrow public associating neutral GFPE route only after #145 proves source-backed association Hessian correctness.

**Architecture:** Treat #190 as the admission layer after #145. It consumes #145's Gross and Sadowski 2002 internal proof, adds public route eligibility and capability evidence for the exact proven association configuration, and keeps electrolyte, reactive, generalized phase-count, and LLLE claims closed.

**Tech Stack:** Python public API and validation checkers; C++/pybind11 selector and Ipopt route diagnostics; CppAD implicit association Hessians; pytest; GitHub issue dependency readiness.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md`
- Source Issue: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md`
- Source Plan: `docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates-plan.md`
- GitHub Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/190`
- Milestone: `M4 - Equilibrium`
- AFK/HITL: `HITL`
- Current blocker: #145 must be closed and merged first.
- Required upstream proof: `associating_neutral_lle_gross_2002_internal_exact_hessian` from the #145 plan.

## Acceptance Criteria

- [x] Associating route admission requires exact association derivative evidence appropriate to the tested association configuration.
- [x] Approximate explicit association closures remain labeled approximate and are not accepted as exact production proof.
- [x] Associating GFPE diagnostics distinguish EOS closure, derivative, solver, and postsolve certification failures.
- [x] Capability evidence names the exact associating configurations proven.
- [x] Public associating admission is limited to the two-phase neutral LLE configuration proven by #145 until a later generalized phase-set issue expands it.
- [x] Electrolyte #191 remains outside #190 and does not borrow associating admission evidence.

## Test Complete And Metrics

Test complete means #145 proof receipts are present, the public associating route gate checker reports `complete: true`, and the route exposes only the exact proven scope.

Required gates:

- The #145 checker output exists and reports complete source-backed Gross 2002 evidence.
- Public `Equilibrium(..., route="lle")` accepts the Gross 2002 methanol/cyclohexane associating mixture and reports exact association Hessian diagnostics.
- Public associating admission rejects ionic, reactive, unsupported phase-count, and missing-proof cases with explicit blocker diagnostics.
- Capability evidence names `Gross2002 Figure8 methanol-cyclohexane`, `assoc_scheme=2B`, `k_ij=0.051`, and `cppad_implicit_association`.
- Exact Hessian, postsolve, and site diagnostics match the #145 thresholds.

## Tasks

### Task 1: Verify #145 Proof Receipts

**Use Cases:**
- #190 cannot start while #145 is open or while the local #145 proof checker is incomplete.
- A worker sees exactly which #145 receipts are trusted for public admission.
- The plan fails loudly if the old generic #190 blocker text is the only evidence.

**Files:**
- Test: `tests/native/contracts/test_associating_lle_gross_2002_checker.py`
- Test: `packages/epcsaft-equilibrium/tests/native/results/test_associating_lle_reference_values.py`
- Modify: `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md`

- [x] **Step 1: Add a preflight test or checker assertion.** Require the #145 checker output to include source data, exact association Hessian evidence, and public route closed state.
- [x] **Step 2: Run preflight.** Run `uv run python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-route-closed --require-complete`; expected result is pass before #190 code changes.
- [x] **Step 3: Sync issue state.** Confirm GitHub #190 has no open blockers after #145 is merged, then update the local issue mirror readiness from `blocked` to `ready`.
- [x] **Step 4: Commit.** Commit preflight/readiness synchronization with message `docs: mark associating GFPE admission ready after issue 145`.

### Task 2: Admit The Narrow Public Associating LLE Route

**Use Cases:**
- Public `route="lle"` accepts the exact Gross 2002 associating proof fixture after #145 has supplied proof receipts.
- The same public route rejects unsupported associating configurations and explains which proof gate is missing.
- Public route maps do not duplicate route names or silently expand electrolyte/reactive admission.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.*`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.*`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py`
- Modify: `scripts/dev/generate_equilibrium_activation.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`

- [x] **Step 1: Write failing public API tests.** Add tests that call `Equilibrium(mixture, route="lle", T=..., P=..., z=...).solve()` for the Gross 2002 fixture and assert exact association Hessian diagnostics in the result.
- [x] **Step 2: Write rejection tests.** Add tests for ionic associating mixtures, reactive inputs, unsupported phase counts, and associating systems without retained proof evidence.
- [x] **Step 3: Run public API tests and verify failure.** Run `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`; expected result is failure on the newly admitted public associating case.
- [x] **Step 4: Implement selector admission.** Replace the blanket associating rejection for the proven LLE case with a source-evidence gate keyed by the activation matrix and #145 proof receipt. Keep all other associating route families closed.
- [x] **Step 5: Regenerate activation mirrors.** Run `uv run python scripts/dev/generate_equilibrium_activation.py` and inspect the generated Python mirror.
- [x] **Step 6: Re-run public API tests.** Run the same command; expected result is pass.
- [x] **Step 7: Commit.** Commit admission behavior with message `feat: admit proven associating neutral LLE route`.

### Task 3: Add Associating GFPE Gate Checker And Capability Evidence

**Use Cases:**
- A release checker can distinguish internal #145 proof, public #190 admission, and future generalized phase-set work.
- Capability evidence names the exact associating configuration and source data.
- Electrolyte #191 cannot pass by pointing to associating #190 proof.

**Files:**
- Create: `scripts/validation/check_associating_gfpe_gate.py`
- Create: `tests/native/contracts/test_associating_gfpe_gate_checker.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

- [x] **Step 1: Write the gate checker contract.** Require checker flags for source proof, exact association Hessian, public associating route admission, unsupported route rejection, and no electrolyte admission.
- [x] **Step 2: Implement the checker.** `check_associating_gfpe_gate.py` must call the public route for the proven Gross 2002 case and inspect capability evidence for exact scope.
- [x] **Step 3: Update capability evidence.** Add a production row for the proven associating neutral LLE scope with source fixture and exact backend fields.
- [x] **Step 4: Update M4 docs.** Move the queue note so #190 closure is the final association gate before #191 electrolyte work resumes.
- [x] **Step 5: Run checker tests.** Run `uv run python run_pytest.py tests/native/contracts/test_associating_gfpe_gate_checker.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`; expected result is pass.
- [x] **Step 6: Commit.** Commit checker and docs with message `docs: record associating GFPE admission gate`.

## Proof Oracle

- `uv run python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-complete`
- `uv run python scripts/validation/check_associating_gfpe_gate.py --json --require-source-data --require-public-admission --require-exact-association-hessian --require-electrolyte-closed --require-complete`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_equilibrium.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py packages/epcsaft-equilibrium/tests/native/results/test_associating_lle_reference_values.py tests/native/contracts/test_associating_gfpe_gate_checker.py -q`
- `uv run python run_pytest.py packages/epcsaft/tests/native/contracts/test_association_implicit_derivative_contract.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft/tests/native/state/test_fugacity_derivatives.py -q`
- `uv run python scripts/dev/validate_project.py quick`
- `bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .`

## Non-Goals And Boundaries

- No electrolyte, reactive, CE, CPE, or LLLE admission.
- No generalized associating phase-count claim.
- No public claim for two-associating-component systems unless a retained stress proof is added and separately admitted.
- No approximate explicit association closure accepted as exact evidence.
