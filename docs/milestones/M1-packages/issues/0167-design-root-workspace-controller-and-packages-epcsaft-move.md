---
issue: 167
title: "M1: design root workspace controller and packages/epcsaft move"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/167"
state: "open"
milestone: "M1 - Packages"
project: "ePC-SAFT Roadmap"
package: "core"
capability: null
backend: null
readiness: "needs design"
release_target: "future"
last_synced: "2026-05-29"
---

# M1: design root workspace controller and packages/epcsaft move

Child slice of #154. Designs the final workspace-controller layout before any
provider source move.

## Design Receipt

The active design plan is
`docs/milestones/M1-packages/plans/design-root-workspace-controller-packages-epcsaft-move.md`.

The agreed target is:

- root owns workspace control, lockfile, repo-wide docs, scripts, CI
  orchestration, milestone plans, and cross-package integration contracts;
- `packages/epcsaft` owns the `epcsaft` distribution metadata, provider source,
  scikit-build configuration, provider native packaging, package-local provider
  tests, and provider package docs;
- extension packages depend on the workspace `epcsaft` member and must not
  consume root-owned provider source paths.

The future move remains blocked from this slice: #168 performs the move, and
#169 proves final installs and removes stale path residue.

## Proof Receipt

- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_workflow_entrypoints.py -q`: 65 passed.
- `uv run python scripts/dev/validate_project.py docs`: Sphinx build passed.
- #167 is design-only. No provider source, package metadata, build behavior,
  public import name, or distribution name changes are made by this slice.
