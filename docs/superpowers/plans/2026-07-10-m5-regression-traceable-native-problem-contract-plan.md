# Traceable Native Regression Problem Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Use
> `superpowers:test-driven-development` for every behavior change,
> `superpowers:systematic-debugging` for every unexpected failure, and
> `superpowers:verification-before-completion` before each checkpoint is
> accepted.

**Goal:** Make one configured `Regression(mixture)` workflow compile a strict
typed dataset, explicit fitted-parameter selection, resolved provider input,
and effective Ceres controls into the exact native problem and receipt that the
returned result describes.

**Architecture:** Split target, control, parameter-selection, problem,
result, native-adapter, and persistence ownership out of the current monolithic
module. A frozen Python compiler consumes the M3 state-resolved provider
contract and constructs one package-owned native problem record; Ceres owns
residual packing, controls, bounds, derivatives, solve termination, and the
authoritative receipt. Public Python results are detached immutable views of
that receipt, and fitted interaction persistence is a separate rollback-safe
transaction.

**Tech Stack:** Python 3.9-3.13, frozen dataclasses and `StrEnum`, NumPy,
pybind11, C++17, Ceres 2.2, CppAD exact/implicit derivatives, the M3 provider
native SDK record schema version 1, pytest, Ruff, Sphinx, `uv`, and Git.

## Global Constraints

- Milestone ownership is M5 and package ownership is
  `packages/epcsaft-regression`; provider changes belong to the blocking M3
  plan and retained real-data artifacts belong to M6.
- The native-problem compiler may start only after the M3 resolved model-input
  SDK seam is stable. Strict target work may land first.
- Every accepted weight, scale, start, bound, fixed value, loss, tolerance,
  and iteration limit must change a native record or native behavior; otherwise
  reject the option before dispatch.
- Native row semantics are fixed at the cutover:
  `weighted_residual = sqrt(weight) * (model_value - target) / residual_scale`
  and Ceres' linear-loss objective is
  `0.5 * sum(weighted_residual**2)`. Tests must prove weight and scale alter
  the evaluated residual/objective by this formula, not merely alter a hash.
- The first loss contract supports only explicit linear loss. Unknown loss
  names and row-specific loss overrides are rejected.
- A lower or unchanged objective does not convert an unusable or unaccepted
  Ceres termination into success.
- Python must not own the production optimizer loop, residual packing, or
  derivative substitution.
- Do not preserve displaced free-function production paths, raw mapping
  dispatch, post-solve receipt annotation, or retired options through wrappers.
- Do not broaden regression capability rows in this plan. The dependent M5/M6
  plans reset and later re-admit only evidence-backed scopes.
- Do not edit or repair Khudaida, Gross 2002, electrolyte-equilibrium,
  phase-discovery, reactive, or other paper-validation programs.
- Tests that calculate model predictions must use retained traceable source
  rows and preserve an observation/model plot; contract-only mutation tests do
  not require a plot.

---

## Source Evidence

- Approved source spec:
  `docs/superpowers/specs/2026-07-10-m5-regression-traceable-native-problem-contract.md`.
- Parent tracker: GitHub issue #193 under `M5 - Regression`.
- `verified`: `TargetRow` currently permits blank identity/source fields,
  inserts weight `1.0`, and stores family payloads in a loose mapping in
  `packages/epcsaft-regression/src/epcsaft_regression/core.py`.
- `verified`: public helpers currently accept `weights`, `loss`,
  `solver_options`, and `output_report`, while
  `_annotate_contract_problem()` records them after the native solve.
- `verified`: `Regression(mixture)` stores a mixture but delegates to a free
  function that does not compile that mixture into the native problem.
- `verified`: the generic native adapter forwards row records, targets, bounds,
  starts, and one limit, but not the declared control surface.
- `verified`: generic pure-ion and binary native paths currently accept
  `summary.IsSolutionUsable()` **or** a non-increasing objective as success.
- `verified`: fitted matrix and manifest files are replaced one at a time, so
  an injected failure can expose generations from different transactions.
- `verified`: the M3 source spec assigns component order, parameter and
  formulation fingerprints, state evaluation, and native snapshot ownership
  to `ResolvedModelInput`.
- `verified`: the approved M3 plan selects
  `mixture.resolved_model_input`, `ResolvedModelInput.fingerprint_sha256`, and
  immutable `EvaluatedModelInput` objects returned by
  `ResolvedModelInput.evaluate(temperature=..., composition=...)` as the M5
  consumer seam. Each object carries the exact read-only native snapshot handle
  and detached receipt. Task 2 remains blocked until that seam is implemented
  and its provider tests pass.

## Test Complete And Metrics

The contract is test-complete when all of the following are measured by named
tests and retained receipts:

- every accepted `TargetRow` has one nonblank unique row ID, a source identity,
  explicit canonical units, a positive finite weight and residual scale, and a
  complete family-specific payload;
- literature, user-measurement, and generated component-test source kinds have
  distinct citation rules;
- target row order and row/source IDs survive compilation, native execution,
  receipt emission, and Python result construction unchanged;
- mutation tests cover every field of `RegressionControls` and every fitted
  parameter start/bound; native option capture proves exact Ceres field mapping,
  a bounded-iteration fixture proves effective solver behavior, and native
  evaluation proves row weights/scales change residuals and objectives by the
  declared formula;
