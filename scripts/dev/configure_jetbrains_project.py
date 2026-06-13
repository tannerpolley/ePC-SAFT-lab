from __future__ import annotations

import argparse
import io
import json
import shlex
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

from jetbrains_run_manifest import (
    CANONICAL_RUN_CONFIGS,
    POWERSHELL_RUNNER,
    PYTHON_RUNNER,
    SHELL_RUNNER,
    RunConfigSpec,
    UV_RUNNER,
    canonical_run_config_names,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
IDEA_DIR = REPO_ROOT / ".idea"
WORKSPACE_PATH = IDEA_DIR / "workspace.xml"
RUN_DIR = REPO_ROOT / ".run"
RUN_WORKING_DIRECTORY = REPO_ROOT.as_posix()
MODULE_URL_PREFIX = "file://$MODULE_DIR$"
CONTENT_URL = MODULE_URL_PREFIX
MODULE_DIR_MACRO = "$MODULE_DIR$"
PROJECT_NAME = "ePC-SAFT"
PROVIDER_MODULE_NAME = "epcsaft"
LEGACY_PROVIDER_MODULE_NAME = PROJECT_NAME
EQUILIBRIUM_MODULE_NAME = "epcsaft-equilibrium"
REGRESSION_MODULE_NAME = "epcsaft-regression"
PYTHON_CONFIG_TYPE = "PythonConfigurationType"
SHELL_CONFIG_TYPE = "ShConfigurationType"
POWERSHELL_CONFIG_TYPE = "PowerShellRunType"
UV_RUN_CONFIG_TYPE = "UvRunConfigurationType"
CMAKE_CONFIG_TYPE = "CMakeRunConfiguration"
PYTEST_CONFIG_TYPE = "tests"
MANAGED_RUN_CONFIG_TYPES = (PYTHON_CONFIG_TYPE, SHELL_CONFIG_TYPE, POWERSHELL_CONFIG_TYPE, UV_RUN_CONFIG_TYPE)
RUN_DASHBOARD_CONFIG_TYPES = (POWERSHELL_CONFIG_TYPE, UV_RUN_CONFIG_TYPE)
RUN_CONFIG_EXECUTOR_PREFIXES = (
    "Python.",
    "Shell Script.",
    "PowerShell.",
    "PowerShellRunType.",
    "UvRunConfigurationType.",
    "uv run.",
)
CMAKE_EXECUTION_TARGET_PREFIX = "CMakeBuildProfile:"
CMAKE_ACTIVE_PROFILE = "dev-native"
CMAKE_ACTIVE_PROFILE_DISPLAY_NAME = "IDE dev build (Windows Ninja)"
CMAKE_ACTIVE_PROFILE_GENERATION_DIR = "$PROJECT_DIR$/build/dev"
STALE_CMAKE_PROFILE_NAMES = frozenset({"ePC-SAFT dev MinGW"})
PYTHON_SDK_HOME = "$MODULE_DIR$/.venv/Scripts/python.exe"
PYTHON_SDK_NAME = "uv (ePC-SAFT)"
PYTHON_VIRTUAL_ENV = str(REPO_ROOT / ".venv")
POWERSHELL_INTERPRETER = "C:/Program Files/PowerShell/7/pwsh.exe"
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
PROVIDER_SOURCE_ROOTS: tuple[tuple[str, bool], ...] = (("packages/epcsaft/src", False),)


@dataclass(frozen=True)
class ModuleSpec:
    name: str
    iml_path: Path
    module_type: str
    content_root: str
    source_roots: tuple[tuple[str, bool], ...]
    exclude_roots: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()


CANONICAL_PYTHON_MODULES: tuple[ModuleSpec, ...] = (
    ModuleSpec(
        name=PROVIDER_MODULE_NAME,
        iml_path=IDEA_DIR / f"{PROVIDER_MODULE_NAME}.iml",
        module_type="PYTHON_MODULE",
        content_root="packages/epcsaft",
        source_roots=PROVIDER_SOURCE_ROOTS,
    ),
    ModuleSpec(
        name=EQUILIBRIUM_MODULE_NAME,
        iml_path=IDEA_DIR / f"{EQUILIBRIUM_MODULE_NAME}.iml",
        module_type="PYTHON_MODULE",
        content_root="packages/epcsaft-equilibrium",
        source_roots=(("packages/epcsaft-equilibrium/src", False),),
        dependencies=(PROVIDER_MODULE_NAME,),
    ),
    ModuleSpec(
        name=REGRESSION_MODULE_NAME,
        iml_path=IDEA_DIR / f"{REGRESSION_MODULE_NAME}.iml",
        module_type="PYTHON_MODULE",
        content_root="packages/epcsaft-regression",
        source_roots=(("packages/epcsaft-regression/src", False),),
        dependencies=(PROVIDER_MODULE_NAME,),
    ),
)


def _runtime_python_modules(transient_paths: tuple[str, ...]) -> tuple[ModuleSpec, ...]:
    return CANONICAL_PYTHON_MODULES


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
        "--check",
        action="store_true",
        help="Report pending changes and exit nonzero if metadata is not normalized.",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite module files in place.",
    )
    return parser


def _mode_prefix(args: argparse.Namespace) -> str:
    if args.apply:
        return "APPLY"
    if args.check:
        return "CHECK"
    return "DRY-RUN"


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


