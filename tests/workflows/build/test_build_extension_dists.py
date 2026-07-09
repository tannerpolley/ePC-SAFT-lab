from __future__ import annotations

import os
import types
from pathlib import Path

import pytest

from scripts.dev import build_extension_dists


def test_extension_dist_builder_uses_short_build_root() -> None:
    relative = build_extension_dists.BUILD_ROOT.relative_to(build_extension_dists.REPO_ROOT).as_posix()

    assert relative == "build/xd"
    assert build_extension_dists.BUILD_MODE_DIRS["installed-provider"] == "i"
    assert build_extension_dists.BUILD_PACKAGE_DIRS["epcsaft-equilibrium"] == "eq"


def test_extension_dist_builder_requires_existing_provider_wheel(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(build_extension_dists, "DIST_ROOT", tmp_path)

    with pytest.raises(RuntimeError, match="provider epcsaft wheel"):
        build_extension_dists._provider_wheel()


def test_extension_dist_builder_selects_provider_wheel_not_extension_wheel(tmp_path, monkeypatch) -> None:
    provider = tmp_path / "epcsaft-0.2.0-cp313-cp313-manylinux_2_28_x86_64.whl"
    equilibrium = tmp_path / "epcsaft_equilibrium-0.1.0-cp313-cp313-manylinux_2_28_x86_64.whl"
    provider.write_text("", encoding="utf-8")
    equilibrium.write_text("", encoding="utf-8")
    monkeypatch.setattr(build_extension_dists, "DIST_ROOT", tmp_path)

    assert build_extension_dists._provider_wheel() == provider


def test_extension_dist_builder_stages_complete_wheel_set_across_builds(tmp_path, monkeypatch) -> None:
    dist_root = tmp_path / "dist"
    build_root = tmp_path / "build"
    dist_root.mkdir()
    provider = dist_root / "epcsaft-0.2.0-cp313-cp313-linux_x86_64.whl"
    equilibrium = dist_root / "epcsaft_equilibrium-0.1.0-cp313-cp313-linux_x86_64.whl"
    provider.write_bytes(b"provider")
    equilibrium.write_bytes(b"equilibrium")
    monkeypatch.setattr(build_extension_dists, "DIST_ROOT", dist_root)
    monkeypatch.setattr(build_extension_dists, "BUILD_ROOT", build_root)

    build_extension_dists._prepare_artifact_staging()
    staged = [build_extension_dists._stage_wheel(provider), build_extension_dists._stage_wheel(equilibrium)]
    provider.unlink()
    equilibrium.unlink()
    build_extension_dists._restore_staged_wheels(staged)

    assert provider.read_bytes() == b"provider"
    assert equilibrium.read_bytes() == b"equilibrium"


def test_extension_dist_builder_sets_provider_sdk_mode_and_ipopt_root(monkeypatch, tmp_path) -> None:
    captured: dict[str, object] = {}
    wheel = tmp_path / "epcsaft_equilibrium-0.1.0-cp313-cp313-manylinux_2_28_x86_64.whl"
    wheel.write_text("", encoding="utf-8")
    ipopt_root = tmp_path / "ipopt"
    ipopt_root.mkdir()

    def fake_run(cmd: list[str], *, env=None):
        captured["cmd"] = cmd
        captured["env"] = dict(env or {})

    monkeypatch.setattr(build_extension_dists, "_run", fake_run)
    monkeypatch.setattr(build_extension_dists, "_newest_wheel", lambda prefix: wheel)

    result = build_extension_dists._build_package(
        "epcsaft-equilibrium",
        mode="installed-provider",
        env={},
        ipopt_root=ipopt_root,
        provider_sdk_config=Path("/sdk/epcsaft_provider_sdk.cmake"),
    )

    assert result == wheel
    assert captured["cmd"] == ["uv", "build", str(build_extension_dists.EQUILIBRIUM_PACKAGE_DIR)]
    env = captured["env"]
    assert env["EPCSAFT_PROVIDER_SDK_MODE"] == "installed-provider"
    assert env["EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG"].endswith("epcsaft_provider_sdk.cmake")
    assert env["EPCSAFT_PEP517_IPOPT_ROOT"] == str(ipopt_root.resolve())


def test_extension_dist_builder_prefers_repo_local_ceres_cache(monkeypatch, tmp_path) -> None:
    ceres_dir = tmp_path / "install" / "lib" / "cmake" / "Ceres"
    ceres_dir.mkdir(parents=True)
    (ceres_dir / "CeresConfig.cmake").write_text("# test\n", encoding="utf-8")
    env: dict[str, str] = {}

    monkeypatch.setattr(build_extension_dists, "resolve_default_system_ceres_config_dir", lambda root: ceres_dir)

    build_extension_dists._configure_reusable_ceres(env)

    assert env["EPCSAFT_PEP517_CERES_DIR"] == str(ceres_dir)


def test_extension_dist_builder_applies_explicit_ipopt_runtime_dir(tmp_path) -> None:
    ipopt_root = tmp_path / "ipopt"
    include_dir = ipopt_root / "include" / "coin"
    include_dir.mkdir(parents=True)
    (include_dir / "IpIpoptApplication.hpp").write_text("// test\n", encoding="utf-8")
    runtime_dir = ipopt_root / "lib" / "x86_64-linux-gnu"
    runtime_dir.mkdir(parents=True)
    (runtime_dir / "libipopt.so").write_text("", encoding="utf-8")
    env = {"LD_LIBRARY_PATH": "/existing"}

    result = build_extension_dists._configure_extension_runtime_env(
        env,
        ["epcsaft-equilibrium"],
        ipopt_root,
    )

    assert result == env
    assert env["LD_LIBRARY_PATH"].split(os.pathsep) == [str(runtime_dir.resolve()), "/existing"]


def test_extension_dist_builder_discovers_shared_linux_ipopt_when_root_is_omitted(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    ipopt_root = tmp_path / "ipopt"
    include_dir = ipopt_root / "include" / "coin"
    include_dir.mkdir(parents=True)
    (include_dir / "IpIpoptApplication.hpp").write_text("// test\n", encoding="utf-8")
    lib_dir = ipopt_root / "lib" / "aarch64-linux-gnu"
    lib_dir.mkdir(parents=True)
    (lib_dir / "libipopt.so").write_text("", encoding="utf-8")
    monkeypatch.setattr(
        build_extension_dists,
        "resolve_default_linux_ipopt_root_with_source",
        lambda: types.SimpleNamespace(root=ipopt_root.resolve(), source="system:/usr"),
    )

    resolved = build_extension_dists._resolve_ipopt_root_for_packages(
        ["epcsaft-equilibrium"],
        None,
    )

    assert resolved == ipopt_root.resolve()
    assert "ipopt_root_source: system:/usr" in capsys.readouterr().out


def test_extension_dist_builder_rejects_invalid_explicit_ipopt_root(tmp_path) -> None:
    incomplete_root = tmp_path / "ipopt"
    incomplete_root.mkdir()

    with pytest.raises(FileNotFoundError, match="shared Ipopt root"):
        build_extension_dists._resolve_ipopt_root_for_packages(
            ["epcsaft-equilibrium"],
            incomplete_root,
        )


def test_extension_dist_builder_rejects_equilibrium_without_ipopt_root(tmp_path) -> None:
    with pytest.raises(RuntimeError, match="requires a shared Ipopt root"):
        build_extension_dists._build_package(
            "epcsaft-equilibrium",
            mode="monorepo",
            env={},
            ipopt_root=tmp_path / "absent",
            provider_sdk_config=None,
        )


def test_extension_dist_builder_does_not_require_ipopt_for_regression(monkeypatch, tmp_path) -> None:
    wheel = tmp_path / "epcsaft_regression-0.1.0-cp313-cp313-manylinux_2_28_x86_64.whl"
    wheel.write_text("", encoding="utf-8")
    captured: dict[str, object] = {}

    def fake_run(cmd: list[str], *, env=None):
        captured["cmd"] = cmd
        captured["env"] = dict(env or {})

    monkeypatch.setattr(build_extension_dists, "_run", fake_run)
    monkeypatch.setattr(build_extension_dists, "_newest_wheel", lambda prefix: wheel)

    result = build_extension_dists._build_package(
        "epcsaft-regression",
        mode="monorepo",
        env={},
        ipopt_root=tmp_path / "absent",
        provider_sdk_config=None,
    )

    assert result == wheel
    assert captured["cmd"] == ["uv", "build", str(build_extension_dists.REGRESSION_PACKAGE_DIR)]
    assert "EPCSAFT_PEP517_IPOPT_ROOT" not in captured["env"]
