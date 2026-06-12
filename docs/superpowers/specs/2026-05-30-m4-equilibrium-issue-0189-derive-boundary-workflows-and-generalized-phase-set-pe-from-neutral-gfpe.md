# Derive boundary workflows and generalized phase-set PE from neutral GFPE

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/189`
Status: `open`
Last synced: `2026-06-02`
Updated: `2026-06-12`

## Summary

Generalize from the neutral GFPE proof into boundary workflows and phase-set phase-equilibrium behavior without losing route certification or capability honesty.

This issue is also the natural owner for the Pereira-style all-phase completion
gap unless planning splits it: HELD cannot be treated as generalized phase-set
adoption until the candidate phase set can satisfy the global feed mass balance,
reject duplicate or collapsed phases, and prove completeness beyond a fixed
two-phase route.

## Acceptance Gates

- [ ] Boundary workflows are derived from the certified neutral GFPE path, not special-cased route copies.
- [ ] Generalized phase-set PE exposes deterministic diagnostics for selected and rejected phase sets.
- [ ] Tests cover phase-set selection, conservation, residuals, and rejection of uncertified solutions.
- [ ] Docs explain what generalized phase-set behavior is supported and what remains blocked.
- [ ] HELD completion cannot be reported while the candidate phase set fails
  the global feed mass-balance feasibility test.
- [ ] Phase-set records include phase count, phase kind, source, amount,
  volume, composition, objective value, feasibility, candidate origin, and
  status for selected and rejected phases.
- [ ] Duplicate, collapsed, lower-free-energy, and uncertified phase sets are
  rejected with distinct diagnostics.
- [ ] LLLE-ready neutral phase-set evidence is separated from associating LLLE
  admission; associating LLLE remains blocked until #145/#190 derivative and
  source-backed evidence exists.

## Source Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
- `docs/papers/md/Equilibrium/Pereira et al. - 2012 - The HELD algorithm for multicomponent, multiphase equilibrium calculations with generic equations of.md`

## Implementation Notes

- Keep this issue in `equilibrium` scope unless the
  GitHub issue explicitly approves cross-milestone work.
- Preserve capability claims and backend labels unless the proof oracle records
  matching implementation evidence.
- Use the linked issue mirror and plan as the execution entry points for
  `project-resolve`.
- Treat boundary workflows as degree-of-freedom swaps over a certified neutral
  GFPE path.
- Treat generalized phase-set PE as unknown phase-count discovery and
  certification, not repeated two-phase route calls.
- Treat Pereira 2012 LLLE examples as algorithm context unless local model
  parity or source-backed ePC-SAFT-compatible fixtures exist.

## Non-Goals

- No associating/electrolyte/reactive route admission unless separately proven.
- No public route broadening without capability evidence.
- No release publication.
- No associating LLLE claim from neutral LLLE-ready mechanics.

## Validation

- Run focused equilibrium phase-set workflow tests.
- Run native contracts.
- Run HELD phase-discovery checker with route refinement when phase-discovery
  diagnostics are touched.
- Run docs validation.
