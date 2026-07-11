# M4 Standalone CE Diagnostic, Repair, And Admission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to execute this plan task-by-task. Use
> `superpowers:test-driven-development` for every behavior change,
> `superpowers:systematic-debugging` before selecting a defect owner, and
> `superpowers:verification-before-completion` before each checkpoint.

**Goal:** Complete the M4 component receipt/checker contract independently,
then consume source-qualified M6 evidence in a separate M4 classification or
defect leaf before issue #330 can admit `reactive_speciation`.

**Architecture:** M4 owns the typed chemical-system boundary, one native
`NlpProblem`/Ipopt path, primitive numerical receipt, independent physical/KKT
checker, source-qualified classification, canonical result, and selector
admission. M6 owns the nonideal MEA source ledger, executable model-input
bundle, evidence-completeness checker, literature/model tables, and retained
plots. Preserve the live #329 `blocked_by` #328 edge: Task 4 executes first to
complete the typed constructor-request prerequisite. Component fixtures then
complete issue #329 without waiting on M6; the M6
leaf is then blocked by that component contract, a later M4 classification
leaf is blocked by M6, and #330 is blocked by the classification leaf.

**Tech Stack:** Python 3.13 local development baseline, C++17, pybind11,
CppAD-backed exact derivatives, Ipopt, NumPy, pytest, `uv`, Ruff, JSON/CSV,
Sphinx, and GitHub native sub-issues/dependencies.

## Global Constraints

- Milestone ownership is `M4 - Equilibrium`; provider typed-input work remains
  M3 and nonideal MEA evidence remains M6.
- Preserve one CE activation-plan, `NlpProblem`, Ipopt, result, and acceptance
  path. Do not add a direct solver, alternate algorithm selector, checker-only
  execution path, or compatibility wrapper.
- Keep `reactive_speciation`, reactive LLE, reactive electrolyte LLE, CPE,
  neutral LLE, electrolyte LLE, TP flash, and multiphase closed unless their
  own admission issue passes.
- Do not invent model parameters, reaction constants, standard states,
  structural zeros, source identities, or validity domains.
- Do not change a thermodynamic equation, derivative, scaling rule, or Ipopt
  profile until a reproducible receipt identifies that owner.
- Final acceptance requires `lambda == 1`, `balance_inf_norm <= 1.0e-8`,
  `reaction_stationarity_inf_norm <= 1.0e-6`, exact-derivative evidence,
  acceptable native status, and independent agreement.
- Source-oracle or imported-model seeds may initialize a diagnostic attempt;
  they never replace final unassisted physical/KKT proof.
- No individual Gross, Khudaida, or other paper-validation repair belongs to
  this plan.
- Every implementation checkpoint runs focused tests, `git diff --check`, and
  `bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .`.

---

## Source Evidence

- Approved source spec:
  `docs/superpowers/specs/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission.md`.
- Historical foundation:
  `docs/superpowers/specs/2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md`.
- Parent/tracker issues: #321 (foundation), #328 (typed public request and
  result schema), #329 (validation ladder), and #330 (sole admission gate).
- Closed issues #382, #384-#389, and #396-#402 already supply convergence
  diagnostics, proof correction, EOS activity continuation, seed escalation,
  scaling metrics, feasible initialization, failure taxonomy, artifact digest,
  and robustness matrix evidence. Task 1 inventories those fields before any
  new field is added.
- Canonical checker:
  `scripts/validation/check_standalone_ce_gate.py`.
- Verified retained failure on 2026-07-10: loading `0.4` at `40 degC`,
  `balance_inf_norm = 2.5999999998789356`,
  `reaction_stationarity_inf_norm = 73.79118023038392`, classification
  `balance_failure`, not accepted.
- M6 input source:
  `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/`.
  Its executable JSON files are intentionally absent while the source ledger is
  blocked.

## Native Tracker Dependency DAG

The issue graph is directional and milestone-owned:

```text
#328 M4 typed constructor request
  -> #329 M4 receipt schema/primitives/component checker
     -> M6 source/input/evidence leaf
  -> M4 source-qualified classification or owner-specific defect leaf
  -> #330 M4 admission
```

