# Regression Real-Data Evidence Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. Use
> `superpowers:test-driven-development` for each artifact/checker change,
> `superpowers:systematic-debugging` for any unexpected numerical or source
> failure, `chemical-engineer` for source/model interpretation, and
> `superpowers:verification-before-completion` before accepting each lane.

**Goal:** Produce two retained, checker-gated observation/model evidence
bundles: a methane fit against NIST saturation properties and an ethanol-water
constant-`k_ij` fit against Susial 2021 observed-state fugacity imbalance.

**Architecture:** Each lane owns a source snapshot, strict M3 model-input
bundle, configured M5 `TargetDataset`, native fit/evaluation receipts, exact
source/model table, metrics, plotted-data table, table-only renderer, and
schema-v1 evidence receipt. One repository checker verifies hashes, row
coverage, receipt identity, structural solve acceptance, and plot/table
consistency and emits a downstream checker receipt that hashes the evidence
receipt. M6 does not mutate runtime capability state; accepted checker receipts
flow forward to the final M5 importer.

**Tech Stack:** Python 3.9-3.13, `epcsaft`, `epcsaft-regression`, native Ceres
and CppAD receipts, CSV/JSON, SHA-256, Matplotlib, NumPy, pytest, Ruff, Sphinx,
MPLGallery, `uv`, and Git.

## Global Constraints

- Milestone ownership is M6; reuse GitHub issue #194 as the parent and create
  separate methane/NIST and ethanol-water/Susial child issues.
- Both lanes are blocked by the M5 native-problem contract and the M5 empty-set
  evidence schema. Neither lane depends on final M5 admission.
- Final M5 admission is blocked by both accepted M6 checker receipts, preserving the
  acyclic order: M5 contract -> M5 schema/reset -> M6 lanes -> final M5
  readmission.
- Methane fit rows are exactly 110, 130, 150, and 170 K. Evaluation and plots
  use all nine retained NIST rows from 100 through 180 K in 10 K increments.
- Each methane training temperature has exactly two native rows. The
  phase-equilibrium row evaluates
  `g_sat = ln(f_liquid(T, P_obs)) - ln(f_vapor(T, P_obs))` at the retained
  NIST pressure with target `0.0`, residual scale `1.0`, and weight `0.25`.
  The density row evaluates `rho_liquid_mass(T, P_obs)` with target `rho_obs`
  in `kg/m3`, residual scale exactly `rho_obs`, and weight `0.25`; a molar
  native density is multiplied by the exact resolved methane molar mass. This preserves
  the existing pure-neutral objective's equal mean-square contribution from
  the four fugacity rows and four relative-density rows; it is not an accuracy
  threshold or a direct predicted-pressure residual.
- Methane plotted pressure and density values use a separate before/after
  prediction pass through the scoped public `single_component_vle` route at
  each evaluation temperature. That pass receives no observed pressure or
  density as a target. Training-objective residuals and predicted saturation
  properties are retained in separate tables and never substituted for one
  another.
- The Susial lane consumes all 26 retained Table 6 rows at 100 kPa. It fits one
  symmetric constant `k_ij` and evaluates both component log-fugacity
  imbalances at each observed T/P/x/y state.
- For Susial component `i`, the exact modeled value is
  `g_i = log(x_i) + log(phi_i_liquid(T,P,x)) - log(y_i) -
  log(phi_i_vapor(T,P,y))`, equivalently
  `log(x_i * phi_i_liquid / (y_i * phi_i_vapor))`. The exact target is `0.0`
  for each component. Do not draw or claim a predicted `x-y` equilibrium curve.
- Report all numerical metrics, but do not invent a pass/fail model-error or
  parameter-distance threshold. Structural acceptance requires a complete
  receipt, accepted native solve, exact derivatives, finite predictions,
  preserved identity, a finite retained movement vector whose final vector
  differs from the deliberately displaced start as a whole, and final objective
  no worse than the declared start under the same problem. No individual
  parameter is required to move by a nonzero amount.
- NIST evidence proves an operational fit to the retained NIST rows; it is not
  a Gross/Sadowski parameter-reproduction claim.
- Susial's reported `k_ij = -0.0269` is contextual metadata only and is never
  an identity or tolerance oracle.
- Keep pure-ion, liquid-electrolyte, association-parameter, reactive,
  Khudaida, and all other paper/equilibrium work closed and untouched.
- A generation script writes tables/receipts; a renderer reads only retained
  tables and never imports or calls the model runtime.
- Every generated prediction bundle retains its exact source rows and renders
  observation and model series together in SVG, PNG, and PDF.

---

## Source Evidence

- Approved source spec:
  `docs/superpowers/specs/2026-07-10-m5-m6-regression-real-data-admission.md`.
- Blocking M5 contract plan:
  `docs/superpowers/plans/2026-07-10-m5-regression-traceable-native-problem-contract-plan.md`.
