from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from scripts.validation import native_freshness


def _assert_jsonable(value: Any) -> None:
    if value is None or isinstance(value, str | int | float | bool):
        return
    if isinstance(value, list):
        for item in value:
            _assert_jsonable(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            assert isinstance(key, str)
            _assert_jsonable(item)
        return
    raise AssertionError(f"non-jsonable value {value!r}")


def test_build_receipt_records_commit_native_path_checker_and_refresh_command(tmp_path: Path) -> None:
    native_path = tmp_path / "extension_native_core.pyd"
    native_path.write_text("", encoding="utf-8")
    native_module = SimpleNamespace(__file__=str(native_path))

    receipt = native_freshness.build_receipt(
        native_module=native_module,
        checker_command=["python", "scripts/validation/check_phase_discovery.py", "--json"],
    )

    assert isinstance(receipt["git_commit"], str)
    assert len(receipt["git_commit"]) >= 7
    assert receipt["native_module_path"] == str(native_path.resolve())
    assert receipt["checker_command"] == [
        "python",
        "scripts/validation/check_phase_discovery.py",
        "--json",
    ]
    assert receipt["build_refresh_command"] == (
        "uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4"
    )


def test_require_receipt_rejects_missing_commit_or_native_path() -> None:
    valid = {
        "git_commit": "0123456789abcdef",
        "native_module_path": "C:/repo/build/extension_native_core.pyd",
    }
    native_freshness.require_receipt(valid)

    with pytest.raises(ValueError, match="git_commit"):
        native_freshness.require_receipt({**valid, "git_commit": ""})

    with pytest.raises(ValueError, match="native_module_path"):
        native_freshness.require_receipt({**valid, "native_module_path": ""})


def test_receipt_to_jsonable_returns_only_json_safe_values(tmp_path: Path) -> None:
    native_path = tmp_path / "extension_native_core.pyd"
    native_path.write_text("", encoding="utf-8")
    native_module = SimpleNamespace(__file__=str(native_path))

    receipt = native_freshness.build_receipt(
        native_module=native_module,
        checker_command=["python", "checker.py"],
    )
    jsonable = native_freshness.receipt_to_jsonable(receipt)

    _assert_jsonable(jsonable)


def test_equilibrium_receipt_requires_embedded_identity_equal_to_current_sources(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    native_path = tmp_path / "extension_native_core.so"
    native_path.write_text("native", encoding="utf-8")
    current = native_freshness.equilibrium_native_source_identity()
    native_module = SimpleNamespace(
        __file__=str(native_path),
        __name__="fresh_native",
        _native_equilibrium_build_identity=lambda: {
            "algorithm": current["algorithm"],
            "source_identity": current["source_identity"],
            "source_scope": current["scope"],
            "source_file_count": current["file_count"],
            "scope_limit": current["scope_limit"],
        },
    )
    monkeypatch.setattr(native_freshness, "git_commit", lambda: "0123456789abcdef")

    receipt = native_freshness.build_equilibrium_native_receipt(
        native_module=native_module,
        checker_command=["python", "checker.py"],
    )

    native_freshness.require_equilibrium_native_fresh(receipt)
    assert receipt["source_identity_matches"] is True
    assert receipt["freshness_mode"] == "embedded_source_identity"
    assert receipt["source_identity_limit"] == current["scope_limit"]
    assert receipt["embedded_source_identity_limit"] == current["scope_limit"]
    assert receipt["embedded_source_identity_algorithm"] == current["algorithm"]
    assert receipt["embedded_source_identity_scope"] == current["scope"]
    assert receipt["embedded_source_identity_file_count"] == current["file_count"]


def test_equilibrium_receipt_recomputes_identity_instead_of_trusting_match_flag() -> None:
    current = native_freshness.equilibrium_native_source_identity()
    forged = {
        "git_commit": "0123456789abcdef",
        "native_module_path": "/tmp/stale_native.so",
        "build_refresh_command": native_freshness.BUILD_REFRESH_COMMAND,
        "freshness_mode": "embedded_source_identity",
        "source_identity_algorithm": current["algorithm"],
        "source_identity_scope": current["scope"],
        "source_identity_limit": current["scope_limit"],
        "source_identity_file_count": current["file_count"],
        "current_source_identity": current["source_identity"],
        "embedded_source_identity_algorithm": current["algorithm"],
        "embedded_source_identity_scope": current["scope"],
        "embedded_source_identity_limit": current["scope_limit"],
        "embedded_source_identity_file_count": current["file_count"],
        "embedded_source_identity": "0" * 64,
        "source_identity_matches": True,
    }

    with pytest.raises(ValueError, match="does not match"):
        native_freshness.require_equilibrium_native_fresh(forged)


@pytest.mark.parametrize(
    ("field", "mutated_value"),
    [
        ("freshness_mode", "source_identity"),
        ("source_identity_limit", "forged-scope-limit"),
        ("embedded_source_identity_limit", "forged-scope-limit"),
        ("embedded_source_identity_algorithm", "sha256-forged-v0"),
        ("embedded_source_identity_scope", "forged-scope"),
        ("embedded_source_identity_file_count", 1),
    ],
)
def test_equilibrium_receipt_rejects_mutated_embedded_identity_metadata(
    field: str,
    mutated_value: object,
) -> None:
    current = native_freshness.equilibrium_native_source_identity()
    receipt = {
        "git_commit": "0123456789abcdef",
        "native_module_path": "/tmp/stale_native.so",
        "build_refresh_command": native_freshness.BUILD_REFRESH_COMMAND,
        "freshness_mode": "embedded_source_identity",
        "source_identity_algorithm": current["algorithm"],
        "source_identity_scope": current["scope"],
        "source_identity_limit": current["scope_limit"],
        "source_identity_file_count": current["file_count"],
        "current_source_identity": current["source_identity"],
        "embedded_source_identity_algorithm": current["algorithm"],
        "embedded_source_identity_scope": current["scope"],
        "embedded_source_identity_limit": current["scope_limit"],
        "embedded_source_identity_file_count": current["file_count"],
        "embedded_source_identity": current["source_identity"],
        "source_identity_matches": True,
    }
    receipt[field] = mutated_value

    with pytest.raises(ValueError, match="does not match"):
        native_freshness.require_equilibrium_native_fresh(receipt)


@pytest.mark.parametrize(
    "field",
    ["freshness_mode", "source_identity_limit", "embedded_source_identity_limit"],
)
def test_equilibrium_receipt_rejects_missing_freshness_metadata(field: str) -> None:
    current = native_freshness.equilibrium_native_source_identity()
    receipt = {
        "git_commit": "0123456789abcdef",
        "native_module_path": "/tmp/stale_native.so",
        "build_refresh_command": native_freshness.BUILD_REFRESH_COMMAND,
        "freshness_mode": "embedded_source_identity",
        "source_identity_algorithm": current["algorithm"],
        "source_identity_scope": current["scope"],
        "source_identity_limit": current["scope_limit"],
        "source_identity_file_count": current["file_count"],
        "current_source_identity": current["source_identity"],
        "embedded_source_identity_algorithm": current["algorithm"],
        "embedded_source_identity_scope": current["scope"],
        "embedded_source_identity_limit": current["scope_limit"],
        "embedded_source_identity_file_count": current["file_count"],
        "embedded_source_identity": current["source_identity"],
        "source_identity_matches": True,
    }
    receipt.pop(field)

    with pytest.raises(ValueError, match=field):
        native_freshness.require_equilibrium_native_fresh(receipt)
