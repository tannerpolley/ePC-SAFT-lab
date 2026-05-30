# Harden Born EOS Layout, Naming, and CppAD Derivatives

## Issue Metadata

- GitHub issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/198
- Milestone: `M3 - EOS`
- Full roadmap: `docs/milestones/PROJECT_CONTEXT.md`
- Roadmap section: `## M3 - EOS`
- Labels: `type:task`, `status:ready`, `agent-ready`, `area:core`, `area:derivatives`, `backend:cppad`

## Outcome

The provider EOS harness has a properties folder, canonical Born naming, no
SSMDS runtime/API names, default Born-with-options behavior, direct-Born
reduction when SSM and DS options are off, and CppAD-backed public Born
derivative evidence.

## Implementation Scope

- Move EOS property implementation files into
  `packages/epcsaft/src/epcsaft/native/eos/properties/`, including residual
  Helmholtz, residual properties, density/pressure/compressibility, fugacity,
  activity, chemical potential, and provider property-derivative entrypoints.
- Keep `packages/epcsaft/src/epcsaft/native/eos/state.cpp` and
  `packages/epcsaft/src/epcsaft/native/eos/core_internal.h` at the EOS root as
  the native state facade and shared declaration hub.
- Delete the one-file `eos/derivatives/` folder by moving Born parameter
  derivative construction to the Born-owning implementation path.
- Hard-rename SSMDS-labelled runtime surfaces with no compatibility wrappers:
  use names like `BornDerivativeResult`, `BornGeometryData`,
  `born_parameter_derivatives_cpp`, and
  `State.born_parameter_derivatives()`.
- Keep SSM/DS wording only where it names actual options or term-specific
  equations/gates: `solvation_shell_model`, `dielectric_saturation`, local
  `use_ssm`/`use_ds` logic, and equation/gate names that explicitly refer to
  SSM or DS terms.
- Route public Born `d_born` and `f_solv` derivative payloads through the CppAD
  component-parameter derivative path so public backend labels and capability
  evidence say `cppad`, not `analytic`.

## Public Interface Changes

- Replace Python/native public method `born_ssmds_liquid_derivatives` with
  `born_parameter_derivatives`.
- Rename capability/evidence keys from SSMDS-specific names to Born parameter
  derivative names.
- Preserve the public `ModelOptions.BornModelOptions` fields and defaults:
  Born enabled by default, `solvation_shell_model=True`,
  `dielectric_saturation=True`, and both booleans set false reduce the
  canonical Born path to the direct Born equation.
- Do not add aliases, fallback methods, compatibility wrappers, or old-name
  redirectors.

## Acceptance Criteria

- [ ] EOS property source files are grouped under `eos/properties/` and all
  CMake/provider SDK manifests use the new paths.
- [ ] `eos/derivatives/` is removed after Born derivative logic is moved to the
  Born owner.
- [ ] No runtime function, file, public method, capability key, or test name
  uses `ssmds`/`SSMDS` as the Born API name.
- [ ] SSM/DS wording remains only for option fields, local option logic, or
  equations/gates that name actual SSM or DS terms.
- [ ] Default Born options still enable solvation shell and dielectric
  saturation, and disabling both reduces the canonical path to direct Born
  behavior.
- [ ] Public Born parameter derivative payloads report CppAD-backed coverage
  consistently across state, fugacity, activity, regression, and capability
  evidence.
- [ ] Provider native type stubs, derivative coverage/backend contract tests,
  regression extension capability text, and regression electrolyte tests are
  updated so no stale SSMDS API/test identifiers remain.

## Non-Goals

- No equilibrium route implementation or HELD/GFPE work.
- No public compatibility aliases for old SSMDS names.
- No package split or release packaging redesign beyond source manifest path
  updates.

## Proof Oracle

- `uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10`
- `uv run python run_pytest.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py packages/epcsaft/tests/native/state/test_eos_contributions.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/build/test_build_epcsaft.py -q`
- `uv run python run_pytest.py packages/epcsaft/tests/native/contracts/test_derivative_coverage_matrix.py packages/epcsaft/tests/native/contracts/test_property_derivative_backend_contract.py packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py -q`
- `uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability`
- `uv run python run_pytest.py tests/native/contracts/test_equation_registry.py -q`
- `uv run python scripts/dev/validate_project.py quick`

## Candidate Allowed Files

- `CMakeLists.txt`
- `packages/epcsaft/CMakeLists.txt`
- `packages/epcsaft/src/epcsaft/native/eos/**`
- `packages/epcsaft/src/epcsaft/native/bindings/module.cpp`
- `packages/epcsaft/src/epcsaft/native/model/native_types.h`
- `packages/epcsaft/src/epcsaft/_core.pyi`
- `packages/epcsaft/src/epcsaft/state/native_adapter.py`
- `packages/epcsaft/src/epcsaft/runtime/core.py`
- `packages/epcsaft/src/epcsaft/runtime/capability_evidence.py`
- `packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1/**`
- `packages/epcsaft-regression/src/epcsaft_regression/capabilities.py`
- `packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp`
- `packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py`
- `packages/epcsaft/tests/native/state/**`
- `packages/epcsaft/tests/native/contracts/test_derivative_coverage_matrix.py`
- `packages/epcsaft/tests/native/contracts/test_property_derivative_backend_contract.py`
- `tests/workflows/**`
- `tests/native/contracts/**`
- `docs/latex/equations.tex`
- `docs/equations.md`
- `docs/equations_registry.yaml`

## Execution Boundary

Use `$issue-goal-execute-merge` to resolve the linked GitHub issue. This plan
does not authorize implementation branch creation, GoalBuddy setup, product-code
edits, PR creation, merge, or closeout during issue planning.
