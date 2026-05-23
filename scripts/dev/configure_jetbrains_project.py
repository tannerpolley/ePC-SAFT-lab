from __future__ import annotations

import argparse
import io
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]
IDEA_DIR = REPO_ROOT / ".idea"
WORKSPACE_PATH = IDEA_DIR / "workspace.xml"
RUN_DIR = REPO_ROOT / ".run"
RUN_WORKING_DIRECTORY = REPO_ROOT.as_posix()
MODULE_URL_PREFIX = "file://$MODULE_DIR$"
CONTENT_URL = MODULE_URL_PREFIX
MODULE_DIR_MACRO = "$MODULE_DIR$"
MODULE_NAME = "ePC-SAFT"
PYTHON_CONFIG_TYPE = "PythonConfigurationType"
SHELL_CONFIG_TYPE = "ShConfigurationType"
RUN_DASHBOARD_CONFIG_TYPES = (PYTHON_CONFIG_TYPE, SHELL_CONFIG_TYPE)
PYTHON_RUNNER = "Python"
SHELL_RUNNER = "Shell Script"
PYTHON_SDK_HOME = "$MODULE_DIR$/.venv/Scripts/python.exe"
PYTHON_SDK_NAME = "uv (ePC-SAFT)"
POWERSHELL_INTERPRETER = "C:/Program Files/PowerShell/7/pwsh.exe"
RUN_CONFIG_FOLDER = "ePC-SAFT"
RUN_CONFIG_FOLDER_ATTRIBUTE: str | None = None
FOLDER_SETUP_HEALTH = "Setup & Health"
FOLDER_BUILD_PACKAGE = "Build & Package"
FOLDER_VALIDATION = "Validation"
FOLDER_TESTS = "Tests"
FOLDER_DOCS_REPORTS = "Docs & Reports"
FOLDER_ANALYSIS_FIGURES = "Analysis & Figures"
FOLDER_MAINTENANCE = "Maintenance"
TRANSIENT_PATHS: tuple[str, ...] = (
    "build",
    "dist",
    ".venv",
    ".worktrees",
    "_codex",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "docs/_build",
    "docs/latex/out",
    "results/runs",
)
# Keep tests under the module content root, not as a source root. Marking
# tests as a source root makes tests/api, tests/native, and tests/support look
# like top-level namespace packages in IntelliJ.
CANONICAL_SOURCE_ROOTS: tuple[tuple[str, bool], ...] = (("src", False),)


@dataclass(frozen=True)
class RunConfigSpec:
    name: str
    runner: str
    folder_name: str
    command: str
    parameters: str = ""


