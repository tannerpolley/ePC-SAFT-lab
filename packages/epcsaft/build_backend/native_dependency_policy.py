"""Shared native dependency policy for dev and PEP 517 builds."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_WINDOWS_IPOPT_SDK_RELATIVE = Path("Documents") / "deps" / "ipopt-msvc"
CERES_VERSION = "2.2.0"
DEFAULT_SYSTEM_CERES_RELATIVE = Path("build") / "system-ceres" / CERES_VERSION


def default_windows_ipopt_sdk_root(home: Path | None = None) -> Path:
    """Return the machine-local default Windows Ipopt SDK root."""
    return (Path.home() if home is None else home).expanduser() / DEFAULT_WINDOWS_IPOPT_SDK_RELATIVE


def resolve_default_windows_ipopt_sdk_root(
    *,
    home: Path | None = None,
    platform_name: str | None = None,
) -> Path | None:
    """Return the default Windows Ipopt SDK root when it exists."""
    if (os.name if platform_name is None else platform_name) != "nt":
        return None
    root = default_windows_ipopt_sdk_root(home)
    return root.resolve() if root.is_dir() else None


def default_system_ceres_root(source_root: Path | str) -> Path:
    """Return the repo-local reusable Ceres root for the supported Ceres version."""
    return Path(source_root).expanduser().resolve() / DEFAULT_SYSTEM_CERES_RELATIVE


def default_system_ceres_config_dir(source_root: Path | str) -> Path:
    """Return the default repo-local Ceres CMake package config directory."""
    return default_system_ceres_root(source_root) / "install" / "lib" / "cmake" / "Ceres"


def resolve_default_system_ceres_config_dir(source_root: Path | str) -> Path | None:
    """Return the default repo-local Ceres package config directory when it exists."""
    install_dir = default_system_ceres_root(source_root) / "install"
    candidates = (
        install_dir / "lib" / "cmake" / "Ceres",
        install_dir / "lib64" / "cmake" / "Ceres",
    )
    for candidate in candidates:
        if any((candidate / name).is_file() for name in ("CeresConfig.cmake", "ceres-config.cmake")) and (
            _default_system_ceres_config_is_compatible(candidate)
        ):
            return candidate.resolve()
    return None


def _default_system_ceres_config_is_compatible(ceres_dir: Path, *, platform_name: str | None = None) -> bool:
    if (os.name if platform_name is None else platform_name) != "nt":
        return True
    target_text = "\n".join(
        target.read_text(encoding="utf-8", errors="ignore").lower()
        for target in ceres_dir.glob("CeresTargets*.cmake")
    )
    if not target_text:
        return True
    return "libceres.a" not in target_text and ".dll.a" not in target_text


def ipopt_root_prefers_msvc(
    ipopt_root: Path | str | None,
    *,
    platform_name: str | None = None,
) -> bool:
    """Return true when an Ipopt root exposes MSVC import libraries only."""
    if (os.name if platform_name is None else platform_name) != "nt" or ipopt_root is None:
        return False
    lib_dir = Path(ipopt_root).expanduser().resolve() / "lib"
    if not lib_dir.is_dir():
        return False
    has_msvc_import_lib = any((lib_dir / name).is_file() for name in ("ipopt.lib", "ipopt-3.lib"))
    has_mingw_import_lib = any((lib_dir / name).is_file() for name in ("libipopt.dll.a", "ipopt.dll.a"))
    return has_msvc_import_lib and not has_mingw_import_lib


def validate_ceres_dir(raw_path: str, *, env_name: str = "EPCSAFT_PEP517_CERES_DIR") -> Path:
    """Validate a Ceres CMake package config directory."""
    ceres_dir = Path(raw_path).expanduser().resolve()
    if not ceres_dir.is_dir():
        raise FileNotFoundError(f"{env_name} does not exist or is not a directory: {ceres_dir}")
    if not any((ceres_dir / name).is_file() for name in ("CeresConfig.cmake", "ceres-config.cmake")):
        raise FileNotFoundError(
            f"{env_name} must point at the directory containing CeresConfig.cmake "
            f"or ceres-config.cmake: {ceres_dir}"
        )
    return ceres_dir


def validate_ipopt_dir(raw_path: str, *, env_name: str = "EPCSAFT_PEP517_IPOPT_DIR") -> Path:
    """Validate an Ipopt CMake package config directory."""
    ipopt_dir = Path(raw_path).expanduser().resolve()
    if not ipopt_dir.is_dir():
        raise FileNotFoundError(f"{env_name} does not exist or is not a directory: {ipopt_dir}")
    if not any((ipopt_dir / name).is_file() for name in ("IpoptConfig.cmake", "ipopt-config.cmake")):
        raise FileNotFoundError(
            f"{env_name} must point at the directory containing IpoptConfig.cmake "
            f"or ipopt-config.cmake: {ipopt_dir}"
        )
    return ipopt_dir


def validate_ipopt_root(raw_path: str, *, env_name: str = "EPCSAFT_PEP517_IPOPT_ROOT") -> Path:
    """Validate an Ipopt install root with include and library directories."""
    ipopt_root = Path(raw_path).expanduser().resolve()
    if not ipopt_root.is_dir():
        raise FileNotFoundError(f"{env_name} does not exist or is not a directory: {ipopt_root}")
    include_dir = ipopt_root / "include"
    lib_dir = ipopt_root / "lib"
    if not include_dir.is_dir() or not lib_dir.is_dir():
        raise FileNotFoundError(f"{env_name} must point at an Ipopt tree with include/ and lib/: {ipopt_root}")
    headers = (
        include_dir / "coin-or" / "IpIpoptApplication.hpp",
        include_dir / "coin" / "IpIpoptApplication.hpp",
        include_dir / "IpIpoptApplication.hpp",
    )
    libraries = (
        lib_dir / "ipopt.lib",
        lib_dir / "ipopt-3.lib",
        lib_dir / "libipopt.dll.a",
        lib_dir / "libipopt.a",
    )
    if not any(path.is_file() for path in headers):
        raise FileNotFoundError(f"{env_name} is missing Ipopt C++ headers: {ipopt_root}")
    if not any(path.is_file() for path in libraries):
        raise FileNotFoundError(f"{env_name} is missing an Ipopt link library: {ipopt_root}")
    return ipopt_root
