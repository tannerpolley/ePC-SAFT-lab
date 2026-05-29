from __future__ import annotations

import zipfile

import pytest

from scripts.dev import build_dist


def _wheel(path, names: list[str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name in names:
            archive.writestr(name, "")


def test_dist_wheel_audit_accepts_package_only_wheel(tmp_path) -> None:
    wheel = tmp_path / "epcsaft-0-py3-none-any.whl"
    _wheel(wheel, ["epcsaft/__init__.py", "epcsaft/_core.cp313-win_amd64.pyd"])

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
    monkeypatch.setenv("EPCSAFT_PEP517_IPOPT_ROOT", "C:/ipopt")
    monkeypatch.setenv("EPCSAFT_RUNTIME_DLL_DIRS", "C:/ipopt/bin")
    monkeypatch.setattr(build_dist, "resolve_default_system_ceres_config_dir", lambda source_root: None)

    env = build_dist._env("1")

    assert env["CMAKE_BUILD_PARALLEL_LEVEL"] == "1"
    assert env["EPCSAFT_SANDBOX_SAFE_TEMPFILE"] == "1"
    assert "EPCSAFT_PEP517_IPOPT_ROOT" not in env
    assert "EPCSAFT_RUNTIME_DLL_DIRS" not in env


def test_dist_build_env_uses_default_repo_system_ceres(tmp_path, monkeypatch) -> None:
    ceres_dir = tmp_path / "build" / "system-ceres" / "2.2.0" / "install" / "lib" / "cmake" / "Ceres"
    ceres_dir.mkdir(parents=True)
    (ceres_dir / "CeresConfig.cmake").write_text("# test config\n", encoding="utf-8")
    monkeypatch.delenv("EPCSAFT_PEP517_CERES_DIR", raising=False)
    monkeypatch.delenv("EPCSAFT_PEP517_USE_SYSTEM_CERES", raising=False)
    monkeypatch.delenv("Ceres_DIR", raising=False)
    monkeypatch.setattr(build_dist, "resolve_default_system_ceres_config_dir", lambda source_root: ceres_dir)

    env = build_dist._env("1")

    assert env["EPCSAFT_PEP517_CERES_DIR"] == str(ceres_dir)
    assert env["EPCSAFT_PEP517_USE_SYSTEM_CERES"] == "1"
    assert "no-ipopt-system-ceres-" in env["EPCSAFT_PEP517_BUILD_DIR"]


def test_dist_build_env_preserves_explicit_system_ceres(tmp_path, monkeypatch) -> None:
    explicit_ceres_dir = tmp_path / "explicit" / "lib" / "cmake" / "Ceres"
    default_ceres_dir = tmp_path / "default" / "lib" / "cmake" / "Ceres"
    explicit_ceres_dir.mkdir(parents=True)
    default_ceres_dir.mkdir(parents=True)
    (explicit_ceres_dir / "CeresConfig.cmake").write_text("# explicit config\n", encoding="utf-8")
    (default_ceres_dir / "CeresConfig.cmake").write_text("# default config\n", encoding="utf-8")
    monkeypatch.setenv("EPCSAFT_PEP517_CERES_DIR", str(explicit_ceres_dir))
    monkeypatch.setattr(build_dist, "resolve_default_system_ceres_config_dir", lambda source_root: default_ceres_dir)

    env = build_dist._env("1")

    assert env["EPCSAFT_PEP517_CERES_DIR"] == str(explicit_ceres_dir)
    assert "system-ceres-" in env["EPCSAFT_PEP517_BUILD_DIR"]


def test_dist_build_env_uses_reusable_fetchcontent_build_dir(monkeypatch) -> None:
    monkeypatch.delenv("EPCSAFT_PEP517_CERES_DIR", raising=False)
    monkeypatch.delenv("EPCSAFT_PEP517_USE_SYSTEM_CERES", raising=False)
    monkeypatch.delenv("Ceres_DIR", raising=False)
    monkeypatch.setattr(build_dist, "resolve_default_system_ceres_config_dir", lambda source_root: None)

    env = build_dist._env("1")

    assert env["EPCSAFT_PEP517_BUILD_DIR"].endswith("no-ipopt-fetchcontent-ceres")


def test_dist_build_uses_provider_only_release_baseline() -> None:
    cmd = build_dist._uv_build_command(with_local_ipopt=False)

    assert cmd[:2] == ["uv", "build"]
    assert "cmake.define.EPCSAFT_ENABLE_CERES=OFF" in cmd
    assert "cmake.define.EPCSAFT_ENABLE_IPOPT=OFF" in cmd
    assert "cmake.define.EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE=OFF" in cmd
    assert "cmake.define.EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE=OFF" in cmd
    assert "cmake.define.EPCSAFT_USE_SYSTEM_IPOPT=OFF" in cmd
    assert "cmake.define.EPCSAFT_IPOPT_ROOT=" in cmd


def test_dist_build_can_opt_into_local_ipopt() -> None:
    assert build_dist._uv_build_command(with_local_ipopt=True) == ["uv", "build"]
