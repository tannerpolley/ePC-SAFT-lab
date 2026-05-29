# Package-Transfer Transition Audit

Milestone: `M1 - Packages`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/177`
Status: `implemented pending PR merge`
Last synced: `2026-05-29`

## Summary

Resolve the remaining package-transfer friction after the provider move into
`packages/epcsaft`. This slice keeps the monorepo as the source of truth and
makes extension package build/install proof executable instead of leaving
`epcsaft-equilibrium` and `epcsaft-regression` as source-checkout shells that
depend on root CMake side effects.

## Acceptance Gates

- [x] `packages/epcsaft-equilibrium` owns package-local native build metadata,
  including a PEP 517/scikit-build backend, `CMakeLists.txt`, and executable
  `_native_core` wheel/sdist proof.
- [x] `packages/epcsaft-regression` owns package-local native build metadata,
  including a PEP 517/scikit-build backend, `CMakeLists.txt`, and executable
  `_native_core` wheel/sdist proof.
- [x] `packages/epcsaft` ships a versioned provider source/CMake SDK that
  extension builds can consume from a monorepo sibling checkout or an installed
  provider package.
- [x] Provider SDK discovery through `epcsaft.provider_native_sdk()` reports
  the source SDK kind/version, CMake config path, source manifest path, include
  root, and supported extension-native consumers.
- [x] A package build proof helper builds and smokes extension packages in both
  monorepo-provider and installed-provider modes.
- [x] Active analysis, script, docs, and tests no longer import retired
  `epcsaft.equilibrium`, `epcsaft.regression`, `epcsaft.equilibrium_core`, or
  `scripts.validation.equilibrium_core` paths outside explicitly historical
  text.
- [x] Docs and structural tests fail if standalone extension package build
  support is claimed without package-local build metadata and proof commands.
- [x] GitHub issue #177 criteria are checked and the PR body contains
  `Closes #177`.

## Proof Receipts

- `uv lock` and `uv sync --all-packages` exited 0.
- `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
  exited 0 and configured Ceres OFF, Ipopt OFF, extension native modules OFF,
  and CppAD ON.
- `uv run --package epcsaft python -c "import epcsaft; import epcsaft._core; print(epcsaft.provider_native_sdk())"`
  exited 0 and reported `provider_only_core=True`, source/CMake SDK metadata,
  and both extension-native flags false.
- `uv run python scripts/dev/build_dist.py --parallel 1` exited 0 and smoke
  imported the provider wheel with no extension-native leakage.
- `uv run python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"`
  exited 0 and smoke imported the extension wheels with package-owned
  `_native_core` modules.
- `uv run python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"`
  exited 0 and proved the extension package builds can consume the provider SDK
  from an installed `epcsaft` wheel.
- `uv run python -c "import epcsaft_equilibrium; import epcsaft_equilibrium._native_core; import epcsaft_regression; import epcsaft_regression._native_core"`
  exited 0 from the source checkout.
- Focused workflow/build tests exited 0 with `150 passed`.
- `uv run python run_pytest.py --provider-api -q` exited 0 with `20 passed`.
- `uv run python run_pytest.py --native-contracts -q` exited 0 with
  `50 passed`.
- `uv run python run_pytest.py --integration -q` exited 0 with `19 passed`.
- `uv run python scripts/dev/validate_project.py quick` exited 0 with
  `153 passed`.
- `uv run python scripts/dev/validate_project.py docs` exited 0 and Sphinx
  reported `build succeeded`.
- Retired-import and old package-root native path audits returned no matches.

## Implementation Notes

- Keep public imports and distribution names unchanged: `epcsaft`,
  `epcsaft_equilibrium`, and `epcsaft_regression`.
- Do not create separate extension GitHub repos, publish to PyPI, or split this
  work into child issues without a new explicit plan.
- Root `CMakeLists.txt` may remain the source-checkout orchestrator, but it
  must not be the only executable extension-native build path.
- Production equilibrium package proof must use a real Ipopt SDK. A no-Ipopt
  smoke is not completion evidence for this issue.
- Regression package proof must build with Ceres through the package-local
  backend.

## Validation

```powershell
uv lock
uv sync --all-packages
uv run python scripts/dev/build_epcsaft.py --clean --profile provider
uv run --package epcsaft python -c "import epcsaft; import epcsaft._core; print(epcsaft.provider_native_sdk())"
uv run python scripts/dev/build_dist.py --parallel 1
uv run python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"
uv run python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"
uv run python -c "import epcsaft_equilibrium; import epcsaft_equilibrium._native_core; import epcsaft_regression; import epcsaft_regression._native_core"
uv run python run_pytest.py tests/workflows/repo/test_internal_package_workspace.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/repo/test_project_structure.py tests/workflows/build/test_build_backend.py tests/workflows/build/test_build_dist.py -q
uv run python run_pytest.py --provider-api -q
uv run python run_pytest.py --native-contracts -q
uv run python run_pytest.py --integration -q
uv run python scripts/dev/validate_project.py quick
uv run python scripts/dev/validate_project.py docs
```

Path audit:

```powershell
rg "from epcsaft\.equilibrium|import epcsaft\.equilibrium|from epcsaft\.regression|import epcsaft\.regression|epcsaft\.equilibrium_core|scripts\.validation\.equilibrium_core" analyses packages scripts tests docs/pages docs/contracts docs/protocols README.md
```

The audit above must return no active references outside explicitly historical
text.
