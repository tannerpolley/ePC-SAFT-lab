# Harden Provider Source Structure and Remove Unnamed Namespaces

- Issue title: Harden provider source structure and remove unnamed native namespaces
- Milestone: `M3 - EOS`
- Package scope: `epcsaft` provider/core only

## Problem

The provider native and Python state layers have accumulated several shallow or
overloaded modules. The most severe case is
`packages/epcsaft/src/epcsaft/native/eos/properties/residual_helmholtz.cpp`,
which now owns core residual contribution evaluation, CppAD phase objective and
pressure derivatives, phase-state sensitivities, parameter phase derivatives,
and residual derivative entrypoints in one large source file.

The current provider scan also found unnamed C++ namespace blocks in:

- `packages/epcsaft/src/epcsaft/native/autodiff/implicit_sensitivity.cpp`
- `packages/epcsaft/src/epcsaft/native/bindings/module.cpp`
- `packages/epcsaft/src/epcsaft/native/eos/properties/pure_neutral_parameter_derivatives.cpp`
- `packages/epcsaft/src/epcsaft/native/eos/properties/residual_helmholtz.cpp`

For M3, provider EOS/state/derivative ownership should be explicit and easy to
navigate. Private implementation regions should live behind named detail
ownership, and large files should be split by the thermodynamic or binding
surface they own.

## Intended Outcome

The M3 provider code has no unnamed native namespaces, oversized provider
modules are split by EOS/state/binding ownership, public behavior is unchanged,
and workflow structure tests prevent the drift from returning.

## Key Changes

- Split `residual_helmholtz.cpp` by ownership while preserving behavior:
  - Keep core residual contribution evaluation in `residual_helmholtz.cpp`.
  - Move CppAD phase objective/pressure derivatives, phase-state sensitivities,
    parameter phase derivatives, and residual temperature/composition/density
    derivative entrypoints into focused `eos/properties/*` source files.
  - Put any shared templated CppAD residual kernels in one internal named-detail
    header instead of unnamed namespaces.
- Split Python provider adapter responsibilities:
  - Keep public `ePCSAFTMixture` and `ePCSAFTState` facade methods in
    `state/native_adapter.py`.
  - Move native struct/options/payload helpers and derivative payload shaping
    into focused provider-owned `state/` or `runtime/` modules.
- Split pybind payload conversion:
  - Keep `native/bindings/module.cpp` focused on `_core` module registration.
  - Move `py::dict` conversion helpers into named binding converter
    source/header files.
- Enforce provider-wide namespace hygiene:
  - Replace every `namespace {` under
    `packages/epcsaft/src/epcsaft/native/**` with named `*_detail` namespaces
    or file-local `static` functions where appropriate.
  - Add a lightweight structure guard in existing workflow structure tests to
    fail on unnamed provider native namespaces and renewed oversized provider
    files.
- Update root/package CMake source lists and provider native SDK source
  manifests for all moved or added provider files.

## Public Interfaces

No public API change. Provider `State` methods, capability surfaces, CppAD
derivative behavior, and native SDK contracts remain behavior-compatible. This
issue is structure-only.

## Acceptance Criteria

- [ ] No `namespace {` block remains under
  `packages/epcsaft/src/epcsaft/native/**`.
- [ ] `residual_helmholtz.cpp` no longer owns phase objective derivatives,
  phase-state sensitivities, parameter phase derivatives, and residual
  derivative entrypoints in one giant source file.
- [ ] `state/native_adapter.py` keeps the public provider facade while helper
  payload/option/derivative shaping code is moved into focused provider-owned
  modules.
- [ ] `native/bindings/module.cpp` is focused on module registration and no
  longer owns the large pybind payload-converter block.
- [ ] CMake source lists and provider native SDK manifests reference the new
  provider file layout.
- [ ] A lightweight workflow structure guard fails on unnamed provider native
  namespaces and renewed oversized provider files.
- [ ] No public API names, derivative payload shapes, or capability contracts
  change.

## Non-Goals

- No equilibrium extension implementation work.
- No regression extension package or `M5 - Regression` work.
- No EOS equation theory changes.
- No public compatibility wrappers, aliases, or fallback modes.
- No broad validation-suite expansion beyond the lightweight structure guard
  and existing focused proof commands.

## Proof Oracle

```powershell
uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10
uv run python run_pytest.py packages/epcsaft/tests/native/state/test_contributions.py packages/epcsaft/tests/native/state/test_eos_contributions.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py -q
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/build/test_build_epcsaft.py -q
rg -n "^\\s*namespace\\s*\\{" packages/epcsaft/src/epcsaft/native
uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability
uv run python run_pytest.py tests/native/contracts/test_equation_registry.py -q
uv run python scripts/dev/validate_project.py quick
```

Use the full native build command instead of `--build-only` when `build/dev` is
not already configured.