- the receipt contains schema version, provider definition/state
  fingerprints, ordered parameters/rows, controls, objective values,
  evaluation counts, termination, usability, derivative ownership, movement,
  active bounds, and per-row diagnostics;
- changing the configured mixture changes the compiled provider fingerprint;
- raw records, raw mappings, and free `fit_*` exports cannot reach production
  native solve functions;
- every injected persistence failure leaves all destination files either the
  complete original generation or the complete accepted generation;
- focused M5 tests, the regression validation lane, Ruff, strict docs, diff
  checks, and cleanup pass.

## Outcome Proof

**Intent:** Ensure a returned regression result is an exact, reproducible view
of the configured provider inputs, target rows, fitted parameters, controls,
and native Ceres problem that actually ran.

**Current Behavior:** Loose target rows and duplicated problem builders allow
source identity to disappear, accepted controls to be recorded after solving,
the configured mixture to be ignored, cost-only success to mask an unusable
termination, and multi-file persistence to expose mixed generations.

**Expected Outcome:** One strict dataset and one configured workflow compile
through one M3-aware problem owner into one native Ceres record; Ceres emits the
authoritative versioned receipt; Python returns immutable receipt-backed views;
and persistence is all-new or all-original under failure injection.

**Target Output:** Focused target/control/parameter/problem/result/persistence
modules, package-owned native problem/receipt records, a single configured
workflow, strict tests, updated exports/docs, deleted displaced modules and
helpers, and transaction-failure receipts.

**Owner:** M5 and `packages/epcsaft-regression`; M3 owns the consumed resolved
provider record and M6 owns later scientific evidence artifacts.

**Interface:** `Regression(mixture, controls=RegressionControls(...))`,
`Regression.fit(dataset, parameters=tuple[FittedParameter, ...]) -> FitResult`,
`Regression.evaluate(result.problem, parameter_values=Mapping[str, float]) ->
RegressionEvaluation`, `FitResult.problem`, `FitResult.receipt`, and
`write_fit_result(result, dataset_root=..., overwrite=...)`.

**Cutover:** The configured workflow and compiled native record replace free
`fit_*` production dispatch, unchecked record sequences, raw native payload
maps, and post-solve annotation in one coordinated API cutover.

**Replaced Path:** Delete `core.py`, `pure.py`, `binary.py`,
`_annotate_contract_problem`, public free `fit_*` exports, raw mapping solve
entry points, and one-by-one matrix/manifest commit helpers after all consumers
move to the focused owners.

**Evidence:** Strict target mutation tests, native control mutation tests,
provider-fingerprint consumer tests, native receipt snapshots, derivative and
termination tests, persistence failure injection, import/structure gates,
focused regression tests, docs, Ruff, diff review, and cleanup output.

**Acceptance Proof:** A configured methane contract fixture and a configured
binary contract fixture preserve exact row/source/model fingerprints through
native receipts; every accepted control maps to the exact effective Ceres
option and at least one controlled fixture proves changed solver behavior;
weight/scale mutations change native residuals/objectives by the declared
formula; invalid inputs fail before dispatch; only `CONVERGENCE` and
`USER_SUCCESS` can satisfy the accepted-termination predicate; and all
transaction cut points reload as a coherent original or new dataset.

**Stop Criteria:** Stop on an unstable M3 SDK seam, any accepted option with no
native field or mutation effect, incomplete derivative columns, row identity
reordering, a cost-only success path, or a persistence failure that cannot
restore exact original bytes.

**Avoid:** Do not add fallback values, infer missing compositions or units,
normalize supplied fractions silently, invent source locators, duplicate the
provider serializer, keep a compatibility solve path, or use scientific plots
as a substitute for contract mutation proof.

**Risk:** This intentional cutover will break callers that relied on implicit
defaults or free functions, and applying controls for real can change fitted
values; synchronized docs, analysis migrations, and receipt comparisons must
make those changes visible.

## Implementation Boundaries

**Files To Create:** `targets.py`, `controls.py`, `parameters.py`, `problem.py`,
`results.py`, `persistence.py`, `native/regression/regression_problem.h`, and
focused API/native/persistence tests under `packages/epcsaft-regression`.

**Files To Modify:** `workflow.py`, `native_adapter.py`, `_native_core.pyi`,
`native/regression/module.cpp`, `native/regression/ceres_regression.cpp`,
`__init__.py`, package/root regression docs, validation registry entries, and
repo structure tests that enumerate the public regression surface.

**Files To Avoid:** Provider implementation under `packages/epcsaft`, all M4
equilibrium implementation, all paper-validation programs, M6 retained
scientific artifacts, release metadata, stashes, and remote refs.

**Source Of Truth:** The approved M5 spec, the accepted M3 resolved-input SDK
record, typed `TargetDataset`, package-owned C++ problem record, native Ceres
summary, and native-emitted receipt.

**Read Path:** Parse a strict dataset, read the configured mixture's resolved
definition, retain each typed `EvaluatedModelInput` at its row condition, compile ordered
parameter/control/row records, solve or evaluate natively, then construct a
detached Python view from the native receipt.

**Write Path:** Only explicit post-fit persistence writes parameter data; it
stages all destinations on the same filesystem, records exact original bytes,
replaces deterministically, strict-reloads, rolls back on failure, fsyncs the
directory, and removes its transaction files.

