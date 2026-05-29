from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

try:
    from scripts.dev.package_paths import (
        EQUILIBRIUM_PACKAGE_DIR,
        PROVIDER_BUILD_BACKEND_DIR,
        PROVIDER_PACKAGE_DIR,
        REGRESSION_PACKAGE_DIR,
        REPO_ROOT,
    )
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from package_paths import (
        EQUILIBRIUM_PACKAGE_DIR,
        PROVIDER_BUILD_BACKEND_DIR,
        PROVIDER_PACKAGE_DIR,
        REGRESSION_PACKAGE_DIR,
        REPO_ROOT,
    )

if str(PROVIDER_BUILD_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(PROVIDER_BUILD_BACKEND_DIR))

from native_dependency_policy import (  # noqa: E402
    ipopt_root_prefers_msvc,
    resolve_default_system_ceres_config_dir,
    validate_ceres_dir,
)

DIST_ROOT = REPO_ROOT / "dist"
BUILD_ROOT = REPO_ROOT / "build" / "xd"
BUILD_MODE_DIRS = {
    "monorepo": "m",
    "installed-provider": "i",
}
BUILD_PACKAGE_DIRS = {
    "epcsaft-equilibrium": "eq",
    "epcsaft-regression": "rg",
}
EXTENSION_PACKAGES = {
    "epcsaft-equilibrium": {
        "package_dir": EQUILIBRIUM_PACKAGE_DIR,
        "wheel_prefix": "epcsaft_equilibrium-",
        "module": "epcsaft_equilibrium",
    },
    "epcsaft-regression": {
        "package_dir": REGRESSION_PACKAGE_DIR,
        "wheel_prefix": "epcsaft_regression-",
        "module": "epcsaft_regression",
    },
}


def _run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, check=True)


def _env(parallel: str | None) -> dict[str, str]:
    temp_root = BUILD_ROOT / "tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["TMP"] = str(temp_root.resolve())
    env["TEMP"] = str(temp_root.resolve())
    env["TMPDIR"] = str(temp_root.resolve())
    env["EPCSAFT_SANDBOX_SAFE_TEMPFILE"] = "1"
    if parallel:
        env["CMAKE_BUILD_PARALLEL_LEVEL"] = str(parallel)
    return env


def _configure_reusable_ceres(env: dict[str, str], explicit_ceres_dir: Path | None = None) -> None:
    if explicit_ceres_dir is not None:
        ceres_dir = validate_ceres_dir(str(explicit_ceres_dir), env_name="--ceres-dir")
        env["EPCSAFT_PEP517_CERES_DIR"] = str(ceres_dir)
        print(f"ceres_reuse: explicit --ceres-dir {ceres_dir}", flush=True)
        return
    raw_ceres_dir = env.get("EPCSAFT_PEP517_CERES_DIR") or env.get("Ceres_DIR")
    if raw_ceres_dir:
        ceres_dir = validate_ceres_dir(raw_ceres_dir)
        env["EPCSAFT_PEP517_CERES_DIR"] = str(ceres_dir)
        print(f"ceres_reuse: explicit env {ceres_dir}", flush=True)
        return
    default_ceres_dir = resolve_default_system_ceres_config_dir(REPO_ROOT)
    if default_ceres_dir is not None:
        env["EPCSAFT_PEP517_CERES_DIR"] = str(default_ceres_dir)
        print(f"ceres_reuse: repo-local cache {default_ceres_dir}", flush=True)
        return
    print("ceres_reuse: repo-local cache missing; regression package build will use Ceres FetchContent", flush=True)