- Blocking/following capability plan:
  `docs/superpowers/plans/2026-07-10-m5-regression-capability-reset-and-scoped-readmission-plan.md`.
- Parent validation tracker: GitHub issue #194 under `M6 - Validation`.
- `verified`: `data/reference/pure_component/saturation_properties/methane/saturation_properties.csv`
  contains nine NIST rows at 100-180 K with pressure, saturated-liquid density,
  SI units in headers, and a complete NIST Chemistry WebBook URL on every row.
- `verified`: the fixed methane training temperatures select four of those nine
  rows; the intervening and endpoint rows make evaluation outside the training
  set visible.
- `verified`: `data/reference/regression/binary/vle/ethanol_water/100kpa.csv`
  contains 26 Susial 2021 Table 6 rows with DOI, temperature, pressure, and
  complete liquid/vapor mole fractions.
- `verified`: the local source note identifies DOI
  `10.1021/acs.jced.0c00686`, Table 6, and the contextual paper value
  `-0.0269`.
- `verified`: retained Gross 2002 Table 1 rows provide source-qualified water
  and ethanol associating pure parameters; the M3 explicit-neutral schema
  permits electrostatics to be disabled without a preset.
- `verified`: the old regression smoke plot compares parameter bars and does
  not preserve before/after observation/model predictions for either lane.
- `verified`: current M4 associating public VLE prediction is not admitted, so
  an observed-state residual is the valid binary regression observable.
- `inference`: a compact Susial input may reuse retained source-qualified pure
  definitions only if its exact association mixing and structural-zero records
  are proven for the active temperature range. The lane stops at the source
  gate if that proof cannot be retained; it does not repair or make a Gross or
  Held paper-validation bundle executable.

## Immutable Lane Definitions

### Methane/NIST

- Source rows: all nine NIST rows, 100-180 K inclusive.
- Fit rows: 110, 130, 150, and 170 K.
- Observables per temperature: saturation pressure in Pa and saturated-liquid
  mass density in kg/m3.
- Native fit rows per temperature:
  - `pure_saturation_fugacity_balance`: model
    `ln(f_liquid(T, P_obs)) - ln(f_vapor(T, P_obs))`, target `0.0`, units and
    residual scale dimensionless `1.0`, weight `0.25`;
  - `pure_liquid_density_at_pressure`: model `rho_liquid_mass(T, P_obs)`, target
    `rho_obs`, units `kg/m3`, residual scale `rho_obs`, weight `0.25`.
- Native objective:
  `0.5 * sum_rows(weight * ((model - target) / residual_scale)^2)`; with four
  rows per family this is the existing equal-family mean-square normalization.
- Fitted parameters: `Methane.m`, `Methane.sigma`, and `Methane.epsilon_k`.
- Declared start: `m=1.08`, `sigma=3.555744`, `epsilon_k=157.5315`.
- Bounds: `m=[0.5, 3.5]`, `sigma=[2.0, 5.0] Angstrom`, and
  `epsilon_k=[50.0, 400.0] K`.
- Model configuration: M3 schema version 1, complete explicit neutral
  formulation, electrostatics disabled, source IDs naming the retained
  hydrocarbon parameter source.
- Plot: two panels versus temperature; observed/before/after saturation
  pressure (log pressure axis) and saturated-liquid density.

### Ethanol-water/Susial

- Source rows: all 26 Table 6 records at exactly 100000 Pa.
- Observed state: each row's exact T, P, liquid x, and vapor y in component
  order `(Ethanol, H2O)`.
- Fitted parameter: symmetric constant `Ethanol:H2O.k_ij`.
- Declared start and bounds: `k_ij=0.0`, `[-0.15, 0.10]`.
- Weight and residual scale: explicit dimensionless `1.0` for every source row;
  these are problem-definition fields, not scientific accuracy thresholds.
- Model configuration: M3 schema version 1, complete explicit neutral
  associating formulation with electrostatics disabled and exact source IDs for
  every pure/association/mixing record.
- Modeled values: component log-fugacity imbalances before and after fitting;
  for component `i`, compute
  `log(x_i) + log(phi_i_liquid) - log(y_i) - log(phi_i_vapor)` at the exact
  observed T/P/x/y, with target exactly `0.0` for both components at every
  measured state.
- Plot: top panel shows measured liquid and vapor ethanol mole fractions versus
  source row order as source context only; bottom panel shows zero target plus
  before/after imbalance for both components versus measured liquid ethanol
  fraction. No model composition curve is present.

## Test Complete And Metrics

- The methane source snapshot contains exactly nine rows and exact source-file
  values; the fit receipt names exactly four temperature rows and eight
  observable target rows.
- The eight methane target rows are exactly four observed-pressure
  liquid/vapor log-fugacity-balance rows and four observed-pressure liquid-
  density rows with the fixed weights/scales above. Mutation tests reject a
  direct predicted-`P_sat` target, unit drift, any other scale, or any other
  weight.
