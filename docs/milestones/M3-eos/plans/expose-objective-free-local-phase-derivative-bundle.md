# Expose Objective-Free Local Phase EOS Derivative Bundle

GitHub issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/207

## Summary

Provider EOS should expose a local phase thermodynamic derivative bundle without
owning equilibrium objective semantics. The provider remains responsible for
CppAD-backed residual Helmholtz, pressure, chemical-potential, fugacity,
Born/SSM/DS, relative-permittivity, and implicit-association chain rules. The
equilibrium extension consumes that provider bundle and adds route objective
terms separately.

## Key Changes

- Replace provider objective-style entrypoints such as
  `eos_phase_objective_derivatives_cpp(...)` with an objective-free local phase
  derivative bundle over local variables such as `n_i`, `V`, and optional `T`.
- Remove `target_pressure`, `pressure_work`, and solver-objective wording from
  provider EOS derivative APIs, declarations, CMake/source manifests, and
  provider native SDK metadata.
- Preserve CppAD and implicit chain-rule coverage for Born, SSM/DS,
  relative-permittivity, and association site sensitivities.
- Keep provider scope limited to `packages/epcsaft`; do not change
  `epcsaft-equilibrium` route assembly beyond documented provider contract
  adjustments, and do not touch `epcsaft-regression`.

## Acceptance Criteria

- [x] Provider EOS derivative APIs no longer expose solver-objective names, target
  pressure, or pressure-work terms.
- [x] A local phase derivative bundle exposes the derivative orders needed by
  equilibrium without making provider EOS own an NLP objective.
- [x] Born, SSM/DS, relative-permittivity, and implicit association chain-rule
  coverage remains provider-owned and CppAD-backed.
- [x] Provider build lists, native SDK manifests, declarations, and focused provider
  tests use the new provider derivative interface.
- [x] No `packages/epcsaft-equilibrium` or `packages/epcsaft-regression`
  implementation behavior is changed except through documented provider
  contracts.

## Proof Oracle

- `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
- `uv run python run_pytest.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft/tests/native/state/test_eos_contributions.py packages/epcsaft/tests/native/contracts/test_provider_only_core_symbols.py -q`
- `rg -n "eos_phase_objective_derivatives_cpp|target_pressure|pressure_work" packages/epcsaft/src/epcsaft/native/eos`

## Non-Goals

- No equilibrium route assembly changes in this issue.
- No M5 regression package work.
- No public compatibility wrappers for old provider objective function names.

## Candidate Files

- `CMakeLists.txt`
- `packages/epcsaft/CMakeLists.txt`
- `packages/epcsaft/src/epcsaft/native/eos/**`
- `packages/epcsaft/src/epcsaft/native/model/native_types.h`
- `packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1/**`
- `packages/epcsaft/tests/native/state/**`
- `packages/epcsaft/tests/native/contracts/**`
- `tests/workflows/repo/test_package_extension_boundary.py`
- `tests/workflows/build/test_build_epcsaft.py`
