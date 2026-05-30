from __future__ import annotations

from pathlib import Path
import runpy
import xml.etree.ElementTree as ET

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[3]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _toml(path: str) -> dict:
    return tomllib.loads(_read(path))


def _run_config_options(config: ET.Element) -> dict[str, str]:
    return {
        option.attrib["name"]: option.attrib.get("value", "")
        for option in config.findall("option")
        if "name" in option.attrib
    }


def _module_script_path(relative_path: str) -> str:
    return "$MODULE_DIR$/" + relative_path.replace("\\", "/").strip("/")


def test_bootstrap_scripts_use_normal_build_and_fast_suite() -> None:
    for path in ("scripts/dev/bootstrap_uv.ps1", "scripts/dev/bootstrap_uv.sh"):
        content = _read(path)

        assert "python pin 3.13" in content or '"python", "pin", "3.13"' in content
        assert "sync --no-install-project" in content or '"sync", "--no-install-project"' in content
        assert "scripts/dev/build_epcsaft.py --clean" not in content
        assert "scripts\\dev\\build_epcsaft.py --clean" not in content
        assert (
            "scripts\\dev\\validate_project.py quick" in content
            or "scripts/dev/validate_project.py quick" in content
            or '"scripts\\dev\\validate_project.py", "quick"' in content
        )
        assert "run_pytest.py tests/test_runtime.py -q" not in content
        assert "run_pytest.py tests\\test_runtime.py -q" not in content


def test_python_bootstrap_entrypoint_orchestrates_current_setup_sequence() -> None:
    bootstrap = _read("scripts/dev/bootstrap.py")
    development_workflows = _read("docs/pages/development_workflows.rst")
    new_agent_start = _read("docs/agents/new-agent-start-here.md")

    for token in (
        "uv sync --no-install-project",
        "uv run python scripts/dev/build_epcsaft.py",
        "uv run python scripts/dev/doctor.py",
        "uv run python scripts/dev/validate_project.py quick",
    ):
        assert token in bootstrap.replace('", "', " ")
        assert token in development_workflows
        assert token in new_agent_start
    assert "--dry-run" in bootstrap
    assert "bootstrap_state: current" in bootstrap
    assert "next_command:" in bootstrap
    assert "ipopt_sdk_root_source" in bootstrap
    assert "ipopt_change_command" in bootstrap


def test_clean_scripts_announce_repair_only_scope() -> None:
    for path in ("scripts/dev/clean_build.ps1", "scripts/dev/clean_build.sh"):
        content = _read(path)

        assert "REPAIR-ONLY" in content
        assert "build/cache/native artifacts" in content


def test_docs_make_confidence_suite_the_default_runtime_check() -> None:
    readme = _read("README.md")
    getting_started = _read("docs/pages/getting_started.rst")
    overview = _read("docs/pages/README.rst")
    release_installation = _read("docs/pages/release_installation.rst")
    release_note = _read("docs/releases/v0.2.0.md")
    docs_index = _read("docs/pages/index.rst")
    development_workflows = _read("docs/pages/development_workflows.rst")
    cmake_protocol = _read("CMAKE.md")

    assert "README intentionally stays focused on package users" in readme
    assert "uv run python scripts\\validate_project.py quick" not in readme
    assert "uv run python run_pytest.py --confidence -q" not in readme
    assert "The `v0.2.0` GitHub release provides a Windows CPython 3.13 wheel" in readme
    assert "If PyPI returns 404 for `epcsaft`, use the GitHub release wheel above." in readme
    assert "python -m pip install epcsaft" in readme
    assert "python -m pip install -e packages/epcsaft" in readme
    assert "README intentionally stays focused on package users" in readme
    assert "Editable source install" in release_installation
    assert "python -m pip install -e packages/epcsaft" in release_installation
    assert "Source and editable installs build a native C++ extension" in getting_started
    assert "default source-checkout validation sequence" not in getting_started
    assert "``run_pytest.py -q`` is the default fast contract suite" not in getting_started
    assert "Current package version: ``0.2.0``" in overview
    assert "If PyPI returns 404 for ``epcsaft``, use the GitHub release wheel above." in overview
    assert "The ``v0.2.0`` tag supports source installs" in overview
    assert "python -m pip install -e packages/epcsaft" in overview
    assert "For the current release, install the Windows CPython 3.13 wheel from GitHub" in getting_started
    assert "After the package is published on PyPI" in getting_started
    assert "Current package version: ``0.2.0``" in release_installation
    assert "The ``v0.2.0`` GitHub release provides a Windows CPython 3.13 wheel" in release_installation
    assert "Public root exports" in release_note
    assert "neutral bubble/dew routes, neutral TP flash, and neutral nonassociating LLE" in release_note
    assert "Electrolyte LLE, reactive speciation, reactive LLE, reactive electrolyte LLE, and associating LLE are declared not exposed" in release_note
    assert "PyPI publishing remains a manual Trusted Publishing action" in release_note
    assert "production-exposed families are neutral bubble/dew routes, neutral TP flash" in overview
    assert "and neutral nonassociating LLE" in overview
    assert "uv run python run_pytest.py --confidence -q" not in overview
    assert "run_pytest.py tests/test_runtime.py -q" not in overview
    assert "release_installation" in docs_index
    assert "development_workflows" in docs_index
    assert "native_debugging" in docs_index
    assert "publishing" in docs_index
    assert "native/equation debugging guide" not in getting_started
    assert "Start every fresh source checkout with this sequence" in development_workflows
    assert "uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10" in development_workflows
    assert "Root ``CMAKE.md`` is the source of truth for direct CMake preset operations" in development_workflows
    assert "Direct CMake preset operations must use ``scripts/dev/cmake_preset.ps1``" in development_workflows
    assert "Do not call raw ``cmake --preset`` or ``cmake --build``" in development_workflows
    assert "Strawberry" in development_workflows
    for token in (
        "Direct CMake preset work must use",
        "scripts/dev/cmake_preset.ps1",
        "CMake Configure dev-native",
        "CMake Build _core dev-native",
        ".venv\\Scripts\\cmake.exe",
        ".venv\\Scripts\\ninja.exe",
        "Strawberry may remain installed for unrelated tooling",
        "Do not run raw `cmake --preset`",
        "IDE-generated `CMake Application` targets",
        "CMAKE_MAKE_PROGRAM",
    ):
        assert token in cmake_protocol
    assert "uv run python run_pytest.py --runtime -q" in development_workflows
    assert "scripts/benchmarks/" + "benchmark_neutral_equilibrium.py" not in development_workflows
    assert "scripts/benchmarks/" + "benchmark_literature_suite.py" not in development_workflows
    assert "The previous local benchmark scripts were removed as obsolete" in development_workflows
    assert "uv run python run_pytest.py --list-slices" in development_workflows
    assert "EPCSAFT_PYTEST_TEMP_ROOT" in development_workflows
    assert "reuse them inside hot loops" in development_workflows
    assert "Do not route performance claims through pytest" in development_workflows
    assert "uv run python scripts/dev/build_dist.py" in development_workflows
    assert "Do not use ``--clean`` for routine validation" in development_workflows


