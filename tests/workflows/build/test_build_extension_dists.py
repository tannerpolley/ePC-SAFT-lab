from __future__ import annotations

from pathlib import Path

import pytest

from scripts.dev import build_extension_dists


def test_extension_dist_builder_uses_short_windows_build_root() -> None:
    relative = build_extension_dists.BUILD_ROOT.relative_to(build_extension_dists.REPO_ROOT).as_posix()

    assert relative == "build/xd"
    assert build_extension_dists.BUILD_MODE_DIRS["installed-provider"] == "i"
    assert build_extension_dists.BUILD_PACKAGE_DIRS["epcsaft-equilibrium"] == "eq"


def test_extension_dist_builder_requires_existing_provider_wheel(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(build_extension_dists, "DIST_ROOT", tmp_path)

    with pytest.raises(RuntimeError, match="provider epcsaft wheel"):
        build_extension_dists._provider_wheel()


def test_extension_dist_builder_selects_provider_wheel_not_extension_wheel(tmp_path, monkeypatch) -> None:
    provider = tmp_path / "epcsaft-0.2.0-cp313-win_amd64.whl"
    equilibrium = tmp_path / "epcsaft_equilibrium-0.1.0-cp313-win_amd64.whl"
    provider.write_text("", encoding="utf-8")
    equilibrium.write_text("", encoding="utf-8")
    monkeypatch.setattr(build_extension_dists, "DIST_ROOT", tmp_path)

    assert build_extension_dists._provider_wheel() == provider


def test_extension_dist_builder_sets_provider_sdk_mode_and_ipopt_root(monkeypatch, tmp_path) -> None:
    captured: dict[str, object] = {}
    wheel = tmp_path / "epcsaft_equilibrium-0.1.0-cp313-win_amd64.whl"
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
        provider_sdk_config=Path("C:/sdk/epcsaft_provider_sdk.cmake"),
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


def test_extension_dist_builder_loads_msvc_for_msvc_ipopt_sdk(monkeypatch, tmp_path) -> None:
    ipopt_root = tmp_path / "ipopt"
    (ipopt_root / "lib").mkdir(parents=True)
    (ipopt_root / "lib" / "ipopt.lib").write_text("", encoding="utf-8")

    def fake_load_msvc_env(env: dict[str, str]) -> dict[str, str]:
        updated = env.copy()
        updated["VSCMD_VER"] = "test"
        return updated

    monkeypatch.setattr(build_extension_dists.os, "name", "nt")
    monkeypatch.setattr(build_extension_dists, "_load_msvc_env", fake_load_msvc_env)

    result = build_extension_dists._configure_extension_toolchain(
        {},
        ["epcsaft-equilibrium"],
        ipopt_root,
    )

    assert result["VSCMD_VER"] == "test"
    assert result["CMAKE_GENERATOR"] == "Ninja"


def test_extension_dist_builder_rejects_equilibrium_without_ipopt_root(tmp_path) -> None:
    with pytest.raises(RuntimeError, match="requires Ipopt SDK root"):
        build_extension_dists._build_package(
            "epcsaft-equilibrium",
            mode="monorepo",
            env={},
            ipopt_root=tmp_path / "absent",
            provider_sdk_config=None,
        )


def test_extension_dist_builder_does_not_require_ipopt_for_regression(monkeypatch, tmp_path) -> None:
    wheel = tmp_path / "epcsaft_regression-0.1.0-cp313-win_amd64.whl"
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
