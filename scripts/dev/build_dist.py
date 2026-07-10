from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DIST_ROOT = REPO_ROOT / "dist"

try:
    from scripts.dev.package_paths import PROVIDER_PACKAGE_DIR
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from package_paths import PROVIDER_PACKAGE_DIR

try:
    from native_runtime_env import ipopt_runtime_lib_dir, resolve_default_linux_ipopt_root
except ImportError:  # pragma: no cover - supports importing this module as scripts.dev.build_dist
    from scripts.dev.native_runtime_env import ipopt_runtime_lib_dir, resolve_default_linux_ipopt_root


def _run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, check=True)


def _remove_path_entry(raw: str, entry: Path) -> str:
    normalized_entry = os.path.normcase(os.path.normpath(str(entry.resolve())))
    return os.pathsep.join(
        part for part in raw.split(os.pathsep) if part and os.path.normcase(os.path.normpath(part)) != normalized_entry
    )


def _strip_ipopt_env(env: dict[str, str]) -> None:
    ipopt_roots = [
        Path(raw).expanduser() for name in ("EPCSAFT_IPOPT_ROOT", "EPCSAFT_PEP517_IPOPT_ROOT") if (raw := env.get(name))
    ]
    for name in (
        "EPCSAFT_IPOPT_ROOT",
        "EPCSAFT_PEP517_IPOPT_ROOT",
        "EPCSAFT_PEP517_IPOPT_DIR",
        "EPCSAFT_PEP517_ENABLE_IPOPT",
        "EPCSAFT_PEP517_USE_SYSTEM_IPOPT",
        "Ipopt_DIR",
    ):
        env.pop(name, None)
    default_ipopt = resolve_default_linux_ipopt_root()
    if default_ipopt is not None:
        ipopt_roots.append(default_ipopt)
    for ipopt_root in ipopt_roots:
        lib_dir = ipopt_runtime_lib_dir(ipopt_root)
        if lib_dir is not None:
            env["LD_LIBRARY_PATH"] = _remove_path_entry(env.get("LD_LIBRARY_PATH", ""), lib_dir)


def _apply_persistent_pep517_build_dir(env: dict[str, str]) -> None:
    if env.get("EPCSAFT_PEP517_BUILD_DIR"):
        return
    env["EPCSAFT_PEP517_BUILD_DIR"] = str((REPO_ROOT / "build" / "pep517" / "provider-only").resolve())


def _print_build_env_summary(env: dict[str, str]) -> None:
    print("Provider package build: Ceres OFF, Ipopt OFF, extension native modules OFF.", flush=True)
    print(f"PEP 517 build directory: {env['EPCSAFT_PEP517_BUILD_DIR']}", flush=True)


def _env(parallel: str | None = None) -> dict[str, str]:
    temp_root = REPO_ROOT / "build" / "dist-temp"
    temp_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["TMP"] = str(temp_root.resolve())
    env["TEMP"] = str(temp_root.resolve())
    env["TMPDIR"] = str(temp_root.resolve())
    _strip_ipopt_env(env)
    _apply_persistent_pep517_build_dir(env)
    if parallel:
        env["CMAKE_BUILD_PARALLEL_LEVEL"] = str(parallel)
    return env


def _uv_build_command() -> list[str]:
    cmd = ["uv", "build", str(PROVIDER_PACKAGE_DIR)]
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
            name for name in archive.namelist() if any(fragment in f"/{name}".lower() for fragment in blocked_fragments)
        ]
    if offenders:
        sample = "\n".join(f"  - {name}" for name in offenders[:20])
        raise RuntimeError(
            "wheel contains Ceres development artifacts; vendored solver dependencies must not be installed into epcsaft:\n"
            f"{sample}"
        )


def _smoke_wheel(wheel: Path) -> None:
    target = REPO_ROOT / "build" / "wheel-smoke-target"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    smoke_env = _env()
    _run(["uv", "pip", "install", "--target", str(target), str(wheel)], env=smoke_env)
    code = f"""
import sys
sys.path.insert(0, {str(target)!r})
import numpy as np
import epcsaft
import epcsaft._core
from epcsaft import Mixture, ParameterSet, State
from epcsaft.model.parameters import PureRecord
sdk = epcsaft.provider_native_sdk()
mixture = Mixture(ParameterSet.from_records([
    PureRecord(
        component="Methane",
        molar_mass=16.043e-3,
        m=1.0,
        sigma=3.7039,
        epsilon_k=150.03,
        charge=0.0,
        epsilon_k_ab=0.0,
        kappa_ab=0.0,
        association_scheme=None,
        relative_permittivity=1.0,
        born_diameter=0.0,
        solvation_factor=1.0,
    ),
]))
state = State(mixture, T=300.0, x=np.asarray([1.0]), rho=100.0)
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
        help="CMake build parallelism for isolated PEP 517 builds. Defaults to 1 for reproducible package proofs.",
    )
    args = parser.parse_args()

    _clean_dist()
    build_env = _env(args.parallel)
    _print_build_env_summary(build_env)
    _run(
        _uv_build_command(),
        env=build_env,
    )
    wheel = _newest_wheel()
    _assert_wheel_has_no_solver_dev_artifacts(wheel)
    if not args.skip_smoke:
        _smoke_wheel(wheel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
