# M4 CE Generic Pope Homotopy Continuation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a generic native continuation substrate and use it to make `reactive_speciation` solve CE from independent constraints, with adaptive Pope-style homotopy and ePC-SAFT EOS-derived activity support.

**Architecture:** Activation admits the `reactive_speciation` family, `NlpProblem` remains the thin Ipopt contract, and a generic continuation driver orchestrates accepted stage solves above it. CE is the first adopter: max-min feasible seed, direct true-Gibbs proof, K-scaling homotopy when needed, and a final proof solve. Nonideal CE uses existing ePC-SAFT EOS/fugacity methods and CppAD derivative infrastructure through an objective-provider boundary without opening phase-equilibrium routes.

**Tech Stack:** Python 3.12, pybind11, C++17 native equilibrium core, Ipopt, CppAD-backed ePC-SAFT EOS derivative kernels, pytest, retained Matplotlib validation artifacts.

---

Source spec: `docs/superpowers/specs/2026-06-29-m4-ce-generic-pope-homotopy-continuation.md`
Prior CE plan to revise where needed: `docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md`
Milestone: `M4 - Equilibrium`
Package owner: `packages/epcsaft-equilibrium`
IntelliJ receipt: IntelliJ MCP was available (`ide_index_status`, `ide_find_definition`, `ide_diagnostics`), indexing was ready, but Python semantic lookup and diagnostics were polluted by missing SDK/dependency indexing. Native and Python anchors below were verified with targeted repo reads.

## Outcome Proof

**Intent:** Replace oracle-seeded standalone CE proof with a robust CE/speciation solver that can start from constraints and use adaptive Pope-style continuation inside the admitted `reactive_speciation` activation family.
**Current Behavior:** `reactive_speciation` requires caller-provided positive `initial_amounts`; MEA proof plots are oracle-seeded; feed-derived no-oracle MEA attempts currently show zero accepted points in the retained audit.
**Expected Outcome:** `reactive_speciation(initial_amounts=None, ...)` computes an independent feasible seed, tries the final CE proof solve, runs adaptive K-scaling homotopy when needed, and accepts only final true-Gibbs proof results.
**Target Output:** Native diagnostics, API results, retained MEA plots, and standalone CE checker evidence show accepted unassisted CE solves, clean activation metadata, strict residuals, and no source-oracle seed use.
**Owner:** M4 equilibrium package owner for `packages/epcsaft-equilibrium`.
**Interface:** Public Python `epcsaft_equilibrium.reactive_speciation`, `EquilibriumSolverOptions`, native `_native_chemical_equilibrium_nlp_activation`, activation matrix metadata, retained analysis artifacts, and CE checker output.
**Cutover:** Omitted `initial_amounts` becomes the proof-oriented path; explicit caller seeds remain labeled diagnostic inputs; old oracle-seeded MEA plots lose proof status.
**Replaced Path:** The old requirement that every CE solve receives caller-provided source-oracle-like amounts is displaced by max-min initialization plus adaptive continuation. The old anti-Pope rule is narrowed to forbid public bypass routes, not internal continuation infrastructure.
**Evidence:** Focused native tests for the continuation driver and max-min initializer, CE API tests, Pope tiny-species oracle tests, ePC-SAFT EOS-derived activity tests, MEA retained pointwise and CE-owned continuation plots, seed audit CSVs, and checker output.
**Acceptance Proof:** All retained MEA 20 C and 40 C loading points are accepted with `uses_source_oracle_initial_amounts=false`, max mole-fraction error <= `1e-8`, balance norm <= `1e-8`, affinity/stationarity norm <= `1e-6`, and final proof solve accepted at `lambda=1`.
**Stop Criteria:** Stop if the implementation opens public Pope/homotopy/max-min routes, hides intermediate homotopy stages as final proof, weakens activation-family cleanliness, uses source-oracle values as proof seeds, or cannot produce ePC-SAFT EOS derivative evidence for the nonideal CE target.
**Avoid:** Do not change bubble/dew, HELD, branch tracing, CPE public admission, or phase-route behavior in this plan.
**Risk:** The ePC-SAFT EOS-derived activity target may expose missing CE/EOS context plumbing; if so, keep the failure loud and split a child issue rather than weakening proof gates.

