# Extension Compatibility Contract

Status: pre-extraction contract.

This contract defines how future extension packages depend on `epcsaft` without
turning equilibrium or regression back into hidden core package behavior.

## Packages

Final package ownership:

- `epcsaft`: core thermodynamic provider.
- `epcsaft-equilibrium`: Ipopt-backed equilibrium extension.
- `epcsaft-regression`: Ceres-backed regression extension.

The current repository is a monorepo transition build. `Equilibrium` is owned
by `epcsaft-equilibrium`; `Regression` remains a root transition export until a
coordinated regression migration moves it to `epcsaft-regression`.

## Dependency Rules

`epcsaft-equilibrium` may depend on:

- `epcsaft`
- Ipopt and its native runtime requirements

It must not depend on Ceres.

`epcsaft-regression` may depend on:

- `epcsaft`
- Ceres and its native runtime requirements

It must not require Ipopt for the default regression install. Regression target
families that need equilibrium solve evidence must use an explicit integration
lane that installs both extensions.

CppAD remains part of the core provider derivative substrate.

The transition repository keeps Ceres enabled by default for source-checkout
regression validation, but Ceres-disabled package-boundary builds must remain
valid for provider and equilibrium proof lanes. The transition repository keeps
Ipopt enabled by default when a usable local install is present, but
Ipopt-disabled package-boundary builds must remain valid for provider and
regression proof lanes.

## Import Rules

Core provider imports must not import extension packages by default.

Extensions must consume the public provider contract. They must not use private
core modules, private pybind names, or native memory layouts as a compatibility
surface. Public provider diagnostics are consumed through
`epcsaft.runtime.RouteDiagnosticsView` or `SolutionError.route_diagnostics`,
not through extension-owned module paths.

The migration must not leave hidden long-lived compatibility wrappers in core.
When a public object moves to an extension package, the old core-owned path is
removed in the coordinated migration unless a later ADR explicitly accepts a
short deprecation window.

## Capability Rules

Each package owns its capability report:

- `epcsaft.capabilities()` reports provider behavior after the split.
- `epcsaft-equilibrium` reports route admission, Ipopt, GFPE, postsolve, and
  equilibrium validation evidence.
- `epcsaft-regression` reports Ceres, target-kind, residual-block, and
  regression validation evidence.

An aggregate report may exist only when it is explicit, opt-in, and tested.

## Version Rules

Extension packages must declare compatible `epcsaft` versions. During sibling
checkout development, tests may use path dependencies, but published packages
must depend on released compatible versions unless a release plan explicitly
coordinates pre-release artifacts.

Breaking movement of `Equilibrium`, `Regression`, target rows, or result
schemas must happen at a coordinated release boundary with matching docs and
validation.

## Integration Rules

Regression/equilibrium integration is an integration feature, not a default
dependency. It must have its own validation lane and failure diagnostics.

Downstream application packages consume generic provider, equilibrium, and
regression outputs. Application-specific MEA, lithium, or absorption-column
workflows do not move upstream as public package APIs.
