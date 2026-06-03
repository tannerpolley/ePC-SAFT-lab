---
issue: 186
title: "M4: harden GFPE pretreatment and selector admission pipeline"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/186"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0186-harden-gfpe-pretreatment-and-selector-admission-pipeline.md"
source_plan: "docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0186-harden-gfpe-pretreatment-and-selector-admission-pipeline-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0186-harden-gfpe-pretreatment-and-selector-admission-pipeline
last_synced: "2026-06-02"
---

# Harden GFPE pretreatment and selector admission pipeline

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/186
Source Spec: docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0186-harden-gfpe-pretreatment-and-selector-admission-pipeline.md
Source Plan: docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0186-harden-gfpe-pretreatment-and-selector-admission-pipeline-plan.md
Branch: codex/issue-0186-harden-gfpe-pretreatment-and-selector-admission-pipeline
AFK/HITL: AFK

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Harden the early GFPE pretreatment, closure, stage-state, and selector/admission pipeline so later Ipopt/GFPE work starts from deterministic package-local contracts instead of route-specific assumptions.

## Supplemental Context

- `docs/superpowers/specs/2026-05-26-m4-equilibrium-generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`

## Acceptance Criteria

- [ ] GFPE input and runtime state contracts are package-owned and deterministic.
- [ ] Pretreatment and selector/admission logic has focused tests for admissible and rejected route states.
- [ ] Legacy route-specific assumptions are either removed or isolated behind explicit tests.
- [ ] Capability evidence remains conservative and does not broaden production routes.
- [ ] Docs and local mirrors identify this as the first ready M4 GFPE implementation issue.

## Proof Oracle

- Run focused package-local equilibrium API/native tests for selector/admission.
- Run native contracts for activation/capability boundaries.
- Run docs validation.

## Non-Goals And Boundaries

- No associating LLE admission.
- No electrolyte or reactive route admission.
- No public API rename.
- No release publication.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `AFK`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
