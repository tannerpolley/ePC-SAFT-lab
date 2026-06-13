from __future__ import annotations

from dataclasses import dataclass

PYTHON_RUNNER = "Python"
UV_RUNNER = "uv run"
POWERSHELL_RUNNER = "PowerShell"
SHELL_RUNNER = "Shell Script"
REPO_SERVICES_FOLDER = "ePC-SAFT"
REPO_CONFIG_NAME_PREFIX = f"{REPO_SERVICES_FOLDER}: "
FOLDER_SETUP_HEALTH = REPO_SERVICES_FOLDER
FOLDER_BUILD_PACKAGE = REPO_SERVICES_FOLDER
FOLDER_VALIDATION = REPO_SERVICES_FOLDER
FOLDER_TESTS = REPO_SERVICES_FOLDER
FOLDER_DOCS_REPORTS = REPO_SERVICES_FOLDER
FOLDER_ANALYSIS_FIGURES = REPO_SERVICES_FOLDER
FOLDER_MAINTENANCE = REPO_SERVICES_FOLDER


def repo_run_config_name(name: str) -> str:
    if name.startswith(REPO_CONFIG_NAME_PREFIX):
        return name
    return f"{REPO_CONFIG_NAME_PREFIX}{name}"


@dataclass(frozen=True)
class RunConfigSpec:
    name: str
    runner: str
    folder_name: str
    command: str
    parameters: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", repo_run_config_name(self.name))