def _is_stale_legacy_project_cpp_iml(path: Path) -> bool:
    if path != IDEA_DIR / f"{LEGACY_PROVIDER_MODULE_NAME}.iml":
        return False
    try:
        module_root = ET.parse(path).getroot()
    except ET.ParseError:
        return False
    if module_root.tag != "module" or module_root.get("type") != "CPP_MODULE":
        return False
    manager = _find_child(module_root, "component", name="NewModuleRootManager")
    if manager is None:
        return False
    return manager.find("content") is None


def _existing_non_python_module_paths() -> tuple[Path, ...]:
    paths: list[Path] = []
    for path in sorted(IDEA_DIR.glob("*.iml")):
        if path in {spec.iml_path for spec in CANONICAL_PYTHON_MODULES}:
            continue
        if not path.exists():
            continue
        if _is_stale_legacy_project_cpp_iml(path):
            continue
        try:
            module_root = ET.parse(path).getroot()
        except ET.ParseError:
            paths.append(path)
            continue
        if module_root.get("type") != "PYTHON_MODULE":
            paths.append(path)
    return tuple(paths)


def _legacy_provider_iml_path() -> Path:
    return IDEA_DIR / f"{LEGACY_PROVIDER_MODULE_NAME}.iml"


def _is_owned_legacy_provider_iml(path: Path) -> bool:
    if not path.exists() or path == IDEA_DIR / f"{PROVIDER_MODULE_NAME}.iml":
        return False
    try:
        module_root = ET.parse(path).getroot()
    except ET.ParseError:
        return False
    if module_root.tag != "module" or module_root.get("type") != "PYTHON_MODULE":
        return False

    manager = _find_child(module_root, "component", name="NewModuleRootManager")
    if manager is None:
        return False
    content = _find_child(manager, "content", url=_module_url("packages/epcsaft"))
    if content is None:
        return False

    source_roots = {
        (source.get("url"), "true" if source.get("isTestSource") == "true" else "false")
        for source in content.findall("sourceFolder")
    }
    if source_roots != {(f"{MODULE_URL_PREFIX}/packages/epcsaft/src", "false")}:
        return False

    jdk = _find_child(manager, "orderEntry", type="jdk", jdkName=PYTHON_SDK_NAME, jdkType="Python SDK")
    return jdk is not None


def _find_child(parent: ET.Element, tag: str, **attrs: str) -> ET.Element | None:
    for child in parent.findall(tag):
        if all(child.get(key) == value for key, value in attrs.items()):
            return child
    return None


def _qualified_run_config_name(value: str | None) -> str | None:
    if value is None:
        return None
    for prefix in RUN_CONFIG_EXECUTOR_PREFIXES:
        if value.startswith(prefix):
            return value[len(prefix) :]
    return None


def _prune_run_manager_items(
    run_manager: ET.Element | None,
    active_run_manager_names: set[str],
    actions: list[str],
) -> None:
    if run_manager is None:
        return
    for run_list in run_manager.findall("list"):
        for item in list(run_list.findall("item")):
            itemvalue = item.get("itemvalue")
            name = _qualified_run_config_name(itemvalue)
            if name is None or name in active_run_manager_names:
                continue
            run_list.remove(item)
            actions.append(f"remove stale run manager item {itemvalue}")


def _prune_run_dashboard_statuses(
    dashboard: ET.Element,
    active_run_manager_names: set[str],
    actions: list[str],
) -> None:
    statuses = _find_child(dashboard, "option", name="configurationStatuses")
    if statuses is None:
        return
    for type_entry in statuses.findall("./map/entry"):
        config_type = type_entry.get("key")
        if config_type not in RUN_DASHBOARD_CONFIG_TYPES:
            continue
        status_map = type_entry.find("./value/map")
        if status_map is None:
            continue
        for status_entry in list(status_map.findall("entry")):
            name = status_entry.get("key")
            if not name or name in active_run_manager_names:
                continue
            status_map.remove(status_entry)
            actions.append(f"remove stale configuration status {config_type}.{name}")


def _prune_run_dashboard_disallowed_types(dashboard: ET.Element, actions: list[str]) -> None:
    statuses = _find_child(dashboard, "option", name="configurationStatuses")
    if statuses is None:
        return
    status_parent = statuses.find("./map")
    if status_parent is None:
        return
    for type_entry in list(status_parent.findall("entry")):
        config_type = type_entry.get("key")
        if config_type and config_type not in RUN_DASHBOARD_CONFIG_TYPES:
            status_parent.remove(type_entry)
            actions.append(f"remove Services configuration statuses for {config_type}")


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


def _ensure_content_root(manager: ET.Element, content_root: str, actions: list[str]) -> ET.Element:
    content_url = _module_url(content_root)
    content = _find_child(manager, "content", url=content_url)
    if content is not None:
        return content

    first_content = manager.find("content")
    if first_content is not None:
        if first_content.get("url") != content_url:
            first_content.set("url", content_url)
            actions.append(f"set content root to {content_url}")
        return first_content

    content = ET.Element("content", {"url": content_url})
    insert_at = 1 if manager.find("exclude-output") is not None else 0
    manager.insert(insert_at, content)
    actions.append(f"create content root {content_url}")
    return content