def test_build_package_dependency_protocol_is_linked_and_guarded() -> None:
    protocol = _read("docs/protocols/build_package_dependency_protocol.rst")
    docs_index = _read("docs/pages/index.rst")
    full_plan = _read("docs/milestones/PROJECT_CONTEXT.md")
    development_workflows = _read("docs/pages/development_workflows.rst")
    native_debugging = _read("docs/pages/native_debugging.rst")
    workflow = _read(".github/workflows/native-build-profiles.yml")
    package_lanes = _read(".github/workflows/package-build-lanes.yml")

    assert "../protocols/build_package_dependency_protocol" in docs_index
    assert "docs/protocols/build_package_dependency_protocol.rst" in full_plan
    assert ":doc:`../protocols/build_package_dependency_protocol`" in development_workflows
    assert ":doc:`../protocols/build_package_dependency_protocol`" in native_debugging
    assert "Root ``CMAKE.md`` is the direct CMake execution protocol." in protocol

    for token in (
        "Build/Package Dependency Protocol",
        "Ceres, CppAD, and Ipopt should therefore be enabled by default",
        "CppAD is required",
        "Ipopt is required for production equilibrium validation",
        "transition capabilities",
        "current monorepo",
        "reproducible friction",
        "Do not reframe Ceres, CppAD, or Ipopt as greenfield optional dependencies",
        "package-boundary exceptions",
        "Conda or mamba must not be the normal Ipopt CI provisioning path",
        "local proof first",
        "manual-only",
        "Option B is the accepted production Ipopt lane direction",
        "no-Ipopt smoke lane",
        "focused CppAD derivative lane",
        "2026-05-29 - Early package PR gates",
        "Status: Implemented as policy",
    ):
        assert token in protocol

    assert "--enable-cppad" not in workflow
    assert "native no-Ipopt smoke" in workflow
    assert "native CppAD derivative contract" in workflow
    assert "workflow_dispatch || github.event_name == 'schedule'" not in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "schedule:" not in workflow
    assert "--profile full --disable-ipopt" in workflow
    for token in (
        "provider package build",
        "regression package build",
        "equilibrium package build",
        "installed-provider extension builds",
        "scripts/dev/build_dist.py --parallel 1",
        "scripts/dev/build_system_ceres.py --parallel 2",
        "scripts/dev/build_extension_dists.py --mode monorepo --package epcsaft-regression --parallel 1",
        "scripts/dev/build_extension_dists.py --mode monorepo --package epcsaft-equilibrium --parallel 1 --ipopt-root",
        "scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1 --ipopt-root",
        "scripts/dev/check_release_installs.py --dist-dir dist --combination all",
        "requires a real Ipopt SDK root; no no-Ipopt package proof is accepted",
    ):
        assert token in package_lanes
    assert "pull_request:" not in package_lanes
    assert "push:" not in package_lanes
    assert "schedule:" not in package_lanes