- The methane evaluation table contains exactly 18 rows: two observables for
  each of nine temperatures, with source, before, and after values from
  independent `single_component_vle` prediction calls. A separate objective
  diagnostics table retains the eight training rows' raw and weighted
  residuals.
- Methane metrics report fit/evaluation partitions separately for pressure and
  density, plus parameter movement and native objective diagnostics.
- The Susial source snapshot contains exactly 26 rows and exact source-file
  values; the evaluation table contains exactly 52 component residual rows.
- Susial metrics report before/after imbalance summaries by component and
  native objective/parameter movement without comparing the fitted parameter
  to `-0.0269` as a pass condition.
- Each lane's model table, plotted-data table, and renderer series join exactly
  on stable row/observable/component IDs.
- Each lane's evidence receipt hashes only upstream source, model, metrics,
  plotted data, native receipt, configuration, and generator inputs;
  model/problem fingerprints agree with every result row. The checker then
  hashes that immutable evidence receipt plus the subsequently rendered plots
  and other checked artifacts into a separate checker receipt. The evidence
  receipt never hashes or references the
  checker receipt, so the DAG is
  `artifacts -> evidence_receipt.json -> checker_receipt.json -> M5 importer`.
- Checker mutation tests catch missing rows, duplicates, reordered component
  identity, unit/basis changes, stale hashes, mismatched fingerprints,
  nonfinite values, failed native status, missing derivatives, missing plot
  series, and a renderer/model call.
- Both lane checkers, focused M5 consumer tests, strict docs, Ruff, MPLGallery,
  diff checks, and cleanup pass.

## Outcome Proof

**Intent:** Retain enough independent observations and exact native output to
show that two configured regression workflows consume the stated real data and
produce reproducible before/after model values.

**Current Behavior:** Existing tests exercise useful native components, but
capability evidence is backend-derived and retained plots compare parameter
bars rather than the actual observations with model values/residuals.

**Expected Outcome:** Each lane is reproducible from retained source/input
files, executes through the configured M5 native problem, retains exact
receipts/tables/metrics, renders a table-only observation/model plot, and passes
a strict hash/identity/coverage checker.

**Target Output:** A `regression_real_data` analysis with metadata/docs, two
figure-owned source/script/result bundles, two three-format plots, exact
plotted-data CSVs, native/evidence/checker receipts, one strict checker and its
mutation tests, MPLGallery records, and M6 handoff receipts for M5.

**Owner:** M6 owns source snapshots, model tables, metrics, plots, freshness,
and checker receipts; M5 owns configured regression behavior and later
capability admission; M3 owns resolved model-input fingerprints.

**Interface:** `Regression.fit`, `Regression.evaluate(result.problem,
parameter_values=...)`,
`FitResult.receipt`, figure-local `generate_data.py` and `render_figure.py`, and
`scripts/validation/check_regression_real_data_evidence.py --lane <lane>
--json --require-complete`.

**Cutover:** These two retained observation/model bundles replace the old
parameter-bar-only regression artifacts as admission evidence; the old smoke
plots may remain only if clearly labeled as non-admission smoke context.

**Replaced Path:** Do not use `fit_pure_neutral`, `fit_binary_pair`, the old
smoke-only Susial subset, model-calling plot tests, or parameter-distance bars
as the evidence oracle.

**Evidence:** Exact NIST and Susial source snapshots, source manifests, strict
M3 configuration receipts, M5 native problem/result receipts, before/after
model tables, metrics, plotted-data tables, SVG/PNG/PDF figures, strict checker
JSON, MPLGallery validation, focused tests, docs, Ruff, diff review, and
cleanup output.

**Acceptance Proof:** The methane checker verifies 9/4/18 source-fit-model
counts and exact fingerprints; the Susial checker verifies 26/52 source-model
counts, target-zero residual semantics, and no predicted composition series;
both verify structural native acceptance, plot/table identity, and all hashes.

**Stop Criteria:** Stop a lane on missing or conflicting source input, an
unsupported model-record domain, a failed M3 configuration receipt, failed
native solve, incomplete derivative columns, row/fingerprint mismatch,
nonfinite prediction, stale artifact, model import in the renderer, or an
attempt to add a numerical threshold without approved source evidence.

**Avoid:** Do not invent parameters, source locators, hashes, uncertainty
limits, or fit-quality thresholds; do not equate NIST fitting with Gross
reproduction, equate fitted `k_ij` with the paper value, or label a residual
plot as a VLE curve.

**Risk:** The exact source-qualified Susial model basis may expose a missing
association/mixing record or the native fit may fail. Either outcome remains a
specific M6 blocker and prevents final M5 admission; it does not authorize a
fallback input or a paper-validation repair in this plan.

## Implementation Boundaries

**Files To Create:** `analyses/package_validation/regression_real_data` with
README/metadata/tests; methane and Susial figure-owned `source`, `scripts`, and
`results` files; `scripts/validation/check_regression_real_data_evidence.py`;
and `tests/native/contracts/test_regression_real_data_evidence_gate.py`.

