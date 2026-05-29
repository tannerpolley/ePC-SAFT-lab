# Test Ownership Relocation Roadmap

Issue: [#152](https://github.com/ePC-SAFT/ePC-SAFT/issues/152)

## Purpose

This tranche completes the test-layout cleanup required by the monorepo package
reorganization. The root `tests/` tree remains the owner for provider,
repository, build, integration, registry, and workflow contracts. Extension
packages own their own API, native, solver-dependency, and result-contract tests
inside their package-local `tests/` trees.

This roadmap is intentionally limited to test ownership and validation routing.
It does not move the core package into `packages/epcsaft`, split native modules,
change solver behavior, change public imports, or prepare releases.

## Target State

- `tests/` owns provider API tests, repository/workflow checks, build/package
  checks, docs and capability-registry governance, integration checks, and
  cross-package boundary tests.
- `packages/epcsaft-equilibrium/tests/` owns equilibrium API, native
  equilibrium, Ipopt/result/selector, diagnostics, and equilibrium contract
  tests.
- `packages/epcsaft-regression/tests/` owns regression API, native regression,
  Ceres/backend, result-schema, and regression contract tests.
- Package-local tests do not import `tests.support`; each extension package owns
  any fixtures required for its local test tree.
- `run_pytest.py`, `src/epcsaft/runtime/capability_evidence.py`, structural
  tests, and workflow docs route extension validation through package-local
  paths.

## Non-Goals

- No native module split.
- No core move into `packages/epcsaft`.
- No solver algorithm changes.
- No public package API changes.
- No PyPI, release, or publishing workflow changes.
- No removal of global registry, roadmap, or integration tests that govern the
  whole monorepo.

## Ownership Matrix

| Current owner | Test family | Final owner |
| --- | --- | --- |
| `tests/api/frontend/test_regression.py` | Regression public API | `packages/epcsaft-regression/tests/api/` |
| `tests/native/regression/*.py` | Regression native/Ceres/backend tests | `packages/epcsaft-regression/tests/native/` |
| Root native contracts that assert Ceres/regression behavior | Regression build/backend contracts | `packages/epcsaft-regression/tests/contracts/` |
| `tests/native/equilibrium/blocks/**` | Equilibrium NLP block tests | `packages/epcsaft-equilibrium/tests/native/blocks/` |
| `tests/native/equilibrium/diagnostics/**` | Equilibrium diagnostics tests | `packages/epcsaft-equilibrium/tests/native/diagnostics/` |
| `tests/native/equilibrium/results/**` | Equilibrium result tests | `packages/epcsaft-equilibrium/tests/native/results/` |
| `tests/native/contracts/test_equilibrium_native_contracts.py` | Equilibrium native/result contracts | `packages/epcsaft-equilibrium/tests/contracts/` |
| Root registry and roadmap tests | Global capability and documentation governance | `tests/` |
| Root provider, build, repo, docs, workflow, and integration tests | Provider/repo/cross-package contracts | `tests/` |

## Gates

- [x] Regression API/native/Ceres tests live under
  `packages/epcsaft-regression/tests/`.
- [x] Equilibrium API/native/Ipopt/result/selector tests live under
  `packages/epcsaft-equilibrium/tests/`.
- [x] Package-local tests do not import `tests.support`.
- [x] Root `tests/` retains provider, repo/workflow, build/package,
  docs/registry, integration, and cross-package boundary tests only.
- [x] `run_pytest.py` routes `--regression`, `--equilibrium-api`,
  `--native-contracts`, `--all`, debug target prefixes, long-target guards, and
  equilibrium confidence paths to current owners.
- [x] `src/epcsaft/runtime/capability_evidence.py` names package-local
  validation targets for extension-owned lanes.
- [x] Workflow and package-architecture docs describe the package-local test
  ownership model.
- [x] Structural tests prevent extension-owned tests from returning to root
  native/API trees.
- [x] Obsolete shallow root support files are removed when no imports remain.
- [ ] Pull request body contains `Closes #152`.

## Proof Oracle

Focused checks:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_internal_package_workspace.py tests/workflows/repo/test_package_extension_boundary.py -q
uv run python run_pytest.py --provider-api -q
uv run python run_pytest.py --regression -q
uv run python run_pytest.py --equilibrium-api -q
uv run python run_pytest.py --native-contracts -q
```

Closure checks:

```powershell
uv run python scripts/dev/validate_project.py quick
uv run python scripts/dev/validate_project.py docs
```

Path audit:

```powershell
rg "from tests\.support|import tests\.support" packages/epcsaft-equilibrium/tests packages/epcsaft-regression/tests
rg --files tests/native/equilibrium tests/native/regression
```

The first audit command must find no package-local imports from root
`tests.support`. The second command must find no extension-owned native test
files remaining in the root tree; any retained root file must be a global
registry, workflow, integration, or boundary-governance test with an explicit
reason.

Cleanup hook:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Receipts

Implementation receipts belong in the GitHub issue, the pull request, and the
local GoalBuddy board while the goal is active. The local GoalBuddy board is
ephemeral and must be deleted before staging tracked changes.

Current receipts:

- `uv run python run_pytest.py tests/workflows/repo/test_run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_internal_package_workspace.py tests/workflows/repo/test_package_extension_boundary.py -q`: 113 passed.
- `uv run python run_pytest.py --provider-api -q`: 16 passed.
- `uv run python run_pytest.py --regression -q`: 13 passed.
- `uv run python run_pytest.py --equilibrium-api -q`: 23 passed.
- `uv run python run_pytest.py --native-contracts -q`: 49 passed, 1 skipped for provider-profile-only symbol proof.
- `uv run python scripts/dev/validate_project.py quick`: doctor passed, pytest 145 passed, 1 skipped for provider-profile-only symbol proof.
- `uv run python scripts/dev/validate_project.py docs`: Sphinx build passed.
- `uv run python scripts/docs/sync_algorithm_registry.py --check`: algorithm registry outputs are up to date.
- Path audit: no package-local tests import `tests.support`; no files remain under root `tests/native/equilibrium` or `tests/native/regression`.
