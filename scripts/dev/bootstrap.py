from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROVIDER_BUILD_BACKEND_DIR = REPO_ROOT / "packages" / "epcsaft" / "build_backend"
if str(PROVIDER_BUILD_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(PROVIDER_BUILD_BACKEND_DIR))

from native_dependency_policy import default_system_ceres_config_dir  # noqa: E402
from native_dependency_policy import resolve_default_system_ceres_config_dir  # noqa: E402
from native_dependency_policy import resolve_default_windows_ipopt_sdk_root_with_source  # noqa: E402

Command = tuple[str, ...]

SYNC_COMMAND: Command = ("uv", "sync", "--no-install-project")
UV_RUN_PYTHON: Command = ("uv", "run", "--no-sync", "python")
CERES_BUILD_COMMAND: Command = (*UV_RUN_PYTHON, "scripts/dev/build_system_ceres.py", "--parallel", "2")
BASE_DOCTOR_COMMAND: Command = (
    *UV_RUN_PYTHON,
    "scripts/dev/doctor.py",
    "--require-provider-sdk",
)
PROVIDER_NATIVE_DOCTOR_COMMAND: Command = (
    *UV_RUN_PYTHON,
    "scripts/dev/doctor.py",
    "--require-provider-sdk",
    "--require-provider-native",
)
EQUILIBRIUM_NATIVE_DOCTOR_COMMAND: Command = (
    *UV_RUN_PYTHON,
    "scripts/dev/doctor.py",
    "--require-provider-sdk",
    "--require-equilibrium-native",
)
REGRESSION_NATIVE_DOCTOR_COMMAND: Command = (
    *UV_RUN_PYTHON,
    "scripts/dev/doctor.py",
    "--require-provider-sdk",
    "--require-regression-native",
)
FULL_NATIVE_DOCTOR_COMMAND: Command = (
    *UV_RUN_PYTHON,
    "scripts/dev/doctor.py",
    "--require-provider-sdk",
    "--require-extension-native",
)
INTELLIJ_COMMANDS: tuple[Command, ...] = (
    (*UV_RUN_PYTHON, "scripts/dev/configure_jetbrains_project.py", "--apply"),
    (*UV_RUN_PYTHON, "scripts/dev/configure_jetbrains_project.py", "--check"),
)
NEXT_COMMAND = "uv run python scripts/dev/validate_project.py quick"
IPOPT_CHANGE_COMMAND = '$env:EPCSAFT_IPOPT_ROOT = "C:\\path\\to\\ipopt-msvc"'
BOOTSTRAP_CURRENT_STATE = "bootstrap_state: current"
SETUP_COMMAND_SUMMARY = (
    "uv sync --no-install-project",
    "uv run --no-sync python scripts/dev/build_system_ceres.py --parallel 2",
    "uv run --no-sync python scripts/dev/build_epcsaft.py",
    "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk",
    "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-provider-native",
    "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-equilibrium-native",
    "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-regression-native",
    "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-extension-native",
    NEXT_COMMAND,
)


def _format_command(command: Command) -> str:
    return " ".join(str(part) for part in command)


def _prepend_env_path(env: dict[str, str], name: str, path: Path) -> None:
    entry = str(path.resolve())
    normalized_entry = os.path.normcase(os.path.normpath(entry))
    current = [part for part in env.get(name, "").split(os.pathsep) if part]
    kept = [part for part in current if os.path.normcase(os.path.normpath(part)) != normalized_entry]
    env[name] = os.pathsep.join([entry, *kept])


