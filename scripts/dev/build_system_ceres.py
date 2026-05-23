from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
try:
    from build_backend.native_dependency_policy import CERES_VERSION, default_system_ceres_root
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(REPO_ROOT / "build_backend"))
    from native_dependency_policy import CERES_VERSION, default_system_ceres_root

CERES_REPOSITORY = "https://github.com/ceres-solver/ceres-solver.git"
DEFAULT_ROOT = default_system_ceres_root(REPO_ROOT)


def _run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(cwd or REPO_ROOT), env=env, check=True)


def _capture(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    return subprocess.check_output(cmd, cwd=str(cwd or REPO_ROOT), env=env, text=True).strip()


def _repo_tool_path(name: str) -> Path | None:
    suffix = ".exe" if os.name == "nt" and not name.lower().endswith(".exe") else ""
    executable_name = f"{name}{suffix}"
    candidates = [
        Path(sys.executable).resolve().parent / executable_name,
        REPO_ROOT / ".venv" / ("Scripts" if os.name == "nt" else "bin") / executable_name,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _cmake_command() -> list[str]:
    repo_cmake = _repo_tool_path("cmake")
    return [str(repo_cmake)] if repo_cmake is not None else ["cmake"]


def _find_vsdevcmd() -> Path | None:
    explicit = os.environ.get("EPCSAFT_VSDEVCMD")
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.is_file():
            return path
    vswhere = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / (
        "Microsoft Visual Studio/Installer/vswhere.exe"
    )
    if vswhere.is_file():
        try:
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
                stderr=subprocess.DEVNULL,
            ).strip()
        except (subprocess.CalledProcessError, OSError):
            output = ""
        if output:
            candidate = Path(output) / "Common7" / "Tools" / "VsDevCmd.bat"
            if candidate.is_file():
                return candidate
    default_path = Path(r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat")
    return default_path if default_path.is_file() else None


def _load_msvc_env_if_available(env: dict[str, str], *, generator: str) -> None:
    if os.name != "nt" or generator == "mingw" or env.get("CXX") or shutil.which("cl", path=env.get("PATH")):
        return
    vsdevcmd = _find_vsdevcmd()
    if vsdevcmd is None:
        return
    command = f'call "{vsdevcmd}" -arch=x64 -host_arch=x64 >nul && set'
    output = subprocess.check_output(command, text=True, shell=True, env=env)
    for line in output.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key] = value


def _env(*, generator: str) -> dict[str, str]:
    env = os.environ.copy()
    temp_root = REPO_ROOT / "build" / "temp"
    temp_root.mkdir(parents=True, exist_ok=True)
    env["TMP"] = str(temp_root.resolve())
    env["TEMP"] = str(temp_root.resolve())
    env["TMPDIR"] = str(temp_root.resolve())
    _load_msvc_env_if_available(env, generator=generator)
    return env


def _generator_args(env: dict[str, str], requested: str) -> list[str]:
    repo_ninja = _repo_tool_path("ninja")
    if requested == "ninja":
        args = ["-G", "Ninja"]
        if repo_ninja is not None:
            args.append(f"-DCMAKE_MAKE_PROGRAM={repo_ninja.as_posix()}")
        return args
    if requested == "mingw":
        return ["-G", "MinGW Makefiles"]
    if repo_ninja is not None:
        return ["-G", "Ninja", f"-DCMAKE_MAKE_PROGRAM={repo_ninja.as_posix()}"]
    if shutil.which("ninja", path=env.get("PATH")):
        return ["-G", "Ninja"]
    if os.name == "nt" and shutil.which("mingw32-make", path=env.get("PATH")):
        return ["-G", "MinGW Makefiles"]
    return []


def _needs_gnu_cstdint_workaround(generator_args: list[str], env: dict[str, str]) -> bool:
    if os.name != "nt":
        return False
    generator_text = " ".join(generator_args).lower()
    if "mingw" in generator_text or "msys" in generator_text:
        return True
    cxx = env.get("CXX", "")
    if cxx and Path(cxx).name.lower() in {"c++", "g++", "g++.exe", "mingw32-g++.exe", "x86_64-w64-mingw32-g++.exe"}:
        return True
    if shutil.which("cl", path=env.get("PATH")):
        return False
    return bool(shutil.which("g++", path=env.get("PATH")) or shutil.which("c++", path=env.get("PATH")))


def _write_eigen_config(config_dir: Path, env: dict[str, str]) -> None:
    include_dir = _capture([sys.executable, "-c", "import includeigen; print(includeigen.get_include())"], env=env)
    include_cmake = include_dir.replace("\\", "/")
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "Eigen3Config.cmake").write_text(
        "\n".join(
            [
                "if(NOT TARGET Eigen3::Eigen)",
                "    add_library(Eigen3::Eigen INTERFACE IMPORTED)",
                f'    set_target_properties(Eigen3::Eigen PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "{include_cmake}")',
                "endif()",
                "set(Eigen3_VERSION 3.4.0)",
                "set(Eigen3_FOUND TRUE)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (config_dir / "Eigen3ConfigVersion.cmake").write_text(
        "\n".join(
            [
                "set(PACKAGE_VERSION 3.4.0)",
                "set(PACKAGE_VERSION_COMPATIBLE TRUE)",
                "set(PACKAGE_VERSION_EXACT FALSE)",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _clone_ceres(source_dir: Path, env: dict[str, str]) -> None:
    if source_dir.exists():
        return
    source_dir.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            CERES_VERSION,
            CERES_REPOSITORY,
            str(source_dir),
        ],
        env=env,
    )


def _ceres_config_dir(install_dir: Path) -> Path:
    candidates = [
        install_dir / "lib" / "cmake" / "Ceres",
        install_dir / "lib64" / "cmake" / "Ceres",
    ]
    for candidate in candidates:
        if (candidate / "CeresConfig.cmake").is_file():
            return candidate
    return candidates[0]


def _configure_ceres(root: Path, generator: str, env: dict[str, str]) -> None:
    source_dir = root / "src"
    build_dir = root / "build"
    install_dir = root / "install"
    eigen_config_dir = root / "generated_eigen3_config"
    _write_eigen_config(eigen_config_dir, env)
    cmd = [
        *_cmake_command(),
        "-S",
        str(source_dir),
        "-B",
        str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_CXX_STANDARD=17",
        "-DCMAKE_CXX_STANDARD_REQUIRED=ON",
        "-DCMAKE_CXX_EXTENSIONS=OFF",
        "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
        f"-DCMAKE_INSTALL_PREFIX={install_dir}",
        f"-DEigen3_DIR={eigen_config_dir}",
        "-DBUILD_TESTING=OFF",
        "-DBUILD_EXAMPLES=OFF",
        "-DBUILD_BENCHMARKS=OFF",
        "-DMINIGLOG=ON",
        "-DGFLAGS=OFF",
        "-DSUITESPARSE=OFF",
        "-DEIGENSPARSE=OFF",
        "-DLAPACK=OFF",
        "-DUSE_CUDA=OFF",
        "-DSCHUR_SPECIALIZATIONS=OFF",
        "-DBUILD_SHARED_LIBS=OFF",
        "-DEXPORT_BUILD_DIR=ON",
    ]
    generator_args = _generator_args(env, generator)
    if _needs_gnu_cstdint_workaround(generator_args, env):
        cmd.append("-DCMAKE_CXX_FLAGS=-include cstdint")
    cmd.extend(generator_args)
    _run(cmd, env=env)


def _build_and_install(root: Path, parallel: str, env: dict[str, str]) -> None:
    _run(
        [*_cmake_command(), "--build", str(root / "build"), "--target", "install", "--parallel", parallel],
        env=env,
    )


def _print_usage(root: Path) -> None:
    config_dir = _ceres_config_dir(root / "install")
    print(f"CeresConfigDir: {config_dir}")
    print("Default source-checkout package builds auto-detect this path when it is compiler-compatible.")
    print("For a custom Ceres package or another checkout, set:")
    print(f'  $env:EPCSAFT_PEP517_CERES_DIR = "{config_dir}"')
    print('  $env:EPCSAFT_PEP517_USE_SYSTEM_CERES = "1"')
    print('  # Optional for external/checkout-specific reuse:')
    print('  $env:EPCSAFT_PEP517_BUILD_DIR = "$PWD\\.uv-cache\\epcsaft-build"')
    print("  uv sync --reinstall-package epcsaft")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and install a reusable local Ceres package for ePC-SAFT.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Reusable Ceres build/install root.")
    parser.add_argument("--parallel", default="4", help="CMake build parallelism.")
    parser.add_argument("--generator", choices=("auto", "ninja", "mingw"), default="auto")
    parser.add_argument("--configure-only", action="store_true")
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--print-env", action="store_true", help="Print package-install environment variables.")
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.configure_only and args.build_only:
        raise SystemExit("--configure-only cannot be combined with --build-only")
    root = args.root.expanduser().resolve()
    env = _env(generator=args.generator)
    if args.print_env:
        _print_usage(root)
        return 0
    if not args.build_only:
        _clone_ceres(root / "src", env)
        _configure_ceres(root, args.generator, env)
    if not args.configure_only:
        _build_and_install(root, args.parallel, env)
    _print_usage(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
