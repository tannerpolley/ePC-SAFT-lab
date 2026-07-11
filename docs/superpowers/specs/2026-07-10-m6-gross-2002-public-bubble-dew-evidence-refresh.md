# M6 Gross 2002 Public Bubble/Dew Evidence Refresh

Milestone: `M6 - Validation`
Package: retained validation evidence for `epcsaft-equilibrium`
Parent issue: [#194](https://github.com/ePC-SAFT/ePC-SAFT/issues/194)
Status: `approved for planning`
Last reviewed: `2026-07-10`

## Context

The public equilibrium surface currently includes `bubble_pressure` and
`dew_pressure`. The corresponding capability evidence names the retained
Gross/Sadowski 2002 Figures 2-9 associating-binary VLE bundle, and the
repository `equilibrium-confidence` and `full` lanes run the strict Gross 2002
checker. That evidence is therefore not optional paper cleanup while those
routes remain exposed.

The Task 9 typed-model-input cutover intentionally defers paper-bundle
migration. This M6 slice owns the later, focused migration and evidence refresh
needed by the already exposed bubble/dew scope. It does not reopen every Gross
paper task or make M3 depend on paper repair.

## Goals

- Migrate only the Gross 2002 bundle needed by Figures 2-9 to the accepted M3
  versioned model-input contract after the provider/M4 cutover lands.
- Regenerate Figures 2-9 sequentially through the public bubble/dew paths on
  Linux, retaining source rows, model rows, route receipts, and plots.
- Prove the exact evidence cited by the public capability rows with fresh
  native identity and an accepted strict checker receipt.
- Remove the Gross contract test's redundant dependency on the private
  `workflows.EquilibriumResult` owner so later M4 decomposition can move that
  type without editing an M6 caller.
- Make this accepted M6 receipt an explicit prerequisite of program closeout
  and the route-gated M4 result-type cutover.

## Non-Goals

- No Gross Figure 1 pure-parameter regression or Figures 8/10 LLE admission
  expansion beyond preserving any unchanged artifacts the strict checker
  already requires.
- No associating LLE, electrolyte, reactive, TP-flash, or multiphase
  admission.
- No new fit, parameter value, structural zero, score threshold, or source
  identity invented to make the checker pass.
- No change to the M3 completion gate; paper migration remains a downstream M6
  consumer.
- No release, PyPI, manylinux, or broad paper-reproduction claim.

## Verified Ownership And Dependencies

- M3 owns `model_configuration.json`, typed scientific records, state-resolved
  inputs, and deterministic input receipts.
- M4 owns the public bubble/dew selectors, exact derivatives, result acceptance,
  and capability rows.
- M6 owns the Gross source/model tables, plots, strict checker, freshness, and
  final evidence receipt.
- This M6 issue is blocked by the coordinated M3 provider cutover and the M4
  resolved-input consumer leaf.
- The M0 closeout gate and M4 route-gated result-type extraction are blocked by
  this M6 receipt. Other Gross and Khudaida work remains independently deferred.

## Selected Evidence Contract

### Source and input boundary

The retained Gross/Sadowski source files, digitization metadata, existing
parameter provenance, and interaction manifests are authoritative. Migration
may translate those proven values into the M3 schema; it may not fill a missing
record. Any absent or conflicting active value leaves the affected figure
non-executable with an exact blocker.

### Figure scope

Figures 2-9 run in numerical order. Every model-comparable figure retains:

- immutable source-table rows and source identity;
- exact M3 definition/state fingerprints;
- public route name and M4 native build identity;
- model-curve and plotted-data tables;
- strict derivative, branch/postsolve, and acceptance fields required by the
  current checker; and
- PNG/SVG/PDF artifacts rendered from retained tables only.

No later figure receives acceptance credit when an earlier required figure is
blocked. The implementation may checkpoint subsets, but the M6 gate accepts
only the complete public-route evidence set.

### Checker and receipt

The primary oracle remains:

```bash
uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py \
  --json --require-complete --require-exact-association-hessian \
  --require-fresh-native
```

If that checker contains requirements unrelated to the capability evidence,
the implementation may split a dedicated public-bubble/dew checker only after
mutation tests prove it is at least as strict for every Figure 2-9 field cited
by `capability_evidence.py`. It may not weaken or bypass a failing public-route
requirement.

The final M6 receipt hashes the source/model/plotted tables, plots, M3/M4
receipts, checker command, checker output, and native identity. It records the
exact figure and route scope; it does not claim full-paper accuracy outside
that scope.

### Mechanical caller cutover

`tests/native/contracts/test_gross_2002_figure01_internal_saturation.py`
already proves the internal validation result has exact type `dict`. Its extra
`isinstance(..., workflows.EquilibriumResult)` assertion couples M6 evidence
to a private owner without adding behavior proof. This slice removes that
private import/assertion while preserving the exact-dict and source-receipt
checks. The change is mechanical and must pass the same test before and after.

## Loud Failures And Stop Gates

- Stop on any missing active configuration, parameter, correlation domain,
  interaction evidence, or structural-zero source.
- Stop when a public route, derivative, branch, or postsolve receipt is missing
  or rejected; do not substitute an internal or diagnostic route.
- Stop on a source/model/plot hash mismatch or a renderer that calls the model.
- Stop if resolving a failure requires changing a paper value, tolerance, or
  unrelated capability.
- If the evidence cannot be refreshed, route a separate M4 capability decision
  to replace or close the affected bubble/dew evidence; M6 does not silently
  preserve a stale public claim.

## Testing And Proof

- RED mutation tests for missing model configuration, source rows, M3/M4
  fingerprints, public route identity, derivative/postsolve fields, plots, and
  checker freshness.
- Focused Gross figure contracts and sequential generators for Figures 2-9.
- Strict Gross checker, activation/capability equality, and
  `equilibrium-confidence` validation.
- Table-only renderer/import guards and retained literature-versus-model plots.
- Ruff, strict docs, `git diff --check`, cleanup, independent scientific/code
  review, and a clean worktree.

## Issue Shape

Create one blocked M6 gate leaf under #194. Its plan may use multiple local
checkpoints, but the GitHub issue closes only when one accepted receipt covers
the complete Figures 2-9 public bubble/dew evidence scope. It blocks the M0
closeout issue and the M4 route-gated result-type owner cutover.

## Decision Ledger

| Decision | Evidence | Selected outcome | Owner |
| --- | --- | --- | --- |
| Is Gross entirely deferred? | Public bubble/dew capability rows and validation lanes consume Figures 2-9 | Keep only the public-route Figures 2-9 refresh active | M6 |
| Does M3 wait on it? | M3 owns a reusable SDK and explicitly defers paper bundles | No; M6 is a downstream consumer | M3/M6 |
| Checker | Existing strict checker is current repository oracle | Reuse it, or prove parity before a scoped split | M6 |
| Missing inputs | No invented scientific values | Stop the affected figure and report the blocker | M6/M3 |
| Private type import | Exact `dict` assertion already proves the behavior | Remove redundant private-owner coupling mechanically | M6/M4 |
| Closeout | `full` and `equilibrium-confidence` execute this proof | Accepted receipt is an active M0 prerequisite | M0/M6 |
