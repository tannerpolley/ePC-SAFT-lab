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
        "uv run --no-sync python scripts/dev/build_epcsaft.py "
        "--profile equilibrium --build-only --parallel 4"
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
