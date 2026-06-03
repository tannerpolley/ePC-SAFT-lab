# Admit associating GFPE through exact derivative proof gates

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/190`
Status: `open`
Last synced: `2026-06-02`

## Summary

Admit associating GFPE only after the exact-derivative and associating-route proof gates are satisfied, preserving the blocked relationship from associating LLE to its prerequisites.

## Acceptance Gates

- [ ] Associating route admission requires exact association derivative evidence appropriate to the tested association configuration.
- [ ] Approximate explicit association closures remain labeled approximate and are not accepted as exact production proof.
- [ ] Associating GFPE diagnostics distinguish EOS closure, derivative, solver, and postsolve certification failures.
- [ ] Capability evidence names the exact associating configurations proven.

## Source Context

- `docs/superpowers/specs/2026-05-26-m4-equilibrium-generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`

## Implementation Notes

- Keep this issue in `equilibrium` scope unless the
  GitHub issue explicitly approves cross-milestone work.
- Preserve capability claims and backend labels unless the proof oracle records
  matching implementation evidence.
- Use the linked issue mirror and plan as the execution entry points for
  `project-resolve`.

## Non-Goals

- No approximate association closure as production exact proof.
- No broad associating LLE claim from a single narrow fixture.
- No electrolyte/reactive admission.

## Validation

- Run focused associating EOS/derivative tests required by the gate.
- Run focused associating equilibrium package tests.
- Run docs validation.
