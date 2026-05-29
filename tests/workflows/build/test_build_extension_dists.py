from __future__ import annotations

from pathlib import Path

import pytest

from scripts.dev import build_extension_dists


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