Preserve the live #329 `blocked_by` #328 edge. The M6 leaf is `blocked_by`
#329. The later M4 classification leaf is
`blocked_by` the M6 leaf. Issue #330 is `blocked_by` that classification leaf
and independently by the typed request work in #328. Do not add an M6
`blocked_by` edge to #329: #329 is complete when the generic component receipt
and independent checker pass, even while the nonideal source bundle remains
unavailable.

During tracker publication, remove `status:ready` from #329, apply
`status:blocked` while #328 remains open, and synchronize the #329 local mirror
plus M4 milestone row. Readiness may return only through the repository
dependency reconciler after every native blocker closes.

## Test Complete And Metrics

Test complete for this program means:

- every required receipt family has labels, dimensions, finite primitive
  values, stable hashes, and an explicit evidence class;
- each continuation trial retains its parameter value, initial state, final
  state, multipliers, native status, acceptance, and handoff source;
- an independent component checker reconstructs conservation, charge,
  reaction affinities, bound complementarity, and unscaled Lagrangian
  stationarity from retained primitives without calling the CE production
  solver;
- CppAD/analytic derivative rows match bounded symmetric two-sided reference evaluations at
  interior component-fixture states within the tolerance recorded by the test;
- after #328 closes, issue #329 closes from the component receipt/checker proof
  alone and has no dependency on the M6 source leaf;
- after the M6 evidence-completeness checker passes, a separate M4
  classification record has exactly one outcome from `admission_candidate`,
  `source_qualified_rejection`, `diagnostic_contract_defect`,
  `canonical_formulation_defect`, or `not_reproduced`;
- a `canonical_formulation_defect` outcome names one production owner and one
  reproducing test before a Bug is created;
- the M6 evidence receipt is structurally complete before the source-qualified
  M4 classification runs; a scientifically rejected solve may complete M6 but
  cannot satisfy #330;
- #330 changes only the `reactive_speciation` selector route and keeps all
  coupled phase families closed;
- focused M4 API, receipt, derivative, activation, checker, docs, Ruff, diff,
  and cleanup checks pass freshly.

## Outcome Proof

**Intent:** Distinguish bad or incomplete scientific input from a CE
implementation defect, then admit standalone speciation only when the same
source-qualified native solve passes independent numerical proof.

**Current Behavior:** The native CE path has extensive diagnostics, but the
retained live MEA case uses an ideal component fixture with hard-coded
constants, fails strict balance/stationarity, and lacks a complete typed
nonideal model-input receipt. The activation row is correctly
`declared_not_exposed`.

**Expected Outcome:** A versioned component receipt preserves sufficient
primitives to recompute every physical and KKT gate and completes #329 without
M6. M6 then supplies a source-qualified evidence receipt to a separate M4
classification/defect leaf; only an evidence-selected defect is repaired, and
#330 either admits one constructor-configured `reactive_speciation` workflow
or remains blocked with an exact reason.

**Target Output:** `StandaloneCEReceipt` schema and builder, native primitive
payload, independent receipt checker, root-cause decision record, typed
`ChemicalSystem` request, focused contract tests, and a selector/capability
change owned only by #330 after all gates pass.

**Owner:** M4 owns `packages/epcsaft-equilibrium/**`, #329's component CE
receipt checker, the later source-qualified classification/repair leaf, and
admission; M6 supplies the evidence-complete nonideal source-model receipt;
M3 supplies the resolved model-input contract.

**Interface:** `ChemicalSystem`, `Equilibrium(mixture,
route="reactive_speciation", chemical_system=...)`,
`build_standalone_ce_receipt(...)`, the native
`_native_chemical_equilibrium_nlp_activation` payload,
`check_standalone_ce_receipt.py`, and `check_standalone_ce_gate.py`.

**Cutover:** The existing internal validation function remains the only CE
execution path until #330. Receipt construction becomes mandatory around that
path; after admission, constructor-configured `Equilibrium.solve()` dispatches
to the same native owner and the internal-only entrypoint is removed in the
same #330 slice.

**Replaced Path:** Norm-only summaries, stale source-seeded artifacts,
checker-reconstructed pseudo-results, hard-coded loose MEA inputs, and any
direct/public CE helper are displaced; none remains as an alternate route.

**Evidence:** Focused mutation tests, fresh equilibrium-native build identity,
retained input and runtime fingerprints, primitive receipt hashes, independent
component recalculation, derivative perturbation receipts, the M6
evidence-completeness receipt, the later M4 source-qualified classification,
strict admission-checker JSON, activation generation, capability equality, and
independent thermodynamic/code review.

