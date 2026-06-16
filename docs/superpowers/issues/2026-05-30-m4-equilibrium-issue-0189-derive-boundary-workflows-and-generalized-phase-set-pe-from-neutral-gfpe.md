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
readiness: "ready"
release_target: "equilibrium-0.x"
source_spec: "docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md"
source_plan: "docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md"
afk_hitl: "HITL"
branch: codex/issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe
last_synced: "2026-06-16"
---

# Derive boundary workflows and generalized phase-set PE from neutral GFPE

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/189
Source Spec: docs/superpowers/specs/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md
Source Plan: docs/superpowers/plans/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe-plan.md
Branch: codex/issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe
AFK/HITL: HITL umbrella; #252, #256, #258, and #260 closed as AFK child issues; #261 is the current ready AFK child for generalized phase-set certification.

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Generalize from the neutral GFPE proof into boundary workflows and phase-set phase-equilibrium behavior without losing route certification or capability honesty.

#189 is no longer dependency-blocked after #188 and #241 closed. It remains the
HITL umbrella for boundary workflows and generalized phase-set PE. #252 closed
the first AFK implementation slice for neutral generalized phase-set
diagnostics; #256 closed through #257 with retained bubble/dew boundary traces
and stricter generalized phase-set rejection diagnostics; #258 closed through
#259 with the retained cloud/shadow source-data gate while keeping native route
admission closed; #260 closed through #262 with checker-gated native isobaric
cloud/shadow route evidence while keeping public cloud/shadow route keys
closed. #261 is the current ready AFK child and owns the next generalized
phase-set certification gate:
Stage II candidate-set replay plus strict Stage III Ipopt refinement for the
requested neutral multiphase phase-kind list. The umbrella remains open until
generalized phase-set completion and public capability admission gates are
separately proven.

## Supplemental Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `https://github.com/ePC-SAFT/ePC-SAFT/issues/252`
- `https://github.com/ePC-SAFT/ePC-SAFT/issues/253`
- `https://github.com/ePC-SAFT/ePC-SAFT/issues/256`
- `https://github.com/ePC-SAFT/ePC-SAFT/issues/258`
- `https://github.com/ePC-SAFT/ePC-SAFT/issues/260`
- `https://github.com/ePC-SAFT/ePC-SAFT/issues/261`

## Acceptance Criteria

- [ ] Boundary workflows are derived from the certified neutral GFPE path, not special-cased route copies.
- [ ] Generalized phase-set PE exposes deterministic diagnostics for selected and rejected phase sets.
- [ ] Tests cover phase-set selection, conservation, residuals, and rejection of uncertified solutions.
- [ ] Docs explain what generalized phase-set behavior is supported and what remains blocked.

## Proof Oracle

- Run focused equilibrium phase-set workflow tests.
- Run native contracts.
- Run docs validation.
- For #252, run `uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --require-complete` after implementation.
- For #256, run `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-current-boundary-route --allow-route-sweep --route-point-count 1 --require-complete` and keep `check_generalized_phase_set.py --json --require-complete` green.
- For #258, run `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --cloud-shadow-gate --require-cloud-shadow-gate` and keep the neutral LLE showcase checker green.
- For #260, run `uv run --no-sync python scripts/validation/check_boundary_workflows.py --json --run-cloud-shadow-route --require-cloud-shadow-route` after implementation and keep the #258 source-data gate green.
- For #261, run `uv run --no-sync python scripts/validation/check_generalized_phase_set.py --json --phase-kinds liquid,liquid,liquid --run-route-refinement --require-route-refinement --require-complete` and keep #260 route evidence green.

## Non-Goals And Boundaries

- No associating/electrolyte/reactive route admission unless separately proven.
- No public route broadening without capability evidence.
- No release publication.

## Tracker Metadata

- Milestone: `M4 - Equilibrium`
- Package: `equilibrium`
- Capability: `lle`
- Backend: `Ipopt`
- Readiness: `ready`
- AFK/HITL: `HITL umbrella; #252, #256, #258, and #260 closed; #261 ready`
- Release target: `equilibrium-0.x`
- Labels: `enhancement, native, solver, docs, validation, equilibrium, area:equilibrium, backend:ipopt, status:ready, type:feature`
