# Issue Tracker: GitHub

Issues and PRDs for this repo live in GitHub Issues for the repository shown by
`git remote -v`. Before the organization transfer this is
`tannerpolley/ePC-SAFT`; after transfer it should be `ePC-SAFT/ePC-SAFT`. Use
the `gh` CLI for issue operations from inside this clone.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`
- **Read an issue**: `gh issue view <number> --comments`
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments`
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply or remove labels**: `gh issue edit <number> --add-label "..."` or `--remove-label "..."`
- **Assign a milestone**: `gh issue edit <number> --milestone "M3 - Equilibrium"`
- **Close an issue**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`. The GitHub CLI does this automatically when run inside this clone.

## Roadmap Milestones

GitHub milestones mirror `docs/roadmaps/FULL_ROADMAP.md` and use short
dashboard names:

| Milestone | Tracker meaning |
| --- | --- |
| `M0 - Governance` | Roadmap hygiene, tracker setup, labels, issue templates, completion rules, GoalBuddy/project discipline, and repo-wide process gates. |
| `M1 - Packages` | Monorepo package layout, package ownership, test relocation, provider-only build proof, extension-native boundaries, and package CI/docs/release structure. |
| `M2 - Core` | Provider EOS/state/parameters, native SDK contract, exact derivatives, CppAD/implicit sensitivities, and provider-only capability claims. |
| `M3 - Equilibrium` | `epcsaft-equilibrium`, GFPE, selector/admission, Ipopt NLP, HELD/TPD, phase discovery, and phase-equilibrium workflows. |
| `M4 - Regression` | `epcsaft-regression`, TargetDataset/result contracts, Ceres optimizer, parameter sensitivities, and regression workflows. |
| `M5 - Validation` | Executable literature benchmarks, registry evidence, capability evidence, docs/test proof, and release-quality validation gates. |
| `M6 - Release` | Downstream integration, install proofs, PyPI/release choreography, migration docs, and no private downstream workarounds. |

Every GitHub issue should have exactly one milestone. If a new issue seems to
span multiple milestones, create a tracking issue in the earliest blocking
milestone and split the later work into child issues.

## Project And Issue Shape

- Smaller roadmap files map to one tracking issue in the matching milestone.
- Micro issues are implementation slices that close one checklist item or gate
  on the tracking issue.
- Gate issues prove CI, docs, benchmark, capability, release, or downstream
  evidence.
- Use labels for stable facts and routing. Use the GitHub Project for workflow
  state and dashboard grouping.
- The organization Project groups and sorts by Milestone, Package, Capability,
  Backend, Readiness, and Release target.

## When a skill says "publish to the issue tracker"

Create a GitHub issue in the repository shown by `git remote -v`.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