CANONICAL_RUN_CONFIGS: tuple[RunConfigSpec, ...] = (
    RunConfigSpec(
        name="Sync Environment",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command="uv sync --no-install-project",
    ),
    RunConfigSpec(
        name="Bootstrap uv",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command="scripts/dev/bootstrap_uv.ps1",
    ),
    RunConfigSpec(
        name="Doctor",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command=".codex/environments/setup.ps1",
        parameters="-Step Doctor",
    ),
    RunConfigSpec(
        name="Doctor Script",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command="scripts/dev/doctor.py",
    ),
    RunConfigSpec(
        name="Build Native Extension",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command=".codex/environments/setup.ps1",
        parameters="-Step Build",
    ),
    RunConfigSpec(
        name="Build Status",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/build_epcsaft.py",
        parameters="--status",
    ),
    RunConfigSpec(
        name="Build Native Incremental",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/build_epcsaft.py",
        parameters="--build-only --parallel 10",
    ),
    RunConfigSpec(
        name="Build System Ceres",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/build_system_ceres.py",
        parameters="--parallel 4",
    ),
    RunConfigSpec(
        name="Clean Build Artifacts",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/clean_build.ps1",
    ),
    RunConfigSpec(
        name="Validate Quick",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/dev/validate_project.py",
        parameters="quick",
    ),
    RunConfigSpec(
        name="Validate Confidence",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/dev/validate_project.py",
        parameters="confidence",
    ),
    RunConfigSpec(
        name="Check Text Gates",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/dev/check_text_gates.py",
    ),
    RunConfigSpec(
        name="Validate Hydrocarbon Regression",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/validation/validate_hydrocarbon_regression.py",
    ),
    RunConfigSpec(
        name="Run Ipopt Exact Hessian Proofs",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/dev/run_ipopt_exact_hessian_proofs.py",
    ),
    RunConfigSpec(
        name="Test List Slices",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--list-slices",
    ),
    RunConfigSpec(
        name="Test API",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--api -q",
    ),
    RunConfigSpec(
        name="Test Equilibrium API",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--equilibrium-api -q",
    ),
    RunConfigSpec(
        name="Test Runtime",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--runtime -q",
    ),
    RunConfigSpec(
        name="Test Native",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--native -q",
    ),
    RunConfigSpec(
        name="Test Native Contracts",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--native-contracts -q",
    ),
    RunConfigSpec(
        name="Test Workflow Guards",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="tests/workflows/repo/test_workflow_entrypoints.py tests/workflows/build/test_build_epcsaft.py -q",
    ),
    RunConfigSpec(
        name="Build Docs",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/dev/validate_project.py",
        parameters="docs",
    ),
    RunConfigSpec(
        name="Build Equations PDF",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/docs/build_equations_pdf.ps1",
    ),
    RunConfigSpec(
        name="Sync Equation Registry",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/docs/sync_equation_registry.py",
    ),
    RunConfigSpec(
        name="Sync Algorithm Registry",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/docs/sync_algorithm_registry.py",
    ),
    RunConfigSpec(
        name="Build Parameter Catalog",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/data/build_epcsaft_parameter_catalog.py",
    ),
    RunConfigSpec(
        name="Extract Paper Parameter CSVs",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/data/extract_paper_parameter_csvs.py",
    ),
    RunConfigSpec(
        name="Sync MIAC Variants",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/data/sync_miac_variants.py",
    ),
    RunConfigSpec(
        name="Sync LaTeX Mirror",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/docs/sync_latex_mirror.ps1",
    ),
    RunConfigSpec(
        name="Setup LaTeX Mirror",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/docs/setup_latex_mirror.ps1",
    ),
    RunConfigSpec(
        name="Install LaTeX Sync Hook",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/docs/install_latex_sync_hook.ps1",
    ),
    RunConfigSpec(
        name="Build Distribution",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/build_dist.py",
    ),
    RunConfigSpec(
        name="Generate Equilibrium Activation",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_ANALYSIS_FIGURES,
        command="scripts/dev/generate_equilibrium_activation.py",
    ),
    RunConfigSpec(
        name="Create Dev Worktree",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/create_dev_worktree.ps1",
    ),
    RunConfigSpec(
        name="Configure IntelliJ Runs (Dry Run)",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/configure_jetbrains_project.py",
        parameters="--dry-run",
    ),
    RunConfigSpec(
        name="Configure IntelliJ Runs (Apply)",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/configure_jetbrains_project.py",
        parameters="--apply",
    ),
    RunConfigSpec(
        name="Association Goal 1+2 Tests",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters=(
            "tests/native/contracts/test_association_implicit_derivative_contract.py "
            "tests/native/state/test_eos_contributions.py "
            "tests/native/state/test_phase_state_sensitivities.py "
            "tests/native/equilibrium/blocks/test_eos_phase_block.py "
            "tests/api/frontend/test_state_properties.py -q"
        ),
    ),
    RunConfigSpec(
        name="Association Goal 3 Tests",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="tests/native/contracts tests/native/regression tests/api/frontend/test_regression.py -q",
    ),
    RunConfigSpec(
        name="Association Goal 4 Tests",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters=(
            "tests/native/state/test_fugacity_derivatives.py "
            "tests/native/state/test_association_parameter_derivative_validation.py "
            "tests/native/state/test_pressure_derivatives.py "
            "tests/native/state/test_phase_state_sensitivities.py "
            "tests/native/contracts/test_association_implicit_derivative_contract.py "
            "tests/native/contracts/test_ceres_cppad_build_contract.py -q"
        ),
    ),
    RunConfigSpec(
        name="Association Goal 5 Tests",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters=(
            "tests/native/state/test_fugacity_derivatives.py "
            "tests/native/state/test_association_parameter_derivative_validation.py "
            "tests/native/state/test_pressure_derivatives.py "
            "tests/native/regression/test_binary.py "
            "tests/native/contracts/test_ceres_cppad_build_contract.py -q"
        ),
    ),
    RunConfigSpec(
        name="Association Goal 6 Tests",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters=(
            "tests/native/equilibrium/blocks/test_association_block.py "
            "tests/native/equilibrium/blocks/test_eos_phase_block.py "
            "tests/native/equilibrium/diagnostics/test_selector_core_contracts.py -q"
        ),
    ),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize JetBrains module metadata under .idea/.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Report pending changes without writing files.",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite module files in place.",
    )
    return parser