**Acceptance Proof:** The exact source-qualified solve at the declared MEA
states reaches final full nonideality and `lambda == 1`, satisfies the
`1.0e-8` balance and `1.0e-6` stationarity limits, agrees with the independent
checker, retains its literature/model comparison, and is reachable through
the single selector-backed `Equilibrium` route after #330 changes only that
activation family.

**Stop Criteria:** Stop #329 work on a missing primitive array or failed
component reconstruction. Stop only the later source-qualified leaf on an
incomplete M6 input graph, mismatched input/native fingerprint, unclassified
result, a third unsuccessful repair hypothesis, or any need to broaden a
sibling equilibrium family.

**Avoid:** Do not tune Ipopt first, relax tolerances, accept an intermediate
continuation state, treat a component fixture as MEA validation, or create a
Bug without a receipt-backed formulation reproducer.

**Risk:** The accepted source input may prove that the historical MEA point is
not a valid executable target, or may still reveal a genuine formulation
defect. Either result is useful, but only the latter authorizes a production
repair and neither guarantees admission.

## Implementation Boundaries

**Files To Create:**
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/chemical_equilibrium_receipt.py`,
`packages/epcsaft-equilibrium/tests/contracts/test_standalone_ce_receipt_contract.py`,
`packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`,
`scripts/validation/check_standalone_ce_receipt.py`,
`tests/native/contracts/test_standalone_ce_receipt.py`,
`analyses/package_validation/standalone_ce/shared/results/standalone_ce_component_receipt.json`, and
`analyses/package_validation/standalone_ce/shared/results/standalone_ce_root_cause.json`.

**Files To Modify:** CE schema/workflow/result modules under
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/`, native CE result and
binding owners under
`packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/`,
`packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json`, focused
CE tests, `scripts/validation/check_standalone_ce_gate.py`, activation source
and generated mirror, capability evidence, analysis metadata, and user-facing
equilibrium documentation only when #330 passes.

**Files To Avoid:** Provider implementation files, regression files,
paper-specific parameter bundles, downstream repositories, release metadata,
and any closed sibling route implementation.

**Source Of Truth:** The approved spec, #329 component receipt/checker output,
M6 source ledger and evidence-complete input receipt, typed M3 resolved-input
receipt, native CE `NlpProblem` primitives, Ipopt solve result, the later M4
classification record, activation matrix, and admission-checker output.

