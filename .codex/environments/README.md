# ePC-SAFT Codex Environment

This folder intentionally has one Codex app environment: `environment.toml`.
The files are tracked so Codex app worktrees receive the current Linux
bootstrap contract from Git.

The setup path is:

```bash
bash .codex/environments/setup.sh
```

The setup wrapper checks common Linux prerequisites before every action and
requires the Ipopt development files for setup, equilibrium-native, and
full-native actions. A migrated checkout therefore fails with Debian/Zorin
install guidance before a later native-build error.

The Bash wrapper is intentionally thin. The changing project/package setup
lives in tracked Python code:

```bash
uv sync --no-install-workspace
uv run --no-sync python scripts/dev/bootstrap.py
```

The setup wrapper and Python bootstrap run the full-native setup sequence:

```bash
uv sync --no-install-workspace
uv run --no-sync python scripts/dev/build_system_ceres.py --parallel 2
uv run --no-sync python scripts/dev/build_epcsaft.py --use-system-ceres --ceres-dir <CeresConfig-dir>
uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-extension-native
```

This keeps new Codex app worktrees aligned with the current package split
without relying on IDE-owned project metadata.

The native build action intentionally uses the current bootstrap build step:
Ceres, CppAD, and native Ipopt are enabled when available. The Python bootstrap
resolves `EPCSAFT_IPOPT_ROOT` and `EPCSAFT_PEP517_IPOPT_ROOT`, then checks the
Linux default install roots reported by `scripts/dev/doctor.py`. When an Ipopt
root has a usable `lib`, `lib64`, or `lib/x86_64-linux-gnu` directory, the build
helpers prepend it to `LD_LIBRARY_PATH`.

Use `Provider Smoke` for a fresh Codex worktree check. It runs
`uv sync --no-install-workspace` followed by the lightweight provider/core
doctor:

```bash
uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk
```

The setup wrapper writes a venv `.pth` file pointing at the three package
`src` directories after no-workspace sync. This keeps source-checkout imports
working without reinstalling workspace packages or relying on caller
`PYTHONPATH`.

Use the package-native actions when a thread is scoped to one package lane:

- `Provider Native` runs the provider-only native profile and requires provider
  SDK plus provider `_core`.
- `Equilibrium Native` runs the equilibrium native profile and requires only
  provider prerequisites plus `epcsaft_equilibrium._native_core`.
- `Regression Native` runs the regression native profile and requires only
  provider prerequisites plus `epcsaft_regression._native_core`.
- `Full Native` runs the transition source-checkout native profile and requires
  both extension-owned native modules.

Use `Doctor Full Native` after `Build Native Extension` or full setup when the
equilibrium and regression extension-native modules are expected to import.

Fresh Codex worktree setup builds or reuses the default local Ceres package
with `uv run --no-sync python scripts/dev/build_system_ceres.py --parallel 2`
after `uv sync --no-install-workspace` and passes that package to the native
build via `build_epcsaft.py --use-system-ceres --ceres-dir <CeresConfig-dir>`.
Do not set `EPCSAFT_PEP517_CERES_DIR` or `EPCSAFT_PEP517_BUILD_DIR` for normal
source-checkout setup; those variables are only for a custom Ceres package or a
different checkout.

Native Ipopt discovery is system-dependency work. Use
`EPCSAFT_IPOPT_ROOT=<Ipopt-root>` or
`EPCSAFT_PEP517_IPOPT_ROOT=<Ipopt-root>` when the local default is not present.
Use `build_epcsaft.py --ipopt-dir <IpoptConfig-dir>` manually when only an
`IpoptConfig.cmake` directory is available.

The action list should stay lean and limited to the normal project workflow:

- `Sync Environment`
- `Provider Smoke`
- `Provider Native`
- `Equilibrium Native`
- `Regression Native`
- `Full Native`
- `Doctor`
- `Doctor Full Native`
- `Build Native Extension`
- `Validate Quick`
- `Validate Confidence`
- `Build Docs`
- `Build Distribution`

Advanced commands such as fast native rebuilds, clean repair, profiling,
equation registry maintenance, and targeted tests stay in
`docs/pages/development_workflows.rst` and should be run manually when needed.

Maintenance rules:

- Keep `scripts/dev/bootstrap.py` as the source of truth whenever script names,
  test paths, package layout, or native dependency policy expectations change.
- Keep this file and `environment.toml` current whenever visible Codex app
  actions change.
- Remove stale actions immediately when a workflow is deleted.
- Do not re-add plot gallery, gallery server, manifest, index, `--plots`, or
  obsolete test-slice actions to this package.
- Keep `docs/agents/agent-happy-path.md` aligned with setup, Doctor,
  validation, and transferred-artifact cleanup commands.
- Before handoff after workflow edits, run `uv sync --no-install-workspace` and
  `uv run --no-sync python scripts/dev/bootstrap.py --dry-run`.
