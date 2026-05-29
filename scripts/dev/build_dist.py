from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DIST_ROOT = REPO_ROOT / "dist"
TEMPFILE_SITE = REPO_ROOT / "scripts" / "sandbox_tempfile_site"

try:
    from native_runtime_env import apply_native_runtime_env, resolve_default_windows_ipopt_sdk_root
except ImportError:  # pragma: no cover - supports importing this module as scripts.dev.build_dist
    from scripts.dev.native_runtime_env import apply_native_runtime_env, resolve_default_windows_ipopt_sdk_root

try:
    from build_backend.native_dependency_policy import resolve_default_system_ceres_config_dir
except ModuleNotFoundError:  # pragma: no cover - direct script execution from scripts/dev
    sys.path.insert(0, str(REPO_ROOT / "build_backend"))
    from native_dependency_policy import resolve_default_system_ceres_config_dir


def _run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, check=True)


def _remove_path_entry(raw: str, entry: Path) -> str:
    normalized_entry = os.path.normcase(os.path.normpath(str(entry.resolve())))
    return os.pathsep.join(
        part
        for part in raw.split(os.pathsep)
        if part and os.path.normcase(os.path.normpath(part)) != normalized_entry
    )


def _strip_ipopt_env(env: dict[str, str]) -> None:
    for name in (
        "EPCSAFT_IPOPT_ROOT",
        "EPCSAFT_PEP517_IPOPT_ROOT",
        "EPCSAFT_PEP517_IPOPT_DIR",
        "EPCSAFT_PEP517_ENABLE_IPOPT",
        "EPCSAFT_PEP517_USE_SYSTEM_IPOPT",
        "EPCSAFT_RUNTIME_DLL_DIRS",
        "Ipopt_DIR",
    ):
        env.pop(name, None)
    default_ipopt = resolve_default_windows_ipopt_sdk_root()
    if default_ipopt is None:
        return
    bin_dir = default_ipopt / "bin"
    if not bin_dir.is_dir():
        return
    env["PATH"] = _remove_path_entry(env.get("PATH", ""), bin_dir)


