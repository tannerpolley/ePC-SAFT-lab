# Provider Native SDK v1 Contract

Status: pre-extraction contract.

This contract defines the provider-owned native surface that future extension
packages may use when Python provider calls are not enough for hot equilibrium
or regression loops.

Provider native SDK contract id: `provider_native_sdk_v1`.

## Owner

`epcsaft` owns the provider-native SDK. The SDK belongs to the same provider
boundary as `provider_api_v1`; it is not owned by `epcsaft-equilibrium` or
`epcsaft-regression`.

## Stable Surface

The stable Python discovery surface is `epcsaft.provider_native_sdk()`.

`epcsaft._core` is not the provider-native SDK. Extension packages must not
import private provider pybind names, private native object names, or native
memory layouts as their compatibility surface.

The current transition native target name is `epcsaft_provider_native`.
Extension packages may reference that target only through the SDK contract and
workspace build metadata while this repository remains a monorepo transition
build.

The native SDK payload reports the provider `_core` boundary:

- `provider_only_core`
- `equilibrium_native_enabled`
- `regression_native_enabled`

Current provider builds require `provider_only_core=true` and both extension
flags `false`; extension native symbols live in package-owned `_native_core`
modules.

## Native Dependency Rules

Required provider-native dependencies:

- CppAD
- Eigen

Forbidden provider-native dependencies:

- Ceres
- Ipopt

CppAD remains provider-owned because exact provider derivatives are part of the
thermodynamic provider substrate. Ceres belongs to `epcsaft-regression`; Ipopt
belongs to `epcsaft-equilibrium`.

## Extension Consumers

The intended consumers are:

- `epcsaft-equilibrium`
- `epcsaft-regression`

The equilibrium extension may use provider-native derivatives and property
calls for route assembly, stability, and postsolve checks. The regression
extension may use provider-native derivatives and property calls for residual
assembly. Neither extension owns provider equations or provider derivative
recording policy.

## Extraction Rule

Before true repository extraction, tests must prove that the SDK metadata,
runtime capability reports, CMake target naming, and extension package
manifests agree on the same provider boundary. Separate extension packages may
not treat the monorepo `_core` module as their native ABI.
