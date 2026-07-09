# M4 CE Convergence Robustness Hardening Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans`, `superpowers:test-driven-development`, `superpowers:systematic-debugging` for failing convergence gates, and `superpowers:verification-before-completion`.

**Goal:** Turn the seven CE convergence robustness improvements into strict, issue-backed implementation slices that harden accepted standalone CE results without weakening proof gates or producing duplicate plot artifacts.

**Architecture:** Standalone CE remains a single activation-family workflow. Robustness support lives inside CE-owned initialization, continuation, objective, scaling, proof-correction, and diagnostics layers. The public API remains `reactive_speciation`; route metadata may report strategy evidence, but it must not expose new public solver routes.

**Tech Stack:** Python 3.13 source checkout, C++17 equilibrium native core, Ipopt, CppAD-backed EOS derivative path, pytest, retained CSV/JSON diagnostics.

---

Source spec: `docs/superpowers/specs/2026-06-30-m4-ce-convergence-robustness-hardening.md`
Prior implementation plan: `docs/superpowers/plans/2026-06-29-m4-ce-generic-pope-homotopy-continuation-plan.md`
Milestone: `M4 - Equilibrium`
Package owner: `packages/epcsaft-equilibrium`
IntelliJ receipt: CE-scoped IntelliJ MCP was available through `mcp__intellij_index_ePC_SAFT_CE`; `ide_index_status` reported `isDumbMode=false` and `isIndexing=false`.

## Outcome Proof

**Intent:** Harden standalone CE so difficult MEA and synthetic stress points either pass strict final reaction-stationarity proof or fail with a precise class that explains the missing proof.
**Current Behavior:** The current branch can recover at least one hard MEA point through max-min/homotopy, but the convergence envelope is not retained as machine-readable robustness evidence and failure causes are still too coarse for looped repair.
**Expected Outcome:** CE convergence has retained diagnostics, stronger final correction, EOS nonideality continuation, seed escalation policy, scaled reaction proof, extent/nullspace initialization, and sharp failure taxonomy.
**Target Output:** Tests, retained CSV/JSON diagnostics, checker output, and CE result diagnostics show strict stationarity, balance, seed provenance, activity continuation, scaling evidence, and failure classes.
**Owner:** M4 equilibrium package owner for `packages/epcsaft-equilibrium`.
**Interface:** `reactive_speciation`, `ReactiveSpeciationResult.diagnostics`, native CE activation payloads, CE objective/continuation bindings, retained analysis diagnostics, and standalone CE checker output.
**Cutover:** Replace one-off convergence claims and caller-seed escalation ambiguity with retained robustness gates and proof-classified failures.
**Replaced Path:** Ad hoc pointwise solver inspection, plot-only proof, intermediate homotopy acceptance, and vague convergence failure text are displaced by strict final-proof diagnostics.
**Evidence:** Focused native/API tests, retained robustness CSV/JSON artifacts, standalone CE checker receipts, and exact command output from the proof oracle.
**Acceptance Proof:** The proof oracle passes and the retained diagnostics show accepted points below strict stationarity and balance gates, with failures classified by exact gate instead of hidden behind generic convergence status.
**Stop Criteria:** Stop if strict gates must be relaxed, if EOS activity support cannot produce derivative evidence, if final proof depends on intermediate stages, or if the work would broaden into CPE or phase-equilibrium admission.
**Avoid:** Do not add public solver routes, MEA-specific package APIs, downstream metrics, duplicated plot deliverables, or phase-equilibrium behavior.
**Risk:** Scaling and proof-correction changes can mask physical residuals if diagnostics are not separated; accepted proof must continue reporting unscaled physical stationarity and balance norms.

## Implementation Boundaries

