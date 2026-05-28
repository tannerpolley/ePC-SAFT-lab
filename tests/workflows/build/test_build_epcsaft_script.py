from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import tomllib

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "dev" / "build_epcsaft.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("build_epcsaft_for_test", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_script_preserves_existing_generator_for_auto() -> None:
    build = _load_script()

    args = build._generator_args({"EPCSAFT_CMAKE_GENERATOR": ""}, configured_generator="MinGW Makefiles")

    assert args == []


def test_build_script_rejects_explicit_generator_switch_without_clean() -> None:
    build = _load_script()

    with pytest.raises(RuntimeError, match="Use --clean before switching"):
        build._generator_args({"EPCSAFT_CMAKE_GENERATOR": "ninja"}, configured_generator="MinGW Makefiles")


def test_build_script_prefers_repo_local_cmake(monkeypatch) -> None:
    build = _load_script()
    cmake = Path("C:/repo/.venv/Scripts/cmake.exe")

    monkeypatch.setattr(build, "_repo_tool_path", lambda name: cmake if name == "cmake" else None)

    assert build._cmake_command() == [str(cmake)]


def test_build_script_pins_repo_local_ninja_for_new_tree(monkeypatch) -> None:
    build = _load_script()
    ninja = Path("C:/repo/.venv/Scripts/ninja.exe")

    monkeypatch.setattr(build, "_repo_tool_path", lambda name: ninja if name == "ninja" else None)
    monkeypatch.setattr(build.shutil, "which", lambda name, path=None: "C:/Strawberry/c/bin/ninja.exe")

    args = build._generator_args({"EPCSAFT_CMAKE_GENERATOR": ""}, configured_generator=None)

    assert args == ["-G", "Ninja", f"-DCMAKE_MAKE_PROGRAM={ninja.as_posix()}"]


def test_build_script_auto_prefers_ninja_for_new_build_tree(monkeypatch) -> None:
    build = _load_script()

    monkeypatch.setattr(build, "_repo_tool_path", lambda name: None)
    monkeypatch.setattr(build.shutil, "which", lambda name, path=None: "ninja.exe" if name == "ninja" else None)

    args = build._generator_args({"EPCSAFT_CMAKE_GENERATOR": ""}, configured_generator=None)

    assert args == ["-G", "Ninja"]


def test_build_script_auto_loads_msvc_for_new_windows_tree(monkeypatch) -> None:
    build = _load_script()
    env = {"PATH": "C:/repo/.venv/Scripts"}
    loaded = {"PATH": "C:/repo/.venv/Scripts", "VSCMD_VER": "17.0"}

    monkeypatch.setattr(build.os, "name", "nt")
    monkeypatch.setattr(build, "_configured_cxx_compiler", lambda: None)
    monkeypatch.setattr(build, "_load_msvc_env", lambda build_env: loaded)

    result = build._apply_toolchain_env(env, toolchain="auto", enable_ipopt=False, ipopt_root=None)

    assert result == loaded


def test_build_script_auto_preserves_existing_non_msvc_windows_tree_without_clean(monkeypatch) -> None:
    build = _load_script()
    env = {"PATH": "C:/Strawberry/c/bin"}

    monkeypatch.setattr(build.os, "name", "nt")
    monkeypatch.setattr(build, "_configured_cxx_compiler", lambda: "C:/Strawberry/c/bin/c++.exe")

    result = build._apply_toolchain_env(env, toolchain="auto", enable_ipopt=False, ipopt_root=None)

    assert result == env


def test_build_script_reads_version_from_pyproject() -> None:
    build = _load_script()
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert build._pyproject_version() == pyproject["project"]["version"]
