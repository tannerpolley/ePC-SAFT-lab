# Project Roadmap Setup

This file records the GitHub tracker setup expected by local skills. GitHub
Issues and the `ePC-SAFT Roadmap` Project remain authoritative for live state.

## Repository

- Target repository: `ePC-SAFT/ePC-SAFT`
- Default branch: `main`
- Full roadmap/context: `docs/superpowers/PROJECT_CONTEXT.md`
- Local tracker guide: `docs/agents/issue-tracker.md`
- Project: `ePC-SAFT Roadmap` at `https://github.com/orgs/ePC-SAFT/projects/1`

## Issue Types

The organization has native GitHub issue types enabled:

- `Bug`: unexpected current behavior or reproducible defect.
- `Feature`: new capability, user-facing improvement, or broadened package behavior.
- `Task`: setup, implementation slice, audit, cleanup, proof, docs, or governance work.

Use both native issue types and `type:*` labels because older CLI surfaces and
some agent skills still route through labels.

Required compatibility labels:

- `type:bug`
- `type:feature`
- `type:task`

Required readiness labels:

- `status:triage`
- `status:ready`
- `status:blocked`

## Issue Relationships

Use GitHub native issue dependencies for blocker relationships. The dependency
edge is authoritative; title prefixes such as `[Blocked]` are forbidden for
open issues.

Dashboard mirrors are still allowed:

- `status:blocked` label for issue-list filtering.
- Project `Readiness=blocked` for roadmap views.

Current audited dependency edge:

- #145 is `blocked_by` #148.
- #148 is `blocking` #145.

## Issue Forms

Canonical type forms:

- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/ISSUE_TEMPLATE/feature.yml`
- `.github/ISSUE_TEMPLATE/task.yml`

Existing specialized forms also declare native issue types:

- `tracking_issue.yml`: `task`
- `micro_issue.yml`: `task`
- `gate_issue.yml`: `task`
- `upstream_package_request.yml`: `feature`
- `downstream_dependency_bug.yml`: `bug`

Every form must include `projects: ["ePC-SAFT/1"]`, a top-level native `type`,
and a matching `type:*` label.

## Apply Policy

Tracker setup changes are applied on synced `main` and pushed directly. Do not
create implementation branches, GoalBuddy boards, PRs, or product-code changes
for setup-project-roadmap work.

## Audit State

Last setup audit: 2026-05-30.

All non-PR GitHub issues had a native issue type after the audit:

- `Bug`: 2
- `Feature`: 46
- `Task`: 36

Current open issues were audited to carry matching `type:*` labels. Closed
historical issues are native-type backfilled but are not label-backfilled unless
they are reopened or otherwise touched.
