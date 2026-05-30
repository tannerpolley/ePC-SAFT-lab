# Remove One-Off Born Parameter Derivative Adapter

- Issue title: Remove one-off Born parameter derivative adapter from provider EOS
- Milestone: `M3 - EOS`
- Package scope: `epcsaft` provider/core only
- Related issue: #198

## Problem

Issue #198 moved Born derivative reporting to the CppAD component-parameter
derivative path, but left `born_parameter_derivatives.cpp` as a standalone EOS
contribution source file. That file no longer owns analytical Born derivative
logic; it only adapts generic CppAD derivative columns into the public
`State.born_parameter_derivatives()` payload.

The remaining one-off file makes the provider EOS layout look like it still has
a Born-specific derivative implementation surface and leaves stale build/SDK
manifest entries for a compilation unit that should not exist.

## Intended Outcome

The provider EOS keeps public CppAD-backed Born parameter derivative reporting
while deleting the redundant one-off Born derivative source file and stale
build/SDK manifest references.

## Key Changes

- Delete `packages/epcsaft/src/epcsaft/native/eos/contributions/born_parameter_derivatives.cpp`.
- Remove that source path from root/package CMake source lists and provider
  native SDK manifests.
- Keep `State.born_parameter_derivatives()` public and behavior-compatible.
- Assemble the public Born derivative payload directly from the generic CppAD
  component-parameter derivative route for `d_born` and `f_solv`.
- Remove the now-unneeded `born_parameter_derivatives_cpp(...)` shared EOS
  declaration from `core_internal.h`.
- Do not add analytical Born parameter derivative formulas, fallback paths,
  old-name aliases, or compatibility redirectors.

## Acceptance Criteria

- [ ] `packages/epcsaft/src/epcsaft/native/eos/contributions/born_parameter_derivatives.cpp` is deleted.
- [ ] CMake and provider native SDK manifests no longer reference
  `eos/contributions/born_parameter_derivatives.cpp`.
- [ ] `State.born_parameter_derivatives()` remains public and reports
  CppAD-backed `d_born` and `f_solv` derivative payloads with unchanged field
  names and shapes.
- [ ] No analytical Born parameter derivative implementation or separate
  `born_parameter_derivatives_cpp` shared EOS helper remains.
- [ ] No `packages/epcsaft-regression` files, M5 regression scope, new tests,
  compatibility aliases, or old-name redirectors are added.

## Non-Goals

- No public API removal for `State.born_parameter_derivatives()`.
- No `epcsaft-regression` package or `M5 - Regression` work.
- No new tests; use existing focused build, manifest, and state derivative
  checks.
- No equation theory changes, equilibrium work, or package split redesign.

## Proof Oracle

```powershell
uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10
uv run python run_pytest.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/build/test_build_epcsaft.py -q
rg -n "eos/contributions/born_parameter_derivatives\\.cpp|born_parameter_derivatives_cpp" CMakeLists.txt packages/epcsaft/CMakeLists.txt packages/epcsaft/src/epcsaft/native_sdk packages/epcsaft/src/epcsaft/native/eos
uv run python scripts/dev/validate_project.py quick
```

