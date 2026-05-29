# Milestone Mirror

This folder is the local, agent-facing mirror of the GitHub roadmap tracker.
GitHub Issues and the `ePC-SAFT Roadmap` Project remain authoritative for live
state, ownership fields, readiness, and release target.

Use this folder for fast local orientation:

- `docs/roadmaps/FULL_ROADMAP.md` gives full package context and milestone meaning.
- `docs/milestones/M*/README.md` gives the current milestone dashboard view.
- `docs/milestones/M*/issues/*.md` gives concise handoff notes for open issues.

Do not treat these issue mirror files as full GitHub issue duplicates. If a
mirror disagrees with GitHub, update the mirror from GitHub rather than treating
the Markdown as authoritative.

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

## Sync Rules

- Mirror open issues only unless a future governance issue explicitly backfills closed history.
- Each issue mirror must include front matter with the GitHub issue URL and Project fields.
- Keep `last_synced` current when the mirror is intentionally refreshed.
- Do not close a GitHub issue from Markdown state alone.
- Use GitHub as the source of truth for status, milestone, labels, Project fields, comments, and PR links.