**Files To Modify:** `.mplgallery/manifest.yaml`, project-structure tests,
validation registry, validation documentation, and the old package plot smoke
test only to remove its admission implication after the new evidence exists.

**Files To Avoid:** All paper-validation generated results and parameters, M5
capability registry, provider/equilibrium implementation, electrolyte/reactive
inputs, Khudaida/Gross repair tests, release metadata, stashes, and remote refs.

**Source Of Truth:** The retained NIST/Susial reference CSVs, exact local
primary-source extracts cited by input manifests, accepted M3 configuration
receipts, M5 native receipts, generated source/model tables, and strict checker
receipts.

**Read Path:** Copy and verify source rows, load one strict model input, compile
one configured `TargetDataset`, fit natively, evaluate before/after through the
same problem, write exact tables/receipts, render from tables, then check every
identity/hash/series.

**Write Path:** Figure-local generators write canonical CSV/JSON results and
evidence receipts; renderers read only those tables and write SVG/PNG/PDF;
each evidence receipt hashes only artifacts already present. Checkers read that
receipt and its upstream artifacts without mutation and write a canonical
checker receipt only when all gates pass; the checker receipt hashes the
evidence receipt, never the reverse.

**Integration Points:** M3 model configuration/receipt, M5 strict targets and
native receipts, retained reference data, Matplotlib/MPLGallery, validation
registry, project structure, issue #194 children, and final M5 importer.

**Migration Or Cutover:** Establish the shared analysis/checker contract, land
and review methane, land and review Susial, then publish both accepted receipts
to the final M5 importer in the one-way order
`artifacts -> evidence -> checker -> importer` without changing capability
state in M6.

**Replaced Path Handling:** Remove admission references to the old parameter
bar plots and smoke subset; do not delete useful smoke artifacts unless their
only role was the displaced admission claim. No redirect script is added.

**Acceptance Proof Gate:** M6 is complete only when both current lane checker
commands pass, figures match plotted-data tables, exact source/model/problem
fingerprints and hashes agree, excluded claim tests pass, and independent
scientific/code reviews find no unresolved real issue.

## Decision Ledger

| Decision | Evidence | Selected answer | Consequence | Deferred? | Owner |
| --- | --- | --- | --- | --- | --- |
| Tracker | Existing roadmap | Reuse #194 with two child issues | Each lane is independently reviewable. | No | M6 |
| Dependency | Milestone policy | M5 contract/schema before M6; final M5 after both lanes | No dependency cycle. | No | M5/M6 |
| Pure case | Approved execution selection | Methane; fit 110/130/150/170 K, evaluate 100-180 K | Training and nontraining rows are visible. | No | M6 |
| Pure claim | NIST source is not the original parameter paper | Operational native fit to NIST rows | No Gross reproduction claim. | No | M6 |
| Binary rows | Retained Table 6 source | All 26 rows at 100 kPa | Smoke subset cannot admit the workflow. | No | M6 |
| Binary observable | M4 associating prediction route remains closed | Observed-state component log-fugacity imbalance with target zero | No false `x-y` prediction curve. | No | M5/M6 |
| Paper parameter | Pure basis differs | `-0.0269` is context only | No parameter identity tolerance. | No | M6 |
| Accuracy | No approved source-backed cutoff | Report metrics; gate only structural execution facts | No invented scientific threshold. | No | M6 |
| Input basis | Traceable compact sources required | Stop if any active pure/association/mixing record is unproven | No incomplete bundle becomes executable. | No | M6 |
| Electrolytes | Separate future evidence | Excluded | Khudaida and electrolyte regression remain closed. | No | M5/M6 |

## Execution Dependency Graph

```text
M5 native contract + M5 evidence schema/reset
                       |
                       v
             Task 1 shared source/checker shell
                    /             \
                   v               v
      Task 2 methane/NIST    Task 3 Susial residual
                   \               /
                    v             v
                Task 4 combined M6 proof
                       |
                       v
             final M5 two-scope importer
```

### Task 1: Establish the analysis, source-input gates, and strict checker schema

**Use Cases:**

- Each lane has one immutable source snapshot and one complete explicit M3
  model input before any prediction runs.
- Missing association/mixing provenance blocks only the Susial lane and is
  visible in checker evidence.
- Checker mutation tests validate row coverage, identities, hashes, receipts,
  and plot series without computing model predictions.
- The new analysis replaces parameter-bar smoke evidence with a durable
  table/receipt contract.

**Files:**

