# ADR 0005: Package Extension Split

## Status

Accepted.

## Context

`epcsaft` currently exposes provider, equilibrium, and regression workflows from
one source repository, one Python distribution, and one native `_core` module.
That shape is useful during active solver development, but it does not match the
long-term dependency boundary. Property users should not need Ceres or Ipopt,
and equilibrium or regression implementations should not become hidden core
dependencies.

The organization roadmap targets one core provider package plus two extension
packages:

- `epcsaft` for the ePC-SAFT thermodynamic provider.
- `epcsaft-equilibrium` for Ipopt-backed equilibrium workflows.
- `epcsaft-regression` for Ceres-backed regression workflows.

## Decision

- `epcsaft` is the long-term core EoS/provider package. It owns
  `ParameterSet`, `ModelOptions`, `Mixture`, `State`, property evaluation,
  density and pressure closure, fugacity coefficients, activity coefficients,
  chemical potentials, contribution traces, provider diagnostics, provider
  capabilities, and the stable provider API consumed by extensions.
- CppAD and exact derivative provider support remain core-owned because the
  derivative-capable EoS algebra and implicit state sensitivities live beside
  the thermodynamic provider.
- `epcsaft-equilibrium` is the long-term owner of `Equilibrium`, route specs,
  GFPE assembly, phase discovery, stability evidence, Ipopt NLP assembly,
  Ipopt option profiles, postsolve certification, equilibrium result schemas,
  diagnostics, and equilibrium capability reports.
- `epcsaft-regression` is the long-term owner of `Regression`, regression
  datasets and target rows, parameter maps and bounds, Ceres residual blocks,
  optimizer diagnostics, regression result schemas, and regression capability
  reports.
- The current top-level `Equilibrium` and `Regression` exports are transition
  surfaces for the monorepo. They remain valid until a coordinated migration
  release moves ownership to the extension packages.
- The migration must not leave hidden long-lived compatibility wrappers in the
  core package. When ownership moves, old core-owned paths are removed in the
  same coordinated migration unless a short public deprecation window is
  explicitly accepted in a later ADR.
- After the split, `epcsaft.capabilities()` reports provider capabilities only.
  Extension packages expose their own capability reports. Any aggregate
  capability view must be explicit and test-backed.
- Repository transfer to the `ePC-SAFT` GitHub organization is separate from
  code extraction. Do not create a replacement repository or fork at the old
  source location after transfer because that would remove GitHub's redirect.

## Consequences

Source-checkout builds may continue to compile the current monorepo capability
set while the split is being prepared. Documentation must call that a transition
state, not final core ownership. Phase 2 must define the provider and extension
contracts before code moves. Phase 3 must prove provider-only, equilibrium,
regression, and integration boundaries inside this repository before any
extension repository is extracted.

Ceres belongs to the regression capability. Ipopt belongs to the equilibrium
capability. CppAD remains part of the core derivative substrate. Dependency
presence alone is not a capability claim; each package's capability report must
be backed by its own validation lane.

## Migration Gate

Before extracting an extension repository:

- source-of-truth docs agree with this ADR;
- provider API and native adapter contracts are documented and tested;
- current public surfaces have a future owner;
- build targets or package proofs show provider-only behavior without Ceres and
  Ipopt;
- equilibrium validation proves Ipopt-owned routes without Ceres;
- regression validation proves Ceres-owned fitting without Ipopt;
- regression/equilibrium integration is separate and opt-in;
- no moved public API remains in core as a hidden compatibility path.
