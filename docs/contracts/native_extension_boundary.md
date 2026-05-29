# Native Extension Boundary Contract

Status: pre-extraction contract.

This contract defines the native build and linkage boundary that must be proven
before package extraction. It records the target boundary and the current
transition implementation inside one source repository.

## Current State

The current source checkout builds provider `_core` plus extension-owned native modules.
Provider/CppAD code links into `epcsaft._core`; equilibrium/Ipopt symbols link
into `epcsaft_equilibrium._native_core`; regression/Ceres symbols link into
`epcsaft_regression._native_core`.

That current shape is a transition state. It is not evidence that Ceres or
Ipopt are core provider dependencies after the split.

The package-boundary proof lanes may disable Ceres and/or Ipopt while keeping
CppAD enabled. The provider-only proof is stricter: it disables equilibrium and
regression native registration entirely so provider `_core` exposes only the
provider-owned symbol surface.

## Target Native Ownership

The first implementation target is native target and package-owned pybind modules
separation inside this repository. The target groups are:

- provider/autodiff target: core EoS, state, property, contribution, CppAD, and
  provider derivative support;
- equilibrium/Ipopt target: GFPE selector, route NLPs, Ipopt adapter, stability
  and postsolve certification, equilibrium pybind registration;
- regression/Ceres target: regression problem assembly, Ceres residual blocks,
  optimizer diagnostics, regression pybind registration.

This target is deliberately before separate repositories. It proves ownership
without introducing cross-repo churn.

## Linkage Rules

Provider target:

- must not link Ceres;
- must not link Ipopt;
- may link or include CppAD for provider derivative support;
- must expose provider capabilities without importing equilibrium or
  regression extension packages by default.

Equilibrium target:

- depends on provider/autodiff;
- owns Ipopt linkage and Ipopt runtime diagnostics;
- must not link Ceres;
- owns equilibrium route admission and result/certification schemas.

Regression target:

- depends on provider/autodiff;
- owns Ceres linkage and regression optimizer diagnostics;
- must not link Ipopt by default;
- may use an explicit integration lane when equilibrium-backed targets are
  validated.

## Pybind Boundary

During the transition, one monorepo build may produce multiple pybind modules.
Provider `_core` must stay provider-only; extension pybind registrars live in
package-owned `_native_core` modules.

Extensions must not use private provider `_core` names as a stable Python API.
Extension native adapters import their package-owned native modules and consume
the provider-native SDK for compatibility checks.

Provider-only build rule:

- provider `_core` must not export equilibrium or regression native entrypoints,
  probes, or fit bindings in any profile.
- when `EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE=OFF` and
  `EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE=OFF`, no extension-owned native module
  is built.

The provider-native SDK discovery surface is `provider_native_sdk_v1`, exposed
through `epcsaft.provider_native_sdk()` and mirrored by the native
`_native_provider_sdk_contract` probe. That probe describes the provider-owned
target and dependency boundary; it does not make `_core` the extension ABI.

## Proof Matrix

Before repository extraction:

- provider-only build or install proof passes without Ceres and Ipopt;
- equilibrium proof passes with Ipopt and without Ceres;
- regression proof passes with Ceres and without Ipopt;
- regression/equilibrium integration proof is explicit and separate;
- capability reports are package-owned and evidence-backed;
- docs, tests, and build metadata agree on the same ownership boundary.

Current local proof commands:

- provider dependency lane: ``uv run python scripts/dev/build_epcsaft.py --clean --profile provider`` or ``python -m build --wheel --config-setting=cmake.define.EPCSAFT_ENABLE_CERES=OFF --config-setting=cmake.define.EPCSAFT_ENABLE_IPOPT=OFF --config-setting=cmake.define.EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE=OFF --config-setting=cmake.define.EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE=OFF``;
- equilibrium dependency lane: ``python -m build --wheel --config-setting=cmake.define.EPCSAFT_ENABLE_CERES=OFF`` with a documented Ipopt root or config package;
- regression dependency lane: ``python -m build --wheel --config-setting=cmake.define.EPCSAFT_ENABLE_IPOPT=OFF``;
- integration lane: the normal native source build with Ceres, CppAD, and Ipopt enabled.
