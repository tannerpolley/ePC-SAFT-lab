from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
DEV_BUILD_CACHE = REPO_ROOT / "build" / "dev" / "CMakeCache.txt"
EXTENSION_NATIVE_MODULES = (
    "epcsaft_equilibrium._native_core",
    "epcsaft_regression._native_core",
)
STALE_TRACKED_REPORTS: tuple[Path, ...] = ()
REQUIRED_CORE_SYMBOLS = (
    "_native_cppad_smoke",
    "NativeSolutionError",
)

try:
    from scripts.dev.package_paths import PROVIDER_BUILD_BACKEND_DIR
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from package_paths import PROVIDER_BUILD_BACKEND_DIR

if str(PROVIDER_BUILD_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(PROVIDER_BUILD_BACKEND_DIR))

from native_dependency_policy import (
    CERES_VERSION,
    default_system_ceres_config_dir,
    default_system_ceres_root,
    linux_ipopt_root_candidates,
    resolve_default_linux_ipopt_root,
    resolve_default_linux_ipopt_root_with_source,
    resolve_default_system_ceres_config_dir,
)

try:
    from scripts.dev.native_runtime_env import apply_to_current_process
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from native_runtime_env import apply_to_current_process


def _git_output(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def _module_path(module_name: str) -> tuple[Path | None, str | None]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
    origin = getattr(module, "__file__", None)
    if origin is None:
        return None, None
    return Path(origin).resolve(), None


def _module_state(module_name: str) -> dict[str, str]:
    path, error = _module_path(module_name)
    return {
        "path": str(path) if path else "<missing>",
        "error": error or "<none>",
    }


def _missing_core_symbols() -> tuple[str, ...]:
    try:
        import epcsaft._core as core
    except Exception as exc:
        raise RuntimeError(f"epcsaft._core import failed: {type(exc).__name__}: {exc}") from exc
    return tuple(name for name in REQUIRED_CORE_SYMBOLS if not hasattr(core, name))


def _missing_core_symbols_or_error() -> tuple[tuple[str, ...], str | None]:
    try:
        return _missing_core_symbols(), None
    except RuntimeError as exc:
        return (), str(exc)


def _cppad_status() -> str:
    return _runtime_native_dependency_status("cppad")


def _runtime_native_dependency_status(name: str) -> str:
    try:
        import epcsaft

        info = epcsaft.runtime_build_info()
    except Exception:
        return "<unknown>"
    native_dependencies = info.get("native_dependencies", {})
    if not isinstance(native_dependencies, dict):
        return "<unknown>"
    payload = native_dependencies.get(name, {})
    if not isinstance(payload, dict):
        return "<unknown>"
    return str(payload.get("status", "<unknown>"))


def _ceres_status() -> str:
    try:
        from epcsaft_regression.native_adapter import native_ceres_backend_info
    except Exception:
        return "<extension module absent>"
    return str(native_ceres_backend_info().get("status", "<unknown>"))


def _ipopt_status() -> str:
    try:
        from epcsaft_equilibrium._native import native_ipopt_backend_info
    except Exception:
        return "<extension module absent>"
    return str(native_ipopt_backend_info().get("status", "<unknown>"))


def _ipopt_available() -> bool:
    try:
        from epcsaft_equilibrium._native import native_ipopt_backend_info
    except Exception:
        return False
    payload = native_ipopt_backend_info()
    return payload.get("status") == "enabled_available" and bool(payload.get("available"))


def _provider_sdk_state() -> tuple[dict[str, object], str | None]:
    try:
        import epcsaft

        sdk = epcsaft.provider_native_sdk()
    except Exception as exc:
        return {}, f"{type(exc).__name__}: {exc}"
    return dict(sdk), None


def _provider_sdk_missing_paths(sdk: dict[str, object]) -> tuple[str, ...]:
    required = {
        "cmake_config_path": sdk.get("cmake_config_path"),
        "source_manifest_path": sdk.get("source_manifest_path"),
        "include_root": sdk.get("include_root"),
    }
    return tuple(name for name, raw_path in required.items() if not raw_path or not Path(str(raw_path)).exists())


def _newest_source_mtime(*roots: Path) -> float | None:
    suffixes = {".cpp", ".h", ".hpp", ".cmake", ".txt", ".py"}
    newest: float | None = None
    for root in roots:
        if root.is_file() and root.suffix.lower() in suffixes:
            newest = max(newest or 0.0, root.stat().st_mtime)
            continue
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in suffixes:
                newest = max(newest or 0.0, path.stat().st_mtime)
    return newest


def _artifact_freshness(artifact: Path | None, *roots: Path) -> str:
    if artifact is None:
        return "missing"
    try:
        artifact.relative_to(REPO_ROOT)
    except ValueError:
        return "external-install"
    newest_source = _newest_source_mtime(*roots)
    if newest_source is None:
        return "unknown"
    return "current" if artifact.stat().st_mtime >= newest_source else "stale"


def _extension_native_modules_available() -> bool:
    return all(_module_path(module)[0] is not None for module in EXTENSION_NATIVE_MODULES)


def _native_module_available(state: dict[str, str]) -> bool:
    return state["path"] != "<missing>" and state["error"] == "<none>"


def _ipopt_root_provenance() -> tuple[str, str, str, str]:
    cache_root = _cmake_cache_value("EPCSAFT_IPOPT_ROOT")
    if cache_root and cache_root != "<unconfigured>":
        return (
            str(Path(cache_root).expanduser().resolve()),
            "cmake-cache:EPCSAFT_IPOPT_ROOT",
            'export EPCSAFT_IPOPT_ROOT="/path/to/ipopt"',
            _ipopt_candidate_summary(),
        )
    env_root = os.environ.get("EPCSAFT_IPOPT_ROOT") or os.environ.get("EPCSAFT_PEP517_IPOPT_ROOT")
    if env_root:
        env_name = "EPCSAFT_IPOPT_ROOT" if os.environ.get("EPCSAFT_IPOPT_ROOT") else "EPCSAFT_PEP517_IPOPT_ROOT"
        return (
            str(Path(env_root).expanduser().resolve()),
            f"env:{env_name}",
            f'export {env_name}="/path/to/ipopt"',
            _ipopt_candidate_summary(),
        )
    if _cmake_cache_value("Ipopt_DIR"):
        return (
            "<Ipopt_DIR>",
            "cmake-cache:Ipopt_DIR",
            'export Ipopt_DIR="/path/to/ipopt/lib/cmake/Ipopt"',
            _ipopt_candidate_summary(),
        )
    resolution = resolve_default_linux_ipopt_root_with_source()
    if resolution.root is not None:
        return (
            str(resolution.root),
            resolution.source,
            'export EPCSAFT_IPOPT_ROOT="/path/to/ipopt"',
            _ipopt_candidate_summary(),
        )
    return (
        "<missing>",
        "missing",
        'export EPCSAFT_IPOPT_ROOT="/path/to/ipopt"',
        _ipopt_candidate_summary(),
    )


def _ipopt_candidate_summary() -> str:
    candidates = linux_ipopt_root_candidates()
    if not candidates:
        return "<none>"
    return json.dumps(
        [{"source": source, "path": str(path)} for source, path in candidates],
        sort_keys=True,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check local ePC-SAFT development runtime health.")
    parser.add_argument(
        "--require-ipopt",
        action="store_true",
        help="Fail unless native Ipopt is compiled and available in the current runtime.",
    )
    parser.add_argument(
        "--require-provider-sdk",
        action="store_true",
        help="Fail unless provider_native_sdk() exposes complete source/CMake SDK metadata.",
    )
    parser.add_argument(
        "--require-provider-native",
        action="store_true",
        help="Fail unless provider epcsaft._core imports and exports required provider symbols.",
    )
    parser.add_argument(
        "--require-equilibrium-native",
        action="store_true",
        help="Fail unless epcsaft-equilibrium package-owned native module imports.",
    )
    parser.add_argument(
        "--require-regression-native",
        action="store_true",
        help="Fail unless epcsaft-regression package-owned native module imports.",
    )
    parser.add_argument(
        "--require-extension-native",
        action="store_true",
        help="Fail unless both extension-owned native modules import in the current runtime.",
    )
    return parser


def _cmake_cache_value(name: str, cache_path: Path = DEV_BUILD_CACHE) -> str | None:
    if not cache_path.exists():
        return None
    prefix = f"{name}:"
    for line in cache_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(prefix):
            return line.split("=", 1)[1].strip()
    return None


def _tool_path(name: str) -> str:
    if name in {"cmake", "ninja"}:
        candidate = REPO_ROOT / ".venv" / "bin" / name
        if candidate.is_file():
            return str(candidate)
    found = shutil.which(name)
    if found is not None:
        return found
    if name == "uv":
        local_uv = Path.home() / ".local" / "bin" / "uv"
        if local_uv.is_file():
            return str(local_uv)
    return "<missing>"


def _cmake_generator(cache_path: Path = DEV_BUILD_CACHE) -> str | None:
    if not cache_path.exists():
        return None
    for line in cache_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("CMAKE_GENERATOR:INTERNAL="):
            return line.split("=", 1)[1].strip()
    return None


def _ninja_migration_recommendation(generator: str | None, ninja_path: str) -> str | None:
    if generator and generator != "Ninja" and ninja_path != "<missing>":
        return "uv run python scripts/dev/build_epcsaft.py --clean --generator ninja"
    return None


def _tracked_generated_count() -> int | None:
    output = _git_output("ls-files")
    if output is None:
        return None
    count = 0
    generated_extensions = {".png", ".svg", ".csv", ".md"}
    for raw_line in output.splitlines():
        path = Path(raw_line)
        parts = path.parts
        if "out" not in parts and "runs" not in parts:
            continue
        if not parts or parts[0] not in {"analyses", "scripts", "tests", "src"}:
            continue
        if path.suffix.lower() in generated_extensions:
            count += 1
    return count


def _stale_report_state() -> str:
    stale = [path.relative_to(REPO_ROOT).as_posix() for path in STALE_TRACKED_REPORTS if path.exists()]
    return ", ".join(stale) if stale else "<none>"


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))
    runtime_env = apply_to_current_process()

    branch = _git_output("branch", "--show-current") or "<unknown>"
    head = _git_output("rev-parse", "--short", "HEAD") or "<unknown>"
    package_path, package_error = _module_path("epcsaft")
    core_path, core_error = _module_path("epcsaft._core")
    equilibrium_native_state = _module_state("epcsaft_equilibrium._native_core")
    regression_native_state = _module_state("epcsaft_regression._native_core")
    provider_sdk, provider_sdk_error = _provider_sdk_state()
    provider_sdk_missing_paths = _provider_sdk_missing_paths(provider_sdk)
    default_ipopt_root = resolve_default_linux_ipopt_root()
    ipopt_active_root, ipopt_active_root_source, ipopt_change_command, ipopt_candidates = _ipopt_root_provenance()
    ceres_root = default_system_ceres_root(REPO_ROOT)
    ceres_config_dir = default_system_ceres_config_dir(REPO_ROOT)
    resolved_ceres_config_dir = resolve_default_system_ceres_config_dir(REPO_ROOT)

    print(f"repo_root: {REPO_ROOT}")
    print(f"python: {sys.executable}")
    print(f"python_prefix: {sys.prefix}")
    print(f"git_branch: {branch}")
    print(f"git_head: {head}")
    print(f"uv: {_tool_path('uv')}")
    print(f"cmake: {_tool_path('cmake')}")
    ninja_path = _tool_path("ninja")
    print(f"ninja: {ninja_path}")
    cmake_generator = _cmake_generator()
    print(f"cmake_generator: {cmake_generator or '<missing>'}")
    generator_recommendation = _ninja_migration_recommendation(cmake_generator, ninja_path)
    print(f"build_generator_recommendation: {generator_recommendation or '<none>'}")
    print(f"epcsaft_import: {package_path if package_path else '<missing>'}")
    print(f"epcsaft_import_error: {package_error or '<none>'}")
    print(f"epcsaft_core: {core_path if core_path else '<missing>'}")
    print(f"epcsaft_core_error: {core_error or '<none>'}")
    print(
        "epcsaft_core_artifact_freshness: "
        f"{_artifact_freshness(core_path, REPO_ROOT / 'packages' / 'epcsaft' / 'src' / 'epcsaft' / 'native', REPO_ROOT / 'packages' / 'epcsaft' / 'CMakeLists.txt')}"
    )
    missing_core_symbols, missing_core_error = _missing_core_symbols_or_error() if core_path is not None else ((), None)
    print(f"epcsaft_core_missing_symbols: {', '.join(missing_core_symbols) if missing_core_symbols else '<none>'}")
    print(f"epcsaft_core_symbol_error: {missing_core_error or '<none>'}")
    print(f"provider_sdk_error: {provider_sdk_error or '<none>'}")
    print(f"provider_sdk_contract_id: {provider_sdk.get('contract_id', '<missing>')}")
    print(f"provider_sdk_source_kind: {provider_sdk.get('source_sdk_kind', '<missing>')}")
    print(f"provider_sdk_cmake_config: {provider_sdk.get('cmake_config_path', '<missing>')}")
    print(f"provider_sdk_source_manifest: {provider_sdk.get('source_manifest_path', '<missing>')}")
    print(f"provider_sdk_include_root: {provider_sdk.get('include_root', '<missing>')}")
    print(
        "provider_sdk_supported_extension_native_modules: "
        f"{json.dumps(provider_sdk.get('supported_extension_native_modules', []), sort_keys=True)}"
    )
    print(
        "provider_sdk_missing_paths: "
        f"{', '.join(provider_sdk_missing_paths) if provider_sdk_missing_paths else '<none>'}"
    )
    print(f"provider_sdk_native_contract_exported: {provider_sdk.get('native_contract_exported', '<missing>')}")
    print(f"provider_sdk_provider_only_core: {provider_sdk.get('provider_only_core', '<missing>')}")
    print(f"epcsaft_equilibrium_native_core: {equilibrium_native_state['path']}")
    print(f"epcsaft_equilibrium_native_core_error: {equilibrium_native_state['error']}")
    print(
        "epcsaft_equilibrium_native_artifact_freshness: "
        f"{_artifact_freshness(Path(equilibrium_native_state['path']) if equilibrium_native_state['path'] != '<missing>' else None, REPO_ROOT / 'packages' / 'epcsaft-equilibrium' / 'src' / 'epcsaft_equilibrium' / 'native', REPO_ROOT / 'packages' / 'epcsaft-equilibrium' / 'CMakeLists.txt')}"
    )
    print(f"epcsaft_regression_native_core: {regression_native_state['path']}")
    print(f"epcsaft_regression_native_core_error: {regression_native_state['error']}")
    print(
        "epcsaft_regression_native_artifact_freshness: "
        f"{_artifact_freshness(Path(regression_native_state['path']) if regression_native_state['path'] != '<missing>' else None, REPO_ROOT / 'packages' / 'epcsaft-regression' / 'src' / 'epcsaft_regression' / 'native', REPO_ROOT / 'packages' / 'epcsaft-regression' / 'CMakeLists.txt')}"
    )
    print(f"ceres_configured: {_cmake_cache_value('EPCSAFT_ENABLE_CERES') or '<unconfigured>'}")
    print(f"ceres_reusable_root: {ceres_root}")
    print(f"ceres_reusable_config_dir: {ceres_config_dir}")
    print(f"ceres_reusable_config_found: {resolved_ceres_config_dir if resolved_ceres_config_dir else '<missing>'}")
    print(f"ceres_reusable_version: {CERES_VERSION}")
    print(f"cppad_status: {_cppad_status()}")
    print(f"ceres_status: {_ceres_status()}")
    print(f"ipopt_configured: {_cmake_cache_value('EPCSAFT_ENABLE_IPOPT') or '<unconfigured>'}")
    print(f"ipopt_root: {_cmake_cache_value('EPCSAFT_IPOPT_ROOT') or '<unconfigured>'}")
    print(f"ipopt_default_root: {default_ipopt_root if default_ipopt_root else '<missing>'}")
    print(f"ipopt_default_candidates: {ipopt_candidates}")
    print(f"ipopt_active_root: {ipopt_active_root}")
    print(f"ipopt_active_root_source: {ipopt_active_root_source}")
    print(f"ipopt_change_command: {ipopt_change_command}")
    print(f"ipopt_runtime_lib_dir: {runtime_env.ipopt_runtime_dir if runtime_env.ipopt_runtime_dir else '<none>'}")
    print(f"ipopt_runtime_env_applied: {'true' if runtime_env.applied else 'false'}")
    print(f"ipopt_status: {_ipopt_status()}")
    print(f"stale_generated_reports: {_stale_report_state()}")
    tracked_generated = _tracked_generated_count()
    print(f"tracked_generated_run_files: {tracked_generated if tracked_generated is not None else '<unknown>'}")

    if package_path is None:
        print("install_state: missing-package")
        print("next_command: uv sync --no-install-workspace")
        return 1
    if core_path is None:
        print("install_state: missing-core")
        print("next_command: uv run python scripts/dev/build_epcsaft.py")
        return 1
    if missing_core_error is not None:
        print("install_state: broken-core-import")
        print("next_command: uv run python scripts/dev/build_epcsaft.py")
        return 1
    if missing_core_symbols:
        print("install_state: stale-core")
        print("next_command: uv run python scripts/dev/build_epcsaft.py")
        return 1
    if args.require_provider_sdk and (provider_sdk_error is not None or provider_sdk_missing_paths):
        print("install_state: missing-provider-sdk")
        print("next_command: uv run python scripts/dev/build_dist.py --parallel 1")
        return 1
    if args.require_provider_native and not _native_module_available(
        {"path": str(core_path), "error": core_error or "<none>"}
    ):
        print("install_state: missing-provider-native")
        print("next_command: uv run python scripts/dev/build_epcsaft.py --profile provider")
        return 1
    if args.require_equilibrium_native and not _native_module_available(equilibrium_native_state):
        print("install_state: missing-equilibrium-native")
        print("next_command: uv run python scripts/dev/build_epcsaft.py --profile equilibrium")
        return 1
    if args.require_regression_native and not _native_module_available(regression_native_state):
        print("install_state: missing-regression-native")
        print("next_command: uv run python scripts/dev/build_epcsaft.py --profile regression")
        return 1
    if args.require_extension_native and not _extension_native_modules_available():
        print("install_state: missing-extension-native")
        print("next_command: uv run python scripts/dev/build_epcsaft.py")
        return 1
    if args.require_ipopt and not _ipopt_available():
        print("install_state: missing-ipopt")
        print("next_command: uv run python scripts/dev/build_epcsaft.py --profile ipopt --ipopt-root <IpoptRoot>")
        return 1
    print("install_state: current")
    print("next_command: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
