from __future__ import annotations

import os
import types
from pathlib import Path

import pytest

from scripts.dev import bootstrap, build_epcsaft, doctor
from scripts.dev.native_runtime_env import (
    apply_native_runtime_env,
    ipopt_runtime_lib_dir,
    resolve_default_linux_ipopt_root,
    resolve_default_linux_ipopt_root_with_source,
    resolve_ipopt_root_for_build,
    validate_ipopt_root,
)


def _write_ipopt_tree(
    root: Path,
    *,
    lib_dir_name: str = "lib",
    library_name: str = "libipopt.so",
) -> None:
    include = root / "include" / "coin"
    lib = root / lib_dir_name
    include.mkdir(parents=True)
    lib.mkdir(parents=True)
    (include / "IpIpoptApplication.hpp").write_text("// test\n", encoding="utf-8")
    (lib / library_name).write_text("", encoding="utf-8")


def test_native_runtime_env_injects_ipopt_lib_from_cmake_cache(tmp_path: Path) -> None:
    ipopt_root = tmp_path / "Ipopt"
    _write_ipopt_tree(ipopt_root)
    ipopt_lib = ipopt_root / "lib"
    cache = tmp_path / "CMakeCache.txt"
    cache.write_text(
        "\n".join(
            [
                "EPCSAFT_ENABLE_IPOPT:BOOL=ON",
                f"EPCSAFT_IPOPT_ROOT:PATH={ipopt_root}",
            ]
        ),
        encoding="utf-8",
    )
    env = {"LD_LIBRARY_PATH": f"/existing{os.pathsep}{ipopt_lib}"}

    runtime = apply_native_runtime_env(env, cache_path=cache)

    assert runtime.ipopt_configured is True
    assert runtime.ipopt_root == ipopt_root.resolve()
    assert runtime.ipopt_runtime_dir == ipopt_lib.resolve()
    assert runtime.applied is True
    assert env["LD_LIBRARY_PATH"].split(os.pathsep)[0] == str(ipopt_lib.resolve())
    assert env["LD_LIBRARY_PATH"].split(os.pathsep).count(str(ipopt_lib.resolve())) == 1


def test_ipopt_runtime_dir_selects_directory_that_contains_the_library(tmp_path: Path) -> None:
    ipopt_root = tmp_path / "Ipopt"
    (ipopt_root / "lib").mkdir(parents=True)
    multiarch_lib = ipopt_root / "lib" / "x86_64-linux-gnu"
    multiarch_lib.mkdir()
    (multiarch_lib / "libipopt.so").write_text("", encoding="utf-8")

    assert ipopt_runtime_lib_dir(ipopt_root) == multiarch_lib.resolve()


def test_ipopt_root_accepts_portable_linux_multiarch_library_directory(tmp_path: Path) -> None:
    ipopt_root = tmp_path / "Ipopt"
    _write_ipopt_tree(ipopt_root, lib_dir_name="lib/aarch64-linux-gnu")

    assert validate_ipopt_root(str(ipopt_root)) == ipopt_root.resolve()
    assert ipopt_runtime_lib_dir(ipopt_root) == (ipopt_root / "lib" / "aarch64-linux-gnu").resolve()


def test_ipopt_root_rejects_static_only_install_without_proven_link_closure(tmp_path: Path) -> None:
    ipopt_root = tmp_path / "Ipopt"
    _write_ipopt_tree(ipopt_root, library_name="libipopt.a")

    with pytest.raises(FileNotFoundError, match="shared Ipopt library"):
        validate_ipopt_root(str(ipopt_root))
    assert ipopt_runtime_lib_dir(ipopt_root) is None


def test_explicit_ipopt_build_root_must_be_a_complete_shared_install(tmp_path: Path) -> None:
    incomplete_root = tmp_path / "Ipopt"
    incomplete_root.mkdir()

    with pytest.raises(FileNotFoundError, match="include/ and lib"):
        resolve_ipopt_root_for_build(
            incomplete_root,
            enable_ipopt=True,
            label="Explicit Ipopt root",
        )


def test_native_runtime_env_leaves_non_ipopt_builds_untouched(tmp_path: Path) -> None:
    ipopt_root = tmp_path / "Ipopt"
    _write_ipopt_tree(ipopt_root)
    cache = tmp_path / "CMakeCache.txt"
    cache.write_text(
        "\n".join(
            [
                "EPCSAFT_ENABLE_IPOPT:BOOL=OFF",
                f"EPCSAFT_IPOPT_ROOT:PATH={ipopt_root}",
            ]
        ),
        encoding="utf-8",
    )
    env = {"LD_LIBRARY_PATH": "/existing"}

    runtime = apply_native_runtime_env(env, cache_path=cache)

    assert runtime.ipopt_configured is False
    assert runtime.applied is False
    assert env == {"LD_LIBRARY_PATH": "/existing"}


