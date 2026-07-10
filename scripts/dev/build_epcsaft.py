from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import sysconfig
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

try:
    from scripts.dev.native_runtime_env import (
        apply_native_runtime_env,
        resolve_ipopt_root_for_build,
    )
    from scripts.dev.package_paths import PROVIDER_MODULE_DIR, PROVIDER_PYPROJECT
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from native_runtime_env import apply_native_runtime_env, resolve_ipopt_root_for_build
    from package_paths import PROVIDER_MODULE_DIR, PROVIDER_PYPROJECT

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = REPO_ROOT / "build" / "dev"
PACKAGE_DIR = PROVIDER_MODULE_DIR
LOG_FILE_NAME = "build_epcsaft.log"
STALE_LOCK_SECONDS = 120
EDITABLE_MARKER_NAME = "_editable_skbc_epcsaft.py"


class BuildProfile(NamedTuple):
    enable_ceres: bool
    build_equilibrium_native_module: bool
    build_regression_native_module: bool
    enable_ipopt: bool
    default_parallel: str
    description: str


class BuildSettings(NamedTuple):
    enable_ceres: bool
    build_equilibrium_native_module: bool
    build_regression_native_module: bool
    enable_ipopt: bool
    parallel: str | None


BUILD_PROFILES: dict[str, BuildProfile] = {
    "fast": BuildProfile(
        enable_ceres=True,
        build_equilibrium_native_module=True,
        build_regression_native_module=True,
        enable_ipopt=True,
        default_parallel="4",
        description="default source-checkout profile: provider _core plus extension-owned native modules",
    ),
    "full": BuildProfile(
        enable_ceres=True,
        build_equilibrium_native_module=True,
        build_regression_native_module=True,
        enable_ipopt=True,
        default_parallel="4",
        description="full source-checkout profile: provider _core plus extension-owned native modules",
    ),
    "ipopt": BuildProfile(
        enable_ceres=True,
        build_equilibrium_native_module=True,
        build_regression_native_module=True,
        enable_ipopt=True,
        default_parallel="4",
        description="native Ipopt source-checkout profile with extension-owned native modules",
    ),
    "equilibrium": BuildProfile(
        enable_ceres=False,
        build_equilibrium_native_module=True,
        build_regression_native_module=False,
        enable_ipopt=True,
        default_parallel="1",
        description=(
            "equilibrium native lane: provider _core plus epcsaft-equilibrium native module, "
            "Ceres/regression OFF, fresh-worktree parallelism bounded"
        ),
    ),
    "regression": BuildProfile(
        enable_ceres=True,
        build_equilibrium_native_module=False,
        build_regression_native_module=True,
        enable_ipopt=False,
        default_parallel="1",
        description=(
            "regression native lane: provider _core plus epcsaft-regression native module, "
            "Ipopt/equilibrium OFF, fresh-worktree parallelism bounded"
        ),
    ),
    "provider": BuildProfile(
        enable_ceres=False,
        build_equilibrium_native_module=False,
        build_regression_native_module=False,
        enable_ipopt=False,
        default_parallel="1",
        description=(
            "provider-only boundary profile: CppAD ON, Ceres OFF, Ipopt OFF, extension native modules OFF, "
            "fresh-worktree parallelism bounded"
        ),
    ),
}


def _run(cmd: list[str], *, env: dict[str, str]) -> None:
    print("Running:", " ".join(cmd), flush=True)
    _append_log(f"\n[{_timestamp()}] Running: {' '.join(cmd)}\n")
    completed = subprocess.Popen(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert completed.stdout is not None
    with _log_path().open("a", encoding="utf-8", errors="replace") as handle:
        for line in completed.stdout:
            print(line, end="", flush=True)
            handle.write(line)
    returncode = completed.wait()
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, cmd)


def _capture(cmd: list[str], *, env: dict[str, str]) -> str:
    return subprocess.check_output(cmd, cwd=str(REPO_ROOT), env=env, text=True).strip()


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _log_path() -> Path:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    return BUILD_DIR / LOG_FILE_NAME


def _append_log(text: str) -> None:
    with _log_path().open("a", encoding="utf-8", errors="replace") as handle:
        handle.write(text)