- Create: `analyses/package_validation/regression_real_data/README.md`
- Create: `analyses/package_validation/regression_real_data/analysis.yaml`
- Create: `analyses/package_validation/regression_real_data/tests/test_regression_real_data_sources.py`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/source/nist_methane_saturation.csv`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/source/source_manifest.json`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/source/model_input/model_configuration.json`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/source/model_input/parameter_set.json`
- Create: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/source/susial_2021_table6_100kpa.csv`
- Create: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/source/source_manifest.json`
- Create after all records pass the source gate: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/source/model_input/model_configuration.json`
- Create after all records pass the source gate: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/source/model_input/parameter_set.json`
- Create: `scripts/validation/check_regression_real_data_evidence.py`
- Create: `tests/native/contracts/test_regression_real_data_evidence_gate.py`
- Modify: `tests/workflows/repo/test_project_structure.py`

**Interfaces:**

- Consumes: the two retained reference CSVs, retained primary-source rows, M3
  schema-v1 explicit-neutral configuration, and M5 evidence-receipt field list.
- Produces checker lane IDs `methane_nist` and `ethanol_water_susial` and the CLI
  `--lane`, `--json`, and `--require-complete` flags.
- Produces source manifests with exact source path, citation/locator, units,
  copied-row SHA-256, model-record sources/domains, and claim exclusions.

- [ ] **Step 1: Write RED source-copy, configuration, and checker-mutation
  tests.**

  Assert the methane copy equals all nine reference rows and the Susial copy
  equals all 26 reference rows byte-for-byte after canonical newline handling.
  Assert M3 loads each complete bundle, preserves source IDs, and reports
  electrostatics disabled. For Susial, require explicit pure/association/mixing
  records and valid domains for 351.4-372.3 K. Create checker fixtures and
  mutate row count, row ID, unit, basis, hash, fingerprint, status, derivative
  field, and plot series.

- [ ] **Step 2: Run RED source/checker tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/regression_real_data/tests/test_regression_real_data_sources.py tests/native/contracts/test_regression_real_data_evidence_gate.py tests/workflows/repo/test_project_structure.py -q
  ```

  Expected: tests fail because the analysis, source snapshots, strict input
  bundles, and checker do not exist.

- [ ] **Step 3: Retain exact source snapshots and complete model inputs.**

  Copy NIST/Susial rows without changing numerical values. Build methane from
  the retained hydrocarbon source and M3 explicit-neutral fixture shape. Build
  the Susial subset only from source-qualified water/ethanol pure and
  association/mixing records, with each active record/domain in the manifest.
  If any Susial record cannot be proven, retain the failed manifest/status,
  omit the executable input files, and stop the Susial branch without changing
  the methane branch.

- [ ] **Step 4: Implement read-only checker parsing and schema checks.**

  The checker must validate exact lane IDs, required file set, canonical IDs,
  hashes, receipt schema/fingerprint joins, finite values, expected counts,
  plot-data series, and renderer source imports. The generator-owned
  `evidence_receipt.json` hashes only upstream artifacts and contains no checker
  path/hash. The checker writes `checker_receipt.json` only after complete
  acceptance; that output includes the evidence-receipt path/hash plus every
  checked path/hash. Mutation tests reject any reverse checker reference in the
  evidence receipt.

- [ ] **Step 5: Run GREEN source/checker tests.**

  Run the Step 2 command again. Expected: source and checker mutation tests pass;
  a complete Susial input either loads with exact evidence or reports one
  explicit source blocker and remains non-executable.

- [ ] **Step 6: Commit the shared gate checkpoint.**

  ```bash
  git add analyses/package_validation/regression_real_data scripts/validation/check_regression_real_data_evidence.py tests/native/contracts/test_regression_real_data_evidence_gate.py tests/workflows/repo/test_project_structure.py
  git commit -m "test(validation): define regression evidence gates"
  ```

### Task 2: Generate, render, and accept the methane/NIST lane

**Use Cases:**

- The configured native fit consumes exactly four declared NIST temperatures
  and both observables.
- Before/after model evaluation covers all nine retained temperatures and keeps
  fit/evaluation membership visible.
- A two-panel retained plot shows NIST observations with both model states.
- The strict checker produces the methane acceptance receipt for later M5
  import.

**Files:**

- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/scripts/generate_data.py`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/scripts/render_figure.py`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/native_fit_receipt.json`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/training_objective_table.csv`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/source_model_table.csv`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/metrics.json`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/plotted_data.csv`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/methane_nist_fit.svg`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/methane_nist_fit.png`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/methane_nist_fit.pdf`
- Create: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/evidence_receipt.json`
- Create after checker acceptance: `analyses/package_validation/regression_real_data/figures/methane_nist_fit/results/checker_receipt.json`
- Create: `analyses/package_validation/regression_real_data/tests/test_methane_nist_lane.py`
- Modify: `.mplgallery/manifest.yaml`

**Interfaces:**

- Consumes: Task 1 methane input, M5 `Regression.fit/evaluate`, fixed starts and
  bounds, and explicit `RegressionControls` from the M5 contract.
