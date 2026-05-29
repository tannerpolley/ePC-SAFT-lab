# Provider-Only Build Proof

Milestone: `M1 - Packages`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/164`
Status: `proof passed`
Last synced: `2026-05-29`

## Summary

Prove that the current root-owned `epcsaft` provider package can build and
import without Ceres, Ipopt, equilibrium native objects, or regression native
objects. This is a prerequisite slice for the later `packages/epcsaft` move,
not the package move itself.

## Acceptance Gates

- [x] `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
  configures with `EPCSAFT_ENABLE_CERES=OFF`, `EPCSAFT_ENABLE_IPOPT=OFF`,
  `EPCSAFT_ENABLE_EQUILIBRIUM_NATIVE=OFF`,
  `EPCSAFT_ENABLE_REGRESSION_NATIVE=OFF`, and `EPCSAFT_ENABLE_CPPAD=ON`.
- [x] `import epcsaft` and `import epcsaft._core` work after the provider-only
  build.
- [x] `provider_native_sdk()` reports `provider_only_core=True`,
  `equilibrium_native_enabled=False`, and `regression_native_enabled=False`.
- [x] Provider-only `_core` exports no known equilibrium or regression native
  pybind symbols.
- [x] Validation docs and tracker state name the provider-only proof command.

## Implementation Notes

The normal source-checkout build remains the transition native profile with
Ceres, Ipopt, equilibrium, and regression enabled where dependencies are
available. The provider profile is the package-boundary proof lane for the
future core-only `epcsaft` distribution.

The provider profile writes `EPCSAFT_BUILD_PROFILE=provider` into CMake cache
and forces Ceres, Ipopt, equilibrium native, and regression native off during
regeneration. This prevents Ninja regeneration from drifting a provider-only
tree back to the transition defaults.

Do not close parent issue #154 from this slice. Only #164 is resolved here;
#165 through #169 remain separate M1 package slices.

## Receipt

Passed on `2026-05-29` from branch `codex/provider-only-build-proof`:

- `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
- `uv run python scripts/dev/build_epcsaft.py --profile provider --build-only`
- `uv run python scripts/dev/build_epcsaft.py --status`
- `uv run python -c "import epcsaft; import epcsaft._core; print(epcsaft.provider_native_sdk())"`
- `uv run python run_pytest.py tests/native/contracts/test_provider_only_core_symbols.py -q`
- `uv run python run_pytest.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/repo/test_package_extension_boundary.py -q`
- `uv run python run_pytest.py tests/workflows/build/test_build_epcsaft.py tests/workflows/build/test_build_epcsaft_script.py -q`

## Validation

```powershell
uv run python scripts/dev/build_epcsaft.py --status
uv run python scripts/dev/build_epcsaft.py --clean --profile provider
uv run python -c "import epcsaft; import epcsaft._core; print(epcsaft.provider_native_sdk())"
uv run python run_pytest.py tests/native/contracts/test_provider_only_core_symbols.py -q
uv run python run_pytest.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/repo/test_package_extension_boundary.py -q
uv run python scripts/dev/validate_project.py docs
```
