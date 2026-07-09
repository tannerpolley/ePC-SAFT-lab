from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "dev" / "build_system_ceres.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("build_system_ceres_for_test", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_system_ceres_helper_uses_build_scoped_default_root() -> None:
    script = _load_script()
    script_text = SCRIPT_PATH.read_text(encoding="utf-8")

    assert script.DEFAULT_ROOT == REPO_ROOT / "build" / "system-ceres" / script.CERES_VERSION
    assert script.CERES_VERSION == "2.2.0"
    assert "-DCMAKE_CXX_STANDARD=17" in script_text
    assert "-DCMAKE_CXX_EXTENSIONS=OFF" in script_text


def test_system_ceres_helper_pins_repo_local_ninja(monkeypatch) -> None:
    script = _load_script()
    ninja = Path("/repo/.venv/bin/ninja")

    monkeypatch.setattr(script, "_repo_tool_path", lambda name: ninja if name == "ninja" else None)

    assert script._generator_args({"PATH": "/usr/bin"}, "auto") == [
        "-G",
        "Ninja",
        f"-DCMAKE_MAKE_PROGRAM={ninja.as_posix()}",
    ]


def test_system_ceres_helper_fails_when_repo_local_cmake_is_missing(monkeypatch) -> None:
    script = _load_script()

    monkeypatch.setattr(script, "_repo_tool_path", lambda name: None)

    with pytest.raises(FileNotFoundError, match="repo-local CMake"):
        script._cmake_command()


def test_system_ceres_helper_fails_when_repo_local_ninja_is_missing(monkeypatch) -> None:
    script = _load_script()

    monkeypatch.setattr(script, "_repo_tool_path", lambda name: None)

    with pytest.raises(FileNotFoundError, match="repo-local Ninja"):
        script._generator_args({"PATH": "/usr/bin"}, "auto")


def test_system_ceres_configure_omits_legacy_cstdint_workaround(tmp_path, monkeypatch) -> None:
    script = _load_script()
    captured: list[list[str]] = []
    env = {"PATH": ""}

    monkeypatch.setattr(script, "_write_eigen_config", lambda config_dir, build_env: None)
    monkeypatch.setattr(script, "_generator_args", lambda build_env, generator: [])
    monkeypatch.setattr(script, "_run", lambda cmd, env=None: captured.append(cmd))

    script._configure_ceres(tmp_path, "auto", env)

    assert "-DCMAKE_CXX_FLAGS=-include cstdint" not in captured[0]
    assert "_needs_gnu_cstdint_workaround" not in SCRIPT_PATH.read_text(encoding="utf-8")


def test_system_ceres_config_dir_prefers_installed_cmake_package(tmp_path) -> None:
    script = _load_script()
    config_dir = tmp_path / "install" / "lib" / "cmake" / "Ceres"
    config_dir.mkdir(parents=True)
    (config_dir / "CeresConfig.cmake").write_text("# test\n", encoding="utf-8")

    assert script._ceres_config_dir(tmp_path / "install") == config_dir


def test_system_ceres_config_dir_rejects_install_without_cmake_package(tmp_path) -> None:
    script = _load_script()
    install_dir = tmp_path / "install"
    install_dir.mkdir()

    with pytest.raises(FileNotFoundError, match=r"CeresConfig\.cmake"):
        script._ceres_config_dir(install_dir)


def test_system_ceres_print_env_mentions_pep517_ceres_dir(tmp_path, capsys) -> None:
    script = _load_script()
    config_dir = tmp_path / "install" / "lib" / "cmake" / "Ceres"
    config_dir.mkdir(parents=True)
    (config_dir / "CeresConfig.cmake").write_text("# test\n", encoding="utf-8")

    script._print_usage(tmp_path)

    output = capsys.readouterr().out
    assert "auto-detect" in output
    assert "EPCSAFT_PEP517_CERES_DIR" in output
    assert "Optional for external/checkout-specific reuse" in output
    assert "EPCSAFT_PEP517_BUILD_DIR" in output
    assert str(config_dir) in output