def test_native_runtime_env_resolves_local_linux_ipopt_default(tmp_path: Path) -> None:
    ipopt_root = tmp_path / ".local" / "opt" / "ipopt"
    _write_ipopt_tree(ipopt_root)

    assert resolve_default_linux_ipopt_root(home=tmp_path, platform_name="posix") == ipopt_root.resolve()
    assert resolve_default_linux_ipopt_root(home=tmp_path, platform_name="nt") is None


def test_native_runtime_env_prefers_explicit_ipopt_cache_roots(tmp_path: Path) -> None:
    preferred = tmp_path / ".local" / "opt" / "ipopt"
    _write_ipopt_tree(preferred)

    resolution = resolve_default_linux_ipopt_root_with_source(
        home=tmp_path,
        platform_name="posix",
    )

    assert resolution.root == preferred.resolve()
    assert resolution.source == "user-local"
    assert ("user-local", preferred) in resolution.candidates


def test_bootstrap_reports_explicit_ipopt_environment_root_as_active(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    explicit_root = tmp_path / "explicit-ipopt"
    default_root = tmp_path / "default-ipopt"
    _write_ipopt_tree(explicit_root)
    _write_ipopt_tree(default_root)
    monkeypatch.setenv("EPCSAFT_IPOPT_ROOT", str(explicit_root))
    monkeypatch.setattr(
        bootstrap,
        "resolve_default_linux_ipopt_root_with_source",
        lambda: types.SimpleNamespace(root=default_root.resolve(), source="user-local"),
    )

    env = bootstrap._bootstrap_env()

    output = capsys.readouterr().out
    assert f"ipopt_root: {explicit_root.resolve()}" in output
    assert "ipopt_root_source: environment:EPCSAFT_IPOPT_ROOT" in output
    assert f"ipopt_root: {default_root.resolve()}" not in output
    assert env["EPCSAFT_IPOPT_ROOT"] == str(explicit_root.resolve())


def test_doctor_resolves_module_paths_by_importing(monkeypatch, tmp_path: Path) -> None:
    core_path = tmp_path / "_core.cpython-313-x86_64-linux-gnu.so"

    def fake_import(name: str):
        if name == "epcsaft._core":
            raise ImportError("shared object load failed while importing _core")
        return types.SimpleNamespace(__file__=str(core_path))

    monkeypatch.setattr(doctor.importlib, "import_module", fake_import)

    path, error = doctor._module_path("epcsaft._core")

    assert path is None
    assert error == "ImportError: shared object load failed while importing _core"


def test_doctor_reports_user_local_uv_when_not_on_path(monkeypatch, tmp_path: Path) -> None:
    local_uv = tmp_path / ".local" / "bin" / "uv"
    local_uv.parent.mkdir(parents=True)
    local_uv.write_text("", encoding="utf-8")
    monkeypatch.setattr(doctor.shutil, "which", lambda name: None)
    monkeypatch.setattr(doctor.Path, "home", staticmethod(lambda: tmp_path))

    assert doctor._tool_path("uv") == str(local_uv)


def test_build_status_reports_ipopt_runtime_lib_dir(monkeypatch, tmp_path: Path) -> None:
    build_dir = tmp_path / "build" / "dev"
    package_dir = tmp_path / "src" / "epcsaft"
    ipopt_root = tmp_path / "Ipopt"
    _write_ipopt_tree(ipopt_root)
    build_dir.mkdir(parents=True)
    package_dir.mkdir(parents=True)
    (build_dir / "CMakeCache.txt").write_text(
        "\n".join(
            [
                "CMAKE_GENERATOR:INTERNAL=Ninja",
                "EPCSAFT_ENABLE_CERES:BOOL=ON",
                "EPCSAFT_USE_SYSTEM_CERES:BOOL=OFF",
                "EPCSAFT_ENABLE_CPPAD:BOOL=ON",
                "EPCSAFT_ENABLE_IPOPT:BOOL=ON",
                "EPCSAFT_USE_SYSTEM_IPOPT:BOOL=ON",
                f"EPCSAFT_IPOPT_ROOT:PATH={ipopt_root}",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(build_epcsaft, "BUILD_DIR", build_dir)
    monkeypatch.setattr(build_epcsaft, "PACKAGE_DIR", package_dir)
    monkeypatch.setattr(build_epcsaft, "_repo_build_processes", lambda: [])

    lines = build_epcsaft._status_lines()

    assert f"ipopt_runtime_lib_dir: {(ipopt_root / 'lib').resolve()}" in lines
    assert "ipopt_runtime_env_applied: true" in lines
