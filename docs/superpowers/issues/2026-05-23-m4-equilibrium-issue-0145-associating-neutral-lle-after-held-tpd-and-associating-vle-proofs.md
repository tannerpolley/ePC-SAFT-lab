---
issue: 145
title: "Associating neutral LLE after HELD/TPD and associating VLE proofs"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/145"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs.md"
source_plan: "docs/superpowers/plans/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs
last_synced: "2026-06-17"
---

# Associating neutral LLE after HELD/TPD and associating VLE proofs

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/145
Source Spec: docs/superpowers/specs/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs.md
Source Plan: docs/superpowers/plans/2026-05-23-m4-equilibrium-issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs-plan.md
Branch: codex/issue-0145-associating-neutral-lle-after-held-tpd-and-associating-vle-proofs
AFK/HITL: HITL

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

#148 is closed, so the native GitHub dependency blocker for this issue is
satisfied. #145 is ready for its own associating neutral LLE proof scope; this
does not admit associating GFPE or electrolyte GFPE behavior.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`

## Acceptance Criteria

- [ ] GitHub issue #145 outcome is satisfied without broadening unrelated package capability claims.

## Proof Oracle

- uv run python scripts/dev/validate_project.py quick

## Non-Goals And Boundaries

- No unrelated package, milestone, or public API scope should be added.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `HITL`
- Release target: `equilibrium-0.x`
- Labels: `python-api, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
