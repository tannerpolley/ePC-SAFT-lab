# New Agent Start Here

This is the entry point for work in the preserved ePC-SAFT lab.
`docs/superpowers/PROJECT_CONTEXT.md` remains the monorepo package-context and
completion-standard record while the clean repositories are populated. The
lab does not own new issue intake, roadmap state, or production authority.

## Fresh Checkout

For a compact migrated-Linux flow, read `docs/agents/agent-happy-path.md`.

Check host prerequisites first:

```bash
scripts/dev/check_linux_prereqs.sh --check
```

Run the explicit fresh-worktree bootstrap first:

```bash
uv sync --no-install-workspace
uv run --no-sync python scripts/dev/bootstrap.py
```

It runs:

```bash
uv sync --no-install-workspace
uv run --no-sync python scripts/dev/build_epcsaft.py
uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-extension-native
```

Bootstrap and doctor print the active Ipopt root, where it came from, and the
exact `export EPCSAFT_IPOPT_ROOT="..."` command to change it. Prefer an
explicit `EPCSAFT_IPOPT_ROOT` for reproducible Ipopt work; Linux defaults probe
`~/.local/opt/ipopt`, `/usr/local`, `/usr`, and `/opt/ipopt`.

The repo-owned Codex app setup contract lives in `.codex/environments/`:
`environment.toml` exposes the visible Codex actions, `setup.sh` dispatches to
`scripts/dev/bootstrap.py`, and `.codex/environments/README.md` explains the
fresh-worktree contract. Shared agent routing lives in tracked `AGENTS.md`;
machine-local user settings stay outside tracked package docs.

If the checkout was copied from Windows, inspect ignored transferred artifacts
before running builds:

```bash
scripts/dev/clean_transferred_artifacts.sh --dry-run
```

When bootstrap succeeds, run the printed next command:

```bash
uv run --no-sync python scripts/dev/validate_project.py quick
```

## Diagnostics

Use lightweight Doctor when package/provider SDK state is unclear in a fresh
worktree:

```bash
uv sync --no-install-workspace
uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk
```

Use package-native Doctor checks for lane-specific worktrees:

```bash
uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-provider-native
uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-equilibrium-native
uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-regression-native
uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-extension-native
```

The Codex app actions expose the same lanes as `Provider Native`,
`Equilibrium Native`, `Regression Native`, and `Full Native`. Use `Full Native`
for cross-package source-checkout proof. For production equilibrium proof, also
require Ipopt:

```bash
uv run python scripts/dev/doctor.py --require-ipopt --require-provider-sdk --require-extension-native
```

## Package Proof

Provider package proof:

```bash
uv run python scripts/dev/build_dist.py --parallel 1
```

Extension package proof with a real local Ipopt SDK:

```bash
uv run python scripts/dev/build_system_ceres.py --parallel 2
uv run python scripts/dev/build_extension_dists.py --mode monorepo --parallel 1
uv run python scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1
uv run python scripts/dev/check_release_installs.py --dist-dir dist
```

The extension helper uses the shared Linux Ipopt discovery policy. To pin a
specific audited install, run `export EPCSAFT_IPOPT_ROOT=/path/to/ipopt` before
the extension build commands.

`build_extension_dists.py` auto-detects the repo-local reusable Ceres package
for regression builds when it exists, or accepts `--ceres-dir` /
`EPCSAFT_PEP517_CERES_DIR`. The Ceres source tree is build-time dependency
work. The equilibrium wheel runtime payload is the audited dependency closure
for `epcsaft_equilibrium._native_core` and Ipopt, not broad build-time
dependency trees.

Missing Ipopt is not a production equilibrium package proof. Fix the SDK path
or run a non-equilibrium lane instead.

## Archive boundary

Use retained specs and plans as provenance, not as a live intake queue. Do not
resurrect retired roadmap files, issue forms, tracker automation, or old
source-layout commands. A future production change must be admitted by the
clean repository that owns its vertical slice; this lab remains recoverable
historical evidence.
