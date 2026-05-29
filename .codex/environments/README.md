# ePC-SAFT Codex Environment

This folder intentionally has one Codex app environment: `environment.toml`.
The files are tracked so Codex app worktrees receive the current bootstrap
contract from Git.

The setup path is:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .codex/environments/setup.ps1
```

The PowerShell wrapper is intentionally thin. The changing project/package setup
lives in tracked Python code:

```powershell
uv run python scripts/dev/bootstrap.py
```

Bootstrap runs the current worktree setup sequence:

```powershell
uv sync --no-install-project
uv run python scripts/dev/configure_jetbrains_project.py --apply
uv run python scripts/dev/configure_jetbrains_project.py --check
uv run python scripts/dev/build_system_ceres.py --parallel 4
uv run python scripts/dev/build_epcsaft.py --use-system-ceres --ceres-dir <CeresConfig-dir>
uv run python scripts/dev/doctor.py --require-provider-sdk --require-extension-native
```

This keeps new Codex app worktrees aligned with the current package split and
the repo-owned IntelliJ Services dashboard. The IntelliJ MCP still attaches to
the IntelliJ project that is actually open, so open the new worktree path as its
own IntelliJ project before using `intellij-index`, `jetbrains-bundled`, or the
debugger MCP against that worktree.

The native build action intentionally uses the current bootstrap build step:
Ceres, CppAD, and native Ipopt are enabled when available. The Python bootstrap
resolves ``EPCSAFT_IPOPT_ROOT`` first, then the local Windows SDK defaults
defined by the package build backend. It also adds the Ipopt ``bin`` directory
to ``PATH`` and ``EPCSAFT_RUNTIME_DLL_DIRS`` when a default SDK is available.
Use ``uv run python scripts/dev/validate_project.py ceres-cppad`` when the task
needs the focused Ceres regression/backend slice.

Fresh Codex worktree setup builds or reuses the default local Ceres package
with ``uv run python scripts/dev/build_system_ceres.py --parallel 4`` and passes
that package to the native build via ``build_epcsaft.py --use-system-ceres
--ceres-dir <CeresConfig-dir>``. The bootstrap uses the current backend policy
to reject a default Ceres package that exports MinGW ``libceres.a`` for an MSVC
worktree. Do not set ``EPCSAFT_PEP517_CERES_DIR`` or
``EPCSAFT_PEP517_BUILD_DIR`` for normal source-checkout setup; those variables
are only for a custom Ceres package or a different checkout.

Native Ipopt discovery outside this Windows setup remains explicit
system-dependency work. Use ``EPCSAFT_IPOPT_ROOT=<Ipopt-root>`` or
``EPCSAFT_PEP517_IPOPT_ROOT=<Ipopt-root>`` when the local default is not
present. Use ``build_epcsaft.py --ipopt-dir <IpoptConfig-dir>`` manually when
only an ``IpoptConfig.cmake`` directory is available.
Existing ``build/dev`` trees configured with MinGW/Strawberry cannot be switched
in place to the MSVC Ipopt toolchain; use a fresh Codex worktree or run the
coordinated clean build repair before enabling this setup on an old checkout.

The action list should stay lean and limited to the normal project workflow:

- `Sync Environment`
- `Doctor`
- `Build Native Extension`
- `Check IntelliJ Contract`
- `Validate Quick`
- `Validate Confidence`
- `Build Docs`
- `Build Distribution`

Advanced commands such as fast native rebuilds, clean repair, profiling, equation registry maintenance, and targeted tests stay in `docs/pages/development_workflows.rst` and should be run manually when needed.

Maintenance rules:

- Keep `scripts/dev/bootstrap.py` as the source of truth whenever script names,
  test paths, package layout, native dependency policy, or IntelliJ metadata
  expectations change.
- Keep this file and `environment.toml` current whenever visible Codex app
  actions change.
- Remove stale actions immediately when a workflow is deleted.
- Do not re-add plot gallery, gallery server, manifest, index, `--plots`, or obsolete test-slice actions to this package.
- Before handoff after workflow edits, run
  ``uv run python scripts/dev/bootstrap.py --dry-run`` and
  ``uv run python scripts/dev/configure_jetbrains_project.py --check``.
