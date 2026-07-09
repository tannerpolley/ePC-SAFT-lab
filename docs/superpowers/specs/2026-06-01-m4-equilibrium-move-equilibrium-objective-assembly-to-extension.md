# Move Equilibrium Objective Assembly Onto Provider Derivative Bundles

GitHub issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/208

## Summary

`epcsaft-equilibrium` should own pressure-transformed Helmholtz objective
assembly and exact NLP derivative payloads while consuming objective-free local
phase derivative bundles from provider EOS. This keeps thermodynamic chain-rule
coverage provider-owned and route/NLP assembly equilibrium-owned.

## Key Changes

- Build pressure-transformed Helmholtz objective terms, pressure-work
  derivatives, gradients, Hessians, and third-derivative tensors inside
  `epcsaft-equilibrium`.
- Consume the provider local phase derivative bundle instead of provider
  objective APIs that accept `target_pressure` or return solver objective
  values.
- Preserve existing public equilibrium behavior, backend labels,
  `EosPhaseBlockResult` payload shapes, exact-Hessian evidence, and NLP
  contract diagnostics.
- Keep scope limited to `packages/epcsaft-equilibrium` plus provider contract
  call-site updates; do not include HELD, phase discovery, full route rewrites,
  or M5 regression work.

## Acceptance Criteria

- Equilibrium constructs pressure-transformed Helmholtz objective terms,
  gradients, Hessians, third-derivative tensors, and pressure-work derivatives
  from the provider derivative bundle.
- No provider API called by equilibrium requires `target_pressure` or returns a
  solver objective value as a provider-owned concept.
- `EosPhaseBlockResult` and NLP contract evidence keep existing public/test
  payload shapes and exact derivative backend labels.
- M4 native CMake/source lists and focused equilibrium tests use the new
  assembly path.
- This issue is blocked by the M3 provider derivative bundle issue until that
  provider contract is merged.

## Proof Oracle

- `bash scripts/dev/cmake_preset.sh --action build --target epcsaft_equilibrium_native_core --parallel 10`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py -q`
- `uv run python scripts/dev/validate_project.py quick`

## Non-Goals

- No provider EOS equation theory changes beyond consuming the new bundle.
- No HELD, phase discovery, or full route rewrite.
- No M5 regression work.

## Candidate Files

- `CMakeLists.txt`
- `packages/epcsaft-equilibrium/CMakeLists.txt`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/blocks/**`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/derivatives/**`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/**`
- `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/**`
- `packages/epcsaft-equilibrium/tests/native/blocks/**`
- `packages/epcsaft-equilibrium/tests/native/diagnostics/**`
- `packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py`
- `tests/workflows/repo/test_project_structure.py`