**Integration Points:** M3 resolved-model-input SDK, provider native records,
Ceres/CppAD regression code, pybind11, public regression exports, dataset
interaction manifests, user docs, validation registry, and repo structure
gates.

**Migration Or Cutover:** Characterize the current paths, land strict targets,
add the M3-aware compiler and native record, cut the workflow and results to the
receipt, land transactional persistence, then delete every displaced owner in
the same commit that moves its final caller.

**Replaced Path Handling:** No redirect modules or compatibility wrappers are
retained. Import and structure tests assert that deleted free functions,
annotation helpers, raw payload entry points, and monolithic owners are absent.

**Acceptance Proof Gate:** Do not close #193's contract children until focused
tests prove row/source/fingerprint preservation, every supported control's
native effect, strict termination semantics, exact derivative coverage,
workflow exclusivity, and rollback at every injected write boundary.

## Decision Ledger

| Decision | Evidence | Selected answer | Consequence | Deferred? | Owner |
| --- | --- | --- | --- | --- | --- |
| Task grouping | Tasks 10, 11, and the M5 half of Task 21 share one problem path | One native-contract plan | Target, control, receipt, workflow, and decomposition cannot drift into parallel implementations. | No | M5 |
| Tracker | Open issue audit | Reuse #193 as parent | Bounded implementation leaves become subissues instead of another tracker. | No | M5 |
| Source identity | Private and literature data have different evidence | Require source identity for every row; require a citation locator only for literature | Private measurements remain valid without a fabricated publication. | No | M5 |
| Composition | Only some families carry compositions | Validate family-specific composition records and never silently normalize | Pure-property rows do not receive meaningless composition fields. | No | M5 |
| Controls | Current accepted controls can be ignored | Native field plus mutation proof or rejection | The Python receipt cannot claim a control Ceres did not receive. | No | M5 |
| Loss | No approved robust-loss use case | Linear only at first cutover | Later losses require separate native mapping and mutation evidence. | Yes | M5 |
| Result authority | Current post-solve annotation defect | Native-emitted schema-v1 receipt | Python views cannot describe a different problem. | No | M5 |
| Success | Current cost shortcut | Usable solution plus accepted native termination and finite required fields | Unfinished or unusable solves remain failures. | No | M5 |
| Workflow | Stored mixture currently is not compiled | `Regression(mixture)` is the sole production owner | Free production fit functions are deleted. | No | M5 |
| Persistence | Multi-file partial replacement | Same-filesystem staged transaction with exact-byte rollback | Matrix and manifest reload as one generation. | No | M5 |
| Capability | Real-data evidence is a separate milestone boundary | Keep all admission changes out of this plan | The M5/M6 DAG remains acyclic. | No | M5/M6 |

## Execution Dependency Graph

```text
M3 resolved-model-input SDK
          |
Task 1 strict targets ----+
          |               |
          +----> Task 2 compiler and controls
                         |
                         v
                  Task 3 native record/receipt
                         |
                         v
                  Task 4 workflow cutover
                         |
                         v
              Task 5 persistence
                         |
                         v
              Task 6 deletion/docs/proof
```

### Task 1: Extract strict target and source contracts

**Use Cases:**

- A literature row carries an exact source locator and remains visible by its
  row/source IDs in later acceptance evidence.
- A private measurement carries stable dataset and row identity without a
  fabricated DOI.
- A composition-bearing row rejects missing fractions, wrong species order,
  and silent normalization before provider evaluation.
- A pure saturation training point uses two explicit target families: a
  dimensionless liquid-minus-vapor log-fugacity balance at observed pressure,
  and a liquid-density value at that same observed pressure. It is not
  silently reinterpreted as a direct predicted-saturation-pressure residual.
- A binary observed-state row defines one zero target per component as
  `log(x_i) + log(phi_i_liquid) - log(y_i) - log(phi_i_vapor)` at the row's
  exact T/P/x/y; pressure cancels because both phases share the same pressure.
- The cutover replaces unchecked records while preserving deterministic row
  order for native diagnostics.

**Files:**

- Create: `packages/epcsaft-regression/src/epcsaft_regression/targets.py`
- Create: `packages/epcsaft-regression/tests/api/test_targets.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/__init__.py`
- Modify: `packages/epcsaft-regression/tests/api/test_regression.py`

**Interfaces:**

- Consumes: mappings only through
  `TargetDataset.from_records(records, *, dataset_id, default_family=None)`.
- Produces: `SourceKind`, `SourceIdentity`, `CompositionBasis`,
  `CompositionRecord`, `TargetFamily`, frozen `TargetRow`, and frozen
  `TargetDataset`.
- `TargetRow` fields are exactly `row_id`, `target_family`, `conditions`,
  `observations`, `units`, `weight`, `residual_scale`, `source`, `phase`, and
  `compositions`; weight and residual scale are mandatory positive finite
  values.

