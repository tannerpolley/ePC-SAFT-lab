# Post-Move Cleanup And Install Proof

Milestone: `M1 - Packages`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/169`
Status: `active`
Last synced: `2026-05-29`

## Summary

Prove the final monorepo package layout after the provider distribution move.
This slice closes #169 and, if every parent gate is honestly satisfied, closes
#154 as the completed M1 provider-package move tracker.

## Acceptance Gates

- [x] Workspace editable installs work for `epcsaft`, `epcsaft-equilibrium`,
  and `epcsaft-regression`.
- [x] Provider wheel/sdist checks prove `pip install epcsaft` remains
  provider-only and does not require Ceres or Ipopt.
- [x] Active docs, CI, scripts, build config, and tests no longer require the
  retired root provider paths `src/epcsaft`, root `epcsaft`, or root
  `build_backend`.
- [x] Stale scripts, tests, exports, compatibility wrappers, and M1 tracker
  entries from the root-provider layout are removed or explicitly marked
  historical.
- [x] #169 acceptance criteria are checked and the PR body contains
  `Closes #169`.
- [x] #154 has every child and parent acceptance criterion checked and the PR
  body contains `Closes #154`.

## Proof Receipts

- `uv lock` passed.
- `uv sync --all-packages` passed.
- Package import smokes passed for `epcsaft`, `epcsaft-equilibrium`, and
  `epcsaft-regression`.
- `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
  built provider `_core` with Ceres OFF, Ipopt OFF, extension native modules
  OFF, and CppAD ON.
- `uv run python scripts/dev/build_dist.py --parallel 1` built provider
  sdist/wheel from `packages/epcsaft` and the isolated wheel smoke confirmed
  provider-only `_core`.
- Focused repo/build workflow tests, provider API, native contracts,
  integration, quick validation, and docs validation passed.
- Path audit confirmed no tracked root provider source, root provider shim, or
  root provider build backend.

## Implementation Notes

- Keep the public import and distribution names as `epcsaft`.
- Keep root `pyproject.toml` as the workspace/controller and
  `packages/epcsaft` as the provider distribution owner.
- Do not do PyPI, release, downstream private-repo migration, or provider API
  redesign work in this slice.
- Historical plans may mention retired paths only when they are clearly
  superseded and not used as current workflow guidance.

## Validation

```powershell
uv lock
uv sync --all-packages
uv run --package epcsaft python -c "import epcsaft; import epcsaft._core; print(epcsaft.provider_native_sdk())"
uv run --package epcsaft-equilibrium python -c "import epcsaft_equilibrium"
uv run --package epcsaft-regression python -c "import epcsaft_regression"
uv run python scripts/dev/build_epcsaft.py --clean --profile provider
uv run python scripts/dev/build_dist.py --parallel 1
uv run python run_pytest.py tests/workflows/repo/test_internal_package_workspace.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/build/test_build_dist.py -q
uv run python run_pytest.py --provider-api -q
uv run python run_pytest.py --native-contracts -q
uv run python run_pytest.py --integration -q
uv run python scripts/dev/validate_project.py quick
uv run python scripts/dev/validate_project.py docs
```

Path audit:

```powershell
git ls-files src/epcsaft epcsaft build_backend
```

The command above must return no tracked provider files. Active workflow,
build, test, docs, and CI paths must resolve provider ownership through
`packages/epcsaft`.
