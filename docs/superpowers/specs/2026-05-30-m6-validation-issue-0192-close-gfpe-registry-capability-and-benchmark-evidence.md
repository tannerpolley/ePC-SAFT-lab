# Reconcile Current GFPE Registry, Capability, And Benchmark Evidence

Milestone: `M6 - Validation`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/192`
Status: `open`, blocked by #236 and #455
Last reconciled: `2026-07-10`

## Purpose

Make the algorithm registry, capability payloads, user documentation, and
confidence checks describe the equilibrium workflows that are actually public
and backed by current executable evidence after the resolved-model-input
cutover.

This is a private-project reproducibility gate. It prevents stale internal or
historical evidence from being counted as public validation; it is not a
release, publication, or universal-accuracy claim.

## Current Public Scope

Only these equilibrium workflows may appear as public:

- `bubble_pressure`;
- `dew_pressure`;
- scoped nonassociating hydrocarbon `single_component_vle`.

Neutral or associating LLE, electrolyte LLE, neutral TP flash, reactive
equilibrium, and generalized multiphase remain closed. Historical internal
receipts for those families may remain documented, but they cannot populate an
active public capability row.

## Prerequisites

- #236 reconciles the `single_component_vle` ownership and registry boundary.
- #455 refreshes Gross/Sadowski 2002 Figures 2-9 through the current public
  bubble/dew routes after the M3/M4 resolved-input cutover.
- Closed #188-#191 remain historical inputs. Their closed state does not
  authorize broader current public scope.

## Required Behavior

1. Every active public capability row names an executable route, a current
   evidence/checker identity, and the exact supported scope.
2. Provider capabilities list globally supported model-configuration schemas
   and presets. Active route or instance policy appears in the configured
   mixture/state receipt, not as an inferred provider default.
3. Registry and docs checks fail when planned-only, internal, stale, or closed
   route evidence is presented as current public support.
4. Evidence metadata retains source identity, exact locator, model/input
   receipt identity, and the command that validates it.
5. The final M6 receipt is deterministic and refers to exact accepted child
   receipts rather than broad tracker state.

## Acceptance Gates

- [ ] #236 and #455 are closed with accepted receipts.
- [ ] Public capability snapshots contain exactly bubble pressure, dew
  pressure, and scoped nonassociating hydrocarbon single-component VLE.
- [ ] Closed route families remain absent from public selectors and capability
  rows.
- [ ] Registry entries point to current executable checkers and retained
  source/model evidence.
- [ ] Focused capability, activation, confidence, docs, and generated-registry
  checks pass from a clean tree.

## Ownership

M6 owns registry/evidence reconciliation and its strict checks. M3 owns
provider model-input schemas and receipts. M4 owns equilibrium route admission
and result acceptance. This issue does not repair either package's solver or
input implementation.

## Non-Goals

- No new solver or route implementation.
- No re-admission of LLE, TP flash, reactive, electrolyte, or multiphase
  workflows.
- No repair of unrelated Gross, Khudaida, or other paper-validation programs.
- No fallback evidence, invented parameter, uncited tolerance, or release
  claim.

## Validation

- Focused capability and activation contract tests.
- Gross #455 and single-component #236 strict receipts.
- Generated-registry checks and strict Sphinx build.
- Diff check and cleanup audit.