def test_repo_local_agent_guidance_uses_current_dev_workflow_and_roster() -> None:
    agents_md = _read("AGENTS.md")
    new_agent_start = _read("docs/agents/new-agent-start-here.md")
    development_workflows = _read("docs/pages/development_workflows.rst")
    cmake_md = _read("CMAKE.md")
    env_toml = _read(".codex/environments/environment.toml")
    env_data = _toml(".codex/environments/environment.toml")
    env_setup = _read(".codex/environments/setup.ps1")
    env_readme = _read(".codex/environments/README.md")
    build_owner = _read(".codex/agents/build_packaging_owner.toml")
    command_runner = _read(".codex/agents/command_runner.toml")

    for token in (
        "docs/milestones/PROJECT_CONTEXT.md",
        "docs/agents/new-agent-start-here.md",
        "docs/pages/development_workflows.rst",
        "docs/protocols/build_package_dependency_protocol.rst",
        "docs/agents/issue-tracker.md",
        "docs/agents/INTELLIJ.md",
        "docs/pages/project_structure.rst",
        "packages/epcsaft-equilibrium",
        "use IntelliJ Bridge/MCP first",
        "ask the user to open or focus IntelliJ",
    ):
        assert token in agents_md

    for stale in (
        "Machine-Local",
        "Do Not Commit",
        "C:\\Users\\Tanner",
        "Best new-agent workflow",
        "Git Sandbox Rules",
        "Sandbox Notes",
        "Preferred native build",
        "uv run python scripts/build_epcsaft.py",
        "uv run python scripts/doctor.py",
        "uv run python scripts/validate_project.py quick",
        "uv run python scripts/validate_project.py confidence",
        "uv run python scripts/validate_project.py docs",
        "uv run python scripts/build_dist.py",
        "Prefer Spark owner agents",
    ):
        assert stale not in agents_md

    for token in (
        "uv run python scripts/dev/bootstrap.py",
        "uv run python scripts/dev/doctor.py --require-provider-sdk --require-extension-native",
        "uv run python scripts/dev/check_release_installs.py --dist-dir dist",
        "docs/milestones/PROJECT_CONTEXT.md",
        "EPCSAFT_PEP517_CERES_DIR",
        "audited dependency closure",
        "The repo-owned Codex app setup contract lives in `.codex/environments/`",
        "Shared agent routing lives in tracked `AGENTS.md`",
        "IntelliJ policy lives in `docs/agents/INTELLIJ.md`",
    ):
        assert token in new_agent_start

    assert "docs/roadmaps" not in new_agent_start

    for token in (
        "uv run python scripts/dev/build_epcsaft.py",
        "uv run python scripts/dev/doctor.py",
        "uv run python scripts/dev/validate_project.py quick",
        "uv run python scripts/dev/validate_project.py confidence",
        "uv run python scripts/dev/validate_project.py docs",
        "uv run python scripts/dev/build_dist.py",
    ):
        assert token in new_agent_start or token in development_workflows

    assert "Direct CMake preset work must use the repo wrapper" in cmake_md
    assert "scripts/dev/cmake_preset.ps1" in cmake_md

    expected_env_actions = [
        "Sync Environment",
        "Doctor",
        "Build Native Extension",
        "Check IntelliJ Contract",
        "Validate Quick",
        "Validate Confidence",
        "Build Docs",
        "Build Distribution",
    ]
    env_actions = env_data["actions"]
    assert [action["name"] for action in env_actions] == expected_env_actions
    for action_name in expected_env_actions:
        assert f"- `{action_name}`" in env_readme
    assert env_actions[0]["command"] == "uv sync --no-install-project"
    assert env_actions[1]["command"].endswith(".codex/environments/setup.ps1 -Step Doctor")
    assert env_actions[2]["command"].endswith(".codex/environments/setup.ps1 -Step Build")
    assert env_actions[3]["command"] == "uv run python scripts/dev/configure_jetbrains_project.py --check"
    assert env_actions[4]["command"] == "uv run python scripts/dev/validate_project.py quick"
    assert env_actions[5]["command"] == "uv run python scripts/dev/validate_project.py confidence"
    assert env_actions[6]["command"] == "uv run python scripts/dev/validate_project.py docs"
    assert env_actions[7]["command"] == "uv run python scripts/dev/build_dist.py"

    assert 'name = "Build Native Extension (Bounded)"' not in env_toml
    assert 'name = "Check IntelliJ Contract"' in env_toml
    assert "pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .codex/environments/setup.ps1 -Step Build" in env_toml
    assert "uv run python scripts/dev/configure_jetbrains_project.py --check" in env_toml
    assert "scripts/dev/bootstrap.py --step $bootstrapStep" in env_setup
    assert "Invoke-ReusableCeresBuild" not in env_setup
    assert "scripts/dev/build_system_ceres.py" in _read("scripts/dev/bootstrap.py")
    assert "--use-system-ceres" in _read("scripts/dev/bootstrap.py")
    assert "--ceres-dir" in _read("scripts/dev/bootstrap.py")
    assert "libceres.a" in _read("packages/epcsaft/build_backend/native_dependency_policy.py")
    assert "Do not set ``EPCSAFT_PEP517_CERES_DIR``" in env_readme
    assert "build_epcsaft.py --use-system-ceres" in env_readme
    assert ".codex/environments/setup.ps1 builds or reuses scripts/dev/build_system_ceres.py output" in build_owner
    assert "scripts/dev/build_dist.py builds the provider-only packages/epcsaft distribution" in command_runner
    assert "plus EPCSAFT_PEP517_CERES_DIR" not in build_owner
    assert "prefer a persistent EPCSAFT_PEP517_BUILD_DIR and prebuilt Ceres via EPCSAFT_PEP517_CERES_DIR" not in command_runner