def _repo_tool_path(name: str) -> Path | None:
    candidate = REPO_ROOT / ".venv" / "bin" / name
    return candidate if candidate.is_file() else None


def _cmake_command() -> list[str]:
    repo_cmake = _repo_tool_path("cmake")
    if repo_cmake is None:
        raise FileNotFoundError(
            "The repo-local CMake executable is missing. Run `uv sync --no-install-workspace` "
            "to restore .venv/bin/cmake before building."
        )
    repo_python = _repo_tool_path("python")
    if repo_python is not None:
        return [str(repo_python), "-m", "cmake"]
    return [str(repo_cmake)]


def _pyproject_version() -> str:
    text = PROVIDER_PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    if not match:
        raise RuntimeError(f"Could not derive package version from {PROVIDER_PYPROJECT}")
    return match.group(1)


def _env() -> dict[str, str]:
    temp_root = REPO_ROOT / "build" / "temp"
    temp_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["TMP"] = str(temp_root.resolve())
    env["TEMP"] = str(temp_root.resolve())
    env["TMPDIR"] = str(temp_root.resolve())
    env.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")
    return env


def _configured_cxx_compiler() -> str | None:
    return _cmake_cache_value("CMAKE_CXX_COMPILER")


def _clean() -> None:
    # Remove importable extensions before deleting the reusable CMake build tree.
    for artifact in _native_artifacts():
        _remove_extension_artifact(artifact)
    for artifact in _editable_native_artifacts():
        _remove_extension_artifact(artifact)
    shutil.rmtree(BUILD_DIR, ignore_errors=True)


def _remove_extension_artifact(artifact: Path) -> None:
    try:
        artifact.unlink()
    except PermissionError as exc:
        message = (
            f"Unable to remove {artifact}. The compiled extension is probably "
            "loaded by an active Python process. Close Python terminals, IDE "
            "test runners, or parallel workers that imported epcsaft._core, "
            "then rerun the build."
        )
        raise PermissionError(message) from exc


def _configured_generator() -> str | None:
    return _cmake_cache_value("CMAKE_GENERATOR")


def _cmake_cache_value(name: str) -> str | None:
    cache = BUILD_DIR / "CMakeCache.txt"
    if not cache.exists():
        return None
    prefix = f"{name}:"
    for line in cache.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(prefix):
            return line.split("=", 1)[1].strip()
    return None


def _native_artifacts() -> list[Path]:
    return sorted(PACKAGE_DIR.glob("_core*.so"))


def _editable_package_dir() -> Path | None:
    purelib = sysconfig.get_path("purelib")
    if not purelib:
        return None
    site_root = Path(purelib)
    package_dir = site_root / "epcsaft"
    if not (site_root / EDITABLE_MARKER_NAME).is_file():
        stale_native_artifacts = sorted(package_dir.glob("_core*.so")) if package_dir.is_dir() else []
        if stale_native_artifacts:
            paths = ", ".join(str(path) for path in stale_native_artifacts)
            raise RuntimeError(
                f"Native import target exists without the required {EDITABLE_MARKER_NAME} editable marker: {paths}"
            )
        return None
    if not package_dir.is_dir():
        raise RuntimeError(f"Editable marker exists but the epcsaft package directory is missing: {package_dir}")
    return package_dir


def _editable_native_artifacts() -> list[Path]:
    package_dir = _editable_package_dir()
    if package_dir is None:
        return []
    return sorted(package_dir.glob("_core*.so"))


def _sync_editable_native_artifacts() -> None:
    package_dir = _editable_package_dir()
    if package_dir is None:
        return
    source_artifacts = _native_artifacts()
    if not source_artifacts:
        raise FileNotFoundError(f"No source-checkout native _core artifact found under {PACKAGE_DIR}.")
    package_dir.mkdir(parents=True, exist_ok=True)
    source_names = {artifact.name for artifact in source_artifacts}
    for stale in _editable_native_artifacts():
        if stale.name not in source_names:
            _remove_extension_artifact(stale)
    for artifact in source_artifacts:
        target = package_dir / artifact.name
        try:
            shutil.copy2(artifact, target)
        except PermissionError as exc:
            message = (
                f"Unable to update editable native artifact {target}. The compiled extension is probably "
                "loaded by an active Python process. Close Python terminals, IDE test runners, or parallel "
                "workers that imported epcsaft._core, then rerun the build."
            )
            raise PermissionError(message) from exc


