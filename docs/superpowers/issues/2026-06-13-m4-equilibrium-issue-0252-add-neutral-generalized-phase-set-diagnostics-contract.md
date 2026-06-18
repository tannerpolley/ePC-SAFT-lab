---
issue: 252
title: "M4: add neutral generalized phase-set diagnostics contract"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/252"
state: "closed"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "closed"
release_target: "equilibrium-0.x"
source_spec: null
source_plan: null
afk_hitl: "AFK"
branch: null
last_synced: "2026-06-13"
---

# M4: add neutral generalized phase-set diagnostics contract

**Mirror Retention:** Keep

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/252
Parent Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/189
Source Plan: docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md
Branch: codex/issue-0252-neutral-generalized-phase-set-diagnostics
AFK/HITL: AFK

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Implement the first AFK slice under #189: make the internal neutral generalized
phase-set path expose and validate deterministic phase-set diagnostic records
without public route admission.

## Acceptance Criteria

- [x] `neutral_multiphase_nonassoc` remains internal-only and absent from public route/capability surfaces.
- [x] Internal neutral multiphase diagnostics expose complete phase-set records for at least one three-phase neutral state.
- [x] Each selected or rejected record carries phase count, phase kind/role, source, phase amount or fraction, volume or density evidence, composition, objective or TPD evidence, feasibility status, selected/rejected status, and rejection reason when rejected.
- [x] A retained checker fails on missing records, malformed rows, mass-balance infeasibility, collapsed or duplicate phases, uncertified phase sets, or accidental public route exposure.
- [x] `PE-Generalized Multiphase` remains `planned_not_public`; docs and registry text do not claim public generalized multiphase, associating LLLE, electrolyte, or reactive support.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
```

## Validation Evidence

Recorded on 2026-06-13 from branch
`codex/issue-0252-neutral-generalized-phase-set-diagnostics`.

- `uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4` passed.
- `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q` passed: 3 tests.
- `uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_phase_set_checker.py -q` passed: 7 tests.
- `uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete` passed with no blockers, 3 selected rows, 3 rejected rows, and no public route exposure.
- `uv run --no-sync python scripts/dev/validate_project.py docs` passed.

## Closeout

Closed by PR https://github.com/ePC-SAFT/ePC-SAFT/pull/255 on
2026-06-13T14:13:58Z. This advances #189 with internal neutral generalized
phase-set diagnostic records only; #189 remains open for boundary workflows,
source-backed generalized phase-set validation, and final public admission
gates.

## Non-Goals And Boundaries

- No public `neutral_multiphase_nonassoc` route exposure.
- No associating, electrolyte, reactive, CE, or CPE admission.
- No boundary workflow admission in this issue.
- No closure of #189 unless all umbrella gates are separately proven.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `AFK`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, agent-ready, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