## Implementation Boundaries

**Files To Create:** `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/continuation_driver.h`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/continuation_driver.cpp`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/feasible_initialization.h`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/feasible_initialization.cpp`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_objective.h`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_objective.cpp`, focused native tests under `packages/epcsaft-equilibrium/tests/native/diagnostics/`, and retained MEA no-oracle artifact outputs under the existing MEA analysis folder.
**Files To Modify:** `packages/epcsaft-equilibrium/CMakeLists.txt`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.h`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`, `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`, CE tests, standalone CE checker tests, and MEA retained analysis scripts.
**Files To Avoid:** Bubble/dew route code, HELD route code, CPE route admission, downstream application studies, and unrelated provider package APIs outside the minimum ePC-SAFT EOS derivative entry points already used by equilibrium.
**Source Of Truth:** The approved source spec, current activation matrix, current `NlpProblem` contract, current Ipopt adapter proof policy, and current ePC-SAFT EOS CppAD derivative kernels.
**Read Path:** Read activation matrix, CE schema, CE NLP, Ipopt adapter, EOS phase block derivatives, standard-state tests, MEA retained analysis, and standalone CE checker before editing each task.
**Write Path:** Add failing tests first, make the narrow native/Python changes, update retained analysis outputs, then update docs/checker/capability evidence.
**Integration Points:** `solve_ipopt_nlp`, `IpoptSolveOptions`, continuation-state binding helpers, `chemical_equilibrium_schema_payload`, `StandardStateRecord.activity_convention`, `eos_phase_block`/phase derivative helpers, and `reactive_speciation` result diagnostics.
**Migration Or Cutover:** Keep the public route name and activation family stable. Migrate proof tests and MEA validation away from source-oracle initial amounts. Keep explicit seeds available but labeled diagnostic.
**Replaced Path Handling:** Revise tests/docs that currently ban Pope-style continuation absolutely so they instead reject public bypass routes and accept internal activation-family continuation evidence.
**Acceptance Proof Gate:** The plan is complete only when focused native/API tests, standalone CE checker, retained MEA data generation, retained plot rendering, and cleanup pass with strict metrics.

## Test Complete And Metrics

Test complete means all of the following are true:

- Native max-min, continuation-driver, K-scaling homotopy, and ePC-SAFT EOS-derived activity tests pass.
- `reactive_speciation(initial_amounts=None, ...)` passes ideal A/B, Pope tiny-species, and MEA tests.
- MEA pointwise independent and CE-owned continuation sweeps both run over 161 loading points at 20 C and 40 C.
- Every MEA proof row reports `uses_source_oracle_initial_amounts=false`.
- MEA max mole-fraction error is <= `1e-8`, balance norm <= `1e-8`, and affinity/stationarity norm <= `1e-6`.
- Final accepted CE rows are from the true final proof solve, not an intermediate homotopy stage.
- ePC-SAFT EOS-derived activity CE reports CppAD derivative backend evidence for the nonideal objective path.
- Activation matrix public routes remain unchanged except for clean solver-strategy metadata.
- Repo cleanup hook runs before handoff.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Source artifact | User-approved spec, 2026-06-29 | Plan from `docs/superpowers/specs/2026-06-29-m4-ce-generic-pope-homotopy-continuation.md`. | Keeps implementation tied to approved brainstorm scope. | No | M4 owner |
| Plan route | Native workflow answer, 2026-06-29 | Create one implementation plan. | Produces one coordinated CE continuation plan before issue or implementation routing. | No | M4 owner |
| Generic substrate | User decision, 2026-06-29 | Prefer generic continuation infrastructure with CE as first adopter. | Creates reusable driver interfaces while avoiding phase-route migration now. | No | M4 owner |
| Activation cleanliness | User decision, 2026-06-29 | Activation matrix and family must stay clean for CE and future phase equilibrium. | Homotopy is strategy evidence, not public route vocabulary. | No | M4 owner |
| `NlpProblem` boundary | User decision, 2026-06-29 | Keep `NlpProblem` as the Ipopt problem contract only. | Continuation orchestration belongs above individual NLP problems. | No | M4 owner |
| Homotopy form | Native planning grill, 2026-06-29 | Use K-scaling: scale reaction `ln_K` from zero to true values. | First homotopy path is deterministic and reuses current ideal CE objective machinery. | No | M4 owner |
| Solve policy | Native planning grill, 2026-06-29 | Adaptive: max-min seed, direct final proof, homotopy when needed or requested. | Easy points avoid unnecessary staged solves while difficult points gain Pope-style support. | No | M4 owner |
| Nonideal target | User planning answer, 2026-06-29 | Include ePC-SAFT EOS-derived activity/fugacity CE in this first implementation. | Plan must wire an EOS objective provider and CppAD evidence, not only ideal CE. | No | M4 owner |
| EOS context | User planning answer, 2026-06-29 | Reuse existing ePC-SAFT EOS methods and context instead of a toy gamma model. | Nonideal CE must use existing mixture/state/native argument plumbing. | No | M4 owner |
| MEA metrics | Native planning grill, 2026-06-29 | Strict gates: mole error <= `1e-8`, balance <= `1e-8`, stationarity <= `1e-6`. | MEA plots become numerical proof, not qualitative overlays. | No | M4 owner |
| TDD policy | Native planning grill, 2026-06-29 | Strict TDD. | Each task starts with failing tests and commits after green validation. | No | M4 owner |
| Phase-route adoption | Source spec and user answer | Plan later after CE proof. | Bubble/dew, HELD, branch tracing, and CPE stay outside this implementation. | Yes | M4 owner |

## Task Plan

### Task 1: Activation And Public Contract Tests

**Use Cases:**
- A user calls `reactive_speciation` and sees the same public route and activation family after continuation support lands.
- A checker proves continuation support is internal solver strategy evidence, not a public bypass route.
- A worker revises the old anti-Pope guardrail without opening reactive phase routes.
- Acceptance evidence covers the replaced path from absolute Pope ban to clean internal continuation.

**Files:**
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`

