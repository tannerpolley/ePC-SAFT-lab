# M0 Plan: GitHub Dependency Auto-Unblock Closeout

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` for implementation. Steps use checkbox
> (`- [ ]`) syntax for tracking.

**Goal:** Add GitHub-backed automation that moves dependent issues from
`status:blocked` to `status:ready` when a fully resolved issue was their final
open GitHub native blocker, then syncs the local mirror files in the repo.

**Architecture:** GitHub native issue dependencies remain the source of truth.
The repo should provide a dry-run-first Python synchronizer plus a GitHub
Actions workflow that runs on issue closure, merged PR closure, manual dispatch,
and a scheduled reconciliation pass. The workflow updates GitHub readiness
labels first, then updates `docs/superpowers/issues` mirrors and milestone
README rows in the same repository commit when local files change. It must not
depend on plugin cache files or hidden agent state. `agent-ready` is added only
when the issue mirror/source plan is AFK-ready; dependency unblocking alone is
not enough.

**Tech Stack:** Python standard library, GitHub REST API or GitHub CLI,
GitHub Actions, local Markdown mirrors under `docs/superpowers`, docs under
`docs/agents`, and pytest contract tests under `tests/workflows/repo`.

---

## Intake

- Milestone: `M0 - Governance`
- Scope: repo workflow and tracker hygiene
- Source docs:
  - `docs/agents/issue-tracker.md`
  - `docs/agents/project-roadmap.md`
  - `docs/superpowers/PROJECT_CONTEXT.md`
- Triggering example: #189 still had `status:blocked` after #188 and #241 closed.

## Acceptance Gates

- [ ] A dry-run command can list issues blocked by a resolved issue and show which dependents have zero open blockers left.
- [ ] A GitHub Actions workflow runs the same logic on issue close, manual dispatch, and scheduled reconciliation.
- [ ] An apply command removes `status:blocked` and adds `status:ready` only for dependents whose native blockers are all closed.
- [ ] `agent-ready` is added only when local mirror/source-plan checks prove the issue is AFK-ready.
- [ ] Local mirrors and milestone README rows are refreshed and committed by the workflow when changes are needed, or reported as missing.
- [ ] Merge/resolve closeout docs require running the dependency auto-unblock check after a clean merge.
- [ ] Tests cover no dependents, dependents with remaining blockers, dependents with all blockers closed, missing local mirrors, workflow event parsing, local commit/no-commit decisions, and dry-run/apply separation.

## Tasks

### Task 1: Define The Dependency Readiness Model

**Use Cases:**

- When a closed issue blocks no other issues, the closeout command should report no-op success.
- When a dependent issue still has one or more open blockers, the command should leave `status:blocked` intact and list the remaining blockers.
- When a dependent issue has zero open blockers, the command should propose `status:blocked` removal and `status:ready` addition.

**Files:**

- `tests/workflows/repo/test_issue_dependency_readiness.py`
- `scripts/dev/update_issue_dependency_readiness.py`

- [ ] Add tests around small JSON fixtures that model `blocking` and `blocked_by` responses.
- [ ] Define a pure function that classifies each dependent as `no_op`, `still_blocked`, or `ready_to_unblock`.
- [ ] Make malformed GitHub API payloads fail loudly.
- [ ] Keep issue labels separate from native dependency state in the model.

### Task 2: Implement Dry-Run And Apply Commands

**Use Cases:**

- When an agent finishes a merge, it can run one command with the resolved issue number and see every dependent issue that should unblock.
- When `--apply` is omitted, the command must not edit GitHub or local files.
- When `--apply` is present, the command should edit labels and write a concise comment explaining the unblock evidence.

**Files:**

- `scripts/dev/update_issue_dependency_readiness.py`
- `tests/workflows/repo/test_issue_dependency_readiness.py`

- [ ] Implement `--issue <number>` and optional `--repo ePC-SAFT/ePC-SAFT`.
- [ ] Query `/issues/<number>/dependencies/blocking` to enumerate dependents.
- [ ] Query `/issues/<dependent>/dependencies/blocked_by` for each dependent and compute open blockers.
- [ ] In dry-run mode, emit JSON with dependent issue number, state, current labels, remaining blockers, and proposed label changes.
- [ ] In apply mode, remove `status:blocked`, add `status:ready`, and comment with the closed blocker evidence.
- [ ] Avoid adding `agent-ready` unless the local mirror/source plan checks pass.

### Task 3: Add The GitHub Actions Automation

**Use Cases:**

- When an issue closes directly, the workflow should inspect issues that were blocked by that issue and unblock any dependent with no open blockers left.
- When a pull request merges and closes one or more issues, the workflow should inspect the closed issue numbers from the PR body and merge commit context.
- When GitHub does not emit an issue-dependency-specific workflow event, the scheduled reconciliation pass should catch stale `status:blocked` labels and stale local mirrors.
- When a maintainer needs to repair drift, `workflow_dispatch` should accept an optional issue number and dry-run/apply mode.

**Files:**

- `.github/workflows/sync-issue-readiness.yml`
- `scripts/dev/update_issue_dependency_readiness.py`
- `tests/workflows/repo/test_issue_dependency_readiness.py`

- [ ] Create `.github/workflows/sync-issue-readiness.yml`.
- [ ] Configure triggers for `issues` closed/reopened/labeled/unlabeled events, `pull_request` closed events, `workflow_dispatch`, and a scheduled reconciliation.
- [ ] Set least-privilege permissions: `issues: write`, `contents: write`, `pull-requests: read`, and `actions: read` only if required by the implementation.
- [ ] Install no external dependencies unless a test proves the standard library path is inadequate.
- [ ] Run the synchronizer in dry-run mode first and print a JSON summary.
- [ ] In apply mode, run the synchronizer, validate changed docs, and commit mirror/table changes only if the worktree changed.
- [ ] Prevent infinite workflow churn by ignoring commits whose message is the synchronization commit and by exiting with no-op when no files changed.

### Task 4: Refresh Local Mirrors And Milestone Tables

**Use Cases:**

- When a dependent issue has a local mirror, readiness frontmatter and tracker metadata should match GitHub labels.
- When the mirror is missing, the command should report the missing path rather than inventing a new scope silently.
- When a milestone README contains a current-open row, its readiness cell should match the new state.
- When the GitHub Action runs in apply mode, mirror changes should be committed to the repo so local `main` receives them on the next pull.

**Files:**

- `scripts/dev/update_issue_dependency_readiness.py`
- `docs/superpowers/issues/*.md`
- `docs/superpowers/milestones/*/README.md`
- `tests/workflows/repo/test_issue_dependency_readiness.py`

- [ ] Locate local mirrors by frontmatter `issue: <number>`.
- [ ] Update `readiness`, `last_synced`, tracker metadata, and status-label text for mirrors that exist.
- [ ] Update matching milestone README current-open rows from `blocked` to `ready`.
- [ ] Emit missing mirror or missing milestone-row warnings as JSON diagnostics.
- [ ] Return a nonzero status in strict apply mode if GitHub labels changed but the local mirror update failed.

### Task 5: Document The GitHub-Backed Closeout Gate

**Use Cases:**

- When a resolve/merge workflow closes an issue, the closeout checklist should point to the GitHub workflow run instead of relying on manual agent memory.
- When an issue becomes ready but not AFK-ready, docs should explain why `agent-ready` is withheld.
- When plugin skills are unavailable or stale, the repo-owned command should still be usable from the shell.
- When the workflow cannot push mirror changes, docs should tell the agent to run the command locally and commit the mirror sync.

**Files:**

- `docs/agents/issue-tracker.md`
- `docs/agents/project-roadmap.md`
- `docs/superpowers/milestones/M0-governance/README.md`

- [ ] Add the workflow name, command, and fallback closeout rule to `docs/agents/issue-tracker.md`.
- [ ] Update `docs/agents/project-roadmap.md` to distinguish dependency-unblocked from AFK-ready.
- [ ] Keep the #253 row current in the M0 current-open table.
- [ ] Do not edit plugin cache files.

### Task 6: Validate Against #189 As A Real Example

**Use Cases:**

- When the command runs against #188 or #241 in dry-run mode, it should identify #189 as eligible because no open blockers remain.
- When the command runs in apply mode after manual review, it should bring GitHub labels and local mirrors into agreement.
- When reporting completion, the final evidence should show both GitHub labels and local mirror readiness.
- When the GitHub workflow runs from `workflow_dispatch` with #188 or #241, it should produce a no-op after this manual #189 repair because labels and mirrors are already ready.

**Files:**

- `.github/workflows/sync-issue-readiness.yml`
- `scripts/dev/update_issue_dependency_readiness.py`
- `docs/superpowers/issues/2026-05-30-m4-equilibrium-issue-0189-derive-boundary-workflows-and-generalized-phase-set-pe-from-neutral-gfpe.md`
- `docs/superpowers/milestones/M4-equilibrium/README.md`

- [ ] Run the dry-run command against #188 and #241.
- [ ] Run the workflow locally through the same script arguments used by `workflow_dispatch`.
- [ ] Confirm #189 is proposed for unblock only after all blockers are closed.
- [ ] Run the apply path in a controlled local/git state.
- [ ] Verify #189 carries `status:ready`, not `status:blocked`, and does not automatically gain `agent-ready`.

## Proof Oracle

```powershell
uv run --no-sync python run_pytest.py tests/workflows/repo/test_issue_dependency_readiness.py -q
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --issue 188 --dry-run --json
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --issue 241 --dry-run --json
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --reconcile --dry-run --json
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Issue Creation Packet

