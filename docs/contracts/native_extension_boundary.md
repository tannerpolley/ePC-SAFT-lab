# Native Extension Boundary Contract

Status: pre-extraction contract.

This contract defines the native build and linkage boundary that must be proven
before package extraction. It records the target boundary and the current
transition implementation inside one source repository.

## Current State

The current source checkout builds one native `_core` module from logical
native object targets. Provider/CppAD, equilibrium/Ipopt, and regression/Ceres
code now compile under separate native targets and are linked into the same
pybind module for local development.

That current shape is a transition state. It is not evidence that Ceres or
Ipopt are core provider dependencies after the split.

The package-boundary proof lanes may disable Ceres and/or Ipopt while keeping
CppAD enabled. The provider-only proof is stricter: it disables equilibrium and
regression native registration entirely so provider `_core` exposes only the
provider-owned symbol surface.

## Target Native Ownership

The first implementation target is logical target separation inside this
repository while keeping one pybind module temporarily. The target groups are:

- provider/autodiff target: core EoS, state, property, contribution, CppAD, and
  provider derivative support;
- equilibrium/Ipopt target: GFPE selector, route NLPs, Ipopt adapter, stability
  and postsolve certification, equilibrium pybind registration;
- regression/Ceres target: regression problem assembly, Ceres residual blocks,
  optimizer diagnostics, regression pybind registration.

This target is deliberately before separate pybind modules or separate
repositories. It proves ownership without introducing cross-repo churn.

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

During the transition, one `_core` module may remain. The binding registrar must
make ownership clear enough that provider, equilibrium, and regression symbols
can later move without hidden compatibility paths.

Extensions must not use private `_core` names as a stable Python API. A future
native adapter may be documented only after provider-owned symbols and extension
symbols are separated and tested.

Provider-only build rule:

- when `EPCSAFT_ENABLE_EQUILIBRIUM_NATIVE=OFF` and
  `EPCSAFT_ENABLE_REGRESSION_NATIVE=OFF`, provider `_core` must not export
  equilibrium or regression native entrypoints, probes, or fit bindings.

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

- provider dependency lane: ``uv run python scripts/dev/build_epcsaft.py --clean --profile provider`` or ``python -m build --wheel --config-setting=cmake.define.EPCSAFT_ENABLE_CERES=OFF --config-setting=cmake.define.EPCSAFT_ENABLE_IPOPT=OFF --config-setting=cmake.define.EPCSAFT_ENABLE_EQUILIBRIUM_NATIVE=OFF --config-setting=cmake.define.EPCSAFT_ENABLE_REGRESSION_NATIVE=OFF``;
- equilibrium dependency lane: ``python -m build --wheel --config-setting=cmake.define.EPCSAFT_ENABLE_CERES=OFF`` with a documented Ipopt root or config package;
- regression dependency lane: ``python -m build --wheel --config-setting=cmake.define.EPCSAFT_ENABLE_IPOPT=OFF``;
- integration lane: the normal native source build with Ceres, CppAD, and Ipopt enabled.