def _module_url(relative_path: str) -> str:
    normalized = relative_path.replace("\\", "/").strip("/")
    if not normalized:
        return CONTENT_URL
    return f"{MODULE_URL_PREFIX}/{normalized}"


def _relative_module_path(url: str | None) -> PurePosixPath | None:
    if url is None:
        return None
    if url == MODULE_URL_PREFIX:
        return PurePosixPath(".")
    prefix = f"{MODULE_URL_PREFIX}/"
    if not url.startswith(prefix):
        return None
    relative = url[len(prefix) :].strip("/")
    if not relative:
        return PurePosixPath(".")
    return PurePosixPath(relative)


def _is_under_path(url: str | None, relative_path: str) -> bool:
    candidate = _relative_module_path(url)
    if candidate is None:
        return False
    base = PurePosixPath(relative_path)
    return candidate == base or base in candidate.parents


def _existing_transient_paths() -> tuple[str, ...]:
    existing: list[str] = []
    for relative_path in TRANSIENT_PATHS:
        if (REPO_ROOT / relative_path).exists():
            existing.append(relative_path)
    return tuple(existing)


def _discover_iml_files() -> tuple[Path, ...]:
    candidates = list(IDEA_DIR.glob("*.iml"))
    candidates.extend(REPO_ROOT.glob("*.iml"))
    return tuple(sorted(path.resolve() for path in candidates))


def _find_child(parent: ET.Element, tag: str, **attrs: str) -> ET.Element | None:
    for child in parent.findall(tag):
        if all(child.get(key) == value for key, value in attrs.items()):
            return child
    return None


def _ensure_root_manager(module_root: ET.Element, actions: list[str]) -> ET.Element:
    manager = _find_child(module_root, "component", name="NewModuleRootManager")
    if manager is None:
        manager = ET.Element("component", {"name": "NewModuleRootManager", "inherit-compiler-output": "true"})
        module_root.insert(0, manager)
        actions.append("create NewModuleRootManager component")
    elif manager.get("inherit-compiler-output") is None:
        manager.set("inherit-compiler-output", "true")
        actions.append("set NewModuleRootManager inherit-compiler-output=true")
    return manager


def _ensure_exclude_output(manager: ET.Element, actions: list[str]) -> None:
    exclude_output = manager.find("exclude-output")
    if exclude_output is None:
        manager.insert(0, ET.Element("exclude-output"))
        actions.append("add exclude-output element")


def _ensure_content_root(manager: ET.Element, actions: list[str]) -> ET.Element:
    content = _find_child(manager, "content", url=CONTENT_URL)
    if content is not None:
        return content

    first_content = manager.find("content")
    if first_content is not None:
        if first_content.get("url") != CONTENT_URL:
            first_content.set("url", CONTENT_URL)
            actions.append(f"set content root to {CONTENT_URL}")
        return first_content

    content = ET.Element("content", {"url": CONTENT_URL})
    insert_at = 1 if manager.find("exclude-output") is not None else 0
    manager.insert(insert_at, content)
    actions.append(f"create content root {CONTENT_URL}")
    return content


def _ensure_source_folder_order_entry(manager: ET.Element, actions: list[str]) -> None:
    for entry in manager.findall("orderEntry"):
        if entry.get("type") == "sourceFolder":
            return
    manager.append(ET.Element("orderEntry", {"type": "sourceFolder", "forTests": "false"}))
    actions.append("add sourceFolder orderEntry")


def _prune_stale_module_dependencies(manager: ET.Element, declared_modules: set[str], actions: list[str]) -> None:
    if not declared_modules:
        return
    for entry in list(manager.findall("orderEntry")):
        if entry.get("type") != "module":
            continue
        module_name = entry.get("module-name")
        if module_name and module_name not in declared_modules:
            manager.remove(entry)
            actions.append(f"remove stale module dependency {module_name}")


