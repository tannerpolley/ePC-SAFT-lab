# M4 Standalone CE Diagnostic, Repair, And Admission

Milestone: `M4 - Equilibrium`
Tracking issue: `#321`
Validation issue: `#329`
Admission issue: `#330`
Status: `approved for planning; #328 typed-request reconciliation precedes #329 component receipt/checker work; source-qualified classification and admission wait on M6 evidence`
Last synced: `2026-07-10`

## Summary

Complete the remaining homogeneous chemical-equilibrium work in five ordered
stages: reconcile the typed constructor request in #328, finish the generic
component receipt/checker contract in #329, build the
source-qualified M6 evidence bundle, classify or repair the source-qualified
M4 outcome, and consider `reactive_speciation` admission only after every
numerical gate passes together.

This merges Tasks 13-14 and only the standalone-speciation slice of Task 15.
The historical CE foundation remains in
`2026-06-25-m4-equilibrium-standalone-chemical-equilibrium-before-cpe.md`;
this spec governs its remaining diagnostic, repair, and admission work.

## Context And Verified Current Behavior

- M4 already owns typed reaction/standard-state contracts, one native
  `NlpProblem`/Ipopt CE path, validation oracles, strict physical limits, and
  extensive diagnostics from closed issues #382-#402.
- `reactive_speciation` is currently `declared_not_exposed` with no public or
  proof route. Public equilibrium remains bubble pressure, dew pressure, and
  scoped nonassociating hydrocarbon `single_component_vle`.
- The canonical checker is:

  ```bash
  uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete
  ```

  On 2026-07-10 it exited nonzero with
  `mea_loading_0.4_balance_failure` and `mea_loading_0.4_not_accepted`.
  The retained balance and reaction-stationarity norms are
  `2.5999999998789356` and `73.79118023038392`, versus `1.0e-8` and `1.0e-6`.
- The live checker case is an ideal mole-fraction-activity component fixture
  with hard-coded constants and a project/module source label. It is not a
  source-complete typed nonideal ePC-SAFT receipt.
- The nonideal input audit under
  `analyses/package_validation/standalone_ce/figures/mea_reactive_speciation_oracle_comparison/source/model_input/`
  deliberately leaves `model_configuration.json` and `parameter_set.json`
  absent while reaction-basis, parameter, domain, and interaction evidence is
  unresolved.
- The old Task 13 path
  `analyses/package_validation/standalone_ce/scripts/check_standalone_ce.py`
  does not exist and is not recreated.

## Goals

1. Inventory existing CE diagnostics before adding fields.
2. Retain primitive values needed to reproduce every continuation stage and
   independently recompute physical and KKT acceptance.
3. Separate generic CE algorithm correctness from nonideal MEA validation.
4. Reconcile #328's request schema with constructor-configured
   `Equilibrium` before closing #329.
5. Complete #329 from component evidence without waiting on M6.
6. Select the source-qualified outcome and root-cause owner from evidence
   before changing code.
7. Repair only that owner while preserving the one-NLP invariant.
8. Admit standalone speciation only through the selector and canonical result
   path after typed inputs, source evidence, and numerical gates pass.

## Non-Goals

- No M3 typed-model-configuration implementation or invention of missing data.
- No Khudaida, Gross 2002, or other paper-specific repair.
- No LLE, electrolyte LLE, TP flash, multiphase, reactive LLE, reactive
  electrolyte LLE, or CPE admission.
- No alternate solver, public helper, direct binding, compatibility wrapper,
  relaxed tolerance, or success based only on solver status.
- No unrelated equilibrium refactor.

## Alternatives

### Tune Ipopt Until The MEA Point Passes

Rejected. Input, standard-state, equation, derivative, scaling, and solver
causes are not yet distinguished; tuning would obscure ownership.

### Wait For Every Nonideal Input Before Improving Diagnostics

Rejected. Explicitly labeled component fixtures can prove generic diagnostic
correctness without claiming nonideal MEA validation.

### Separate Diagnostic Correctness From Scientific Admission

Selected. After #328 establishes the typed constructor request, generic
diagnostics proceed on component fixtures and complete #329.
Named nonideal MEA validation then runs in an M6 leaf, followed by a separate
M4 source-classification or defect leaf. Public admission remains blocked by
that chain.

## Selected Design

### Gate A: Component Receipt And Independent Checker

Compare the required schema with diagnostics already delivered by #382-#402;
add only proven gaps. The versioned retained receipt records:

- commit/build/package/solver identity and exact input or component-fixture ID;
- labeled variables, constraints, bounds, multipliers, options, tolerances,
  scaling, initialization, and seed provenance;
- every accepted and rejected continuation trial with `lambda`, EOS activity
  parameter when applicable, start state, final state, and handoff source;
