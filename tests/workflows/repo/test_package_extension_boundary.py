from __future__ import annotations

from pathlib import Path

import epcsaft
import epcsaft_equilibrium
import epcsaft_regression

REPO_ROOT = Path(__file__).resolve().parents[3]

CONTRACTS = {
    "provider": REPO_ROOT / "docs" / "contracts" / "provider_api_v1.md",
    "provider_native": REPO_ROOT / "docs" / "contracts" / "provider_native_sdk_v1.md",
    "extension": REPO_ROOT / "docs" / "contracts" / "extension_compatibility.md",
    "native": REPO_ROOT / "docs" / "contracts" / "native_extension_boundary.md",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_package_extension_contract_docs_exist_and_share_status() -> None:
    for path in CONTRACTS.values():
        text = _read(path)
        assert "Status: pre-extraction contract." in text

    assert "provider_api_v1" in _read(CONTRACTS["provider"])
    assert "provider_native_sdk_v1" in _read(CONTRACTS["provider_native"])
    assert "Final package ownership" in _read(CONTRACTS["extension"])
    assert "Target Native Ownership" in _read(CONTRACTS["native"])


def test_transfer_roadmap_current_state_matches_runtime_boundary_progress() -> None:
    roadmap = _read(REPO_ROOT / "docs" / "roadmaps" / "package_extension_transfer_roadmap.md")

    assert "provider runtime metadata is provider-scoped" in roadmap
    assert "provider runtime metadata still reports regression transition capability data" not in roadmap


def test_adr_and_source_docs_agree_on_package_owners() -> None:
    files = [
        REPO_ROOT / "docs" / "adr" / "0005-package-extension-split.md",
        REPO_ROOT / "docs" / "roadmaps" / "FULL_ROADMAP.md",
        REPO_ROOT / "docs" / "pages" / "package_architecture.rst",
        REPO_ROOT / "docs" / "protocols" / "build_package_dependency_protocol.rst",
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "pages" / "README.rst",
    ]

    for path in files:
        text = _read(path)
        assert "epcsaft-equilibrium" in text, path
        assert "epcsaft-regression" in text, path


def test_live_docs_do_not_use_rejected_core_ownership_phrases() -> None:
    stale_phrases = (
        "package-owned equilibrium/regression",
        "package-owned phase",
        "Regression and equilibrium are core package capabilities",
        "one installable distribution",
        "avoid splitting EOS/equilibrium/regression",
        "Downstream projects should file GitHub issues against ``tannerpolley/ePC-SAFT``",
    )
    roots = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "pages",
        REPO_ROOT / "docs" / "protocols",
        REPO_ROOT / "docs" / "agents",
        REPO_ROOT / "docs" / "contracts",
    ]

    offenders: list[str] = []
    for root in roots:
        paths = [root] if root.is_file() else list(root.rglob("*"))
        for path in paths:
            if path.is_file() and path.suffix in {".md", ".rst"}:
                text = _read(path)
                for phrase in stale_phrases:
                    if phrase in text:
                        offenders.append(f"{path.relative_to(REPO_ROOT)}: {phrase}")

    assert offenders == []


def test_extension_compatibility_contract_rejects_hidden_core_wrappers() -> None:
    text = _read(CONTRACTS["extension"])

    assert "Core provider imports must not import extension packages by default." in text
    assert "must not use private" in text
    assert "hidden long-lived compatibility wrappers" in text
    assert "removed in the coordinated migration" in text


def test_runtime_capabilities_are_separable_by_future_package_owner() -> None:
    capabilities = epcsaft.capabilities()

    assert capabilities["package"] == "epcsaft"
    assert capabilities["owner"] == "core_provider"
    assert capabilities["reports_only_provider_capabilities_after_split"] is True
    assert capabilities["native_sdk_contract_id"] == "provider_native_sdk_v1"
    assert "package_ownership" not in capabilities
    assert "package_views" not in capabilities
    assert "equilibrium" not in capabilities
    assert "regression" not in capabilities
    assert "optimizers" not in capabilities

    equilibrium_capabilities = epcsaft_equilibrium.capabilities()
    assert equilibrium_capabilities["package"] == "epcsaft-equilibrium"
    assert equilibrium_capabilities["owner"] == "equilibrium_extension"
    assert equilibrium_capabilities["provider_contract"]["provider_native_sdk_contract_id"] == "provider_native_sdk_v1"
    assert equilibrium_capabilities["forbidden_default_dependencies"] == ["ceres"]
    assert equilibrium_capabilities["requires"] == ["epcsaft", "cppad", "ipopt"]
    assert equilibrium_capabilities["public_routes"] == [
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
        "flash",
        "lle",
    ]

    regression_capabilities = epcsaft_regression.capabilities()
    assert regression_capabilities["package"] == "epcsaft-regression"
    assert regression_capabilities["owner"] == "regression_extension"
    assert regression_capabilities["provider_contract"]["provider_native_sdk_contract_id"] == "provider_native_sdk_v1"
    assert regression_capabilities["forbidden_default_dependencies"] == ["ipopt"]
    assert regression_capabilities["requires"] == ["epcsaft", "cppad", "ceres"]


def test_provider_native_sdk_is_runtime_visible_without_extension_ownership() -> None:
    sdk = epcsaft.provider_native_sdk()

    assert sdk["contract_id"] == "provider_native_sdk_v1"
    assert sdk["provider_api_contract_id"] == "provider_api_v1"
    assert sdk["owner_package"] == "epcsaft"
    assert sdk["native_target"] == "epcsaft_provider_native"
    assert sdk["required_native_dependencies"] == ["cppad", "eigen"]
    assert sdk["forbidden_native_dependencies"] == ["ceres", "ipopt"]
    assert sdk["extension_consumers"] == ["epcsaft-equilibrium", "epcsaft-regression"]
    assert "epcsaft._core" not in sdk["stable_python_surface"]
    assert sdk["native_contract_exported"] is True
    assert isinstance(sdk["provider_only_core"], bool)
    assert isinstance(sdk["equilibrium_native_enabled"], bool)
    assert isinstance(sdk["regression_native_enabled"], bool)
    assert sdk["native_metadata"]["native_target"] == "epcsaft_provider_native"


def test_issue_tracker_and_downstream_docs_are_transfer_aware() -> None:
    issue_tracker = _read(REPO_ROOT / "docs" / "agents" / "issue-tracker.md")
    downstream = _read(REPO_ROOT / "docs" / "pages" / "downstream_dependency_protocol.rst")

    assert "git remote -v" in issue_tracker
    assert "git remote -v" in downstream
    assert "ePC-SAFT/ePC-SAFT" in issue_tracker
    assert "ePC-SAFT/ePC-SAFT" in downstream


def test_downstream_local_install_docs_use_provider_scoped_capabilities() -> None:
    downstream = _read(REPO_ROOT / "docs" / "pages" / "downstream_local_installs.rst")

    assert 'provider_caps["package"] == "epcsaft"' in downstream
    assert 'provider_caps["package_ownership"]' not in downstream
