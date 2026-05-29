from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_PATH = REPO_ROOT / "packages" / "epcsaft" / "build_backend" / "epcsaft_build_backend.py"
EQUILIBRIUM_BACKEND_PATH = (
    REPO_ROOT
    / "packages"
    / "epcsaft-equilibrium"
    / "build_backend"
    / "epcsaft_equilibrium_build_backend.py"
)
REGRESSION_BACKEND_PATH = (
    REPO_ROOT
    / "packages"
    / "epcsaft-regression"
    / "build_backend"
    / "epcsaft_regression_build_backend.py"
)


def _load_backend():
    spec = importlib.util.spec_from_file_location("epcsaft_build_backend_for_test", BACKEND_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pep517_build_backend_uses_isolated_build_dir_by_default(tmp_path, monkeypatch) -> None:
    backend = _load_backend()
    monkeypatch.setenv("TMP", str(tmp_path))
    monkeypatch.setenv("TEMP", str(tmp_path))
    monkeypatch.setenv("TMPDIR", str(tmp_path))

    config = backend._isolated_build_config(None)

    build_dir = Path(config["build-dir"])
    assert build_dir.exists()
    assert REPO_ROOT not in build_dir.parents
    assert build_dir.name.startswith("epcsaft-pep517-build-")


def test_pep517_build_backend_preserves_explicit_build_dir(tmp_path) -> None:
    backend = _load_backend()
    requested = tmp_path / "build"

    config = backend._isolated_build_config({"build-dir": str(requested)})

    assert config["build-dir"] == str(requested)


def test_pep517_build_backend_honors_persistent_build_dir_env(tmp_path, monkeypatch) -> None:
    backend = _load_backend()
    requested = tmp_path / "persistent"
    monkeypatch.setenv("EPCSAFT_PEP517_BUILD_DIR", str(requested))

    config = backend._isolated_build_config(None)

    assert Path(config["build-dir"]) == requested.resolve()
    assert requested.exists()


def test_pep517_build_backend_defaults_to_provider_only_native_config(tmp_path, monkeypatch) -> None:
    backend = _load_backend()
    monkeypatch.delenv("EPCSAFT_PEP517_CERES_DIR", raising=False)
    monkeypatch.delenv("EPCSAFT_PEP517_USE_SYSTEM_CERES", raising=False)
    monkeypatch.delenv("Ceres_DIR", raising=False)
    monkeypatch.delenv("EPCSAFT_PEP517_IPOPT_DIR", raising=False)
    monkeypatch.delenv("EPCSAFT_PEP517_IPOPT_ROOT", raising=False)
    monkeypatch.delenv("EPCSAFT_PEP517_ENABLE_IPOPT", raising=False)
    monkeypatch.delenv("EPCSAFT_PEP517_USE_SYSTEM_IPOPT", raising=False)
    monkeypatch.delenv("Ipopt_DIR", raising=False)
    monkeypatch.delenv("EPCSAFT_IPOPT_ROOT", raising=False)

    config = backend._isolated_build_config(None)

    assert config["cmake.define.EPCSAFT_ENABLE_CPPAD"] == "ON"
    assert config["cmake.define.EPCSAFT_ENABLE_CERES"] == "OFF"
    assert config["cmake.define.EPCSAFT_ENABLE_IPOPT"] == "OFF"
    assert config["cmake.define.EPCSAFT_USE_SYSTEM_IPOPT"] == "OFF"
    assert config["cmake.define.EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE"] == "OFF"
    assert config["cmake.define.EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE"] == "OFF"
    assert "cmake.define.EPCSAFT_USE_SYSTEM_CERES" not in config
    assert "cmake.define.Ceres_DIR" not in config
    assert "cmake.define.Ipopt_DIR" not in config
    assert "cmake.define.EPCSAFT_IPOPT_ROOT" not in config


def test_pep517_build_backend_allows_provider_build_without_ceres() -> None:
    backend = _load_backend()

    config = backend._isolated_build_config(
        {
            "cmake.define.EPCSAFT_ENABLE_CERES": "OFF",
            "cmake.define.EPCSAFT_ENABLE_IPOPT": "OFF",
        }
    )

    assert config["cmake.define.EPCSAFT_ENABLE_CERES"] == "OFF"
    assert config["cmake.define.EPCSAFT_ENABLE_CPPAD"] == "ON"
    assert config["cmake.define.EPCSAFT_ENABLE_IPOPT"] == "OFF"
    assert config["cmake.define.EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE"] == "OFF"
    assert config["cmake.define.EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE"] == "OFF"
    assert "cmake.define.EPCSAFT_USE_SYSTEM_CERES" not in config
    assert "cmake.define.Ceres_DIR" not in config


@pytest.mark.parametrize(
    ("key", "label"),
    [
        ("cmake.define.EPCSAFT_ENABLE_CERES", "Ceres"),
        ("cmake.define.EPCSAFT_ENABLE_IPOPT", "Ipopt"),
        ("cmake.define.EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE", "equilibrium native module"),
        ("cmake.define.EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE", "regression native module"),
    ],
)
def test_pep517_build_backend_rejects_extension_native_dependency_flags(key: str, label: str) -> None:
    backend = _load_backend()

    with pytest.raises(ValueError, match=label):
        backend._isolated_build_config({key: "ON"})


def test_pep517_build_backend_rejects_disabled_required_cppad() -> None:
    backend = _load_backend()

    with pytest.raises(ValueError, match="CppAD is required"):
        backend._isolated_build_config({"cmake.define.EPCSAFT_ENABLE_CPPAD": "OFF"})


def test_pep660_editable_hook_uses_isolated_build_dir(tmp_path, monkeypatch) -> None:
    backend = _load_backend()
    wheel_dir = tmp_path / "wheelhouse"
    wheel_dir.mkdir()
    captured = {}

    def fake_build_editable(wheel_directory, config_settings=None, metadata_directory=None):
        captured["wheel_directory"] = wheel_directory
        captured["config_settings"] = config_settings
        captured["metadata_directory"] = metadata_directory
        return "epcsaft-0.2.0-0.editable-py3-none-any.whl"

    monkeypatch.setattr(backend._scikit_build, "build_editable", fake_build_editable)

    result = backend.build_editable(str(wheel_dir), config_settings={"editable.mode": "redirect"})

    assert result == "epcsaft-0.2.0-0.editable-py3-none-any.whl"
    assert captured["wheel_directory"] == str(wheel_dir)
    assert captured["metadata_directory"] is None
    assert captured["config_settings"]["editable.mode"] == "redirect"
    build_dir = Path(captured["config_settings"]["build-dir"])
    assert build_dir.exists()
    assert REPO_ROOT not in build_dir.parents


def test_equilibrium_extension_backend_defaults_to_monorepo_provider_sdk_and_ipopt(monkeypatch, tmp_path) -> None:
    backend = _load_module(EQUILIBRIUM_BACKEND_PATH, "epcsaft_equilibrium_build_backend_for_test")
    monkeypatch.delenv("EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG", raising=False)
    monkeypatch.delenv("EPCSAFT_PROVIDER_SDK_MODE", raising=False)
    monkeypatch.setenv("EPCSAFT_PEP517_IPOPT_ROOT", str(tmp_path))

    config = backend._apply_build_config({"build-dir": str(tmp_path / "build")})

    assert config["cmake.define.EPCSAFT_ENABLE_CPPAD"] == "ON"
    assert config["cmake.define.EPCSAFT_ENABLE_IPOPT"] == "ON"
    assert config["cmake.define.EPCSAFT_USE_SYSTEM_IPOPT"] == "ON"
    assert config["cmake.define.EPCSAFT_IPOPT_ROOT"] == str(tmp_path.resolve())
    assert config["cmake.define.EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG"].endswith("epcsaft_provider_sdk.cmake")


def test_equilibrium_extension_backend_rejects_installed_mode_without_provider_sdk_config(tmp_path) -> None:
    backend = _load_module(EQUILIBRIUM_BACKEND_PATH, "epcsaft_equilibrium_build_backend_for_test")

    with pytest.raises(ValueError, match="installed provider SDK mode requires"):
        backend._apply_build_config({"build-dir": str(tmp_path / "build"), "epcsaft.provider-sdk-mode": "installed"})


def test_equilibrium_extension_editable_backend_does_not_require_ipopt(monkeypatch, tmp_path) -> None:
    backend = _load_module(EQUILIBRIUM_BACKEND_PATH, "epcsaft_equilibrium_build_backend_for_test")
    wheel_dir = tmp_path / "wheelhouse"
    wheel_dir.mkdir()
    captured = {}

    def fake_build_editable(wheel_directory, config_settings=None, metadata_directory=None):
        captured["wheel_directory"] = wheel_directory
        captured["config_settings"] = config_settings
        captured["metadata_directory"] = metadata_directory
        return "epcsaft_equilibrium-0.1.0-0.editable-py3-none-any.whl"

    monkeypatch.delenv("EPCSAFT_PEP517_IPOPT_ROOT", raising=False)
    monkeypatch.delenv("EPCSAFT_IPOPT_ROOT", raising=False)
    monkeypatch.setattr(backend._scikit_build, "build_editable", fake_build_editable)

    result = backend.build_editable(str(wheel_dir), config_settings={"build-dir": str(tmp_path / "build")})

    assert result.endswith(".whl")
    assert captured["wheel_directory"] == str(wheel_dir)
    assert captured["config_settings"]["cmake.define.EPCSAFT_BUILD_EXTENSION_NATIVE"] == "OFF"
    assert "cmake.define.EPCSAFT_IPOPT_ROOT" not in captured["config_settings"]


def test_regression_extension_backend_defaults_to_ceres_and_provider_sdk(tmp_path) -> None:
    backend = _load_module(REGRESSION_BACKEND_PATH, "epcsaft_regression_build_backend_for_test")

    config = backend._apply_build_config({"build-dir": str(tmp_path / "build")})

    assert config["cmake.define.EPCSAFT_ENABLE_CPPAD"] == "ON"
    assert config["cmake.define.EPCSAFT_ENABLE_CERES"] == "ON"
    assert config["cmake.define.EPCSAFT_ENABLE_IPOPT"] == "OFF"
    assert config["cmake.define.EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG"].endswith("epcsaft_provider_sdk.cmake")


def test_regression_extension_backend_uses_system_ceres_dir(monkeypatch, tmp_path) -> None:
    backend = _load_module(REGRESSION_BACKEND_PATH, "epcsaft_regression_build_backend_for_test")
    ceres_dir = tmp_path / "ceres"
    ceres_dir.mkdir()
    monkeypatch.setenv("EPCSAFT_PEP517_CERES_DIR", str(ceres_dir))

    config = backend._apply_build_config({"build-dir": str(tmp_path / "build")})

    assert config["cmake.define.EPCSAFT_USE_SYSTEM_CERES"] == "ON"
    assert config["cmake.define.Ceres_DIR"] == str(ceres_dir.resolve())


def test_regression_extension_editable_backend_disables_native_build(monkeypatch, tmp_path) -> None:
    backend = _load_module(REGRESSION_BACKEND_PATH, "epcsaft_regression_build_backend_for_test")
    wheel_dir = tmp_path / "wheelhouse"
    wheel_dir.mkdir()
    captured = {}

    def fake_build_editable(wheel_directory, config_settings=None, metadata_directory=None):
        captured["wheel_directory"] = wheel_directory
        captured["config_settings"] = config_settings
        captured["metadata_directory"] = metadata_directory
        return "epcsaft_regression-0.1.0-0.editable-py3-none-any.whl"

    monkeypatch.delenv("EPCSAFT_PEP517_CERES_DIR", raising=False)
    monkeypatch.delenv("Ceres_DIR", raising=False)
    monkeypatch.setattr(backend._scikit_build, "build_editable", fake_build_editable)

    result = backend.build_editable(str(wheel_dir), config_settings={"build-dir": str(tmp_path / "build")})

    assert result.endswith(".whl")
    assert captured["wheel_directory"] == str(wheel_dir)
    assert captured["config_settings"]["cmake.define.EPCSAFT_BUILD_EXTENSION_NATIVE"] == "OFF"
    assert "cmake.define.Ceres_DIR" not in captured["config_settings"]
