# Derive boundary workflows and generalized phase-set PE from neutral GFPE

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`
Status: `open`
Last synced: `2026-06-02`

## Summary

Generalize from the neutral GFPE proof into boundary workflows and phase-set phase-equilibrium behavior without losing route certification or capability honesty.

## Acceptance Gates

- [ ] Boundary workflows are derived from the certified neutral GFPE path, not special-cased route copies.
- [ ] Generalized phase-set PE exposes deterministic diagnostics for selected and rejected phase sets.
- [ ] Tests cover phase-set selection, conservation, residuals, and rejection of uncertified solutions.
- [ ] Docs explain what generalized phase-set behavior is supported and what remains blocked.

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

- No associating/electrolyte/reactive route admission unless separately proven.
- No public route broadening without capability evidence.
- No release publication.

## Validation

- Run focused equilibrium phase-set workflow tests.
- Run native contracts.
- Run docs validation.