- Compiles exactly four
  `TargetFamily.PURE_SATURATION_FUGACITY_BALANCE` rows and four
  `TargetFamily.PURE_LIQUID_DENSITY_AT_PRESSURE` rows. Each fugacity row uses
  model `ln(f_liquid(T, P_obs)) - ln(f_vapor(T, P_obs))`, target/scale
  `0.0/1.0`, and weight `0.25`; each density row uses model
  `rho_liquid_mass(T, P_obs)`, target/scale `rho_obs/rho_obs` in `kg/m3`, and weight
  `0.25`.
- Produces `training_objective_table.csv` with the eight exact target/model/raw-
  residual/weighted-residual records at both start and fit values.
- Produces exactly 18 `source_model_table.csv` rows keyed by
  `(source_row_id, observable)` from independent before/after
  `single_component_vle` predictions, and plotted series keyed by
  `(observable, source|before|after)`.
- Produces evidence ID `pure_neutral_methane_nist_saturation_v1`.

- [ ] **Step 1: Write RED generator, table, renderer, and checker tests.**

  Require training temperatures `(110.0, 130.0, 150.0, 170.0)`, evaluation
  temperatures `(100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0,
  180.0)`, exact starts/bounds, eight fit target rows, 18 evaluation rows, one
  accepted native receipt, a finite retained movement vector, a final parameter
  vector different from the deliberately displaced start as a whole, and final
  objective not greater than initial objective. Assert the four fugacity rows'
  exact observed-pressure formula/zero target/scale `1.0`/weight `0.25`, the
  four density rows' exact model/observed target/`rho_obs` scale/weight `0.25`,
  and exact recomputation of every raw and weighted residual. Mutate each row
  to direct predicted pressure, weight `1.0`, or a unit-based constant density
  scale and require a specific failure. Assert the 18 evaluation rows come from
  `single_component_vle(T)` calls that receive no NIST P/rho target. Do not
  require every selected parameter to move nonzero. Require the renderer to
  import no ePC-SAFT module and its plotted values to equal the table.

- [ ] **Step 2: Run the RED methane tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/regression_real_data/tests/test_methane_nist_lane.py tests/native/contracts/test_regression_real_data_evidence_gate.py -q
  ```

  Expected: tests fail because no methane generator/results/plot exist.

- [ ] **Step 3: Implement generation through the configured M5 workflow.**

  Load `Mixture.from_folder`; construct the four strict observed-pressure
  fugacity-balance rows and four observed-pressure density rows with the exact
  target, units, weights, and scales above; then call `Regression.fit`. Use
  `Regression.evaluate(result.problem, parameter_values=...)` only for the
  eight-row objective diagnostics at start and fitted values. Separately run
  the scoped public `single_component_vle` prediction at each of the nine
  temperatures for the start and fitted parameter vectors without supplying
  NIST pressure/density targets. Write canonical native receipt, training-
  objective table, source/model prediction table, metrics, and plot-data files
  with identical model/problem fingerprints on every row.

- [ ] **Step 4: Implement the table-only two-panel renderer.**

  Read only `plotted_data.csv`; render NIST observations, before fit, and after
  fit on pressure/density panels; label the four training temperatures without
  hiding the five evaluation-only temperatures; save SVG/PNG/PDF and close the
  figure.

- [ ] **Step 5: Generate, render, and run the strict methane checker.**

  Run:

  ```bash
  uv run --no-sync python analyses/package_validation/regression_real_data/figures/methane_nist_fit/scripts/generate_data.py
  uv run --no-sync python analyses/package_validation/regression_real_data/figures/methane_nist_fit/scripts/render_figure.py
  uv run --no-sync python scripts/validation/check_regression_real_data_evidence.py --lane methane_nist --json --require-complete
  uv run --no-sync python run_pytest.py analyses/package_validation/regression_real_data/tests/test_methane_nist_lane.py tests/native/contracts/test_regression_real_data_evidence_gate.py -q
  ```

  Expected: generator/renderer exit zero; checker reports 9 source rows, 4 fit
  temperatures, 18 model rows, matching hashes/fingerprints, accepted structural
  solve facts, and all tests pass.

- [ ] **Step 6: Review the retained plot and refactor without changing data.**

  Inspect the SVG/PNG axes, units, legends, observation/model distinctions, and
  training markers. Move shared CSV parsing only if duplicated; regenerate and
  prove `source_model_table.csv` and `plotted_data.csv` are byte-identical.

- [ ] **Step 7: Commit the methane checkpoint.**

  ```bash
  git add analyses/package_validation/regression_real_data/figures/methane_nist_fit analyses/package_validation/regression_real_data/tests/test_methane_nist_lane.py .mplgallery/manifest.yaml
  git commit -m "test(validation): retain methane NIST regression evidence"
  ```

### Task 3: Generate, render, and accept the ethanol-water/Susial residual lane

**Use Cases:**

- One configured native fit consumes all 26 observed T/P/x/y rows and one
  symmetric constant `k_ij`.
- Before/after evaluation preserves 52 component residual rows with observed
  target zero.
- The retained figure shows measured composition context and model residuals
  without implying a predicted composition curve.
- The strict checker produces the Susial acceptance receipt only from a
  complete source-qualified input.

**Files:**

- Create after Task 1 source closure: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/scripts/generate_data.py`
- Create after Task 1 source closure: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/scripts/render_figure.py`
- Create after successful generation: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/native_fit_receipt.json`
- Create after successful generation: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/source_model_table.csv`
- Create after successful generation: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/metrics.json`
- Create after successful generation: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/plotted_data.csv`
- Create after successful rendering: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/ethanol_water_susial_residual.svg`
- Create after successful rendering: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/ethanol_water_susial_residual.png`
- Create after successful rendering: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/ethanol_water_susial_residual.pdf`
- Create after successful generation: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/evidence_receipt.json`
- Create after checker acceptance: `analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/results/checker_receipt.json`
- Create: `analyses/package_validation/regression_real_data/tests/test_susial_residual_lane.py`
- Modify: `.mplgallery/manifest.yaml`

**Interfaces:**

- Consumes: Task 1 source-qualified Susial input, all 26 source rows, M5
  `Regression.fit/evaluate`, start `0.0`, bounds `[-0.15, 0.10]`, and explicit
  controls.
- Produces exactly 52 model rows keyed by `(source_row_id, component)` with
  `target_log_fugacity_imbalance == 0.0` and
  `model_log_fugacity_imbalance = log(x_i) + log(phi_i_liquid) - log(y_i) -
  log(phi_i_vapor)` for the named component.
- Produces evidence ID
  `binary_constant_kij_ethanol_water_susial_100kpa_v1`.

- [ ] **Step 1: Write RED all-row, residual-definition, renderer, and checker
  tests.**

  Assert 26 unique source IDs, 52 component rows, component order
  `(Ethanol, H2O)`, exact observed compositions, target zero, explicit
  weight/scale `1.0`, and, for every component row, exact recomputation of
  `log(x_i) + log(phi_i_liquid) - log(y_i) - log(phi_i_vapor)` from the retained
  native phase diagnostics. Require a constant symmetric fitted parameter,
  accepted receipt, a finite retained movement vector whose final vector differs
  from the deliberately displaced start as a whole, final objective not greater
  than initial, and exact model/problem fingerprints; do not add a separate
  per-parameter movement threshold. Assert the paper value appears only in
  contextual metadata and no series is named predicted `x`, predicted `y`, VLE
  curve, bubble, or dew.

- [ ] **Step 2: Run the RED Susial tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/regression_real_data/tests/test_susial_residual_lane.py tests/native/contracts/test_regression_real_data_evidence_gate.py -q
  ```

  Expected: tests fail because the lane has no generator/results/plot; if Task
  1 retained a source blocker, the test must report that blocker and this task
  stops before model execution.

