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
readiness: "blocked"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates.md"
source_plan: "docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0191-prove-electrolyte-gfpe-and-held2-0-validation-gates
last_synced: "2026-06-25"
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
**Labels:** enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature
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

Prove electrolyte GFPE and HELD2.0 validation gates after the neutral generalized phase-set path, associating prerequisite evidence, electrolyte source gate, reduced-basis/Born exactness gate, electrolyte TPD screening gate, HELD2 phase discovery, Stage III electrolyte refinement, postsolve certification, and public route-admission gates are each proven by retained evidence.

## Closed Prerequisites And Remaining Gates

- #189, #275, #286, #300, and #302 are closed and remain only as historical dependency provenance.
- #306 is the active open child blocker. It owns HELD2 counterion-pair phase-discovery evidence in reduced electroneutral coordinates.
- After #306 closes, the remaining gates are Stage III electrolyte refinement, postsolve electrolyte phase-set certification, and public electrolyte route admission.

## Child Issues

- [#269](2026-06-17-m4-equilibrium-issue-0269-add-electrolyte-gfpe-closed-admission-source-gate.md) closed the first #191 child gate. It proved the Khudaida source fixture, explicit-ion expansion, path-based paper-validation parameter-bundle execution, native electrolyte/charge diagnostics, and public route boundary state. It did not admit public electrolyte GFPE, electrolyte TPD, HELD2 phase discovery, or electrolyte postsolve certification.
- [#300](2026-06-24-m4-equilibrium-issue-0300-add-electrolyte-held2-readiness-and-born-exactness-gate.md) closed the reduced electroneutral variable and Born SSM/DS exactness readiness gate. It proved the exact charge-neutral NaCl amount lift, CppAD Born SSM/DS composition, fugacity, activity-parameter, `d_born`, and `f_solv` derivative receipts, and kept public electrolyte route admission closed.
- [#302](2026-06-24-m4-equilibrium-issue-0302-add-electrolyte-charge-neutral-tpd-gate.md) closed the native-backed charge-neutral electrolyte TPD screening gate. It proves three finite source-backed candidates, selected candidate count `2`, minimum TPD `-0.010922388988229025`, maximum charge residual `0.0`, readiness-only HELD2 status, and closed public electrolyte route state. It does not close HELD2 dual discovery, Stage III electrolyte refinement, postsolve electrolyte phase-set certification, or public route admission.
- [#306](2026-06-25-m4-equilibrium-issue-0306-add-electrolyte-held2-counterion-pair-phase-discovery-gate.md) is the active ready child. It must add native reduced-coordinate HELD2 phase-discovery diagnostics with independent counterion-pair matrix rank evidence, charge-neutral candidates, mean-ionic residual bookkeeping, and closed public route state. It must not claim Stage III refinement, postsolve certification, or public electrolyte route admission.

## HELD2 Adoption Checkpoint Sequence

- Source and readiness checkpoints: #269, #300, and #302 remain prerequisite
  evidence for source fixtures, reduced electroneutral variables, Born SSM/DS
  derivatives, and charge-neutral TPD screening.
- #306 phase-discovery checkpoint: required diagnostics are counterion-pair
  matrix rank, reduced-coordinate lift/back-lift residuals, finite TPD
  candidate metrics, pair-based mean-ionic residual bookkeeping, closed public
  routes, and a Stage III handoff record.
- Stage III refinement checkpoint: consume the #306 candidate set and solve the
  electrolyte reduced-variable phase-set equations with exact residual
  derivative receipts.
- Postsolve checkpoint: certify explicit-ion material reconstruction,
  per-phase charge balance, neutral transfer, mean-ionic transfer, pressure
  consistency, phase amounts, and domain margins.
- Public admission checkpoint: consume all prior checkers and expose only the
  certified electrolyte route surface.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/superpowers/plans/2026-06-17-m4-equilibrium-issue-0191-electrolyte-gfpe-closed-admission-gate-plan.md`
- `docs/superpowers/plans/2026-06-25-m4-equilibrium-issue-0306-electrolyte-held2-counterion-pair-phase-discovery-gate-plan.md`
- `docs/papers/md/Equilibrium/Ascani, Sadowski, Held - 2022 - Calculation of Multiphase Equilibria Containing Mixed Solvents and M.md`
- `docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md`

## Acceptance Criteria

- [ ] HELD2 counterion-pair phase discovery consumes #269, #300, and #302 evidence and reports full-rank reduced-coordinate diagnostics.
- [ ] Stage III electrolyte refinement consumes the HELD2 candidate set and solves in reduced electroneutral variables.
- [ ] Postsolve electrolyte certification reports material, charge, pressure, neutral transfer, mean-ionic transfer, and domain diagnostics.
- [ ] Electrolyte GFPE route admission is gated by source-backed validation and postsolve certification.
- [ ] Capability evidence distinguishes neutral, associating, electrolyte, and reactive support.
- [ ] Docs do not claim electrolyte production support before executable evidence passes.

## Proof Oracle

- Run the active child proof oracle.
- Run focused electrolyte equilibrium tests when implemented by a child gate.
- Run native contracts for changed native diagnostics.
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
- Readiness: `blocked`
- AFK/HITL: `HITL`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:blocked, type:feature`