- [ ] **Step 1: Add failing activation tests.** Update tests so `reactive_speciation` still has exactly one public route, but its activation row may report solver strategy metadata for continuation-capable Ipopt CE.
- [ ] **Step 2: Run focused tests and verify failure.** Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`. Expected: failures mention missing continuation strategy metadata or old absolute Pope ban.
- [ ] **Step 3: Update activation metadata.** Add clean solver-strategy fields in `activation_matrix.h` and capability reporting without adding public routes.
- [ ] **Step 4: Run focused tests and verify pass.** Re-run the command from Step 2. Expected: pass.
- [ ] **Step 5: Commit.** Commit with `git commit -m "Clarify CE continuation activation strategy"`.

### Task 2: Generic Continuation Driver

**Use Cases:**
- A native route can execute an ordered plan of Ipopt `NlpProblem` stages.
- Accepted primal and dual state from one stage seeds the next stage.
- A final proof stage can reject the whole trace even after intermediate stages pass.
- Diagnostics show stage status, parameter value, Ipopt status, and KKT metrics for acceptance evidence.

**Files:**
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/continuation_driver.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/continuation_driver.cpp`
- Modify: `packages/epcsaft-equilibrium/CMakeLists.txt`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Create: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_continuation_driver.py`

- [ ] **Step 1: Write failing native smoke tests.** Add tests for a tiny quadratic parameter path exposed by a native smoke binding. Assert trace length, accepted state transfer, final proof status, and incompatible continuation-state rejection.
- [ ] **Step 2: Run tests and verify failure.** Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_continuation_driver.py -q`. Expected: native binding or trace fields are missing.
- [ ] **Step 3: Add driver types.** Implement stage spec, stage result, trace result, and `run_continuation_plan(...)` around `solve_ipopt_nlp`.
- [ ] **Step 4: Add native smoke binding.** Bind a synthetic continuation smoke function only for tests; keep it outside CE public routes.
- [ ] **Step 5: Register new C++ sources.** Add `continuation_driver.cpp` to `packages/epcsaft-equilibrium/CMakeLists.txt`.
- [ ] **Step 6: Run tests and verify pass.** Re-run Step 2. Expected: pass with retained trace fields.
- [ ] **Step 7: Commit.** Commit with `git commit -m "Add generic native continuation driver"`.

### Task 3: Max-Min Feasible Interior Initializer

