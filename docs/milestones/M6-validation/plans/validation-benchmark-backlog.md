# Validation Benchmark Backlog

Milestone: `M6 - Validation`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/194`
Status: `open`
Last synced: `2026-05-30`

## Summary

Re-open executable literature benchmark and capability-evidence work as a
validation milestone plan. The goal is to make capability claims depend on
command-backed fixtures, tolerances, sources, and registry entries.

## Acceptance Gates

- [ ] Inventory benchmark families with source, fixture, expected behavior,
  tolerance, and command requirements.
- [ ] Define capability evidence rules for provider, equilibrium, regression,
  and cross-package validation lanes.
- [ ] Separate release-quality validation from ordinary PR local-proof gates.
- [ ] Define registry/docs/test ownership so evidence cannot drift from
  implementation.

## Implementation Notes

This plan is a backlog anchor. It should not claim validation evidence exists
until future implementation issues add executable fixtures and command receipts.

## Validation

- `uv run python scripts/dev/validate_project.py docs`
- GitHub Project audit: issue #194 belongs to `M6 - Validation`, package
  `benchmark`, readiness `needs design`, release target `future`.
