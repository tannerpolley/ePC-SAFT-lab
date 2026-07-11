# M0 - Governance

Planning hygiene, tracker setup, labels, issue templates, completion rules,
GoalBuddy/project discipline, and repo-wide process gates.

## Operating Rule

Use this milestone for tracker/process changes that make agents, GitHub Issues,
Project fields, local docs, templates, and completion standards agree.

## Current Open Issues

| Issue | Role | Readiness | Summary |
| --- | --- | --- | --- |
| [#431](../../issues/2026-07-11-m0-governance-issue-0431-m0-characterize-ownership-and-maintainability-ratchets.md) | rollup | `ready` | Track the package-aware ownership index and measured structural ratchets. |
| [#432](../../issues/2026-07-11-m0-governance-issue-0432-m0-define-versioned-ownership-index-and-pure-ratchet-validator.md) | leaf | `ready` | Define the inactive schema and deterministic offline validator. |
| [#433](../../issues/2026-07-11-m0-governance-issue-0433-m0-activate-measured-ownership-baselines-and-repository-ratchet-gate.md) | leaf | `blocked` | Activate measured baselines after the M3/M5 cutovers and M4 characterization. |
| [#434](../../issues/2026-07-11-m0-governance-issue-0434-m0-close-tasks-9-22-validation-correctness-program.md) | leaf | `blocked` | Assemble exact terminal receipts and close the Tasks 9-22 program. |

## Current Plans

- [Characterized ownership and maintainability ratchets](../../plans/2026-07-10-m0-characterized-ownership-and-maintainability-ratchets-plan.md)
- [Validation-correctness program closeout](../../plans/2026-07-10-m0-validation-correctness-program-closeout-plan.md)

## Retained Workflow

`sync issue readiness` runs on issue close, manual dispatch, and scheduled
reconciliation. The local command is
`uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py`;
use `--dry-run --json` before `--apply --json`.

## Closed Issues

- [https://github.com/ePC-SAFT/ePC-SAFT/issues/235](https://github.com/ePC-SAFT/ePC-SAFT/issues/235) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/237](https://github.com/ePC-SAFT/ePC-SAFT/pull/237) on 2026-06-10T21:41:46Z
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/253](https://github.com/ePC-SAFT/ePC-SAFT/issues/253) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/254](https://github.com/ePC-SAFT/ePC-SAFT/pull/254) on 2026-06-13T13:20:29Z