def _bootstrap_env() -> dict[str, str]:
    env = os.environ.copy()
    ipopt_resolution = resolve_default_windows_ipopt_sdk_root_with_source()
    print(f"ipopt_sdk_root: {ipopt_resolution.root if ipopt_resolution.root else '<missing>'}", flush=True)
    print(f"ipopt_sdk_root_source: {ipopt_resolution.source}", flush=True)
    print(f"ipopt_change_command: {IPOPT_CHANGE_COMMAND}", flush=True)
    ipopt_root = Path(env["EPCSAFT_IPOPT_ROOT"]).resolve() if env.get("EPCSAFT_IPOPT_ROOT") else ipopt_resolution.root
    if ipopt_root is not None:
        env.setdefault("EPCSAFT_IPOPT_ROOT", str(ipopt_root))
        ipopt_bin = ipopt_root / "bin"
        if ipopt_bin.is_dir():
            _prepend_env_path(env, "PATH", ipopt_bin)
            _prepend_env_path(env, "EPCSAFT_RUNTIME_DLL_DIRS", ipopt_bin)
            print(f"ipopt_runtime_bin: {ipopt_bin}", flush=True)
    return env


def _run(command: Command, *, dry_run: bool, env: dict[str, str]) -> int:
    print("Running:", _format_command(command), flush=True)
    if dry_run:
        return 0
    completed = subprocess.run(command, cwd=REPO_ROOT, env=env, check=False)
    return int(completed.returncode)


def _ensure_ceres(*, dry_run: bool, env: dict[str, str]) -> tuple[int, Path]:
    ceres_dir = resolve_default_system_ceres_config_dir(REPO_ROOT)
    if ceres_dir is not None:
        print(f"ceres_dir: {ceres_dir}", flush=True)
        return 0, ceres_dir

    exit_code = _run(CERES_BUILD_COMMAND, dry_run=dry_run, env=env)
    if exit_code != 0:
        return exit_code, default_system_ceres_config_dir(REPO_ROOT)
    if dry_run:
        return 0, default_system_ceres_config_dir(REPO_ROOT)

    ceres_dir = resolve_default_system_ceres_config_dir(REPO_ROOT)
    if ceres_dir is None:
        print("bootstrap_state: failed", flush=True)
        print("failed_command: uv run --no-sync python scripts/dev/build_system_ceres.py --parallel 2", flush=True)
        print(
            "failure_reason: reusable Ceres build did not produce CeresConfig.cmake under build/system-ceres/2.2.0",
            flush=True,
        )
        return 1, default_system_ceres_config_dir(REPO_ROOT)
    print(f"ceres_dir: {ceres_dir}", flush=True)
    return 0, ceres_dir


def _native_build_command(ceres_dir: Path) -> Command:
    return (
        *UV_RUN_PYTHON,
        "scripts/dev/build_epcsaft.py",
        "--use-system-ceres",
        "--ceres-dir",
        str(ceres_dir),
    )


def _profile_build_command(profile: str) -> Command:
    return (*UV_RUN_PYTHON, "scripts/dev/build_epcsaft.py", "--profile", profile)


def _provider_native_build_command() -> Command:
    return (*UV_RUN_PYTHON, "scripts/dev/build_epcsaft.py", "--clean", "--profile", "provider")


def _regression_native_build_command(ceres_dir: Path) -> Command:
    return (
        *UV_RUN_PYTHON,
        "scripts/dev/build_epcsaft.py",
        "--profile",
        "regression",
        "--use-system-ceres",
        "--ceres-dir",
        str(ceres_dir),
    )


def _run_commands(commands: tuple[Command, ...], *, dry_run: bool, env: dict[str, str]) -> int:
    for command in commands:
        exit_code = _run(command, dry_run=dry_run, env=env)
        if exit_code != 0:
            print("bootstrap_state: failed", flush=True)
            print(f"failed_command: {_format_command(command)}", flush=True)
            print(f"next_command: {_format_command(command)}", flush=True)
            return exit_code
    return 0


def _run_build(*, dry_run: bool, env: dict[str, str]) -> int:
    sync_exit_code = _run_commands((SYNC_COMMAND,), dry_run=dry_run, env=env)
    if sync_exit_code != 0:
        return sync_exit_code
    exit_code, ceres_dir = _ensure_ceres(dry_run=dry_run, env=env)
    if exit_code != 0:
        return exit_code
    return _run_commands((_native_build_command(ceres_dir),), dry_run=dry_run, env=env)


