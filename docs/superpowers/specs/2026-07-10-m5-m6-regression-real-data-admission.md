# M5/M6 Regression Real-Data Admission

Milestones: `M5 - Regression`, `M6 - Validation`
Packages: `packages/epcsaft-regression`, retained package-validation analyses
Issues: [#193](https://github.com/ePC-SAFT/ePC-SAFT/issues/193), [#194](https://github.com/ePC-SAFT/ePC-SAFT/issues/194)
Status: `draft for review`
Last reviewed: `2026-07-10`

## Context

This spec replaces Task 12 of the repository-wide program defined by:

- [2026-07-09 program spec](2026-07-09-m3-core-repository-truth-and-scientific-integrity-program.md)
- [2026-07-09 implementation plan](../plans/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program-plan.md)

The repository currently has useful Ceres component tests and retained source
data, but capability rows can become active from backend availability and
synthetic recovery tests. For this private workspace, admission means a local
workflow is reproducibly exercised through the configured API and native
problem using retained real observations. It does not mean a universal model
accuracy claim or release certification.

M5 owns regression behavior and capability state. M6 owns exact source/model
tables, plots, checkers, and retained run receipts. Because one GitHub issue can
belong to only one milestone, this cross-workstream spec intentionally produces
separate M5 and M6 plans/issues.

## Verified Current Behavior

- `epcsaft_regression.capabilities()` marks pure-neutral, constant binary
  `k_ij`, and liquid-electrolyte Born routes as production whenever Ceres and
  provider derivative availability are true; complete independent data
  evidence is not part of that decision.
- current pure-neutral tests use retained NIST saturation-property rows, but
  retained plots compare fitted parameter bars with reference parameter bars
  rather than observations with model values;
- `data/reference/regression/binary/vle/ethanol_water/100kpa.csv` retains 26
  Susial 2021 Table 6 rows with DOI, temperature, pressure, and full liquid and
  vapor mole fractions;
- the current ethanol/water plot compares the start, fitted `k_ij`, and the
  paper's reported `-0.0269` as bars; it does not plot the native residual
  prediction over the observed rows;
- the local source notes state that repository pure parameters are not
  byte-identical to the paper's parameter basis, so equality to `-0.0269` is
  not a valid acceptance condition; and
- pure-ion and liquid-electrolyte regressions remain based on synthetic or
  self-recovery evidence for capability purposes.

Open issue #193 is the M5 parent for contract and capability behavior. Open
issue #194 is the M6 parent for executable literature and capability evidence.
Closed issues [#67](https://github.com/ePC-SAFT/ePC-SAFT/issues/67),
[#95](https://github.com/ePC-SAFT/ePC-SAFT/issues/95), and
[#119](https://github.com/ePC-SAFT/ePC-SAFT/issues/119) are historical evidence
efforts, not duplicates to reopen. Issue
[#338](https://github.com/ePC-SAFT/ePC-SAFT/issues/338) is a separate future
Khudaida electrolyte-fit problem and does not admit an electrolyte regression
family here.

## Goals

- Reset regression capability state to no admitted families before rebuilding
  evidence.
- Define a complete evidence record that mechanically joins one configured API,
  native Ceres receipt, derivative path, retained source rows, exact model
  output table, metrics, checker, and observation/model plot.
- Re-admit a narrowly scoped pure-neutral fit using retained NIST saturation
  properties.
- Re-admit a narrowly scoped constant binary `k_ij` fit using Susial 2021
  ethanol/water VLE rows.
- Preserve synthetic recovery tests as component evidence without letting them
  activate capability state.
- Report model fit quality without inventing accuracy thresholds or equating a
  repository fit with a paper's differently parameterized fit.
- Keep pure-ion, liquid-electrolyte, association-parameter, and reactive
  regression closed until separate real-data evidence exists.

## Non-Goals

- No claim that NIST rows reproduce the original Gross/Sadowski parameter fit.
- No requirement that the Susial fit equal the paper's reported `k_ij`.
- No associating public VLE-curve solve through M4.
- No Khudaida parameter regression or electrolyte LLE repair.
- No arbitrary AAD, RMS, parameter-distance, or holdout threshold introduced
  only to make a gate pass.
- No release or broad end-user accuracy claim.
- No data download during the proof run; retained source rows are the input.

## Alternatives Considered

### Keep backend-gated capability rows and improve plot captions

This preserves current behavior but does not join source observations to the
actual native problem. A caption cannot prove which controls and rows Ceres
used.

### Require full paper reproduction before any regression workflow is usable

This provides strong paper-specific validation but conflates optimizer
correctness with reproducing a parameterization, source basis, and equilibrium
route that may differ from the repository model.

### Admit narrowly scoped workflows from complete retained evidence

This is selected. The capability statement is limited to the exact target,
parameter, source, formulation, and API scope proven locally. Model-error
metrics are reported separately from workflow correctness.

## Selected Design

### M5 capability reset and evidence contract

M5 begins with an empty admitted regression-family set. Backend compilation,
target-kind registration, derivative support, and optimizer support remain
separate facts.

One regression family can be marked locally validated only when its evidence
record contains:

- package and workflow owner;
- configured `Regression(mixture)` entry point;
- supported parameter and target families;
- exact model-input and native-problem receipt fingerprints;
- Ceres and derivative ownership;
- collected proof node or strict checker;
- retained independent source-table identity;
- retained model-output table, metrics, and observation/model plot; and
- exact scope and exclusions.

An incomplete record is rejected by a capability contract test. Capability
state is authored by M5, not inferred from an analysis directory or Ceres
availability.

### Pure-neutral NIST lane

The first lane fits neutral nonassociating `m`, `sigma`, and `epsilon/k` from
retained saturation pressure and saturated-liquid-density rows for a selected
hydrocarbon case. It uses deliberately displaced valid starts, declared bounds,
typed target rows, and one exact neutral model configuration.

The retained evidence includes:

- all source rows and their NIST source URLs;
- the exact training/evaluation row partition, if a partition is used;
- the native problem/result receipt;
- before/after predictions for saturation pressure and liquid density at every
  retained evaluation temperature;
- per-observable residual metrics and parameter movement; and
- plots of observed and before/after model values versus temperature.

Gross/Sadowski or workbook parameters may be plotted as context, but closeness
to those parameters is not the acceptance oracle. The admitted statement is
that this native configured fit consumes the specified NIST rows correctly.

### Susial 2021 constant-`k_ij` lane

The second lane fits one symmetric constant `k_ij` for ethanol/water from the
retained 100 kPa Susial rows using an exact source-qualified pure-parameter and
model-configuration basis.

The M5 residual is evaluated at the observed temperature, pressure, liquid
composition, and vapor composition. Until an associating M4 VLE prediction
route is independently admitted, the retained model quantity is the component
log-fugacity equilibrium imbalance whose experimental target is zero. The
evidence therefore plots:

- the retained liquid and vapor composition rows as source context; and
- target zero against native before/after log-fugacity imbalance for each
  component over the measured composition grid.

This is an observation/model comparison for the residual actually fitted. It
does not pretend to be a predicted `x-y` curve. A future `x-y` prediction plot
is an M4-dependent evidence issue.

The paper's `-0.0269` value is contextual metadata only because the pure input
basis differs. The checker must not require identity or choose a tolerance to
force agreement.

### Structural versus numerical acceptance

Workflow admission requires a complete native receipt, accepted Ceres status,
supported exact derivatives, preserved row/source identity, finite before and
after predictions, and deliberate parameter movement. The final objective must
be no worse than the declared start under the same native problem.

Numerical accuracy metrics are always retained. They become a pass/fail gate
only when a source uncertainty, published tolerance, or separately approved
validation requirement justifies the threshold. Otherwise the capability
scope states that fitting executes reproducibly, not that the model is accurate
for all related systems.

## Package And Milestone Ownership

- M5 / `packages/epcsaft-regression` owns capability reset, evidence-record
  validation, configured workflow, and native receipt requirements.
- M6 owns retained source copies, source/model tables, plots, metrics, checker,
  and freshness rules.
- M3 owns the exact model-input fingerprint used by each lane.
- M4 owns any later full equilibrium prediction route; it is not silently
  imported into this proof.

Issue #193 should have one prerequisite M5 child for capability reset and the
evidence-record schema, plus a later final re-admission child. Issue #194 should
have separate M6 gate children for the NIST and Susial lanes. Each M6 child is
blocked by the M5 native-problem contract and evidence-schema child. The final
M5 re-admission child is blocked by both accepted M6 gates. Broad #194 is not
blocked because unrelated benchmark work can proceed.

## Interfaces And Data Flow

1. A retained source table is parsed through strict `TargetDataset` contracts.
2. A source-qualified `Mixture` and configured `Regression` compile the exact
   native problem.
3. Native Ceres fits the selected parameters and emits its receipt.
4. A package-owned prediction oracle evaluates the same before/after parameter
   states at every retained source row.
5. M6 writes exact source/model tables, receipt, metrics, and plot.
6. A strict checker verifies identities, hashes, row coverage, receipt fields,
   finite predictions, and plot/table consistency.
7. The final M5 re-admission leaf references those exact accepted checkers and
   artifact sets before adding the two narrowly scoped capability rows.

## Loud Errors And Stop Gates

- Reject capability rows without every required evidence field.
- Reject generated/self-recovery rows as independent admission data.
- Reject a source table lacking units, species/basis identity, or an exact
  source locator.
- Reject a proof whose fitted native receipt differs from the prediction
  oracle's model-input or parameter fingerprint.
- Stop if Task 9 or the M5 native problem contract is not complete.
- Stop the Susial lane if exact source-qualified pure parameters and model
  configuration cannot be established; do not substitute paper `k_ij`.
- Stop before an `x-y` curve claim when no admitted M4 associating route exists.
- Keep a family closed when its real-data lane is incomplete.

## Testing And Proof

- capability contract mutation tests delete each evidence field and require a
  loud failure;
- focused M5 tests execute each configured fit through native Ceres and verify
  exact problem receipt, parameter movement, row IDs, source IDs, and derivative
  ownership;
- NIST checker tests verify source-row coverage, units, before/after prediction
  tables, metrics, and plotted series identity;
- Susial checker tests verify all retained rows, composition basis, zero-target
  residual definition, before/after native values, and contextual treatment of
  the paper parameter;
- plot tests compare plotted-data CSVs with retained source/model tables;
- capability tests prove synthetic, pure-ion, and electrolyte evidence cannot
  activate a family; and
- strict docs, Ruff, diff, and cleanup checks pass.

Every model prediction created by these lanes must retain its source data and
observation/model plot in accordance with repository policy.

## Migration And Cutover

1. Reset M5 admitted regression families without removing useful component
   tests and land the complete evidence-record schema.
2. Stabilize the M5 native problem contract; those two M5 prerequisites unblock
   the M6 evidence gates.
3. Build and independently review the NIST lane.
4. Build and independently review the Susial residual lane.
5. Run the final M5 re-admission leaf and add only the exact NIST and Susial
   scopes backed by accepted M6 records.
6. Replace parameter-bar-only artifacts as admission evidence; they may remain
   clearly labeled exploratory context if still useful.
7. Update #193, #194, capability docs, analysis metadata, and milestone pages.

## Risks

- Using training rows for all displayed metrics can exaggerate predictive
  confidence; row use must be visible and held-out rows should be reported when
  a stable partition is practical.
- NIST property tables are reliable operational inputs but are not the original
  PC-SAFT fitting publication.
- The Susial residual plot may be mistaken for an equilibrium curve unless its
  axes and caption clearly state the zero-residual target.
- Capability vocabulary can sound broader than the exact fitted case; scope
  fields and exclusions must remain machine-checked.
- Regenerating plots against a different native build can create stale evidence
  unless fingerprints are checked.

## Execution-Time Selections

- The first pure-neutral lane is methane. Fit rows are the currently retained
  110, 130, 150, and 170 K NIST records; evaluation and plots use all nine
  retained 100-180 K rows, making the intervening/end rows visibly held out.
  This exact partition is fixed before the RED test.
- No scientific accuracy threshold is selected. If a later task needs one, it
  must cite source uncertainty or an approved validation requirement.

## Decision Ledger

| Decision | Evidence | Selected answer | Consequence | Deferred? | Owner |
| --- | --- | --- | --- | --- | --- |
| Milestone shape | Tracker policy | One cross-workstream spec, separate M5 and M6 plans/issues. | Each issue retains one milestone and package owner. | No | M5/M6 |
| Existing trackers | Live issue audit | Use #193 and #194 as parents. | Do not duplicate the open backlogs. | No | M5/M6 |
| Initial state | Current backend-derived claims | Begin with no admitted regression families. | Evidence must add each scope explicitly. | No | M5 |
| Pure lane claim | NIST/Gross source comparison | Prove an operational NIST fit, not Gross parameter reproduction. | Parameter comparison is contextual only. | No | M5/M6 |
| Binary lane claim | Susial source notes and current M4 boundary | Fit observed-state fugacity imbalance and plot target zero versus model residual. | No false `x-y` prediction curve. | No | M5/M6 |
| Paper parameter | Nonidentical pure basis | Treat `-0.0269` as context, not an identity oracle. | No invented tolerance around a mismatched basis. | No | M6 |
| Accuracy thresholds | No source-backed threshold selected | Retain metrics; gate accuracy only from an approved source. | Workflow support and model accuracy stay distinct. | No | M5/M6 |
| Electrolyte scope | Synthetic evidence and open #338 | Keep pure-ion, liquid-electrolyte, and Khudaida fitting closed. | Future evidence cannot inherit this admission. | No | M5 |
| Pure species/partition | Current methane API test and nine retained NIST rows | Fit 110/130/150/170 K; evaluate all 100-180 K rows. | No ad hoc row selection during fitting. | No | M6 |
