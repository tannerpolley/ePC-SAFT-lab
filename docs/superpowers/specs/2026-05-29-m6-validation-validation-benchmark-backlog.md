# Validation Benchmark Backlog

Milestone: `M6 - Validation`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/194`
Status: `historical; superseded for execution`
Last reconciled: `2026-07-10`

> Historical backlog anchor only. Do not execute this document. Live #194 now
> routes work through the focused July 10 M6 regression, Gross, and standalone
> CE evidence plans plus the refreshed #192 evidence gate.

## Summary

Re-open executable literature benchmark and capability-evidence work as a
validation milestone plan. The goal is to make capability claims depend on
command-backed fixtures, tolerances, sources, and registry entries.

## Acceptance Gates

- [ ] Inventory benchmark families with source, fixture, expected behavior,
  tolerance, and command requirements.
- [ ] Define capability evidence rules for provider, equilibrium, regression,
  and cross-package validation lanes.
- [ ] Separate reproducible benchmark and capability-evidence validation from ordinary PR local-proof gates.
- [ ] Define registry/docs/test ownership so evidence cannot drift from
  implementation.

## Implementation Notes

This plan is a backlog anchor. It should not claim validation evidence exists
until future implementation issues add executable fixtures and command receipts.

## Validation

- `uv run python scripts/dev/validate_project.py docs`
- GitHub Project routing target: `ePC-SAFT Roadmap`; live Project membership was
  not verifiable with the active token during the July 10 reconciliation.
