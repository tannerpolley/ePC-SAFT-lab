from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_PATH = REPO_ROOT / "packages" / "epcsaft" / "build_backend" / "epcsaft_build_backend.py"
EQUILIBRIUM_BACKEND_PATH = (
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "build_backend" / "epcsaft_equilibrium_build_backend.py"
)
REGRESSION_BACKEND_PATH = (
    REPO_ROOT / "packages" / "epcsaft-regression" / "build_backend" / "epcsaft_regression_build_backend.py"
)
NATIVE_DEPENDENCY_POLICY_PATH = REPO_ROOT / "packages" / "epcsaft" / "build_backend" / "native_dependency_policy.py"
PACKAGE_BUILD_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "package-build-lanes.yml"
EQUILIBRIUM_PYPROJECT_PATH = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "pyproject.toml"
CPPAD_CMAKE_PATHS = (
    REPO_ROOT / "CMakeLists.txt",
    REPO_ROOT / "packages" / "epcsaft" / "CMakeLists.txt",
    REPO_ROOT / "packages" / "epcsaft-equilibrium" / "CMakeLists.txt",
    REPO_ROOT / "packages" / "epcsaft-regression" / "CMakeLists.txt",
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


def test_equilibrium_extension_build_repairs_linux_wheel_before_returning(monkeypatch, tmp_path) -> None:
    backend = _load_module(EQUILIBRIUM_BACKEND_PATH, "epcsaft_equilibrium_build_backend_for_test_repair")
    wheel_dir = tmp_path / "wheelhouse"
    wheel_dir.mkdir()
    raw_name = "epcsaft_equilibrium-0.1.0-cp313-cp313-linux_x86_64.whl"
    repaired_name = "epcsaft_equilibrium-0.1.0-cp313-cp313-manylinux_2_34_x86_64.whl"
    captured: dict[str, Path] = {}

    def fake_build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
        raw_dir = Path(wheel_directory)
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_wheel = raw_dir / raw_name
        raw_wheel.write_bytes(b"raw wheel")
        captured["raw_dir"] = raw_dir
        captured["raw_wheel"] = raw_wheel
        return raw_name

    def fake_repair_linux_wheel(raw_wheel: Path, output_dir: Path) -> str:
        assert raw_wheel.read_bytes() == b"raw wheel"
        assert output_dir == wheel_dir
        (output_dir / repaired_name).write_bytes(b"repaired wheel")
        captured["repair_input"] = raw_wheel
        return repaired_name

    monkeypatch.setattr(backend._scikit_build, "build_wheel", fake_build_wheel)
    monkeypatch.setattr(backend, "_repair_linux_wheel", fake_repair_linux_wheel)

    result = backend.build_wheel(str(wheel_dir), config_settings={"build-dir": str(tmp_path / "build")})

    assert result == repaired_name
    assert captured["raw_dir"] != wheel_dir
    assert captured["repair_input"] == captured["raw_wheel"]
    assert not captured["raw_dir"].exists()
    assert not (wheel_dir / raw_name).exists()
    assert (wheel_dir / repaired_name).is_file()


def test_regression_extension_backend_defaults_to_ceres_and_provider_sdk(tmp_path) -> None:
    backend = _load_module(REGRESSION_BACKEND_PATH, "epcsaft_regression_build_backend_for_test")

    config = backend._apply_build_config({"build-dir": str(tmp_path / "build")})

    assert config["cmake.define.EPCSAFT_ENABLE_CPPAD"] == "ON"
    assert config["cmake.define.EPCSAFT_ENABLE_CERES"] == "ON"
    assert config["cmake.define.EPCSAFT_ENABLE_IPOPT"] == "OFF"
    assert config["cmake.define.EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG"].endswith("epcsaft_provider_sdk.cmake")


def test_regression_extension_backend_auto_detects_repo_local_ceres(monkeypatch, tmp_path) -> None:
    backend = _load_module(REGRESSION_BACKEND_PATH, "epcsaft_regression_build_backend_for_test_auto_ceres")
    ceres_dir = tmp_path / "install" / "lib" / "cmake" / "Ceres"
    ceres_dir.mkdir(parents=True)
    (ceres_dir / "CeresConfig.cmake").write_text("# test\n", encoding="utf-8")
    monkeypatch.delenv("EPCSAFT_PEP517_CERES_DIR", raising=False)
    monkeypatch.delenv("Ceres_DIR", raising=False)
    monkeypatch.setattr(backend, "_repo_local_ceres_config_dir", lambda: ceres_dir)

    config = backend._apply_build_config({"build-dir": str(tmp_path / "build")})

    assert config["cmake.define.EPCSAFT_USE_SYSTEM_CERES"] == "ON"
    assert config["cmake.define.Ceres_DIR"] == str(ceres_dir.resolve())


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


def test_equilibrium_build_system_provisions_auditwheel_runtime_repair() -> None:
    pyproject = EQUILIBRIUM_PYPROJECT_PATH.read_text(encoding="utf-8")

    assert '"auditwheel' in pyproject
    assert '"patchelf' in pyproject
    assert pyproject.count("sys_platform == 'linux'") == 3


def test_equilibrium_cmake_leaves_linux_runtime_closure_to_auditwheel() -> None:
    cmake = (REPO_ROOT / "packages" / "epcsaft-equilibrium" / "CMakeLists.txt").read_text(encoding="utf-8")

    assert "file(GLOB EPCSAFT_IPOPT_RUNTIME_" + 'DLLS "${EPCSAFT_IPOPT_ROOT}/bin/*.' + 'dll")' not in cmake
    assert "file(GET_RUNTIME_DEPENDENCIES" not in cmake
    assert "bin/*." + "dll" not in cmake
    assert "EPCSAFT_IPOPT_ROOT_CMAKE}/lib" in cmake
    assert "EPCSAFT_IPOPT_ROOT_CMAKE}/lib/x86_64-linux-gnu" in cmake
    assert "INTERFACE_COMPILE_DEFINITIONS HAVE_CSTDDEF" in cmake


@pytest.mark.parametrize("cmake_path", CPPAD_CMAKE_PATHS, ids=lambda path: str(path.relative_to(REPO_ROOT)))
def test_generated_cppad_config_detects_mkstemp(cmake_path: Path) -> None:
    cmake = cmake_path.read_text(encoding="utf-8")

    assert "check_cxx_source_compiles" in cmake
    assert "mkstemp(pattern)" in cmake
    assert "set(cppad_has_mkstemp 1)" in cmake
    assert "set(cppad_has_mkstemp 0)" in cmake


def test_native_dependency_policy_has_no_noop_ceres_compatibility_gate() -> None:
    policy = NATIVE_DEPENDENCY_POLICY_PATH.read_text(encoding="utf-8")

    assert "_default_system_ceres_config_is_compatible" not in policy


def test_package_build_workflow_provisions_linux_ipopt() -> None:
    workflow = PACKAGE_BUILD_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "ipopt_root:" not in workflow
    assert "coinor-libipopt-dev" in workflow
    assert workflow.count("--ipopt-root /usr") == 2
    assert "${{ inputs.ipopt_root }}" not in workflow