def _find_vsdevcmd() -> Path:
    explicit = os.environ.get("EPCSAFT_VSDEVCMD")
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.is_file():
            return path
    vswhere = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / (
        "Microsoft Visual Studio/Installer/vswhere.exe"
    )
    if vswhere.is_file():
        output = subprocess.check_output(
            [
                str(vswhere),
                "-latest",
                "-products",
                "*",
                "-requires",
                "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                "-property",
                "installationPath",
            ],
            text=True,
        ).strip()
        if output:
            candidate = Path(output) / "Common7" / "Tools" / "VsDevCmd.bat"
            if candidate.is_file():
                return candidate
    default_path = Path(r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat")
    if default_path.is_file():
        return default_path
    raise FileNotFoundError("MSVC toolchain requested, but VsDevCmd.bat was not found.")


def _load_msvc_env(env: dict[str, str]) -> dict[str, str]:
    vsdevcmd = _find_vsdevcmd()
    command = f'call "{vsdevcmd}" -arch=x64 -host_arch=x64 >nul && set'
    output = subprocess.check_output(command, env=env, text=True, shell=True)
    updated = env.copy()
    for line in output.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        updated[key] = value
    return updated


def _configure_extension_toolchain(env: dict[str, str], packages: list[str], ipopt_root: Path) -> dict[str, str]:
    if os.name != "nt" or "epcsaft-equilibrium" not in packages:
        return env
    if not ipopt_root_prefers_msvc(ipopt_root):
        return env
    updated = _load_msvc_env(env)
    updated.setdefault("CMAKE_GENERATOR", "Ninja")
    print("toolchain: loaded MSVC environment for MSVC Ipopt SDK", flush=True)
    return updated


def _newest_wheel(prefix: str) -> Path:
    wheels = sorted(DIST_ROOT.glob(f"{prefix}*.whl"), key=lambda path: path.stat().st_mtime_ns)
    if not wheels:
        raise RuntimeError(f"uv build completed but no wheel matching {prefix}*.whl was found in dist/")
    return wheels[-1]


def _provider_wheel() -> Path:
    wheels = sorted(
        (
            path
            for path in DIST_ROOT.glob("epcsaft-*.whl")
            if not path.name.startswith(("epcsaft_equilibrium-", "epcsaft_regression-"))
        ),
        key=lambda path: path.stat().st_mtime_ns,
    )
    if not wheels:
        raise RuntimeError("No provider epcsaft wheel found in dist/. Run scripts/dev/build_dist.py first.")
    return wheels[-1]


def _clean_extension_artifacts() -> None:
    DIST_ROOT.mkdir(exist_ok=True)
    for pattern in ("epcsaft_equilibrium-*", "epcsaft_regression-*"):
        for artifact in DIST_ROOT.glob(pattern):
            artifact.unlink()


def _install_provider_for_sdk(provider_wheel: Path, env: dict[str, str]) -> Path:
    target = BUILD_ROOT / "sdk"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    _run(["uv", "pip", "install", "--target", str(target), str(provider_wheel)], env=env)
    return target


def _provider_sdk_from_target(target: Path, env: dict[str, str]) -> dict[str, object]:
    code = f"""
import json
import sys
sys.path.insert(0, {str(target)!r})
import epcsaft
print(json.dumps(epcsaft.provider_native_sdk(), sort_keys=True))
"""
    result = subprocess.run(
        [sys.executable, "-S", "-c", code],
        cwd=str(REPO_ROOT),
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def _build_package(
    package_name: str,
    *,
    mode: str,
    env: dict[str, str],
    ipopt_root: Path,
    provider_sdk_config: Path | None,
) -> Path:
    metadata = EXTENSION_PACKAGES[package_name]
    package_env = env.copy()
    package_env["EPCSAFT_PROVIDER_SDK_MODE"] = mode
    build_dir = BUILD_ROOT / BUILD_MODE_DIRS[mode] / BUILD_PACKAGE_DIRS[package_name]
    shutil.rmtree(build_dir, ignore_errors=True)
    package_env["EPCSAFT_PEP517_BUILD_DIR"] = str(build_dir.resolve())
    if provider_sdk_config is not None:
        package_env["EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG"] = str(provider_sdk_config)
    if package_name == "epcsaft-equilibrium":
        if not ipopt_root.is_dir():
            raise RuntimeError(f"Production epcsaft-equilibrium build proof requires Ipopt SDK root: {ipopt_root}")
        package_env["EPCSAFT_PEP517_IPOPT_ROOT"] = str(ipopt_root.resolve())
    _run(["uv", "build", str(metadata["package_dir"])], env=package_env)
    return _newest_wheel(str(metadata["wheel_prefix"]))


def _sync_extension_artifacts_to_source(package_names: list[str], extension_wheels: list[Path]) -> None:
    for package_name, wheel in zip(package_names, extension_wheels, strict=True):
        metadata = EXTENSION_PACKAGES[package_name]
        module = str(metadata["module"])
        package_source = Path(metadata["package_dir"]) / "src" / module
        for stale in [*package_source.glob("_native_core*.pyd"), *package_source.glob("*.dll")]:
            stale.unlink()
        with zipfile.ZipFile(wheel) as archive:
            for member in archive.namelist():
                path = Path(member)
                if len(path.parts) != 2 or path.parts[0] != module:
                    continue
                if path.suffix.lower() not in {".pyd", ".dll"}:
                    continue
                target = package_source / path.name
                target.write_bytes(archive.read(member))


def _smoke_extension_wheels(
    provider_wheel: Path,
    extension_wheels: list[Path],
    package_names: list[str],
    env: dict[str, str],
) -> None:
    target = BUILD_ROOT / "smoke"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    _run(["uv", "pip", "install", "--target", str(target), str(provider_wheel), *map(str, extension_wheels)], env=env)
    import_lines = [
        "import epcsaft",
        "import epcsaft._core",
    ]
    for package_name in package_names:
        module = EXTENSION_PACKAGES[package_name]["module"]
        import_lines.append(f"import {module}")
        import_lines.append(f"import {module}._native_core")
    code = f"""
import sys
sys.path.insert(0, {str(target)!r})
{chr(10).join(import_lines)}
sdk = epcsaft.provider_native_sdk()
assert sdk["provider_only_core"] is True
assert sdk["source_sdk_kind"] == "source_cmake_sdk"
assert sdk["cmake_config_path"]
assert sdk["source_manifest_path"]
print("extension wheel smoke ok")
"""
    _run([sys.executable, "-S", "-c", code], env=env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["monorepo", "installed-provider"], required=True)
    parser.add_argument("--parallel", default=os.environ.get("EPCSAFT_BUILD_DIST_PARALLEL", "1"))
    parser.add_argument("--ipopt-root", default=os.environ.get("EPCSAFT_IPOPT_ROOT", ""))
    parser.add_argument(
        "--ceres-dir",
        type=Path,
        help="Directory containing CeresConfig.cmake for reusable regression extension package builds.",
    )
    parser.add_argument(
        "--package",
        choices=sorted(EXTENSION_PACKAGES),
        action="append",
        help="Build one extension package. Defaults to both packages.",
    )
    parser.add_argument("--skip-smoke", action="store_true")
    args = parser.parse_args()

    packages = args.package or sorted(EXTENSION_PACKAGES)
    env = _env(args.parallel)
    _configure_reusable_ceres(env, args.ceres_dir)
    ipopt_root = Path(args.ipopt_root).expanduser()
    env = _configure_extension_toolchain(env, packages, ipopt_root)
    ipopt_bin = ipopt_root / "bin"
    if ipopt_bin.is_dir():
        env["PATH"] = os.pathsep.join([str(ipopt_bin.resolve()), env.get("PATH", "")])
    provider_wheel = _provider_wheel()
    _clean_extension_artifacts()
    provider_sdk_config = PROVIDER_PACKAGE_DIR / "src" / "epcsaft" / "native_sdk" / "provider_native_sdk_v1" / "epcsaft_provider_sdk.cmake"
    if not provider_sdk_config.is_file():
        raise RuntimeError(f"Monorepo provider SDK CMake config is missing: {provider_sdk_config}")
    if args.mode == "installed-provider":
        provider_target = _install_provider_for_sdk(provider_wheel, env)
        sdk = _provider_sdk_from_target(provider_target, env)
        provider_sdk_config = Path(str(sdk["cmake_config_path"])).resolve()
        if not provider_sdk_config.is_file():
            raise RuntimeError(f"Installed provider SDK did not expose a CMake config file: {provider_sdk_config}")

    extension_wheels = [
        _build_package(
            package_name,
            mode=args.mode,
            env=env,
            ipopt_root=ipopt_root,
            provider_sdk_config=provider_sdk_config,
        )
        for package_name in packages
    ]
    _sync_extension_artifacts_to_source(packages, extension_wheels)
    if not args.skip_smoke:
        _smoke_extension_wheels(provider_wheel, extension_wheels, packages, env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
