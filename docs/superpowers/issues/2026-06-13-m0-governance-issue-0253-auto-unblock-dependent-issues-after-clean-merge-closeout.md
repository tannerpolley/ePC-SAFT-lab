---
issue: 253
title: "M0: auto-unblock dependent issues after clean merge closeout"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/253"
state: "open"
milestone: "M0 - Governance"
project: "ePC-SAFT Roadmap"
package: "governance"
capability: "issue-tracker"
backend: "GitHub"
readiness: "ready"
release_target: "none"
source_spec: ""
source_plan: "docs/superpowers/plans/2026-06-13-m0-github-dependency-auto-unblock-closeout-plan.md"
afk_hitl: "AFK"
branch: codex/issue-0253-auto-unblock-dependent-issues
last_synced: "2026-06-13"
---

# M0: auto-unblock dependent issues after clean merge closeout

GitHub Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/253
Source Plan: docs/superpowers/plans/2026-06-13-m0-github-dependency-auto-unblock-closeout-plan.md
Branch: codex/issue-0253-auto-unblock-dependent-issues
AFK/HITL: AFK

GitHub remains authoritative for state, labels, Project fields, comments,
dependency edges, and PR linkage. This mirror exists so `project-resolve` can
start from a durable local source plan.

## Summary

Add GitHub-backed automation that moves dependent issues from `status:blocked`
to `status:ready` when a fully resolved issue was their final open GitHub
native blocker, then syncs the local mirror files in the repo.

## Triggering Example

#189 remained labeled `status:blocked` after its native blockers #188 and #241
were closed. The auto-unblock workflow should make that stale state visible in
dry-run mode, apply the label refresh, and commit the mirror/table sync when
requested or when a scheduled reconciliation finds drift.

## Acceptance Criteria

- [ ] A dry-run command lists issues blocked by a resolved issue and shows which dependents have zero open blockers left.
- [ ] A GitHub Actions workflow runs the same logic on issue close, merged PR close, manual dispatch, and scheduled reconciliation.
- [ ] An apply command removes `status:blocked` and adds `status:ready` only for dependents whose native blockers are all closed.
- [ ] `agent-ready` is added only when local mirror/source-plan checks prove the issue is AFK-ready.
- [ ] Local mirrors and milestone README rows are refreshed and committed by the workflow when changes are needed, or reported as missing.
- [ ] Merge/resolve closeout docs require checking the GitHub workflow result after a clean merge and give a local fallback command.
- [ ] Tests cover no dependents, dependents with remaining blockers, dependents with all blockers closed, missing local mirrors, workflow event parsing, local commit/no-commit decisions, and dry-run/apply separation.

## Proof Oracle

```powershell
uv run --no-sync python run_pytest.py tests/workflows/repo/test_issue_dependency_readiness.py -q
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --issue 188 --dry-run --json
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --issue 241 --dry-run --json
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --reconcile --dry-run --json
uv run --no-sync python scripts/dev/validate_project.py docs
```

## Non-Goals And Boundaries

- No plugin-cache edits.
- No automatic issue closure.
- No automatic `agent-ready` label from dependency state alone.
- No product-code changes.
- No dependence on a GitHub issue-dependency-specific event; scheduled reconciliation must catch dependency drift.

## Tracker Metadata

- Milestone: `M0 - Governance`
- Package: `governance`
- Capability: `issue-tracker`
- Backend: `GitHub`
- Readiness: `ready`
- AFK/HITL: `AFK`
- Release target: `none`
- Labels: `agent-ready, docs, validation, area:docs, status:ready, type:task`
