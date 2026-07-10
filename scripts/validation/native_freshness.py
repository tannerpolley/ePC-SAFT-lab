from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
EQUILIBRIUM_PACKAGE_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium"
EQUILIBRIUM_NATIVE_SOURCE_ROOT = EQUILIBRIUM_PACKAGE_ROOT / "src" / "epcsaft_equilibrium" / "native" / "equilibrium"
EQUILIBRIUM_NATIVE_SOURCE_MANIFEST = EQUILIBRIUM_PACKAGE_ROOT / "cmake" / "equilibrium_native_sources.json"
PROVIDER_PACKAGE_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src" / "epcsaft"
PROVIDER_NATIVE_SOURCE_ROOT = PROVIDER_PACKAGE_ROOT / "native"
PROVIDER_SDK_ROOT = PROVIDER_PACKAGE_ROOT / "native_sdk" / "provider_native_sdk_v1"
EQUILIBRIUM_SOURCE_IDENTITY_ALGORITHM = "sha256-relative-path-content-v1"
EQUILIBRIUM_SOURCE_IDENTITY_SCOPE = "equilibrium-explicit-source-manifest-and-provider-manifest-driven-target-graph"
EQUILIBRIUM_SOURCE_IDENTITY_LIMIT = (
    "Covers the canonical equilibrium object/module/header manifest, every listed equilibrium "
    "file, this shared CMake loader/identity helper, the provider source manifest contract, the "
    "exact manifest-listed provider target .cpp files, and the .h/.hpp header contracts "
    "reachable from manifest include roots. Root/standalone target compile definitions, "
    "include/link flags, compiler identity, generated dependency sources, and dependency "
    "binaries are outside this source receipt."
)
BUILD_REFRESH_COMMAND = (
    "uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4"
)


def _equilibrium_native_manifest_paths() -> tuple[Path, ...]:
    manifest = json.loads(EQUILIBRIUM_NATIVE_SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("equilibrium native source manifest requires schema_version 1")
    relative_paths: list[str] = []
    for key in ("object_sources", "module_sources", "headers"):
        entries = manifest.get(key)
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"equilibrium native source manifest '{key}' must be a nonempty list")
        for entry in entries:
            if not isinstance(entry, str) or not entry or Path(entry).is_absolute() or ".." in Path(entry).parts:
                raise ValueError(f"equilibrium native source manifest path must be package-relative: {entry!r}")
            relative_paths.append(entry)
    if len(relative_paths) != len(set(relative_paths)):
        raise ValueError("equilibrium native source manifest entries must be unique")
    return tuple(EQUILIBRIUM_NATIVE_SOURCE_ROOT / path for path in relative_paths)


def _provider_source_manifest() -> dict[str, Any]:
    manifest = json.loads((PROVIDER_SDK_ROOT / "provider_sources.json").read_text(encoding="utf-8"))
    if manifest.get("contract_id") != "provider_native_sdk_v1":
        raise ValueError("provider source manifest requires contract_id 'provider_native_sdk_v1'")
    return manifest


def _provider_manifest_paths(*, key: str) -> tuple[Path, ...]:
    entries = _provider_source_manifest().get(key)
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"provider native source manifest '{key}' must be a nonempty list")
    relative_paths: list[str] = []
    for entry in entries:
        if not isinstance(entry, str) or not entry or Path(entry).is_absolute() or ".." in Path(entry).parts:
            raise ValueError(
                f"provider native source manifest path must be a nonempty package-relative path: {entry!r}"
            )
        absolute_path = PROVIDER_PACKAGE_ROOT / entry
        if not absolute_path.exists():
            raise FileNotFoundError(f"provider native source manifest entry is missing: {absolute_path}")
        if key == "sources" and not absolute_path.is_file():
            raise ValueError(
                f"provider native source manifest 'sources' entries must be existing files: {absolute_path}"
            )
        if key == "include_dirs" and not absolute_path.is_dir():
            raise ValueError(
                f"provider native source manifest 'include_dirs' entries must be existing directories: {absolute_path}"
            )
        relative_paths.append(entry)
    if len(relative_paths) != len(set(relative_paths)):
        raise ValueError(f"provider native source manifest '{key}' entries must be unique")
    return tuple(PROVIDER_PACKAGE_ROOT / path for path in relative_paths)


def _provider_manifest_header_paths() -> tuple[Path, ...]:
    headers: set[Path] = set()
    for include_root in _provider_manifest_paths(key="include_dirs"):
        for pattern in ("*.h", "*.hpp"):
            headers.update(include_root.rglob(pattern))
    return tuple(sorted(headers))