**Read Path:** Component fixture -> native CE input -> primitive receipt ->
independent component reconstruction (#329) -> M6 source rows -> M3 resolved
model receipt -> `ChemicalSystem` and `Mixture` -> source-qualified native CE
receipt -> separate M4 classification -> selector/capability gate (#330).

**Write Path:** Add one failing contract, observe the expected failure, make
the smallest owner change, rerun focused checks, record the receipt or root
cause, and commit one reviewable checkpoint.

**Integration Points:** Provider resolved input, CE standard-state registry,
activation plan, variable layout, Ipopt adapter, continuation driver, native
pybind result conversion, public `Equilibrium`, capability evidence, M6
analysis artifacts, and strict validation scripts.

**Migration Or Cutover:** Execute Task 4 first to reconcile and close the typed
constructor request under #328; then introduce receipt support around the
closed internal route and complete #329; perform a
separate evidence-selected repair only if required; then let #330 remove the
internal-only call surface while opening the same selector path.

**Replaced Path Handling:** Delete displaced serializers, duplicate receipt
fields, direct call paths, and stale capability statements in the slice that
removes their final caller. Do not leave redirectors or dual result builders.

**Acceptance Proof Gate:** Preserve #329 `blocked_by` #328. After #328 closes,
issue #329 needs only the component receipt and independent checker proof. No
later repair issue is ready without an
evidence-complete M6 receipt and source-qualified M4 classification record, and
#330 is not ready without an `admission_candidate` classification, strict M4
receipt proof, fresh native identity, focused/default/confidence checks, docs,
Ruff, diff, cleanup, and independent scientific/code review.

## Decision Ledger

| Decision | Evidence | Resolution | Owner |
| --- | --- | --- | --- |
| Reuse diagnostics before adding fields | Closed #382 and #384-#402 already cover major diagnostic families | Inventory keys and add only missing primitives/identity | M4 |
| Separate component and source evidence | Current component fixture is not a nonideal MEA input | `evidence_class` is mandatory and component receipts cannot admit | M4/M6 |
| Keep checker independent | Production summaries can repeat the same defect | Recompute from retained arrays in a separate script | M4 review owner |
| Delay repair selection | Current failure does not identify input, equation, derivative, scaling, or solver ownership | Root-cause record selects the next issue; no speculative source edit | M4 |
| Use one typed chemical system | Issue #328 must reconcile CE with constructor-configured `Equilibrium` | Add `ChemicalSystem`; do not restore a free helper | M4 |
| Keep #330 sole admission | Existing issue hierarchy already assigns activation | All preceding tasks produce blockers/evidence for #330 | M4 |
| Keep coupled phase routes closed | Standalone CE contains no phase split | No reactive LLE, electrolyte LLE, or CPE activation change | M4 |
| Preserve live prerequisite and keep #329 independent of M6 | #329 is currently blocked by #328, while component receipts can prove the generic checker before nonideal input exists | #328 blocks #329; #329 blocks M6; M6 blocks a separate M4 classification leaf; that leaf blocks #330 | M4/M6 |

## Execution Order

Execute **Task 4 first**, then Tasks 1-3, followed by the separate M6 evidence
plan, Task 5, and Task 6. Task 4 keeps its approved behavior grouping number,
but it is an explicit live-tracker prerequisite rather than a later parallel
slice. Before implementation dispatch, tracker publication must also label
#329 `status:blocked` and synchronize its mirror/milestone row with the live
#328 dependency.

### Task 1: Inventory Existing Diagnostics And Establish The Receipt Schema

**Use Cases:**

- A maintainer can see which #382-#402 fields already exist and gets a named
  schema failure only for genuinely missing primitive or identity fields.
- A component-fixture receipt is visibly excluded from admission evidence,
  preserving the replaced-path boundary against old MEA summaries.

**Files:**

- Create: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/chemical_equilibrium_receipt.py`
- Create: `packages/epcsaft-equilibrium/tests/contracts/test_standalone_ce_receipt_contract.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/__init__.py`

**Interfaces:**

- Produces: `STANDALONE_CE_RECEIPT_SCHEMA_VERSION: int = 1`.
- Produces: `required_standalone_ce_receipt_fields() -> tuple[str, ...]`.
- Produces: `validate_standalone_ce_receipt_shape(receipt: Mapping[str,
  object]) -> tuple[str, ...]`.
- Consumes later: Task 2's `build_standalone_ce_receipt(...)` and Task 3's
  independent checker.

- [ ] **Step 1: Write the RED schema tests.** Add tests named
  `test_receipt_schema_reuses_closed_diagnostic_families`,
  `test_receipt_schema_rejects_each_missing_primitive_family`, and
  `test_component_fixture_receipt_cannot_claim_admission_evidence`. Require the
  top-level families `identity`, `evidence_class`, `input`, `state`,
  `variables`, `constraints`, `derivatives`, `solve`, `continuation`, and
  `acceptance`.

- [ ] **Step 2: Verify RED.** Run
  `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_standalone_ce_receipt_contract.py -q`.
  Expected: collection succeeds and fails because the receipt module is absent.

- [ ] **Step 3: Implement the minimal frozen schema validator.** Accept only
  `component_fixture` and `source_model`; require a component `fixture_id` or a
  source-model `model_configuration_fingerprint` plus
  `parameter_set_fingerprint`; reject unknown keys at version 1; return stable
  path-qualified blockers rather than filling missing values.

- [ ] **Step 4: Refactor and verify GREEN.** Keep field declarations in one
  immutable tuple and reuse them in the validator. Re-run the Task 1 command;
  expected: all Task 1 tests pass.

- [ ] **Step 5: Checkpoint commit.** Commit
  `feat(equilibrium): define standalone CE receipt contract`.

### Task 2: Emit Complete Native And Python Receipt Primitives

**Use Cases:**

- Every accepted or rejected CE attempt can be reconstructed from labeled
  solver, physical, derivative, bound, multiplier, tolerance, and continuation
  arrays rather than norm-only summaries.
- The new receipt replaces duplicated diagnostic assembly without changing the
  one native solve or its current acceptance result.

**Files:**

- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activated_equilibrium_nlp.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activated_equilibrium_nlp.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/chemical_equilibrium_receipt.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_standalone_ce_receipt_contract.py`

**Interfaces:**

- Produces native `ChemicalEquilibriumReceiptPrimitives` containing
  `NlpBounds`, `NlpScaling`, objective gradient, sparse Jacobian
  row/column/value arrays, sparse Lagrangian Hessian row/column/value arrays,
  Ipopt variables/constraints/multipliers, and final physical block arrays.
- Produces: `build_standalone_ce_receipt(compiled:
  CompiledChemicalEquilibrium, standard_states: StandardStateRegistry,
  native_payload: Mapping[str, object], *, evidence_class: str,
  input_identity: Mapping[str, object], runtime_identity: Mapping[str,
  object]) -> StandaloneCEReceipt`.
- Preserves: `_native_chemical_equilibrium_nlp_activation` as the sole native
  execution binding.

- [ ] **Step 1: Add RED native and Python mutation tests.** Require exact
  species/reaction/conservation labels; solver and physical variables; bounds;
  objective, gradient, constraint, Jacobian, and Hessian primitives; lower,
  upper, and constraint multipliers; route scaling; options/tolerances; all
  continuation stage initial/final states; activities, chemical potentials,
  affinities, and stable hashes. Remove each family one at a time and require a
  path-qualified blocker.

- [ ] **Step 2: Verify RED.** Run
  `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py packages/epcsaft-equilibrium/tests/contracts/test_standalone_ce_receipt_contract.py -q`.
  Expected: only the new primitive/receipt assertions fail.

- [ ] **Step 3: Capture primitives at the final native state.** Extend
  `ChemicalEquilibriumNlpResult` with one
  `ChemicalEquilibriumReceiptPrimitives` member. Populate it from the same
  `HomogeneousChemicalEquilibriumNlp`, `IpoptSolveResult`, and final physical
  proof used for acceptance. Serialize one nested `receipt_primitives` object;
  do not re-evaluate through a second solver or insert defaults.

- [ ] **Step 4: Build the immutable Python receipt.** Combine the native
  primitives with compiled-schema labels, standard-state source metadata,
  provided M3/M6 input identity, equilibrium-native build identity, tolerances,
  and evidence class. Hash canonical JSON subtrees after validation and expose
  the receipt on the internal validation result without changing acceptance.

- [ ] **Step 5: Refactor and verify GREEN.** Move repeated shape/hash checks
  into private receipt helpers, not a second result serializer. Rebuild with
  `uv run --no-sync python scripts/dev/build_epcsaft.py --build-only --parallel 10`,
  then rerun the Task 2 tests. Expected: build succeeds and all focused tests
  pass with the retained live MEA result still rejected.

- [ ] **Step 6: Checkpoint commit.** Commit
  `feat(equilibrium): retain standalone CE proof primitives`.

### Task 3: Add Independent Component Reconstruction And Close Issue #329

**Use Cases:**

- A reviewer can recompute balances, charge, affinities, complementarity, and
  unscaled KKT stationarity from a component receipt without importing the CE
  production solver.
- After prerequisite Task 4 closes #328, issue #329 can close from generic
  receipt/checker evidence while the M6 nonideal source bundle remains blocked
  and `reactive_speciation` remains closed.

**Files:**

- Create: `scripts/validation/check_standalone_ce_receipt.py`
- Create: `tests/native/contracts/test_standalone_ce_receipt.py`
- Create: `analyses/package_validation/standalone_ce/shared/results/standalone_ce_component_receipt.json`
- Modify: `tests/native/contracts/test_standalone_ce_gate.py`

**Interfaces:**

- Produces CLI:
  `check_standalone_ce_receipt.py --receipt PATH --json --require-component-complete`.
- Produces JSON fields `recomputed`, `reported`, `disagreements`,
  `derivative_checks`, `component_contract_status`, and `blockers`.
- Consumes Task 2 `StandaloneCEReceipt`; does not call
  `_run_standalone_ce_validation` or any native solve binding.

- [ ] **Step 1: Write RED independent-checker tests.** Use a small ideal
  component fixture and mutations for a balance row, charge row, affinity,
  gradient, Jacobian, multiplier, bound, label, and hash. Require a complete
  component receipt to pass reconstruction, reject a source-model claim from a
  component fixture, and prove the strict admission gate remains nonzero.

- [ ] **Step 2: Verify RED.** Run
  `uv run --no-sync python run_pytest.py tests/native/contracts/test_standalone_ce_receipt.py tests/native/contracts/test_standalone_ce_gate.py -q`.
  Expected: the new checker tests fail because the component checker CLI does
  not exist; existing closed-route assertions continue to pass.

- [ ] **Step 3: Implement independent arithmetic.** Parse JSON with no import
  from CE production modules. Recompute `C@n-b`, charge when present,
  `nu@mu`, stationarity `grad_f + J.T@lambda - z_L + z_U`, bound
  complementarity, and scaled/unscaled norms. At bounded interior component
  states, compare retained exact derivatives with symmetric two-sided reference evaluations used
  only as a diagnostic test oracle, never as a production derivative path.

- [ ] **Step 4: Record the component-contract result.** Run the checker against
  the retained component fixture, require exact agreement for every
  reconstructable field, record `component_contract_status=complete`, and
  retain `evidence_class=component_fixture` in
  `shared/results/standalone_ce_component_receipt.json`. Do not read M6 files,
  select a nonideal root cause, or change the production activation row.

- [ ] **Step 5: Refactor and verify GREEN.** Keep production and independent
  formulas in separate modules; share only schema field names. Run the Task 3
  tests and the checker with `--require-component-complete`. Expected: the
  component checker passes, issue #329 has complete local proof, the M6 leaf
  may become dependency-ready, and the public route remains closed.

- [ ] **Step 6: Checkpoint commit.** Commit
  `feat(validation): check standalone CE component receipts`.

### Task 4: Reconcile Issue #328 With A Typed Constructor Request (Execute First)

**Use Cases:**

- A caller can configure a homogeneous reaction system without loose mappings,
  while the route remains closed until #330.
- The typed request displaces the internal function signature at admission and
  cannot be mistaken for reactive phase equilibrium.

**Files:**

- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/chemical_equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_requests.py`
- Create: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_schema.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`

**Interfaces:**

- Produces frozen `ChemicalSystem(species, reactions, feed_amounts,
  equilibrium_constants)` with `.compiled` and `.standard_states` properties.
- Produces constructor shape `Equilibrium(mixture, *,
  route="reactive_speciation", chemical_system=system)` while the activation
  guard still rejects execution before #330.
- Preserves public result route through `Equilibrium.solve()`; no free
  `reactive_speciation(...)` function is exported.

- [ ] **Step 1: Write RED request tests.** Require `ChemicalSystem` to reject
  duplicate/order-mismatched reactions, missing equilibrium constants,
  conflicting standard-state contexts, unknown mappings, and phase-splitting
  fields. Require `Equilibrium(..., route="reactive_speciation")` to accept
  only `chemical_system`, prohibit `x/y/z`, and fail at the closed activation
  guard before native dispatch.

- [ ] **Step 2: Verify RED.** Run
  `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_schema.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py -q`.
  Expected: new typed request tests fail while existing closed-capability tests
  pass.

- [ ] **Step 3: Implement the typed request without admission.** Freeze the
  compiled reaction and standard-state records in `ChemicalSystem`; extend the
  configured problem metadata with the typed chemical-system payload; preserve
  the activation guard so `solve()` rejects before calling native code while
  #330 is blocked.

- [ ] **Step 4: Refactor and verify GREEN.** Remove any duplicate compilation
  performed after `ChemicalSystem` construction. Rerun the Task 4 command;
  expected: typed request/schema tests pass and `reactive_speciation` remains
  absent from public capability routes.

- [ ] **Step 5: Checkpoint commit.** Commit
  `feat(equilibrium): type standalone chemical systems`.

### Task 5: Classify The Source-Qualified Outcome In A Separate M4 Leaf

**Use Cases:**

- An evidence-complete M6 receipt with a scientifically rejected solve becomes
  an explicit `source_qualified_rejection`, not a failed M6 task or a
  speculative production edit.
- A proven diagnostic or canonical defect gets one reproducing RED test and
  one owner-specific follow-up, while only `admission_candidate` can unblock
  #330.

**Files:**

- Create: `analyses/package_validation/standalone_ce/shared/results/standalone_ce_root_cause.json`
- Modify: `scripts/validation/check_standalone_ce_receipt.py`
- Modify: `scripts/validation/check_standalone_ce_gate.py`
- Modify: `tests/native/contracts/test_standalone_ce_receipt.py`
- Modify: `tests/native/contracts/test_standalone_ce_gate.py`
- Modify for a proven diagnostic-contract defect only: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/chemical_equilibrium_receipt.py`
- Create for a proven canonical defect only: one new M4 Bug mirror and one
  owner-specific plan under `docs/superpowers/issues/` and
  `docs/superpowers/plans/` after its GitHub number exists.

**Interfaces:**

- Consumes: Task 3's complete component checker result and the M6 receipt only
  after
  `check_nonideal_mea_evidence.py --json --require-evidence-complete` exits
  zero.
- Produces CLI mode:
  `check_standalone_ce_receipt.py --receipt PATH --m6-evidence PATH --json --require-source-classified`.
- Produces exactly one `classification` from `admission_candidate`,
  `source_qualified_rejection`, `diagnostic_contract_defect`,
  `canonical_formulation_defect`, or `not_reproduced`, plus one
  `classification_owner` and explicit #330 readiness.
- Produces an owner-specific M4 Bug only for
  `canonical_formulation_defect`; the Bug blocks this classification leaf until
  a fresh source-qualified run is reclassified.

- [ ] **Step 1: Assert one source-qualified outcome and owner.** Add RED
  mutations for a missing M6 evidence-checker receipt, input/runtime hash
  mismatch, zero outcomes, multiple outcomes, a rejected solve mislabeled as
  `admission_candidate`, and a canonical defect without a reproducing test node
  and exact owner path.

- [ ] **Step 2: Verify RED.** Run the Task 3 focused tests plus
  `tests/native/contracts/test_standalone_ce_gate.py`. Expected: each malformed
  source-qualified mutation fails for its named reason and the current strict
  gate remains closed.

- [ ] **Step 3: Reconstruct and classify the source-qualified case.** Verify
  the M6 evidence-completeness receipt first, match its input/native/M4 receipt
  hashes, and run the independent M4 arithmetic on the selected source-model
  receipt. Select `admission_candidate` only when every numerical gate passes;
  select `source_qualified_rejection` when evidence is complete but the solve
  is scientifically rejected and no code owner is proven; select
  `diagnostic_contract_defect` only for production/checker disagreement;
  select `canonical_formulation_defect` only when one implementation owner has
  a reproducing RED node; select `not_reproduced` for identity mismatch or
  non-repeatability.

- [ ] **Step 4: Execute only the selected follow-up.** Make no production edit
  for `source_qualified_rejection` or `not_reproduced`. For
  `diagnostic_contract_defect`, fix only the receipt/checker owner under TDD.
  For `canonical_formulation_defect`, stop source editing, create the
  owner-specific Bug and plan, attach it as a native blocker of this leaf, and
  rerun classification only after that Bug closes. For `admission_candidate`,
  record #330 as dependency-ready without changing activation.

- [ ] **Step 5: Verify GREEN and refactor.** Re-run the M6 evidence checker,
  component receipt checker, source-qualified receipt checker, and strict M4
  gate. Expected: exactly one classification is retained, a rejected solve can
  complete this classification while #330 stays blocked, and no sibling route
  or unselected owner changes.

- [ ] **Step 6: Checkpoint commit.** Use
  `fix(validation): repair standalone CE receipt diagnostics` only for a
  diagnostic defect, or `docs(equilibrium): classify source-qualified CE result`
  for a non-code outcome. A canonical formulation fix uses the later Bug's own
  checkpoint commit.

### Task 6: Execute Issue #330 As The Sole Admission Cutover

**Use Cases:**

- An evidence-complete M3/M6 source-model receipt, an
  `admission_candidate` M4 classification, and a repaired M4 native path become
  reachable through one selector-backed constructor workflow.
- Negative activation tests prove every coupled phase family and every
  alternate CE path remains closed after cutover.

**Files:**

- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.h`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium_activation.py` through its generator
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/core/native_requests.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/equilibrium.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capabilities.py`
- Modify: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capability_evidence.py`
- Modify: `packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py`
- Modify: `packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py`
- Modify: `tests/native/contracts/test_standalone_ce_gate.py`
- Modify: `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/generate_nonideal_data.py`
- Modify: user-facing equilibrium docs that list public routes

**Interfaces:**

- Consumes: evidence-complete M6 `source_model` receipt, Task 5
  `admission_candidate` classification, strict
  `check_standalone_ce_receipt.py`, and typed `ChemicalSystem`.
- Produces: one production route row
  `reactive_speciation -> reactive_speciation`, one proof-route identity, and
  constructor-configured `Equilibrium.solve()` dispatch through selector core
  to the existing native CE `NlpProblem`/Ipopt owner.
- Removes: the internal-only `_run_standalone_ce_validation` entrypoint after
  all repository callers use the constructor workflow.

- [ ] **Step 1: Add the admission RED tests.** Require the strict M6/M4 receipt
  fingerprints, final `lambda == 1`, accepted Ipopt/application status,
  `balance_inf_norm <= 1.0e-8`,
  `reaction_stationarity_inf_norm <= 1.0e-6`, independent agreement, exact
  derivative evidence, one selector dispatch, one result build, and exact
  capability/activation equality. Add negative tests for every sibling route
  and direct binding.

- [ ] **Step 2: Verify RED.** Run
  `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_standalone_ce_gate.py -q`.
  Expected before admission: only the new production-route assertions fail and
  the strict checker remains nonzero.

- [ ] **Step 3: Add the single selector route and canonical result cutover.**
  Mark only the `reactive_speciation` selector route production-exposed with
  the accepted proof route, generate the Python activation mirror, add one
  selector-core chemical-system dispatch to the existing native CE solver, and
  build the public result once. Remove the direct CE solve binding and internal
  entrypoint, then update every analysis caller in the same slice.

- [ ] **Step 4: Refactor and verify GREEN.** Remove obsolete internal-only
  validation metadata and duplicate serializers. Rebuild the equilibrium
  native profile, rerun Task 6 tests, then run the full proof oracle below.
  Expected: `reactive_speciation` alone is newly public, all strict CE gates
  pass, and coupled phase routes remain closed.

- [ ] **Step 5: Checkpoint commit.** Commit
  `feat(equilibrium): admit standalone reactive speciation`.

## Proof Oracle

```bash
uv run --no-sync python scripts/validate_plan_task_use_cases.py --plan-path docs/superpowers/plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md
uv run --no-sync python scripts/validate_plan_outcome_proof.py --plan-path docs/superpowers/plans/2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission-plan.md
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_standalone_ce_receipt_contract.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_schema.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py packages/epcsaft-equilibrium/tests/native/blocks/test_chemical_equilibrium_blocks.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py packages/epcsaft-equilibrium/tests/api/test_reactive_speciation_api.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_standalone_ce_receipt.py tests/native/contracts/test_standalone_ce_gate.py tests/native/contracts/test_ce_robustness_followup_gate.py -q
uv run --no-sync python scripts/validation/check_ce_robustness_followup.py --json --require-complete
uv run --no-sync python scripts/validation/check_standalone_ce_receipt.py --receipt analyses/package_validation/standalone_ce/shared/results/standalone_ce_component_receipt.json --json --require-component-complete
uv run --no-sync python analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/scripts/check_nonideal_mea_evidence.py --json --require-evidence-complete
uv run --no-sync python scripts/validation/check_standalone_ce_receipt.py --receipt analyses/package_validation/standalone_ce/shared/results/standalone_ce_receipt.json --m6-evidence analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/output/nonideal_mea_evidence_receipt.json --json --require-source-classified
uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete
uv run --no-sync python run_pytest.py --equilibrium-api -q
uv run --no-sync python run_pytest.py --confidence -q
uv run --no-sync ruff check packages/epcsaft-equilibrium/src/epcsaft_equilibrium packages/epcsaft-equilibrium/tests scripts/validation/check_standalone_ce_receipt.py scripts/validation/check_standalone_ce_gate.py tests/native/contracts/test_standalone_ce_receipt.py tests/native/contracts/test_standalone_ce_gate.py
uv run --no-sync python scripts/dev/validate_project.py docs
git diff --check
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
```

Task 4 is the live tracker prerequisite. After it closes #328, Tasks 1-3 and
the component-checker command are the complete proof for #329; they do not run
or require the M6 checker. The M6 and source-classification
commands belong to the later dependency leaves. A scientifically rejected
source solve may satisfy the M6 evidence checker and Task 5 classification but
must leave the final #330 gate nonzero unless Task 5 records
`admission_candidate`.
