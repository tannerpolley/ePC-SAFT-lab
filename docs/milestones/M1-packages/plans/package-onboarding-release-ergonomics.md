# Package Onboarding And Release Ergonomics

Milestone: `M1 - Packages`
Issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/179`
Status: `implemented-pending-pr`
Last synced: `2026-05-29`

## Summary

Resolve the remaining post-package-transfer friction after the provider and
extension distributions moved into `packages/`. The goal is executable
onboarding and package proof, not actual PyPI publication.

## Acceptance Gates

- [x] `scripts/dev/bootstrap.py` is the first-run entrypoint and runs uv sync,
      native build, doctor, and prints the next exact validation command.
- [x] `scripts/dev/doctor.py` reports provider SDK metadata, extension native
      module state, local Ipopt SDK discovery, reusable Ceres package state,
      and source-checkout artifact freshness.
- [x] Local dependency reuse guidance names the supported Ceres cache and
      Ipopt SDK paths without implying fake no-Ipopt production proof.
- [x] Extension package proof prefers the reusable Ceres package/cache when it
      exists and does not rebuild Ceres source repeatedly in that case.
- [x] `epcsaft-equilibrium` wheel packaging installs an audited Ipopt runtime
      dependency payload instead of copying every DLL from the SDK `bin/`
      directory.
- [x] Bootstrap and doctor report the active Ipopt SDK root, provenance, default
      probe paths, and exact command to change the root.
- [x] GitHub Actions expose provider package, regression package, equilibrium
      package, and installed-provider extension build lanes.
- [x] Local release/install proof installs built artifacts for `epcsaft`,
      `epcsaft-equilibrium`, and `epcsaft-regression` in the supported
      combinations.
- [x] `docs/agents/new-agent-start-here.md` points agents to current commands
      only.
- [x] Docs, structural tests, workflow tests, and issue tracker receipts agree
      with the executable commands.

## Implementation Notes

- Completion means proof plus workflows. Real PyPI upload and trusted-publisher
  activation are out of scope for this issue.
- Production equilibrium package proof requires a real Ipopt SDK. Hosted CI may
  block only the Ipopt-dependent lane if the configured SDK artifact is absent;
  local proof must still use the real SDK.
- Public import and distribution names remain `epcsaft`,
  `epcsaft_equilibrium`, and `epcsaft_regression`.

## Validation

Passed local proof before PR handoff:

- `uv lock`
- `uv sync --all-packages`
- `uv run python scripts/dev/bootstrap.py --dry-run`
- `uv run python scripts/dev/bootstrap.py`
- `uv run python scripts/dev/doctor.py --require-provider-sdk --require-extension-native`
- `uv run python scripts/dev/build_system_ceres.py --print-env`
- `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
- `uv run python scripts/dev/build_dist.py --parallel 1`
- `uv run python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"`
- `uv run python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"`
- `uv run python scripts/dev/check_release_installs.py --dist-dir dist`
- `uv run python run_pytest.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/repo/test_project_structure.py tests/workflows/build/test_build_dist.py tests/workflows/build/test_build_extension_dists.py tests/workflows/build/test_build_system_ceres.py tests/workflows/build/test_build_backend.py tests/workflows/build/test_native_runtime_env.py -q`
- `uv run python run_pytest.py --provider-api -q`
- `uv run python run_pytest.py --native-contracts -q`
- `uv run python run_pytest.py --integration -q`
- `uv run python scripts/dev/validate_project.py quick`
- `uv run python scripts/dev/validate_project.py docs`

Remaining closeout is PR merge, #179 closure, default-branch sync, local board
removal, and cleanup hook proof.
