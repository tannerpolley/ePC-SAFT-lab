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

## Issue Hierarchy Policy

The M4 tracker should use native GitHub sub-issues:

- one Phase Equilibrium parent;
- one direct core-contract implementation leaf under that parent;
- broad family parents for LLE, VLE, flash/multiphase, boundary routes, and
  reactive/coupled phase equilibrium;
- detailed LLE parent issues for neutral nonassociating LLE, associating LLE,
  electrolyte LLE, and reactive electrolyte LLE;
- PR-sized leaf issues under the detailed family parents.

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
