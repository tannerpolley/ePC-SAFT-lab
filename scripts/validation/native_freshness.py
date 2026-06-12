from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_REFRESH_COMMAND = (
    "uv run --no-sync python scripts/dev/build_epcsaft.py "
    "--profile equilibrium --build-only --parallel 4"
)


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def native_module_path(native_module: Any) -> str:
    module_file = getattr(native_module, "__file__", "")
    if not module_file:
        raise ValueError("native_module_path requires a native module with __file__")
    return str(Path(module_file).resolve())


def build_receipt(
    *,
    native_module: Any,
    checker_command: list[str] | tuple[str, ...],
    build_refresh_command: str = BUILD_REFRESH_COMMAND,
) -> dict[str, Any]:
    return {
        "git_commit": git_commit(),
        "native_module_name": str(getattr(native_module, "__name__", type(native_module).__name__)),
        "native_module_path": native_module_path(native_module),
        "checker_command": [str(item) for item in checker_command],
        "build_refresh_command": str(build_refresh_command),
    }


def require_receipt(receipt: dict[str, Any]) -> None:
    missing = [
        key
        for key in ("git_commit", "native_module_path")
        if not str(receipt.get(key, "")).strip()
    ]
    if missing:
        raise ValueError("native freshness receipt missing required field(s): " + ", ".join(missing))


def receipt_to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): receipt_to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [receipt_to_jsonable(item) for item in value]
    raise TypeError(f"native freshness receipt value is not JSON serializable: {type(value).__name__}")
