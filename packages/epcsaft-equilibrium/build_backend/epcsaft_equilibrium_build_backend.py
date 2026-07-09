"""PEP 517 backend for the Ipopt-backed equilibrium extension package."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from scikit_build_core import build as _scikit_build

PACKAGE_NAME = "epcsaft-equilibrium"
PROVIDER_SDK_RELATIVE_CONFIG = (
    Path("src") / "epcsaft" / "native_sdk" / "provider_native_sdk_v1" / "epcsaft_provider_sdk.cmake"
)


def _source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _packages_root() -> Path:
    return _source_root().parent


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
    candidates: list[Path] = [Path("/tmp")]
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
        (
            _config_value(config, "epcsaft.provider-sdk-mode")
            or os.environ.get("EPCSAFT_PROVIDER_SDK_MODE")
            or "monorepo"
        )
        .strip()
        .lower()
    )


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
            build_dir = Path(
                tempfile.mkdtemp(prefix="epcsaft-equilibrium-pep517-build-", dir=_external_temp_root())
            ).resolve()
        config["build-dir"] = str(build_dir)

    if not native_required:
        _set_config_default(config, "cmake.define.EPCSAFT_BUILD_EXTENSION_NATIVE", "OFF")
        return config

    provider_config = _provider_sdk_config(config)
    if not provider_config.is_file():
        raise ValueError(f"Provider SDK CMake config does not exist: {provider_config}")
    _set_config_default(config, "cmake.define.EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG", str(provider_config))
    _set_config_default(config, "cmake.define.EPCSAFT_ENABLE_CPPAD", "ON")
    _set_config_default(config, "cmake.define.EPCSAFT_ENABLE_IPOPT", "ON")
    _set_config_default(config, "cmake.define.EPCSAFT_USE_SYSTEM_IPOPT", "ON")
    ipopt_root = os.environ.get("EPCSAFT_PEP517_IPOPT_ROOT") or os.environ.get("EPCSAFT_IPOPT_ROOT")
    if ipopt_root:
        _set_config_default(config, "cmake.define.EPCSAFT_IPOPT_ROOT", str(Path(ipopt_root).expanduser().resolve()))
    ipopt_dir = os.environ.get("EPCSAFT_PEP517_IPOPT_DIR") or os.environ.get("Ipopt_DIR")
    if ipopt_dir:
        _set_config_default(config, "cmake.define.Ipopt_DIR", str(Path(ipopt_dir).expanduser().resolve()))
    return config


def _repair_linux_wheel(raw_wheel: Path, wheel_directory: Path) -> str:
    if sys.platform != "linux":
        raise RuntimeError("epcsaft-equilibrium native wheels are built and repaired on Linux.")
    if not raw_wheel.is_file():
        raise FileNotFoundError(f"Scikit-build-core did not produce the expected wheel: {raw_wheel}")

    wheel_directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="epcsaft-equilibrium-auditwheel-", dir=wheel_directory) as repair_temp:
        repair_dir = Path(repair_temp)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "auditwheel",
                "repair",
                "--wheel-dir",
                str(repair_dir),
                str(raw_wheel),
            ],
            check=True,
        )
        repaired_wheels = list(repair_dir.glob("*.whl"))
        if len(repaired_wheels) != 1:
            raise RuntimeError(
                f"auditwheel must produce exactly one repaired wheel; found {len(repaired_wheels)} in {repair_dir}"
            )
        repaired_wheel = repaired_wheels[0]
        final_wheel = wheel_directory / repaired_wheel.name
        os.replace(repaired_wheel, final_wheel)
    return final_wheel.name


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    output_dir = Path(wheel_directory).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="epcsaft-equilibrium-raw-wheel-",
        dir=_external_temp_root(),
    ) as raw_temp:
        raw_dir = Path(raw_temp)
        raw_name = _scikit_build.build_wheel(
            str(raw_dir),
            config_settings=_apply_build_config(config_settings),
            metadata_directory=metadata_directory,
        )
        return _repair_linux_wheel(raw_dir / raw_name, output_dir)


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
