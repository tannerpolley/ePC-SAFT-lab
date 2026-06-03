# Harden GFPE pretreatment and selector admission pipeline

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/186`
Status: `open`
Last synced: `2026-06-02`

## Summary

Harden the early GFPE pretreatment, closure, stage-state, and selector/admission pipeline so later Ipopt/GFPE work starts from deterministic package-local contracts instead of route-specific assumptions.

## Acceptance Gates

- [ ] GFPE input and runtime state contracts are package-owned and deterministic.
- [ ] Pretreatment and selector/admission logic has focused tests for admissible and rejected route states.
- [ ] Legacy route-specific assumptions are either removed or isolated behind explicit tests.
- [ ] Capability evidence remains conservative and does not broaden production routes.
- [ ] Docs and local mirrors identify this as the first ready M4 GFPE implementation issue.

## Source Context

- `docs/superpowers/specs/2026-05-26-m4-equilibrium-generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`

## Implementation Notes

- Keep this issue in `equilibrium` scope unless the
  GitHub issue explicitly approves cross-milestone work.
- Preserve capability claims and backend labels unless the proof oracle records
  matching implementation evidence.
- Use the linked issue mirror and plan as the execution entry points for
  `project-resolve`.

## Non-Goals

- No associating LLE admission.
- No electrolyte or reactive route admission.
- No public API rename.
- No release publication.

## Validation

- Run focused package-local equilibrium API/native tests for selector/admission.
- Run native contracts for activation/capability boundaries.
- Run docs validation.