def _ensure_order_entries(manager: ET.Element, spec: ModuleSpec, declared_modules: set[str], actions: list[str]) -> None:
    for entry in list(manager.findall("orderEntry")):
        entry_type = entry.get("type")
        if entry_type == "inheritedJdk":
            manager.remove(entry)
            actions.append("remove inheritedJdk orderEntry")
        elif entry_type == "jdk" and (
            entry.get("jdkName") != PYTHON_SDK_NAME or entry.get("jdkType") != "Python SDK"
        ):
            manager.remove(entry)
            actions.append("remove stale Python SDK orderEntry")

    if _find_child(manager, "orderEntry", type="jdk", jdkName=PYTHON_SDK_NAME, jdkType="Python SDK") is None:
        manager.append(ET.Element("orderEntry", {"type": "jdk", "jdkName": PYTHON_SDK_NAME, "jdkType": "Python SDK"}))
        actions.append(f"add Python SDK orderEntry {PYTHON_SDK_NAME}")

    if _find_child(manager, "orderEntry", type="sourceFolder") is None:
        manager.append(ET.Element("orderEntry", {"type": "sourceFolder", "forTests": "false"}))
        actions.append("add sourceFolder orderEntry")

    desired_dependencies = set(spec.dependencies)
    for entry in list(manager.findall("orderEntry")):
        if entry.get("type") != "module":
            continue
        module_name = entry.get("module-name")
        if module_name not in desired_dependencies:
            manager.remove(entry)
            actions.append(f"remove stale module dependency {module_name}")
            continue
        desired_dependencies.remove(module_name)

    for module_name in spec.dependencies:
        if module_name not in declared_modules:
            continue
        if _find_child(manager, "orderEntry", type="module", **{"module-name": module_name}) is not None:
            continue
        manager.append(ET.Element("orderEntry", {"type": "module", "module-name": module_name}))
        actions.append(f"add module dependency {module_name}")


def _replace_content_roots(
    content: ET.Element,
    source_roots: tuple[tuple[str, bool], ...],
    exclude_roots: tuple[str, ...],
    actions: list[str],
) -> None:
    existing_source_folders = list(content.findall("sourceFolder"))
    existing_exclude_folders = list(content.findall("excludeFolder"))
    preserved_children = [child for child in list(content) if child.tag not in {"sourceFolder", "excludeFolder"}]
    canonical_source_keys = {
        (_module_url(relative_path), "true" if is_test else "false")
        for relative_path, is_test in source_roots
    }

    desired_sources: dict[tuple[str, str], ET.Element] = {}
    for source in existing_source_folders:
        url = source.get("url")
        is_test = "true" if source.get("isTestSource") == "true" else "false"
        if any(_is_under_path(url, path) for path in exclude_roots):
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

    for relative_path, is_test in source_roots:
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
                for relative_path in exclude_roots
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

    for relative_path in exclude_roots:
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


def _load_or_new_project_tree(path: Path) -> tuple[ET.ElementTree, str]:
    if path.exists():
        original_text = path.read_text(encoding="UTF-8")
        return ET.ElementTree(ET.fromstring(original_text)), original_text
    return ET.ElementTree(ET.Element("project", {"version": "4"})), ""


def _desired_module_paths() -> tuple[Path, ...]:
    paths = [spec.iml_path for spec in CANONICAL_PYTHON_MODULES]
    paths.extend(_existing_non_python_module_paths())
    return tuple(sorted(path for path in paths if path.exists() or path in {spec.iml_path for spec in CANONICAL_PYTHON_MODULES}))


def _module_file_attributes(path: Path) -> tuple[str, str]:
    relative = path.relative_to(REPO_ROOT).as_posix()
    return f"file://$PROJECT_DIR$/{relative}", f"$PROJECT_DIR$/{relative}"


def _normalize_modules_xml() -> tuple[list[str], list[str], str | None]:
    modules_path = IDEA_DIR / "modules.xml"
    try:
        tree, original_text = _load_or_new_project_tree(modules_path)
    except ET.ParseError as exc:
        return [], [f".idea/modules.xml: invalid XML ({exc})"], None

    root = tree.getroot()
    if root.tag != "project":
        return [], [".idea/modules.xml: root element is not <project>"], None

    actions: list[str] = []
    manager = _find_child(root, "component", name="ProjectModuleManager")
    if manager is None:
        manager = ET.Element("component", {"name": "ProjectModuleManager"})
        root.append(manager)
        actions.append("create ProjectModuleManager component")

    modules = manager.find("modules")
    if modules is None:
        modules = ET.Element("modules")
        manager.append(modules)
        actions.append("create modules list")

    desired_paths = _desired_module_paths()
    desired_filepaths = {_module_file_attributes(path)[1] for path in desired_paths}
    existing_by_filepath = {
        module.get("filepath"): module
        for module in modules.findall("module")
        if module.get("filepath")
    }

    for module in list(modules.findall("module")):
        filepath = module.get("filepath")
        if filepath in desired_filepaths:
            continue
        modules.remove(module)
        actions.append(f"remove stale module {filepath or module.get('fileurl') or '<unnamed>'}")

    for path in desired_paths:
        fileurl, filepath = _module_file_attributes(path)
        module = existing_by_filepath.get(filepath)
        if module is None:
            modules.append(ET.Element("module", {"fileurl": fileurl, "filepath": filepath}))
            actions.append(f"add module {filepath}")
            continue
        if module.get("fileurl") != fileurl:
            module.set("fileurl", fileurl)
            actions.append(f"set module fileurl {filepath}")

    sorted_modules = sorted(list(modules.findall("module")), key=lambda element: element.get("filepath", ""))
    for child in list(modules):
        modules.remove(child)
    for module in sorted_modules:
        modules.append(module)

    proposed_text = _serialize_tree(tree)
    if proposed_text == original_text:
        actions = []
    return actions, [], proposed_text if proposed_text != original_text else None


