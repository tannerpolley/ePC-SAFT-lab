# ePC-SAFT CMake Protocol

This is the source of truth for direct CMake work in this repo.

The normal source checkout workflow remains:

```powershell
uv sync --no-install-project
uv run python scripts/dev/build_epcsaft.py
uv run python scripts/dev/doctor.py
```

Direct CMake preset work must use the repo wrapper, either through JetBrains
Services or the same wrapper from PowerShell. Do not run raw `cmake --preset`
or `cmake --build` commands for this repo.

## Standard Entry Points

Use these shared JetBrains Services entries for direct preset work:

| Task | Services entry |
| --- | --- |
| Configure `build/dev` | `CMake Configure dev-native` |
| Build only `_core` | `CMake Build _core dev-native` |
| Build all default CMake targets | `CMake Build dev-native` |

These entries are Shell Script run configurations. They are not the
IDE-generated `CMake Application` targets. `CMake Application` targets may
appear in IntelliJ's run configuration list, but they are not the repo standard
and should not be added to Services as the normal CMake workflow.

The terminal form of the same standard is:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/dev/cmake_preset.ps1 -Action Configure -Preset dev-native
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/dev/cmake_preset.ps1 -Action Build -Preset dev-native -Target _core -Parallel 10
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/dev/cmake_preset.ps1 -Action Build -Preset dev-native -Parallel 10
```

Do not create alternate wrapper scripts, duplicate `.run` entries, raw CMake
Services entries, or IDE-only CMake target conventions.

## Wrapper Contract

`scripts/dev/cmake_preset.ps1` owns the direct preset environment:

- loads Visual Studio through `VsDevCmd.bat`;
- uses `.venv\Scripts\cmake.exe`;
- uses `.venv\Scripts\ninja.exe`;
- pins `CMAKE_MAKE_PROGRAM` for `dev-native`;
- refuses to run while `build/dev/.ninja_lock` exists;
- reconfigures before a build when the existing cache does not point at the
  repo-local Ninja executable.

This keeps Services, terminal use, and future agents on the same CMake path.

## Toolchain Contract

The ePC-SAFT direct CMake standard is:

- preset: `dev-native`;
- build tree: `build/dev`;
- generator: Ninja;
- compiler family: MSVC from the Visual Studio developer environment;
- CMake executable: `.venv\Scripts\cmake.exe`;
- Ninja executable: `.venv\Scripts\ninja.exe`;
- native extension target: `_core`.

Strawberry may remain installed for unrelated tooling, but it is not the
ePC-SAFT CMake standard. Do not select Strawberry MinGW for this repo, and do
not rely on Strawberry `cmake.exe`, `ninja.exe`, `gcc.exe`, or `g++.exe` for
`build/dev`.

## Coordination Rules

- Prefer one `_core` builder at a time.
- Run `Build Status` before direct CMake work when another agent, test run, IDE
  run configuration, or Python REPL may be active.
- Do not run clean or repair actions while tests, Python REPLs, IDE runs, or
  other agents may import `epcsaft._core`.
- Do not delete `build/dev/.ninja_lock` by hand. Stop the owning repo build
  process, then rerun the wrapper.
- Use `Doctor` after build or configuration repair.
- Use `Test Workflow Guards` after changing CMake workflow docs, wrappers,
  presets, build helpers, run manifests, or `.run` files.

## Drift Checks

Before handing off a CMake workflow change, verify:

```powershell
uv run python scripts/dev/configure_jetbrains_project.py --dry-run
uv run python run_pytest.py tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/build/test_build_epcsaft.py tests/workflows/build/test_build_epcsaft_script.py tests/workflows/build/test_build_system_ceres.py -q
```

When IntelliJ is ready, run the equivalent shared Services entries:

- `Check IntelliJ Contract`;
- `Configure IntelliJ Runs (Dry Run)`;
- `Test Workflow Guards`;
- `Doctor`;
- the specific `CMake ... dev-native` entry that changed.

## Decision Log

2026-05-23: Direct CMake work was standardized on wrapper-backed Shell Script
Services entries. Strawberry MinGW was kept out of the ePC-SAFT CMake standard.
IDE-generated `CMake Application` targets are allowed to exist as IDE metadata,
but they are not the durable repo workflow.
