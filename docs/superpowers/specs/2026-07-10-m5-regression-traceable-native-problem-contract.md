# M5 Traceable Native Regression Problem Contract

Milestone: `M5 - Regression`
Package: `packages/epcsaft-regression`
Issue: [#193](https://github.com/ePC-SAFT/ePC-SAFT/issues/193)
Status: `draft for review`
Last reviewed: `2026-07-10`

## Context

This spec reconciles Tasks 10 and 11, the regression half of Task 21, and the
open M5 regression backlog. Source program documents are:

- [2026-07-09 program spec](2026-07-09-m3-core-repository-truth-and-scientific-integrity-program.md)
- [2026-07-09 implementation plan](../plans/2026-07-09-m3-core-repository-truth-and-scientific-integrity-program-plan.md)

For this single-user scientific repository, the practical requirement is that
a returned regression result describe exactly the problem Ceres solved. Target
identity, units, source, weights, fitted and fixed parameters, bounds, loss,
solver limits, and provider model input must survive Python-to-native
compilation without post-solve reinterpretation.

Open issue #193 is the exact milestone tracker for this work. Its existing
spec and plan are backlog placeholders and should be replaced by this design
and its implementation plan rather than creating a competing M5 tracker.

## Verified Current Behavior

The following were checked on `main` at `1fc4c819`:

- `TargetRow` permits blank `row_id` and `source`, supplies weight `1.0`, and
  stores most values in a loose mapping;
- `TargetDataset` requires rows but does not enforce unique row identities,
  canonical units, source-kind rules, composition basis, or conflicting-row
  checks;
- public pure and binary helpers accept `weights`, `loss`, `solver_options`,
  and `output_report`, then `_annotate_contract_problem()` writes those values
  into the returned Python problem after the native solve;
- `Regression(mixture)` stores a `Mixture`, but its fit method dispatches the
  supplied records without compiling that mixture into the native problem;
- the generic native adapter forwards records, target arrays, bounds, initial
  values, and one evaluation limit, but not the full accepted control surface;
- native generic Ceres success accepts either `IsSolutionUsable()` or a
  non-increasing objective, so a non-improving termination can appear
  successful;
- binary fit persistence stages multiple CSVs and replaces them individually;
  a failure after the first replacement can leave matrix and manifest content
  from different generations; and
- `epcsaft_regression/core.py` still combines target contracts, problem
  compilation, native dispatch, result shaping, and persistence.

Closed issues [#88](https://github.com/ePC-SAFT/ePC-SAFT/issues/88),
[#94](https://github.com/ePC-SAFT/ePC-SAFT/issues/94),
[#53](https://github.com/ePC-SAFT/ePC-SAFT/issues/53),
[#65](https://github.com/ePC-SAFT/ePC-SAFT/issues/65),
[#66](https://github.com/ePC-SAFT/ePC-SAFT/issues/66), and
[#135](https://github.com/ePC-SAFT/ePC-SAFT/issues/135) are implementation
history, not proof that the current contract is complete.

## Goals

- Make `TargetRow` and `TargetDataset` the only public target-data boundary.
- Require enough identity, units, basis, and source data to reproduce every
  residual row without demanding a fabricated literature citation for private
  measurements.
- Compile every accepted regression control into one typed native problem or
  reject it before native dispatch.
- Make `Regression(mixture, ...)` the configured production workflow and
  consume the exact M3 resolved provider input.
- Return a native-authored, versioned problem receipt and construct Python
  result views only from that receipt.
- Use Ceres termination and solution-usability facts without a cost-only
  success shortcut.
- Make multi-file fitted-interaction persistence all-or-original under injected
  failures.
- Split target, option, problem, result, native-adapter, and persistence owners
  out of `core.py` while preserving characterized numerical behavior.

## Non-Goals

- No regression-family capability admission; real-data admission is specified
  separately in the M5/M6 regression evidence spec.
- No reactive, pure-ion, or liquid-electrolyte production claim.
- No Python-owned production optimizer or residual loop.
- No preservation of contradictory free-function production APIs through
  wrappers after the workflow cutover.
- No requirement to support every historical option. Unsupported options are
  removed or rejected.
- No requirement for a DOI or publication locator on user-owned measurements,
  generated component tests, or private laboratory rows.
- No row-specific robust-loss feature until a separate use case justifies its
  precedence and native mapping.

## Alternatives Considered

### Patch each public helper independently

This can make a few controls effective quickly, but it preserves parallel
problem builders and cannot guarantee that `Regression(mixture)` and free
functions solve the same problem.

### Keep loose rows and add validation immediately before Ceres

Late validation reduces API work but loses source and row identity during
earlier transformations. Native diagnostics would still be reconstructed from
position rather than stable row IDs.

### One typed dataset and one native problem compiler

This is the selected design. Targets, provider input, parameter map, controls,
and source identities compile once into a native problem record. The receipt
is emitted from that record, not annotated after solving.

## Selected Design

### Strict target contracts

`TargetRow` becomes a family-discriminated record. Every row has:

- a nonblank unique `row_id`;
- `target_family` and family-specific observable schema;
- canonical target and condition units;
- finite conditions and observations;
- a positive finite row weight and positive finite residual scale;
- `source_id` and `source_kind`; and
- family-specific species, phase, and composition fields.

Literature rows additionally require citation identity and an exact table,
figure, equation, or row locator. User measurements require a stable dataset
and row identity but not a publication. Synthetic or generated rows carry an
explicit component-test source kind and cannot later satisfy production
evidence gates.

Composition-bearing families require an explicit basis, ordered species, all
fractions, and family-specific sum/charge constraints. Pure-property rows do
not carry meaningless composition fields. Missing fractions are never inferred
and supplied fractions are never silently normalized.

Raw CSV and mapping inputs are conveniences only through named strict
constructors that produce a complete `TargetDataset`. Public fit methods accept
the typed dataset, not an unchecked record sequence.

### Typed controls and problem compilation

A regression problem compiler consumes:

1. the configured `Regression.mixture` and its resolved provider definition;
2. one `TargetDataset`;
3. an explicit fitted-parameter map and fixed-parameter records;
4. starts and bounds; and
5. typed solver controls.

The initially supported loss contract is one explicit global loss applied in
native Ceres. Linear loss is the only mandatory first-cutover value. Additional
Ceres loss types may be admitted individually with option-validation and
mutation tests. Per-row weights and residual scales remain part of each row;
row-specific loss overrides are rejected.

Unknown solver controls, conflicting fitted/fixed parameters, missing starts,
invalid bounds, unsupported target/parameter combinations, and controls not
represented in the native record fail before solve construction.

### Native problem and receipt

The compiled native record owns ordered row IDs, source IDs, resolved model
input fingerprint, parameter names and indices, fixed values, starts, bounds,
weights, scales, loss, tolerances, and evaluation/iteration limits. Ceres owns
residual packing, loss application, bounds, iteration, and final diagnostics.

The native layer returns a versioned receipt containing the exact submitted
problem plus termination type, solution-usability flag, objective values,
evaluation counts, parameter movement, active bounds, row diagnostics, and
derivative ownership. Python `FitProblem` and `FitResult` become immutable views
of this receipt. `_annotate_contract_problem` is deleted.

Public success is true only when the native solution is usable, termination is
in an explicitly accepted Ceres category, required result fields are finite,
and the derivative contract is satisfied. Lower or unchanged cost alone never
changes failure to success.

### Configured workflow ownership

`Regression(mixture, ...)` is the sole configured production entry point. Its
methods accept `TargetDataset` plus typed overrides and always compile the
stored mixture. During the ADR 0005 transition, the class remains owned and
exported by `epcsaft-regression`; contradictory root free functions are removed
in the coordinated cutover instead of retained as compatibility shims.

### Rollback-safe persistence

Writing fitted interactions is a separate explicit action after a successful
fit. The persistence owner:

- validates the intended matrix and source-manifest generation in memory;
- stages every destination on the same filesystem and fsyncs staged data;
- records exact original bytes for transaction recovery;
- replaces files in a deterministic order;
- restores every replaced destination if any replace or post-write strict
  reload fails;
- fsyncs the directory and removes transaction artifacts; and
- reports success only after the complete dataset strictly reloads.

Failure-injection tests cover each replacement and reload boundary. If recovery
itself cannot complete, the operation raises with exact affected paths and does
not claim a successful write.

## Package And Milestone Ownership

- M5 / `packages/epcsaft-regression` owns target contracts, problem compiler,
  Ceres records, receipts, result views, persistence, and regression docs.
- M3 supplies the resolved model-input contract. The native-problem slice is
  blocked until that provider seam is stable; strict target work can proceed.
- M6 owns retained real-data artifacts and cannot repair this contract in an
  analysis script.
- M4 is not required for fixed observed-state regression residuals.

## Interfaces And Data Flow

1. A strict constructor parses source data into `TargetDataset`.
2. `Regression(mixture, options...).fit(dataset, parameter_map...)` validates
   target families against fitted parameters.
3. The compiler resolves provider inputs for each row's exact conditions and
   emits one native regression problem.
4. Native Ceres evaluates residuals and exact supported derivatives, applies
   controls, solves, and emits the problem/result receipt.
5. Python returns detached immutable result views derived only from the native
   receipt.
6. Optional persistence applies the accepted fit to a user-owned dataset under
   the rollback-safe transaction.

## Loud Errors And Stop Gates

- Reject blank or duplicate row IDs, missing source identity, invalid units,
  nonfinite values, invalid composition, nonpositive weights/scales, and
  conflicting duplicates before provider evaluation.
- Reject literature rows without a source locator; never invent one for a
  private measurement.
- Reject any accepted-looking control that lacks a native record field and a
  mutation test.
- Reject any fitted parameter whose derivative columns are incomplete.
- Reject target reordering that cannot preserve row IDs through native output.
- Stop the workflow cutover if `Regression(mixture)` does not consume the M3
  fingerprint or if a free path solves a different problem.
- Stop persistence if complete rollback cannot be demonstrated by failure
  injection.

## Testing And Proof

- Mutation tests show each accepted weight, scale, loss, start, bound, fixed
  value, tolerance, and limit changes the native receipt or problem behavior.
- Rejected-control tests prove unknown and unsupported keys fail before native
  dispatch.
- Dataset tests cover units, finite values, source kinds, citation conditions,
  composition basis, uniqueness, normalization rejection, and row ordering.
- Native tests assert receipt identity, Ceres control use, exact derivative
  coverage, termination semantics, and row/source diagnostic propagation.
- Workflow tests prove changing `Regression.mixture` changes the submitted
  provider fingerprint and that no production free-function bypass remains.
- Failure-injection tests prove fitted interaction files are all new or all
  original after each possible persistence failure.
- Focused M5 tests, Ruff, strict docs, diff checks, and cleanup pass.

Real-data prediction plots are not an acceptance gate for this contract-only
spec; they belong to the dependent admission spec.

## Migration And Cutover

1. Add characterization tests for current pure, binary, and electrolyte
   problem/receipt behavior, including ignored-control mutations.
2. Extract and harden `targets.py` while preserving public capability closure.
3. Add typed options and one problem compiler against the M3 resolved input.
4. Extend native records and Ceres ownership; switch result construction to the
   native receipt and delete post-hoc annotation.
5. Cut public production use to `Regression(mixture)` and remove displaced
   free functions in the same coordinated API change.
6. Extract result and persistence owners and add transaction failure proof.
7. Update #193, package docs, CONTEXT.md, ADR-aligned exports, and tests.

Issue #193 should remain the tracking issue, with bounded child issues for
strict targets, native controls/receipt, workflow cutover, and persistence.

## Risks

- Requiring typed rows will expose many test and analysis fixtures that lack
  source identity or units.
- Applying weights and loss for real can change fitted results that previously
  ignored them.
- A broad free-function removal needs synchronized docs and analysis callers.
- Receipt schemas can duplicate Python result models unless the native receipt
  remains authoritative.
- Recovery logic must not leave ad hoc backups or hidden generations behind.

## Deferred Extensions And Publication Facts

- Additional non-linear Ceres loss types are outside the first cutover. Linear
  loss is the only required initial option; each later type needs its own tests.
- Exact child issue numbers are publication facts assigned by GitHub, not
  architecture decisions.

## Decision Ledger

| Decision | Evidence | Selected answer | Consequence | Deferred? | Owner |
| --- | --- | --- | --- | --- | --- |
| Task grouping | Shared target/control/receipt flow | Merge Tasks 10 and 11 into one M5 contract spec. | Avoid two competing problem compilers. | No | M5 |
| Tracker | Live issue audit | Update open #193; do not create another M5 parent. | Closed #88/#94/#53/#66 remain history. | No | M5 |
| Source rule | Generic package use plus scientific traceability | Require source identity for all rows and citation locator only for literature. | Private measurements remain usable without fabricated citations. | No | M5 |
| Composition rule | Family-specific target semantics | Require composition only for composition-bearing families. | Pure rows avoid meaningless fields. | No | M5 |
| Control policy | Ignored-control mutation evidence | Every accepted control reaches native Ceres or is rejected. | Historical options are not automatically preserved. | No | M5 |
| Loss granularity | Current global API and lack of row-specific use case | Use a typed global loss plus row weights/scales; reject row loss overrides. | Smaller unambiguous first contract. | No | M5 |
| Result authority | Post-hoc annotation defect | Native problem/result receipt is authoritative. | Python views cannot describe a different problem. | No | M5 |
| Success | Ceres shortcut audit | Require usable, accepted native termination; cost alone is insufficient. | Non-improving/unfinished solves remain failures. | No | M5 |
| Persistence | Multi-file partial-replace risk | Use rollback-safe staged replacement with failure injection. | Matrix and manifest remain one logical generation. | No | M5 |
| Decomposition | Task 21 overlap | Extract M5 owners during contract cutover. | Avoid a second behavior-moving refactor. | No | M5 |
| Extra loss types | No approved first-use requirement | Admit later, one tested type at a time. | Linear is the initial required contract. | Yes | M5 |