def _replace_content_roots(content: ET.Element, transient_paths: tuple[str, ...], actions: list[str]) -> None:
    existing_source_folders = list(content.findall("sourceFolder"))
    existing_exclude_folders = list(content.findall("excludeFolder"))
    preserved_children = [child for child in list(content) if child.tag not in {"sourceFolder", "excludeFolder"}]
    canonical_source_keys = {
        (_module_url(relative_path), "true" if is_test else "false")
        for relative_path, is_test in CANONICAL_SOURCE_ROOTS
    }

    desired_sources: dict[tuple[str, str], ET.Element] = {}
    for source in existing_source_folders:
        url = source.get("url")
        is_test = "true" if source.get("isTestSource") == "true" else "false"
        if any(_is_under_path(url, path) for path in transient_paths):
            actions.append(f"remove transient sourceFolder {url}")
            continue
        key = (url or "", is_test)
        if key not in canonical_source_keys:
            actions.append(f"remove noncanonical sourceFolder {url} (isTestSource={is_test})")
            continue
        if key in desired_sources:
            actions.append(f"remove duplicate sourceFolder {url} (isTestSource={is_test})")
            continue
        desired_sources[key] = ET.Element(
            "sourceFolder",
            {"url": url or "", "isTestSource": is_test},
        )

    for relative_path, is_test in CANONICAL_SOURCE_ROOTS:
        url = _module_url(relative_path)
        key = (url, "true" if is_test else "false")
        if key not in desired_sources:
            desired_sources[key] = ET.Element(
                "sourceFolder",
                {"url": url, "isTestSource": "true" if is_test else "false"},
            )
            label = "test source root" if is_test else "source root"
            actions.append(f"ensure {label} {url}")

    desired_excludes: dict[str, ET.Element] = {}
    for exclude in existing_exclude_folders:
        url = exclude.get("url")
        if not url:
            continue
        nested_transient_parent = next(
            (
                relative_path
                for relative_path in TRANSIENT_PATHS
                if _is_under_path(url, relative_path) and url != _module_url(relative_path)
            ),
            None,
        )
        if nested_transient_parent is not None:
            actions.append(f"remove nested transient excludeFolder {url}")
            continue
        if url not in desired_excludes:
            desired_excludes[url] = ET.Element("excludeFolder", {"url": url})
        else:
            actions.append(f"remove duplicate excludeFolder {url}")

    for relative_path in transient_paths:
        url = _module_url(relative_path)
        if url not in desired_excludes:
            desired_excludes[url] = ET.Element("excludeFolder", {"url": url})
            actions.append(f"ensure excludeFolder {url}")

    sorted_exclude_urls = sorted(desired_excludes)
    collapsed_excludes: list[ET.Element] = []
    kept_exclude_urls: list[str] = []
    for url in sorted_exclude_urls:
        if any(
            _is_under_path(url, kept_url[len(MODULE_URL_PREFIX) + 1 :])
            for kept_url in kept_exclude_urls
            if kept_url.startswith(f"{MODULE_URL_PREFIX}/")
        ):
            actions.append(f"remove redundant nested excludeFolder {url}")
            continue
        collapsed_excludes.append(desired_excludes[url])
        kept_exclude_urls.append(url)

    sorted_sources = sorted(
        desired_sources.values(),
        key=lambda element: (
            element.get("url", ""),
            element.get("isTestSource", "false") == "true",
        ),
    )

    for child in list(content):
        content.remove(child)
    for source in sorted_sources:
        content.append(source)
    for exclude in collapsed_excludes:
        content.append(exclude)
    for child in preserved_children:
        content.append(child)


def _serialize_tree(tree: ET.ElementTree) -> str:
    ET.indent(tree, space="  ")
    buffer = io.BytesIO()
    tree.write(buffer, encoding="UTF-8", xml_declaration=True)
    return buffer.getvalue().decode("UTF-8")


def _load_workspace_tree() -> tuple[ET.ElementTree, str]:
    if WORKSPACE_PATH.exists():
        original_text = WORKSPACE_PATH.read_text(encoding="UTF-8")
        return ET.ElementTree(ET.fromstring(original_text)), original_text
    return ET.ElementTree(ET.Element("project", {"version": "4"})), ""


