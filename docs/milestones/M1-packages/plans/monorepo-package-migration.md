# Monorepo Package Migration Plan

Issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/150

## Target State

The canonical source of truth is one GitHub organization repository:

```text
ePC-SAFT/ePC-SAFT
```

The final monorepo package ecosystem publishes three Python distributions:

```text
epcsaft
epcsaft-equilibrium
epcsaft-regression
```

The temporary package layout for the first consolidation tranche is:

```text
ePC-SAFT/
  pyproject.toml                  # temporary root-owned epcsaft core package
  CMakeLists.txt                  # transitional root native build
  src/epcsaft/
  tests/
  packages/
    epcsaft-equilibrium/
    epcsaft-regression/
```

The final workspace layout is:

```text
ePC-SAFT/
  pyproject.toml                  # workspace controller
  packages/
    epcsaft/
    epcsaft-equilibrium/
    epcsaft-regression/
```

Do not move root `epcsaft` into `packages/epcsaft` until source consolidation,
package-local test ownership, provider-only build proof, and extension-native
ownership are already stable.

## Invariants

- No Git submodules.
- No long-term sibling source dependency.
- `pip install epcsaft` must remain a core-only install/build target.
- `epcsaft` does not import `epcsaft_equilibrium` or `epcsaft_regression`.
- Active build, docs, scripts, and tests must not require
  `../epcsaft-equilibrium` or `../epcsaft-regression`.
- Extension package import names remain `epcsaft_equilibrium` and
  `epcsaft_regression`.
- Extension packages stay unpublished transition packages until their native
  modules no longer depend on provider-owned `_core` extension symbols.
- Native extension behavior may remain transitional during source consolidation,
  but native sources must be read from monorepo package directories.
- Ipopt belongs to `epcsaft-equilibrium`; Ceres belongs to
  `epcsaft-regression`.

## Source Inventory

The first consolidation tranche copies the current sibling repositories back
into the monorepo without preserving Git history:

| Package | Source path | Source commit | Destination |
| --- | --- | --- | --- |
| `epcsaft-equilibrium` | `C:\Users\Tanner\Documents\Workspaces\Engineering\epcsaft-equilibrium` | `32b9a1d` | `packages/epcsaft-equilibrium` |
| `epcsaft-regression` | `C:\Users\Tanner\Documents\Workspaces\Engineering\epcsaft-regression` | `d12d55e` | `packages/epcsaft-regression` |

Do not copy sibling `.git/`, `.gitignore`, `uv.lock`, `.venv/`, build outputs,
dist outputs, caches, or generated artifacts. The root monorepo owns the lockfile
and ignore policy.

## Phase 1: Source Consolidation

Goal: make the main repo the only active source checkout used by local builds,
tests, docs, and package metadata.

Gates:

- [x] `packages/epcsaft-equilibrium` contains the copied equilibrium package
  Python, native, docs, tests, README, LICENSE, and `pyproject.toml`.
- [x] `packages/epcsaft-regression` contains the copied regression package
  Python, native, docs, tests, README, LICENSE, and `pyproject.toml`.
- [x] Root uv workspace includes both extension package members.
- [x] Extension metadata uses `epcsaft==0.2.*` and
  `epcsaft = { workspace = true }`.
- [x] Extension metadata declares transition-only publication state and required
  provider-native build symbols.
- [x] CMake reads transitional extension native sources from `packages/`.
- [x] Pytest, Sphinx, scripts, and workflow tests use `packages/` paths.
- [x] Active path audit finds no sibling checkout dependency outside plan
  history or archived discussion documents.

Validation:

```powershell
uv lock
uv sync --all-packages
uv run python -c "import epcsaft"
uv run --package epcsaft-equilibrium python -c "import epcsaft_equilibrium"
uv run --package epcsaft-regression python -c "import epcsaft_regression"
uv run python scripts/dev/build_epcsaft.py --profile fast
uv run python run_pytest.py tests/workflows/repo/test_internal_package_workspace.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_run_pytest.py tests/workflows/repo/test_package_extension_boundary.py -q
uv run python run_pytest.py --provider-api -q
uv run python run_pytest.py --integration -q
uv run python scripts/dev/validate_project.py quick
uv run python scripts/dev/validate_project.py docs
```

## Phase 2: Provider-Only Build Reproof

Goal: after source consolidation, prove again that the root provider package can
build and import without Ipopt, Ceres, equilibrium-native symbols, or
regression-native symbols.

Gates:

- [ ] Provider-only build profile configures with Ceres off and Ipopt off.
- [ ] `epcsaft._core` exposes provider-owned symbols only in the provider profile.
- [ ] Provider tests fail if equilibrium or regression symbols leak into core.
- [ ] Docs and CI name this as the core install proof.

## Phase 3: Extension Native Package Ownership

Goal: split extension-native modules from the provider-owned `_core` dumping
ground after the monorepo source layout is stable.

Gates:

- [ ] `epcsaft-equilibrium` owns its Ipopt-facing native module or target.
- [ ] `epcsaft-regression` owns its Ceres-facing native module or target.
- [ ] Extension modules consume the provider contract instead of private core
  implementation internals.
- [ ] Package-local tests prove each extension independently.
- [ ] Cross-package integration tests prove combined workflows explicitly.

## Phase 4: CI, Docs, Release, And Repo Cleanup

Goal: make the monorepo package ecosystem visible and releasable.

Gates:

- [ ] CI has separate core, equilibrium, regression, docs, and integration lanes.
- [ ] PyPI/release docs publish `epcsaft`, `epcsaft-equilibrium`, and
  `epcsaft-regression` from one repo.
- [ ] Old sibling GitHub repos are archived or clearly point to the monorepo.
- [ ] User-facing docs stop implying sibling repo source checkouts.
- [ ] Root package move to `packages/epcsaft` is separately planned and gated.

## Non-Goals For Issue 150

- Do not move root `epcsaft` into `packages/epcsaft`.
- Do not complete the final native module split.
- Do not publish packages.
- Do not archive GitHub repositories.
- Do not add compatibility wrappers for the old sibling repo layout.

## Issue 150 Completion Gate

Issue 150 is complete only when Phase 1 gates pass, validation results are
recorded in the issue and PR, and the source tree no longer relies on sibling
extension checkouts for active build/test/docs/script workflows.

## Issue 150 Receipt

Completed on branch `codex/monorepo-source-consolidation`.

Validation passed:

- `uv lock`
- `uv sync --all-packages`
- `uv run python -c "import epcsaft"`
- `uv run --package epcsaft-equilibrium python -c "import epcsaft_equilibrium"`
- `uv run --package epcsaft-regression python -c "import epcsaft_regression"`
- `uv run python scripts/dev/build_epcsaft.py --profile fast`
- `uv run python run_pytest.py tests/workflows/repo/test_internal_package_workspace.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_run_pytest.py tests/workflows/repo/test_package_extension_boundary.py -q`
- `uv run python run_pytest.py --provider-api -q`
- `uv run python run_pytest.py --integration -q`
- `uv run python scripts/dev/validate_project.py quick`
- `uv run python scripts/dev/validate_project.py docs`

The active path audit found no live build, test, script, docs-config, or
workflow dependency on sibling extension checkouts. The only remaining sibling
checkout references are this plan's source inventory/forbidden-path gate and
the explicitly superseded historical transfer plan.