def test_jetbrains_services_dashboard_run_configs_are_manifest_backed() -> None:
    normalizer = _read("scripts/dev/configure_jetbrains_project.py")
    manifest = _read("scripts/dev/jetbrains_run_manifest.py")
    manifest_data = runpy.run_path(str(REPO_ROOT / "scripts" / "dev" / "jetbrains_run_manifest.py"))
    run_config_specs = tuple(manifest_data["CANONICAL_RUN_CONFIGS"])
    root_pyproject = _toml("pyproject.toml")
    provider_pyproject = _toml("packages/epcsaft/pyproject.toml")
    equilibrium_pyproject = _toml("packages/epcsaft-equilibrium/pyproject.toml")
    regression_pyproject = _toml("packages/epcsaft-regression/pyproject.toml")
    agents_md = _read("AGENTS.md")
    intellij_guidance = _read("docs/agents/INTELLIJ.md")
    combined_guidance = agents_md + "\n" + intellij_guidance

    assert "CMAKE_CONFIG_TYPE = \"CMakeRunConfiguration\"" in normalizer
    assert "RUN_DASHBOARD_CONFIG_TYPES = (PYTHON_CONFIG_TYPE, SHELL_CONFIG_TYPE)" in normalizer
    assert "CANONICAL_PYTHON_MODULES" in normalizer
    assert 'PROJECT_NAME = "ePC-SAFT"' in normalizer
    assert 'PROVIDER_MODULE_NAME = "epcsaft"' in normalizer
    assert 'LEGACY_PROVIDER_MODULE_NAME = PROJECT_NAME' in normalizer
    assert 'MODULE_NAME = "ePC-SAFT"' not in normalizer
    assert 'EQUILIBRIUM_MODULE_NAME = "epcsaft-equilibrium"' in normalizer
    assert 'REGRESSION_MODULE_NAME = "epcsaft-regression"' in normalizer
    assert 'iml_path=IDEA_DIR / f"{PROVIDER_MODULE_NAME}.iml"' in normalizer
    assert 'iml_path=IDEA_DIR / f"{EQUILIBRIUM_MODULE_NAME}.iml"' in normalizer
    assert 'iml_path=IDEA_DIR / f"{REGRESSION_MODULE_NAME}.iml"' in normalizer
    assert "delete legacy provider module" in normalizer
    assert "not deleting non-owned legacy provider module" in normalizer
    assert 'actions.append(f"set module={PROVIDER_MODULE_NAME}")' in normalizer
    assert '"--check"' in normalizer
    assert "def _mode_prefix" in normalizer
    assert "if args.check and (pending_changes or warnings_found)" in normalizer
    assert "clear stale Python source-root detection paths" in normalizer
    assert "set VCS mapping to project root only" in normalizer
    assert "disable Services Run Dashboard for" in normalizer
    assert "PYTEST_CONFIG_TYPE" in normalizer
    assert 'CMAKE_ACTIVE_PROFILE = "dev-native"' in normalizer
    assert 'CMAKE_EXECUTION_TARGET_PREFIX = "CMakeBuildProfile:"' in normalizer
    assert 'STALE_CMAKE_PROFILE_NAMES = frozenset({"ePC-SAFT dev MinGW"})' in normalizer
    assert "remove stale CMake profile" in normalizer
    assert "ExecutionTargetManager" in normalizer
    assert "clear stale CMake execution target" in normalizer
    assert 'action = "enable" if expected_enabled == "true" else "disable"' in normalizer
    assert 'actions.append(f"{action} CMake profile {profile_name}")' in normalizer
    assert 'component", {"name": "RunDashboard"}' in normalizer
    assert "remove temporary generated run configuration" in normalizer
    assert 'RUN_CONFIG_EXECUTOR_PREFIXES = ("Python.", "Shell Script.")' in normalizer
    assert "remove stale executor property" in normalizer
    assert "remove stale run manager item" in normalizer
    assert "remove stale configuration status" in normalizer
    assert "enable Services Run Dashboard for" in normalizer
    assert "delete stale shared run configuration" in normalizer
    assert "CANONICAL_RUN_CONFIGS" in normalizer
    assert "project" not in root_pyproject
    assert provider_pyproject["project"]["name"] == "epcsaft"
    assert equilibrium_pyproject["project"]["name"] == "epcsaft-equilibrium"
    assert regression_pyproject["project"]["name"] == "epcsaft-regression"
    assert set(root_pyproject["tool"]["uv"]["workspace"]["members"]) == {
        "packages/epcsaft",
        "packages/epcsaft-equilibrium",
        "packages/epcsaft-regression",
    }
    assert "Configure IntelliJ Runs (Dry Run)" in manifest
    assert "Check IntelliJ Contract" in manifest
    assert "Sync Workspace Packages" in manifest
    assert "Check Package Imports" in manifest
    assert "Test Equilibrium Confidence" in manifest
    for removed_config in (
        "Association Goal 1+2 Tests",
        "Doctor Script",
        "Build System Ceres",
        "Validate Hydrocarbon Regression",
        "Run Ipopt Exact Hessian Checks",
        "Check Phase Discovery",
        "Curate Paper Validation Parameters",
        "Sync MIAC Variants",
        "Sync LaTeX Mirror",
        "Create Dev Worktree",
    ):
        assert removed_config not in manifest
    assert "docs/agents/INTELLIJ.md" in agents_md
    assert "IntelliJ MCP Workflow" in intellij_guidance
    assert "Hard rule: use IntelliJ MCP first by default for repo work" in combined_guidance
    assert "call `tool_search`" in intellij_guidance
    assert "Try the relevant indexed action at least twice" in intellij_guidance
    assert "durable scripts, tests, validation commands, build commands" in combined_guidance
    assert "Do not run an equivalent ad hoc `uv run python ...` or PowerShell command" in intellij_guidance
    assert "Check IntelliJ Contract" in intellij_guidance
    assert "exits nonzero" in intellij_guidance
    assert "Use shell only for" in combined_guidance
    assert "shared `.run` configs use single-level" in intellij_guidance
    assert "project/folder identity as `ePC-SAFT`" in intellij_guidance
    assert "provider Python module named `epcsaft`" in intellij_guidance
    for folder_name in (
        "Setup & Health",
        "Build & Package",
        "Validation",
        "Tests",
        "Docs & Reports",
        "Analysis & Figures",
        "Maintenance",
    ):
        assert folder_name in intellij_guidance
    assert "use every relevant index action family before finalizing" in intellij_guidance
    assert "Use the `ij-debugger` skill" in intellij_guidance
    assert "debugger MCP server is `intellij-debugger`" in intellij_guidance
    assert "intellij-debugger" in intellij_guidance
    assert "start_debug_session" in intellij_guidance
    assert "set_breakpoint" in intellij_guidance
    assert "wait_for_pause" in intellij_guidance
    assert "get_variables" in intellij_guidance
    assert "evaluate_expression" in intellij_guidance
    assert "xdebug_" not in intellij_guidance
    assert "C:\\Program Files\\PowerShell\\7\\pwsh.exe" in intellij_guidance
    assert "JetBrains MCP server exposes repository discovery" in intellij_guidance
    assert "Local Git operations stay in the normal repo-root shell" in intellij_guidance
    for tool_name in (
        "ide_read_file",
        "ide_search_text",
        "ide_find_file",
        "ide_find_class",
        "ide_find_symbol",
        "ide_file_structure",
        "ide_find_definition",
        "ide_find_references",
        "ide_find_implementations",
        "ide_find_super_methods",
        "ide_call_hierarchy",
        "ide_type_hierarchy",
        "ide_diagnostics",
        "ide_get_active_file",
        "ide_open_file",
        "ide_sync_files",
        "ide_optimize_imports",
        "ide_reformat_code",
        "ide_refactor_rename",
        "ide_move_file",
        "ide_refactor_safe_delete",
        "ide_build_project",
    ):
        assert tool_name in combined_guidance
    assert "Use shared run configurations for ordinary validation" in intellij_guidance
    assert "CMake Configure dev-native" in intellij_guidance
    assert "CMake Build _core dev-native" in intellij_guidance
    assert "For direct CMake preset execution, also read root `CMAKE.md`" in intellij_guidance
    assert "Do not create raw `cmake --preset` or `cmake --build` Services entries" in intellij_guidance
    assert "Do not use IDE-generated `CMake Application` targets as the repo standard" in intellij_guidance
    assert "Doctor Script" not in _read("CMAKE.md")

    modules_xml = ET.parse(REPO_ROOT / ".idea" / "modules.xml")
    module_filepaths = {
        module.attrib["filepath"]
        for module in modules_xml.findall(".//module")
    }
    assert module_filepaths == {
        "$PROJECT_DIR$/.idea/epcsaft.iml",
        "$PROJECT_DIR$/.idea/epcsaft-equilibrium.iml",
        "$PROJECT_DIR$/.idea/epcsaft-regression.iml",
    }
    assert not (REPO_ROOT / ".idea" / "ePC-SAFT.iml").exists()
    assert not any(".CMake" in filepath for filepath in module_filepaths)

    provider_module = ET.parse(REPO_ROOT / ".idea" / "epcsaft.iml").getroot()
    equilibrium_module = ET.parse(REPO_ROOT / ".idea" / "epcsaft-equilibrium.iml").getroot()
    regression_module = ET.parse(REPO_ROOT / ".idea" / "epcsaft-regression.iml").getroot()

    def content_root(module: ET.Element) -> ET.Element:
        content = module.find(".//content")
        assert content is not None
        return content

    def source_roots(module: ET.Element) -> set[tuple[str, str]]:
        return {
            (source.attrib["url"], source.attrib.get("isTestSource", "false"))
            for source in content_root(module).findall("sourceFolder")
        }

    def module_dependencies(module: ET.Element) -> set[str]:
        return {
            entry.attrib["module-name"]
            for entry in module.findall(".//orderEntry[@type='module']")
        }

    for module in (provider_module, equilibrium_module, regression_module):
        assert module.attrib["type"] == "PYTHON_MODULE"
        assert module.find(".//orderEntry[@type='jdk']").attrib["jdkName"] == "uv (ePC-SAFT)"

    assert content_root(provider_module).attrib["url"] == "file://$MODULE_DIR$/packages/epcsaft"
    assert source_roots(provider_module) == {("file://$MODULE_DIR$/packages/epcsaft/src", "false")}
    assert module_dependencies(provider_module) == set()

    assert content_root(equilibrium_module).attrib["url"] == "file://$MODULE_DIR$/packages/epcsaft-equilibrium"
    assert source_roots(equilibrium_module) == {
        ("file://$MODULE_DIR$/packages/epcsaft-equilibrium/src", "false")
    }
    assert module_dependencies(equilibrium_module) == {"epcsaft"}

    assert content_root(regression_module).attrib["url"] == "file://$MODULE_DIR$/packages/epcsaft-regression"
    assert source_roots(regression_module) == {
        ("file://$MODULE_DIR$/packages/epcsaft-regression/src", "false")
    }
    assert module_dependencies(regression_module) == {"epcsaft"}

    workspace_text = _read(".idea/workspace.xml")
    workspace_xml = ET.fromstring(workspace_text)
    dashboard = next(component for component in workspace_xml.findall("component") if component.attrib.get("name") == "RunDashboard")
    dashboard_types = {
        option.attrib["value"]
        for option in dashboard.findall("./option[@name='configurationTypes']/set/option")
    }
    dashboard_status_types = {
        entry.attrib["key"]
        for entry in dashboard.findall("./option[@name='configurationStatuses']/map/entry")
    }
    assert dashboard_types == {"PythonConfigurationType", "ShConfigurationType"}
    assert "tests" not in dashboard_status_types
    assert "CMakeRunConfiguration" not in dashboard_status_types
    assert "pytest for " not in workspace_text

    run_configs: dict[str, tuple[Path, ET.Element]] = {}
    for path in sorted((REPO_ROOT / ".run").glob("*.run.xml")):
        config = ET.parse(path).getroot().find("configuration")
        assert config is not None, path.name
        name = config.get("name")
        assert name, path.name
        assert name not in run_configs, name
        run_configs[name] = (path, config)

    assert set(run_configs) == {spec.name for spec in run_config_specs}

    specs_by_name = {spec.name: spec for spec in run_config_specs}
    for name, (path, config) in run_configs.items():
        spec = specs_by_name[name]
        assert config.get("folderName") == spec.folder_name, name
        assert config.get("type") in {"PythonConfigurationType", "ShConfigurationType"}, name
        assert config.get("type") != "tests", name
        options = _run_config_options(config)
        if spec.runner == "Python":
            assert config.get("type") == "PythonConfigurationType", name
            module = config.find("module")
            assert module is not None, name
            assert module.attrib["name"] == "epcsaft", name
            assert options["WORKING_DIRECTORY"] == "$MODULE_DIR$", name
            assert options["SCRIPT_NAME"] == _module_script_path(spec.command), name
            assert options["PARAMETERS"] == spec.parameters, name
            script_path = REPO_ROOT / options["SCRIPT_NAME"].removeprefix("$MODULE_DIR$/")
            assert script_path.exists(), f"{path.name} points at missing {script_path}"
        else:
            assert config.get("type") == "ShConfigurationType", name
            assert options["INTERPRETER_PATH"].endswith("/pwsh.exe"), name
            assert options["SCRIPT_WORKING_DIRECTORY"] == REPO_ROOT.as_posix(), name
            script_path_text = options.get("SCRIPT_PATH", "")
            if script_path_text:
                assert options["SCRIPT_OPTIONS"] == spec.parameters, name
                assert Path(script_path_text).exists(), f"{path.name} points at missing {script_path_text}"
            else:
                assert options["SCRIPT_TEXT"] == spec.command, name

    build_native = _run_config_options(run_configs["Build Native Extension"][1])
    assert build_native["SCRIPT_PATH"].endswith("/.codex/environments/setup.ps1")
    assert build_native["SCRIPT_OPTIONS"] == "-Step Build"

    sync_workspace = _run_config_options(run_configs["Sync Workspace Packages"][1])
    assert sync_workspace["SCRIPT_TEXT"] == "uv sync --all-packages"

    check_imports = _run_config_options(run_configs["Check Package Imports"][1])
    assert check_imports["SCRIPT_NAME"] == "$MODULE_DIR$/scripts/dev/check_package_imports.py"
    assert check_imports["PARAMETERS"] == ""

    build_provider_only = _run_config_options(run_configs["Build Provider-Only Core"][1])
    assert build_provider_only["SCRIPT_NAME"] == "$MODULE_DIR$/scripts/dev/build_epcsaft.py"
    assert build_provider_only["PARAMETERS"] == "--clean --profile provider"

    equilibrium_confidence = _run_config_options(run_configs["Test Equilibrium Confidence"][1])
    assert equilibrium_confidence["SCRIPT_NAME"] == "$MODULE_DIR$/run_pytest.py"
    assert equilibrium_confidence["PARAMETERS"] == "--equilibrium-confidence -q"

    cmake_wrapper = _read("scripts/dev/cmake_preset.ps1")
    assert "Assert-NoNinjaLock" in cmake_wrapper
    assert "Assert-MsvcEnvironment" in cmake_wrapper
    assert "Resolve-RepoTool" in cmake_wrapper
    assert "CMAKE_MAKE_PROGRAM" in cmake_wrapper
    assert "VsDevCmd.bat" in cmake_wrapper
    assert "cmd.exe" in cmake_wrapper
    assert "cmake" in cmake_wrapper

    cmake_configure = _run_config_options(run_configs["CMake Configure dev-native"][1])
    assert cmake_configure["SCRIPT_TEXT"] == ""
    assert cmake_configure["SCRIPT_PATH"].endswith("/scripts/dev/cmake_preset.ps1")
    assert cmake_configure["SCRIPT_OPTIONS"] == "-Action Configure -Preset dev-native"

    cmake_core_build = _run_config_options(run_configs["CMake Build _core dev-native"][1])
    assert cmake_core_build["SCRIPT_TEXT"] == ""
    assert cmake_core_build["SCRIPT_PATH"].endswith("/scripts/dev/cmake_preset.ps1")
    assert cmake_core_build["SCRIPT_OPTIONS"] == "-Action Build -Preset dev-native -Target _core -Parallel 10"

    cmake_build = _run_config_options(run_configs["CMake Build dev-native"][1])
    assert cmake_build["SCRIPT_TEXT"] == ""
    assert cmake_build["SCRIPT_PATH"].endswith("/scripts/dev/cmake_preset.ps1")
    assert cmake_build["SCRIPT_OPTIONS"] == "-Action Build -Preset dev-native -Parallel 10"

    dry_run = _run_config_options(run_configs["Configure IntelliJ Runs (Dry Run)"][1])
    assert dry_run["SCRIPT_NAME"] == "$MODULE_DIR$/scripts/dev/configure_jetbrains_project.py"
    assert dry_run["PARAMETERS"] == "--dry-run"

    contract_check = _run_config_options(run_configs["Check IntelliJ Contract"][1])
    assert contract_check["SCRIPT_NAME"] == "$MODULE_DIR$/scripts/dev/configure_jetbrains_project.py"
    assert contract_check["PARAMETERS"] == "--check"

    apply_run = _run_config_options(run_configs["Configure IntelliJ Runs (Apply)"][1])
    assert apply_run["SCRIPT_NAME"] == "$MODULE_DIR$/scripts/dev/configure_jetbrains_project.py"
    assert apply_run["PARAMETERS"] == "--apply"


