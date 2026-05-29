from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

EXTENSION_PACKAGES = {
    "epcsaft-equilibrium": {
        "directory": REPO_ROOT / "packages" / "epcsaft-equilibrium",
        "module": "epcsaft_equilibrium",
        "required_dependencies": {"numpy>=2.0"},
        "forbidden_dependencies": {"ceres", "epcsaft-regression"},
        "forbidden_reexports": {"Regression"},
        "native_module": "epcsaft_equilibrium._native_core",
        "build_option": "EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE=ON",
    },
    "epcsaft-regression": {
        "directory": REPO_ROOT / "packages" / "epcsaft-regression",
        "module": "epcsaft_regression",
        "required_dependencies": {"numpy>=2.0"},
        "forbidden_dependencies": {"ipopt", "epcsaft-equilibrium"},
        "forbidden_reexports": {"Equilibrium"},
        "native_module": "epcsaft_regression._native_core",
        "build_option": "EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE=ON",
    },
}

PROVIDER_PACKAGE_DIR = REPO_ROOT / "packages" / "epcsaft"


def _pyproject(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_provider_repo_uses_monorepo_extension_workspace_members() -> None:
    root = _pyproject(REPO_ROOT / "pyproject.toml")
    provider = _pyproject(PROVIDER_PACKAGE_DIR / "pyproject.toml")

    assert "project" not in root
    assert root["tool"]["uv"]["package"] is False
    assert provider["project"]["name"] == "epcsaft"
    assert root["tool"]["uv"]["workspace"]["members"] == [
        "packages/epcsaft",
        "packages/epcsaft-equilibrium",
        "packages/epcsaft-regression",
    ]
    assert "packages/epcsaft/src" in root["tool"]["pytest"]["ini_options"]["pythonpath"]
    assert "packages/epcsaft-equilibrium/src" in root["tool"]["pytest"]["ini_options"]["pythonpath"]
    assert "packages/epcsaft-regression/src" in root["tool"]["pytest"]["ini_options"]["pythonpath"]


def test_provider_package_owns_distribution_build_metadata() -> None:
    root = _pyproject(REPO_ROOT / "pyproject.toml")
    provider = _pyproject(PROVIDER_PACKAGE_DIR / "pyproject.toml")
    sdist_include = set(provider["tool"]["scikit-build"]["sdist"]["include"])

    assert "build-system" not in root
    assert "scikit-build" not in root.get("tool", {})
    assert provider["build-system"]["build-backend"] == "epcsaft_build_backend"
    assert provider["build-system"]["backend-path"] == ["build_backend"]
    assert provider["tool"]["scikit-build"]["cmake"]["source-dir"] == "."
    assert provider["tool"]["scikit-build"]["wheel"]["packages"] == ["src/epcsaft"]
    assert "CMakeLists.txt" in sdist_include
    assert "build_backend/*.py" in sdist_include
    assert "src/epcsaft/**/*.cpp" in sdist_include
    assert "src/epcsaft/**/*.h" in sdist_include
    assert "src/epcsaft/*.pyd" in provider["tool"]["scikit-build"]["sdist"]["exclude"]


def test_extension_package_manifests_depend_on_provider_workspace_source() -> None:
    for package_name, metadata in EXTENSION_PACKAGES.items():
        package_dir = metadata["directory"]
        pyproject = _pyproject(package_dir / "pyproject.toml")
        dependencies = set(pyproject["project"]["dependencies"])
        normalized_dependencies = {item.lower() for item in dependencies}

        assert pyproject["project"]["name"] == package_name
        assert "epcsaft==0.2.*" in dependencies
        assert metadata["required_dependencies"] <= dependencies
        assert pyproject["tool"]["uv"]["sources"]["epcsaft"] == {"workspace": True}
        assert metadata["forbidden_dependencies"].isdisjoint(normalized_dependencies)
        extension = pyproject["tool"]["epcsaft"]["extension"]
        assert extension["publish"] is False
        assert extension["monorepo_transition_only"] is True
        assert extension["requires_provider_native_sdk"] == "provider_native_sdk_v1"
        assert extension["native_module"] == metadata["native_module"]
        assert extension["build_option"] == metadata["build_option"]


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

    missing = sorted(path.relative_to(REPO_ROOT).as_posix() for path in expected_files if not path.is_file())
    assert missing == []
    assert not (PROVIDER_PACKAGE_DIR / "src" / "epcsaft" / "frontend" / "equilibrium.py").exists()
    assert not (PROVIDER_PACKAGE_DIR / "src" / "epcsaft" / "equilibrium").exists()


def test_equilibrium_extension_native_access_is_isolated_behind_package_native_bridge() -> None:
    module_dir = EXTENSION_PACKAGES["epcsaft-equilibrium"]["directory"] / "src" / "epcsaft_equilibrium"
    offenders: list[str] = []
    for path in sorted(module_dir.rglob("*.py")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if "epcsaft._core" in text and path.name != "_native.py":
            offenders.append(rel)

    native_bridge = (module_dir / "_native.py").read_text(encoding="utf-8")
    assert offenders == []
    assert "provider_native_sdk()" in native_bridge
    assert "provider_native_sdk_v1" in native_bridge
    assert "extension_native_core" in native_bridge
    assert "epcsaft_equilibrium._native_core" in native_bridge
    assert "equilibrium_native_enabled" not in native_bridge
    assert "EPCSAFT_ENABLE_EQUILIBRIUM_NATIVE=ON" not in native_bridge


def test_equilibrium_extension_native_bridge_rejects_extension_module_without_equilibrium_symbols(monkeypatch) -> None:
    import epcsaft_equilibrium._native as native_bridge

    monkeypatch.setattr(
        native_bridge,
        "provider_native_sdk",
        lambda: {
            "contract_id": "provider_native_sdk_v1",
            "native_contract_exported": True,
            "provider_only_core": True,
        },
    )
    monkeypatch.setattr(native_bridge, "import_module", lambda name: object())

    with pytest.raises(RuntimeError, match="epcsaft_equilibrium\\._native_core"):
        native_bridge.extension_native_core()


def test_regression_extension_native_bridge_rejects_extension_module_without_regression_symbols(monkeypatch) -> None:
    import epcsaft_regression.native_adapter as native_bridge

    monkeypatch.setattr(
        native_bridge,
        "provider_native_sdk",
        lambda: {
            "contract_id": "provider_native_sdk_v1",
            "native_contract_exported": True,
            "provider_only_core": True,
        },
    )
    monkeypatch.setattr(native_bridge, "import_module", lambda name: object())

    with pytest.raises(RuntimeError, match="epcsaft_regression\\._native_core"):
        native_bridge._regression_native_core()


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
        rel = path.relative_to(REPO_ROOT).as_posix()
        for fragment in forbidden_import_fragments:
            if fragment in text:
                offenders.append(f"{rel}: {fragment}")

    assert offenders == []