def _truthy_env_value(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _apply_default_system_ceres_env(env: dict[str, str]) -> Path | None:
    if (
        env.get("EPCSAFT_PEP517_CERES_DIR")
        or env.get("Ceres_DIR")
        or _truthy_env_value(env.get("EPCSAFT_PEP517_USE_SYSTEM_CERES"))
    ):
        return None
    ceres_dir = resolve_default_system_ceres_config_dir(REPO_ROOT)
    if ceres_dir is None:
        return None
    env["EPCSAFT_PEP517_CERES_DIR"] = str(ceres_dir)
    env["EPCSAFT_PEP517_USE_SYSTEM_CERES"] = "1"
    return ceres_dir


def _path_token(path: str) -> str:
    normalized = os.path.normcase(os.path.normpath(path))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def _apply_persistent_pep517_build_dir(env: dict[str, str], *, ipopt_enabled: bool) -> None:
    if env.get("EPCSAFT_PEP517_BUILD_DIR"):
        return
    profile = "local-ipopt" if ipopt_enabled else "no-ipopt"
    ceres_dir = env.get("EPCSAFT_PEP517_CERES_DIR") or env.get("Ceres_DIR")
    ceres_profile = f"system-ceres-{_path_token(ceres_dir)}" if ceres_dir else "fetchcontent-ceres"
    env["EPCSAFT_PEP517_BUILD_DIR"] = str((REPO_ROOT / "build" / "pep517" / f"{profile}-{ceres_profile}").resolve())


def _print_build_env_summary(env: dict[str, str]) -> None:
    ceres_dir = env.get("EPCSAFT_PEP517_CERES_DIR") or env.get("Ceres_DIR")
    if ceres_dir:
        print(f"Using reusable Ceres package: {ceres_dir}", flush=True)
    elif _truthy_env_value(env.get("EPCSAFT_PEP517_USE_SYSTEM_CERES")):
        print("Using system Ceres from the CMake package search path.", flush=True)
    else:
        print("Using Ceres FetchContent; install reusable Ceres to skip compiling Ceres.", flush=True)
    print(f"PEP 517 build directory: {env['EPCSAFT_PEP517_BUILD_DIR']}", flush=True)


def _env(parallel: str | None = None, *, ipopt_enabled: bool = False) -> dict[str, str]:
    temp_root = REPO_ROOT / "build" / "dist-temp"
    temp_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["TMP"] = str(temp_root.resolve())
    env["TEMP"] = str(temp_root.resolve())
    env["TMPDIR"] = str(temp_root.resolve())
    env["EPCSAFT_SANDBOX_SAFE_TEMPFILE"] = "1"
    existing_pythonpath = env.get("PYTHONPATH")
    site_path = str(TEMPFILE_SITE.resolve())
    env["PYTHONPATH"] = site_path if not existing_pythonpath else os.pathsep.join([site_path, existing_pythonpath])
    if ipopt_enabled:
        apply_native_runtime_env(env, ipopt_enabled=True)
    else:
        _strip_ipopt_env(env)
    _apply_default_system_ceres_env(env)
    _apply_persistent_pep517_build_dir(env, ipopt_enabled=ipopt_enabled)
    if parallel:
        env["CMAKE_BUILD_PARALLEL_LEVEL"] = str(parallel)
    return env


def _uv_build_command(*, with_local_ipopt: bool) -> list[str]:
    cmd = ["uv", "build"]
    if with_local_ipopt:
        return cmd
    return [
        *cmd,
        "--config-setting",
        "cmake.define.EPCSAFT_ENABLE_CERES=OFF",
        "--config-setting",
        "cmake.define.EPCSAFT_ENABLE_IPOPT=OFF",
        "--config-setting",
        "cmake.define.EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE=OFF",
        "--config-setting",
        "cmake.define.EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE=OFF",
        "--config-setting",
        "cmake.define.EPCSAFT_USE_SYSTEM_IPOPT=OFF",
        "--config-setting",
        "cmake.define.EPCSAFT_IPOPT_ROOT=",
    ]


def _clean_dist() -> None:
    DIST_ROOT.mkdir(exist_ok=True)
    for artifact in DIST_ROOT.glob("epcsaft-*"):
        artifact.unlink()


def _newest_wheel() -> Path:
    wheels = sorted(DIST_ROOT.glob("epcsaft-*.whl"), key=lambda path: path.stat().st_mtime_ns)
    if not wheels:
        raise RuntimeError("uv build completed but no epcsaft wheel was found in dist/")
    return wheels[-1]


def _assert_wheel_has_no_solver_dev_artifacts(wheel: Path) -> None:
    blocked_fragments = (
        "/include/ceres/",
        "/lib/cmake/ceres/",
        "/libceres",
        "numeric" + "_diff",
    )
    with zipfile.ZipFile(wheel) as archive:
        offenders = [
            name
            for name in archive.namelist()
            if any(fragment in f"/{name}".lower() for fragment in blocked_fragments)
        ]
    if offenders:
        sample = "\n".join(f"  - {name}" for name in offenders[:20])
        raise RuntimeError(
            "wheel contains Ceres development artifacts; vendored solver dependencies must not be installed into epcsaft:\n"
            f"{sample}"
        )


def _smoke_wheel(wheel: Path, *, with_local_ipopt: bool) -> None:
    target = REPO_ROOT / "build" / "wheel-smoke-target"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    smoke_env = _env(ipopt_enabled=with_local_ipopt)
    _run(["uv", "pip", "install", "--target", str(target), str(wheel)], env=smoke_env)
    code = f"""
import sys
sys.path.insert(0, {str(target)!r})
import numpy as np
import epcsaft
import epcsaft._core
from epcsaft import Mixture, ParameterSet, State
sdk = epcsaft.provider_native_sdk()
mixture = Mixture(ParameterSet.from_dict(
    {{
        "m": np.asarray([1.0]),
        "s": np.asarray([3.7039]),
        "e": np.asarray([150.03]),
        "MW": np.asarray([16.043e-3]),
    }},
    species=["Methane"],
))
state = State(mixture, T=300.0, x=np.asarray([1.0]), rho=100.0)
if not {with_local_ipopt!r}:
    assert sdk["provider_only_core"] is True
    assert sdk["equilibrium_native_enabled"] is False
    assert sdk["regression_native_enabled"] is False
    blocked = (
        "_native_equilibrium_selector_contract",
        "_native_equilibrium_selector_route_result",
        "_native_ipopt_quadratic_smoke",
        "_native_ipopt_smoke",
        "_native_nlp_shape_validation_smoke",
        "_native_second_order_assembly_smoke",
        "_native_variable_transform_smoke",
        "_native_ceres_smoke",
        "_fit_pure_neutral_native_ceres",
        "_fit_generic_native_ceres",
    )
    leaked = [name for name in blocked if hasattr(epcsaft._core, name)]
    assert leaked == [], leaked
print("wheel smoke ok", epcsaft.__file__, state.z())
"""
    _run([sys.executable, "-S", "-c", code], env=smoke_env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-smoke", action="store_true")
    parser.add_argument(
        "--parallel",
        default=os.environ.get("EPCSAFT_BUILD_DIST_PARALLEL", "1"),
        help="CMake build parallelism for isolated PEP 517 builds. Defaults to 1 to avoid Windows Ceres OOMs.",
    )
    parser.add_argument(
        "--with-local-ipopt",
        action="store_true",
        help=(
            "Build artifacts against the local Ipopt SDK. The default release baseline disables Ipopt "
            "so wheels do not require local Ipopt runtime DLLs."
        ),
    )
    args = parser.parse_args()

    _clean_dist()
    build_env = _env(args.parallel, ipopt_enabled=args.with_local_ipopt)
    _print_build_env_summary(build_env)
    _run(
        _uv_build_command(with_local_ipopt=args.with_local_ipopt),
        env=build_env,
    )
    wheel = _newest_wheel()
    _assert_wheel_has_no_solver_dev_artifacts(wheel)
    if not args.skip_smoke:
        _smoke_wheel(wheel, with_local_ipopt=args.with_local_ipopt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
