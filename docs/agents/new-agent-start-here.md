# New Agent Start Here

This is the current entry point for a new ePC-SAFT repo thread. GitHub Issues
and the `ePC-SAFT Roadmap` Project are authoritative for live tracker state;
`docs/milestones/PROJECT_CONTEXT.md` is the package-context and completion
standard.

## Fresh Checkout

Run the one-command bootstrap first:

```powershell
uv run python scripts/dev/bootstrap.py
```

It runs:

```powershell
uv sync --no-install-project
uv run python scripts/dev/build_epcsaft.py
uv run python scripts/dev/doctor.py
```

Bootstrap and doctor print the active Ipopt SDK root, where it came from, and
the exact `$env:EPCSAFT_IPOPT_ROOT = "..."` command to change it. Prefer an
explicit `EPCSAFT_IPOPT_ROOT` for reproducible Ipopt work; default Windows
probes are `%LOCALAPPDATA%\ePC-SAFT\deps\ipopt-msvc`,
`%USERPROFILE%\.epcsaft\deps\ipopt-msvc`, and legacy
`%USERPROFILE%\Documents\deps\ipopt-msvc`.

The repo-owned Codex app setup contract lives in `.codex/environments/`:
`environment.toml` exposes the visible Codex actions, `setup.ps1` dispatches to
`scripts/dev/bootstrap.py`, and `.codex/environments/README.md` explains the
fresh-worktree contract. Shared agent routing lives in tracked `AGENTS.md`;
IntelliJ policy lives in `docs/agents/INTELLIJ.md`; machine-local user settings
stay outside tracked package docs.

When bootstrap succeeds, run the printed next command:

```powershell
uv run python scripts/dev/validate_project.py quick
```

## Diagnostics

Use doctor when package/native state is unclear:

```powershell
uv run python scripts/dev/doctor.py --require-provider-sdk --require-extension-native
```

For production equilibrium proof, also require Ipopt:

```powershell
uv run python scripts/dev/doctor.py --require-ipopt --require-provider-sdk --require-extension-native
```

## Package Proof

Provider package proof:

```powershell
uv run python scripts/dev/build_dist.py --parallel 1
```

Extension package proof with a real local Ipopt SDK:

```powershell
uv run python scripts/dev/build_system_ceres.py --parallel 4
uv run python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"
uv run python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1 --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"
uv run python scripts/dev/check_release_installs.py --dist-dir dist
```

`build_extension_dists.py` auto-detects the repo-local reusable Ceres package
for regression builds when it exists, or accepts `--ceres-dir` /
`EPCSAFT_PEP517_CERES_DIR`. The Ceres source tree is build-time dependency
work. The equilibrium wheel runtime payload is the audited dependency closure
for `epcsaft_equilibrium._native_core` and Ipopt, not every DLL in the Ipopt
SDK `bin` folder.

Missing Ipopt is not a production equilibrium package proof. Fix the SDK path
or run a non-equilibrium lane instead.

## Tracker

For implementation work, use the matching GitHub issue and the milestone plan
under `docs/milestones/M*/plans/`. Do not resurrect superseded roadmap files or
old source-layout commands. Current package work stays in this monorepo under
`packages/epcsaft`, `packages/epcsaft-equilibrium`, and
`packages/epcsaft-regression`; retired sibling extension checkouts are not
authoritative inputs.