def test_repo_local_agent_roster_uses_supported_models_and_expected_scopes() -> None:
    expected_agents = {
        "build_packaging_owner.toml": ("gpt-5.4", "workspace-write"),
        "command_runner.toml": ("gpt-5.4", "workspace-write"),
        "native_equation_owner.toml": ("gpt-5.4", "read-only"),
        "native_solver_backend_owner.toml": ("gpt-5.4", "workspace-write"),
        "python_api_test_owner.toml": ("gpt-5.4", "workspace-write"),
    }

    agents_dir = REPO_ROOT / ".codex" / "agents"
    for filename, (model, sandbox_mode) in expected_agents.items():
        path = agents_dir / filename
        assert path.is_file(), filename
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        assert data["model"] == model
        assert data["sandbox_mode"] == sandbox_mode


def test_github_default_smoke_uses_downstream_path_install_not_wheel_build() -> None:
    workflow = _read(".github/workflows/wheels.yml")
    old_python = "uv python install " + "3." + "12"
    old_wheel_command = "uv build --" + "wheel"
    old_wheel_step = "Build Windows " + "wheel"

    assert "uv python install 3.13" in workflow
    assert old_python not in workflow
    assert '$repoUrl = "file:///"' in workflow
    assert "epcsaft @ ${repoUrl}/packages/epcsaft" in workflow
    assert "UV_CACHE_DIR" in workflow
    assert "EPCSAFT_PEP517_BUILD_DIR" in workflow
    assert "uv sync --python 3.13" in workflow
    assert "uv run --no-sync python" in workflow
    assert old_wheel_command not in workflow
    assert old_wheel_step not in workflow