def _run_regression_native(*, dry_run: bool, env: dict[str, str]) -> int:
    sync_exit_code = _run_commands((SYNC_COMMAND,), dry_run=dry_run, env=env)
    if sync_exit_code != 0:
        return sync_exit_code
    exit_code, ceres_dir = _ensure_ceres(dry_run=dry_run, env=env)
    if exit_code != 0:
        return exit_code
    return _run_commands(
        (_regression_native_build_command(ceres_dir), REGRESSION_NATIVE_DOCTOR_COMMAND),
        dry_run=dry_run,
        env=env,
    )


def _run_step(step: str, *, dry_run: bool, env: dict[str, str]) -> int:
    if step == "smoke":
        return _run_commands((SYNC_COMMAND, BASE_DOCTOR_COMMAND), dry_run=dry_run, env=env)
    if step == "sync":
        return _run_commands((SYNC_COMMAND,), dry_run=dry_run, env=env)
    if step == "intellij":
        return _run_commands(INTELLIJ_COMMANDS, dry_run=dry_run, env=env)
    if step == "build":
        return _run_build(dry_run=dry_run, env=env)
    if step == "doctor":
        return _run_commands((BASE_DOCTOR_COMMAND,), dry_run=dry_run, env=env)
    if step == "provider-native":
        return _run_commands(
            (SYNC_COMMAND, _provider_native_build_command(), PROVIDER_NATIVE_DOCTOR_COMMAND),
            dry_run=dry_run,
            env=env,
        )
    if step == "equilibrium-native":
        return _run_commands(
            (SYNC_COMMAND, _profile_build_command("equilibrium"), EQUILIBRIUM_NATIVE_DOCTOR_COMMAND),
            dry_run=dry_run,
            env=env,
        )
    if step == "regression-native":
        return _run_regression_native(dry_run=dry_run, env=env)
    if step == "full-native":
        exit_code = _run_build(dry_run=dry_run, env=env)
        if exit_code != 0:
            return exit_code
        return _run_commands((FULL_NATIVE_DOCTOR_COMMAND,), dry_run=dry_run, env=env)
    if step == "doctorfull":
        return _run_commands((FULL_NATIVE_DOCTOR_COMMAND,), dry_run=dry_run, env=env)
    if step == "setup":
        for nested_step in ("sync", "intellij", "full-native"):
            exit_code = _run_step(nested_step, dry_run=dry_run, env=env)
            if exit_code != 0:
                return exit_code
        return 0
    raise AssertionError(f"unknown bootstrap step: {step}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bootstrap a source checkout through sync, IntelliJ metadata, native build, and doctor diagnostics.",
    )
    parser.add_argument(
        "--step",
        choices=(
            "setup",
            "smoke",
            "sync",
            "intellij",
            "build",
            "doctor",
            "provider-native",
            "equilibrium-native",
            "regression-native",
            "full-native",
            "providernative",
            "equilibriumnative",
            "regressionnative",
            "fullnative",
            "doctorfull",
        ),
        default="setup",
        help="Run one bootstrap step instead of the full setup sequence.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands that would run without executing them.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    env = _bootstrap_env()
    step_aliases = {
        "providernative": "provider-native",
        "equilibriumnative": "equilibrium-native",
        "regressionnative": "regression-native",
        "fullnative": "full-native",
    }
    step = step_aliases.get(args.step, args.step)
    exit_code = _run_step(step, dry_run=args.dry_run, env=env)
    if exit_code != 0:
        return exit_code
    state = "bootstrap_state: dry-run" if args.dry_run else BOOTSTRAP_CURRENT_STATE
    print(state, flush=True)
    print(f"next_command: {NEXT_COMMAND}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
