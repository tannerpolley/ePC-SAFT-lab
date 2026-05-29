---
issue: 165
title: "M1: remove extension native objects from provider _core"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/165"
state: "open"
milestone: "M1 - Packages"
project: "ePC-SAFT Roadmap"
package: "core"
capability: null
backend: null
readiness: "ready"
release_target: "future"
last_synced: "2026-05-29"
---

# M1: remove extension native objects from provider _core

Child slice of #154. Stops using provider `_core` as the native dumping ground
for equilibrium and regression implementations.

## Acceptance Gates

- [x] Provider `_core` links only `epcsaft_provider_native` and no longer
  compiles or registers equilibrium/Ipopt or regression/Ceres pybind
  entrypoints.
- [x] `epcsaft-equilibrium` owns `epcsaft_equilibrium._native_core` and imports
  equilibrium native symbols from that module.
- [x] `epcsaft-regression` owns `epcsaft_regression._native_core` and imports
  regression native symbols from that module.
- [x] Provider profile keeps Ceres OFF, Ipopt OFF, extension native modules OFF,
  and CppAD ON.
- [x] Normal source-checkout build can import provider and extension adapters
  without using provider `_core` as an extension dumping ground.
- [x] Boundary tests fail if extension native symbols leak into provider
  `_core`.
- [x] Docs and validation commands describe the transition state without hidden
  compatibility wrappers.

## Receipt

Proof passed on branch
`codex/remove-extension-native-objects-from-provider-core` on `2026-05-29`.

- Provider proof: `uv run python scripts/dev/build_epcsaft.py --clean
  --profile provider`; SDK reports `provider_only_core=True`,
  `equilibrium_native_enabled=False`, and `regression_native_enabled=False`.
- Split-module proof: `uv run python scripts/dev/build_epcsaft.py --clean
  --disable-ipopt` links `_core`, `epcsaft_equilibrium._native_core`, and
  `epcsaft_regression._native_core` as separate pybind modules.
- Adapter proof: extension imports resolve to package-local `_native_core`
  modules under `packages/epcsaft-equilibrium/src` and
  `packages/epcsaft-regression/src`.
- Symbol proof: `tests/native/contracts/test_provider_only_core_symbols.py`
  passed and static audit found no equilibrium/regression native symbols in
  provider `_core`, provider stubs, or provider runtime metadata.
