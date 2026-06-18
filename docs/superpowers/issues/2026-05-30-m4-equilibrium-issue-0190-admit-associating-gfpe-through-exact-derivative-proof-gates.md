---
issue: 190
title: "M4: admit associating GFPE through exact derivative proof gates"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/190"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md"
source_plan: "docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates
last_synced: "2026-06-18"
---

# Admit associating GFPE through exact derivative proof gates

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/190
Source Spec: docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates.md
Source Plan: docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates-plan.md
Branch: codex/issue-0190-admit-associating-gfpe-through-exact-derivative-proof-gates
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Admit associating GFPE only after the exact-derivative and associating-route proof gates are satisfied, preserving the blocked relationship from associating LLE to its prerequisites. The #145 branch now provides the immediate prerequisite internal proof: Gross/Sadowski 2002 methanol/cyclohexane source data, exact association Hessian diagnostics, and closed public admission. #190 should become the next public-admission issue after #145 merges.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`
- `data/reference/equilibrium_benchmarks/associating_lle/gross_2002_methanol_cyclohexane`
- `scripts/validation/check_associating_lle_gross_2002.py`

## Acceptance Criteria

- [ ] Associating route admission requires exact association derivative evidence appropriate to the tested association configuration.
- [ ] Approximate explicit association closures remain labeled approximate and are not accepted as exact production proof.
- [ ] Associating GFPE diagnostics distinguish EOS closure, derivative, solver, and postsolve certification failures.
- [ ] Capability evidence names the exact associating configurations proven.

## Proof Oracle

- Confirm the #145 prerequisite remains green:
  `uv run python scripts/validation/check_associating_lle_gross_2002.py --json --require-source-data --require-exact-association-hessian --require-route-closed --require-complete`.
- Run focused associating EOS/derivative tests required by the gate.
- Run focused associating equilibrium package tests.
- Run docs validation.

## Non-Goals And Boundaries

- No approximate association closure as production exact proof.
- No broad associating LLE claim from a single narrow fixture.
- No electrolyte/reactive admission.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `HITL`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