- primal and physical amounts, activities, chemical potentials, affinities,
  objective, constraints, balances, gradient, labeled Jacobian, labeled
  Lagrangian Hessian, and bound/constraint multipliers;
- scaled and unscaled primal, dual, complementarity, balance, and stationarity
  metrics plus exact acceptance/rejection gate.

Norms do not replace primitive arrays. Labeled dimensions and stable hashes
make the artifact independently checkable and reviewable. An independent
component checker reconstructs the physical and KKT quantities without calling
the production solver. After #328 closes, this gate completes #329 and does
not depend on M6.

### Gate B: Scientific-Input And Evidence Readiness

The existing
`2026-07-10-m4-nonideal-mea-speciation-linux-migration-design.md` is the
canonical source ledger, typed-input readiness design, Linux execution, and
source/model artifact contract for the nonideal MEA case. This spec does not
create a second ledger or plot migration. M6 owns closure of source/artifact
evidence and its evidence-completeness checker; M4 consumes the completed
receipt for later classification. A scientifically rejected solve may complete
M6 evidence while remaining ineligible for admission.

A nonideal admission run requires one immutable receipt containing:

- configuration schema/source, parameter-set identity, units, and species order;
- every active pure parameter, correlation domain, interaction value, and
  justified structural zero;
- reaction stoichiometry, independent basis, conservation/charge basis,
  equilibrium-constant correlation, standard state, and conversion;
- state conditions, feed basis, evaluated correlations, and exact native map.

Missing, conflicting, out-of-domain, or historical-only values stop before
native dispatch. Absence of the executable JSON inputs is the correct blocked
state while the evidence ledger remains open.

### Gate C: Source-Qualified Classification Or Defect Leaf

After the M6 evidence-completeness checker passes, a separate M4 leaf matches
the M3 input, M4 runtime, and retained receipt fingerprints, then recomputes
conservation, charge, affinities, complementarity, and unscaled KKT
stationarity from the source-qualified receipt. Selected analytic/CppAD
derivatives are compared with bounded numerical perturbations at interior
points.

The review records one outcome:

- `admission_candidate`: every source-qualified numerical gate passes;
- `source_qualified_rejection`: evidence is complete, the solve is rejected,
  and no implementation owner has been proven;
- `diagnostic_contract_defect`: repair receipt/checker only;
- `canonical_formulation_defect`: add one red test and repair its owner;
- `not_reproduced`: resolve build/input identity before repair.

Only `canonical_formulation_defect` creates a Bug implementation slice, and it
blocks this classification leaf until a fresh run is reclassified. Only
`admission_candidate` can make #330 dependency-ready.

### Gate D: Smallest Canonical Repair

The repair changes only the evidence-selected CE block, objective, NLP,
standard-state conversion, exact EOS-activity derivative seam, scaling owner,
or Ipopt adapter. It preserves one activation-matrix/NLP/Ipopt solve path,
exact derivatives, strict unscaled limits, and closed unrelated routes. The
defective path is removed rather than retained behind a fallback.

### Gate E: Reactive-Speciation Admission

Issue #330 remains the sole admission gate. It requires Gates A-D, an
`admission_candidate` classification, source/model tables and any required
comparison plot, fresh native/input receipts, and all
focused/default/confidence gates.

Admission uses constructor-configured `epcsaft_equilibrium.Equilibrium`, the
native activation matrix and selector, the one CE NLP owner, and the canonical
result/acceptance builder. The typed chemical-system request owned by #328 must
be reconciled with this workflow; no helper or alternate binding remains.
Only `reactive_speciation` may change. All coupled phase families stay closed.

## Ownership And Data Flow

| Concern | Owner |
| --- | --- |
| CE formulation, NLP, selector, diagnostics, result | M4, `packages/epcsaft-equilibrium` |
| Typed model configuration and resolved native input | M3, `packages/epcsaft` public contract |
| Nonideal MEA source ledger and retained model comparison | M6 evidence using the existing nonideal-MEA design |
| Source-qualified classification or defect routing | Separate M4 leaf after M6 evidence completion |
| Standalone admission | M4 issue #330 |
| Reactive phase coupling | M4 issues #331, #372, and #376; outside this spec |

```text
#328 M4 typed constructor request
-> #329 M4 component receipt/primitives/checker
-> M6 source/fitted/formulation evidence and typed M3 resolved input
-> separate M4 source-qualified classification or defect leaf
-> #330 selector admission
```

