# ADR 0005: Narrow Associating Bubble-Pressure Admission

## Status

Accepted.

## Context

ADR 0004 kept all associating equilibrium selector routes closed until the
association derivative architecture could prove exact first- and second-order
behavior for Ipopt-owned routes. The association derivative tranche has now
made active-association State and parameter derivative evidence strong enough
to start the next equilibrium step.

The next production target is not general associating equilibrium. It is one
small, source-backed route admission that can prove the selector, exact-Hessian
Ipopt path, association diagnostics, and Gross/Sadowski 2002 parameter handling
without reopening LLE, electrolyte, reactive, or cross-associating systems.

## Decision

- ADR 0004 is amended by this ADR.
- The first associating equilibrium route may be a narrow
  `bubble_pressure` admission only.
- The admitted input topology is neutral, nonelectrolyte, nonreactive, and has
  at most one associating component.
- Admission requires exact derivative and postsolve certification evidence for
  the route, including association diagnostics and exact-Hessian callbacks.
- The first benchmark target is Gross/Sadowski 2002 Figure 2,
  methanol/isobutane at `T = 373.15 K` with `k_ij = 0.05`, using the existing
  package parameter structure.
- Associating `bubble_temperature`, `dew_pressure`, `dew_temperature`, TP
  flash, LLE, electrolyte, reactive, and cross-associating route exposure
  remains blocked until each route has separate selector-owned proof.
- Explicit reduced association closures may be added as approximate EOS
  diagnostics or experimental model options, but they must be labeled as
  exact derivatives of an approximate association model unless they are proven
  to match the exact mass-action solution.

## Consequences

Associating `bubble_pressure` is no longer ruled out by policy once the narrow
gate above is implemented and tested. Broad associating equilibrium remains out
of scope. Future documentation and capabilities must describe the first result
as a limited associating bubble-pressure proof, not as general associating VLE
or LLE support.