**Files To Create:** Focused CE diagnostics tests under `packages/epcsaft-equilibrium/tests/native/diagnostics/`, optional retained robustness artifacts under `analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/results/`, and issue-owned helper tests only when a slice needs them.
**Files To Modify:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`, CE native objective/NLP/continuation files, CE native bindings, CE checker, and focused CE tests.
**Files To Avoid:** Bubble/dew routes, HELD route code, CPE route admission, regression package code, provider public APIs beyond existing EOS derivative contracts, and downstream application repositories.
**Source Of Truth:** This plan, the linked spec, the 2026-06-29 CE homotopy plan, current activation matrix, current CE standard-state contract, and the standalone CE checker.
**Read Path:** Before each task, read the owning CE objective/NLP/continuation code, relevant tests, and retained diagnostics schema touched by that task.
**Write Path:** Add failing tests first, make the smallest CE-owned native/Python change, run focused proof, then update retained diagnostics or checker evidence.
**Integration Points:** CE objective provider, Ipopt proof solve, continuation trace, standard-state activity convention, EOS activity provider, result diagnostics, and standalone CE checker.
**Migration Or Cutover:** Keep public route and existing accepted ideal CE behavior stable while adding stronger internal proof gates and clearer diagnostics.
**Replaced Path Handling:** Remove or demote any old result text that implies caller-seeded or intermediate-stage success is final proof.
**Acceptance Proof Gate:** All issue slices are complete only after their focused tests, plan validators, issue mirror validators, cleanup hook, and final focused CE proof pass.

## Task Plan

### Task 1: Retained CE Robustness Diagnostics

**Use Cases:**
- A maintainer can inspect retained CSV/JSON diagnostics and see acceptance evidence for hard CE points without opening plots.
- A future loop run can select the next repair because failures are recorded by proof gate, seed source, activity path, and stationarity norm.
- The old plot-first proof path is replaced by machine-readable diagnostics that drive acceptance and cutover decisions.

**Files:**
- Modify: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
- Modify: `scripts/validation/check_standalone_ce_gate.py`
- Modify: retained CE analysis data generation only if the current diagnostics schema has no machine-readable robustness output.

- [ ] **Step 1: Add failing diagnostics tests.** Require retained rows for MEA and synthetic hard points with stationarity, balance, seed source, activity model, stage count, final proof status, and failure class.
- [ ] **Step 2: Run focused tests and verify failure.** Run the API/checker tests that assert the new diagnostics fields.
- [ ] **Step 3: Add retained diagnostics output.** Emit CSV/JSON robustness summaries without creating duplicate plot deliverables.
- [ ] **Step 4: Update checker.** Require the retained diagnostics before standalone CE completeness can pass.
- [ ] **Step 5: Run proof and verify pass.** Re-run focused tests and the standalone CE checker.

### Task 2: Final Proof Corrector For Reaction Stationarity

**Use Cases:**
- A hard point that reaches feasibility but misses reaction stationarity enters a final proof-correction step instead of being accepted or reported vaguely.
- Accepted results prove unscaled physical stationarity and balance below strict tolerances.
- The old one-shot final proof path is replaced by a correction loop that still rejects if strict final proof is missing.

**Files:**
- Modify: CE native NLP/objective files under `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`

- [ ] **Step 1: Add a failing stationarity-corrector regression.** Capture a case that is feasible but above the strict stationarity gate after ordinary final proof.
- [ ] **Step 2: Run the focused regression and verify failure.**
- [ ] **Step 3: Implement proof correction.** Add CE-owned correction that reuses the final true objective and never accepts intermediate homotopy states.
- [ ] **Step 4: Report correction diagnostics.** Include correction attempts, final stationarity, final balance, and rejection reason.
- [ ] **Step 5: Run focused proof and verify pass.**

### Task 3: EOS Nonideality Continuation

**Use Cases:**
- A nonideal CE solve can start from ideal mole-fraction activity and continue to EOS-derived `x * gamma` activity.
- The final accepted row proves the EOS-derived objective and CppAD-backed derivative evidence, not the ideal staging objective.
- The old direct-jump nonideal path is replaced by a staged activity path when direct proof is too brittle.

**Files:**
- Modify: CE objective provider and native bindings.
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py`

- [ ] **Step 1: Add failing nonideality-continuation tests.** Require activity lambda trace from ideal to EOS-derived activity and final EOS proof.
- [ ] **Step 2: Run focused tests and verify failure.**
- [ ] **Step 3: Add activity-continuation parameterization.** Interpolate the objective contribution while keeping final proof at full EOS activity.
- [ ] **Step 4: Preserve ideal behavior.** Verify ideal CE still reports the existing analytic objective path.
- [ ] **Step 5: Run focused proof and verify pass.**

### Task 4: Caller Seed Escalation Policy

