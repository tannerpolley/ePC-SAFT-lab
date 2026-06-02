# Design Root Workspace Controller And packages/epcsaft Move

Milestone: `M1 - Packages`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/167`
Status: `design complete`
Last synced: `2026-05-29`

## Summary

Design the final monorepo package layout before the provider distribution moves
from the repository root into `packages/epcsaft`. This plan resolves the design
slice only. The provider source move, install proof, and stale-root cleanup
remain owned by #168 and #169.

## Final Ownership

- The repository root becomes a workspace/controller. It owns the root
  `uv.lock`, workspace membership, repo-wide scripts, top-level docs,
  milestone plans, issue templates, GitHub workflow orchestration, and
  cross-package integration tests.
- The root `pyproject.toml` no longer owns the `epcsaft` distribution after the
  move. It should keep only workspace-level configuration and shared
  development groups that are intentionally repo-wide.
- `packages/epcsaft` owns the `epcsaft` distribution metadata, provider source
  tree, scikit-build configuration, provider native packaging configuration,
  package-local provider tests, and provider package docs.
- `packages/epcsaft-equilibrium` and `packages/epcsaft-regression` remain
  workspace members that depend on the workspace `epcsaft` package. They do
  not consume root-owned provider source paths.

## Move Inventory For #168

- Create `packages/epcsaft/pyproject.toml` from the current provider-owned
  root metadata. It must preserve the public distribution name `epcsaft` and
  public import `epcsaft`.
- Move `src/epcsaft` to `packages/epcsaft/src/epcsaft` in the same slice that
  updates imports, build paths, pytest paths, docs, scripts, and CI.
- Move provider package tests to `packages/epcsaft/tests`. Root `tests/` keeps
  repo/workflow, build/package-boundary, docs/registry, integration, and
  cross-package governance tests.
- Move provider-owned build backend code under `packages/epcsaft/build_backend`
  unless #168 proves a smaller package-local backend shape is sufficient. Root
  scripts may orchestrate builds, but root must not own provider wheel/sdist
  metadata.
- Move provider scikit-build ownership under `packages/epcsaft`. A root
  `CMakeLists.txt` may remain only as a repo-dev convenience wrapper; provider
  package builds must resolve source, native output, and install paths from the
  provider package root.
- Replace hard-coded root provider paths in `scripts/dev/build_epcsaft.py`,
  `run_pytest.py`, `packages/epcsaft/src/epcsaft/runtime/capability_evidence.py`,
  docs, and CI with an explicit package-root map.
- Keep the existing extension-native boundary: provider `_core` remains
  provider-only, and extension-native modules remain package-owned.

## Gates For #168 And #169

- #168 may start after this design slice is merged and the branch begins from
  synced `main`.
- #168 must not leave duplicate provider source trees, compatibility wrappers,
  or root-owned provider package metadata.
- #168 must prove `import epcsaft` and `uv run --package epcsaft python -c
  "import epcsaft"` from the workspace after the move.
- #169 owns final install/wheel/sdist proof, stale path removal, and docs/CI
  cleanup after the move lands.
- #154 remains open until #168 and #169 are complete.

## Acceptance Gates

- [x] Root `pyproject.toml` workspace/controller responsibilities are specified.
- [x] Provider package metadata ownership under `packages/epcsaft` is specified.
- [x] CMake, scikit-build, pytest, docs, CI, and script path changes are inventoried.
- [x] The move is blocked until provider-only and native-extension boundary proofs are stable.
- [x] #168 and #169 retain the actual move, install proof, and cleanup work.

## Validation

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_workflow_entrypoints.py -q
uv run python scripts/dev/validate_project.py docs
```

## Receipt

Passed on branch `codex/design-root-workspace-controller-packages-epcsaft-move`
on `2026-05-29`:

- Setup: PGIM `validate-setup.ps1` passed with issue #167, this plan, and
  local-only board `docs/goals/design-root-workspace-controller-packages-epcsaft-move`.
- Design proof: root workspace-controller responsibilities and
  `packages/epcsaft` provider-package ownership are specified above.
- Inventory proof: pyproject, provider source, scikit-build, CMake, build
  backend, pytest, capability evidence, docs, scripts, and CI path changes are
  assigned to #168/#169.
- Guard repair: `CMakeLists.txt` now derives `EPCSAFT_NATIVE_TARGETS` from
  `EPCSAFT_NATIVE_OBJECT_TARGETS` and appends only pybind module targets so the
  existing warning/sanitizer policy guard covers provider and extension object
  targets after the native split.
- Focused proof: `uv run python run_pytest.py
  tests/workflows/repo/test_project_structure.py
  tests/workflows/repo/test_workflow_entrypoints.py -q`: 65 passed.
- Docs proof: `uv run python scripts/dev/validate_project.py docs`: Sphinx
  build passed.
