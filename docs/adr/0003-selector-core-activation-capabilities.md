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
- The only production public equilibrium route is
  `Equilibrium(mixture).bubble_pressure(T=..., x=...)`, limited to neutral,
  non-reactive, non-electrolyte, non-associating mixtures.
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
can be described as production capabilities.
