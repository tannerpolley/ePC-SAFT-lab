from __future__ import annotations

from pathlib import Path

import epcsaft

REPO_ROOT = Path(__file__).resolve().parents[3]

CONTRACTS = {
    "provider": REPO_ROOT / "docs" / "contracts" / "provider_api_v1.md",
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
    assert "Final package ownership" in _read(CONTRACTS["extension"])
    assert "Target Native Ownership" in _read(CONTRACTS["native"])


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

    assert capabilities["package_ownership"] == {
        "provider": "epcsaft",
        "equilibrium": "epcsaft-equilibrium",
        "regression": "epcsaft-regression",
    }
    views = capabilities["package_views"]
    assert views["provider"]["reports_only_provider_capabilities_after_split"] is True
    assert views["equilibrium"]["forbidden_default_dependencies"] == ["ceres"]
    assert views["regression"]["forbidden_default_dependencies"] == ["ipopt"]


def test_issue_tracker_and_downstream_docs_are_transfer_aware() -> None:
    issue_tracker = _read(REPO_ROOT / "docs" / "agents" / "issue-tracker.md")
    downstream = _read(REPO_ROOT / "docs" / "pages" / "downstream_dependency_protocol.rst")

    assert "git remote -v" in issue_tracker
    assert "git remote -v" in downstream
    assert "ePC-SAFT/ePC-SAFT" in issue_tracker
    assert "ePC-SAFT/ePC-SAFT" in downstream
