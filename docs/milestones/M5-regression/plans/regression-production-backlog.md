# Regression Production Backlog

Milestone: `M5 - Regression`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/193`
Status: `open`
Last synced: `2026-05-30`

## Summary

Re-open the regression production backlog as one M5 tracking plan. This is the
durable place to collect the next regression implementation design around
`TargetDataset`, Ceres optimizer behavior, parameter movement, sensitivities,
result diagnostics, and capability evidence.

## Acceptance Gates

- [ ] Inventory current gaps in `TargetDataset`, `TargetRow`, parameter maps,
  bounds, result schemas, and optimizer diagnostics.
- [ ] Define package-local Ceres residual-block and optimizer proof tests.
- [ ] Define parameter movement and sensitivity evidence for pure, binary,
  electrolyte, and optional equilibrium-target workflows.
- [ ] Define capability evidence rules that keep implemented regression support
  separate from planned workflows.

## Implementation Notes

This plan is not a code implementation plan yet. It is the M5 backlog anchor
that prevents regression production work from living only in old roadmap prose.
Future decomposition can split it after the design gaps are concrete.

## Validation

- `uv run python scripts/dev/validate_project.py docs`
- GitHub Project audit: issue #193 belongs to `M5 - Regression`, package
  `regression`, backend `Ceres`, readiness `needs design`, release target
  `regression-0.x`.
