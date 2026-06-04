# Superpowers Milestones

This folder stores durable milestone pages for the GitHub milestone tracker.
GitHub Issues and the `ePC-SAFT Roadmap` Project remain authoritative for live
state, ownership fields, readiness, and release target.

Use this folder for fast local orientation:

- `docs/superpowers/PROJECT_CONTEXT.md` gives full package context and milestone meaning.
- `docs/superpowers/milestones/M*/README.md` gives the current milestone dashboard view.
- `docs/superpowers/specs/*.md` stores durable specs and migrated milestone planning notes.
- `docs/superpowers/plans/*.md` stores implementation plans written from approved specs or issue mirrors.
- `docs/superpowers/issues/*.md` stores optional concise handoff notes for issues that need local context.
- `docs/superpowers/milestones/M*/registries/*` stores milestone-owned registry files when a milestone has executable evidence.
- `docs/superpowers/_templates/` stores reusable local spec, plan, and issue-mirror shapes.

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
| `M8-python-toybox` | `M8 - Python Toybox` |

## Planning Rules

- Put durable specs and planning notes under `docs/superpowers/specs/`.
- Put implementation plans under `docs/superpowers/plans/`.
- Use `docs/superpowers/_templates/spec.md` when creating a durable local spec.
- Use `docs/superpowers/_templates/issue-mirror.md` only when a GitHub issue needs local handoff context.
- Link the GitHub issue to the local source spec or source plan when one exists.
- Keep `last_synced` current when the mirror is intentionally refreshed.
- Do not close a GitHub issue from Markdown state alone.
- Use GitHub as the source of truth for status, milestone, labels, Project fields, comments, and PR links.