- [ ] **Step 1: Write strict identity, source-kind, units, composition, and
  ordering tests.**

  Add tests with this contract shape:

  ```python
  row = TargetRow(
      row_id="susial-table6-row001",
      target_family=TargetFamily.BINARY_VLE,
      conditions={"temperature": 372.3, "pressure": 100000.0},
      observations={},
      units={"temperature": "K", "pressure": "Pa"},
      weight=1.0,
      residual_scale=1.0,
      source=SourceIdentity(
          source_id="Susial_2021_JCED",
          source_kind=SourceKind.LITERATURE,
          citation="10.1021/acs.jced.0c00686",
          locator="Table 6, 100 kPa, row 1",
      ),
      phase="vle",
      compositions=(
          CompositionRecord("liquid", CompositionBasis.MOLE_FRACTION, ("Ethanol", "H2O"), (0.001, 0.999)),
          CompositionRecord("vapor", CompositionBasis.MOLE_FRACTION, ("Ethanol", "H2O"), (0.014, 0.986)),
      ),
  )
  assert TargetDataset(rows=(row,), dataset_id="susial-2021-table6").row_ids == (
      "susial-table6-row001",
  )
  ```

  Include named failures for blank and duplicate IDs, missing source identity,
  missing literature locator, noncanonical units, nonfinite conditions,
  nonpositive weight/scale, incomplete composition, wrong sum, and conflicting
  duplicates. Include a user-measurement source with an empty citation and a
  required nonblank `dataset_id`/`locator`.
  For `TargetFamily.BINARY_VLE`, assert the ordered model values are exactly the
  two component log-fugacity imbalances
  `log(x_i * phi_i_liquid / (y_i * phi_i_vapor))`, each paired with target
  `0.0`; reject nonpositive observed fractions or fugacity coefficients rather
  than changing the logarithm definition.
  For `TargetFamily.PURE_SATURATION_FUGACITY_BALANCE`, assert model value
  `ln(f_liquid(T, P_obs)) - ln(f_vapor(T, P_obs))`, target `0.0`, dimensionless
  residual scale `1.0`, and an explicit positive row weight. For
  `TargetFamily.PURE_LIQUID_DENSITY_AT_PRESSURE`, assert model value
  `rho_liquid_mass(T, P_obs)`, target `rho_obs`, units `kg/m3`, and residual
  scale exactly `rho_obs`, so the unweighted residual is relative density
  error. A molar native density is converted with the exact resolved methane
  molar mass before comparison.
  Mutation tests must reject a direct `P_sat_predicted - P_obs` interpretation
  under either family and reject a density scale that does not equal the
  retained positive observation for this fixed contract.

- [ ] **Step 2: Run the RED target tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/api/test_targets.py -q
  ```

  Expected: collection or assertions fail because the focused module and
  strict source/composition records do not exist.

- [ ] **Step 3: Implement the focused frozen contracts and named strict
  constructor.**

  Use closed enums and immutable tuple-backed records. `from_records` must
  convert known CSV columns explicitly, reject unconsumed keys, preserve input
  order, and run the same constructor validation as direct construction. The
  family dispatcher must contain one validator for each currently supported
  family and must reject an unregistered family. Keep the pure saturation
  fugacity-balance and predicted-saturation-pressure concepts as distinct
  families; the latter is not admitted by this first contract.

- [ ] **Step 4: Run the GREEN target and API tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/api/test_targets.py packages/epcsaft-regression/tests/api/test_regression.py -q
  ```

  Expected: all selected tests pass; every serialized row contains the exact
  explicit identity, units, source, weight, scale, and family payload.

- [ ] **Step 5: Refactor family validation out of the public records without
  changing serialized output.**

  Keep validation helpers private in `targets.py`; rerun Step 4 and compare a
  canonical JSON snapshot before/after the refactor. Expected: byte-identical
  canonical row JSON.

- [ ] **Step 6: Commit the checkpoint.**

  ```bash
  git add packages/epcsaft-regression/src/epcsaft_regression/targets.py packages/epcsaft-regression/src/epcsaft_regression/__init__.py packages/epcsaft-regression/tests/api/test_targets.py packages/epcsaft-regression/tests/api/test_regression.py
  git commit -m "feat(regression): require strict target datasets"
  ```

### Task 2: Add explicit controls, fitted parameters, and the M3-aware problem compiler

**Use Cases:**

- A caller selects every fitted parameter with an explicit start and lower and
  upper bound; resolved mixture values provide the fixed parameter graph.
- An unknown control, missing bound, conflicting parameter key, or unsupported
  target/parameter pair fails before native dispatch.
- Changing the configured mixture changes the provider definition fingerprint
  embedded in the compiled problem and later receipt.
- This task replaces loose option dictionaries and duplicate payload builders
  with one typed compilation path.

**Files:**

- Create: `packages/epcsaft-regression/src/epcsaft_regression/controls.py`
- Create: `packages/epcsaft-regression/src/epcsaft_regression/parameters.py`
- Create: `packages/epcsaft-regression/src/epcsaft_regression/problem.py`
- Create: `packages/epcsaft-regression/tests/api/test_problem_compiler.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/workflow.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/__init__.py`

**Interfaces:**

- Consumes: `mixture.resolved_model_input.fingerprint_sha256`, immutable typed
  `EvaluatedModelInput` objects from
  `mixture.resolved_model_input.evaluate(temperature=..., composition=...)`, a
  strict `TargetDataset`, `tuple[FittedParameter, ...]`, and
  `RegressionControls`.
- Produces: frozen `FittedParameter(key: str, start: float, lower: float,
  upper: float)`, frozen `RegressionControls(loss: LossKind,
  max_num_iterations: int, function_tolerance: float, gradient_tolerance:
  float, parameter_tolerance: float)`, and frozen `CompiledRegressionProblem`.
