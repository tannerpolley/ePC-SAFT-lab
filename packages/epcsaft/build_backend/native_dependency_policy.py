"""Shared native dependency policy for dev and PEP 517 builds."""

from __future__ import annotations

import os
import sysconfig
from dataclasses import dataclass
from pathlib import Path

DEFAULT_LINUX_IPOPT_ROOT_RELATIVE = Path(".local") / "opt" / "ipopt"
LINUX_IPOPT_ROOT_CANDIDATES = (
    Path("/usr/local"),
    Path("/usr"),
    Path("/opt/ipopt"),
)
CERES_VERSION = "2.2.0"
DEFAULT_SYSTEM_CERES_RELATIVE = Path("build") / "system-ceres" / CERES_VERSION


@dataclass(frozen=True)
class IpoptRootResolution:
    root: Path | None
    source: str
    candidates: tuple[tuple[str, Path], ...]


def default_linux_ipopt_root(home: Path | None = None) -> Path:
    """Return the user-local Linux Ipopt install root."""
    return (Path.home() if home is None else home).expanduser() / DEFAULT_LINUX_IPOPT_ROOT_RELATIVE


def linux_ipopt_root_candidates(
    *,
    home: Path | None = None,
    platform_name: str | None = None,
) -> tuple[tuple[str, Path], ...]:
    """Return default Linux Ipopt install-root probe paths in preference order."""
    if (os.name if platform_name is None else platform_name) == "nt":
        return ()
    base_home = (Path.home() if home is None else home).expanduser()
    candidates: list[tuple[str, Path]] = [("user-local", base_home / DEFAULT_LINUX_IPOPT_ROOT_RELATIVE)]
    candidates.extend((f"system:{path}", path) for path in LINUX_IPOPT_ROOT_CANDIDATES)
    return tuple(candidates)


def resolve_default_linux_ipopt_root(
    *,
    home: Path | None = None,
    platform_name: str | None = None,
) -> Path | None:
    """Return the default Linux Ipopt install root when it looks usable."""
    resolution = resolve_default_linux_ipopt_root_with_source(
        home=home,
        platform_name=platform_name,
    )
    return resolution.root


def resolve_default_linux_ipopt_root_with_source(
    *,
    home: Path | None = None,
    platform_name: str | None = None,
) -> IpoptRootResolution:
    """Return the first usable default Linux Ipopt install root with provenance."""
    candidates = linux_ipopt_root_candidates(
        home=home,
        platform_name=platform_name,
    )
    for source, root in candidates:
        try:
            validate_ipopt_root(str(root), env_name=source)
        except FileNotFoundError:
            continue
        return IpoptRootResolution(root.resolve(), source, candidates)
    return IpoptRootResolution(None, "missing", candidates)


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
        if any((candidate / name).is_file() for name in ("CeresConfig.cmake", "ceres-config.cmake")):
            return candidate.resolve()
    return None


def validate_ceres_dir(raw_path: str, *, env_name: str = "EPCSAFT_PEP517_CERES_DIR") -> Path:
    """Validate a Ceres CMake package config directory."""
    ceres_dir = Path(raw_path).expanduser().resolve()
    if not ceres_dir.is_dir():
        raise FileNotFoundError(f"{env_name} does not exist or is not a directory: {ceres_dir}")
    if not any((ceres_dir / name).is_file() for name in ("CeresConfig.cmake", "ceres-config.cmake")):
        raise FileNotFoundError(
            f"{env_name} must point at the directory containing CeresConfig.cmake or ceres-config.cmake: {ceres_dir}"
        )
    return ceres_dir


def validate_ipopt_dir(raw_path: str, *, env_name: str = "EPCSAFT_PEP517_IPOPT_DIR") -> Path:
    """Validate an Ipopt CMake package config directory."""
    ipopt_dir = Path(raw_path).expanduser().resolve()
    if not ipopt_dir.is_dir():
        raise FileNotFoundError(f"{env_name} does not exist or is not a directory: {ipopt_dir}")
    if not any((ipopt_dir / name).is_file() for name in ("IpoptConfig.cmake", "ipopt-config.cmake")):
        raise FileNotFoundError(
            f"{env_name} must point at the directory containing IpoptConfig.cmake or ipopt-config.cmake: {ipopt_dir}"
        )
    return ipopt_dir


def linux_ipopt_library_dirs(ipopt_root: Path | str) -> tuple[Path, ...]:
    """Return portable Linux library-directory candidates for an Ipopt root."""
    root = Path(ipopt_root).expanduser().resolve()
    bases = (root / "lib", root / "lib64")
    candidates: list[Path] = list(bases)
    multiarch = str(sysconfig.get_config_var("MULTIARCH") or "").strip()
    if multiarch:
        candidates.extend(base / multiarch for base in bases)
    for base in bases:
        if base.is_dir():
            candidates.extend(sorted((path for path in base.iterdir() if path.is_dir()), key=str))

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        unique.append(candidate)
    return tuple(unique)


def _has_shared_ipopt_library(lib_dir: Path) -> bool:
    return any(path.is_file() for path in lib_dir.glob("libipopt.so*"))


def validate_ipopt_root(raw_path: str, *, env_name: str = "EPCSAFT_PEP517_IPOPT_ROOT") -> Path:
    """Validate an Ipopt install root with include and library directories."""
    ipopt_root = Path(raw_path).expanduser().resolve()
    if not ipopt_root.is_dir():
        raise FileNotFoundError(f"{env_name} does not exist or is not a directory: {ipopt_root}")
    include_dir = ipopt_root / "include"
    lib_dirs = linux_ipopt_library_dirs(ipopt_root)
    if not include_dir.is_dir() or not any(path.is_dir() for path in lib_dirs):
        raise FileNotFoundError(f"{env_name} must point at an Ipopt tree with include/ and lib*/: {ipopt_root}")
    headers = (
        include_dir / "coin-or" / "IpIpoptApplication.hpp",
        include_dir / "coin" / "IpIpoptApplication.hpp",
        include_dir / "IpIpoptApplication.hpp",
    )
    if not any(path.is_file() for path in headers):
        raise FileNotFoundError(f"{env_name} is missing Ipopt C++ headers: {ipopt_root}")
    if not any(_has_shared_ipopt_library(lib_dir) for lib_dir in lib_dirs):
        raise FileNotFoundError(
            f"{env_name} is missing a shared Ipopt library (libipopt.so*): {ipopt_root}. "
            "Static-only roots are rejected because their full transitive link closure is not proven."
        )
    return ipopt_root
