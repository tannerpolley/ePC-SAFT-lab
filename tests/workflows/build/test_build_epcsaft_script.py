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


def test_build_script_rejects_existing_non_ninja_generator_for_auto(monkeypatch) -> None:
    build = _load_script()
    ninja = Path("/repo/.venv/bin/ninja")
    monkeypatch.setattr(build, "_repo_tool_path", lambda name: ninja if name == "ninja" else None)

    with pytest.raises(RuntimeError, match="Use --clean before switching to 'Ninja'"):
        build._generator_args({"EPCSAFT_CMAKE_GENERATOR": ""}, configured_generator="Unix Makefiles")


def test_build_script_rejects_explicit_generator_switch_without_clean() -> None:
    build = _load_script()

    with pytest.raises(RuntimeError, match="Use --clean before switching"):
        build._generator_args({"EPCSAFT_CMAKE_GENERATOR": "ninja"}, configured_generator="Unix Makefiles")


def test_build_script_prefers_repo_local_cmake(monkeypatch) -> None:
    build = _load_script()
    cmake = Path("/repo/.venv/bin/cmake")

    monkeypatch.setattr(build, "_repo_tool_path", lambda name: cmake if name == "cmake" else None)

    assert build._cmake_command() == [str(cmake)]


def test_build_script_fails_when_repo_local_cmake_is_missing(monkeypatch) -> None:
    build = _load_script()

    monkeypatch.setattr(build, "_repo_tool_path", lambda name: None)

    with pytest.raises(FileNotFoundError, match="repo-local CMake"):
        build._cmake_command()


def test_build_script_pins_repo_local_ninja_for_new_tree(monkeypatch) -> None:
    build = _load_script()
    ninja = Path("/repo/.venv/bin/ninja")

    monkeypatch.setattr(build, "_repo_tool_path", lambda name: ninja if name == "ninja" else None)
    monkeypatch.setattr(build.shutil, "which", lambda name, path=None: "/usr/bin/ninja")

    args = build._generator_args({"EPCSAFT_CMAKE_GENERATOR": ""}, configured_generator=None)

    assert args == ["-G", "Ninja", f"-DCMAKE_MAKE_PROGRAM={ninja.as_posix()}"]


def test_build_script_fails_when_repo_local_ninja_is_missing(monkeypatch) -> None:
    build = _load_script()

    monkeypatch.setattr(build, "_repo_tool_path", lambda name: None)
    monkeypatch.setattr(build.shutil, "which", lambda name, path=None: "/usr/bin/ninja" if name == "ninja" else None)

    with pytest.raises(FileNotFoundError, match="repo-local Ninja"):
        build._generator_args({"EPCSAFT_CMAKE_GENERATOR": ""}, configured_generator=None)


def test_build_script_rejects_removed_toolchain_option() -> None:
    build = _load_script()

    with pytest.raises(SystemExit):
        build._parser().parse_args(["--toolchain", "auto"])


def test_build_script_reads_version_from_pyproject() -> None:
    build = _load_script()
    pyproject = tomllib.loads(build.PROVIDER_PYPROJECT.read_text(encoding="utf-8"))

    assert build._pyproject_version() == pyproject["project"]["version"]