- Produces:
  `compile_regression_problem(*, mixture, dataset, parameters, controls) ->
  `CompiledRegressionProblem` with ordered `EvaluatedModelInput` native handles
  and exact detached definition/state receipts and fingerprints. It does not
  flatten a provider object back into a Python mapping.

- [ ] **Step 1: Write RED compiler and control tests.**

  Use explicit controls:

  ```python
  controls = RegressionControls(
      loss=LossKind.LINEAR,
      max_num_iterations=80,
      function_tolerance=1.0e-10,
      gradient_tolerance=1.0e-10,
      parameter_tolerance=1.0e-10,
  )
  parameters = (
      FittedParameter("Methane.m", start=1.08, lower=0.5, upper=3.5),
      FittedParameter("Methane.sigma", start=3.55, lower=2.0, upper=5.0),
      FittedParameter("Methane.epsilon_k", start=155.0, lower=50.0, upper=400.0),
  )
  compiled = compile_regression_problem(
      mixture=mixture,
      dataset=dataset,
      parameters=parameters,
      controls=controls,
  )
  assert compiled.provider_definition_fingerprint == mixture.resolved_model_input.fingerprint_sha256
  assert compiled.row_ids == dataset.row_ids
  ```

  Add mutations for each control, unknown mapping keys, nonfinite and reversed
  bounds, duplicate/conflicting parameter keys, missing starts, unsupported
  losses, row loss overrides, unsupported target/parameter combinations, and
  a state correlation outside its retained domain.

- [ ] **Step 2: Run the RED compiler tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/api/test_problem_compiler.py -q
  ```

  Expected: failures show that typed controls, fitted-parameter records, and a
  single M3-aware compiler are absent.

- [ ] **Step 3: Implement the typed records and compiler.**

  The compiler must iterate dataset rows in order, evaluate the provider graph
  at each row's exact temperature/composition, retain the returned typed native
  handle and detached receipt without reserialization, verify all state
  fingerprints descend from one definition fingerprint, and emit no native
  defaults. Use a closed target/parameter compatibility table and include the
  exact fixed parameter fingerprints in the compiled record.

- [ ] **Step 4: Run GREEN compiler and M3 consumer-contract tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/api/test_problem_compiler.py packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py -q
  ```

  Expected: all selected tests pass; two source-qualified mixtures produce
  different definition fingerprints and no raw `ParameterSet` or mapping
  enters the regression native adapter.

- [ ] **Step 5: Refactor canonical serialization into one private function.**

  Add `_canonical_problem_json(problem) -> bytes` in `problem.py` and prove
  equivalent input order produces byte-stable output while row order remains
  intentionally significant. Rerun Step 4; expected results remain green.

- [ ] **Step 6: Commit the checkpoint.**

  ```bash
  git add packages/epcsaft-regression/src/epcsaft_regression/controls.py packages/epcsaft-regression/src/epcsaft_regression/parameters.py packages/epcsaft-regression/src/epcsaft_regression/problem.py packages/epcsaft-regression/src/epcsaft_regression/workflow.py packages/epcsaft-regression/src/epcsaft_regression/__init__.py packages/epcsaft-regression/tests/api/test_problem_compiler.py
  git commit -m "feat(regression): compile one resolved native problem"
  ```

### Task 3: Make Ceres controls, termination, and the native receipt authoritative

**Use Cases:**

- Every supported Python control appears in the native problem record and in
  the effective `ceres::Solver::Options` captured immediately before `Solve`;
  a one-field mutation changes that exact native field, and a bounded-iteration
  fixture proves the applied option can change solver behavior.
- Row weight and residual scale mutations preserve the raw model-minus-target
  value while changing native packed residuals and objective by the declared
  square-root-weight/divide-by-scale formula.
- Native row diagnostics retain exact ordered row and source IDs.
- An unusable termination, `NO_CONVERGENCE`, `FAILURE`, or `USER_FAILURE`
  remains unsuccessful even when the final cost does not increase; only
  `CONVERGENCE` and `USER_SUCCESS` are accepted termination enum values, and
  they still require `solution_usable` plus the remaining receipt predicates.
- The native receipt replaces post-solve Python annotation and supplies
  acceptance evidence for later M6 lanes.

**Files:**

- Create: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/regression_problem.h`
- Create: `packages/epcsaft-regression/tests/native/test_problem_receipt.py`
- Create: `packages/epcsaft-regression/tests/native/test_control_mutations.py`
- Create: `packages/epcsaft-regression/tests/native/test_termination_contract.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/module.cpp`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native_adapter.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/_native_core.pyi`

**Interfaces:**

- Consumes: `CompiledRegressionProblem` and the M3 SDK typed
  `EvaluatedModelInput.native_handle` objects already stored in it.
- Produces pybind types `NativeRegressionRow`, `NativeFittedParameter`,
  `NativeRegressionControls`, and `NativeRegressionProblem`.
- Produces `_solve_regression(problem: NativeRegressionProblem) -> dict` and
  `_evaluate_regression(problem: NativeRegressionProblem,
  parameter_values: Sequence[float]) -> dict`.
- Native result dictionaries contain `receipt_schema_version == 1`,
  `problem_receipt`, `problem_fingerprint`, `termination_type`,
  `solution_usable`, `effective_ceres_options`, raw and weighted ordered row
  diagnostics, and exact derivative metadata.

- [ ] **Step 1: Write RED native record, mutation, derivative, and termination
  tests.**

  Parameterize one-field mutations over:

  ```python
  (
      "row.weight",
      "row.residual_scale",
      "parameter.start",
      "parameter.lower",
      "parameter.upper",
      "controls.max_num_iterations",
      "controls.function_tolerance",
      "controls.gradient_tolerance",
      "controls.parameter_tolerance",
  )
  ```

  Assert each mutation changes the canonical native problem fingerprint. For
  each control, also assert the matching value in `effective_ceres_options`
  equals the submitted value read back from the actual options object. On a
  deterministic bounded-iteration fixture, show that changing
  `max_num_iterations` changes the enforced iteration/evaluation ceiling or
  resulting termination. For row weight and residual scale, call
  `_evaluate_regression` on the same parameter vector and assert the raw
  model-minus-target value is unchanged while
  `r = sqrt(weight) * raw / residual_scale` and
  `objective = 0.5 * sum(r**2)` change exactly.

  Parameterize binding-only injected summaries over all Ceres termination enum
  values. Assert `CONVERGENCE` and `USER_SUCCESS` are the only accepted values,
  each still fails when `solution_usable=False`, and `NO_CONVERGENCE`,
  `FAILURE`, and `USER_FAILURE` fail even with non-increasing cost. Assert every
  fitted parameter has a complete Jacobian column owned by the declared
  exact/implicit derivative path.

- [ ] **Step 2: Run RED tests against the current native module.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/native/test_problem_receipt.py packages/epcsaft-regression/tests/native/test_control_mutations.py packages/epcsaft-regression/tests/native/test_termination_contract.py -q
  ```

  Expected: tests fail because the native typed record, complete control
  mapping, receipt schema, and strict termination predicate do not exist.

