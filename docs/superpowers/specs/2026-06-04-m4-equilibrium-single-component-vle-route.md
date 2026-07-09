# Single-Component VLE Route For Equilibrium Extension

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/228`
Status: `open`
Last synced: `2026-06-05`

## Summary

Add a production single-component VLE capability to `epcsaft-equilibrium` using
the same modular NLP/IPOPT discipline as the broader equilibrium framework. The
route should solve pure-component vapor-liquid coexistence at fixed
temperature, returning saturation pressure, vapor density, liquid density,
fugacity or chemical-potential residuals, exact derivative evidence, and route
diagnostics.

This is the production counterpart to the M8 toybox SciPy saturation solver.
The provider package should continue to own EOS state/property evaluation; the
equilibrium extension should own coexistence route assembly and solver policy.

## Project Context Evidence Used

- `docs/adr/0005-package-extension-split.md` assigns equilibrium workflows to
  `epcsaft-equilibrium` while keeping EOS/property evaluation in the provider.
- `docs/superpowers/milestones/M4-equilibrium/README.md` assigns VLE, Ipopt NLP
  behavior, selector/admission, and exact derivative contracts to M4.
- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
  defines the modular equilibrium-core discipline and exact derivative
  expectations.
- `docs/superpowers/specs/2026-06-01-m4-equilibrium-move-equilibrium-objective-assembly-to-extension.md`
  separates provider derivative bundles from equilibrium objective assembly.
- The current provider package can evaluate `P(T, rho)` and density roots, but
  it should not grow route-level VLE solving.

## User Decisions

- Production true saturation-pressure capability should live in
  `epcsaft-equilibrium`.
- The production route should align with the modular IPOPT/NLP framework rather
  than adding a one-off provider helper.
- Single-component VLE is a legitimate equilibrium route even when the
  composition is trivial; it is the pure-component limit of bubble/dew
  coexistence.
- The M8 toybox SciPy route should provide analysis evidence first, then M4 can
  promote the concept into the package framework.

## Recommended Route Shape

Introduce a route or route family for pure-component VLE with neutral naming,
for example:

```text
single_component_vle
pure_vle_temperature
```

The first production mode should solve at fixed temperature:

```text
input: mixture with one component, T, optional initial guesses
output: P_sat, rho_v, rho_l, fugacity residual, pressure residuals, diagnostics
```

The NLP variables can be represented as:

```text
log_rho_v
log_rho_l
log_p_sat
```

with constraints:

```text
P(T, rho_v) - P_sat = 0
P(T, rho_l) - P_sat = 0
mu(T, rho_v) - mu(T, rho_l) = 0
```

The implementation should reuse provider EOS/property calls and derivative
bundles, while equilibrium owns objective/constraint assembly, scaling,
initialization, failure diagnostics, and route result formatting.

## Current Implementation Note

The production branch implements the residual block as `saturation_block.*` and
uses the existing derived pressure-route substrate in `bubble_dew.cpp` for the
`single_component_vle` route instead of adding a one-route source file. This is
acceptable as long as route metadata, activation-matrix admission, exact
derivative evidence, and public result payloads stay specific to
`single_component_vle`. The first production scope is a single neutral,
non-reactive, non-electrolyte, non-associating component.

## Package Boundary

Provider `epcsaft` owns:

- EOS state construction;
- residual Helmholtz, pressure, chemical potential, and fugacity quantities;
- CppAD-backed derivative substrate;
- parameter payloads and provider capability evidence.

`epcsaft-equilibrium` owns:

- coexistence equations;
- Ipopt/NLP variable scaling;
- route admission;
- initialization policy;
- convergence/failure diagnostics;
- route result objects and exact-derivative evidence.

## Non-Goals

- No provider package vapor-pressure public API.
- No binary bubble/dew implementation in the first single-component route.
- No HELD/GFPE phase-discovery expansion in this spec.
- No regression or parameter fitting scope.
- No benchmark admission without a later M6 validation gate.

## Open Questions

- Should this route be exposed before or after the broader GFPE shared NLP gate
  issues, or should it be used as a narrow proving route for that gate?
- Should fixed-pressure saturation temperature be part of the same first route
  or a follow-up route?
- Which exact provider derivative bundle is sufficient for the pure VLE
  constraints after objective assembly is moved fully to equilibrium?
- How should near-critical or single-root cases be diagnosed without fake
  convergence?

## Proof Oracle Candidates For Later Planning

- `bash scripts/dev/cmake_preset.sh --action build --target epcsaft_equilibrium_native_core --parallel 10`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py -q`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py -q`
- `uv run python scripts/dev/validate_project.py quick`
