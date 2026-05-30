# Issue Tracker: GitHub

Issues and PRDs for this repo live in GitHub Issues for the repository shown by
`git remote -v`. The active organization repository is
`ePC-SAFT/ePC-SAFT`. Use the `gh` CLI for issue operations from inside this
clone.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`
- **Read an issue**: `gh issue view <number> --comments`
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments`
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply or remove labels**: `gh issue edit <number> --add-label "..."` or `--remove-label "..."`
- **Assign a milestone**: `gh issue edit <number> --milestone "M4 - Equilibrium"`
- **Close an issue**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`. The GitHub CLI does this automatically when run inside this clone.

## Roadmap Setup

The local setup contract for milestones, issue types, labels, issue forms, and
Project policy lives in `docs/agents/project-roadmap.md` and
`docs/agents/project-roadmap.json`.

GitHub native issue types are enabled at the organization level and must use
one of:

- `Bug`
- `Feature`
- `Task`

Keep `type:bug`, `type:feature`, and `type:task` labels as compatibility
labels because not every CLI or agent skill exposes native GitHub issue types.
Every active GitHub issue should have exactly one native issue type and, when
actively routed, the matching `type:*` label.

## Milestones

GitHub milestones follow `docs/milestones/PROJECT_CONTEXT.md` and use short
dashboard names. `docs/milestones/` is the local planning root for milestone
plans, optional issue handoffs, and milestone-owned registries. GitHub Issues
and the `ePC-SAFT Roadmap` Project remain authoritative for live state.

| Milestone | Tracker meaning |
| --- | --- |
| `M0 - Governance` | Planning hygiene, tracker setup, labels, issue templates, completion rules, GoalBuddy/project discipline, and repo-wide process gates. |
| `M1 - Packages` | Monorepo package layout, package ownership, test relocation, provider-only build proof, extension-native boundaries, and package CI/docs/release structure. |
| `M2 - Python API` | Public Python package surface, user-facing workflow ergonomics, result schemas, diagnostics, examples, import stability, and package-level user experience. |
| `M3 - EOS` | Provider EOS/state/parameters, native SDK contract, exact derivatives, CppAD/implicit sensitivities, and provider-only capability claims. |
| `M4 - Equilibrium` | `epcsaft-equilibrium`, GFPE, selector/admission, Ipopt NLP, HELD/TPD, phase discovery, and phase-equilibrium workflows. |
| `M5 - Regression` | `epcsaft-regression`, TargetDataset/result contracts, Ceres optimizer, parameter sensitivities, and regression workflows. |
| `M6 - Validation` | Executable literature benchmarks, registry evidence, capability evidence, docs/test proof, and release-quality validation gates. |
| `M7 - Release` | Downstream integration, install proofs, PyPI/release choreography, migration docs, and no private downstream workarounds. |

Every GitHub issue should have exactly one milestone. If a new issue seems to
span multiple milestones, create a tracking issue in the earliest blocking
milestone and split the later work into child issues.

## Project And Issue Shape

- Canonical Project: `ePC-SAFT Roadmap`
  (`https://github.com/orgs/ePC-SAFT/projects/1`).
- Do not use untitled organization Projects for milestone work. They are scratch
  or closed state, not the tracker source of truth.
- Use the issue templates for new work:
  - `Bug`, `Feature`, and `Task` for the canonical native issue-type forms.
  - `Milestone tracking issue` for a milestone plan or major tranche.
  - `Micro implementation issue` for one PR-sized implementation slice.
  - `Milestone gate issue` for CI, docs, benchmark, capability, release, or
    downstream proof.
  - `Upstream ePC-SAFT package request` and `Downstream ePC-SAFT dependency
    bug` for downstream-driven package work.
- Larger milestone plan files map to one tracking issue in the matching milestone.
- Micro issues are implementation slices that close one checklist item or gate
  on the tracking issue.
- Gate issues prove CI, docs, benchmark, capability, release, or downstream
  evidence.
- Structured issue templates include `projects: ["ePC-SAFT/1"]`, so new issues
  filed through those templates are added to the canonical Project
  automatically.
- Use labels for stable facts and routing. Use the GitHub Project for workflow
  state and dashboard grouping.
- Issue forms set both a native GitHub issue type and a matching `type:*`
  compatibility label.
- The organization Project groups and sorts by Milestone, Package, Capability,
  Backend, Readiness, and Release target.
- Use `docs/milestones/M*/plans/*.md` for durable plans created for larger
  issues or tranches, and link the GitHub issue to the plan.
- Use `docs/milestones/M*/issues/*.md` only for optional concise handoff
  context. Refresh those files from GitHub when issue scope or Project fields
  change.

## Pull Requests

- Every milestone PR should close one micro or gate issue when possible.
- The PR body must name the issue, milestone, tracking issue or plan, and
  relevant Project fields.
- Ordinary early package-development PRs use local proof first. Heavy native,
  package, release, and installed-provider lanes are manual-only unless the PR
  claims release readiness, capability support, or production native behavior.
- Branch protection intentionally has no required status checks or required
  reviews while this early package policy is active.
- Keep milestone and Project state current before requesting review and before
  merge.
- Do not close an issue by documenting incompleteness; split remaining work
  into child issues or keep the issue open.
- Use risk-based focused validation in the PR body. Ordinary PRs do not need
  boilerplate skipped-heavy-lane notes.

## When a skill says "publish to the issue tracker"

Create a GitHub issue in the repository shown by `git remote -v`.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
