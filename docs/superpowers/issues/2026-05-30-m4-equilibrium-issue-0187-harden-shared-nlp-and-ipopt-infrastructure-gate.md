---
issue: 187
title: "M4: harden shared NLP and Ipopt infrastructure gate"
url: https://github.com/ePC-SAFT/ePC-SAFT/issues/187
state: closed
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: equilibrium
capability: lle
backend: Ipopt
readiness: closed
release_target: equilibrium-0.x
source_spec: null
source_plan: null
afk_hitl: HITL
branch: null
last_synced: "2026-06-11"
---

# Harden shared NLP and Ipopt infrastructure gate

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/187
Source Spec: docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate.md
Source Plan: docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate-plan.md
Branch: codex/issue-0187-harden-shared-nlp-and-ipopt-infrastructure-gate
AFK/HITL: HITL

Closed by https://github.com/ePC-SAFT/ePC-SAFT/pull/242 on 2026-06-11.

**Mirror Retention:** Keep this closed mirror as historical context for the
HELD 1.0 Stage II queue handoff to #241.

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror is retained only to preserve the
closed prerequisite context for the M4 queue.

## Summary

Build the shared GFPE NLP and Ipopt infrastructure only after the pretreatment/selector gate is hardened, keeping Ipopt behavior explicit and testable.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`

## Acceptance Criteria

- [ ] Shared NLP assembly owns variable layout, constraints, scaling, bounds, and diagnostics for neutral GFPE routes.
- [ ] Ipopt option handling is package-owned and tested without leaking provider-core assumptions.
- [ ] Postsolve diagnostic payloads preserve enough evidence for later HELD/TPD certification.
- [ ] Failure modes are loud and distinguish solver failure from inadmissible route state.

## Proof Oracle

- Run focused Ipopt package-local native/API tests.
- Run native contracts.
- Run docs validation.

## Non-Goals And Boundaries

- No HELD/TPD production admission in this slice.
- No associating/electrolyte/reactive admission.
- No fake no-Ipopt success path.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `closed`
- AFK/HITL: `HITL`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
