from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pytest

from scripts.dev import build_dist, check_release_installs


def _wheel(path, names: list[str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name in names:
            archive.writestr(name, "")


def test_dist_wheel_audit_accepts_package_only_wheel(tmp_path) -> None:
    wheel = tmp_path / "epcsaft-0-py3-none-any.whl"
    _wheel(wheel, ["epcsaft/__init__.py", "epcsaft/_core.cpython-313-x86_64-linux-gnu.so"])

    build_dist._assert_wheel_has_no_solver_dev_artifacts(wheel)


def test_dist_wheel_audit_rejects_ceres_development_artifacts(tmp_path) -> None:
    wheel = tmp_path / "epcsaft-0-py3-none-any.whl"
    _wheel(
        wheel,
        [
            "include/ceres/solver.h",
            "lib/cmake/Ceres/CeresConfig.cmake",
            "include/ceres/" + "numeric" + "_diff_cost_function.h",
        ],
    )

    with pytest.raises(RuntimeError, match="Ceres development artifacts"):
        build_dist._assert_wheel_has_no_solver_dev_artifacts(wheel)


def test_dist_build_env_sets_conservative_parallel_level(monkeypatch) -> None:
    monkeypatch.delenv("PYTHONPATH", raising=False)
    monkeypatch.delenv("EPCSAFT_SANDBOX_SAFE_TEMPFILE", raising=False)
    monkeypatch.setenv("EPCSAFT_PEP517_IPOPT_ROOT", "/opt/ipopt")
    monkeypatch.setenv("LD_LIBRARY_PATH", "/opt/ipopt/lib")

    env = build_dist._env("1")

    assert env["CMAKE_BUILD_PARALLEL_LEVEL"] == "1"
    assert "EPCSAFT_SANDBOX_SAFE_TEMPFILE" not in env
    assert "EPCSAFT_PEP517_IPOPT_ROOT" not in env


def test_provider_dist_env_removes_explicit_ipopt_runtime_path(monkeypatch, tmp_path) -> None:
    ipopt_root = tmp_path / "ipopt"
    ipopt_lib = ipopt_root / "lib"
    ipopt_lib.mkdir(parents=True)
    (ipopt_lib / "libipopt.so").write_text("", encoding="utf-8")
    monkeypatch.setenv("EPCSAFT_IPOPT_ROOT", str(ipopt_root))
    monkeypatch.setenv("LD_LIBRARY_PATH", os.pathsep.join(("/keep", str(ipopt_lib))))
    monkeypatch.setattr(build_dist, "resolve_default_linux_ipopt_root", lambda: None)

    env = build_dist._env("1")

    assert env["LD_LIBRARY_PATH"] == "/keep"
    assert "EPCSAFT_IPOPT_ROOT" not in env


def test_dist_build_env_uses_provider_only_pep517_build_dir(monkeypatch) -> None:
    monkeypatch.delenv("EPCSAFT_PEP517_BUILD_DIR", raising=False)
    env = build_dist._env("1")

    assert Path(env["EPCSAFT_PEP517_BUILD_DIR"]).parts[-3:] == ("build", "pep517", "provider-only")


def test_dist_build_env_preserves_explicit_pep517_build_dir(monkeypatch, tmp_path) -> None:
    custom_build_dir = tmp_path / "pep517"
    monkeypatch.setenv("EPCSAFT_PEP517_BUILD_DIR", str(custom_build_dir))

    env = build_dist._env("1")

    assert env["EPCSAFT_PEP517_BUILD_DIR"] == str(custom_build_dir)


def test_dist_build_uses_provider_only_release_baseline() -> None:
    cmd = build_dist._uv_build_command()

    assert cmd[:3] == ["uv", "build", str(build_dist.PROVIDER_PACKAGE_DIR)]
    assert "cmake.define.EPCSAFT_ENABLE_CERES=OFF" in cmd
    assert "cmake.define.EPCSAFT_ENABLE_IPOPT=OFF" in cmd
    assert "cmake.define.EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE=OFF" in cmd
    assert "cmake.define.EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE=OFF" in cmd
    assert "cmake.define.EPCSAFT_USE_SYSTEM_IPOPT=OFF" in cmd
    assert "cmake.define.EPCSAFT_IPOPT_ROOT=" in cmd


def test_release_install_proof_requires_all_requested_artifacts(tmp_path) -> None:
    provider = tmp_path / "epcsaft-0.2.0-cp313-cp313-manylinux_2_28_x86_64.whl"
    provider.write_text("", encoding="utf-8")

    check_release_installs._assert_artifacts(tmp_path, ("epcsaft",))

    with pytest.raises(RuntimeError, match="epcsaft-equilibrium"):
        check_release_installs._assert_artifacts(tmp_path, ("epcsaft", "epcsaft-equilibrium"))


def test_release_install_proof_imports_extension_native_modules() -> None:
    code = check_release_installs._smoke_code(
        Path("/target"),
        ("epcsaft", "epcsaft-equilibrium", "epcsaft-regression"),
    )

    assert "import epcsaft" in code
    assert "import epcsaft._core" in code
    assert "import epcsaft_equilibrium._native_core" in code
    assert "import epcsaft_regression._native_core" in code
    assert "provider_native_sdk_v1" in code
