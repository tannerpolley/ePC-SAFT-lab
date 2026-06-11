---
issue: 188
title: "M4: prove source-backed neutral TP-flash GFPE fixture after HELD gate"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/188"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0188-prove-source-backed-neutral-tp-flash-gfpe-fixture-after-held-gate.md"
source_plan: "docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0188-prove-source-backed-neutral-tp-flash-gfpe-fixture-after-held-gate-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0188-prove-source-backed-neutral-tp-flash-gfpe-fixture-after-held-gate
last_synced: "2026-06-11"
---

# Prove source-backed neutral TP-flash GFPE fixture after HELD gate

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/188
Source Spec: docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0188-prove-source-backed-neutral-tp-flash-gfpe-fixture-after-held-gate.md
Source Plan: docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0188-prove-source-backed-neutral-tp-flash-gfpe-fixture-after-held-gate-plan.md
Branch: codex/issue-0188-prove-source-backed-neutral-tp-flash-gfpe-fixture-after-held-gate
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

After HELD/TPD and shared NLP gates, prove a source-backed neutral TP-flash GFPE fixture with executable evidence rather than synthetic-only route confidence.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`

## Acceptance Criteria

- [x] Neutral TP-flash fixture is tied to documented source data or a clearly recorded validation source.
- [x] HELD/TPD certification is used as an admission prerequisite.
- [x] Result diagnostics prove conservation, pressure/fugacity consistency, phase distinctness, and candidate completeness.
- [x] Capabilities remain honest about exact supported route scope.

## Resolution Notes

- The hydrocarbon workbook TP-flash fixture remains the source-backed PC-SAFT
  validation target.
- `scripts/validation/check_neutral_tp_flash_fixture.py` now reports the
  `held_tpd_admission` gate from the complete phase-discovery payload before
  admitting the fixture route.
- The same checker fails closed unless route diagnostics prove TPD postsolve
  certification, candidate completeness, a certified phase set, positive phase
  distance, selected-candidate count, material balance, pressure consistency,
  fugacity consistency, source phase compositions, and source phase fractions.
- The M4 registry still keeps generalized PE-Neutral TP Flash
  `planned_not_public`; this issue does not broaden associating,
  electrolyte, reactive, multiphase, or benchmark-registry closure claims.

## Proof Oracle

- Run focused neutral TP-flash package-local equilibrium tests.
- Run native contracts.
- Run docs validation.

## Non-Goals And Boundaries

- No associating LLE admission.
- No electrolyte/reactive route admission.
- No benchmark registry closure beyond this fixture.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `HITL`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