def _normalize_workspace() -> tuple[list[str], list[str], str | None]:
    if not IDEA_DIR.exists():
        return [], [], None

    try:
        tree, original_text = _load_workspace_tree()
    except ET.ParseError as exc:
        return [], [f".idea/workspace.xml: invalid XML ({exc})"], None

    root = tree.getroot()
    if root.tag != "project":
        return [], [".idea/workspace.xml: root element is not <project>"], None

    actions: list[str] = []
    canonical_names = {spec.name for spec in CANONICAL_RUN_CONFIGS}
    removed_run_manager_names: list[str] = []
    run_manager = _find_child(root, "component", name="RunManager")
    if run_manager is not None:
        for config in list(run_manager.findall("configuration")):
            name = config.get("name")
            if (
                config.get("temporary") == "true"
                and config.get("nameIsGenerated") == "true"
                and config.get("type") in RUN_DASHBOARD_CONFIG_TYPES
                and name not in canonical_names
            ):
                run_manager.remove(config)
                removed_run_manager_names.append(name or "<unnamed>")
        for name in removed_run_manager_names:
            actions.append(f"remove temporary generated run configuration {name}")
        selected = run_manager.get("selected")
        if selected and any(selected.endswith(f".{name}") for name in removed_run_manager_names):
            del run_manager.attrib["selected"]
            actions.append("clear stale selected temporary run configuration")
    active_run_manager_names = set(canonical_names)
    if run_manager is not None:
        active_run_manager_names.update(
            name
            for name in (config.get("name") for config in run_manager.findall("configuration"))
            if name
        )

    properties_component = _find_child(root, "component", name="PropertiesComponent")
    if properties_component is not None:
        raw_properties = properties_component.text or "{}"
        try:
            properties = json.loads(raw_properties)
        except json.JSONDecodeError:
            properties = None
        if isinstance(properties, dict):
            key_to_string = properties.get("keyToString")
            if isinstance(key_to_string, dict):
                for key in list(key_to_string):
                    if not key.startswith("Python.") or not key.endswith(".executor"):
                        continue
                    name = key[len("Python.") : -len(".executor")]
                    if name in active_run_manager_names:
                        continue
                    del key_to_string[key]
                    actions.append(f"remove stale executor property {key}")
                properties_component.text = json.dumps(properties, indent=2, sort_keys=False)

    dashboard = _find_child(root, "component", name="RunDashboard")
    if dashboard is None:
        dashboard = ET.Element("component", {"name": "RunDashboard"})
        root.append(dashboard)
        actions.append("create RunDashboard component")

    config_types = _find_child(dashboard, "option", name="configurationTypes")
    if config_types is None:
        config_types = ET.Element("option", {"name": "configurationTypes"})
        dashboard.append(config_types)
        actions.append("create RunDashboard configurationTypes option")

    values = config_types.find("set")
    if values is None:
        values = ET.Element("set")
        config_types.append(values)
        actions.append("create RunDashboard configurationTypes set")

    existing_values = {
        child.get("value")
        for child in values.findall("option")
        if child.get("value")
    }
    for config_type in RUN_DASHBOARD_CONFIG_TYPES:
        if config_type in existing_values:
            continue
        values.append(ET.Element("option", {"value": config_type}))
        actions.append(f"enable Services Run Dashboard for {config_type}")

    if not actions:
        return [], [], None

    proposed_text = _serialize_tree(tree)
    return actions, [], proposed_text if proposed_text != original_text else None


def _run_script_path(relative_path: str) -> str:
    normalized = relative_path.replace("\\", "/").strip("/")
    if not normalized:
        return MODULE_DIR_MACRO
    return f"{MODULE_DIR_MACRO}/{normalized}"


def _shell_script_path(relative_path: str) -> str:
    normalized = relative_path.replace("\\", "/").strip("/")
    if not normalized:
        return RUN_WORKING_DIRECTORY
    return (REPO_ROOT / normalized).as_posix()


def _add_option(parent: ET.Element, name: str, value: str) -> None:
    parent.append(ET.Element("option", {"name": name, "value": value}))


def _run_component(configuration: ET.Element) -> ET.ElementTree:
    component = ET.Element("component", {"name": "ProjectRunConfigurationManager"})
    component.append(configuration)
    return ET.ElementTree(component)


def _run_config_type(spec: RunConfigSpec) -> str:
    if spec.runner == PYTHON_RUNNER:
        return PYTHON_CONFIG_TYPE
    if spec.runner == SHELL_RUNNER:
        return SHELL_CONFIG_TYPE
    raise ValueError(f"Unsupported run config runner: {spec.runner}")


