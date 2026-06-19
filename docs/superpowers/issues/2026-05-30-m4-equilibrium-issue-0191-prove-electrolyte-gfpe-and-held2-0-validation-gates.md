---
issue: 191
title: "M4: prove electrolyte GFPE and HELD2.0 validation gates"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/191"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "electrolyte"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
source_plan: "docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates
last_synced: "2026-06-19"
---

# Prove electrolyte GFPE and HELD2.0 validation gates

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/191
Source Spec: docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
Source Plan: docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md
Branch: codex/issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates
AFK/HITL: HITL

**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/191
**GitHub Milestone:** M4 - Equilibrium
**Issue Type:** Feature
**Source Spec:** docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md
**Source Plan:** docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md
**Classification:** HITL
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Prove electrolyte GFPE and HELD2.0 validation gates after the neutral generalized phase-set path is certified and the Gross 2002 association acceptance campaign proves the associating premise that electrolyte work would otherwise rely on.

## Blocking Prerequisites

- [#275](2026-06-18-m4-equilibrium-issue-0275-add-gross-2002-paper-validation-association-acceptance-campaign.md) is open and blocks #191. It adds the Gross/Sadowski 2002 paper-validation association acceptance campaign under `analyses/paper_validation/2002_gross`, with Figures 8 and 10 as hard phase-split gates.
- #189 is already closed and remains only as historical dependency provenance.

## Child Issues

- [#269](2026-06-17-m4-equilibrium-issue-0269-add-electrolyte-gfpe-closed-admission-source-gate.md) closed the first #191 child gate. It proved the Khudaida source fixture, explicit-ion expansion, path-based paper-validation parameter-bundle execution, native electrolyte/charge diagnostics, and public route boundary state. It did not admit public electrolyte GFPE, electrolyte TPD, HELD2 phase discovery, or electrolyte postsolve certification.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/superpowers/plans/2026-06-17-m4-equilibrium-issue-0191-electrolyte-gfpe-closed-admission-gate-plan.md`

## Acceptance Criteria

- [ ] Electrolyte GFPE route admission is gated by source-backed validation and postsolve certification.
- [ ] HELD2.0 diagnostics cover electrolyte-specific stability/candidate evidence.
- [ ] Capability evidence distinguishes neutral, associating, electrolyte, and reactive support.
- [ ] Docs do not claim electrolyte production support before executable evidence passes.

## Proof Oracle

- Run focused electrolyte equilibrium tests when implemented.
- Run native contracts.
- Run docs validation.

## Non-Goals And Boundaries

- No reactive route admission.
- No associating shortcut around exact derivative gates.
- No publication or release claim.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `electrolyte`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `HITL`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
