---
issue: 207
title: "Expose objective-free local phase EOS derivative bundle"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/207"
state: "closed"
milestone: "M3 - EOS"
project: "ePC-SAFT Roadmap"
package: "core"
capability: "derivatives"
backend: "CppAD"
readiness: "closed"
release_target: "core-0.x"
source_spec: null
source_plan: null
afk_hitl: "AFK"
branch: null
last_synced: "2026-06-08"
---

# Expose objective-free local phase EOS derivative bundle

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/207
Synced Commit: https://github.com/ePC-SAFT/ePC-SAFT/commit/58bcf830
AFK/HITL: AFK
**Mirror Retention:** Keep

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This closed mirror exists because #208
depends on #207 and local M4 planning needs a durable repo-local reference.

## Summary

Provider EOS exposes an objective-free local phase thermodynamic derivative
bundle with CppAD/implicit chain-rule coverage. The provider contract has no
equilibrium objective, target-pressure, or pressure-work semantics.

## Acceptance Criteria

- [x] Provider EOS derivative APIs no longer expose solver-objective names,
  target pressure, or pressure-work terms.
- [x] A local phase derivative bundle exposes the derivative orders needed by
  equilibrium without making provider EOS own an NLP objective.
- [x] Born, SSM/DS, relative-permittivity, and implicit association chain-rule
  coverage remains provider-owned and CppAD-backed.
- [x] Provider build lists, native SDK manifests, declarations, and focused
  provider tests use the provider derivative interface.
- [x] No `packages/epcsaft-equilibrium` or `packages/epcsaft-regression`
  implementation behavior changed except through documented provider contracts.

## Proof Oracle

- `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
- `uv run python run_pytest.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft/tests/native/state/test_eos_contributions.py packages/epcsaft/tests/native/contracts/test_provider_only_core_symbols.py -q`
- `rg -n "eos_phase_objective_derivatives_cpp|target_pressure|pressure_work" packages/epcsaft/src/epcsaft/native/eos`

## Tracker Metadata

- Milestone: `M3 - EOS`
- Package: `core`
- Capability: `derivatives`
- Backend: `CppAD`
- Readiness: `closed`
- AFK/HITL: `AFK`
- Release target: `core-0.x`
- Labels: `agent-ready, native, area:core, area:derivatives, backend:cppad, type:task`
