# Prove electrolyte GFPE and HELD2.0 validation gates

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/191`
Status: `open`
Last synced: `2026-06-02`

## Summary

Prove electrolyte GFPE and HELD2.0 validation gates after the neutral generalized phase-set path is certified.

## Acceptance Gates

- [ ] Electrolyte GFPE route admission is gated by source-backed validation and postsolve certification.
- [ ] HELD2.0 diagnostics cover electrolyte-specific stability/candidate evidence.
- [ ] Capability evidence distinguishes neutral, associating, electrolyte, and reactive support.
- [ ] Docs do not claim electrolyte production support before executable evidence passes.

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

- No reactive route admission.
- No associating shortcut around exact derivative gates.
- No publication or release claim.

## Validation

- Run focused electrolyte equilibrium tests when implemented.
- Run native contracts.
- Run docs validation.