- [ ] **Step 3: Implement package-owned C++ records and bind their exact
  constructors.**

  `regression_problem.h` must define value-only records for rows, fitted
  parameters, controls, typed provider snapshot handles, and problem identity.
  Validate all sizes, finite fields, row/source IDs, bounds, and enum values in
  the native constructor; do not read absent fields with an inserted value or
  rebuild a provider payload from a receipt mapping.

- [ ] **Step 4: Apply controls in Ceres and emit the complete native receipt.**

  Configure the four selected solver fields directly from
  `NativeRegressionControls`, copy their effective values back from the actual
  `ceres::Solver::Options` object into the receipt immediately before `Solve`,
  apply linear loss and
  `sqrt(weight) * (model_value - target) / residual_scale` in native residual
  construction, and populate the receipt from the submitted record plus
  `ceres::Solver::Summary`. Define accepted termination exactly as
  `{ceres::CONVERGENCE, ceres::USER_SUCCESS}`; success additionally requires a
  usable solution, finite required output, and complete derivative ownership.

- [ ] **Step 5: Build the regression native extension and run GREEN native
  tests.**

  Run:

  ```bash
  uv run --no-sync python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/native/test_problem_receipt.py packages/epcsaft-regression/tests/native/test_control_mutations.py packages/epcsaft-regression/tests/native/test_termination_contract.py packages/epcsaft-regression/tests/native/test_pure.py packages/epcsaft-regression/tests/native/test_binary.py packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py -q
  ```

  Expected: build succeeds; all selected tests pass; the mutation matrix reports
  one changed native fingerprint and exact effective mapping per control,
  weight/scale evaluations obey the residual/objective formula, the iteration
  fixture demonstrates effective behavior, and no cost-only success remains.

- [ ] **Step 6: Refactor repeated pure-ion/binary result assembly into the
  receipt builder.**

  Remove duplicated success and metadata assembly from both native solver
  branches, route both through one `make_regression_receipt`, rerun Step 5, and
  verify canonical receipts are unchanged for characterized fixtures.

- [ ] **Step 7: Commit the checkpoint.**

  ```bash
  git add packages/epcsaft-regression/src/epcsaft_regression/native/regression/regression_problem.h packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp packages/epcsaft-regression/src/epcsaft_regression/native/regression/module.cpp packages/epcsaft-regression/src/epcsaft_regression/native_adapter.py packages/epcsaft-regression/src/epcsaft_regression/_native_core.pyi packages/epcsaft-regression/tests/native/test_problem_receipt.py packages/epcsaft-regression/tests/native/test_control_mutations.py packages/epcsaft-regression/tests/native/test_termination_contract.py
  git commit -m "feat(regression): emit authoritative native receipts"
  ```

### Task 4: Cut the public workflow and result views to the receipt-backed path

**Use Cases:**

- A user calls one configured `Regression.fit` API with a strict dataset and
  explicit parameter records.
- A package-owned `Regression.evaluate` oracle evaluates the exact compiled
  `FitProblem` at a supplied parameter vector for M6 before/after tables.
- Mutating a returned receipt dictionary cannot mutate the result or later
  evaluation.
- Public free functions, loose records, and a mismatched mixture cannot bypass
  the configured cutover.

**Files:**

- Create: `packages/epcsaft-regression/src/epcsaft_regression/results.py`
- Create: `packages/epcsaft-regression/tests/api/test_workflow.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/workflow.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/native_adapter.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/__init__.py`
- Modify: `packages/epcsaft-regression/tests/api/test_regression.py`
- Modify: `packages/epcsaft-regression/tests/test_imports.py`

