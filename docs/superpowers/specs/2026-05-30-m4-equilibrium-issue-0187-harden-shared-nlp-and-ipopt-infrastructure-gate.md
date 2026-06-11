# Harden shared NLP and Ipopt infrastructure gate

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/187`
Status: `open`
Last synced: `2026-06-02`

## Summary

Build the shared GFPE NLP and Ipopt infrastructure only after the pretreatment/selector gate is hardened, keeping Ipopt behavior explicit and testable.

## Acceptance Gates

- [ ] Shared NLP assembly owns variable layout, constraints, scaling, bounds, and diagnostics for neutral GFPE routes.
- [ ] Ipopt option handling is package-owned and tested without leaking provider-core assumptions.
- [ ] Postsolve diagnostic payloads preserve enough evidence for later HELD/TPD certification.
- [ ] Failure modes are loud and distinguish solver failure from inadmissible route state.

## Source Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`

## Implementation Notes

- Keep this issue in `equilibrium` scope unless the
  GitHub issue explicitly approves cross-milestone work.
- Preserve capability claims and backend labels unless the proof oracle records
  matching implementation evidence.
- Use the linked issue mirror and plan as the execution entry points for
  `project-resolve`.

## Non-Goals

- No HELD/TPD production admission in this slice.
- No associating/electrolyte/reactive admission.
- No fake no-Ipopt success path.

## Validation

- Run focused Ipopt package-local native/API tests.
- Run native contracts.
- Run docs validation.
