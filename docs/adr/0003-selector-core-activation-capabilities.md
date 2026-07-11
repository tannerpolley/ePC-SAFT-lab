# ADR 0003: Selector Core And Activation-Driven Equilibrium Capabilities

## Status

Accepted.

## Context

The package had native equilibrium route implementations and Python-facing route
surfaces that were broader than the production evidence. Keeping those routes
callable made `epcsaft.capabilities()` disagree with executable evidence and left
deleted or unproven families looking available.

## Decision

- The native activation matrix in
  `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h` is the source of
  truth for equilibrium route-family exposure.
- The selector core in `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp`
  owns production route admission, activation checks, exact-derivative
  requirements, density-closure diagnostics, and certification gating.
- The production public surface is limited to one
  `Equilibrium(mixture, route=..., ...).solve()` workflow with the
  evidence-backed `bubble_pressure`, `dew_pressure`, and scoped nonassociating
  hydrocarbon `single_component_vle` route specs.
- Bubble/dew temperature and neutral TP-flash contracts remain declared but
  closed. Their retained inverse/workbook component checks do not establish
  live, literature-backed production evidence.
- Non-production neutral LLE, TP flash, temperature-boundary VLE, stability,
  electrolyte, reactive, and speciation paths are not public exports. Retained
  implementation and evidence are labeled internal validation, not preserved as
  callable stubs or compatibility wrappers.
- `epcsaft_equilibrium.capabilities()` reports production families and
  declared-not-exposed future families separately, without claiming route
  availability for future rows.

## Consequences

Selector-ineligible requests fail before solver dispatch. Solver or
certification failures after dispatch raise with diagnostics. Future route
families must enter through the activation matrix and selector core before they
can be described as production capabilities. Neutral LLE remains closed because
the retained sampled-candidate Stage II audit is not a global HELD proof. TP flash remains closed until a
source-backed live proof covers selector-owned seed generation, residual
closure, and postsolve certification; direct flash bindings remain deleted.

## Route-Addition Gate

Before adding any equilibrium route, implementation must prove the existing
production owner, write the route-spec matrix, add negative tests for selector
bypass and direct pybind routes, and get owner review before design lock when
the path is ambiguous. For neutral VLE, the current production owner is the
bubble/dew pressure residual core reached through the selector; adding a
standalone flash route or route-specific public execution method is a rejected
design.
