from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
try:
    from scripts.dev.package_paths import PROVIDER_BUILD_BACKEND_DIR
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    from package_paths import PROVIDER_BUILD_BACKEND_DIR

sys.path.insert(0, str(PROVIDER_BUILD_BACKEND_DIR))
from native_dependency_policy import CERES_VERSION, default_system_ceres_root

CERES_REPOSITORY = "https://github.com/ceres-solver/ceres-solver.git"
DEFAULT_ROOT = default_system_ceres_root(REPO_ROOT)


def _run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print("Running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(cwd or REPO_ROOT), env=env, check=True)


def _capture(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    return subprocess.check_output(cmd, cwd=str(cwd or REPO_ROOT), env=env, text=True).strip()


def _repo_tool_path(name: str) -> Path | None:
    candidate = REPO_ROOT / ".venv" / "bin" / name
    return candidate if candidate.is_file() else None


def _cmake_command() -> list[str]:
    repo_cmake = _repo_tool_path("cmake")
    if repo_cmake is None:
        raise FileNotFoundError(
            "The repo-local CMake executable is missing. Run `uv sync --no-install-workspace` "
            "to restore .venv/bin/cmake before building Ceres."
        )
    repo_python = _repo_tool_path("python")
    if repo_python is not None:
        return [str(repo_python), "-m", "cmake"]
    return [str(repo_cmake)]


def _env(*, generator: str) -> dict[str, str]:
    env = os.environ.copy()
    temp_root = REPO_ROOT / "build" / "temp"
    temp_root.mkdir(parents=True, exist_ok=True)
    env["TMP"] = str(temp_root.resolve())
    env["TEMP"] = str(temp_root.resolve())
    env["TMPDIR"] = str(temp_root.resolve())
    return env


def _generator_args(_env: dict[str, str], _requested: str) -> list[str]:
    repo_ninja = _repo_tool_path("ninja")
    if repo_ninja is None:
        raise FileNotFoundError(
            "The repo-local Ninja executable is missing. Run `uv sync --no-install-workspace` "
            "to restore .venv/bin/ninja before building Ceres."
        )
    return ["-G", "Ninja", f"-DCMAKE_MAKE_PROGRAM={repo_ninja.as_posix()}"]


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
    searched = ", ".join(str(candidate / "CeresConfig.cmake") for candidate in candidates)
    raise FileNotFoundError(f"Ceres installation did not produce CeresConfig.cmake; searched: {searched}")


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
    cmd.extend(generator_args)
    _run(cmd, env=env)


def _build_and_install(root: Path, parallel: str, env: dict[str, str]) -> None:
    if _repo_tool_path("ninja") is None:
        raise FileNotFoundError(
            "The repo-local Ninja executable is missing. Run `uv sync --no-install-workspace` "
            "to restore .venv/bin/ninja before building Ceres."
        )
    _run(
        [*_cmake_command(), "--build", str(root / "build"), "--target", "install", "--parallel", parallel],
        env=env,
    )


def _print_usage(root: Path) -> None:
    config_dir = _ceres_config_dir(root / "install")
    print(f"CeresConfigDir: {config_dir}")
    print("Use this package with the source-checkout native build:")
    print(f"  uv run python scripts/dev/build_epcsaft.py --use-system-ceres --ceres-dir {config_dir}")
    print("Use this package with extension PEP 517 builds:")
    print(f'  export EPCSAFT_PEP517_CERES_DIR="{config_dir}"')
    print("Optional for external/checkout-specific reuse:")
    print(f'  export EPCSAFT_PEP517_BUILD_DIR="{(REPO_ROOT / "build" / "pep517").resolve()}"')
    print("Regression extension builds auto-detect this repo-local reusable Ceres package when it exists.")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and install a reusable local Ceres package for ePC-SAFT.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Reusable Ceres build/install root.")
    parser.add_argument("--parallel", default="4", help="CMake build parallelism.")
    parser.add_argument("--generator", choices=("auto", "ninja"), default="auto")
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