def _python_configuration(spec: RunConfigSpec) -> ET.Element:
    attrs = {
        "default": "false",
        "name": spec.name,
        "type": PYTHON_CONFIG_TYPE,
        "factoryName": PYTHON_RUNNER,
    }
    if RUN_CONFIG_FOLDER_ATTRIBUTE:
        attrs["folderName"] = RUN_CONFIG_FOLDER_ATTRIBUTE
    config = ET.Element(
        "configuration",
        attrs,
    )
    config.append(ET.Element("module", {"name": MODULE_NAME}))
    _add_option(config, "ENV_FILES", "")
    _add_option(config, "INTERPRETER_OPTIONS", "")
    _add_option(config, "PARENT_ENVS", "true")
    envs = ET.Element("envs")
    envs.append(ET.Element("env", {"name": "PYTHONUNBUFFERED", "value": "1"}))
    config.append(envs)
    _add_option(config, "SDK_HOME", PYTHON_SDK_HOME)
    _add_option(config, "SDK_NAME", PYTHON_SDK_NAME)
    _add_option(config, "WORKING_DIRECTORY", MODULE_DIR_MACRO)
    _add_option(config, "IS_MODULE_SDK", "false")
    _add_option(config, "ADD_CONTENT_ROOTS", "true")
    _add_option(config, "ADD_SOURCE_ROOTS", "true")
    _add_option(config, "DEBUG_JUST_MY_CODE", "false")
    _add_option(config, "RUN_TOOL", "")
    _add_option(config, "SCRIPT_NAME", _run_script_path(spec.command))
    _add_option(config, "PARAMETERS", spec.parameters)
    _add_option(config, "SHOW_COMMAND_LINE", "false")
    _add_option(config, "EMULATE_TERMINAL", "false")
    _add_option(config, "MODULE_MODE", "false")
    _add_option(config, "REDIRECT_INPUT", "false")
    _add_option(config, "INPUT_FILE", "")
    config.append(ET.Element("method", {"v": "2"}))
    return config


def _is_powershell_script(command: str) -> bool:
    return command.lower().endswith(".ps1")


def _path_option(parent: ET.Element, name: str, value: str) -> None:
    _add_option(parent, f"INDEPENDENT_{name}", "true")
    _add_option(parent, name, value)


def _shell_configuration(spec: RunConfigSpec) -> ET.Element:
    attrs = {
        "default": "false",
        "name": spec.name,
        "type": SHELL_CONFIG_TYPE,
        "factoryName": SHELL_RUNNER,
    }
    if RUN_CONFIG_FOLDER_ATTRIBUTE:
        attrs["folderName"] = RUN_CONFIG_FOLDER_ATTRIBUTE
    config = ET.Element(
        "configuration",
        attrs,
    )
    if _is_powershell_script(spec.command):
        script_text = ""
        script_path = _shell_script_path(spec.command)
        script_options = spec.parameters
        interpreter_options = "-NoProfile -ExecutionPolicy Bypass -File"
        execute_script_file = "true"
    else:
        script_text = spec.command
        script_path = ""
        script_options = ""
        interpreter_options = "-NoProfile -ExecutionPolicy Bypass -Command"
        execute_script_file = "false"

    _add_option(config, "SCRIPT_TEXT", script_text)
    _path_option(config, "SCRIPT_PATH", script_path)
    _add_option(config, "SCRIPT_OPTIONS", script_options)
    _path_option(config, "SCRIPT_WORKING_DIRECTORY", RUN_WORKING_DIRECTORY)
    _path_option(config, "INTERPRETER_PATH", POWERSHELL_INTERPRETER)
    _add_option(config, "INTERPRETER_OPTIONS", interpreter_options)
    _add_option(config, "EXECUTE_IN_TERMINAL", "false")
    _add_option(config, "EXECUTE_SCRIPT_FILE", execute_script_file)
    config.append(ET.Element("method", {"v": "2"}))
    return config


def _run_configuration(spec: RunConfigSpec) -> ET.Element:
    if spec.runner == PYTHON_RUNNER:
        return _python_configuration(spec)
    if spec.runner == SHELL_RUNNER:
        return _shell_configuration(spec)
    raise ValueError(f"Unsupported run config runner: {spec.runner}")


