# M4 Phase Equilibrium Unified Certification Contract

## Purpose

Create one enforceable phase-equilibrium certification contract for
`epcsaft-equilibrium`, with route-family residual blocks for LLE, VLE, flash,
boundary, electrolyte, and reactive/coupled phase-equilibrium work.

The contract exists to prevent a route from claiming capability support because
one partial diagnostic passed. A production-exposed phase-equilibrium route must
prove the same high-level lifecycle:

1. Resolve the public request into a declared family and variable model.
2. Discover or seed a candidate phase set with retained provenance.
3. Refine that same candidate set through the shared `NlpProblem`/Ipopt route
   when the route claims exact-Hessian support.
4. Certify the refined result with material, pressure, transfer, stability, and
   noncollapse diagnostics.
5. Compare source-backed validation rows or retained fixtures within declared
   tolerances when the route claims data reproduction.
6. Publish capability and registry evidence only for the route scope that passed.

## Contract Levels

### Shared Phase-Equilibrium Contract

Every production-exposed phase-equilibrium route must retain:

- public route key and selector family;
- activation metadata and exact derivative status;
- variable model, bounds, scaling, and fixed specifications;
- phase labels, phase kinds, phase fractions, and phase compositions;
- material-balance residuals;
- pressure-consistency residuals for common-pressure routes;
- transfer residuals appropriate to the species basis;
- phase-distance or noncollapse evidence;
- stability or candidate-completeness evidence;
- seed/discovery provenance;
- postsolve acceptance status and rejection reason;
- capability/registry row proving the admitted scope.

### LLE Family Residual Block

LLE routes add:

- two-liquid or multi-liquid phase-kind evidence;
- liquid-liquid transfer residuals;
- phase-distance evidence that rejects duplicate liquid phases;
- candidate-set replay evidence when HELD/TPD discovery is claimed;
- source-backed LLE tolerance rows for data-reproduction claims.

### Neutral Nonassociating LLE Residual Block

Neutral nonassociating LLE uses molecular transfer residuals:

```text
ln f_i^liquid1 - ln f_i^liquid2 = 0
```

for transferable neutral species, plus material balance, common pressure, and
noncollapse diagnostics.

### Associating LLE Residual Block

Associating LLE uses the same molecular transfer condition, but the chemical
potential or fugacity source must include active association contributions,
association derivative receipts, and source-backed associating fixture evidence.

The route must distinguish global family proof metadata from request-specific
proof applicability. A nonassociating request may belong to the neutral LLE
family without pretending the associating proof route was used for that request.

### Electrolyte LLE Residual Block

Electrolyte LLE uses reduced electroneutral variables. It must retain:

- reduced-basis construction and rank evidence;
- physical lift/back-lift residuals;
- per-phase charge residuals;
- projected electrochemical or modified mean-ionic transfer residuals;
- active electrolyte block evidence such as Born, SSM, DS, and permittivity
  derivative receipts when those blocks are enabled;
- explicit proof that raw single-ion equality was not used as the acceptance
  condition.

### VLE, Flash, Boundary, And Reactive Blocks

VLE, flash, boundary, and reactive/coupled phase-equilibrium routes use the
same shared contract with family-specific residual blocks:

- VLE: vapor-liquid transfer, saturation or split evidence, and noncollapsed
  vapor/liquid phases.
- Flash and multiphase: requested phase-kind set, phase-set completeness,
  candidate replay, and selected/rejected candidate provenance.
- Boundary routes: traced parent state, degree-of-freedom swap, continuation or
  branch provenance, and source-row tolerance evidence when data reproduction is
  claimed.
- Reactive/coupled routes: independent reaction/speciation basis, conserved
  material balances, reaction stationarity, and phase transfer on the correct
  transformed species basis.

## Enforcement Policy

The first implementation gate applies to production-exposed routes only. Planned
or private routes may remain declared as planned, internal, or diagnostic, but
they must not publish capability claims until they pass the contract.