**Use Cases:**
- A caller-provided seed is used as a hint but must still pass independent final proof.
- A bad caller seed escalates to CE-owned initialization and records that escalation in diagnostics.
- The old caller-seed truth path is replaced by proof-driven seed provenance.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`

- [ ] **Step 1: Add failing seed-policy tests.** Cover good seed, bad positive seed, nonpositive seed rejection, and escalation to max-min or extent/nullspace initialization.
- [ ] **Step 2: Run API tests and verify failure.**
- [ ] **Step 3: Implement seed policy.** Keep explicit seed validation loud and record provenance for every solve.
- [ ] **Step 4: Update diagnostics schema.** Report seed attempt order, accepted seed source, and whether caller seed proof was rejected.
- [ ] **Step 5: Run focused proof and verify pass.**

### Task 5: Reaction Scaling And Proof Metrics

**Use Cases:**
- Ill-conditioned reaction sets are scaled for solver conditioning while final proof still reports unscaled stationarity.
- Diagnostics expose reaction scaling factors and condition estimates for acceptance evidence.
- The old tolerance-pressure path is replaced by better conditioning without relaxing strict gates.

**Files:**
- Modify: CE native conservation/reaction basis code.
- Modify: CE native diagnostics tests.
- Modify: standalone CE checker if it owns proof metric thresholds.

- [ ] **Step 1: Add failing scaling tests.** Cover badly scaled `ln_K`, tiny species, and near-dependent reaction rows.
- [ ] **Step 2: Run focused tests and verify failure.**
- [ ] **Step 3: Implement reaction scaling.** Scale solver equations and map diagnostics back to physical norms.
- [ ] **Step 4: Add proof metric diagnostics.** Report scaled and unscaled stationarity, balance, and scaling factors.
- [ ] **Step 5: Run focused proof and verify pass.**

### Task 6: Extent/Nullspace Feasible Initialization

**Use Cases:**
- CE can construct an independent feasible start from reaction extents or a conservation nullspace when max-min alone is weak.
- Conservation closure and positivity are proven before the proof solve starts.
- The old single-initializer path is replaced by a ranked initializer ladder with diagnostics.

**Files:**
- Modify or create CE feasible-initialization native helpers.
- Modify CE native bindings.
- Modify CE feasible-initialization tests.

- [ ] **Step 1: Add failing nullspace-initializer tests.** Cover full-rank, rank-deficient, charged, and tiny-feasible systems.
- [ ] **Step 2: Run focused tests and verify failure.**
- [ ] **Step 3: Implement extent/nullspace initializer.** Use linear algebra to build positive feasible candidates and reject ambiguous rank cases loudly.
- [ ] **Step 4: Integrate initializer ladder.** Try caller seed proof, max-min, extent/nullspace, homotopy as dictated by diagnostics.
- [ ] **Step 5: Run focused proof and verify pass.**

### Task 7: Sharp CE Failure Classification

**Use Cases:**
- A failed CE solve reports the exact failing gate instead of a generic convergence status.
- The checker and loop controller can route future repair issues from failure class evidence.
- The old ambiguous failure text is replaced by a stable diagnostic taxonomy and tests.

**Files:**
- Modify: CE result diagnostics in Python and native payload adapters.
- Modify: `scripts/validation/check_standalone_ce_gate.py`
- Modify: CE API and native diagnostics tests.

- [ ] **Step 1: Add failing failure-taxonomy tests.** Assert classes for infeasible conservation, initialization failure, Ipopt failure, proof-correction failure, stationarity failure, balance failure, EOS activity failure, and unsupported standard-state request.
- [ ] **Step 2: Run focused tests and verify failure.**
- [ ] **Step 3: Implement classification.** Map native and Python failures to stable classes without hiding original Ipopt/proof diagnostics.
- [ ] **Step 4: Update checker and docs.** Require classified failures in retained robustness output.
- [ ] **Step 5: Run focused proof and verify pass.**

## Proof Oracle

Primary proof commands:

```powershell
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-06-30-m4-ce-convergence-robustness-hardening-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --build-only --parallel 10
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py -q
uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Issue Creation Packet

Create seven AFK task issues in `M4 - Equilibrium`, all owned by `packages/epcsaft-equilibrium`, with labels `agent-ready`, `status:ready`, `type:task`, `area:equilibrium`, `equilibrium`, `solver`, `native`, `backend:ipopt`, and `validation`. Add `backend:cppad` to EOS nonideality work. No issue should claim CPE, reactive LLE, reactive electrolyte LLE, or phase-equilibrium admission.

## Risk Notes

- The work must not turn a harder solver into weaker proof. Keep proof norms strict and physically interpretable.
- EOS nonideality continuation may expose missing derivative plumbing; split a provider-contract issue only if the missing owner is outside M4 equilibrium.
- Retained diagnostics may be enough for this tranche; avoid producing duplicate plots unless a later issue specifically owns a figure.