def _load_shared_run_config_paths() -> tuple[dict[str, list[Path]], list[str]]:
    configs_by_name: dict[str, list[Path]] = {}
    warnings: list[str] = []
    if not RUN_DIR.exists():
        return configs_by_name, warnings

    for path in sorted(RUN_DIR.glob("*.run.xml")):
        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            warnings.append(f"{path.relative_to(REPO_ROOT).as_posix()}: invalid XML ({exc})")
            continue
        config = tree.getroot().find("configuration")
        name = config.get("name") if config is not None else None
        if not name:
            warnings.append(f"{path.relative_to(REPO_ROOT).as_posix()}: missing configuration name")
            continue
        configs_by_name.setdefault(name, []).append(path)
    return configs_by_name, warnings


def _option_value(config: ET.Element, name: str) -> str | None:
    option = _find_child(config, "option", name=name)
    return option.get("value") if option is not None else None


def _expected_option_values(spec: RunConfigSpec) -> dict[str, str]:
    if spec.runner == PYTHON_RUNNER:
        return {
            "WORKING_DIRECTORY": MODULE_DIR_MACRO,
            "SCRIPT_NAME": _run_script_path(spec.command),
            "PARAMETERS": spec.parameters,
        }
    if spec.runner == SHELL_RUNNER and _is_powershell_script(spec.command):
        return {
            "SCRIPT_PATH": _shell_script_path(spec.command),
            "SCRIPT_OPTIONS": spec.parameters,
            "SCRIPT_WORKING_DIRECTORY": RUN_WORKING_DIRECTORY,
            "INTERPRETER_PATH": POWERSHELL_INTERPRETER,
            "EXECUTE_SCRIPT_FILE": "true",
        }
    if spec.runner == SHELL_RUNNER:
        return {
            "SCRIPT_TEXT": spec.command,
            "SCRIPT_WORKING_DIRECTORY": RUN_WORKING_DIRECTORY,
            "INTERPRETER_PATH": POWERSHELL_INTERPRETER,
            "EXECUTE_SCRIPT_FILE": "false",
        }
    raise ValueError(f"Unsupported run config runner: {spec.runner}")


def _run_config_actions(spec: RunConfigSpec, current_config: ET.Element | None) -> list[str]:
    if current_config is None:
        return [f"create {spec.runner} run configuration"]

    actions: list[str] = []
    expected_type = _run_config_type(spec)
    if current_config.get("type") != expected_type:
        actions.append(f"set runner type to {spec.runner}")
    if current_config.get("factoryName") != spec.runner:
        actions.append(f"set factoryName={spec.runner}")
    if RUN_CONFIG_FOLDER_ATTRIBUTE:
        if current_config.get("folderName") != RUN_CONFIG_FOLDER_ATTRIBUTE:
            actions.append(f"set folderName={RUN_CONFIG_FOLDER_ATTRIBUTE}")
    elif current_config.get("folderName") is not None:
        actions.append("remove folderName")
    for option_name, expected_value in _expected_option_values(spec).items():
        if _option_value(current_config, option_name) != expected_value:
            actions.append(f"set {option_name}={expected_value}")
    return actions


def _normalize_run_config(
    spec: RunConfigSpec,
    existing_paths: dict[str, list[Path]],
) -> tuple[Path, list[str], str | None]:
    path = existing_paths.get(spec.name, [RUN_DIR / f"{spec.name}.run.xml"])[0]
    original_text = path.read_text(encoding="UTF-8") if path.exists() else ""
    current_config: ET.Element | None = None
    if path.exists():
        try:
            current_config = ET.parse(path).getroot().find("configuration")
        except ET.ParseError:
            current_config = None

    proposed_text = _serialize_tree(_run_component(_run_configuration(spec)))
    if proposed_text == original_text:
        return path, [], None

    actions = _run_config_actions(spec, current_config)
    if not actions:
        actions = ["normalize run configuration XML"]
    return path, actions, proposed_text


def _load_declared_modules() -> set[str]:
    modules_path = IDEA_DIR / "modules.xml"
    if not modules_path.exists():
        return set()
    tree = ET.parse(modules_path)
    root = tree.getroot()
    names: set[str] = set()
    for module in root.findall(".//module"):
        for attr_name in ("filepath", "fileurl"):
            value = module.get(attr_name)
            if not value or not value.endswith(".iml"):
                continue
            names.add(Path(value).stem)
            break
    return names