def test_github_full_packaging_remains_manual_only() -> None:
    workflow = _read(".github/workflows/wheels.yml")
    old_cibw = 'CIBW_BUILD: "cp' + '312-*"'

    assert "workflow_dispatch:" in workflow
    assert "if: ${{ github.event_name == 'workflow_dispatch' && inputs.full_wheel_matrix }}" in workflow
    assert 'CIBW_BUILD: "cp313-*"' in workflow
    assert 'CIBW_ARCHS_WINDOWS: "AMD64"' in workflow
    assert old_cibw not in workflow
    assert "ubuntu-latest, macos-latest, windows-latest" not in workflow
    assert "build Windows wheel" in workflow


def test_github_default_events_run_windows_package_boundary_smoke() -> None:
    workflow = _read(".github/workflows/wheels.yml")

    assert "fast-pr-smoke:" in workflow
    assert "windows-install-smoke:" in workflow
    assert "if: ${{ github.event_name == 'pull_request' }}" in workflow
    windows_smoke = workflow.split("\n  windows-install-smoke:", 1)[1].split("\n  build:", 1)[0]
    assert "    if:" not in windows_smoke
    assert workflow.count("runs-on: windows-latest") >= 3
    assert workflow.count("name: windows install smoke") == 1
    assert workflow.count("name: fast workflow smoke") == 1


