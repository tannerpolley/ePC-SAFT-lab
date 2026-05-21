# ADR 0003: Selector Core And Activation-Driven Equilibrium Capabilities

## Status

Accepted.

## Context

The package had native equilibrium route implementations and Python-facing route
surfaces that were broader than the production evidence. Keeping those routes
callable made `epcsaft.capabilities()` difficult to keep honest and left
deleted or unproven families looking available.

## Decision

- The native activation matrix in
  `src/epcsaft/native/equilibrium/core/activation_matrix.h` is the source of
  truth for equilibrium route-family exposure.
- The selector core in `src/epcsaft/native/equilibrium/core/selector_core.cpp`
  owns production route admission, activation checks, exact-derivative
  requirements, density-closure diagnostics, and certification gating.
- The production public neutral VLE surface is limited to one
  `Equilibrium(mixture).solve(route=..., ...)` execution method with route specs
  for bubble pressure, bubble temperature, dew pressure, dew temperature, and
  two-phase flash, limited to neutral, non-reactive, non-electrolyte,
  non-associating mixtures.
- Bubble/dew and flash requests are route specs admitted by the selector over
  the shared native VLE residual/constraint core; Gibbs/free-energy terms may
  help initialization or objective shaping but are not the acceptance gate.
- Non-production TP flash, LLE, stability, electrolyte, reactive, and
  speciation route files, bindings, public exports, docs, and tests are deleted
  rather than preserved as stubs or compatibility wrappers.
- `epcsaft.capabilities()["equilibrium"]` reports production families and
  declared-not-exposed future families separately, without claiming route
  availability for future rows.

## Consequences

Selector-ineligible requests fail before solver dispatch. Solver or
certification failures after dispatch raise with diagnostics. Future route
families must enter through the activation matrix and selector core before they
can be described as production capabilities. TP flash is production-exposed only
through selector-owned seed generation, residual closure, and postsolve
certification; direct flash bindings remain deleted.

## Route-Addition Gate

Before adding any equilibrium route, implementation must prove the existing
production owner, write the route-spec matrix, add negative tests for selector
bypass and direct pybind routes, and get owner review before design lock when
the path is ambiguous. For neutral VLE, the correct production owner is the
bubble/dew derived residual core reached through the selector; adding another
standalone flash route or route-specific public execution method is a rejected
design.
