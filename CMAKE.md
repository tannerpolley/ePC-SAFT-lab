# ePC-SAFT CMake Protocol

This is the source of truth for direct CMake work in this repo. The supported
local platform is Debian-style Linux with Bash, uv, CMake, and Ninja.

The normal source checkout workflow is:

```bash
uv sync --no-install-workspace
uv run --no-sync python scripts/dev/build_epcsaft.py
uv run --no-sync python scripts/dev/doctor.py
```

Direct CMake preset work must use the repo wrapper from a Bash terminal. Do not run raw `cmake --preset` or `cmake --build` commands for this repo.

## Standard Entry Points

```bash
scripts/dev/cmake_preset.sh --action configure --preset dev-native
scripts/dev/cmake_preset.sh --action build --preset dev-native --target _core --parallel 10
scripts/dev/cmake_preset.sh --action build --preset dev-native --parallel 10
```

## Wrapper Contract

`scripts/dev/cmake_preset.sh` owns the direct preset environment:

- uses `.venv/bin/python -m cmake`;
- uses `.venv/bin/ninja`;
- pins `CMAKE_MAKE_PROGRAM` for `dev-native`;
- refuses to run while `build/dev/.ninja_lock` exists;
- reconfigures before a build when the existing cache does not point at the
  repo-local Ninja executable.

This keeps terminal use and future agents on the same CMake path.

## Toolchain Contract

The ePC-SAFT direct CMake standard is:

- preset: `dev-native`;
- build tree: `build/dev`;
- generator: Ninja;
- compiler family: the current Linux C++ compiler visible to the shell;
- CMake executable: `.venv/bin/python -m cmake`;
- Ninja executable: `.venv/bin/ninja`;
- native extension target: `_core`.

## Coordination Rules

- Prefer one `_core` builder at a time.
- Run `uv run --no-sync python scripts/dev/build_epcsaft.py --status` before
  direct CMake work when another agent, test run, or Python REPL may be active.
- Do not run clean or repair actions while tests, Python REPLs, or other agents
  may import `epcsaft._core`.
- Do not delete `build/dev/.ninja_lock` by hand. Stop the owning repo build
  process, then rerun the wrapper.
- Use `uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk`
  for provider/core health and
  `uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-extension-native`
  after build or configuration repair.
- Run the focused workflow guard tests after changing CMake workflow docs,
  wrappers, presets, or build helpers.

## Drift Checks

Before handing off a CMake workflow change, verify:

```bash
uv run --no-sync python run_pytest.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/build/test_build_epcsaft.py tests/workflows/build/test_build_epcsaft_script.py tests/workflows/build/test_build_system_ceres.py -q
```

## Decision Log

2026-05-23: Direct CMake work was standardized on a repo wrapper so direct
preset work is shared across local terminal workflows.

2026-07-08: The local workflow was migrated to Debian-style Linux Bash wrappers,
`.venv/bin` tools, and Ninja.
