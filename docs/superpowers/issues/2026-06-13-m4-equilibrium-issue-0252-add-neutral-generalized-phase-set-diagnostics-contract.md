---
issue: 252
title: "M4: add neutral generalized phase-set diagnostics contract"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/252"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md"
source_plan: "docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0252-neutral-generalized-phase-set-diagnostics
last_synced: "2026-06-13"
---

# M4: add neutral generalized phase-set diagnostics contract

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

- [ ] `neutral_multiphase_nonassoc` remains internal-only and absent from public route/capability surfaces.
- [ ] Internal neutral multiphase postsolve diagnostics expose complete phase-set records for at least one three-phase neutral state.
- [ ] Each selected or rejected record carries phase count, phase kind/role, source, phase amount or fraction, volume or density evidence, composition, objective or TPD evidence, feasibility status, selected/rejected status, and rejection reason when rejected.
- [ ] A retained checker fails on missing records, malformed rows, mass-balance infeasibility, collapsed or duplicate phases, uncertified phase sets, or accidental public route exposure.
- [ ] `PE-Generalized Multiphase` remains `planned_not_public`; docs and registry text must not claim public generalized multiphase, associating LLLE, electrolyte, or reactive support.

## Proof Oracle

```powershell
uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py -q
uv run --no-sync python run_pytest.py packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py tests/native/contracts/test_generalized_phase_set_checker.py -q
uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete
uv run --no-sync python scripts/dev/validate_project.py docs
```

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