- [ ] **Step 3: Implement all-row configured generation and observed-state
  evaluation.**

  Load the strict model input, convert every source row into one binary-VLE
  `TargetRow`, call `Regression.fit` for the single parameter, and evaluate the
  same compiled problem at start/final values. Write 52 rows with target zero,
  before/after values from the exact component formula, retained
  `log(phi_i_liquid)`/`log(phi_i_vapor)` terms, source T/P/x/y, receipt IDs, and
  fingerprints. Retain metrics by component and overall without a numerical
  acceptance cutoff.

- [ ] **Step 4: Implement the table-only composition-context/residual
  renderer.**

  Top panel: plot measured liquid and vapor ethanol mole fractions versus
  source row order, labeled `measured source context`. Bottom panel: plot target
  zero and before/after imbalance for both components versus measured liquid
  ethanol fraction. Read only `plotted_data.csv`, use no model import, and save
  SVG/PNG/PDF.

- [ ] **Step 5: Generate, render, and run the strict Susial checker.**

  Run:

  ```bash
  uv run --no-sync python analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/scripts/generate_data.py
  uv run --no-sync python analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual/scripts/render_figure.py
  uv run --no-sync python scripts/validation/check_regression_real_data_evidence.py --lane ethanol_water_susial --json --require-complete
  uv run --no-sync python run_pytest.py analyses/package_validation/regression_real_data/tests/test_susial_residual_lane.py tests/native/contracts/test_regression_real_data_evidence_gate.py -q
  ```

  Expected: generator/renderer exit zero; checker reports 26 source rows, 52
  component model rows, exact per-component target-zero log-fugacity formula,
  exact hashes/fingerprints, no predicted-composition series, accepted
  structural solve facts, and all tests pass.

- [ ] **Step 6: Review scientific labeling and refactor without changing
  tables.**

  Inspect the plot and captions for observed-state residual language, component
  identity, dimensionless axes, paper-value context, and absence of a predicted
  equilibrium claim. Regenerate and prove both retained CSVs are byte-identical
  after any renderer refactor.

