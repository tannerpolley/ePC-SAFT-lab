# Move Provider Distribution Into packages/epcsaft

Milestone: `M1 - Packages`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/168`
Status: `active`
Last synced: `2026-05-29`

## Summary

Move the provider-owned `epcsaft` distribution from the repository root into
`packages/epcsaft` while preserving the public distribution name and public
import. The repository root becomes a workspace/controller for uv, scripts,
docs, CI orchestration, and cross-package validation. This slice resolves the
actual package move; #169 retains final post-move install proof and exhaustive
stale-reference cleanup.

## Acceptance Gates

- [x] `packages/epcsaft` owns the `epcsaft` distribution metadata,
  scikit-build configuration, provider build backend, source tree, and
  provider package tests.
- [x] Root `pyproject.toml` is workspace/controller-only and no longer owns
  provider `[project]`, build backend, or scikit-build distribution config.
- [x] Public import remains `import epcsaft`, including
  `uv run --package epcsaft python -c "import epcsaft; import epcsaft._core"`.
- [x] Public distribution remains `epcsaft`; package build tooling targets
  `packages/epcsaft`.
- [x] No tracked provider source remains under root `src/epcsaft` or root
  `epcsaft`.
- [x] Provider package tests live under `packages/epcsaft/tests`; root tests
  remain for repo/workflow, build/package-boundary, docs/registry,
  integration, and cross-package governance.
- [x] Active CMake, build, pytest, docs, CI, and workflow guards resolve the
  provider package root from `packages/epcsaft`.
- [x] #154 remains open, the PR closeout path closes #168 and checks only the
  #168 child item, and #169 remains open.

## Proof Receipts

- `uv lock` and `uv sync --all-packages` pass with all three workspace
  distributions.
- Package import smokes pass for `epcsaft`, `epcsaft-equilibrium`, and
  `epcsaft-regression`; provider Python imports from `packages/epcsaft/src`.
- `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
  builds provider `_core` with Ceres OFF, Ipopt OFF, extension native modules
  OFF, and CppAD ON.
- `uv run python scripts/dev/build_epcsaft.py --clean --disable-ipopt` builds
  provider `_core` plus package-owned extension native modules from the
  monorepo packages.
- `uv run python scripts/dev/build_dist.py --parallel 1` builds the provider
  sdist/wheel from `packages/epcsaft` and the wheel smoke confirms
  provider-only `_core`.
- Focused repo/package guards, provider API, native contracts, integration,
  regression, and equilibrium API slices pass.
- `uv run python scripts/dev/validate_project.py quick` passes with 151 tests.
- `uv run python scripts/dev/validate_project.py docs` builds Sphinx
  successfully.
- Path audit confirms `git ls-files src/epcsaft epcsaft` returns no tracked
  provider files and package-local tests do not import root `tests.support`.

## Implementation Notes

- Keep root `CMakeLists.txt` as the repo-wide native build wrapper, but make
  provider source, version lookup, include paths, native output copy, and
  in-place `_core` placement derive from `packages/epcsaft`.
- Move the provider PEP 517 build backend under
  `packages/epcsaft/build_backend`. Repo scripts may orchestrate builds, but
  provider wheel/sdist ownership must be package-local.
- Add one shared package-path helper for repo scripts and tests so provider
  path policy is not scattered across `run_pytest.py`, build scripts, and
  validation scripts.
- Preserve the extension-native boundary established by #165. Extension public
  imports and extension-owned native modules do not change in this slice.
- Update live docs and workflow guard tests that describe the provider layout.
  #169 owns final broad stale-reference cleanup after this move lands.

## Validation

```powershell
uv lock
uv sync --all-packages
uv run --package epcsaft python -c "import epcsaft; import epcsaft._core; print(epcsaft.provider_native_sdk())"
uv run --package epcsaft-equilibrium python -c "import epcsaft_equilibrium"
uv run --package epcsaft-regression python -c "import epcsaft_regression"
uv run python scripts/dev/build_epcsaft.py --clean --profile provider
uv run python scripts/dev/build_epcsaft.py --clean --disable-ipopt
uv run python scripts/dev/build_dist.py --parallel 1
uv run python run_pytest.py tests/workflows/repo/test_internal_package_workspace.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_workflow_entrypoints.py packages/epcsaft/tests/api/package/test_package_main.py -q
uv run python run_pytest.py --provider-api -q
uv run python run_pytest.py --native-contracts -q
uv run python run_pytest.py --integration -q
uv run python scripts/dev/validate_project.py quick
uv run python scripts/dev/validate_project.py docs
```

Path audit:

```powershell
git ls-files src/epcsaft epcsaft
```

The command above must return no tracked provider files. Package-local provider
tests must not import root `tests.support`, and active workflow/build/test
configuration must use `packages/epcsaft` for provider package paths.
