# M0 - Governance

Planning hygiene, tracker setup, labels, issue templates, completion rules,
GoalBuddy/project discipline, and repo-wide process gates.

## Operating Rule

Use this milestone for tracker/process changes that make agents, GitHub Issues,
Project fields, local docs, templates, and completion standards agree.

## Current Open Issues

| Issue | Readiness | Summary |
| --- | --- | --- |
| [#253](../../issues/2026-06-13-m0-governance-issue-0253-auto-unblock-dependent-issues-after-clean-merge-closeout.md) | `ready` | Add the GitHub-backed workflow and local repair command that unblock dependent issues and sync local mirrors when their final native GitHub blocker closes. |

## Current Plans

| Plan | Summary |
| --- | --- |
| [GitHub dependency auto-unblock closeout](../../plans/2026-06-13-m0-github-dependency-auto-unblock-closeout-plan.md) | GitHub Actions plus dry-run/apply local repair for moving dependents from `status:blocked` to `status:ready` and syncing local mirrors after clean merges. |

## Retained Workflow

`sync issue readiness` runs on issue close, merged PR close, manual dispatch,
and scheduled reconciliation. The local command is
`uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py`;
use `--dry-run --json` before `--apply --json`.

## Closed Issues

- [https://github.com/ePC-SAFT/ePC-SAFT/issues/235](https://github.com/ePC-SAFT/ePC-SAFT/issues/235) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/237](https://github.com/ePC-SAFT/ePC-SAFT/pull/237) on 2026-06-10T21:41:46Z
