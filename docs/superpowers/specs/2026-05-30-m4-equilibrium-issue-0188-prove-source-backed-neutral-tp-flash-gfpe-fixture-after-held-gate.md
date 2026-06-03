# Prove source-backed neutral TP-flash GFPE fixture after HELD gate

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/188`
Status: `open`
Last synced: `2026-06-02`

## Summary

After HELD/TPD and shared NLP gates, prove a source-backed neutral TP-flash GFPE fixture with executable evidence rather than synthetic-only route confidence.

## Acceptance Gates

- [ ] Neutral TP-flash fixture is tied to documented source data or a clearly recorded validation source.
- [ ] HELD/TPD certification is used as an admission prerequisite.
- [ ] Result diagnostics prove conservation, pressure/fugacity consistency, phase distinctness, and candidate completeness.
- [ ] Capabilities remain honest about exact supported route scope.

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
- No electrolyte/reactive route admission.
- No benchmark registry closure beyond this fixture.

## Validation

- Run focused neutral TP-flash package-local equilibrium tests.
- Run native contracts.
- Run docs validation.
