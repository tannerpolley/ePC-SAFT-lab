---
issue: 189
title: "M4: derive boundary workflows and generalized phase-set PE from neutral GFPE"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/189"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "blocked"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md"
source_plan: "docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe
last_synced: "2026-06-02"
---

# Derive boundary workflows and generalized phase-set PE from neutral GFPE

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/189
Source Spec: docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md
Source Plan: docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md
Branch: codex/issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Generalize from the neutral GFPE proof into boundary workflows and phase-set phase-equilibrium behavior without losing route certification or capability honesty.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`

## Acceptance Criteria

- [ ] Boundary workflows are derived from the certified neutral GFPE path, not special-cased route copies.
- [ ] Generalized phase-set PE exposes deterministic diagnostics for selected and rejected phase sets.
- [ ] Tests cover phase-set selection, conservation, residuals, and rejection of uncertified solutions.
- [ ] Docs explain what generalized phase-set behavior is supported and what remains blocked.

## Proof Oracle

- Run focused equilibrium phase-set workflow tests.
- Run native contracts.
- Run docs validation.

## Non-Goals And Boundaries

- No associating/electrolyte/reactive route admission unless separately proven.
- No public route broadening without capability evidence.
- No release publication.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `blocked`
- AFK/HITL: `HITL`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature`
