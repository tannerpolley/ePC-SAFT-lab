# Remove Extension Native Objects From Provider Core

Milestone: `M1 - Packages`
Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/165
Status: `active`
Last synced: `2026-05-29`

## Summary

Resolve the monorepo native-boundary slice by making provider `epcsaft._core`
provider-only in every build. Equilibrium and regression native pybind symbols
must move behind package-owned native modules while the public Python imports
remain `epcsaft`, `epcsaft_equilibrium`, and `epcsaft_regression`.

## Acceptance Gates

- [x] Provider `_core` links only provider-native objects and does not compile
  or register equilibrium/Ipopt or regression/Ceres pybind entrypoints.
- [x] `epcsaft-equilibrium` owns its native pybind module and imports
  equilibrium native symbols from that module, not from `epcsaft._core`.
- [x] `epcsaft-regression` owns its native pybind module and imports
  regression native symbols from that module, not from `epcsaft._core`.
- [x] Provider profile keeps Ceres OFF, Ipopt OFF, extension native modules OFF,
  and CppAD ON.
- [x] Normal source-checkout build can import provider and extension Python
  adapters without using provider `_core` as an extension dumping ground.
- [x] Boundary tests fail if extension native symbols leak into provider
  `_core`.
- [x] Docs, issue mirrors, and tracker state describe the transition truth
  without hidden compatibility wrappers.

## Implementation Notes

- Do not move the provider package into `packages/epcsaft`.
- Do not publish packages or change public import names.
- Prefer a loud import/build failure over fake fallback behavior if a required
  extension native module is missing.
- If pybind cross-module type sharing is brittle, adapt the extension module
  boundary to consume explicit provider/public payloads rather than restoring
  extension symbols to provider `_core`.

## Validation

```powershell
uv run python scripts/dev/build_epcsaft.py --status
uv run python scripts/dev/build_epcsaft.py --clean --profile provider
uv run python -c "import epcsaft, epcsaft._core; print(epcsaft.provider_native_sdk())"
uv run python scripts/dev/build_epcsaft.py --clean --disable-ipopt
uv run python -c "import epcsaft_equilibrium._native; import epcsaft_regression.native_adapter"
uv run python run_pytest.py tests/native/contracts/test_provider_only_core_symbols.py -q
uv run python run_pytest.py tests/workflows/repo/test_internal_package_workspace.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_run_pytest.py -q
uv run python run_pytest.py --provider-api -q
uv run python run_pytest.py --integration -q
uv run python run_pytest.py --native-contracts -q
uv run python run_pytest.py --regression -q
uv run python run_pytest.py --equilibrium-api -q
uv run python scripts/dev/validate_project.py docs
```
