# Milestone Tracker Hardening Plan

Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/163
Milestone: `M0 - Governance`
Status: `implementation`
Last synced: `2026-05-29`

## Summary

Harden the local milestone planning root so future agents use
`docs/superpowers/milestones/` for durable plans, optional issue handoffs, and milestone
owned registries while GitHub Issues and the `ePC-SAFT Roadmap` Project remain
authoritative for live state.

## Acceptance Gates

- [x] GitHub milestone descriptions and `docs/superpowers/PROJECT_CONTEXT.md`
      milestone descriptions match for the active milestone taxonomy.
- [x] Closed GitHub issue mirrors are removed from `docs/superpowers/issues/`.
- [x] Local issue mirrors that remain all point to open GitHub issues.
- [x] `docs/superpowers/_templates/` contains reusable plan and issue-mirror
      templates.
- [x] Milestone README open-issue indexes match current GitHub open issues.
- [x] Structural tests enforce milestone folder, template, and issue-mirror
      shape.
- [x] Issue #154 lists the M1 child package slices.

## Validation

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_workflow_entrypoints.py -q
uv run python scripts/dev/validate_project.py docs
gh issue list --repo ePC-SAFT/ePC-SAFT --state open
gh issue view 154 --repo ePC-SAFT/ePC-SAFT --comments
```