## Task 15 Reconciliation And Future Admission Leaves

Task 15 of the 2026-07-09 validation-correctness program is a routing rule, not one
implementation task. Its named families have different variables, derivatives,
phase-discovery requirements, source evidence, and blockers. They must never be
batch-admitted by one issue, one checker result, or one activation change.

The current capability state is unchanged: the public selector exposes `bubble_pressure`,
`dew_pressure`, and scoped nonassociating hydrocarbon
`single_component_vle`. Neutral LLE, electrolyte LLE, neutral TP flash,
neutral multiphase, standalone reactive speciation, reactive LLE, reactive
electrolyte LLE, and CPE remain internal, planned, or closed as recorded by the
native activation matrix.

Remaining work is routed as follows:

- **Standalone reactive speciation:** issue #330 is the only admission gate. It
  follows the diagnostic, repair, typed-input, and source-evidence gates in
  `2026-07-10-m4-standalone-ce-diagnostic-repair-and-admission.md`. It cannot
  admit a phase-splitting or CPE route.
- **Neutral LLE:** create a future successor leaf under live family parent #363
  for phase discovery complete within its declared route, state, and search
  scope, selector dispatch, canonical result construction, and independent
  source-backed validation. Closed #364-#366 remain historical local/sampled
  evidence and are not reopened as active parents.
- **Electrolyte LLE:** create a separate successor leaf under live family parent
  #363. It requires source-complete typed electrolyte input, charge-neutral
  phase discovery complete within its declared route, state, and search scope,
  exact active-model derivatives, Stage III/postsolve residuals, selector
  ownership, and retained literature/model comparison. Closed #191, #314,
  #343, #350, #370, and #371 are inputs and history, not current admission.
- **Neutral multiphase:** create a future successor leaf under live parent #361
  for phase-set discovery complete within its declared route, state, and search
  scope, canonical selector/result ownership, and source-backed
  multiphase validation. Finite sampled-candidate replay remains internal
  diagnostic evidence.
- **Neutral TP flash:** create a different successor leaf under live parent
  #361. It requires a
  live source-backed flash fixture, selector-owned seed/discovery path,
  material/pressure/transfer closure, and postsolve acceptance. Workbook or
  inverse-consistency evidence alone is insufficient.
- **Reactive and coupled phase equilibrium:** issues #331, #372, and #376 remain
  blocked future work. They are not part of the standalone Task 15 slice.

Closed governance parents #364, #370, and #374 remain historical completed
tranches. New successor leaves attach to the live broad parent (#363 for LLE;
#361 for flash/multiphase) so closed issues are not reopened or made to imply
new proof.

Each future leaf changes at most one activation family and must prove its own
negative selector-bypass tests, source/input receipt, exact derivative path,
independent physical residuals, retained plot when predictions are computed,
and capability/registry equality. A passing family leaf gives no evidence for a
sibling family. Until a leaf passes, its activation row, public routes, and
proof routes remain empty.

## Issue Hierarchy Policy

The M4 tracker should use native GitHub sub-issues:

- one Phase Equilibrium parent;
- one direct core-contract implementation leaf under that parent;
- broad family parents for LLE, VLE, flash/multiphase, boundary routes, and
  reactive/coupled phase equilibrium;
- detailed LLE parent issues for the initial neutral nonassociating LLE,
  associating LLE, electrolyte LLE, and reactive electrolyte LLE contract
  tranches;
- PR-sized initial leaves under those detailed parents; after a detailed parent
  is closed, a new admission successor attaches directly to its still-open
  broad family parent rather than reopening completed governance history.

Existing electrolyte history remains retained evidence. The existing #191
electrolyte GFPE/HELD2 issue becomes part of the electrolyte LLE subtree, with
its closed children retained as historical implementation proof.

## Non-Goals

- No parameter regression inside M4 route-validation issues.
- No release claim.
- No downstream application metrics.
- No broad capability text for planned routes.
- No solver dodge flags or diagnostic-only success counted as production
  route acceptance.