**Use Cases:**
- CE can derive a strictly positive feasible amount vector from conservation constraints without source-oracle species amounts.
- Infeasible or rank-broken constraints stop before the CE proof solve.
- Initializer diagnostics provide acceptance evidence for min amount, conservation closure, active constraints, and Ipopt status.
- The old feed-stoichiometric seed path is displaced by a constraint-owned initializer.

**Files:**
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/feasible_initialization.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/feasible_initialization.cpp`
- Modify: `packages/epcsaft-equilibrium/CMakeLists.txt`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Create: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_feasible_initialization.py`

- [ ] **Step 1: Write failing initializer tests.** Cover total conservation, charged conservation, tiny feasible species, infeasible totals, and duplicate conservation rows.
- [ ] **Step 2: Run tests and verify failure.** Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_feasible_initialization.py -q`. Expected: initializer binding or diagnostics are missing.
- [ ] **Step 3: Implement initializer `NlpProblem`.** Use amounts plus margin variable, conservation equality constraints, positivity inequalities, exact linear Jacobian, zero Hessian contribution for linear constraints, and objective `-margin`.
- [ ] **Step 4: Add binding diagnostics.** Return accepted flag, margin, minimum amount, balance norm, Ipopt diagnostics, and initial amount vector.
- [ ] **Step 5: Register source and run tests.** Add `feasible_initialization.cpp` to CMake and re-run Step 2. Expected: pass.
- [ ] **Step 6: Commit.** Commit with `git commit -m "Add max-min CE feasible initializer"`.

### Task 4: CE Objective Provider And K-Scaling Homotopy

**Use Cases:**
- Ideal CE can scale reaction constants from `ln_K=0` to true values without changing the final proof objective.
- Direct proof from max-min seed is tried before homotopy stages.
- Homotopy stages are retained as initialization trace, and only the final true-Gibbs solve can accept a public result.
- Pope tiny-species and A/B closed-form cases pass without caller seeds.

**Files:**
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_objective.h`
- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_objective.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp`
- Modify: `packages/epcsaft-equilibrium/CMakeLists.txt`
- Create: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py`
- Modify: `tests/native/contracts/test_chemical_equilibrium_reference_oracles.py`

- [ ] **Step 1: Write failing K-scaling tests.** Add tests that solve A/B and Pope tiny-species cases with no caller seed and assert final `lambda=1`, accepted final proof, and trace policy.
- [ ] **Step 2: Run tests and verify failure.** Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py tests/native/contracts/test_chemical_equilibrium_reference_oracles.py -q`. Expected: no homotopy trace or no optional seed path.
- [ ] **Step 3: Add objective provider.** Move standard potential construction and ideal Gibbs evaluation behind a CE objective provider that can apply `log_equilibrium_constants_lambda = lambda * log_equilibrium_constants`.
- [ ] **Step 4: Integrate driver into CE solve.** Build max-min seed, direct final proof stage, adaptive K-scaling stage plan when needed, and final proof acceptance.
- [ ] **Step 5: Return trace diagnostics.** Add final proof status, stage count, lambda values, seed source, and source-oracle flag to native payload.
- [ ] **Step 6: Register source and run tests.** Add `chemical_equilibrium_objective.cpp` to CMake and re-run Step 2. Expected: pass.
- [ ] **Step 7: Commit.** Commit with `git commit -m "Add adaptive CE K-scaling homotopy"`.

### Task 5: Public Python Optional Initialization

**Use Cases:**
- A public user can call `reactive_speciation(..., initial_amounts=None)` and get a CE-only result.
- A diagnostic user can still provide explicit initial amounts and see seed provenance in diagnostics.
- Bad seeds or nonpositive amounts raise before native solving.
- Result schema exposes initialization trace without broadening CE into CPE.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`