CANONICAL_RUN_CONFIGS: tuple[RunConfigSpec, ...] = (
    RunConfigSpec(
        name="Sync Workspace Packages",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command=".codex/environments/setup.ps1",
        parameters="-Step Sync",
    ),
    RunConfigSpec(
        name="Check Package Imports",
        runner=UV_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command="scripts/dev/check_package_imports.py",
    ),
    RunConfigSpec(
        name="Provider Smoke",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command=".codex/environments/setup.ps1",
        parameters="-Step Smoke",
    ),
    RunConfigSpec(
        name="Provider Native",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command=".codex/environments/setup.ps1",
        parameters="-Step ProviderNative",
    ),
    RunConfigSpec(
        name="Equilibrium Native",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command=".codex/environments/setup.ps1",
        parameters="-Step EquilibriumNative",
    ),
    RunConfigSpec(
        name="Regression Native",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command=".codex/environments/setup.ps1",
        parameters="-Step RegressionNative",
    ),
    RunConfigSpec(
        name="Full Native",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command=".codex/environments/setup.ps1",
        parameters="-Step FullNative",
    ),
    RunConfigSpec(
        name="Doctor",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command=".codex/environments/setup.ps1",
        parameters="-Step Doctor",
    ),
    RunConfigSpec(
        name="Doctor Full Native",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command=".codex/environments/setup.ps1",
        parameters="-Step DoctorFull",
    ),
    RunConfigSpec(
        name="Build Status",
        runner=UV_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command="scripts/dev/build_epcsaft.py",
        parameters="--status",
    ),
    RunConfigSpec(
        name="Build Native Extension",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command=".codex/environments/setup.ps1",
        parameters="-Step Build",
    ),
    RunConfigSpec(
        name="Build Native Incremental",
        runner=UV_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/build_epcsaft.py",
        parameters="--build-only --parallel 10",
    ),
    RunConfigSpec(
        name="Build Provider-Only Core",
        runner=UV_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/build_epcsaft.py",
        parameters="--clean --profile provider",
    ),
    RunConfigSpec(
        name="CMake Configure dev-native",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/cmake_preset.ps1",
        parameters="-Action Configure -Preset dev-native",
    ),
    RunConfigSpec(
        name="CMake Build _core dev-native",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/cmake_preset.ps1",
        parameters="-Action Build -Preset dev-native -Target _core -Parallel 10",
    ),
    RunConfigSpec(
        name="CMake Build dev-native",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/cmake_preset.ps1",
        parameters="-Action Build -Preset dev-native -Parallel 10",
    ),
    RunConfigSpec(
        name="Build Distribution",
        runner=UV_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/build_dist.py",
    ),
    RunConfigSpec(
        name="Validate Quick",
        runner=UV_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/dev/validate_project.py",
        parameters="quick",
    ),
    RunConfigSpec(
        name="Validate Confidence",
        runner=UV_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/dev/validate_project.py",
        parameters="confidence",
    ),
    RunConfigSpec(
        name="Check Text Gates",
        runner=UV_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/dev/check_text_gates.py",
    ),
    RunConfigSpec(
        name="Validate HELD Reliability Smoke",
        runner=UV_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/validation/check_held_reliability.py",
        parameters=(
            "--family neutral-lle --conditions 2 --repeats 2 --seed 1729 "
            "--require-complete --json --output-dir "
            "analyses/package_validation/held_lle_reliability/shared/results"
        ),
    ),
    RunConfigSpec(
        name="Test List Slices",
        runner=UV_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--list-slices",
    ),
    RunConfigSpec(
        name="Test Provider API",
        runner=UV_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--provider-api -q",
    ),
    RunConfigSpec(
        name="Test Equilibrium API",
        runner=UV_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--equilibrium-api -q",
    ),
    RunConfigSpec(
        name="Test Equilibrium Confidence",
        runner=UV_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--equilibrium-confidence -q",
    ),
    RunConfigSpec(
        name="Test Regression",
        runner=UV_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--regression -q",
    ),
    RunConfigSpec(
        name="Test Integration",
        runner=UV_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--integration -q",
    ),
    RunConfigSpec(
        name="Test Runtime",
        runner=UV_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--runtime -q",
    ),
    RunConfigSpec(
        name="Test Native",
        runner=UV_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--native -q",
    ),
    RunConfigSpec(
        name="Test Native Contracts",
        runner=UV_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--native-contracts -q",
    ),
    RunConfigSpec(
        name="Test Workflow Guards",
        runner=UV_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters=(
            "tests/workflows/repo/test_workflow_entrypoints.py "
            "tests/workflows/build/test_build_epcsaft.py "
            "tests/workflows/build/test_build_epcsaft_script.py "
            "tests/workflows/build/test_build_system_ceres.py -q"
        ),
    ),
    RunConfigSpec(
        name="Build Docs",
        runner=UV_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/dev/validate_project.py",
        parameters="docs",
    ),
    RunConfigSpec(
        name="Build Equations PDF",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/docs/build_equations_pdf.ps1",
    ),
    RunConfigSpec(
        name="Sync Equation Registry",
        runner=UV_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/docs/sync_equation_registry.py",
    ),
    RunConfigSpec(
        name="Sync Algorithm Registry",
        runner=UV_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/docs/sync_algorithm_registry.py",
    ),
    RunConfigSpec(
        name="Generate Equilibrium Activation",
        runner=UV_RUNNER,
        folder_name=FOLDER_ANALYSIS_FIGURES,
        command="scripts/dev/generate_equilibrium_activation.py",
    ),
    RunConfigSpec(
        name="Check IntelliJ Contract",
        runner=UV_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/configure_jetbrains_project.py",
        parameters="--check",
    ),
    RunConfigSpec(
        name="Configure IntelliJ Runs (Dry Run)",
        runner=UV_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/configure_jetbrains_project.py",
        parameters="--dry-run",
    ),
    RunConfigSpec(
        name="Configure IntelliJ Runs (Apply)",
        runner=UV_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/configure_jetbrains_project.py",
        parameters="--apply",
    ),
    RunConfigSpec(
        name="Clean Build Artifacts",
        runner=POWERSHELL_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/clean_build.ps1",
    ),
)


def canonical_run_config_names() -> frozenset[str]:
    return frozenset(spec.name for spec in CANONICAL_RUN_CONFIGS)