def _last_ninja_target() -> str | None:
    log = BUILD_DIR / ".ninja_log"
    if not log.exists():
        return None
    for line in reversed(log.read_text(encoding="utf-8", errors="replace").splitlines()):
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 4:
            return parts[3]
    return None


def _repo_build_processes() -> list[str]:
    current_pid = os.getpid()
    try:
        output = subprocess.check_output(
            ["ps", "-eo", "pid=,comm=,args="],
            cwd=str(REPO_ROOT),
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except (subprocess.SubprocessError, OSError):
        return []
    processes = []
    root = str(REPO_ROOT)
    for line in output.splitlines():
        process = line.strip()
        if not process:
            continue
        parts = process.split(maxsplit=2)
        if not parts or parts[0] == str(current_pid) or root not in process:
            continue
        normalized = process.lower()
        is_build_script = "scripts/dev/build_epcsaft.py" in normalized and "--status" not in normalized
        is_cmake_build = "cmake" in normalized and "--build" in normalized
        is_ninja_build = "ninja" in normalized
        if is_build_script or is_cmake_build or is_ninja_build:
            processes.append(process)
    return processes


def _status_lines(*, stale_lock_seconds: int = STALE_LOCK_SECONDS) -> list[str]:
    generator = _configured_generator() or "<unconfigured>"
    compiler = _configured_cxx_compiler() or "<unconfigured>"
    build_type = _cmake_cache_value("CMAKE_BUILD_TYPE") or "<unconfigured>"
    build_profile = _cmake_cache_value("EPCSAFT_BUILD_PROFILE") or "<unconfigured>"
    ceres = _cmake_cache_value("EPCSAFT_ENABLE_CERES") or "<unconfigured>"
    regression_native = _cmake_cache_value("EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE") or "<unconfigured>"
    system_ceres = _cmake_cache_value("EPCSAFT_USE_SYSTEM_CERES") or "<unconfigured>"
    ceres_dir = _cmake_cache_value("Ceres_DIR") or "<unconfigured>"
    cppad = _cmake_cache_value("EPCSAFT_ENABLE_CPPAD") or "<unconfigured>"
    ipopt = _cmake_cache_value("EPCSAFT_ENABLE_IPOPT") or "<unconfigured>"
    equilibrium_native = _cmake_cache_value("EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE") or "<unconfigured>"
    system_ipopt = _cmake_cache_value("EPCSAFT_USE_SYSTEM_IPOPT") or "<unconfigured>"
    ipopt_dir = _cmake_cache_value("Ipopt_DIR") or "<unconfigured>"
    ipopt_root = _cmake_cache_value("EPCSAFT_IPOPT_ROOT") or "<unconfigured>"
    runtime_env = apply_native_runtime_env(
        {},
        cache_path=BUILD_DIR / "CMakeCache.txt",
        ipopt_enabled=ipopt.upper() == "ON",
    )
    artifacts = _native_artifacts()
    lock = BUILD_DIR / ".ninja_lock"
    lock_present = lock.exists()
    lock_age = time.time() - lock.stat().st_mtime if lock_present else None
    stale_lock = bool(lock_present and lock_age is not None and lock_age >= stale_lock_seconds)
    processes = _repo_build_processes()

    lines = [
        f"repo_root: {REPO_ROOT}",
        f"build_dir: {BUILD_DIR}",
        f"configured_generator: {generator}",
        f"configured_cxx_compiler: {compiler}",
        f"build_type: {build_type}",
        f"build_profile: {build_profile}",
        f"ceres_configured: {ceres}",
        f"regression_native_module_configured: {regression_native}",
        f"system_ceres_configured: {system_ceres}",
        f"ceres_dir: {ceres_dir}",
        f"cppad_configured: {cppad}",
        f"ipopt_configured: {ipopt}",
        f"equilibrium_native_module_configured: {equilibrium_native}",
        f"system_ipopt_configured: {system_ipopt}",
        f"ipopt_dir: {ipopt_dir}",
        f"ipopt_root: {ipopt_root}",
        f"ipopt_runtime_lib_dir: {runtime_env.ipopt_runtime_dir if runtime_env.ipopt_runtime_dir else '<none>'}",
        f"ipopt_runtime_env_applied: {'true' if runtime_env.applied else 'false'}",
        f"profile_hint: {_profile_hint(ceres=ceres, cppad=cppad, ipopt=ipopt, equilibrium_native=equilibrium_native, regression_native=regression_native)}",
        f"native_core: {'present' if artifacts else 'missing'}",
        "native_core_paths: " + (", ".join(str(path) for path in artifacts) if artifacts else "<none>"),
        f"ninja_lock: {'present' if lock_present else 'missing'}",
        f"stale_ninja_lock: {'true' if stale_lock else 'false'}",
        f"last_ninja_target: {_last_ninja_target() or '<none>'}",
        f"live_build_processes: {len(processes)}",
        f"log_file: {_log_path()}",
    ]
    lines.extend(f"live_build_process: {process}" for process in processes)
    if stale_lock:
        lines.append(
            "stale_lock_remediation: inspect live_build_process entries; stop only repo-owned build processes before retrying"
        )
    return lines


def _profile_hint(*, ceres: str, cppad: str, ipopt: str, equilibrium_native: str, regression_native: str) -> str:
    if "<unconfigured>" in {ceres, cppad, ipopt, equilibrium_native, regression_native}:
        return "<unconfigured>"
    normalized = (
        ceres.upper(),
        cppad.upper(),
        ipopt.upper(),
        equilibrium_native.upper(),
        regression_native.upper(),
    )
    if normalized == ("ON", "ON", "ON", "ON", "ON"):
        return "ipopt"
    if normalized == ("OFF", "ON", "OFF", "OFF", "OFF"):
        return "provider"
    if normalized == ("ON", "ON", "OFF", "ON", "ON"):
        return "fast/full-no-ipopt"
    return "custom"


def _print_status() -> None:
    for line in _status_lines():
        print(line)


def _warn_if_stale_build_lock() -> None:
    lines = _status_lines()
    if "stale_ninja_lock: true" not in lines:
        return
    print("Warning: stale Ninja lock detected for build/dev.", flush=True)
    for line in lines:
        if line.startswith(
            ("ninja_lock:", "stale_ninja_lock:", "last_ninja_target:", "live_build_process", "stale_lock")
        ):
            print(line, flush=True)


def _generator_args(env: dict[str, str], configured_generator: str | None = None) -> list[str]:
    requested = env.get("EPCSAFT_CMAKE_GENERATOR", "").strip().lower()
    if requested == "auto":
        requested = ""
    if requested not in {"", "ninja"}:
        raise ValueError(f"Unsupported CMake generator {requested!r}; this repo requires Ninja.")

    repo_ninja = _repo_tool_path("ninja")
    if repo_ninja is None:
        raise FileNotFoundError(
            "The repo-local Ninja executable is missing. Run `uv sync --no-install-workspace` "
            "to restore .venv/bin/ninja before building."
        )
    if configured_generator:
        if configured_generator != "Ninja":
            raise RuntimeError(
                "build/dev is already configured with "
                f"{configured_generator!r}. This repo requires 'Ninja'. "
                "Use --clean before switching to 'Ninja'."
            )
        return [f"-DCMAKE_MAKE_PROGRAM={repo_ninja.as_posix()}"]

    return ["-G", "Ninja", f"-DCMAKE_MAKE_PROGRAM={repo_ninja.as_posix()}"]


def _configure(
    env: dict[str, str],
    *,
    build_profile: str,
    enable_ceres: bool,
    build_equilibrium_native_module: bool,
    build_regression_native_module: bool,
    use_system_ceres: bool,
    ceres_dir: Path | None,
    use_system_cppad: bool,
    enable_ipopt: bool,
    use_system_ipopt: bool,
    ipopt_dir: Path | None,
    ipopt_root: Path | None,
    build_type: str,
) -> None:
    pybind11_dir = _capture([sys.executable, "-m", "pybind11", "--cmakedir"], env=env)
    cmd = [
        *_cmake_command(),
        "-S",
        str(REPO_ROOT),
        "-B",
        str(BUILD_DIR),
        "-DEPCSAFT_DEV_INPLACE=ON",
        f"-DEPCSAFT_BUILD_PROFILE={build_profile}",
        f"-DEPCSAFT_ENABLE_CERES={'ON' if enable_ceres else 'OFF'}",
        f"-DEPCSAFT_USE_SYSTEM_CERES={'ON' if use_system_ceres else 'OFF'}",
        "-DEPCSAFT_ENABLE_CPPAD=ON",
        f"-DEPCSAFT_USE_SYSTEM_CPPAD={'ON' if use_system_cppad else 'OFF'}",
        f"-DEPCSAFT_ENABLE_IPOPT={'ON' if enable_ipopt else 'OFF'}",
        f"-DEPCSAFT_USE_SYSTEM_IPOPT={'ON' if use_system_ipopt else 'OFF'}",
        f"-DEPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE={'ON' if build_equilibrium_native_module else 'OFF'}",
        f"-DEPCSAFT_BUILD_REGRESSION_NATIVE_MODULE={'ON' if build_regression_native_module else 'OFF'}",
        "-DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY",
        f"-DCMAKE_BUILD_TYPE={build_type}",
        f"-DSKBUILD_PROJECT_VERSION={_pyproject_version()}",
        f"-DPython_EXECUTABLE={sys.executable}",
        f"-Dpybind11_DIR={pybind11_dir}",
    ]
    cmd.extend(["-U", "GIT_EXECUTABLE"])
    if ceres_dir is not None:
        cmd.append(f"-DCeres_DIR={ceres_dir}")
    if ipopt_dir is not None:
        cmd.append(f"-DIpopt_DIR={ipopt_dir}")
    else:
        cmd.extend(["-U", "Ipopt_DIR"])
    if ipopt_root is not None:
        cmd.append(f"-DEPCSAFT_IPOPT_ROOT={ipopt_root}")
    else:
        cmd.append("-DEPCSAFT_IPOPT_ROOT=")
    cmd.extend(_generator_args(env, _configured_generator()))
    _run(cmd, env=env)


def _build(env: dict[str, str], parallel: str | None) -> None:
    configured_generator = _configured_generator()
    if configured_generator != "Ninja":
        raise RuntimeError(
            "build/dev is not configured with the required Ninja generator. "
            "Run `uv run --no-sync python scripts/dev/build_epcsaft.py --clean` first."
        )
    if _repo_tool_path("ninja") is None:
        raise FileNotFoundError(
            "The repo-local Ninja executable is missing. Run `uv sync --no-install-workspace` "
            "to restore .venv/bin/ninja before building."
        )
    cmd = [*_cmake_command(), "--build", str(BUILD_DIR)]
    if parallel:
        cmd.extend(["--parallel", parallel])
    _warn_if_stale_build_lock()
    _run(cmd, env=env)


def _verify_native_import(env: dict[str, str]) -> None:
    cmd = [
        sys.executable,
        "-c",
        "import epcsaft._core as core; print(core.__file__)",
    ]
    completed = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    _append_log(f"[{_timestamp()}] Running native import check\n{completed.stdout}")
    if completed.returncode != 0:
        print(completed.stdout, end="", flush=True)
        raise subprocess.CalledProcessError(completed.returncode, cmd)
    core_path = completed.stdout.strip()
    print(f"native import OK: {core_path}", flush=True)


def _timed(label: str, action) -> float:
    start = time.perf_counter()
    action()
    elapsed = time.perf_counter() - start
    print(f"Timing: {label} completed in {elapsed:.2f}s", flush=True)
    return elapsed


def _resolve_settings(args: argparse.Namespace) -> BuildSettings:
    profile = BUILD_PROFILES[args.profile]
    enable_ceres = profile.enable_ceres
    build_equilibrium_native_module = profile.build_equilibrium_native_module
    build_regression_native_module = profile.build_regression_native_module
    explicit_ipopt_config = args.use_system_ipopt or args.ipopt_dir is not None or args.ipopt_root is not None
    env_ipopt_root_available = bool(os.environ.get("EPCSAFT_IPOPT_ROOT") or os.environ.get("EPCSAFT_PEP517_IPOPT_ROOT"))
    if args.enable_ipopt is None:
        enable_ipopt = profile.enable_ipopt
        if explicit_ipopt_config or (build_equilibrium_native_module and env_ipopt_root_available):
            enable_ipopt = True
    else:
        enable_ipopt = bool(args.enable_ipopt)
        if explicit_ipopt_config:
            enable_ipopt = True
    if enable_ipopt and not build_equilibrium_native_module:
        raise ValueError("Ipopt cannot be enabled when the selected profile disables the equilibrium native module.")
    if enable_ceres and not build_regression_native_module:
        raise ValueError("Ceres cannot be enabled when the selected profile disables the regression native module.")

    parallel = args.parallel
    if parallel is None:
        parallel = profile.default_parallel
    return BuildSettings(
        enable_ceres=enable_ceres,
        build_equilibrium_native_module=build_equilibrium_native_module,
        build_regression_native_module=build_regression_native_module,
        enable_ipopt=enable_ipopt,
        parallel=parallel,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build epcsaft._core in-place with direct CMake.")
    parser.add_argument("--clean", action="store_true", help="Remove build/dev and any in-place _core artifact first.")
    parser.add_argument(
        "--configure-only", action="store_true", help="Configure the CMake dev build tree without building."
    )
    parser.add_argument(
        "--build-only", action="store_true", help="Build the existing CMake dev build tree without reconfiguring."
    )
    parser.add_argument(
        "--status", action="store_true", help="Report build/dev status without configuring or building."
    )
    parser.add_argument("--parallel", help="Optional CMake build parallelism value.")
    parser.add_argument(
        "--build-type",
        default=os.environ.get("EPCSAFT_CMAKE_BUILD_TYPE", "Release"),
        help="CMake build type for single-config generators. Defaults to Release.",
    )
    parser.add_argument(
        "--profile",
        choices=tuple(BUILD_PROFILES),
        default="fast",
        help=(
            "Native dependency profile. Source-checkout profiles build extension-owned native modules; "
            "the provider profile disables extension native modules and their solver dependencies."
        ),
    )
    parser.add_argument(
        "--generator",
        choices=("auto", "ninja"),
        default="auto",
        help="CMake generator for a new configure. The repo-local Ninja executable is required.",
    )
    parser.set_defaults(enable_ipopt=None)
    parser.add_argument(
        "--use-system-ceres",
        action="store_true",
        help="Use an installed Ceres Solver package instead of FetchContent.",
    )
    parser.add_argument(
        "--ceres-dir",
        type=Path,
        help="Directory containing CeresConfig.cmake for a prebuilt/exported Ceres package. Implies --use-system-ceres.",
    )
    parser.add_argument(
        "--use-system-cppad",
        action="store_true",
        help="Use an installed CppAD include tree instead of FetchContent.",
    )
    parser.add_argument(
        "--enable-ipopt",
        dest="enable_ipopt",
        action="store_true",
        help="Enable native Ipopt support. Uses explicit paths or Linux system discovery unless another Ipopt path is supplied.",
    )
    parser.add_argument(
        "--disable-ipopt",
        dest="enable_ipopt",
        action="store_false",
        help="Disable native Ipopt support for this build.",
    )
    parser.add_argument(
        "--use-system-ipopt",
        action="store_true",
        help="Use an installed Ipopt package. Implies --enable-ipopt.",
    )
    parser.add_argument(
        "--ipopt-dir",
        type=Path,
        help="Directory containing IpoptConfig.cmake for a native Ipopt package. Implies --use-system-ipopt.",
    )
    parser.add_argument(
        "--ipopt-root",
        type=Path,
        help=(
            "Root directory for an installed Ipopt tree with include/, lib/, and optional bin/. "
            "Implies --use-system-ipopt."
        ),
    )
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    if args.status:
        _print_status()
        return 0
    if args.clean and args.build_only:
        parser.error("--clean cannot be combined with --build-only")
    if args.configure_only and args.build_only:
        parser.error("--configure-only cannot be combined with --build-only")
    if args.ipopt_dir is not None and args.ipopt_root is not None:
        parser.error("--ipopt-dir and --ipopt-root are mutually exclusive")
    try:
        settings = _resolve_settings(args)
    except ValueError as exc:
        parser.error(str(exc))
    if not settings.enable_ceres and (args.use_system_ceres or args.ceres_dir is not None):
        parser.error("Ceres options cannot be used when the selected profile disables the regression native module.")
    use_system_ceres = bool(args.use_system_ceres or args.ceres_dir is not None)
    ipopt_root_env = os.environ.get("EPCSAFT_IPOPT_ROOT") or os.environ.get("EPCSAFT_PEP517_IPOPT_ROOT")
    ipopt_root = resolve_ipopt_root_for_build(
        args.ipopt_root if args.ipopt_root is not None else ipopt_root_env,
        enable_ipopt=settings.enable_ipopt,
        ipopt_dir=args.ipopt_dir,
        label="Ipopt root",
    )
    use_system_ipopt = bool(
        settings.enable_ipopt or args.use_system_ipopt or args.ipopt_dir is not None or ipopt_root is not None
    )

    total_start = time.perf_counter()
    if args.clean:
        _timed("clean", _clean)

    env = _env()
    if args.generator != "auto":
        env["EPCSAFT_CMAKE_GENERATOR"] = args.generator
    runtime_env = apply_native_runtime_env(env, ipopt_root=ipopt_root, ipopt_enabled=settings.enable_ipopt)
    print(
        "Build profile: "
        f"{args.profile} ({BUILD_PROFILES[args.profile].description}); "
        f"RegressionNativeModule={'ON' if settings.build_regression_native_module else 'OFF'}, "
        f"Ceres={'ON' if settings.enable_ceres else 'OFF'}, "
        f"CeresSource={('system' if use_system_ceres else 'FetchContent') if settings.enable_ceres else 'disabled'}, "
        "CppAD=ON, "
        f"EquilibriumNativeModule={'ON' if settings.build_equilibrium_native_module else 'OFF'}, "
        f"Ipopt={'ON' if settings.enable_ipopt else 'OFF'}, "
        f"IpoptSource={('system' if use_system_ipopt else 'disabled') if settings.enable_ipopt else 'disabled'}, "
        f"IpoptRoot={ipopt_root if ipopt_root is not None else '<none>'}, "
        f"IpoptRuntimeLibDir={runtime_env.ipopt_runtime_dir if runtime_env.ipopt_runtime_dir else '<none>'}, "
        f"BuildType={args.build_type}, "
        f"parallel={settings.parallel or '<generator default>'}",
        flush=True,
    )
    if not args.build_only:
        _timed(
            "configure",
            lambda: _configure(
                env,
                build_profile=args.profile,
                enable_ceres=settings.enable_ceres,
                build_equilibrium_native_module=settings.build_equilibrium_native_module,
                build_regression_native_module=settings.build_regression_native_module,
                use_system_ceres=use_system_ceres,
                ceres_dir=args.ceres_dir,
                use_system_cppad=args.use_system_cppad,
                enable_ipopt=settings.enable_ipopt,
                use_system_ipopt=use_system_ipopt,
                ipopt_dir=args.ipopt_dir,
                ipopt_root=ipopt_root,
                build_type=args.build_type,
            ),
        )
    else:
        print("Timing: configure skipped (--build-only)", flush=True)
        print("Build profile does not reconfigure an existing CMake tree when --build-only is used.", flush=True)
    if not args.configure_only:
        _timed("build", lambda: _build(env, settings.parallel))
        _timed("editable native sync", _sync_editable_native_artifacts)
        _timed("native import", lambda: _verify_native_import(env))
    else:
        print("Timing: build skipped (--configure-only)", flush=True)
    print(f"Timing: total completed in {time.perf_counter() - total_start:.2f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