def _normalize_vcs_xml() -> tuple[list[str], list[str], str | None]:
    vcs_path = IDEA_DIR / "vcs.xml"
    try:
        tree, original_text = _load_or_new_project_tree(vcs_path)
    except ET.ParseError as exc:
        return [], [f".idea/vcs.xml: invalid XML ({exc})"], None

    root = tree.getroot()
    if root.tag != "project":
        return [], [".idea/vcs.xml: root element is not <project>"], None

    actions: list[str] = []
    component = _find_child(root, "component", name="VcsDirectoryMappings")
    if component is None:
        component = ET.Element("component", {"name": "VcsDirectoryMappings"})
        root.append(component)
        actions.append("create VcsDirectoryMappings component")

    desired = {("$PROJECT_DIR$", "Git")}
    existing = {(mapping.get("directory"), mapping.get("vcs")) for mapping in component.findall("mapping")}
    if existing != desired:
        for mapping in list(component.findall("mapping")):
            component.remove(mapping)
        component.append(ET.Element("mapping", {"directory": "$PROJECT_DIR$", "vcs": "Git"}))
        actions.append("set VCS mapping to project root only")

    proposed_text = _serialize_tree(tree)
    if proposed_text == original_text:
        actions = []
    return actions, [], proposed_text if proposed_text != original_text else None


def _normalize_py_source_root_detection_xml() -> tuple[list[str], list[str], str | None]:
    path = IDEA_DIR / "pySourceRootDetection.xml"
    if not path.exists():
        return [], [], None
    try:
        tree, original_text = _load_or_new_project_tree(path)
    except ET.ParseError as exc:
        return [], [f".idea/pySourceRootDetection.xml: invalid XML ({exc})"], None

    root = tree.getroot()
    if root.tag != "project":
        return [], [".idea/pySourceRootDetection.xml: root element is not <project>"], None

    actions: list[str] = []
    component = _find_child(root, "component", name="PySourceRootDetectionService")
    if component is None:
        return [], [], None
    source_paths = _find_child(component, "option", name="sourcePathsSet")
    if source_paths is None:
        return [], [], None
    current_set = source_paths.find("set")
    if current_set is not None and len(list(current_set)) > 0:
        for child in list(current_set):
            current_set.remove(child)
        actions.append("clear stale Python source-root detection paths")

    proposed_text = _serialize_tree(tree)
    if proposed_text == original_text:
        actions = []
    return actions, [], proposed_text if proposed_text != original_text else None


def _load_workspace_tree() -> tuple[ET.ElementTree, str]:
    if WORKSPACE_PATH.exists():
        original_text = WORKSPACE_PATH.read_text(encoding="UTF-8")
        return ET.ElementTree(ET.fromstring(original_text)), original_text
    return ET.ElementTree(ET.Element("project", {"version": "4"})), ""


def _run_manager_item_matches_name(itemvalue: str | None, name: str) -> bool:
    if not itemvalue:
        return False
    return itemvalue == name or itemvalue.endswith(f".{name}") or itemvalue.endswith(name)


def _remove_run_manager_item_values(run_manager: ET.Element | None, names: set[str], actions: list[str]) -> None:
    if run_manager is None or not names:
        return
    for list_tag in ("list", "recent_temporary/list"):
        for run_list in run_manager.findall(list_tag):
            for item in list(run_list.findall("item")):
                itemvalue = item.get("itemvalue")
                if not any(_run_manager_item_matches_name(itemvalue, name) for name in names):
                    continue
                run_list.remove(item)
                actions.append(f"remove generated run manager item {itemvalue}")


def _remove_stale_run_manager_items_for_specs(
    run_manager: ET.Element | None,
    specs: tuple[RunConfigSpec, ...],
    actions: list[str],
) -> None:
    if run_manager is None:
        return

    specs_by_name = {spec.name: spec for spec in specs}
    for list_tag in ("list", "recent_temporary/list"):
        for run_list in run_manager.findall(list_tag):
            for item in list(run_list.findall("item")):
                itemvalue = item.get("itemvalue")
                name = _qualified_run_config_name(itemvalue)
                if not itemvalue or not name:
                    continue
                spec = specs_by_name.get(name)
                if spec is None:
                    continue
                if itemvalue.startswith(_run_config_executor_prefixes(spec)):
                    continue
                run_list.remove(item)
                actions.append(f"remove stale run manager item {itemvalue}")