**Interfaces:**

- Consumes: the Task 2 compiler and Task 3 `_solve_regression` /
  `_evaluate_regression` bindings.
- Produces frozen `FitProblem`, `RegressionReceipt`, `FitResult`, and
  `RegressionEvaluation`; each exposes detached mappings and ordered row
  diagnostics.
- Produces the exact public methods:
  `Regression.fit(dataset, *, parameters) -> FitResult` and
  `Regression.evaluate(problem: FitProblem, *, parameter_values) ->
  RegressionEvaluation`.

- [ ] **Step 1: Write RED public cutover and detached-receipt tests.**

  Assert the public shape:

  ```python
  regression = Regression(mixture, controls=controls)
  result = regression.fit(dataset, parameters=parameters)
  evaluation = regression.evaluate(
      result.problem,
      parameter_values=result.final_parameters,
  )
  assert result.receipt.problem_fingerprint == evaluation.receipt.problem_fingerprint
  assert result.receipt.row_ids == dataset.row_ids
  assert not hasattr(epcsaft_regression, "fit_binary_parameters")
  ```

  Add tests that reject raw record sequences, unknown keyword overrides, and
  attempts to override the configured mixture or controls at fit time. Mutate
  `result.receipt.to_dict()` and assert the original remains unchanged.

- [ ] **Step 2: Run the RED workflow tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/api/test_workflow.py packages/epcsaft-regression/tests/test_imports.py -q
  ```

  Expected: failures show the generic fit/evaluate API and immutable
  receipt-backed result classes are absent and free exports remain.

- [ ] **Step 3: Implement result parsing and the configured workflow.**

  Parse only `receipt_schema_version == 1`; reject missing receipt fields and
  unknown versions. Store tuple and read-only scalar fields internally and
  return deep detached dictionaries. The workflow must compile once per call,
  dispatch the compiled problem, and never annotate a native result afterward.

- [ ] **Step 4: Remove public free-function exports and migrate package tests to
  the configured workflow.**

  Delete free names from `__all__`, lazy export tables, and package-specific
  docs/tests. Do not add forwarding functions. Keep private characterization
  helpers only until Task 6 removes their final internal caller.

- [ ] **Step 5: Run GREEN workflow, import, provider-fingerprint, and native
  regression tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/api/test_workflow.py packages/epcsaft-regression/tests/api/test_regression.py packages/epcsaft-regression/tests/test_imports.py packages/epcsaft-regression/tests/native/test_problem_receipt.py packages/epcsaft-regression/tests/native/test_pure.py packages/epcsaft-regression/tests/native/test_binary.py -q
  ```

  Expected: all selected tests pass through `Regression`; imports expose no
  free production fit path; fit and evaluate receipts retain the configured M3
  fingerprints.

- [ ] **Step 6: Refactor result field access while preserving canonical receipt
  bytes.**

  Move all native-to-Python field conversion into
  `RegressionReceipt.from_native`, rerun Step 5, and compare the canonical
  receipt fixture before/after. Expected: byte-identical receipt JSON.

- [ ] **Step 7: Commit the checkpoint.**

  ```bash
  git add packages/epcsaft-regression/src/epcsaft_regression/results.py packages/epcsaft-regression/src/epcsaft_regression/workflow.py packages/epcsaft-regression/src/epcsaft_regression/native_adapter.py packages/epcsaft-regression/src/epcsaft_regression/__init__.py packages/epcsaft-regression/tests/api/test_workflow.py packages/epcsaft-regression/tests/api/test_regression.py packages/epcsaft-regression/tests/test_imports.py
  git commit -m "refactor(regression): cut over to configured workflows"
  ```

### Task 5: Make fitted interaction persistence rollback-safe

**Use Cases:**

- A successful binary fit writes its interaction matrix and source manifest as
  one logical generation.
- An injected stage, replace, fsync, or strict-reload failure restores the
  exact original bytes for every destination.
- A recovery failure reports exact affected paths and never reports a
  successful persistence receipt.
- The transaction replaces one-by-one file commits without leaving backups or
  hidden generations.

**Files:**

- Create: `packages/epcsaft-regression/src/epcsaft_regression/persistence.py`
- Create: `packages/epcsaft-regression/tests/api/test_persistence.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/workflow.py`
- Modify: `packages/epcsaft-regression/src/epcsaft_regression/__init__.py`

**Interfaces:**

- Consumes: successful `FitResult`, a user-owned `dataset_root`, and explicit
  `overwrite: bool`.
- Produces:
  `write_fit_result(result, *, dataset_root: Path, overwrite: bool) ->
  PersistenceReceipt`.
- `PersistenceReceipt` contains transaction ID, destination paths, original
  and accepted SHA-256 values, strict-reload fingerprint, and completion state.

- [ ] **Step 1: Write RED transaction and failure-injection tests.**

  Parameterize failures at `stage_write`, `stage_fsync`, each `replace`,
  `directory_fsync`, and `strict_reload`. Snapshot exact destination bytes
  before each run and assert either every new hash is present after success or
  every original byte string is restored after failure. Assert no transaction
  file remains after either path.

