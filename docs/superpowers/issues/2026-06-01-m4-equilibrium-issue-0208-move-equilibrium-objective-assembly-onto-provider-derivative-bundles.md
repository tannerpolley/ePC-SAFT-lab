---
issue: 208
title: "Move equilibrium objective assembly onto provider derivative bundles"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/208"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "derivatives"
backend: "CppAD"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-06-01-m4-equilibrium-move-equilibrium-objective-assembly-to-extension.md"
source_plan: "docs/superpowers/plans/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles
last_synced: "2026-06-08"
---

# Move equilibrium objective assembly onto provider derivative bundles

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/208
Source Spec: docs/superpowers/specs/2026-06-01-m4-equilibrium-move-equilibrium-objective-assembly-to-extension.md
Source Plan: docs/superpowers/plans/2026-06-01-m4-equilibrium-issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles-plan.md
Branch: codex/issue-0208-move-equilibrium-objective-assembly-onto-provider-derivative-bundles
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

`epcsaft-equilibrium` owns pressure-transformed objective assembly and exact NLP derivative payloads while consuming objective-free provider local phase derivative bundles.

## Supplemental Context

- `docs/superpowers/specs/2026-05-26-m4-equilibrium-generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`

## Acceptance Criteria

- [ ] Equilibrium constructs pressure-transformed Helmholtz objective terms, gradients, Hessians, third-derivative tensors, and pressure-work derivatives from the provider derivative bundle.
- [ ] No provider API called by equilibrium requires `target_pressure` or returns a solver objective value as a provider-owned concept.
- [ ] `EosPhaseBlockResult` and NLP contract evidence keep existing public/test payload shapes and exact derivative backend labels.
- [ ] M4 native CMake/source lists and focused equilibrium tests use the new assembly path.
- [ ] The closed #207 provider derivative bundle contract is verified in the checkout before M4 route-assembly edits begin.

## Proof Oracle

- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/dev/cmake_preset.ps1 -Action Build -Target epcsaft_equilibrium_native_core -Parallel 10`
- `uv run python run_pytest.py packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py -q`
- `uv run python scripts/dev/validate_project.py quick`

## Non-Goals And Boundaries

- No provider EOS equation theory changes beyond consuming the new bundle.
- No HELD, phase discovery, or full route rewrite.
- No M5 regression work.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `derivatives`
- Backend: `CppAD`
- Readiness: `ready`
- AFK/HITL: `HITL`
- Release target: `equilibrium-0.x`
- Labels: `native, area:equilibrium, area:derivatives, backend:cppad, backend:ipopt, ready-for-human, type:task`
