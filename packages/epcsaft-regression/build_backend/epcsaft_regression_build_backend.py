"""PEP 517 backend for the Ceres-backed regression extension package."""

from __future__ import annotations

import errno
import os
import sys
import tempfile
from pathlib import Path

from scikit_build_core import build as _scikit_build

PACKAGE_NAME = "epcsaft-regression"
PROVIDER_SDK_RELATIVE_CONFIG = Path("src") / "epcsaft" / "native_sdk" / "provider_native_sdk_v1" / "epcsaft_provider_sdk.cmake"
CERES_VERSION = "2.2.0"
DEFAULT_SYSTEM_CERES_RELATIVE = Path("build") / "system-ceres" / CERES_VERSION


def _sandbox_safe_mkdtemp(suffix=None, prefix=None, dir=None):
    prefix, suffix, dir, output_type = tempfile._sanitize_params(prefix, suffix, dir)
    names = tempfile._get_candidate_names()
    if output_type is bytes:
        names = map(os.fsencode, names)
    for _ in range(tempfile.TMP_MAX):
        name = next(names)
        path = os.path.join(dir, prefix + name + suffix)
        sys.audit("tempfile.mkdtemp", path)
        try:
            os.mkdir(path, 0o777)
        except FileExistsError:
            continue
        except PermissionError:
            if os.name == "nt" and os.path.isdir(dir) and os.access(dir, os.W_OK):
                continue
            raise
        return os.path.abspath(path)
    raise FileExistsError(errno.EEXIST, "No usable temporary directory name found")


if os.name == "nt":
    tempfile.mkdtemp = _sandbox_safe_mkdtemp


def _source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _packages_root() -> Path:
    return _source_root().parent


def _repo_root() -> Path:
    return _source_root().parents[1]


def _repo_local_ceres_config_dir() -> Path | None:
    install_dir = _repo_root() / DEFAULT_SYSTEM_CERES_RELATIVE / "install"
    candidates = (
        install_dir / "lib" / "cmake" / "Ceres",
        install_dir / "lib64" / "cmake" / "Ceres",
    )
    for candidate in candidates:
        if any((candidate / name).is_file() for name in ("CeresConfig.cmake", "ceres-config.cmake")):
            return candidate.resolve()
    return None


def _has_build_dir(config: dict) -> bool:
    return any(str(key).replace("_", "-") == "build-dir" for key in config)


def _config_has(config: dict, key: str) -> bool:
    return any(str(existing).replace("_", "-") == key.replace("_", "-") for existing in config)


def _set_config_default(config: dict, key: str, value: str) -> None:
    if not _config_has(config, key):
        config[key] = value


def _config_value(config: dict, key: str) -> str | None:
    normalized_key = key.replace("_", "-")
    for existing, value in config.items():
        if str(existing).replace("_", "-") == normalized_key:
            return str(value)
    return None


def _external_temp_root() -> Path | None:
    source_root = _source_root()
    candidates: list[Path] = []
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "Temp")
    if os.name != "nt":
        candidates.append(Path("/tmp"))
    candidates.append(Path(tempfile.gettempdir()))
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
            if resolved == source_root or source_root in resolved.parents:
                continue
            resolved.mkdir(parents=True, exist_ok=True)
        except OSError:
            continue
        return resolved
    return None


def _provider_sdk_mode(config: dict) -> str:
    return (
        _config_value(config, "epcsaft.provider-sdk-mode")
        or os.environ.get("EPCSAFT_PROVIDER_SDK_MODE")
        or "monorepo"
    ).strip().lower()


def _configured_provider_sdk(config: dict) -> Path | None:
    value = _config_value(config, "cmake.define.EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG") or os.environ.get(
        "EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG"
    )
    return Path(value).expanduser().resolve() if value else None


def _monorepo_provider_sdk_config() -> Path:
    return (_packages_root() / "epcsaft" / PROVIDER_SDK_RELATIVE_CONFIG).resolve()


def _provider_sdk_config(config: dict) -> Path:
    configured = _configured_provider_sdk(config)
    if configured is not None:
        return configured
    mode = _provider_sdk_mode(config)
    if mode == "monorepo":
        return _monorepo_provider_sdk_config()
    if mode in {"installed", "installed-provider", "installed_provider"}:
        raise ValueError(
            "installed provider SDK mode requires EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG "
            "or cmake.define.EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG."
        )
    raise ValueError(f"Unknown provider SDK mode for {PACKAGE_NAME}: {mode}")


def _apply_build_config(config_settings=None, *, native_required: bool = True) -> dict:
    config = dict(config_settings or {})
    if not _has_build_dir(config):
        persistent = os.environ.get("EPCSAFT_PEP517_BUILD_DIR")
        if persistent:
            build_dir = Path(persistent).expanduser().resolve() / PACKAGE_NAME
            build_dir.mkdir(parents=True, exist_ok=True)
        else:
            build_dir = Path(tempfile.mkdtemp(prefix="epcsaft-regression-pep517-build-", dir=_external_temp_root())).resolve()
        config["build-dir"] = str(build_dir)

    if not native_required:
        _set_config_default(config, "cmake.define.EPCSAFT_BUILD_EXTENSION_NATIVE", "OFF")
        return config

    provider_config = _provider_sdk_config(config)
    if not provider_config.is_file():
        raise ValueError(f"Provider SDK CMake config does not exist: {provider_config}")
    _set_config_default(config, "cmake.define.EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG", str(provider_config))
    _set_config_default(config, "cmake.define.EPCSAFT_ENABLE_CPPAD", "ON")
    _set_config_default(config, "cmake.define.EPCSAFT_ENABLE_CERES", "ON")
    _set_config_default(config, "cmake.define.EPCSAFT_ENABLE_IPOPT", "OFF")
    ceres_dir = os.environ.get("EPCSAFT_PEP517_CERES_DIR") or os.environ.get("Ceres_DIR") or _repo_local_ceres_config_dir()
    if ceres_dir:
        _set_config_default(config, "cmake.define.EPCSAFT_USE_SYSTEM_CERES", "ON")
        _set_config_default(config, "cmake.define.Ceres_DIR", str(Path(ceres_dir).expanduser().resolve()))
    return config


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    return _scikit_build.build_wheel(
        wheel_directory,
        config_settings=_apply_build_config(config_settings),
        metadata_directory=metadata_directory,
    )


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    return _scikit_build.build_editable(
        wheel_directory,
        config_settings=_apply_build_config(config_settings, native_required=False),
        metadata_directory=metadata_directory,
    )


build_sdist = _scikit_build.build_sdist
get_requires_for_build_editable = _scikit_build.get_requires_for_build_editable
get_requires_for_build_sdist = _scikit_build.get_requires_for_build_sdist
get_requires_for_build_wheel = _scikit_build.get_requires_for_build_wheel
prepare_metadata_for_build_editable = _scikit_build.prepare_metadata_for_build_editable
prepare_metadata_for_build_wheel = _scikit_build.prepare_metadata_for_build_wheel
