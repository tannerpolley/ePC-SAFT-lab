from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import tomllib

REPO_ROOT = Path(__file__).resolve().parents[3]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _toml(path: str) -> dict:
    return tomllib.loads(_read(path))


def _run_git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _write_executable(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def _setup_script_fixture(tmp_path: Path) -> tuple[Path, dict[str, str], Path, Path]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init", "--quiet")
    prereq_log = tmp_path / "prereq.log"
    uv_log = tmp_path / "uv.log"
    _write_executable(
        repo / "scripts" / "dev" / "check_linux_prereqs.sh",
        '#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" >> "$PREREQ_LOG"\n',
    )
    stub_bin = tmp_path / "bin"
    _write_executable(
        stub_bin / "uv",
        '#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" >> "$UV_LOG"\n',
    )
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{stub_bin}{os.pathsep}{env['PATH']}",
            "PREREQ_LOG": str(prereq_log),
            "UV_LOG": str(uv_log),
        }
    )
    return repo, env, prereq_log, uv_log


def test_environment_setup_dry_run_never_syncs(tmp_path: Path) -> None:
    repo, env, _, uv_log = _setup_script_fixture(tmp_path)

    result = subprocess.run(
        ["bash", str(REPO_ROOT / ".codex" / "environments" / "setup.sh"), "--step", "sync", "--dry-run"],
        cwd=repo,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    uv_calls = uv_log.read_text(encoding="utf-8").splitlines() if uv_log.exists() else []
    assert "sync --no-install-workspace" not in uv_calls
    assert "bootstrap_state: dry-run" in result.stdout


def test_environment_build_step_requires_full_native_prerequisites(tmp_path: Path) -> None:
    repo, env, prereq_log, _ = _setup_script_fixture(tmp_path)

    result = subprocess.run(
        ["bash", str(REPO_ROOT / ".codex" / "environments" / "setup.sh"), "--step", "build", "--dry-run"],
        cwd=repo,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert prereq_log.read_text(encoding="utf-8").splitlines() == ["--check"]


def test_environment_setup_runs_non_executable_prerequisite_checker_via_bash(tmp_path: Path) -> None:
    repo, env, prereq_log, _ = _setup_script_fixture(tmp_path)
    (repo / "scripts" / "dev" / "check_linux_prereqs.sh").chmod(0o644)

    result = subprocess.run(
        ["bash", str(REPO_ROOT / ".codex" / "environments" / "setup.sh"), "--step", "build", "--dry-run"],
        cwd=repo,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    prereq_calls = prereq_log.read_text(encoding="utf-8").splitlines() if prereq_log.exists() else []
    assert prereq_calls == ["--check"]


def test_environment_setup_fails_loudly_when_prerequisite_checker_is_missing(tmp_path: Path) -> None:
    repo, env, _, _ = _setup_script_fixture(tmp_path)
    (repo / "scripts" / "dev" / "check_linux_prereqs.sh").unlink()

    result = subprocess.run(
        ["bash", str(REPO_ROOT / ".codex" / "environments" / "setup.sh"), "--step", "build", "--dry-run"],
        cwd=repo,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Required prerequisite checker is missing" in result.stderr


def _ipopt_prereq_env(tmp_path: Path) -> dict[str, str]:
    stub_bin = tmp_path / "bin"
    _write_executable(stub_bin / "pkg-config", "#!/usr/bin/env bash\nexit 1\n")
    env = os.environ.copy()
    env["PATH"] = f"{stub_bin}{os.pathsep}{env['PATH']}"
    env.pop("EPCSAFT_IPOPT_ROOT", None)
    env.pop("EPCSAFT_PEP517_IPOPT_ROOT", None)
    return env


def _write_shared_ipopt_root(root: Path) -> None:
    (root / "include" / "coin").mkdir(parents=True)
    (root / "include" / "coin" / "IpIpoptApplication.hpp").write_text("// test header\n", encoding="utf-8")
    (root / "lib").mkdir()
    (root / "lib" / "libipopt.so.3").write_text("test shared library\n", encoding="utf-8")


def test_linux_prerequisites_accept_pep517_ipopt_root(tmp_path: Path) -> None:
    ipopt_root = tmp_path / "ipopt"
    _write_shared_ipopt_root(ipopt_root)
    env = _ipopt_prereq_env(tmp_path)
    env["EPCSAFT_PEP517_IPOPT_ROOT"] = str(ipopt_root)

    result = subprocess.run(
        ["bash", str(REPO_ROOT / "scripts" / "dev" / "check_linux_prereqs.sh"), "--check"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"ipopt_development_files: EPCSAFT_PEP517_IPOPT_ROOT={ipopt_root}" in result.stdout


def test_linux_prerequisites_reject_conflicting_explicit_ipopt_roots(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime-ipopt"
    pep517_root = tmp_path / "pep517-ipopt"
    _write_shared_ipopt_root(runtime_root)
    _write_shared_ipopt_root(pep517_root)
    env = _ipopt_prereq_env(tmp_path)
    env["EPCSAFT_IPOPT_ROOT"] = str(runtime_root)
    env["EPCSAFT_PEP517_IPOPT_ROOT"] = str(pep517_root)

    result = subprocess.run(
        ["bash", str(REPO_ROOT / "scripts" / "dev" / "check_linux_prereqs.sh"), "--check"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "EPCSAFT_IPOPT_ROOT and EPCSAFT_PEP517_IPOPT_ROOT disagree" in result.stderr


@pytest.mark.parametrize(
    ("script", "option"),
    [
        ("scripts/dev/create_dev_worktree.sh", "--name"),
        ("scripts/dev/create_dev_worktree.sh", "--branch"),
        ("scripts/dev/create_dev_worktree.sh", "--base"),
        ("scripts/dev/cmake_preset.sh", "--action"),
        ("scripts/dev/cmake_preset.sh", "--preset"),
        ("scripts/dev/cmake_preset.sh", "--target"),
        ("scripts/dev/cmake_preset.sh", "--parallel"),
    ],
)
def test_shell_entrypoints_reject_missing_option_values_loudly(script: str, option: str) -> None:
    result = subprocess.run(
        ["bash", str(REPO_ROOT / script), option],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert f"Missing value for {option}" in result.stderr
    assert "Usage:" in result.stderr


@pytest.mark.parametrize("argument", ["--target", "--parallel"])
def test_cmake_configure_rejects_build_only_arguments(argument: str) -> None:
    result = subprocess.run(
        [
            "bash",
            str(REPO_ROOT / "scripts" / "dev" / "cmake_preset.sh"),
            "--action",
            "configure",
            argument,
            "2" if argument == "--parallel" else "_core",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert f"{argument} is only valid with --action build" in result.stderr


def test_create_dev_worktree_rejects_path_traversal(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init", "--quiet")
    _run_git(repo, "config", "user.name", "Workflow Test")
    _run_git(repo, "config", "user.email", "workflow-test@example.invalid")
    (repo / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
    (repo / "README.md").write_text("test repository\n", encoding="utf-8")
    _run_git(repo, "add", ".gitignore", "README.md")
    _run_git(repo, "commit", "--quiet", "-m", "test baseline")

    result = subprocess.run(
        [
            "bash",
            str(REPO_ROOT / "scripts" / "dev" / "create_dev_worktree.sh"),
            "--name",
            "../escape",
            "--branch",
            "codex/worktree-test",
        ],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "simple directory name" in result.stderr
    assert not (tmp_path / "escape").exists()


def test_transferred_artifact_cleanup_preserves_linux_virtualenv(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init", "--quiet")
    (repo / ".gitignore").write_text(".venv/\n", encoding="utf-8")

    pyvenv_cfg = repo / ".venv" / "pyvenv.cfg"
    linux_header = repo / ".venv" / "include" / "python3.13" / "Python.h"
    linux_cache = repo / ".venv" / "lib" / "python3.13" / "site-packages" / "demo" / "__pycache__" / "demo.pyc"
    windows_script = repo / ".venv" / "Scripts" / "python.exe"
    windows_library = repo / ".venv" / "Lib" / "site-packages" / "demo.pyd"
    for path in (pyvenv_cfg, linux_header, linux_cache, windows_script, windows_library):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")

    result = subprocess.run(
        ["bash", str(REPO_ROOT / "scripts" / "dev" / "clean_transferred_artifacts.sh"), "--apply"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert pyvenv_cfg.is_file()
    assert linux_header.is_file()
    assert linux_cache.is_file()
    assert not windows_script.exists()
    assert not windows_library.exists()


def test_transferred_artifact_cleanup_removes_windows_build_state_only(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init", "--quiet")
    (repo / ".gitignore").write_text("build/\n", encoding="utf-8")

    windows_build = repo / "build" / "dev"
    windows_cache = windows_build / "CMakeCache.txt"
    windows_dll = windows_build / "solver.dll"
    stray_windows_binary = repo / "build" / "transferred" / "extension.pyd"
    linux_build = repo / "build" / "linux-valid"
    linux_cache = linux_build / "CMakeCache.txt"
    linux_artifact = linux_build / "libepcsaft.so"
    for path, content in (
        (windows_cache, "CMAKE_GENERATOR:INTERNAL=Visual Studio 17 2022\n"),
        (windows_dll, "windows binary\n"),
        (stray_windows_binary, "windows extension\n"),
        (linux_cache, "CMAKE_GENERATOR:INTERNAL=Ninja\nCMAKE_HOST_SYSTEM_NAME:INTERNAL=Linux\n"),
        (linux_artifact, "linux shared object\n"),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    result = subprocess.run(
        ["bash", str(REPO_ROOT / "scripts" / "dev" / "clean_transferred_artifacts.sh"), "--apply"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert not windows_build.exists()
    assert not stray_windows_binary.exists()
    assert linux_cache.is_file()
    assert linux_artifact.is_file()


def test_bootstrap_scripts_use_normal_build_and_fast_suite() -> None:
    content = _read("scripts/dev/bootstrap_uv.sh")
    linux_prereqs = _read("scripts/dev/check_linux_prereqs.sh")
    transfer_cleanup = _read("scripts/dev/clean_transferred_artifacts.sh")

    assert "scripts/dev/check_linux_prereqs.sh --check" in content
    assert "python pin 3.13" in content or '"python", "pin", "3.13"' in content
    assert "sync --no-install-workspace" in content or '"sync", "--no-install-workspace"' in content
    assert "scripts/dev/build_epcsaft.py --clean" not in content
    assert "scripts\\dev\\build_epcsaft.py --clean" not in content
    assert (
        "scripts\\dev\\validate_project.py quick" in content
        or "scripts/dev/validate_project.py quick" in content
        or '"scripts\\dev\\validate_project.py", "quick"' in content
    )
    assert "run_pytest.py tests/test_runtime.py -q" not in content
    assert "run_pytest.py tests\\test_runtime.py -q" not in content
    assert "sudo apt-get install -y" in linux_prereqs
    assert "uv python install 3.13" in linux_prereqs
    assert "build-essential" in linux_prereqs
    assert "ninja-build" in linux_prereqs
    assert "pkg-config" in linux_prereqs
    assert "coinor-libipopt-dev" in linux_prereqs
    assert "pkg-config --exists ipopt" in linux_prereqs
    assert "sys.version_info >= (3, 9)" in linux_prereqs
    assert "2>/dev/null || true" not in linux_prereqs
    assert "git check-ignore" in transfer_cleanup
    assert "would-remove:" in transfer_cleanup
    assert "*.pyd" in transfer_cleanup
    assert "*.dll" in transfer_cleanup


def test_python_bootstrap_entrypoint_orchestrates_current_setup_sequence() -> None:
    bootstrap = _read("scripts/dev/bootstrap.py")
    development_workflows = _read("docs/pages/development_workflows.rst")
    new_agent_start = _read("docs/agents/new-agent-start-here.md")

    for token in (
        "uv sync --no-install-workspace",
        "uv run --no-sync python scripts/dev/build_epcsaft.py",
        "uv run --no-sync python scripts/dev/doctor.py",
        "uv run --no-sync python scripts/dev/validate_project.py quick",
    ):
        assert token in bootstrap.replace('", "', " ")
        assert token in development_workflows
        assert token in new_agent_start
    assert "UV_RUN_PYTHON" in bootstrap
    assert "uv run --no-sync python scripts/dev/build_system_ceres.py --parallel 2" in bootstrap.replace('", "', " ")
    assert "--dry-run" in bootstrap
    assert "BASE_DOCTOR_COMMAND" in bootstrap
    assert "PROVIDER_NATIVE_DOCTOR_COMMAND" in bootstrap
    assert "EQUILIBRIUM_NATIVE_DOCTOR_COMMAND" in bootstrap
    assert "REGRESSION_NATIVE_DOCTOR_COMMAND" in bootstrap
    assert "FULL_NATIVE_DOCTOR_COMMAND" in bootstrap
    assert "--require-provider-native" in bootstrap
    assert "--require-equilibrium-native" in bootstrap
    assert "--require-regression-native" in bootstrap
    assert 'if step == "smoke":' in bootstrap
    assert 'if step == "provider-native":' in bootstrap
    assert 'if step == "equilibrium-native":' in bootstrap
    assert 'if step == "regression-native":' in bootstrap
    assert 'if step == "full-native":' in bootstrap
    assert "bootstrap_state: current" in bootstrap
    assert "next_command:" in bootstrap
    assert "ipopt_root_source" in bootstrap
    assert "ipopt_change_command" in bootstrap
    setup_body = bootstrap.split('if step == "setup":', 1)[1].split("raise AssertionError", 1)[0]
    assert '"sync"' not in setup_body
    assert env_setup_sync_count() == 1


def env_setup_sync_count() -> int:
    return sum(
        line.strip() == "uv sync --no-install-workspace" for line in _read(".codex/environments/setup.sh").splitlines()
    )


def test_cmake_wrapper_rejects_unowned_presets_before_touching_build_state() -> None:
    result = subprocess.run(
        [
            "bash",
            str(REPO_ROOT / "scripts" / "dev" / "cmake_preset.sh"),
            "--preset",
            "release",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "supports only the dev-native preset" in result.stderr


def test_clean_scripts_announce_repair_only_scope() -> None:
    content = _read("scripts/dev/clean_build.sh")

    assert "REPAIR-ONLY" in content
    assert "build/cache/native artifacts" in content


def _copy_clean_build_script(repo: Path) -> Path:
    script = repo / "scripts" / "dev" / "clean_build.sh"
    _write_executable(script, _read("scripts/dev/clean_build.sh"))
    return script


def test_clean_build_removes_stale_native_modules_from_all_packages(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script = _copy_clean_build_script(repo)
    artifacts = (
        repo / "packages" / "epcsaft" / "src" / "epcsaft" / "_core.cpython-test.so",
        repo / "packages" / "epcsaft-equilibrium" / "src" / "epcsaft_equilibrium" / "_native_core.cpython-test.so",
        repo / "packages" / "epcsaft-regression" / "src" / "epcsaft_regression" / "_native_core.cpython-test.so",
    )
    for artifact in artifacts:
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("stale native module\n", encoding="utf-8")

    result = subprocess.run(
        ["bash", str(script)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert all(not artifact.exists() for artifact in artifacts)


def test_clean_build_propagates_removal_failure(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script = _copy_clean_build_script(repo)
    provider_dir = repo / "packages" / "epcsaft" / "src" / "epcsaft"
    provider_dir.mkdir(parents=True)
    stub_bin = tmp_path / "bin"
    _write_executable(stub_bin / "rm", "#!/usr/bin/env bash\nexit 42\n")
    env = os.environ.copy()
    env["PATH"] = f"{stub_bin}{os.pathsep}{env['PATH']}"

    result = subprocess.run(
        ["bash", str(script)],
        cwd=repo,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 42


def test_docs_make_confidence_suite_the_default_runtime_check() -> None:
    readme = _read("README.md")
    getting_started = _read("docs/pages/getting_started.rst")
    overview = _read("docs/pages/README.rst")
    release_installation = _read("docs/pages/release_installation.rst")
    release_note = _read("docs/releases/v0.2.0.md")
    docs_index = _read("docs/pages/index.rst")
    development_workflows = _read("docs/pages/development_workflows.rst")
    cmake_protocol = _read("CMAKE.md")

    assert "README intentionally stays focused on package users" in readme
    assert "uv run python scripts\\validate_project.py quick" not in readme
    assert "uv run python run_pytest.py --confidence -q" not in readme
    assert "The `v0.2.0` GitHub release provides a Windows CPython 3.13 wheel" in readme
    assert "If PyPI returns 404 for `epcsaft`, use the GitHub release wheel above." in readme
    assert "python -m pip install epcsaft" in readme
    assert "python -m pip install -e packages/epcsaft" in readme
    assert "README intentionally stays focused on package users" in readme
    assert "Editable source install" in release_installation
    assert "python -m pip install -e packages/epcsaft" in release_installation
    assert "Source and editable installs build a native C++ extension" in getting_started
    assert "default source-checkout validation sequence" not in getting_started
    assert "``run_pytest.py -q`` is the default fast contract suite" not in getting_started
    assert "Current package version: ``0.2.0``" in overview
    assert "If PyPI returns 404 for ``epcsaft``, use the GitHub release wheel above." in overview
    assert "The ``v0.2.0`` tag supports source installs" in overview
    assert "python -m pip install -e packages/epcsaft" in overview
    assert "For the current release, install the Windows CPython 3.13 wheel from GitHub" in getting_started
    assert "After the package is published on PyPI" in getting_started
    assert "Current package version: ``0.2.0``" in release_installation
    assert "The ``v0.2.0`` GitHub release provides a Windows CPython 3.13 wheel" in release_installation
    assert "Windows-first native-backed Python package release" in release_note
    assert "neutral bubble/dew routes, neutral TP flash, and neutral nonassociating LLE" in release_note
    assert "Electrolyte LLE, reactive speciation" in release_note
    assert "Release assets are built for the Windows CPython 3.13" in release_note
    assert "PyPI publishing remains a manual Trusted Publishing action" in release_note
    assert "production-exposed" in overview
    assert "neutral bubble/dew routes, neutral TP flash" in overview
    assert "neutral nonassociating LLE" in overview
    assert "source-backed Khudaida explicit-ion electrolyte" in overview
    assert "uv run python run_pytest.py --confidence -q" not in overview
    assert "run_pytest.py tests/test_runtime.py -q" not in overview
    assert "release_installation" in docs_index
    assert "development_workflows" in docs_index
    assert "native_debugging" in docs_index
    assert "publishing" in docs_index
    assert "native/equation debugging guide" not in getting_started
    assert "Start every fresh source checkout with this sequence" in development_workflows
    assert "uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10" in development_workflows
    assert "Root ``CMAKE.md`` is the source of truth for direct CMake preset operations" in development_workflows
    assert "Direct CMake preset operations must use ``scripts/dev/cmake_preset.sh``" in development_workflows
    assert "Do not call raw ``cmake --preset`` or ``cmake --build``" in development_workflows
    for token in (
        "Direct CMake preset work must use",
        "scripts/dev/cmake_preset.sh",
        ".venv/bin/python -m cmake",
        ".venv/bin/ninja",
        "Do not run raw `cmake --preset`",
        "CMAKE_MAKE_PROGRAM",
    ):
        assert token in cmake_protocol
    assert "Jet" + "Brains" not in cmake_protocol
    assert "Serv" + "ices" not in cmake_protocol
    assert "uv run python run_pytest.py --runtime -q" in development_workflows
    assert "scripts/benchmarks/" + "benchmark_neutral_equilibrium.py" not in development_workflows
    assert "scripts/benchmarks/" + "benchmark_literature_suite.py" not in development_workflows
    assert "The previous local benchmark scripts were removed as obsolete" in development_workflows
    assert "uv run python run_pytest.py --list-slices" in development_workflows
    assert "EPCSAFT_PYTEST_TEMP_ROOT" in development_workflows
    assert "reuse them inside hot loops" in development_workflows
    assert "Do not route performance claims through pytest" in development_workflows
    assert "uv run python scripts/dev/build_dist.py" in development_workflows
    assert "Do not use ``--clean`` for routine validation" in development_workflows


def test_linux_documentation_uses_real_latex_and_optional_ipopt_workflows() -> None:
    development_workflows = _read("docs/pages/development_workflows.rst")
    native_boundary = _read("docs/contracts/native_extension_boundary.md")
    release_installation = _read("docs/pages/release_installation.rst")
    new_agent_start = _read("docs/agents/new-agent-start-here.md")
    dependency_protocol = _read("docs/protocols/build_package_dependency_protocol.rst")
    root_gitignore = _read(".gitignore")
    root_gitattributes = _read(".gitattributes")
    root_pyproject = _read("pyproject.toml")

    for stale in (
        "scripts/docs/setup_latex_mirror.sh",
        "scripts/docs/sync_latex_mirror.sh",
        "docs/latex/out",
    ):
        assert stale not in development_workflows
    for token in (
        "cd docs/latex",
        "latexmk -pdf equations.tex",
        "latexmk -pdf explicit_assocation.tex",
        "docs/latex/builds",
    ):
        assert token in development_workflows

    for root_policy in (root_gitignore, root_gitattributes, root_pyproject):
        assert "docs/latex/out" not in root_policy

    for document in (native_boundary, release_installation, new_agent_start, dependency_protocol):
        assert "$HOME/deps/ipopt" not in document
        assert "EPCSAFT_IPOPT_ROOT=/path/to/ipopt" in document

    extension_proof_lines = [
        line
        for document in (native_boundary, release_installation, new_agent_start, dependency_protocol)
        for line in document.splitlines()
        if "build_extension_dists.py" in line
    ]
    assert extension_proof_lines
    assert all("--ipopt-root" not in line for line in extension_proof_lines)


def test_linux_extension_docs_and_execution_records_use_current_package_ownership() -> None:
    execution_records = sorted((REPO_ROOT / "docs" / "superpowers" / "specs").glob("*.md")) + sorted(
        (REPO_ROOT / "docs" / "superpowers" / "plans").glob("*.md")
    )
    stale_preset_references = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in execution_records
        if "scripts/dev/cmake_preset.ps1" in path.read_text(encoding="utf-8")
    ]
    assert stale_preset_references == []

    equilibrium_readme = _read("packages/epcsaft-equilibrium/README.md")
    release_installation = _read("docs/pages/release_installation.rst")
    docs_overview = _read("docs/pages/README.rst")
    downstream_installs = _read("docs/pages/downstream_local_installs.rst")
    ipopt_section = release_installation.split("Native Ipopt support", 1)[1].split("Verify the install", 1)[0]

    assert "${EPCSAFT_IPOPT_ROOT:-/usr}" not in equilibrium_readme
    assert "build_extension_dists.py --mode monorepo --package epcsaft-equilibrium" in equilibrium_readme
    assert "build_extension_dists.py --mode installed-provider --package epcsaft-equilibrium" in equilibrium_readme
    assert "Provider installs do not consume Ipopt" in " ".join(release_installation.split())
    assert 'python -m pip install "epcsaft @ git+' not in ipopt_section
    assert "provider wheel and its native SDK" in docs_overview
    assert "not against a provider-only ``epcsaft`` wheel" not in docs_overview
    assert "epcsaft.__git_commit__" not in downstream_installs
    assert 'epcsaft.runtime_build_info()["source_git_commit"]' in downstream_installs


def test_open_issue_execution_oracles_use_linux_commands() -> None:
    windows_markers = (
        "```powershell",
        "pwsh.exe",
        "scripts\\",
        "analyses\\",
        "$env:",
        "Remove-Item",
        ".ps1",
        ".venv\\Scripts",
        '"$HOME\\/.codex',
    )
    execution_documents: set[Path] = set()
    open_issues: list[Path] = []
    for path in sorted((REPO_ROOT / "docs" / "superpowers" / "issues").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if "\nstate: open\n" not in text:
            continue
        open_issues.append(path)
        for line in text.splitlines():
            if line.startswith(("source_spec:", "source_plan:")):
                source_path = line.split(":", 1)[1].strip()
                if source_path and source_path != "null":
                    execution_documents.add(REPO_ROOT / source_path)
    execution_documents.update(open_issues)

    offenders: dict[str, list[str]] = {}
    for path in sorted(execution_documents):
        text = path.read_text(encoding="utf-8")
        hits = [marker for marker in windows_markers if marker.lower() in text.lower()]
        if hits:
            offenders[path.relative_to(REPO_ROOT).as_posix()] = hits

    assert offenders == {}


def test_linux_agent_and_shared_object_guidance_fail_loudly_and_match_linux_semantics() -> None:
    agents_md = _read("AGENTS.md")
    development_workflows = _read("docs/pages/development_workflows.rst")

    assert "Run the repo cleanup hook before reporting completion:" in agents_md
    assert "before reporting completion when it is available" not in agents_md
    assert "inspect the target directory ownership and permissions" in development_workflows
    assert "a process importing the previous shared object does not lock the output path" in development_workflows
    assert "If Linux reports that ``_core*.so`` is locked or busy" not in development_workflows


def test_equilibrium_capability_docs_separate_exports_from_validated_production_evidence() -> None:
    capabilities_docs = _read("docs/pages/downstream_local_installs.rst")

    assert 'assert equilibrium_caps["production_families"] == [' not in capabilities_docs
    assert "exported" in capabilities_docs
    assert "activation surface" in capabilities_docs
    assert "does not prove" in capabilities_docs
    assert "validated production behavior" in capabilities_docs
    assert 'assert "reactive_speciation" in exported_routes' in capabilities_docs
    assert "scripts/validation/check_standalone_ce_gate.py" in capabilities_docs
    assert "production evidence is withheld" in capabilities_docs
    assert "complete standalone CE gate fails" in capabilities_docs
    assert "without being advertised as callable routes" not in capabilities_docs


def test_explicit_association_toybox_keeps_exact_repo_neutral_source_provenance() -> None:
    references = _read("analyses/package_validation/explicit_association_toybox/references/README.md")

    assert ("MEA-Thermodynamics/archive/legacy_scripts/pcsaft_models_polley/pcsaft_electrolyte.py") in references
    assert "C:\\Users\\Tanner" not in references


def test_build_package_dependency_protocol_is_linked_and_guarded() -> None:
    protocol = _read("docs/protocols/build_package_dependency_protocol.rst")
    docs_index = _read("docs/pages/index.rst")
    full_plan = _read("docs/superpowers/PROJECT_CONTEXT.md")
    development_workflows = _read("docs/pages/development_workflows.rst")
    native_debugging = _read("docs/pages/native_debugging.rst")
    workflow = _read(".github/workflows/native-build-profiles.yml")
    package_lanes = _read(".github/workflows/package-build-lanes.yml")

    assert "../protocols/build_package_dependency_protocol" in docs_index
    assert "docs/protocols/build_package_dependency_protocol.rst" in full_plan
    assert ":doc:`../protocols/build_package_dependency_protocol`" in development_workflows
    assert ":doc:`../protocols/build_package_dependency_protocol`" in native_debugging
    assert "Root ``CMAKE.md`` is the direct CMake execution protocol." in protocol

    for token in (
        "Build/Package Dependency Protocol",
        "Ceres, CppAD, and Ipopt should therefore be enabled by default",
        "CppAD is required",
        "Ipopt is required for production equilibrium validation",
        "transition capabilities",
        "current monorepo",
        "reproducible friction",
        "Do not reframe Ceres, CppAD, or Ipopt as greenfield optional dependencies",
        "package-boundary exceptions",
        "Conda or mamba must not be the normal Ipopt CI provisioning path",
        "local proof first",
        "manual-only",
        "Option B is the accepted production Ipopt lane direction",
        "no-Ipopt smoke lane",
        "focused CppAD derivative lane",
        "2026-05-29 - Early package PR gates",
        "Status: Implemented as policy",
    ):
        assert token in protocol

    assert "--enable-cppad" not in workflow
    assert "native no-Ipopt smoke" in workflow
    assert "native CppAD derivative contract" in workflow
    assert "workflow_dispatch || github.event_name == 'schedule'" not in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "schedule:" not in workflow
    assert "--profile full --disable-ipopt" in workflow
    for token in (
        "provider package build",
        "regression package build",
        "equilibrium package build",
        "installed-provider extension builds",
        "scripts/dev/build_dist.py --parallel 1",
        "scripts/dev/build_system_ceres.py --parallel 2",
        "scripts/dev/build_extension_dists.py --mode monorepo --package epcsaft-regression --parallel 1",
        "scripts/dev/build_extension_dists.py --mode monorepo --package epcsaft-equilibrium --parallel 1 --ipopt-root /usr",
        "scripts/dev/build_extension_dists.py --mode installed-provider --parallel 1 --ipopt-root /usr",
        "scripts/dev/check_release_installs.py --dist-dir dist --combination all",
        "coinor-libipopt-dev",
        "test -f /usr/include/coin/IpIpoptApplication.hpp",
    ):
        assert token in package_lanes
    assert "pull_request:" not in package_lanes
    assert "push:" not in package_lanes
    assert "schedule:" not in package_lanes


def test_repo_local_agent_guidance_uses_current_dev_workflow_and_roster() -> None:
    agents_md = _read("AGENTS.md")
    new_agent_start = _read("docs/agents/new-agent-start-here.md")
    development_workflows = _read("docs/pages/development_workflows.rst")
    cmake_md = _read("CMAKE.md")
    env_toml = _read(".codex/environments/environment.toml")
    env_data = _toml(".codex/environments/environment.toml")
    env_setup = _read(".codex/environments/setup.sh")
    env_readme = _read(".codex/environments/README.md")
    happy_path = _read("docs/agents/agent-happy-path.md")
    build_owner = _read(".codex/agents/build_packaging_owner.toml")
    command_runner = _read(".codex/agents/command_runner.toml")

    for token in (
        "docs/superpowers/PROJECT_CONTEXT.md",
        "docs/agents/new-agent-start-here.md",
        "docs/agents/agent-happy-path.md",
        "docs/pages/development_workflows.rst",
        "docs/protocols/build_package_dependency_protocol.rst",
        "docs/agents/issue-tracker.md",
        "docs/pages/project_structure.rst",
        "packages/epcsaft-equilibrium",
    ):
        assert token in agents_md
    assert "Intel" + "liJ" not in agents_md
    assert "Jet" + "Brains" not in agents_md

    for stale in (
        "Machine-Local",
        "Do Not Commit",
        "C:" + "\\Users\\Tanner",
        "Best new-agent workflow",
        "Git Sandbox Rules",
        "Sandbox Notes",
        "Preferred native build",
        "uv run python scripts/build_epcsaft.py",
        "uv run python scripts/doctor.py",
        "uv run python scripts/validate_project.py quick",
        "uv run python scripts/validate_project.py confidence",
        "uv run python scripts/validate_project.py docs",
        "uv run python scripts/build_dist.py",
        "Prefer Spark owner agents",
    ):
        assert stale not in agents_md

    for token in (
        "uv run --no-sync python scripts/dev/bootstrap.py",
        "uv run --no-sync python scripts/dev/doctor.py --require-provider-sdk --require-extension-native",
        "uv run python scripts/dev/check_release_installs.py --dist-dir dist",
        "docs/superpowers/PROJECT_CONTEXT.md",
        "EPCSAFT_PEP517_CERES_DIR",
        "audited dependency closure",
        "The repo-owned Codex app setup contract lives in `.codex/environments/`",
        "Shared agent routing lives in tracked `AGENTS.md`",
        "docs/agents/agent-happy-path.md",
    ):
        assert token in new_agent_start
    assert "Intel" + "liJ" not in new_agent_start
    assert "Jet" + "Brains" not in new_agent_start

    assert "docs/roadmaps" not in new_agent_start

    for token in (
        "uv run python scripts/dev/build_epcsaft.py",
        "uv run python scripts/dev/doctor.py",
        "uv run python scripts/dev/validate_project.py quick",
        "uv run python scripts/dev/validate_project.py confidence",
        "uv run python scripts/dev/validate_project.py docs",
        "uv run python scripts/dev/build_dist.py",
    ):
        assert token in new_agent_start or token in development_workflows

    assert "Direct CMake preset work must use the repo wrapper" in cmake_md
    assert "scripts/dev/cmake_preset.sh" in cmake_md

    expected_env_actions = [
        "Sync Environment",
        "Provider Smoke",
        "Provider Native",
        "Equilibrium Native",
        "Regression Native",
        "Full Native",
        "Doctor",
        "Doctor Full Native",
        "Build Native Extension",
        "Validate Quick",
        "Validate Confidence",
        "Build Docs",
        "Build Distribution",
    ]
    env_actions = env_data["actions"]
    assert [action["name"] for action in env_actions] == expected_env_actions
    for action_name in expected_env_actions:
        assert f"- `{action_name}`" in env_readme
    assert env_actions[0]["command"].endswith(".codex/environments/setup.sh --step sync")
    assert env_actions[1]["command"].endswith(".codex/environments/setup.sh --step smoke")
    assert env_actions[2]["command"].endswith(".codex/environments/setup.sh --step provider-native")
    assert env_actions[3]["command"].endswith(".codex/environments/setup.sh --step equilibrium-native")
    assert env_actions[4]["command"].endswith(".codex/environments/setup.sh --step regression-native")
    assert env_actions[5]["command"].endswith(".codex/environments/setup.sh --step full-native")
    assert env_actions[6]["command"].endswith(".codex/environments/setup.sh --step doctor")
    assert env_actions[7]["command"].endswith(".codex/environments/setup.sh --step doctorfull")
    assert env_actions[8]["command"].endswith(".codex/environments/setup.sh --step build")
    assert env_actions[9]["command"].endswith(".codex/environments/setup.sh --step validate-quick")
    assert env_actions[10]["command"].endswith(".codex/environments/setup.sh --step validate-confidence")
    assert env_actions[11]["command"].endswith(".codex/environments/setup.sh --step validate-docs")
    assert env_actions[12]["command"].endswith(".codex/environments/setup.sh --step build-dist")

    assert 'name = "Build Native Extension (Bounded)"' not in env_toml
    assert 'name = "Provider Smoke"' in env_toml
    assert 'name = "Provider Native"' in env_toml
    assert 'name = "Equilibrium Native"' in env_toml
    assert 'name = "Regression Native"' in env_toml
    assert 'name = "Full Native"' in env_toml
    assert 'name = "Doctor Full Native"' in env_toml
    assert "Intel" + "liJ" not in env_toml
    assert "Jet" + "Brains" not in env_toml
    assert "bash .codex/environments/setup.sh --step smoke" in env_toml
    assert "bash .codex/environments/setup.sh --step provider-native" in env_toml
    assert "bash .codex/environments/setup.sh --step equilibrium-native" in env_toml
    assert "bash .codex/environments/setup.sh --step regression-native" in env_toml
    assert "bash .codex/environments/setup.sh --step full-native" in env_toml
    assert "bash .codex/environments/setup.sh --step doctorfull" in env_toml
    assert "bash .codex/environments/setup.sh --step build" in env_toml
    assert 'bash scripts/dev/check_linux_prereqs.sh "$prereq_mode"' in env_setup
    assert "setup|build|equilibrium-native|full-native)" in env_setup
    assert 'prereq_mode="--check"' in env_setup
    assert "uv sync --no-install-workspace" in env_setup
    assert 'bootstrap_args=(--step "$step")' in env_setup
    assert 'uv run --no-sync python scripts/dev/bootstrap.py "${bootstrap_args[@]}"' in env_setup
    assert "scripts/dev/check_linux_prereqs.sh --check" in happy_path
    assert "scripts/dev/clean_transferred_artifacts.sh --dry-run" in happy_path
    assert "python3 run_pytest.py --list-slices" in happy_path
    assert "validate_project.py confidence" in happy_path
    assert "Invoke-ReusableCeresBuild" not in env_setup
    assert "scripts/dev/build_system_ceres.py" in _read("scripts/dev/bootstrap.py")
    assert "--use-system-ceres" in _read("scripts/dev/bootstrap.py")
    assert "--ceres-dir" in _read("scripts/dev/bootstrap.py")
    assert "Do not set `EPCSAFT_PEP517_CERES_DIR`" in env_readme
    assert "build_epcsaft.py --use-system-ceres" in env_readme
    assert ".codex/environments/setup.sh builds or reuses scripts/dev/build_system_ceres.py output" in build_owner
    assert "scripts/dev/build_dist.py builds the provider-only packages/epcsaft distribution" in command_runner
    assert "plus EPCSAFT_PEP517_CERES_DIR" not in build_owner
    assert (
        "prefer a persistent EPCSAFT_PEP517_BUILD_DIR and prebuilt Ceres via EPCSAFT_PEP517_CERES_DIR"
        not in command_runner
    )
    assert not (REPO_ROOT / "docs" / "agents" / ("INTEL" + "LIJ.md")).exists()
    assert not (REPO_ROOT / "scripts" / "dev" / ("configure_" + "jet" + "brains_project.py")).exists()
    assert not (REPO_ROOT / "scripts" / "dev" / ("jet" + "brains_run_manifest.py")).exists()
    assert not (REPO_ROOT / ".run").exists()


def test_repo_local_agent_roster_uses_supported_models_and_expected_scopes() -> None:
    expected_agents = {
        "build_packaging_owner.toml": ("gpt-5.4", "workspace-write"),
        "command_runner.toml": ("gpt-5.4", "workspace-write"),
        "native_equation_owner.toml": ("gpt-5.4", "read-only"),
        "native_solver_backend_owner.toml": ("gpt-5.4", "workspace-write"),
        "python_api_test_owner.toml": ("gpt-5.4", "workspace-write"),
    }

    agents_dir = REPO_ROOT / ".codex" / "agents"
    for filename, (model, sandbox_mode) in expected_agents.items():
        path = agents_dir / filename
        assert path.is_file(), filename
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        assert data["model"] == model
        assert data["sandbox_mode"] == sandbox_mode


def test_github_default_smoke_uses_downstream_path_install_not_wheel_build() -> None:
    workflow = _read(".github/workflows/wheels.yml")
    old_python = "uv python install " + "3." + "12"
    old_wheel_command = "uv build --" + "wheel"
    old_wheel_step = "Build Linux " + "wheel"

    assert "uv python install 3.13" in workflow
    assert old_python not in workflow
    assert 'repo_url="file://${GITHUB_WORKSPACE}"' in workflow
    assert "epcsaft @ ${repo_url}/packages/epcsaft" in workflow
    assert "UV_CACHE_DIR" in workflow
    assert "EPCSAFT_PEP517_BUILD_DIR" in workflow
    assert "uv sync --python 3.13" in workflow
    assert "uv run --no-sync python" in workflow
    assert old_wheel_command not in workflow
    assert old_wheel_step not in workflow


def test_github_full_packaging_remains_manual_only() -> None:
    workflow = _read(".github/workflows/wheels.yml")
    old_cibw = 'CIBW_BUILD: "cp' + '312-*"'

    assert "workflow_dispatch:" in workflow
    assert "if: ${{ github.event_name == 'workflow_dispatch' && inputs.full_wheel_matrix }}" in workflow
    assert 'CIBW_BUILD: "cp313-*"' in workflow
    assert 'CIBW_ARCHS_LINUX: "x86_64"' in workflow
    assert old_cibw not in workflow
    assert "ubuntu-latest, macos-latest, " + "win" + "dows-" + "latest" not in workflow
    assert "build Linux wheel" in workflow


def test_github_default_events_run_linux_package_boundary_smoke() -> None:
    workflow = _read(".github/workflows/wheels.yml")

    assert "fast-pr-smoke:" in workflow
    assert "linux-install-smoke:" in workflow
    assert "if: ${{ github.event_name == 'pull_request' }}" in workflow
    linux_smoke = workflow.split("\n  linux-install-smoke:", 1)[1].split("\n  build:", 1)[0]
    assert "    if:" not in linux_smoke
    assert workflow.count("runs-on: ubuntu-24.04") >= 3
    assert workflow.count("name: linux install smoke") == 1
    assert workflow.count("name: fast workflow smoke") == 1


def test_package_build_lanes_are_split_by_distribution_and_sdk_mode() -> None:
    workflow = _read(".github/workflows/package-build-lanes.yml")

    assert "name: package-build-lanes" in workflow
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "schedule:" not in workflow
    assert "provider-package:" in workflow
    assert "regression-package:" in workflow
    assert "equilibrium-package:" in workflow
    assert "installed-provider-extensions:" in workflow
    assert "run_ipopt_lanes:" in workflow
    assert "ipopt_root:" not in workflow
    assert workflow.count("coinor-libipopt-dev") == 2
    assert workflow.count("--ipopt-root /usr") == 2
    assert "uv run python scripts/dev/build_dist.py --parallel 1" in workflow
    assert "uv run python scripts/dev/build_system_ceres.py --parallel 2" in workflow
    assert "uv run python scripts/dev/check_release_installs.py --dist-dir dist --combination provider" in workflow
    assert "uv run python scripts/dev/check_release_installs.py --dist-dir dist --combination regression" in workflow
    assert "uv run python scripts/dev/check_release_installs.py --dist-dir dist --combination equilibrium" in workflow
    assert "uv run python scripts/dev/check_release_installs.py --dist-dir dist --combination all" in workflow
    assert "--disable-ipopt" not in workflow
    assert "sudo apt-get install --yes --no-install-recommends coinor-libipopt-dev" in workflow


def test_heavy_native_workflow_is_manual_only() -> None:
    workflow = _read(".github/workflows/native-build-profiles.yml")

    assert "name: native-build-profiles" in workflow
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "schedule:" not in workflow
    assert "native no-Ipopt smoke" in workflow
    assert "native CppAD derivative contract" in workflow


def test_pr_template_does_not_force_production_proof_answers_on_ordinary_prs() -> None:
    template = _read(".github/PULL_REQUEST_TEMPLATE.md")

    assert "## Required PR Answers" not in template
    assert "What downstream workflow can now run" not in template
    assert "What production native code path now exists" not in template
    assert "What derivative path is used" not in template
    assert "What real data or benchmark proves it" not in template
    assert "This PR does not broaden `capabilities()` or public claims without executable proof" in template


def test_pypi_publish_workflow_uses_trusted_publishing() -> None:
    workflow = _read(".github/workflows/publish-pypi.yml")
    publishing_docs = _read("docs/pages/publishing.rst")

    for token in (
        "name: publish-to-pypi",
        "workflow_dispatch:",
        "id-token: write",
        "environment:",
        "name: pypi",
        "pypa/gh-action-pypi-publish@release/v1",
        "actions/download-artifact@v8.0.1",
        "merge-multiple: true",
        'CIBW_BUILD: "cp313-*"',
        'CIBW_ARCHS_LINUX: "x86_64"',
        "uv build packages/epcsaft --sdist",
        "pypi-preflight:",
        "PyPI trusted publisher preflight",
        "https://pypi.org/pypi/{project}/json",
        "pending publisher",
        "PyPI first-publish preflight",
        "already has {project} {version}",
    ):
        assert token in workflow
    assert "release:" not in workflow
    assert "types: [published]" not in workflow
    assert "github.event.release" not in workflow
    assert "needs: [pypi-preflight]" in workflow
    assert "password:" not in workflow
    assert "username:" not in workflow
    assert "PYPI_API_TOKEN" not in workflow
    assert "pp*" not in workflow
    dispatch_inputs = workflow.split("  workflow_dispatch:", 1)[1].split("\n\npermissions:", 1)[0]
    assert "      tag:" in dispatch_inputs
    assert "      ref:" not in dispatch_inputs
    assert "Workflow filename: ``publish-pypi.yml``" in publishing_docs
    assert "Environment name: ``pypi``" in publishing_docs
    assert "GitHub releases and PyPI uploads are separate steps" in publishing_docs
    assert "Creating a GitHub release does not upload to PyPI" in publishing_docs
    assert "-f tag=vX.Y.Z" in publishing_docs
    assert "-f ref=" not in publishing_docs
    assert "Ipopt runtime DLLs" not in publishing_docs


def test_version_defaults_are_derived_from_pyproject() -> None:
    cmake = _read("CMakeLists.txt")
    docs_conf = _read("docs/conf.py")

    assert 'set(SKBUILD_PROJECT_VERSION "1.5.0")' not in cmake
    assert 'release = "1.5.0"' not in docs_conf
    assert "pyproject.toml" in cmake
    assert "pyproject.toml" in docs_conf
    assert "Could not derive documentation release from pyproject.toml" in docs_conf


def test_native_warning_options_apply_to_all_native_targets() -> None:
    cmake = _read("CMakeLists.txt")

    assert 'option(EPCSAFT_WARNINGS_AS_ERRORS "Treat native warnings as errors" OFF)' in cmake
    assert 'option(EPCSAFT_ENABLE_SANITIZERS "Enable ASAN/UBSAN in debug builds" OFF)' in cmake
    assert "set(EPCSAFT_NATIVE_OBJECT_TARGETS" in cmake
    assert "epcsaft_provider_native" in cmake
    assert "epcsaft_equilibrium_native" in cmake
    assert "epcsaft_regression_native" in cmake
    assert "set(EPCSAFT_NATIVE_TARGETS" in cmake
    assert "${EPCSAFT_NATIVE_OBJECT_TARGETS}" in cmake
    assert "foreach(target_name IN LISTS EPCSAFT_NATIVE_TARGETS)" in cmake
    assert "target_compile_options(${target_name} PRIVATE -Wall -Wextra -Wpedantic)" in cmake