def test_package_build_lanes_are_split_by_distribution_and_sdk_mode() -> None:
    workflow = _read(".github/workflows/package-build-lanes.yml")

    assert "name: package-build-lanes" in workflow
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "schedule:" not in workflow
    assert "provider-package:" in workflow
    assert "regression-package:" in workflow
    assert "equilibrium-package:" in workflow
    assert "installed-provider-extensions:" in workflow
    assert "run_ipopt_lanes:" in workflow
    assert "ipopt_root:" in workflow
    assert "uv run python scripts/dev/build_dist.py --parallel 1" in workflow
    assert "uv run python scripts/dev/build_system_ceres.py --parallel 2" in workflow
    assert "uv run python scripts/dev/check_release_installs.py --dist-dir dist --combination provider" in workflow
    assert "uv run python scripts/dev/check_release_installs.py --dist-dir dist --combination regression" in workflow
    assert "uv run python scripts/dev/check_release_installs.py --dist-dir dist --combination equilibrium" in workflow
    assert "uv run python scripts/dev/check_release_installs.py --dist-dir dist --combination all" in workflow
    assert "--disable-ipopt" not in workflow
    assert "no no-Ipopt package proof is accepted" in workflow


def test_heavy_native_workflow_is_manual_only() -> None:
    workflow = _read(".github/workflows/native-build-profiles.yml")

    assert "name: native-build-profiles" in workflow
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "schedule:" not in workflow
    assert "native no-Ipopt smoke" in workflow
    assert "native CppAD derivative contract" in workflow


