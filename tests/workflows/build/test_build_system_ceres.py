from __future__ import annotations

import importlib.util
from pathlib import Path

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


def test_system_ceres_helper_loads_msvc_env_for_default_windows_build(monkeypatch) -> None:
    script = _load_script()
    env = {"PATH": "C:\\old"}

    monkeypatch.setattr(script.os, "name", "nt")
    monkeypatch.setattr(script.shutil, "which", lambda name, path=None: None)
    monkeypatch.setattr(script, "_find_vsdevcmd", lambda: Path("C:/vs/Common7/Tools/VsDevCmd.bat"))
    monkeypatch.setattr(
        script.subprocess,
        "check_output",
        lambda command, text=True, shell=True, env=None: "PATH=C:\\msvc\nINCLUDE=C:\\include\n",
    )

    script._load_msvc_env_if_available(env, generator="auto")

    assert env["PATH"] == "C:\\msvc"
    assert env["INCLUDE"] == "C:\\include"


def test_system_ceres_helper_does_not_load_msvc_env_for_mingw(monkeypatch) -> None:
    script = _load_script()
    env = {"PATH": "C:\\old"}

    monkeypatch.setattr(script.os, "name", "nt")
    monkeypatch.setattr(script.shutil, "which", lambda name, path=None: None)
    monkeypatch.setattr(script, "_find_vsdevcmd", lambda: Path("C:/vs/Common7/Tools/VsDevCmd.bat"))

    script._load_msvc_env_if_available(env, generator="mingw")

    assert env == {"PATH": "C:\\old"}


def test_system_ceres_helper_pins_repo_local_ninja(monkeypatch) -> None:
    script = _load_script()
    ninja = Path("C:/repo/.venv/Scripts/ninja.exe")

    monkeypatch.setattr(script, "_repo_tool_path", lambda name: ninja if name == "ninja" else None)
    monkeypatch.setattr(script.shutil, "which", lambda name, path=None: "C:/Strawberry/c/bin/ninja.exe")

    assert script._generator_args({"PATH": "C:\\Strawberry\\c\\bin"}, "auto") == [
        "-G",
        "Ninja",
        f"-DCMAKE_MAKE_PROGRAM={ninja.as_posix()}",
    ]


def test_system_ceres_configure_adds_cstdint_workaround_only_for_gnu_windows(tmp_path, monkeypatch) -> None:
    script = _load_script()
    captured: list[list[str]] = []
    env = {"PATH": ""}

    monkeypatch.setattr(script, "_write_eigen_config", lambda config_dir, build_env: None)
    monkeypatch.setattr(script, "_generator_args", lambda build_env, generator: [])
    monkeypatch.setattr(script, "_run", lambda cmd, env=None: captured.append(cmd))
    monkeypatch.setattr(script.os, "name", "nt")
    monkeypatch.setattr(script.shutil, "which", lambda name, path=None: None)

    script._configure_ceres(tmp_path, "auto", env)

    assert "-DCMAKE_CXX_FLAGS=-include cstdint" not in captured[0]


def test_system_ceres_configure_keeps_cstdint_workaround_for_mingw(tmp_path, monkeypatch) -> None:
    script = _load_script()
    captured: list[list[str]] = []
    env = {"PATH": ""}

    monkeypatch.setattr(script, "_write_eigen_config", lambda config_dir, build_env: None)
    monkeypatch.setattr(script, "_generator_args", lambda build_env, generator: ["-G", "MinGW Makefiles"])
    monkeypatch.setattr(script, "_run", lambda cmd, env=None: captured.append(cmd))
    monkeypatch.setattr(script.os, "name", "nt")

    script._configure_ceres(tmp_path, "mingw", env)

    assert "-DCMAKE_CXX_FLAGS=-include cstdint" in captured[0]


def test_system_ceres_config_dir_prefers_installed_cmake_package(tmp_path) -> None:
    script = _load_script()
    config_dir = tmp_path / "install" / "lib" / "cmake" / "Ceres"
    config_dir.mkdir(parents=True)
    (config_dir / "CeresConfig.cmake").write_text("# test\n", encoding="utf-8")

    assert script._ceres_config_dir(tmp_path / "install") == config_dir


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