def _clear_stale_selected_run_manager_item(
    run_manager: ET.Element | None,
    specs: tuple[RunConfigSpec, ...],
    actions: list[str],
) -> None:
    if run_manager is None:
        return
    selected = run_manager.get("selected")
    if not selected:
        return
    selected_name = _qualified_run_config_name(selected)
    if selected_name is None:
        return
    specs_by_name = {spec.name: spec for spec in specs}
    selected_spec = specs_by_name.get(selected_name)
    if selected_spec is None or selected.startswith(_run_config_executor_prefixes(selected_spec)):
        return
    del run_manager.attrib["selected"]
    actions.append(f"clear stale selected run configuration {selected}")


def _remove_executor_properties_for_names(properties: dict[str, object], names: set[str], actions: list[str]) -> None:
    key_to_string = properties.get("keyToString")
    if not isinstance(key_to_string, dict):
        return
    for key in list(key_to_string):
        if not key.endswith(".executor"):
            continue
        if any(name in key for name in names):
            del key_to_string[key]
            actions.append(f"remove generated executor property {key}")


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
    canonical_names = canonical_run_config_names()
    removed_run_manager_names: list[str] = []
    run_manager = _find_child(root, "component", name="RunManager")
    if run_manager is not None:
        for config in list(run_manager.findall("configuration")):
            name = config.get("name")
            if (
                name in canonical_names
                and config.get("default") != "true"
                and config.get("type") in MANAGED_RUN_CONFIG_TYPES
                and config.get("type") != _run_config_type(next(spec for spec in CANONICAL_RUN_CONFIGS if spec.name == name))
            ):
                run_manager.remove(config)
                removed_name = name or "<unnamed>"
                removed_run_manager_names.append(removed_name)
                actions.append(f"remove stale local run configuration {removed_name}")
                continue
            if (
                config.get("temporary") == "true"
                and config.get("nameIsGenerated") == "true"
                and config.get("type") in (*MANAGED_RUN_CONFIG_TYPES, PYTEST_CONFIG_TYPE)
                and name not in canonical_names
            ):
                run_manager.remove(config)
                removed_name = name or "<unnamed>"
                removed_run_manager_names.append(removed_name)
                actions.append(f"remove temporary generated run configuration {removed_name}")
        selected = run_manager.get("selected")
        if selected and any(selected.endswith(f".{name}") for name in removed_run_manager_names):
            del run_manager.attrib["selected"]
            actions.append("clear stale selected temporary run configuration")
        _remove_run_manager_item_values(run_manager, set(removed_run_manager_names), actions)
        _remove_stale_run_manager_items_for_specs(run_manager, CANONICAL_RUN_CONFIGS, actions)
        _clear_stale_selected_run_manager_item(run_manager, CANONICAL_RUN_CONFIGS, actions)
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
            _remove_executor_properties_for_names(properties, set(removed_run_manager_names), actions)
            key_to_string = properties.get("keyToString")
            if isinstance(key_to_string, dict):
                for key in list(key_to_string):
                    if not key.endswith(".executor"):
                        continue
                    name = _qualified_run_config_name(key[: -len(".executor")])
                    if name is None:
                        continue
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
    for child in list(values.findall("option")):
        config_type = child.get("value")
        if config_type and config_type not in RUN_DASHBOARD_CONFIG_TYPES:
            values.remove(child)
            actions.append(f"disable Services Run Dashboard for {config_type}")
    for config_type in RUN_DASHBOARD_CONFIG_TYPES:
        if config_type in existing_values:
            continue
        values.append(ET.Element("option", {"value": config_type}))
        actions.append(f"enable Services Run Dashboard for {config_type}")

    _prune_run_manager_items(run_manager, active_run_manager_names, actions)
    _prune_run_dashboard_statuses(dashboard, active_run_manager_names, actions)
    _prune_run_dashboard_disallowed_types(dashboard, actions)
    _normalize_cmake_workspace(root, actions)

    if not actions:
        return [], [], None

    proposed_text = _serialize_tree(tree)
    return actions, [], proposed_text if proposed_text != original_text else None


def _normalize_cmake_workspace(root: ET.Element, actions: list[str]) -> None:
    cmake_settings = _find_child(root, "component", name="CMakeSettings")
    if cmake_settings is None:
        cmake_settings = ET.Element(
            "component",
            {"name": "CMakeSettings", "AUTO_RELOAD": "true"},
        )
        root.append(cmake_settings)
        actions.append("create CMakeSettings component")
    elif cmake_settings.get("AUTO_RELOAD") != "true":
        cmake_settings.set("AUTO_RELOAD", "true")
        actions.append("enable CMake auto reload")

    configurations = cmake_settings.find("configurations")
    if configurations is None:
        configurations = ET.Element("configurations")
        cmake_settings.append(configurations)
        actions.append("create CMakeSettings configurations")

    active_config = _find_child(configurations, "configuration", PROFILE_NAME=CMAKE_ACTIVE_PROFILE)
    if active_config is None:
        active_config = ET.Element(
            "configuration",
            {
                "PROFILE_NAME": CMAKE_ACTIVE_PROFILE,
                "PROFILE_DISPLAY_NAME": CMAKE_ACTIVE_PROFILE_DISPLAY_NAME,
                "ENABLED": "true",
                "FROM_PRESET": "true",
                "GENERATION_DIR": CMAKE_ACTIVE_PROFILE_GENERATION_DIR,
            },
        )
        configurations.append(active_config)
        actions.append(f"create CMake profile {CMAKE_ACTIVE_PROFILE}")

    for config in list(configurations.findall("configuration")):
        profile_name = config.get("PROFILE_NAME")
        if profile_name in STALE_CMAKE_PROFILE_NAMES:
            configurations.remove(config)
            actions.append(f"remove stale CMake profile {profile_name}")

    for config in configurations.findall("configuration"):
        profile_name = config.get("PROFILE_NAME") or "<unnamed>"
        expected_enabled = "true" if profile_name == CMAKE_ACTIVE_PROFILE else "false"
        if config.get("ENABLED") != expected_enabled:
            config.set("ENABLED", expected_enabled)
            action = "enable" if expected_enabled == "true" else "disable"
            actions.append(f"{action} CMake profile {profile_name}")

    execution_target_manager = _find_child(root, "component", name="ExecutionTargetManager")
    if execution_target_manager is None:
        return
    selected_target = execution_target_manager.get("SELECTED_TARGET")
    stale_targets = {
        f"{CMAKE_EXECUTION_TARGET_PREFIX}{profile_name}"
        for profile_name in STALE_CMAKE_PROFILE_NAMES
    }
    if selected_target in stale_targets:
        del execution_target_manager.attrib["SELECTED_TARGET"]
        actions.append(f"clear stale CMake execution target {selected_target}")


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