def test_pr_template_does_not_force_production_proof_answers_on_ordinary_prs() -> None:
    template = _read(".github/PULL_REQUEST_TEMPLATE.md")

    assert "## Required PR Answers" not in template
    assert "What downstream workflow can now run" not in template
    assert "What production native code path now exists" not in template
    assert "What derivative path is used" not in template
    assert "What real data or benchmark proves it" not in template
    assert "This PR does not broaden `capabilities()` or public claims without executable proof" in template


def test_pypi_publish_workflow_uses_trusted_publishing() -> None:
    workflow = _read(".github/workflows/publish-pypi.yml")
    publishing_docs = _read("docs/pages/publishing.rst")

    for token in (
        "name: publish-to-pypi",
        "workflow_dispatch:",
        "id-token: write",
        "environment:",
        "name: pypi",
        "pypa/gh-action-pypi-publish@release/v1",
        "actions/download-artifact@v8.0.1",
        "merge-multiple: true",
        'CIBW_BUILD: "cp313-*"',
        'CIBW_ARCHS_WINDOWS: "AMD64"',
        "uv build packages/epcsaft --sdist",
        "pypi-preflight:",
        "PyPI trusted publisher preflight",
        "https://pypi.org/pypi/{project}/json",
        "pending publisher",
        "PyPI first-publish preflight",
        "already has {project} {version}",
    ):
        assert token in workflow
    assert "release:" not in workflow
    assert "types: [published]" not in workflow
    assert "github.event.release" not in workflow
    assert "needs: [pypi-preflight]" in workflow
    assert "password:" not in workflow
    assert "username:" not in workflow
    assert "PYPI_API_TOKEN" not in workflow
    assert "pp*" not in workflow
    assert "Workflow filename: ``publish-pypi.yml``" in publishing_docs
    assert "Environment name: ``pypi``" in publishing_docs
    assert "GitHub releases and PyPI uploads are separate steps" in publishing_docs
    assert "Creating a GitHub release does not upload to PyPI" in publishing_docs


def test_version_defaults_are_derived_from_pyproject() -> None:
    cmake = _read("CMakeLists.txt")
    docs_conf = _read("docs/conf.py")

    assert 'set(SKBUILD_PROJECT_VERSION "1.5.0")' not in cmake
    assert 'release = "1.5.0"' not in docs_conf
    assert "pyproject.toml" in cmake
    assert "pyproject.toml" in docs_conf
    assert "Could not derive documentation release from pyproject.toml" in docs_conf


def test_native_warning_options_apply_to_all_native_targets() -> None:
    cmake = _read("CMakeLists.txt")

    assert 'option(EPCSAFT_WARNINGS_AS_ERRORS "Treat native warnings as errors" OFF)' in cmake
    assert 'option(EPCSAFT_ENABLE_SANITIZERS "Enable ASAN/UBSAN in debug builds" OFF)' in cmake
    assert "set(EPCSAFT_NATIVE_OBJECT_TARGETS" in cmake
    assert "epcsaft_provider_native" in cmake
    assert "epcsaft_equilibrium_native" in cmake
    assert "epcsaft_regression_native" in cmake
    assert "set(EPCSAFT_NATIVE_TARGETS" in cmake
    assert "${EPCSAFT_NATIVE_OBJECT_TARGETS}" in cmake
    assert "foreach(target_name IN LISTS EPCSAFT_NATIVE_TARGETS)" in cmake
    assert "target_compile_options(${target_name} PRIVATE -Wall -Wextra -Wpedantic)" in cmake
