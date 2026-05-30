# Monorepo Package Release Cleanup

Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/185`
Milestone: `M1 - Packages`
Status: ready for issue-goal-execute-merge

## Outcome

Finish the remaining tracker, docs, and release-guidance cleanup after the
provider and extension packages moved into the monorepo package layout. The
current source of truth must be unambiguous: this monorepo owns the three
distributions, and old sibling repository guidance must not mislead agents or
users.

## Acceptance Criteria

- [ ] Phase 4 package-release cleanup gates are explicitly reconciled against the current monorepo package layout.
- [ ] Docs identify the monorepo as the source of truth and separate GitHub extension repos, if retained, as archived or non-authoritative mirrors.
- [ ] Release and install guidance names the three distributions without implying sibling local repos are required.
- [ ] M1 milestone README and local issue mirror state match the GitHub issue/project state.
- [ ] No active workflow doc or agent-facing command tells agents to use retired sibling repo paths.

## Implementation Notes

Use `docs/milestones/M1-packages/plans/monorepo-package-migration.md` as the
historical source plan. This issue is the focused closeout slice for the
remaining user-facing and agent-facing cleanup after the package move.

Likely inspection targets:

- `docs/milestones/M1-packages/README.md`
- `docs/milestones/M1-packages/issues/0185-finish-monorepo-package-release-cleanup-and-sibling-repo-archival.md`
- `docs/pages/`
- `docs/agents/`
- `docs/protocols/build_package_dependency_protocol.rst`
- `README.md`
- active scripts and workflow docs that mention extension package source paths

## Proof Oracle

- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_workflow_entrypoints.py -q`
- `uv run python scripts/dev/validate_project.py docs`
- Path audit: active docs, scripts, workflows, and agent-facing guidance do not instruct agents or users to use retired sibling repo paths for normal development.
- GitHub issue/project audit confirms #185 is in `M1 - Packages` with readiness `ready`.
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Non-Goals

- No PyPI publication.
- No package source relocation.
- No native module redesign.
- No separate extension GitHub repo creation.
