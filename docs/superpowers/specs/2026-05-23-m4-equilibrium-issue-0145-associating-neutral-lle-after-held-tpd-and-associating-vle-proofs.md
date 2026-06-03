# Associating neutral LLE after HELD/TPD and associating VLE proofs

Milestone: `M4 - Equilibrium`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/145`
Status: `open`
Last synced: `2026-06-02`

## Summary

This issue is blocked by #148 through the native GitHub issue-dependency relationship. Do not encode blocker state in the title; use the Relationships panel/API as the source of truth.

## Acceptance Gates

- [ ] GitHub issue #145 outcome is satisfied without broadening unrelated package capability claims.

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

- No unrelated package, milestone, or public API scope should be added.

## Validation

- uv run python scripts/dev/validate_project.py quick
