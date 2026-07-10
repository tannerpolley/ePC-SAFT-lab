# ADR 0004: Associating Equilibrium Architecture

## Status

Accepted.

## Context

Association site fractions `X_A` are solved internal variables. Direct CppAD
recording through the association fixed-point iteration is forbidden because it
records an iterative algorithm instead of the thermodynamic residual closure.
State and Regression derivative routes therefore eliminate `X_A`, compute
explicit partials, and apply implicit sensitivities.

Production equilibrium routes have a stricter requirement than State property
payloads: Ipopt needs exact first derivatives and exact Lagrangian Hessian
contributions for every exposed objective and constraint residual. A working
single-phase association derivative payload is not enough to expose associating
equilibrium.

## Decision

- Current production equilibrium selector routes remain neutral,
  non-electrolyte, and non-reactive. Associating admission is restricted to the
  source-backed Gross/Sadowski 2002 bubble/dew pressure fixtures.
- Generalized associating equilibrium remains declared-not-exposed until one
  complete production architecture is proven.
- Future associating equilibrium must choose one of these architectures:
  - eliminate `X_A` and provide complete implicit first- and second-order
    derivatives for every objective and constraint residual used by Ipopt.
  - lift `X_A` as explicit NLP variables with association mass-action
    constraints, true site topology, differentiated association-delta
    dependencies or an explicit fixed-delta diagnostic contract, exact
    Jacobian rows, and exact Lagrangian Hessian rows.
- Central-difference comparison checks are validation-only and are not
  production derivative backends.
- Target-kind registry presence is not optimizer support and must not broaden
  public capability claims.

## Consequences

Associating mixtures outside the admitted Gross/Sadowski pressure-boundary
fixtures fail before solver dispatch. Internal
lifted-`X_A` blocks may be maintained as diagnostic or future-route building
blocks, but they do not make associating equilibrium public. Any future route
that uses lifted `X_A` must first prove site count, site-component ownership,
mass-action residuals, Jacobians, objective Hessian terms, and constraint
Hessian rows for the exact variable model it exposes.

The generalized phase-equilibrium plan now keeps associating phase
equilibrium behind the shared TP-flash architecture beyond the narrow
Gross/Sadowski pressure-boundary admission. Gross/Sadowski 2002 remains the
first associating validation target, but it must enter through exact association
derivatives, phase NLP certification, and the collapsed GFPE registry gates.