def _powershell_script_url(relative_path: str) -> str:
    return _shell_script_path(relative_path)


def _uv_script_path(relative_path: str) -> str:
    return _shell_script_path(relative_path)


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
    if spec.runner == POWERSHELL_RUNNER:
        return POWERSHELL_CONFIG_TYPE
    if spec.runner == UV_RUNNER:
        return UV_RUN_CONFIG_TYPE
    raise ValueError(f"Unsupported run config runner: {spec.runner}")


def _run_config_factory_name(spec: RunConfigSpec) -> str:
    if spec.runner == UV_RUNNER:
        return UV_RUN_CONFIG_TYPE
    if spec.runner == POWERSHELL_RUNNER:
        return POWERSHELL_RUNNER
    return spec.runner


def _run_config_executor_prefixes(spec: RunConfigSpec) -> tuple[str, ...]:
    if spec.runner == PYTHON_RUNNER:
        return ("Python.",)
    if spec.runner == SHELL_RUNNER:
        return ("Shell Script.",)
    if spec.runner == POWERSHELL_RUNNER:
        return ("PowerShell.", "PowerShellRunType.")
    if spec.runner == UV_RUNNER:
        return ("UvRunConfigurationType.", "uv run.")
    raise ValueError(f"Unsupported run config runner: {spec.runner}")


def _python_configuration(spec: RunConfigSpec) -> ET.Element:
    attrs = {
        "default": "false",
        "name": spec.name,
        "type": PYTHON_CONFIG_TYPE,
        "factoryName": PYTHON_RUNNER,
        "folderName": spec.folder_name,
    }
    config = ET.Element(
        "configuration",
        attrs,
    )
    config.append(ET.Element("module", {"name": PROVIDER_MODULE_NAME}))
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


def _split_parameters(parameters: str) -> list[str]:
    if not parameters.strip():
        return []
    return shlex.split(parameters)


def _add_string_list_option(parent: ET.Element, name: str, values: list[str]) -> None:
    option = ET.Element("option", {"name": name})
    list_element = ET.Element("list")
    for value in values:
        list_element.append(ET.Element("option", {"value": value}))
    option.append(list_element)
    parent.append(option)


def _add_string_map_option(parent: ET.Element, name: str, values: dict[str, str]) -> None:
    option = ET.Element("option", {"name": name})
    map_element = ET.Element("map")
    for key, value in sorted(values.items()):
        map_element.append(ET.Element("entry", {"key": key, "value": value}))
    option.append(map_element)
    parent.append(option)


def _uv_configuration(spec: RunConfigSpec) -> ET.Element:
    attrs = {
        "default": "false",
        "name": spec.name,
        "type": UV_RUN_CONFIG_TYPE,
        "factoryName": UV_RUN_CONFIG_TYPE,
        "folderName": spec.folder_name,
    }
    config = ET.Element("configuration", attrs)
    _add_option(config, "runType", "SCRIPT")
    _add_option(config, "scriptOrModule", _uv_script_path(spec.command))
    _add_string_list_option(config, "args", _split_parameters(spec.parameters))
    _add_string_map_option(config, "env", {"PYTHONUNBUFFERED": "1", "VIRTUAL_ENV": PYTHON_VIRTUAL_ENV})
    _add_option(config, "checkSync", "false")
    _add_option(config, "uvSdkKey", PYTHON_SDK_NAME)
    _add_string_list_option(config, "uvArgs", ["--project", RUN_WORKING_DIRECTORY, "--no-sync"])
    _add_option(config, "debugJustMyCode", "false")
    config.append(ET.Element("method", {"v": "2"}))
    return config


def _powershell_configuration(spec: RunConfigSpec) -> ET.Element:
    attrs = {
        "default": "false",
        "name": spec.name,
        "type": POWERSHELL_CONFIG_TYPE,
        "factoryName": POWERSHELL_RUNNER,
        "folderName": spec.folder_name,
        "scriptUrl": _powershell_script_url(spec.command),
        "workingDirectory": RUN_WORKING_DIRECTORY,
        "commandOptions": "-NoProfile -ExecutionPolicy Bypass",
    }
    if spec.parameters:
        attrs["scriptParameters"] = spec.parameters
    config = ET.Element("configuration", attrs)
    config.append(ET.Element("method", {"v": "2"}))
    return config


