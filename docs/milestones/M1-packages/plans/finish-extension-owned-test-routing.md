# Finish Extension-Owned Test Routing

Milestone: `M1 - Packages`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/166`
Status: `PR opened`
Last synced: `2026-05-29`

## Summary

Close the M1 test-routing slice by proving that extension-owned regression and
equilibrium tests now live in package-local test trees after monorepo
consolidation. This is an evidence-hardening and tracker-closure slice: the
prior test-ownership relocation work already moved the tests, so this plan
verifies the current state, records receipts, and only adds guards if an audit
finds drift.

## Target State

- `packages/epcsaft-regression/tests/` owns regression API, native, Ceres,
  result, and regression contract tests.
- `packages/epcsaft-equilibrium/tests/` owns equilibrium API, native, Ipopt,
  selector, result, diagnostics, and equilibrium contract tests.
- Package-local extension tests do not import root `tests.support`.
- Root `tests/` remains limited to provider, repository/workflow, build,
  package-boundary, docs/registry, integration, and cross-package governance
  tests.
- `run_pytest.py` and `src/epcsaft/runtime/capability_evidence.py` route
  extension validation lanes to package-owned test paths.

## Non-Goals

- No core move into `packages/epcsaft`.
- No native module split or native ownership changes.
- No package API changes.
- No broad test relocation unless the audit finds actual drift.
- No closure of #167, #168, #169, or parent #154.

## Acceptance Gates

- [x] Regression API/native/Ceres tests run from
  `packages/epcsaft-regression/tests/`.
- [x] Equilibrium API/native/Ipopt tests run from
  `packages/epcsaft-equilibrium/tests/`.
- [x] Package-local tests do not import root `tests.support`.
- [x] `run_pytest.py` and capability evidence route extension lanes to
  package-owned paths.
- [x] Structural tests prevent extension-owned native/regression/equilibrium
  tests from returning to root `tests/`.
- [x] Root `tests/` ownership remains provider, repo/workflow, build/package,
  docs/registry, integration, and boundary-governance only.
- [x] GitHub issue #166 and the local issue mirror contain proof receipts.
- [x] Pull request body contains `Closes #166`; parent #154 remains open.

## Proof Oracle

Focused proof:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py::test_extension_owned_tests_are_package_local tests/workflows/repo/test_project_structure.py::test_package_local_extension_tests_do_not_import_root_test_support tests/workflows/repo/test_run_pytest.py::test_pytest_slices_are_adapted_from_capability_evidence_registry tests/workflows/repo/test_run_pytest.py::test_slice_targets_use_grouped_test_subpackages tests/workflows/repo/test_run_pytest.py::test_regression_slice_is_package_owned -q
rg "from tests\.support|import tests\.support" packages/epcsaft-equilibrium/tests packages/epcsaft-regression/tests
if ($LASTEXITCODE -eq 0) { throw "package-local extension tests import root tests.support" }
if ($LASTEXITCODE -gt 1) { exit $LASTEXITCODE }
Write-Output "no package-local tests.support imports found"
$legacyNativeTests = @()
foreach ($path in @('tests\native\equilibrium', 'tests\native\regression')) {
  if (Test-Path -LiteralPath $path) {
    $legacyNativeTests += @(Get-ChildItem -LiteralPath $path -Recurse -File)
  }
}
if ($legacyNativeTests.Count -gt 0) { $legacyNativeTests.FullName; throw "root extension-owned native tests remain" }
Write-Output "no root extension-owned native tests found"
```

Closure proof:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_internal_package_workspace.py tests/workflows/repo/test_package_extension_boundary.py -q
uv run python run_pytest.py --regression -q
uv run python run_pytest.py --equilibrium-api -q
uv run python run_pytest.py --native-contracts -q
uv run python scripts/dev/validate_project.py docs
```

## Prior Receipt

The prior implementation receipt is
`docs/milestones/M1-packages/plans/test-ownership-relocation.md`. This plan is
the active closure record for issue #166.

## Current Receipt

Proof passed on branch `codex/finish-extension-owned-test-routing` on
`2026-05-29`.

- Setup: PGIM `validate-setup.ps1` passed with issue #166, branch
  `codex/finish-extension-owned-test-routing`, this plan, and local-only board
  `docs/goals/finish-extension-owned-test-routing`.
- Ownership audit: extension-owned tests are present under
  `packages/epcsaft-equilibrium/tests/` and
  `packages/epcsaft-regression/tests/`; root `tests/native/equilibrium` and
  `tests/native/regression` have no files.
- Support audit: `rg "from tests\.support|import tests\.support"
  packages/epcsaft-equilibrium/tests packages/epcsaft-regression/tests` found
  no package-local imports from root `tests.support`.
- Focused proof: `uv run python run_pytest.py
  tests/workflows/repo/test_project_structure.py::test_extension_owned_tests_are_package_local
  tests/workflows/repo/test_project_structure.py::test_package_local_extension_tests_do_not_import_root_test_support
  tests/workflows/repo/test_run_pytest.py::test_pytest_slices_are_adapted_from_capability_evidence_registry
  tests/workflows/repo/test_run_pytest.py::test_slice_targets_use_grouped_test_subpackages
  tests/workflows/repo/test_run_pytest.py::test_regression_slice_is_package_owned
  -q`: 5 passed.
- Workflow/repo closure proof: `uv run python run_pytest.py
  tests/workflows/repo/test_run_pytest.py
  tests/workflows/repo/test_project_structure.py
  tests/workflows/repo/test_internal_package_workspace.py
  tests/workflows/repo/test_package_extension_boundary.py -q`: 114 passed.
- Regression proof: `uv run python run_pytest.py --regression -q`: 13
  passed.
- Equilibrium API proof: `uv run python run_pytest.py --equilibrium-api -q`:
  23 passed.
- Native-contract proof: `uv run python run_pytest.py --native-contracts -q`:
  50 passed.
- Docs proof: `uv run python scripts/dev/validate_project.py docs`: Sphinx
  build passed.
- Implementation decision: no additional test relocation or structural guard
  was needed; existing repository tests already enforce the ownership boundary.
- Pull request proof: [#173](https://github.com/ePC-SAFT/ePC-SAFT/pull/173)
  contains `Closes #166`. Parent issue #154 remains open until the final
  package-move tracking issue is complete.