Component fixtures enter only at the typed CE request and carry a
`component_evidence` classification that cannot enter admission evidence.
In GitHub native dependency terms, preserve the live #329 `blocked_by` #328
edge. The M6 leaf is `blocked_by` #329, the later
M4 classification leaf is `blocked_by` M6, and #330 is `blocked_by` that leaf
and #328. Issue #329 itself is not blocked by M6.
Tracker publication must remove `status:ready` from #329, apply
`status:blocked` while #328 is open, and synchronize the #329 mirror and M4
milestone row. The normal readiness reconciler may restore `status:ready` only
after all native blockers close.

## Loud Errors And Stop Gates

Stop before dispatch for absent/conflicting/out-of-domain input, unresolved
reaction basis, order mismatch, unjustified zeros, or build/receipt mismatch.
Stop without acceptance after dispatch when final `lambda != 1`, balance exceeds
`1.0e-8`, stationarity exceeds `1.0e-6`, independent KKT disagrees, exact
derivative evidence is absent, Ipopt status is unacceptable, a source-oracle
seed supplied completion, or selector/result/evidence ownership is incomplete.

## Testing And Proof

- Mutation tests remove each receipt/input family and require loud rejection.
- Receipt tests verify labels, shapes, hashes, and every continuation trial.
- Independent component tests reconstruct balances, affinities,
  complementarity, and KKT without any M6 input.
- The later source-qualified M4 test consumes the separately completed M6
  evidence receipt and records one classification before #330 runs.
- Existing ideal/EOS cases remain component tests; they never replace nonideal
  source evidence.
- Focused proof includes:

  ```bash
  uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_schema.py packages/epcsaft-equilibrium/tests/contracts/test_chemical_equilibrium_standard_state.py packages/epcsaft-equilibrium/tests/native/blocks/test_chemical_equilibrium_blocks.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_nlp_activation.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_homotopy.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_standalone_ce_gate.py tests/native/contracts/test_ce_robustness_followup_gate.py -q
  uv run --no-sync python scripts/validation/check_ce_robustness_followup.py --json --require-complete
  uv run --no-sync python scripts/validation/check_standalone_ce_gate.py --json --require-single-nlp-path --require-oracles --require-complete
  ```

The component receipt checker is the completion oracle for #329. The last
command remains nonzero until the later source-qualified classification is
`admission_candidate`; an evidence-complete but scientifically rejected M6 run
does not make it pass. Admission additionally requires fresh build, docs, Ruff,
diff, cleanup, and independent thermodynamic/code review.

## Cutover

- Preserve the older CE spec as foundation history and point its remaining work
  here.
- Retain current failing artifacts as internal evidence until a fresh run with
  matching input/build identity replaces them.
- Remove superseded receipt fields, helpers, and direct paths in the same slice;
  do not add redirectors.

## Risks

| Risk | Control |
| --- | --- |
| Duplicate closed diagnostic work | Field inventory against #382-#402 first |
| Ideal evidence mislabeled as nonideal | Separate evidence classes and require M3 input receipt |
| Tuning around the defect | Root-cause decision precedes repair |
| Unreviewable raw receipt | Labeled schema, stable hashes, semantic summary |
| Checker repeats production logic | Recompute from retained primitive values in a separate owner |
| Accidental route broadening | Exact activation-set and closed-family tests |

## Execution Gates

1. Issue #328 closes the typed constructor-request prerequisite.
2. Gate A then completes #329 independently from source-input readiness.
3. The M6 source/input/evidence leaf is blocked by #329 and M4 cannot choose
   its values.
4. The separate M4 Gate C leaf is blocked by the M6 evidence leaf and must
   identify the source-qualified classification before an implementation Bug
   is marked ready.
5. The evidence owner must identify complete literature observations and domain;
   imported downstream curves alone are insufficient.
6. Issue #330 is blocked by Gate C and #328; do not attach M6 as a blocker of
   all #329 work.

## Decision Ledger

| Decision | Evidence | Outcome | Status |
| --- | --- | --- | --- |
| Grouping | Tasks 13-14 and standalone Task 15 share one dependency chain | One M4 remaining-work spec | Selected for review |
| Capability | Native activation exposes no reactive route | Keep standalone speciation closed | Verified |
| Checker | Current repo uses `check_standalone_ce_gate.py` | Use canonical path | Verified |
| Diagnostics | #382-#402 already cover major surfaces | Inventory before adding fields | Selected for review |
| Scientific input | Executable nonideal inputs are absent by design | Block nonideal run/admission | Verified |
| Repair | Failure class does not identify owner | Independent review selects owner | Selected for review |
| Acceptance | Solver status is insufficient | Require unscaled physical/KKT proof | Selected for review |
| Interface | Task 15 requires selector ownership | Admit only through canonical `Equilibrium` workflow | Selected for review |
| Dependency direction | Live tracker state and component diagnostics do not require the nonideal bundle | #328 -> #329 -> M6 evidence -> separate M4 classification/defect leaf -> #330 | Selected for review |