def _equilibrium_native_identity_files() -> tuple[tuple[str, Path], ...]:
    files: list[tuple[str, Path]] = [
        (
            "equilibrium/cmake/EquilibriumNativeSourceIdentity.cmake",
            EQUILIBRIUM_PACKAGE_ROOT / "cmake" / "EquilibriumNativeSourceIdentity.cmake",
        ),
        (
            "equilibrium/cmake/equilibrium_native_sources.json",
            EQUILIBRIUM_NATIVE_SOURCE_MANIFEST,
        ),
        (
            "provider/native_sdk/provider_native_sdk_v1/epcsaft_provider_sdk.cmake",
            PROVIDER_SDK_ROOT / "epcsaft_provider_sdk.cmake",
        ),
        (
            "provider/native_sdk/provider_native_sdk_v1/provider_sources.json",
            PROVIDER_SDK_ROOT / "provider_sources.json",
        ),
    ]
    files.extend(
        (
            "equilibrium/" + path.relative_to(EQUILIBRIUM_PACKAGE_ROOT).as_posix(),
            path,
        )
        for path in _equilibrium_native_manifest_paths()
    )
    files.extend(
        ("provider/" + path.relative_to(PROVIDER_PACKAGE_ROOT).as_posix(), path)
        for path in _provider_manifest_paths(key="sources")
    )
    files.extend(
        ("provider/" + path.relative_to(PROVIDER_PACKAGE_ROOT).as_posix(), path)
        for path in _provider_manifest_header_paths()
    )
    return tuple(sorted(files, key=lambda item: item[0]))


def equilibrium_native_source_identity() -> dict[str, Any]:
    identity_input = bytearray()
    files = _equilibrium_native_identity_files()
    for logical_path, path in files:
        if not path.is_file():
            raise FileNotFoundError(f"equilibrium native identity source is missing: {path}")
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        identity_input.extend(f"{logical_path}:{content_hash}\n".encode())
    return {
        "algorithm": EQUILIBRIUM_SOURCE_IDENTITY_ALGORITHM,
        "scope": EQUILIBRIUM_SOURCE_IDENTITY_SCOPE,
        "scope_limit": EQUILIBRIUM_SOURCE_IDENTITY_LIMIT,
        "file_count": len(files),
        "source_identity": hashlib.sha256(identity_input).hexdigest(),
    }


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


def build_equilibrium_native_receipt(
    *,
    native_module: Any,
    checker_command: list[str] | tuple[str, ...],
    build_refresh_command: str = BUILD_REFRESH_COMMAND,
) -> dict[str, Any]:
    receipt = build_receipt(
        native_module=native_module,
        checker_command=checker_command,
        build_refresh_command=build_refresh_command,
    )
    current = equilibrium_native_source_identity()
    identity_reader = getattr(native_module, "_native_equilibrium_build_identity", None)
    embedded = dict(identity_reader()) if callable(identity_reader) else {}
    embedded_identity = str(embedded.get("source_identity", ""))
    embedded_algorithm = str(embedded.get("algorithm", ""))
    embedded_scope = str(embedded.get("source_scope", ""))
    embedded_file_count = embedded.get("source_file_count")
    embedded_scope_limit = str(embedded.get("scope_limit", ""))
    receipt.update(
        {
            "freshness_mode": "embedded_source_identity",
            "source_identity_algorithm": current["algorithm"],
            "source_identity_scope": current["scope"],
            "source_identity_limit": current["scope_limit"],
            "source_identity_file_count": current["file_count"],
            "current_source_identity": current["source_identity"],
            "embedded_source_identity_algorithm": embedded_algorithm,
            "embedded_source_identity_scope": embedded_scope,
            "embedded_source_identity_file_count": embedded_file_count,
            "embedded_source_identity_limit": embedded_scope_limit,
            "embedded_source_identity": embedded_identity,
            "source_identity_matches": (
                embedded_identity == current["source_identity"]
                and embedded_algorithm == current["algorithm"]
                and embedded_scope == current["scope"]
                and embedded_file_count == current["file_count"]
            ),
        }
    )
    return receipt


def require_receipt(receipt: dict[str, Any]) -> None:
    missing = [key for key in ("git_commit", "native_module_path") if not str(receipt.get(key, "")).strip()]
    if missing:
        raise ValueError("native freshness receipt missing required field(s): " + ", ".join(missing))


def require_equilibrium_native_fresh(receipt: dict[str, Any]) -> None:
    require_receipt(receipt)
    current = equilibrium_native_source_identity()
    missing = [
        key
        for key in (
            "freshness_mode",
            "source_identity_algorithm",
            "source_identity_scope",
            "source_identity_limit",
            "source_identity_file_count",
            "current_source_identity",
            "embedded_source_identity_algorithm",
            "embedded_source_identity_scope",
            "embedded_source_identity_limit",
            "embedded_source_identity_file_count",
            "embedded_source_identity",
        )
        if key not in receipt or not str(receipt[key]).strip()
    ]
    if missing:
        raise ValueError("equilibrium native freshness receipt missing required field(s): " + ", ".join(missing))
    identity_matches = (
        receipt["freshness_mode"] == "embedded_source_identity"
        and receipt["source_identity_algorithm"] == current["algorithm"]
        and receipt["source_identity_scope"] == current["scope"]
        and receipt["source_identity_limit"] == current["scope_limit"]
        and receipt["source_identity_file_count"] == current["file_count"]
        and receipt["current_source_identity"] == current["source_identity"]
        and receipt["embedded_source_identity_algorithm"] == current["algorithm"]
        and receipt["embedded_source_identity_scope"] == current["scope"]
        and receipt["embedded_source_identity_limit"] == current["scope_limit"]
        and receipt["embedded_source_identity_file_count"] == current["file_count"]
        and receipt["embedded_source_identity"] == current["source_identity"]
        and receipt.get("source_identity_matches") is True
    )
    if not identity_matches:
        raise ValueError(
            "loaded equilibrium native source identity does not match the current package-owned "
            "native sources; rebuild with: " + str(receipt.get("build_refresh_command", BUILD_REFRESH_COMMAND))
        )


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
