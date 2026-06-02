# Release Downstream Backlog

Milestone: `M7 - Release`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/195`
Status: `open`
Last synced: `2026-05-30`

## Summary

Re-open release, PyPI, and downstream migration proof as M7 work. Package-layout
completion does not imply release readiness; this plan tracks the install,
publish, and downstream-consumer evidence needed before making release claims.

## Acceptance Gates

- [ ] Define install proof for `epcsaft`, `epcsaft-equilibrium`,
  `epcsaft-regression`, and all three distributions together.
- [ ] Define downstream migration proof using real downstream workflows without
  private upstream workarounds.
- [ ] Define PyPI/trusted-publisher release choreography and release-note
  expectations for the monorepo source-of-truth model.
- [ ] Define docs that explain source checkout development versus released
  package consumption.

## Implementation Notes

This plan is a release backlog anchor. It does not publish packages, edit
downstream repositories, or rename public imports.

## Validation

- `uv run python scripts/dev/validate_project.py docs`
- GitHub Project audit: issue #195 belongs to `M7 - Release`, package
  `downstream`, readiness `needs design`, release target `future`.
