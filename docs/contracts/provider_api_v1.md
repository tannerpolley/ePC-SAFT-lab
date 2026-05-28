# Provider API v1 Contract

Status: pre-extraction contract.

This contract defines the stable core surface that equilibrium and regression
extensions may consume from `epcsaft`. It is not a new user API in this pass.
It records the boundary that must be preserved before `epcsaft-equilibrium` or
`epcsaft-regression` can be extracted.

## Owner

`epcsaft` owns the provider contract. The provider package owns:

- `ParameterSet`
- `ModelOptions`
- `Mixture`
- `State`
- `create_input_template(...)`
- `runtime_build_info()`
- `provider_native_sdk()`
- `epcsaft.runtime.RouteDiagnosticsView`
- provider-scoped `capabilities()`
- `InputError`, `SolutionError`, and model-parameter errors

`Equilibrium` is owned by `epcsaft-equilibrium` and is no longer exported from
the provider package root. `Regression` remains a remaining transition export
under ADR 0005 until the regression extension migration lands.

## Version

Provider contract id: `provider_api_v1`.

The contract version must be reported by documentation and tests before
extension extraction. A future runtime field may expose the same id, but tests
must not invent a runtime field before implementation exists.

## Parameter Contract

`ParameterSet` is the parameter-family boundary. Extensions may consume
validated parameter records through public `ParameterSet` methods and
`ParameterSet.to_runtime_dict()`.

Required stable facts:

- species order is explicit;
- pure, binary, and option payloads are separated;
- missing required model parameters fail loudly;
- unit and basis conversions are not hidden in extension code;
- full validation analyses keep their own parameter snapshots instead of using
  private package paths.

## Mixture And State Contract

`Mixture` owns component order, model options, and provider construction.
`State` owns thermodynamic condition validation and one closure variable:
pressure or density.

Extensions may create states through public provider objects and may consume:

- pressure and density closure;
- residual Helmholtz and contribution payloads;
- fugacity coefficients;
- activity and osmotic outputs;
- residual chemical potentials;
- derivative result methods;
- diagnostics attached to public provider results or failures.

Extensions must not reinterpret private native state layouts as public schema.

## Result Contract

Provider result payloads are dictionary-like, JSON-compatible where practical,
and include enough shape metadata for extension validation.

`RouteDiagnosticsView` is the provider-owned typed view over public route and
solver diagnostics. `SolutionError.route_diagnostics` must return that
provider-owned view instead of reaching into an extension-owned module path.

Derivative result payloads must include:

- `supported`
- `backend`
- `derivative_backend`
- `message`
- `value`
- `jacobian`
- `outputs`
- `variables`
- `shape`

Contribution traces must name inactive terms explicitly so extension code does
not infer physical activation from missing fields.

## Derivative Contract

CppAD and exact derivative provider support remain core-owned. Extensions may
depend on provider derivative payloads but must not own the provider's CppAD
recording policy.

Required derivative rules:

- derivative coverage is evidence-backed;
- unsupported derivatives fail loudly;
- validation comparison checks are not production derivative backends;
- density and association implicit sensitivities remain provider behavior when
  exposed through provider methods.

## Native Adapter Boundary

Extensions may call public provider Python APIs. They must not import
`epcsaft._core` or private modules as their stable integration boundary.

Native code may still live in one monorepo `_core` module during the transition.
Before extraction, the native boundary must define provider-owned symbols and
extension-owned symbols so provider-only, equilibrium, regression, and
integration validation can be run separately.

Provider-native SDK discovery is exposed through `provider_native_sdk()` and
the `provider_native_sdk_v1` contract. That SDK describes the provider-owned
native target and dependency boundary; it does not make `_core` a stable
extension ABI.

## Capability Contract

Equilibrium capability reporting is owned by `epcsaft-equilibrium`.
`epcsaft.capabilities()` no longer reports equilibrium route admission or Ipopt
route capabilities.

After the split:

- `epcsaft.capabilities()` reports provider capabilities only;
- `epcsaft-equilibrium` reports equilibrium and Ipopt route capabilities;
- `epcsaft-regression` reports regression and Ceres capabilities;
- any aggregate capability view must be explicit and test-backed.

Dependency presence alone is not capability evidence. The transition runtime now
keeps provider capability reporting in `epcsaft.capabilities()` and regression
capability reporting in `epcsaft-regression`.

## Error Contract

Provider input errors use `InputError`. Solver or provider execution failures
use `SolutionError` with diagnostics when available. Extensions may wrap these
errors, but they must preserve the provider diagnostics needed to reproduce the
input and state contract. Extensions may consume typed diagnostics through
`epcsaft.runtime.RouteDiagnosticsView` or `SolutionError.route_diagnostics`.