- [ ] **Step 7: Commit the Susial checkpoint.**

  ```bash
  git add analyses/package_validation/regression_real_data/figures/ethanol_water_susial_residual analyses/package_validation/regression_real_data/tests/test_susial_residual_lane.py .mplgallery/manifest.yaml
  git commit -m "test(validation): retain Susial residual fit evidence"
  ```

### Task 4: Close the combined M6 gate and hand accepted receipts to M5

**Use Cases:**

- A single validation command verifies both current lane bundles and their
  freshness without changing capability state.
- Docs state the exact operational claims and exclusions for both plots.
- Independent scientific review checks sources, units, residual meaning, and
  figure labeling; code review checks receipt/hash/checker behavior.
- Final M6 checker receipts, each linked one-way to its evidence receipt, are
  ready for the separate final M5 importer.

**Files:**

- Modify: `analyses/package_validation/regression_real_data/README.md`
- Modify: `analyses/package_validation/regression_real_data/analysis.yaml`
- Modify: `scripts/dev/validation_registry.py`
- Modify: `docs/pages/development_workflows.rst`
- Modify: `docs/pages/parameter_regression.rst`
- Modify: `analyses/package_validation/package_plot_smokes/tests/plots/test_regression_plot_outputs.py`
- Modify: `tests/workflows/repo/test_project_structure.py`

**Interfaces:**

- Consumes: both accepted checker receipts and the Task 1-3 retained bundles.
- Produces a validation-registry lane that executes both strict checker
  commands and names the two checker-receipt paths consumed by final M5; each
  checker receipt names/hashes its upstream evidence receipt.

- [ ] **Step 1: Write RED combined-gate, docs, and displaced-evidence tests.**

  Require analysis metadata to list both IDs, commands, sources, result paths,
  exact claim boundaries, and no capability mutation. Require old plot smoke
  tests to describe smoke-only context or stop generating displaced parameter
  bars; require user docs to link the new evidence without a broad accuracy or
  equilibrium prediction claim.

- [ ] **Step 2: Run RED combined tests.**

  Run:

  ```bash
  uv run --no-sync python run_pytest.py analyses/package_validation/regression_real_data/tests tests/native/contracts/test_regression_real_data_evidence_gate.py analyses/package_validation/package_plot_smokes/tests/plots/test_regression_plot_outputs.py tests/workflows/repo/test_project_structure.py -q
  ```

  Expected: failures identify incomplete metadata/docs or the old admission
  implication.

- [ ] **Step 3: Update metadata/docs/registry and retire displaced admission
  language.**

  Keep useful smoke checks if they remain developer-useful, but label them
  non-admission and remove parameter-bar output from the validation oracle. Add
  exact M6 checker commands and handoff paths; state that runtime capability
  remains an M5 decision.

- [ ] **Step 4: Run complete M6 verification.**

  Run:

  ```bash
  uv run --no-sync python scripts/validation/check_regression_real_data_evidence.py --lane methane_nist --json --require-complete
  uv run --no-sync python scripts/validation/check_regression_real_data_evidence.py --lane ethanol_water_susial --json --require-complete
  uv run --no-sync python run_pytest.py analyses/package_validation/regression_real_data/tests tests/native/contracts/test_regression_real_data_evidence_gate.py packages/epcsaft-regression/tests/api/test_workflow.py packages/epcsaft-regression/tests/native/test_problem_receipt.py tests/workflows/repo/test_project_structure.py -q
  uv run --no-sync python scripts/dev/validate_project.py regression
  uv run --no-sync ruff check analyses/package_validation/regression_real_data scripts/validation/check_regression_real_data_evidence.py tests/native/contracts/test_regression_real_data_evidence_gate.py
  uv run --no-sync sphinx-build -W --keep-going -b html docs docs/_build/html
  git diff --check
  bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
  ```

  Expected: both checkers report accepted; focused tests, registry validation,
  strict docs, and Ruff pass; diff and cleanup are clean.

- [ ] **Step 5: Perform independent scientific and code review.**

  Scientific reviewer verifies every source row, unit, fit/evaluation
  partition, input source/domain, residual definition, metric interpretation,
  and plot label. Code reviewer verifies no model call in renderers, canonical
  hashes/receipts, mutation coverage, and no M5 capability change. Fix real
  findings under a RED test and rerun Step 4.

- [ ] **Step 6: Commit the M6 closeout checkpoint.**

  ```bash
  git add analyses/package_validation/regression_real_data analyses/package_validation/package_plot_smokes/tests/plots/test_regression_plot_outputs.py .mplgallery/manifest.yaml scripts/validation/check_regression_real_data_evidence.py tests/native/contracts/test_regression_real_data_evidence_gate.py scripts/dev/validation_registry.py docs/pages/development_workflows.rst docs/pages/parameter_regression.rst tests/workflows/repo/test_project_structure.py
  git commit -m "docs(validation): close regression real-data evidence gates"
  ```

  Expected: both checker/evidence receipt chains are current and the checker
  receipts are ready for the final M5 importer; M6 itself has not changed
  `epcsaft_regression.capabilities()`.