Create one M0 task issue from this plan.

**Title:** `M0: auto-unblock dependent issues after clean merge closeout`

**Type:** `Task`

**Milestone:** `M0 - Governance`

**Labels:** `docs`, `validation`, `area:docs`, `status:ready`, `agent-ready`, `type:task`

**Body:**

```markdown
Add GitHub-backed automation that moves dependent issues from `status:blocked` to `status:ready` when a fully resolved issue was their final open GitHub native blocker, then syncs the local mirror files in the repo.

Source plan:
docs/superpowers/plans/2026-06-13-m0-github-dependency-auto-unblock-closeout-plan.md

Triggering example:
#189 remained labeled `status:blocked` after its native blockers #188 and #241 were closed.

Goal:
Provide a dry-run-first script plus a GitHub Actions workflow so GitHub can automatically identify and apply safe dependent-issue unblocks after a clean issue close and commit local mirror updates back to the repo.

Acceptance:
- A dry-run command lists issues blocked by a resolved issue and shows which dependents have zero open blockers left.
- A GitHub Actions workflow runs the same logic on issue close, manual dispatch, and scheduled reconciliation.
- An apply command removes `status:blocked` and adds `status:ready` only for dependents whose native blockers are all closed.
- `agent-ready` is added only when local mirror/source-plan checks prove the issue is AFK-ready.
- Local mirrors and milestone README rows are refreshed and committed by the workflow when changes are needed, or reported as missing.
- Merge/resolve closeout docs require checking the GitHub workflow result after a clean merge and give a local fallback command.
- Tests cover no dependents, dependents with remaining blockers, dependents with all blockers closed, missing local mirrors, workflow event parsing, local commit/no-commit decisions, and dry-run/apply separation.

Non-goals:
- No plugin-cache edits.
- No automatic issue closure.
- No automatic `agent-ready` label from dependency state alone.
- No product-code changes.
- No dependence on a GitHub issue-dependency-specific event; scheduled reconciliation must catch dependency drift.

Proof oracle:
uv run --no-sync python run_pytest.py tests/workflows/repo/test_issue_dependency_readiness.py -q
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --issue 188 --dry-run --json
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --issue 241 --dry-run --json
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --reconcile --dry-run --json
uv run --no-sync python scripts/dev/validate_project.py docs
```