- [ ] **Step 1: Write failing API tests.** Add tests for omitted initial amounts, explicit seed diagnostics, invalid explicit seed rejection, trace fields, and unchanged public route.
- [ ] **Step 2: Run tests and verify failure.** Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`. Expected: `initial_amounts` is still required or trace fields are missing.
- [ ] **Step 3: Update Python signatures.** Make `initial_amounts` optional and pass either no seed or explicit seed provenance through `solve_chemical_equilibrium_nlp_activation`.
- [ ] **Step 4: Update result diagnostics.** Preserve `ReactiveSpeciationResult` schema and add initialization diagnostics through the existing diagnostics view.
- [ ] **Step 5: Run tests and verify pass.** Re-run Step 2. Expected: pass.
- [ ] **Step 6: Commit.** Commit with `git commit -m "Make CE initialization independent by default"`.

### Task 6: ePC-SAFT EOS-Derived Activity CE

**Use Cases:**
- CE can use ePC-SAFT EOS-derived activity/fugacity terms instead of mole-fraction-only activity when the standard state requests `eos_x_phi`.
- The implementation reuses existing ePC-SAFT EOS methods and CppAD derivative infrastructure.
- Nonideal CE proof remains single-phase speciation and does not admit CPE or phase splitting.
- Derivative evidence proves the nonideal objective path is CppAD-backed.

**Files:**
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_objective.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_objective.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/chemical_equilibrium_nlp.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Create: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py`

- [ ] **Step 1: Write failing standard-state/API tests.** Allow `eos_x_phi` records only when ePC-SAFT EOS context is present and reject mixed CE contexts that lack the required EOS data.
- [ ] **Step 2: Write failing native nonideal tests.** Add a small neutral ePC-SAFT EOS-derived CE proof case with artificial reaction constants and assert CppAD derivative backend evidence.
- [ ] **Step 3: Run tests and verify failure.** Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py -q`. Expected: `eos_x_phi` CE objective support is missing.
- [ ] **Step 4: Reuse EOS context plumbing.** Thread the existing ePC-SAFT mixture/native argument context, temperature, pressure, and EOS phase reference into CE only when `eos_x_phi` standard states are present.
- [ ] **Step 5: Add EOS activity objective provider.** Use existing EOS phase/fugacity CppAD methods to evaluate composition-dependent reduced activity terms and exact derivative evidence for the CE objective.
- [ ] **Step 6: Preserve ideal CE path.** Keep `mole_fraction_activity` tests green and ensure ideal CE still reports analytic Hessian backend.
- [ ] **Step 7: Run tests and verify pass.** Re-run Step 3 plus `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py -q`. Expected: pass.
- [ ] **Step 8: Commit.** Commit with `git commit -m "Add EOS-derived activity objective for CE"`.

### Task 7: MEA No-Oracle Retained Validation

**Use Cases:**
- MEA H2O CO2 speciation plots prove CE workflows produce curves from independent initialization.
- Pointwise independent solves and CE-owned continuation solves are both retained.
- Shuffled-order spot checks prove the result is not dependent on source-oracle ordering.
- Old oracle-seeded plots are labeled diagnostic if retained.

**Files:**
- Modify: `analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/generate_data.py`
- Modify: `analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/render_figure.py`
- Modify: `analyses/paper_validation/standalone_ce/analysis.yaml`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
- Create or update retained result CSV/JSON/SVG/PNG/PDF bundles under `analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/results/`

- [ ] **Step 1: Write failing MEA API test.** Change the focused MEA pytest to call `reactive_speciation(initial_amounts=None, ...)` for representative loadings and assert strict metrics.
- [ ] **Step 2: Run test and verify failure.** Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py::test_reactive_speciation_solves_mea_co2_h2o_loading_sweep_against_retained_fixture -q`. Expected: current no-oracle path fails.
- [ ] **Step 3: Update data generation.** Generate pointwise independent, CE-owned continuation, shuffled subset, seed audit, error summary, and trace summary tables.
- [ ] **Step 4: Update plot rendering.** Render unassisted CE vs Smith-Missen oracle, CE-owned continuation vs oracle, max error, and stage-count diagnostics.
- [ ] **Step 5: Run retained generation.** Run `uv run --no-sync python analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/generate_data.py`.
- [ ] **Step 6: Render retained plots.** Run `uv run --no-sync python analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/render_figure.py`.
- [ ] **Step 7: Verify strict metrics.** Confirm retained summary reports all accepted, seed flag false, max mole error <= `1e-8`, balance <= `1e-8`, and stationarity <= `1e-6`.
- [ ] **Step 8: Commit.** Commit with `git commit -m "Add unassisted MEA CE validation plots"`.

### Task 8: Checker, Docs, And Capability Evidence

