# Make Codex App Worktree Environments Frictionless And Self-Updating

Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/184`
Slug: `make-codex-app-worktree-environments-frictionless-and-self-upda`
Status: `localized for issue-goal-execute-merge`
Source: externally sourced GitHub issue localized in the target repository before GoalBuddy execution.

## Outcome

New Codex app worktrees receive a current, repo-owned ePC-SAFT setup contract:
the Codex environment action list, setup wrapper, Python bootstrap, IntelliJ
normalizer, run-dashboard contract, and agent-facing docs all point to the same
package-layout-aware workflow.

## Acceptance Criteria

- [x] `.codex/environments/environment.toml` exposes only current Codex app actions and includes the IntelliJ contract check expected by the environment README.
- [x] `.codex/environments/setup.ps1` remains a thin dispatcher to `scripts/dev/bootstrap.py` and supports the environment action steps without duplicating project setup logic.
- [x] `scripts/dev/bootstrap.py`, `scripts/dev/configure_jetbrains_project.py`, and the repo-owned run manifest remain the authoritative fresh-worktree setup path.
- [x] Agent/user docs identify the repo-owned setup sources and separate them from machine-local IntelliJ/Codex bridge policy.
- [x] Structural tests fail if Codex environment actions, bootstrap guidance, or IntelliJ contract guidance drift from the current package layout.
- [x] Validation proves the dry-run bootstrap, IntelliJ contract check, workflow structure tests, and docs build succeed.

## Implementation Notes

Repo-owned setup sources:

- `.codex/environments/environment.toml`
- `.codex/environments/setup.ps1`
- `.codex/environments/README.md`
- `scripts/dev/bootstrap.py`
- `scripts/dev/configure_jetbrains_project.py`
- `scripts/dev/jetbrains_run_manifest.py`
- `.run/*.run.xml`
- `docs/agents/INTELLIJ.md`
- `docs/agents/new-agent-start-here.md`
- `docs/pages/development_workflows.rst`

Machine-local policy stays outside the public workflow files. User-level Codex,
IntelliJ bridge, and MCP transport rules remain in the local agent instructions,
not in package setup code.

## Proof Oracle

- [x] `uv run python scripts/dev/bootstrap.py --dry-run`
- [x] `uv run python scripts/dev/configure_jetbrains_project.py --check`
- [x] `uv run python run_pytest.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/repo/test_project_structure.py -q`
- [x] `uv run python scripts/dev/validate_project.py docs`
- [x] `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Non-Goals

- No public package API changes.
- No package source layout changes.
- No native build-system redesign.
- No machine-local user-level Codex or IntelliJ bridge configuration changes.
- No PyPI, release, or downstream migration work.

## Candidate Execution Files

- `.codex/environments/**`
- `.run/**`
- `scripts/dev/bootstrap.py`
- `scripts/dev/configure_jetbrains_project.py`
- `scripts/dev/jetbrains_run_manifest.py`
- `docs/agents/**`
- `docs/pages/development_workflows.rst`
- `docs/milestones/M0-governance/**`
- `tests/workflows/repo/test_workflow_entrypoints.py`
- `tests/workflows/repo/test_project_structure.py`
