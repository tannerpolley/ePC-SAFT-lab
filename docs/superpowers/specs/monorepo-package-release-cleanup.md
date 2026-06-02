# Monorepo Package Release Cleanup

Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/185`
Milestone: `M1 - Packages`
Status: complete pending PR merge

## Outcome

Finish the remaining tracker, docs, and release-guidance cleanup after the
provider and extension packages moved into the monorepo package layout. The
current source of truth must be unambiguous: this monorepo owns the three
distributions, and old sibling repository guidance must not mislead agents or
users.

## Acceptance Criteria

- [x] Phase 4 package-release cleanup gates are explicitly reconciled against the current monorepo package layout.
- [x] Docs identify the monorepo as the source of truth and separate GitHub extension repos, if retained, as archived or non-authoritative mirrors.
- [x] Release and install guidance names the three distributions without implying sibling local repos are required.
- [x] M1 milestone README and local issue mirror state match the GitHub issue/project state.
- [x] No active workflow doc or agent-facing command tells agents to use retired sibling repo paths.

## Reconciliation Notes

- GitHub lookup found no retained `ePC-SAFT/epcsaft-equilibrium` or
  `ePC-SAFT/epcsaft-regression` repositories, so there are no authoritative
  sibling repositories to archive.
- Current package architecture, release installation, publishing, README, and
  new-agent guidance identify `ePC-SAFT/ePC-SAFT` as the source of truth and
  the `packages/` workspace members as the active development layout.
- Historical sibling-checkout references remain only in explicitly historical
  M1 plan records.

## Implementation Notes

Use `docs/superpowers/specs/monorepo-package-migration.md` as the
historical source plan. This issue is the focused closeout slice for the
remaining user-facing and agent-facing cleanup after the package move.

Likely inspection targets:

- `docs/superpowers/milestones/M1-packages/README.md`
- `docs/pages/`
- `docs/agents/`
- `docs/protocols/build_package_dependency_protocol.rst`
- `README.md`
- active scripts and workflow docs that mention extension package source paths

The issue mirror is removed in this slice because issue #185 is closed by the
PR; local milestone mirrors track open issues only.

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
