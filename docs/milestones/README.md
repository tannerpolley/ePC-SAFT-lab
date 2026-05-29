# Milestone Plans

This folder is the local planning root for the GitHub milestone tracker.
GitHub Issues and the `ePC-SAFT Roadmap` Project remain authoritative for live
state, ownership fields, readiness, and release target.

Use this folder for fast local orientation:

- `docs/milestones/PROJECT_CONTEXT.md` gives full package context and milestone meaning.
- `docs/milestones/M*/README.md` gives the current milestone dashboard view.
- `docs/milestones/M*/plans/*.md` stores durable plans created for larger issues or tranches.
- `docs/milestones/M*/issues/*.md` stores optional concise handoff notes for issues that need local context.
- `docs/milestones/M*/registries/*` stores milestone-owned registry files when a milestone has executable evidence.

Do not require an exact Markdown file for every GitHub issue. Small issues can
live only in GitHub. If a local file disagrees with GitHub, update the local
file from GitHub rather than treating the Markdown as authoritative.

## Milestone Folders

| Folder | GitHub milestone |
| --- | --- |
| `M0-governance` | `M0 - Governance` |
| `M1-packages` | `M1 - Packages` |
| `M2-python-api` | `M2 - Python API` |
| `M3-eos` | `M3 - EOS` |
| `M4-equilibrium` | `M4 - Equilibrium` |
| `M5-regression` | `M5 - Regression` |
| `M6-validation` | `M6 - Validation` |
| `M7-release` | `M7 - Release` |

## Planning Rules

- Put full plans from the plan-goal-implement-merge workflow under the matching milestone folder.
- Link the GitHub issue to the local plan file when a plan exists.
- Keep `last_synced` current when the mirror is intentionally refreshed.
- Do not close a GitHub issue from Markdown state alone.
- Use GitHub as the source of truth for status, milestone, labels, Project fields, comments, and PR links.