def _path_option(parent: ET.Element, name: str, value: str) -> None:
    _add_option(parent, f"INDEPENDENT_{name}", "true")
    _add_option(parent, name, value)


def _shell_configuration(spec: RunConfigSpec) -> ET.Element:
    attrs = {
        "default": "false",
        "name": spec.name,
        "type": SHELL_CONFIG_TYPE,
        "factoryName": SHELL_RUNNER,
        "folderName": spec.folder_name,
    }
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
    if spec.runner == POWERSHELL_RUNNER:
        return _powershell_configuration(spec)
    if spec.runner == UV_RUNNER:
        return _uv_configuration(spec)
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


def _run_config_path(name: str) -> Path:
    safe_name = name.replace(":", " -")
    return RUN_DIR / f"{safe_name}.run.xml"


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
    if spec.runner == UV_RUNNER:
        return {
            "runType": "SCRIPT",
            "scriptOrModule": _uv_script_path(spec.command),
            "checkSync": "false",
            "uvSdkKey": PYTHON_SDK_NAME,
            "debugJustMyCode": "false",
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
    if spec.runner == POWERSHELL_RUNNER:
        return {}
    raise ValueError(f"Unsupported run config runner: {spec.runner}")


def _expected_attribute_values(spec: RunConfigSpec) -> dict[str, str]:
    if spec.runner == POWERSHELL_RUNNER:
        expected = {
            "scriptUrl": _powershell_script_url(spec.command),
            "workingDirectory": RUN_WORKING_DIRECTORY,
            "commandOptions": "-NoProfile -ExecutionPolicy Bypass",
        }
        if spec.parameters:
            expected["scriptParameters"] = spec.parameters
        return expected
    return {}


def _run_config_actions(spec: RunConfigSpec, current_config: ET.Element | None) -> list[str]:
    if current_config is None:
        return [f"create {spec.runner} run configuration"]

    actions: list[str] = []
    expected_type = _run_config_type(spec)
    if current_config.get("type") != expected_type:
        actions.append(f"set runner type to {spec.runner}")
    expected_factory_name = _run_config_factory_name(spec)
    if current_config.get("factoryName") != expected_factory_name:
        actions.append(f"set factoryName={expected_factory_name}")
    if current_config.get("folderName") != spec.folder_name:
        actions.append(f"set folderName={spec.folder_name}")
    if spec.runner == PYTHON_RUNNER:
        module = current_config.find("module")
        module_name = module.get("name") if module is not None else None
        if module_name != PROVIDER_MODULE_NAME:
            actions.append(f"set module={PROVIDER_MODULE_NAME}")
    for option_name, expected_value in _expected_option_values(spec).items():
        if _option_value(current_config, option_name) != expected_value:
            actions.append(f"set {option_name}={expected_value}")
    for attr_name, expected_value in _expected_attribute_values(spec).items():
        if current_config.get(attr_name) != expected_value:
            actions.append(f"set {attr_name}={expected_value}")
    return actions


def _normalize_run_config(
    spec: RunConfigSpec,
    existing_paths: dict[str, list[Path]],
) -> tuple[Path, list[str], str | None]:
    path = existing_paths.get(spec.name, [_run_config_path(spec.name)])[0]
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
    names = {spec.name for spec in CANONICAL_PYTHON_MODULES}
    for path in _existing_non_python_module_paths():
        names.add(path.stem)
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


def _load_module_tree(spec: ModuleSpec, actions: list[str]) -> tuple[ET.ElementTree, str]:
    if spec.iml_path.exists():
        return ET.parse(spec.iml_path), spec.iml_path.read_text(encoding="UTF-8")

    legacy_path = _legacy_provider_iml_path()
    if spec.name == PROVIDER_MODULE_NAME and _is_owned_legacy_provider_iml(legacy_path):
        actions.append(f"migrate legacy provider module {legacy_path.relative_to(REPO_ROOT).as_posix()}")
        return ET.parse(legacy_path), ""

    return ET.ElementTree(ET.Element("module", {"type": spec.module_type, "version": "4"})), ""


def _normalize_iml(
    spec: ModuleSpec, declared_modules: set[str]
) -> tuple[list[str], list[str], str | None]:
    iml_path = spec.iml_path
    actions: list[str] = []
    tree, original_text = _load_module_tree(spec, actions)
    module_root = tree.getroot()
    if module_root.get("type") != spec.module_type:
        module_root.set("type", spec.module_type)
        actions.append(f"set module type {spec.module_type}")
    if module_root.get("version") != "4":
        module_root.set("version", "4")
        actions.append("set module version 4")
    manager = _ensure_root_manager(module_root, actions)
    _ensure_exclude_output(manager, actions)
    content = _ensure_content_root(manager, spec.content_root, actions)
    _ensure_order_entries(manager, spec, declared_modules, actions)
    _replace_content_roots(content, spec.source_roots, spec.exclude_roots, actions)
    warnings = _module_dependency_warnings(iml_path, module_root, declared_modules)
    proposed_text = _serialize_tree(tree)
    if proposed_text == original_text:
        actions = []
    return actions, warnings, proposed_text if proposed_text != original_text else None


def _legacy_provider_cleanup() -> tuple[list[str], list[str], Path | None]:
    legacy_path = _legacy_provider_iml_path()
    if not legacy_path.exists():
        return [], [], None
    if _is_stale_legacy_project_cpp_iml(legacy_path):
        return [f"delete legacy provider module {legacy_path.relative_to(REPO_ROOT).as_posix()}"], [], legacy_path
    if not _is_owned_legacy_provider_iml(legacy_path):
        return [], [f"{legacy_path.relative_to(REPO_ROOT).as_posix()}: not deleting non-owned legacy provider module"], None
    return [f"delete legacy provider module {legacy_path.relative_to(REPO_ROOT).as_posix()}"], [], legacy_path


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    transient_paths = _existing_transient_paths()
    module_specs = _runtime_python_modules(transient_paths)
    declared_modules = _load_declared_modules()
    run_configs_by_name, run_config_warnings = _load_shared_run_config_paths()

    pending_changes = 0
    warnings_found = 0
    for warning in run_config_warnings:
        warnings_found += 1
        print(f"WARNING {warning}")

    canonical_names = canonical_run_config_names()
    for name, paths in sorted(run_configs_by_name.items()):
        if name not in canonical_names:
            for path in paths:
                pending_changes += 1
                relative_path = path.relative_to(REPO_ROOT).as_posix()
                prefix = _mode_prefix(args)
                print(f"{prefix} {relative_path}: delete stale shared run configuration")
                if args.apply:
                    path.unlink()
            continue
        for duplicate_path in paths[1:]:
            pending_changes += 1
            relative_path = duplicate_path.relative_to(REPO_ROOT).as_posix()
            prefix = _mode_prefix(args)
            print(f"{prefix} {relative_path}: delete duplicate shared run configuration '{name}'")
            if args.apply:
                duplicate_path.unlink()

    metadata_targets = (
        (".idea/modules.xml", _normalize_modules_xml()),
        (".idea/vcs.xml", _normalize_vcs_xml()),
        (".idea/pySourceRootDetection.xml", _normalize_py_source_root_detection_xml()),
    )
    for relative_name, (actions, warnings, proposed_text) in metadata_targets:
        for warning in warnings:
            warnings_found += 1
            print(f"WARNING {warning}")
        if not actions:
            print(f"OK {relative_name}: no changes")
            continue
        pending_changes += 1
        prefix = _mode_prefix(args)
        for action in actions:
            print(f"{prefix} {relative_name}: {action}")
        if args.apply and proposed_text is not None:
            target_path = REPO_ROOT / relative_name
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(proposed_text, encoding="UTF-8", newline="\n")

    workspace_actions, workspace_warnings, proposed_workspace_text = _normalize_workspace()
    for warning in workspace_warnings:
        warnings_found += 1
        print(f"WARNING {warning}")
    if not workspace_actions:
        print("OK .idea/workspace.xml: no changes")
    else:
        pending_changes += 1
        prefix = _mode_prefix(args)
        for action in workspace_actions:
            print(f"{prefix} .idea/workspace.xml: {action}")
        if args.apply and proposed_workspace_text is not None:
            WORKSPACE_PATH.parent.mkdir(parents=True, exist_ok=True)
            WORKSPACE_PATH.write_text(proposed_workspace_text, encoding="UTF-8", newline="\n")

    for spec in module_specs:
        actions, warnings, proposed_text = _normalize_iml(spec, declared_modules)
        relative_path = spec.iml_path.relative_to(REPO_ROOT).as_posix()
        for warning in warnings:
            warnings_found += 1
            print(f"WARNING {relative_path}: {warning}")
        if not actions:
            print(f"OK {relative_path}: no changes")
            continue

        pending_changes += 1
        prefix = _mode_prefix(args)
        for action in actions:
            print(f"{prefix} {relative_path}: {action}")
        if args.apply and proposed_text is not None:
            spec.iml_path.parent.mkdir(parents=True, exist_ok=True)
            spec.iml_path.write_text(proposed_text, encoding="UTF-8", newline="\n")

    legacy_actions, legacy_warnings, legacy_delete_path = _legacy_provider_cleanup()
    for warning in legacy_warnings:
        warnings_found += 1
        print(f"WARNING {warning}")
    if legacy_actions:
        pending_changes += 1
        prefix = _mode_prefix(args)
        for action in legacy_actions:
            print(f"{prefix} .idea/{LEGACY_PROVIDER_MODULE_NAME}.iml: {action}")
        if args.apply and legacy_delete_path is not None:
            legacy_delete_path.unlink()

    for spec in CANONICAL_RUN_CONFIGS:
        path, actions, proposed_text = _normalize_run_config(spec, run_configs_by_name)
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if not actions:
            print(f"OK {relative_path}: no changes")
            continue

        pending_changes += 1
        prefix = _mode_prefix(args)
        for action in actions:
            print(f"{prefix} {relative_path}: {action}")
        if args.apply and proposed_text is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(proposed_text, encoding="UTF-8", newline="\n")

    if pending_changes == 0:
        print("No pending module metadata changes.")
    if warnings_found == 0:
        print("No metadata warnings.")
    if args.check and (pending_changes or warnings_found):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