- [ ] **Step 2: Run the RED persistence tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/api/test_persistence.py -q
  ```

  Expected: injected failures demonstrate the current one-by-one replacement
  cannot guarantee a coherent generation.

- [ ] **Step 3: Implement the same-filesystem staged transaction.**

  Validate all new matrix and manifest bytes in memory, stage each sibling
  temporary file, fsync staged files, retain original bytes in memory for
  recovery, replace in deterministic path order, strict-reload the complete
  dataset, fsync the directory, and remove transaction files. On any failure,
  restore every touched destination from exact original bytes and strict-reload
  the original generation before raising.

- [ ] **Step 4: Run GREEN persistence and provenance tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests/api/test_persistence.py packages/epcsaft/tests/api/frontend/test_interaction_provenance.py -q
  ```

  Expected: all replacement/failure points pass; every success and rollback
  reloads one coherent matrix/manifest generation.

- [ ] **Step 5: Refactor file operations behind an injected transaction I/O
  protocol.**

  Keep the production implementation on `os.replace`, file/directory fsync,
  and strict dataset reload; use the protocol only to make each failure point
  deterministic in tests. Rerun Step 4; expected hashes and cleanup remain
  unchanged.

- [ ] **Step 6: Commit the checkpoint.**

  ```bash
  git add packages/epcsaft-regression/src/epcsaft_regression/persistence.py packages/epcsaft-regression/src/epcsaft_regression/workflow.py packages/epcsaft-regression/src/epcsaft_regression/__init__.py packages/epcsaft-regression/tests/api/test_persistence.py
  git commit -m "fix(regression): persist fitted interactions atomically"
  ```

### Task 6: Delete displaced owners and close the focused M5 contract proof

**Use Cases:**

- Maintainers can locate target, controls, problem, results, native dispatch,
  and persistence in one focused owner each.
- Structure tests prove the old monolithic and free-function paths are gone,
  not hidden behind redirects.
- User docs show the strict configured workflow and its receipt without
  claiming real-data admission before M6 evidence passes.
- Final validation evidence covers the complete contract cutover and replaced
  paths.

**Files:**

- Delete: `packages/epcsaft-regression/src/epcsaft_regression/core.py`
- Delete: `packages/epcsaft-regression/src/epcsaft_regression/pure.py`
- Delete: `packages/epcsaft-regression/src/epcsaft_regression/binary.py`
- Modify: `packages/epcsaft-regression/README.md`
- Modify: `packages/epcsaft-regression/docs/README.md`
- Modify: `docs/pages/parameter_regression.rst`
- Modify: `docs/pages/project_structure.rst`
- Modify: `scripts/dev/validation_registry.py`
- Modify: `tests/workflows/repo/test_project_structure.py`

**Interfaces:**

- Consumes: Tasks 1-5 and the focused M3 consumer contract.
- Produces: the final focused module map, docs, validation registry slice, and
  structure assertions that prevent the removed paths from returning.

- [ ] **Step 1: Write RED structure and documentation contract assertions.**

  Assert `core.py`, `pure.py`, and `binary.py` are absent; root exports contain
  only the configured workflow and typed contracts; the retired annotation and
  free function names do not appear in production source; docs contain one
  strict `Regression.fit(TargetDataset, parameters=...)` example and state
  that regression family admission remains closed pending M6 evidence.

- [ ] **Step 2: Run RED structure and docs tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py tests/workflows/repo/test_project_structure.py packages/epcsaft-regression/tests/test_imports.py -q
  ```

  Expected: assertions fail while displaced modules, exports, helpers, or docs
  remain.

- [ ] **Step 3: Move final characterized helpers, delete displaced files, and
  update docs/registry.**

  Put each still-required private function in its single focused owner; delete
  any helper with no caller. Document the strict dataset/source/control and
  native receipt flow without adding an admitted capability row.

- [ ] **Step 4: Run the complete focused M5 verification matrix.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-regression/tests packages/epcsaft/tests/native/contracts/test_resolved_native_input_contract.py packages/epcsaft/tests/api/frontend/test_interaction_provenance.py tests/workflows/repo/test_project_structure.py -q
  uv run --no-sync python scripts/dev/validate_project.py regression
  uv run --no-sync ruff check packages/epcsaft-regression docs/pages/parameter_regression.rst scripts/dev/validation_registry.py tests/workflows/repo/test_project_structure.py
  uv run --no-sync sphinx-build -W --keep-going -b html docs docs/_build/html
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: all tests and validators pass, strict Sphinx exits zero, Ruff emits
  no findings, diff check emits no errors, and cleanup reports no task-owned
  debris.

- [ ] **Step 5: Perform independent spec and code review.**

  Request one reviewer to compare the diff with the approved spec and one
  reviewer to inspect target/control/native/persistence correctness. Apply real
  findings under a new RED test, rerun Step 4, and retain the review verdicts
  in the issue handoff.

- [ ] **Step 6: Commit the final contract checkpoint.**

  ```bash
  git add packages/epcsaft-regression docs/pages/parameter_regression.rst docs/pages/project_structure.rst scripts/dev/validation_registry.py tests/workflows/repo/test_project_structure.py
  git commit -m "refactor(regression): remove displaced problem owners"
  ```

  Expected: the checkpoint is locally committed, Task 1-6 proof is green, and
  capability admission remains delegated to the acyclic M5/M6 plans.