**Use Cases:**
- Standalone CE checker proves the new workflow evidence is complete.
- Capability text no longer implies oracle-seeded MEA plots prove unassisted CE.
- Old plan/issue text that banned Pope-style continuation is revised to ban only public bypass routes.
- Acceptance evidence and replaced-path handling are visible before issue close.

**Files:**
- Modify: `scripts/validation/check_standalone_ce_gate.py`
- Modify: `tests/native/contracts/test_standalone_ce_gate.py`
- Modify: `analyses/paper_validation/standalone_ce/shared/results/summary.json`
- Modify: `docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md`
- Modify: `docs/superpowers/issues/2026-06-26-m4-equilibrium-issue-0326-m4-ce-add-single-ce-nlp-activation-path.md`
- Modify: `docs/superpowers/issues/2026-06-26-m4-equilibrium-issue-0329-m4-ce-build-standalone-validation-ladder.md`

- [ ] **Step 1: Write failing checker tests.** Require continuation trace evidence, max-min seed evidence, no-oracle MEA proof, and clean activation metadata.
- [ ] **Step 2: Run checker tests and verify failure.** Run `uv run --no-sync python run_pytest.py tests/native/contracts/test_standalone_ce_gate.py -q`. Expected: checker lacks new evidence requirements.
- [ ] **Step 3: Update checker.** Add required fields for independent initialization, homotopy trace, EOS activity evidence, MEA strict metrics, and seed policy.
- [ ] **Step 4: Update docs and issue mirrors.** Revise old anti-Pope text to the new clean activation-family rule and link the new spec/plan.
- [ ] **Step 5: Run checker.** Run `uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete`.
- [ ] **Step 6: Run tests and verify pass.** Re-run Step 2. Expected: pass.
- [ ] **Step 7: Commit.** Commit with `git commit -m "Update CE gate for continuation evidence"`.

### Task 9: Final Integration And Verification

**Use Cases:**
- A maintainer can review one branch with source spec, implementation evidence, retained plots, and strict validation receipts.
- The worktree has no leftover generated clutter outside retained artifacts.
- Final handoff renders all new/updated plots inline and reports the retained data behind them.
- Cleanup and status evidence prove the branch is ready for the next Superpowers route.

**Files:**
- Modify only files touched by Tasks 1-8.
- Test: focused native/API/checker/analysis commands listed below.

- [ ] **Step 1: Run focused test set.** Run `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_continuation_driver.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_feasible_initialization.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_chemical_equilibrium_reference_oracles.py tests/native/contracts/test_standalone_ce_gate.py -q`.
- [ ] **Step 2: Run CE checker.** Run `uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete`.
- [ ] **Step 3: Regenerate MEA data and plots.** Run the generation and render commands from Task 7.
- [ ] **Step 4: Inspect retained metric tables.** Confirm the strict MEA metrics and seed-policy audit before handoff.
- [ ] **Step 5: Run cleanup.** Run `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`.
- [ ] **Step 6: Review git status.** Run `git status --short` and confirm only intended retained artifacts and code/docs changes remain before the next workflow route.
- [ ] **Step 7: Commit final integration if needed.** Commit with `git commit -m "Validate CE continuation workflow"` after staging only intended files.

## Proof Oracle

Primary proof commands:

```powershell
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_continuation_driver.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_feasible_initialization.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_chemical_equilibrium_reference_oracles.py tests/native/contracts/test_standalone_ce_gate.py -q
uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete
uv run --no-sync python analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/generate_data.py
uv run --no-sync python analyses/paper_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/render_figure.py
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Required retained artifacts:

- MEA unassisted pointwise CSV and plots.
- MEA CE-owned continuation CSV and plots.
- MEA strict error summary CSV.
- MEA initialization and seed-policy audit CSV.
- Continuation trace summary JSON/CSV.
- Standalone CE checker JSON summary.

## Risk Notes

- ePC-SAFT EOS-derived CE may require careful standard-state convention handling. The plan treats this as part of Task 6 and requires CppAD derivative evidence before claiming support.
- K-scaling homotopy is an initialization strategy. Final acceptance always comes from true final proof.
- Retained MEA plots compare against Smith-Missen source oracles, but proof seeding must remain independent.
- Phase-equilibrium migration remains a later plan after CE proof is retained.
