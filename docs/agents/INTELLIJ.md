# IntelliJ MCP Workflow

This is the canonical repo-local agent policy for using IntelliJ IDEA, the
JetBrains bundled MCP server, the `intellij-index` MCP server, and debugger MCP
tools in `ePC-SAFT`.

The policy applies when IntelliJ is open for:

- semantic navigation, diagnostics, or refactors;
- durable build, test, docs, validation, package, analysis, or maintenance runs;
- runtime debugging with breakpoints, stack frames, values, or expression
  evaluation;
- Services dashboard maintenance.

It does not replace `docs/protocols/build_package_dependency_protocol.rst`.
That protocol remains the source of truth for build, package, CMake,
dependency, and CI policy.
For direct CMake preset execution, also read root `CMAKE.md`; it is the
entrypoint protocol for the wrapper-backed Services workflow.

## Project Targeting

- Load and follow the `jetbrains-bridge` plugin, or the compatibility
  `jetbrains` skill, before IntelliJ-backed work.
- Ask before launching or focusing IntelliJ for this repo.
- Use `C:\Users\Tanner\Documents\Workspaces\Engineering\ePC-SAFT` as the MCP
  `projectPath` / `project_path` for repo-specific work.
- Open this repo as its own IntelliJ project for repo-specific commands,
  semantic navigation, diagnostics, run configurations, and debugging.
- Keep the standalone IntelliJ project/folder identity as `ePC-SAFT`, but keep
  the root provider Python module named `epcsaft`. The extension modules are
  `epcsaft-equilibrium` and `epcsaft-regression`, and both depend on
  `epcsaft`.
- Use the Engineering workspace root only for workspace-level stewardship such
  as module wiring, SDK consistency, or IDE container repair.
- Do not route repo-specific commands through a nested repo path inside the
  Engineering workspace root.

## Tool Priority

Hard rule: use IntelliJ MCP first by default for repo work when the IDE is
ready and the relevant tool is exposed.

Use `intellij-index` first for semantic work:

- indexed project reads and lookup: `ide_read_file`, `ide_search_text`,
  `ide_find_file`, `ide_find_class`, `ide_find_symbol`,
  `ide_file_structure`;
- semantic navigation: `ide_find_definition`, `ide_find_references`,
  `ide_find_implementations`, `ide_find_super_methods`,
  `ide_call_hierarchy`, `ide_type_hierarchy`;
- diagnostics and editor state: `ide_diagnostics`, `ide_get_active_file`,
  `ide_open_file`, `ide_sync_files`;
- safe edits/refactors: `ide_optimize_imports`, `ide_reformat_code`,
  `ide_refactor_rename`, `ide_move_file`, `ide_refactor_safe_delete`;
- `ide_build_project` only when the IntelliJ project has a meaningful IDE build
  target.

Use `jetbrains-bundled` first for durable execution:

- `get_run_configurations`;
- `execute_run_configuration`;
- `open_file_in_editor`;
- project/module/dependency inspection;
- file problems, lint/build/reformat actions;
- debugger tools;
- notebook tools when relevant.

If a relevant MCP tool is not currently visible, call `tool_search` for it
before falling back.

Try the relevant indexed action at least twice when the first result is stale,
empty, ambiguous, or an indexing-ready retry is plausible. Do not spin
indefinitely.

## Durable Runs

Hard rule: durable scripts, tests, validation commands, build commands,
docs/report commands, analysis commands, package commands, and maintenance
commands must run through shared IntelliJ run configurations when a matching
configuration exists or should exist.

Default sequence:

1. Call `get_run_configurations` at the open repo project root.
2. Execute the named configuration with `execute_run_configuration`.
3. If the durable command is missing, update
   `scripts/dev/configure_jetbrains_project.py` and `.run/*.run.xml`.
4. Run the normalizer dry-run and apply configurations.
5. Execute the new named run configuration through MCP.

Before starting or handing off IntelliJ-backed work, run `Check IntelliJ
Contract` when Services/dashboard drift would affect the task. It is the
non-mutating gate for the repo-owned `.idea` and `.run` contract and exits nonzero
when `Configure IntelliJ Runs (Apply)` would change anything.

Do not run an equivalent ad hoc `uv run python ...` or PowerShell command for a
durable repo workflow unless the IntelliJ run-configuration path is unavailable
after concrete attempts or the command is still being bootstrapped into
Services.

For direct CMake preset operations, the only durable Services entries are
`CMake Configure dev-native`, `CMake Build _core dev-native`, and
`CMake Build dev-native`. They must call `scripts/dev/cmake_preset.ps1`.
Do not create raw `cmake --preset` or `cmake --build` Services entries; the
wrapper owns Visual Studio environment loading, repo-local `.venv` CMake/Ninja
selection, and `build/dev` lock checks.
Do not use IDE-generated `CMake Application` targets as the repo standard; they
may exist in IntelliJ's run configuration list, but the Services dashboard
standard is the wrapper-backed PowerShell entries.

Use shell only for:

- quick one-off probes that should not become Services entries;
- raw config reads after MCP lookup;
- generated file inspection;
- Git operations;
- bootstrapping or fixing the run dashboard before IntelliJ can see it.

## Services Dashboard

This repo owns its shared IntelliJ dashboard through
`scripts/dev/configure_jetbrains_project.py` and `.run/*.run.xml`.

When adding, editing, deleting, or grouping durable run configurations:

1. edit the manifest/normalizer;
2. run `Configure IntelliJ Runs (Dry Run)`;
3. run `Configure IntelliJ Runs (Apply)`;
4. run `Check IntelliJ Contract`;
5. verify XML/idempotence;
6. execute the intended named configuration through MCP.

Shared `.run` configs use the repo-name Services folder `ePC-SAFT`. Keep the
workflow category in the configuration name, not in `folderName`, so the
multi-repo Workspace Services view has one top-level node per repo.

Use native `uv run` run configurations (`UvRunConfigurationType`) for durable
Python scripts, validation, analysis, docs registry sync, and pytest wrapper
workflows. Use native PowerShell run configurations (`PowerShellRunType`) for
repo setup, CMake wrappers, native-build wrappers, cleanup, equation-PDF builds,
and other `.ps1` maintenance entry points. Do not add native Pytest
configuration types to Services by default, because generated gutter configs
clutter the dashboard.

## Index MCP

Treat `intellij-index` as an IDE-backed index over open IntelliJ projects, not
as a generic filesystem indexer.

- Call `ide_index_status` at most once near the start of semantic work.
- Always pass `project_path`.
- After external file edits, call `ide_sync_files` before IDE diagnostics,
  references, or implementation searches on changed files.
- For non-trivial code work, public API or native wrapper changes, architecture
  questions, bug diagnosis, deletion/rename/move work, or shared-behavior
  review, use every relevant index action family before finalizing.
- Prefer shell and `rg` for plain text search, generated files, repo-wide
  mechanical checks, and files outside the IntelliJ project.

## Debugger MCP

Use the `ij-debugger` skill when runtime evidence is needed or when the user
explicitly asks for debugger work.

The debugger MCP server is `intellij-debugger`. Its current tool names include
`list_run_configurations`, `start_debug_session`, `set_breakpoint`,
`wait_for_pause`, `get_debug_session_status`, `get_stack_trace`,
`get_variables`, `evaluate_expression`, stepping tools, and
`stop_debug_session`.

Debugger MCP is worth using for:

- confirming whether a code location is reached;
- collecting actual runtime values at branch points;
- tracing long control-flow paths without reading many files manually;
- proving wrapper-to-native or test-to-runtime value provenance;
- inspecting stack frames before making runtime behavior changes.

Required first sequence:

1. `get_debug_session_status`;
2. `list_breakpoints`;
3. choose the narrowest run configuration or run point via
   `list_run_configurations` or `get_run_configurations`;
4. set at most a small number of agent-owned breakpoints with
   `set_breakpoint`;
5. start with `start_debug_session`;
6. wait with `wait_for_pause`;
7. collect stack and values with `get_stack_trace` and
   `get_variables` or `evaluate_expression`;
8. remove agent-owned breakpoints and stop or resume to completion.

Leave user-owned breakpoints alone unless they block the investigation. If user
breakpoints must be disabled, record their prior enabled state and restore it
once at the end.

Do not use debugger MCP for routine test execution when no runtime question is
being answered. Use shared run configurations for ordinary validation.

## Terminal MCP

The IntelliJ terminal MCP is usable on this machine after setting the terminal
shell path to unquoted PowerShell 7:

```text
C:\Program Files\PowerShell\7\pwsh.exe
```

Use terminal MCP for:

- checking the IDE terminal environment;
- user-visible one-off probes in the IntelliJ terminal context;
- confirming PowerShell, PATH, or working-directory behavior seen by IntelliJ.

Do not make terminal MCP the default for Git, staging, committing, pushing,
broad file inspection, or durable repo workflow execution. It is slower and
less deterministic than the normal repo-root shell for those cases.

## MCP Server Configuration

IntelliJ's MCP Server settings page may show Codex as "Not configured" even
when Codex is correctly configured and actively using the server. Treat
successful tool calls and `codex mcp list` as the source of truth.

The bundled JetBrains MCP server may be configured as either localhost or
loopback:

```text
http://localhost:64345/stream
http://127.0.0.1:64345/stream
```

Both can reach the same server; the UI may compare strings literally.

## Git

The JetBrains MCP server exposes repository discovery, not a full local Git
Tool Window API for staging, committing, branch cleanup, merging, rebasing, or
pushing.

Local Git operations stay in the normal repo-root shell. Use IntelliJ VCS
discovery only to confirm the project VCS root when that is the question.

## Completion Reporting

When IntelliJ-backed tooling was relevant, final responses should list the IDE
tools used, or state why they were skipped.

If debugger MCP was used, include the paused location, stack/value evidence,
and cleanup status.
