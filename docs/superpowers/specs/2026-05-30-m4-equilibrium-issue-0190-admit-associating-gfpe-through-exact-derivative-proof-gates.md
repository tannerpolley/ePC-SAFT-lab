# Admit associating GFPE through exact derivative proof gates

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/190`
Status: `open`
Last synced: `2026-06-02`
Updated: `2026-06-12`

## Summary

Admit associating GFPE only after the exact-derivative and associating-route proof gates are satisfied, preserving the blocked relationship from associating LLE to its prerequisites.

Associating GFPE must be prepared as an extension of the neutral Pereira-style
HELD 1.0 path, not as an independent shortcut. Neutral Stage II/III closure is
necessary evidence, but associating admission still waits for fresh-native
receipts, neutral reliability/all-phase gates where claimed, and exact
association derivative coverage for the chosen source system.

After the neutral LLE reliability gate and exact association derivatives, #190
may start a narrow two-phase associating proof, but it cannot claim generalized
phase-set or associating LLLE coverage until #189 closes.

## Acceptance Gates

- [ ] Associating route admission requires exact association derivative evidence appropriate to the tested association configuration.
- [ ] Approximate explicit association closures remain labeled approximate and are not accepted as exact production proof.
- [ ] Associating GFPE diagnostics distinguish EOS closure, derivative, solver, and postsolve certification failures.
- [ ] Capability evidence names the exact associating configurations proven.
- [ ] The plan cites the current HELD 1.0 full-adoption spec and records which
  pre-associating gates are complete, which are deliberately out of scope for a
  two-phase associating proof, and which remain blockers for generalized
  phase-set claims.
- [ ] Association-specific postsolve checks include site bounds, mass-action
  residuals, contribution activation, and derivative block coverage.

## Source Context

- `docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md`
- `docs/superpowers/specs/2026-06-11-m4-equilibrium-held-1-0-full-adoption.md`
- `docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md`

## Implementation Notes

- Keep this issue in `equilibrium` scope unless the
  GitHub issue explicitly approves cross-milestone work.
- Preserve capability claims and backend labels unless the proof oracle records
  matching implementation evidence.
- Use the linked issue mirror and plan as the execution entry points for
  `project-resolve`.
- Do not use Held 2014 electrolyte literature as HELD 1.0 algorithm evidence;
  HELD 1.0 refers to the Pereira algorithm acronym.
- Do not treat neutral HELD reliability as proof of association derivative
  correctness.

## Non-Goals

- No approximate association closure as production exact proof.
- No broad associating LLE claim from a single narrow fixture.
- No electrolyte/reactive admission.
- No generalized phase-count or LLLE claim unless #189-style phase-set
  completeness is also proven.

## Validation

- Run focused associating EOS/derivative tests required by the gate.
- Run focused associating equilibrium package tests.
- Run the HELD/GFPE receipt gate if associating evidence reuses neutral
  phase-discovery diagnostics.
- Run docs validation.
