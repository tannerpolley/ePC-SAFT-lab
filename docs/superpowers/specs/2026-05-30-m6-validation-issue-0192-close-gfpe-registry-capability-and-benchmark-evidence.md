# Close GFPE registry, capability, and benchmark evidence

Milestone: `M6 - Validation`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/192`
Status: `open`
Last synced: `2026-06-02`

## Summary

Close the GFPE registry/capability/benchmark evidence after the relevant M4 proof gates exist, so user-facing capability claims match executable evidence.

## Acceptance Gates

- [ ] Algorithm registry entries point to executable GFPE evidence rather than planned-only claims.
- [ ] Capability evidence identifies proven neutral, associating, electrolyte, and reactive route scope separately.
- [ ] Benchmark or literature fixture metadata includes source, expected behavior, tolerances, and command receipts.
- [ ] Docs and tests fail if registry support claims outpace executable evidence.

## Source Context

- `docs/superpowers/specs/2026-05-29-m6-validation-validation-benchmark-backlog.md`
- `docs/superpowers/specs/2026-05-26-m4-equilibrium-generalized-fluid-phase-equilibrium.md`

## Implementation Notes

- Keep this issue in `benchmark` scope unless the
  GitHub issue explicitly approves cross-milestone work.
- Preserve capability claims and backend labels unless the proof oracle records
  matching implementation evidence.
- Use the linked issue mirror and plan as the execution entry points for
  `project-resolve`.

## Non-Goals

- No new solver algorithm implementation unless required by a validation gap.
- No release publication.
- No broad unsupported capability claims.

## Validation

- Run capability evidence tests.
- Run benchmark/registry structural tests.
- Run docs validation.