def _module_dependency_warnings(iml_path: Path, module_root: ET.Element, declared_modules: set[str]) -> list[str]:
    if not declared_modules:
        return []
    warnings: list[str] = []
    for dependency in module_root.findall(".//orderEntry[@type='module']"):
        module_name = dependency.get("module-name")
        if module_name and module_name not in declared_modules:
            warnings.append(f"stale module dependency '{module_name}' is not declared in .idea/modules.xml")
    return warnings


def _normalize_iml(
    iml_path: Path, transient_paths: tuple[str, ...], declared_modules: set[str]
) -> tuple[list[str], list[str], str | None]:
    original_text = iml_path.read_text(encoding="UTF-8")
    tree = ET.parse(iml_path)
    module_root = tree.getroot()
    actions: list[str] = []
    manager = _ensure_root_manager(module_root, actions)
    _ensure_exclude_output(manager, actions)
    content = _ensure_content_root(manager, actions)
    _ensure_source_folder_order_entry(manager, actions)
    _prune_stale_module_dependencies(manager, declared_modules, actions)
    _replace_content_roots(content, transient_paths, actions)
    warnings = _module_dependency_warnings(iml_path, module_root, declared_modules)
    proposed_text = _serialize_tree(tree)
    if proposed_text == original_text:
        actions = []
    return actions, warnings, proposed_text if proposed_text != original_text else None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    transient_paths = _existing_transient_paths()
    declared_modules = _load_declared_modules()
    iml_files = _discover_iml_files()
    run_configs_by_name, run_config_warnings = _load_shared_run_config_paths()

    pending_changes = 0
    warnings_found = 0
    for warning in run_config_warnings:
        warnings_found += 1
        print(f"WARNING {warning}")

    canonical_names = {spec.name for spec in CANONICAL_RUN_CONFIGS}
    for name, paths in sorted(run_configs_by_name.items()):
        if name not in canonical_names:
            for path in paths:
                pending_changes += 1
                relative_path = path.relative_to(REPO_ROOT).as_posix()
                prefix = "APPLY" if args.apply else "DRY-RUN"
                print(f"{prefix} {relative_path}: delete stale shared run configuration")
                if args.apply:
                    path.unlink()
            continue
        for duplicate_path in paths[1:]:
            pending_changes += 1
            relative_path = duplicate_path.relative_to(REPO_ROOT).as_posix()
            prefix = "APPLY" if args.apply else "DRY-RUN"
            print(f"{prefix} {relative_path}: delete duplicate shared run configuration '{name}'")
            if args.apply:
                duplicate_path.unlink()

    workspace_actions, workspace_warnings, proposed_workspace_text = _normalize_workspace()
    for warning in workspace_warnings:
        warnings_found += 1
        print(f"WARNING {warning}")
    if not workspace_actions:
        print("OK .idea/workspace.xml: no changes")
    else:
        pending_changes += 1
        prefix = "APPLY" if args.apply else "DRY-RUN"
        for action in workspace_actions:
            print(f"{prefix} .idea/workspace.xml: {action}")
        if args.apply and proposed_workspace_text is not None:
            WORKSPACE_PATH.parent.mkdir(parents=True, exist_ok=True)
            WORKSPACE_PATH.write_text(proposed_workspace_text, encoding="UTF-8", newline="\n")

    for iml_path in iml_files:
        actions, warnings, proposed_text = _normalize_iml(iml_path, transient_paths, declared_modules)
        relative_path = iml_path.relative_to(REPO_ROOT).as_posix()
        for warning in warnings:
            warnings_found += 1
            print(f"WARNING {relative_path}: {warning}")
        if not actions:
            print(f"OK {relative_path}: no changes")
            continue

        pending_changes += 1
        prefix = "APPLY" if args.apply else "DRY-RUN"
        for action in actions:
            print(f"{prefix} {relative_path}: {action}")
        if args.apply and proposed_text is not None:
            iml_path.write_text(proposed_text, encoding="UTF-8", newline="\n")

    for spec in CANONICAL_RUN_CONFIGS:
        path, actions, proposed_text = _normalize_run_config(spec, run_configs_by_name)
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if not actions:
            print(f"OK {relative_path}: no changes")
            continue

        pending_changes += 1
        prefix = "APPLY" if args.apply else "DRY-RUN"
        for action in actions:
            print(f"{prefix} {relative_path}: {action}")
        if args.apply and proposed_text is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(proposed_text, encoding="UTF-8", newline="\n")

    if pending_changes == 0:
        print("No pending module metadata changes.")
    if warnings_found == 0:
        print("No metadata warnings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
