from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_ROOT = REPO_ROOT.parent

EXTENSION_PACKAGES = {
    "epcsaft-equilibrium": {
        "directory": WORKSPACE_ROOT / "epcsaft-equilibrium",
        "module": "epcsaft_equilibrium",
        "required_dependencies": {"numpy>=2.0"},
        "forbidden_dependencies": {"ceres", "epcsaft-regression"},
        "forbidden_reexports": {"Regression"},
    },
    "epcsaft-regression": {
        "directory": WORKSPACE_ROOT / "epcsaft-regression",
        "module": "epcsaft_regression",
        "required_dependencies": {"numpy>=2.0"},
        "forbidden_dependencies": {"ipopt", "epcsaft-equilibrium"},
        "forbidden_reexports": {"Equilibrium"},
    },
}


def _pyproject(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_provider_repo_uses_sibling_extension_repos_instead_of_uv_workspace_members() -> None:
    root = _pyproject(REPO_ROOT / "pyproject.toml")

    assert root["project"]["name"] == "epcsaft"
    assert "workspace" not in root.get("tool", {}).get("uv", {})
    assert "../epcsaft-equilibrium/src" in root["tool"]["pytest"]["ini_options"]["pythonpath"]
    assert "../epcsaft-regression/src" in root["tool"]["pytest"]["ini_options"]["pythonpath"]


def test_extension_package_manifests_depend_on_provider_sibling_path_source() -> None:
    root_version = _pyproject(REPO_ROOT / "pyproject.toml")["project"]["version"]

    for package_name, metadata in EXTENSION_PACKAGES.items():
        package_dir = metadata["directory"]
        pyproject = _pyproject(package_dir / "pyproject.toml")
        dependencies = set(pyproject["project"]["dependencies"])
        normalized_dependencies = {item.lower() for item in dependencies}

        assert pyproject["project"]["name"] == package_name
        assert f"epcsaft=={root_version}" in dependencies
        assert metadata["required_dependencies"] <= dependencies
        assert pyproject["tool"]["uv"]["sources"]["epcsaft"] == {"path": "../ePC-SAFT", "editable": True}
        assert metadata["forbidden_dependencies"].isdisjoint(normalized_dependencies)


def test_extension_package_shells_do_not_reexport_transition_core_objects() -> None:
    for metadata in EXTENSION_PACKAGES.values():
        module = metadata["module"]
        init_file = metadata["directory"] / "src" / module / "__init__.py"
        text = init_file.read_text(encoding="utf-8")

        assert "epcsaft._core" not in text
        for name in metadata["forbidden_reexports"]:
            assert f"from epcsaft import {name}" not in text
            assert f"epcsaft.{name}" not in text


def test_equilibrium_extension_owns_python_workflow_modules() -> None:
    package_dir = EXTENSION_PACKAGES["epcsaft-equilibrium"]["directory"]
    module_dir = package_dir / "src" / "epcsaft_equilibrium"

    expected_files = {
        module_dir / "__init__.py",
        module_dir / "equilibrium.py",
        module_dir / "workflows.py",
        module_dir / "capabilities.py",
        module_dir / "_native.py",
        module_dir / "core" / "__init__.py",
        module_dir / "core" / "native_requests.py",
        module_dir / "core" / "native_results.py",
    }

    missing = sorted(path.relative_to(WORKSPACE_ROOT).as_posix() for path in expected_files if not path.is_file())
    assert missing == []
    assert not (REPO_ROOT / "src" / "epcsaft" / "frontend" / "equilibrium.py").exists()
    assert not (REPO_ROOT / "src" / "epcsaft" / "equilibrium").exists()


def test_equilibrium_extension_native_access_is_isolated_behind_provider_sdk_bridge() -> None:
    module_dir = EXTENSION_PACKAGES["epcsaft-equilibrium"]["directory"] / "src" / "epcsaft_equilibrium"
    offenders: list[str] = []
    for path in sorted(module_dir.rglob("*.py")):
        rel = path.relative_to(WORKSPACE_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if "epcsaft._core" in text and path.name != "_native.py":
            offenders.append(rel)

    native_bridge = (module_dir / "_native.py").read_text(encoding="utf-8")
    assert offenders == []
    assert "provider_native_sdk()" in native_bridge
    assert "provider_native_sdk_v1" in native_bridge


def test_equilibrium_extension_uses_public_provider_imports_only() -> None:
    module_dir = EXTENSION_PACKAGES["epcsaft-equilibrium"]["directory"] / "src" / "epcsaft_equilibrium"
    forbidden_import_fragments = (
        "from epcsaft._types import",
        "import epcsaft._types",
        "from epcsaft.frontend.mixture import",
        "import epcsaft.frontend.mixture",
    )
    offenders: list[str] = []
    for path in sorted(module_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(WORKSPACE_ROOT).as_posix()
        for fragment in forbidden_import_fragments:
            if fragment in text:
                offenders.append(f"{rel}: {fragment}")

    assert offenders == []
