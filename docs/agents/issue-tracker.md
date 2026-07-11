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
- **List blockers for an issue**: `gh api /repos/ePC-SAFT/ePC-SAFT/issues/<number>/dependencies/blocked_by`
- **List issues blocked by an issue**: `gh api /repos/ePC-SAFT/ePC-SAFT/issues/<number>/dependencies/blocking`
- **Mark an issue blocked by another issue**: `gh api -X POST /repos/ePC-SAFT/ePC-SAFT/issues/<blocked-number>/dependencies/blocked_by -F issue_id=<blocking-rest-id>`
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

GitHub native issue dependencies are the source of truth for blocker
relationships. Do not encode blocker state in issue titles with prefixes such
as `[Blocked]`. Use `blocked_by`/`blocking` relationships, then mirror the
state with Project `Readiness=blocked` and `status:blocked` only when useful
for dashboard filtering.

## Dependency Readiness Sync

The `sync issue readiness` GitHub Actions workflow runs after issue close,
manual dispatch, and scheduled reconciliation. It
checks GitHub native dependency edges and moves a dependent issue from
`status:blocked` to `status:ready` only when all native blockers are closed.
Dependency state alone does not add `agent-ready`; the local mirror and source
plan must prove the issue is AFK-ready. The workflow updates labels and local
mirrors silently; it does not post issue comments for routine dependency
readiness changes.

After a clean merge or direct issue close, inspect the workflow result. If the
workflow could not push mirror changes, run the same check locally and commit
the mirror/table sync:

```bash
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --issue <closed-issue> --dry-run --json
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --issue <closed-issue> --apply --json
```

For periodic drift repair:

```bash
uv run --no-sync python scripts/dev/update_issue_dependency_readiness.py --reconcile --dry-run --json
```

## Milestones

GitHub milestones follow `docs/superpowers/PROJECT_CONTEXT.md` and use short
dashboard names. `docs/superpowers/` is the local Superpowers Project root for
milestone pages, specs, plans, issue mirrors, and milestone-owned registries. GitHub
Issues and the `ePC-SAFT Roadmap` Project remain authoritative for live state.

| Milestone | Tracker meaning |
| --- | --- |
| `M0 - Governance` | Planning hygiene, tracker setup, labels, issue templates, completion rules, GoalBuddy/project discipline, and repo-wide process gates. |
| `M1 - Packages` | Monorepo package layout, package ownership, test relocation, provider-only build proof, extension-native boundaries, and package CI/docs/release structure. |
| `M2 - Python API` | Public Python package surface, user-facing workflow ergonomics, result schemas, diagnostics, examples, import stability, and package-level user experience. |
| `M3 - EOS` | Provider EOS/state/parameters, native SDK contract, exact derivatives, CppAD/implicit sensitivities, and provider-only capability claims. |
| `M4 - Equilibrium` | `epcsaft-equilibrium`, GFPE, selector/admission, Ipopt NLP, HELD/TPD, phase discovery, and phase-equilibrium workflows. |
| `M5 - Regression` | `epcsaft-regression`, TargetDataset/result contracts, Ceres optimizer, parameter sensitivities, and regression workflows. |
| `M6 - Validation` | Executable literature benchmarks, registry evidence, capability evidence, docs/test proof, and reproducible validation gates. |
| `M7 - Release` | Downstream integration, install proofs, PyPI/release choreography, migration docs, and no private downstream workarounds. |

Every GitHub issue should have exactly one milestone. If a new issue seems to
span multiple milestones, create a tracking issue in the earliest blocking
milestone and split the later work into child issues.

## Milestone And Package Boundaries

Before creating or updating an issue, durable plan file, proof oracle,
candidate file list, acceptance criteria, or hidden execution marker, identify
the owning milestone and package. Search results are evidence of references,
not evidence of scope.

- `M3 - EOS` is provider/core scope: `packages/epcsaft/**` plus provider-owned
  repo docs, build metadata, SDK manifests, and provider tests.
- `M4 - Equilibrium` is equilibrium-extension scope:
  `packages/epcsaft-equilibrium/**` plus explicitly necessary provider
  public-contract references.
- `M5 - Regression` is regression-extension scope:
  `packages/epcsaft-regression/**` plus explicitly necessary provider
  public-contract references.
- Do not add sibling package files, tests, capability text, proof commands, or
  candidate paths to the current issue unless the user explicitly approves a
  cross-milestone issue set.
- If a change appears to require multiple package milestones, stop and ask
  whether to split the work. Default to separate issues by milestone and
  package.

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
- Larger specs map to one tracking issue in the matching milestone.
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
- Use GitHub issue relationships for dependencies:
  - An issue that cannot start because another issue must finish first should
    be marked `blocked_by` the prerequisite issue.
  - A prerequisite issue should naturally show the dependent work under
    `blocking`.
  - Do not put `[Blocked]`, `Blocked:`, or similar status prefixes in titles.
- The organization Project groups and sorts by Milestone, Package, Capability,
  Backend, Readiness, and Release target.
- Use `docs/superpowers/specs/*.md` for durable specs and planning notes
  created for larger issues or tranches, and link the GitHub issue to the
  source spec when one exists.
- Use `docs/superpowers/plans/*.md` for executable implementation plans.
- Use `docs/superpowers/issues/*.md` only for optional concise handoff
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
