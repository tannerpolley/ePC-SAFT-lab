from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

EXTENSION_PACKAGES = {
    "epcsaft-equilibrium": {
        "directory": REPO_ROOT / "packages" / "epcsaft-equilibrium",
        "module": "epcsaft_equilibrium",
        "forbidden_dependencies": {"ceres", "epcsaft-regression"},
        "forbidden_reexports": {"Equilibrium", "Regression"},
    },
    "epcsaft-regression": {
        "directory": REPO_ROOT / "packages" / "epcsaft-regression",
        "module": "epcsaft_regression",
        "forbidden_dependencies": {"ipopt", "epcsaft-equilibrium"},
        "forbidden_reexports": {"Equilibrium", "Regression"},
    },
}


def _pyproject(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_uv_workspace_names_extension_package_members() -> None:
    root = _pyproject(REPO_ROOT / "pyproject.toml")

    assert root["project"]["name"] == "epcsaft"
    assert root["tool"]["uv"]["workspace"]["members"] == [
        "packages/epcsaft-equilibrium",
        "packages/epcsaft-regression",
    ]


def test_extension_package_manifests_depend_on_provider_workspace_member() -> None:
    root_version = _pyproject(REPO_ROOT / "pyproject.toml")["project"]["version"]

    for package_name, metadata in EXTENSION_PACKAGES.items():
        package_dir = metadata["directory"]
        pyproject = _pyproject(package_dir / "pyproject.toml")
        dependencies = set(pyproject["project"]["dependencies"])
        normalized_dependencies = {item.lower() for item in dependencies}

        assert pyproject["project"]["name"] == package_name
        assert f"epcsaft=={root_version}" in dependencies
        assert pyproject["tool"]["uv"]["sources"]["epcsaft"] == {"workspace": True}
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
