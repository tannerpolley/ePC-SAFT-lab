from __future__ import annotations

from dataclasses import dataclass

PYTHON_RUNNER = "Python"
SHELL_RUNNER = "Shell Script"
FOLDER_SETUP_HEALTH = "Setup & Health"
FOLDER_BUILD_PACKAGE = "Build & Package"
FOLDER_VALIDATION = "Validation"
FOLDER_TESTS = "Tests"
FOLDER_DOCS_REPORTS = "Docs & Reports"
FOLDER_ANALYSIS_FIGURES = "Analysis & Figures"
FOLDER_MAINTENANCE = "Maintenance"


@dataclass(frozen=True)
class RunConfigSpec:
    name: str
    runner: str
    folder_name: str
    command: str
    parameters: str = ""


CANONICAL_RUN_CONFIGS: tuple[RunConfigSpec, ...] = (
    RunConfigSpec(
        name="Sync Workspace Packages",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command="uv sync --all-packages",
    ),
    RunConfigSpec(
        name="Check Package Imports",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command="scripts/dev/check_package_imports.py",
    ),
    RunConfigSpec(
        name="Doctor",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command=".codex/environments/setup.ps1",
        parameters="-Step Doctor",
    ),
    RunConfigSpec(
        name="Build Status",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_SETUP_HEALTH,
        command="scripts/dev/build_epcsaft.py",
        parameters="--status",
    ),
    RunConfigSpec(
        name="Build Native Extension",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command=".codex/environments/setup.ps1",
        parameters="-Step Build",
    ),
    RunConfigSpec(
        name="Build Native Incremental",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/build_epcsaft.py",
        parameters="--build-only --parallel 10",
    ),
    RunConfigSpec(
        name="Build Provider-Only Core",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/build_epcsaft.py",
        parameters="--clean --profile provider",
    ),
    RunConfigSpec(
        name="CMake Configure dev-native",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/cmake_preset.ps1",
        parameters="-Action Configure -Preset dev-native",
    ),
    RunConfigSpec(
        name="CMake Build _core dev-native",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/cmake_preset.ps1",
        parameters="-Action Build -Preset dev-native -Target _core -Parallel 10",
    ),
    RunConfigSpec(
        name="CMake Build dev-native",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/cmake_preset.ps1",
        parameters="-Action Build -Preset dev-native -Parallel 10",
    ),
    RunConfigSpec(
        name="Build Distribution",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_BUILD_PACKAGE,
        command="scripts/dev/build_dist.py",
    ),
    RunConfigSpec(
        name="Validate Quick",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/dev/validate_project.py",
        parameters="quick",
    ),
    RunConfigSpec(
        name="Validate Confidence",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/dev/validate_project.py",
        parameters="confidence",
    ),
    RunConfigSpec(
        name="Check Text Gates",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_VALIDATION,
        command="scripts/dev/check_text_gates.py",
    ),
    RunConfigSpec(
        name="Test List Slices",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--list-slices",
    ),
    RunConfigSpec(
        name="Test Provider API",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--provider-api -q",
    ),
    RunConfigSpec(
        name="Test Equilibrium API",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--equilibrium-api -q",
    ),
    RunConfigSpec(
        name="Test Equilibrium Confidence",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--equilibrium-confidence -q",
    ),
    RunConfigSpec(
        name="Test Regression",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--regression -q",
    ),
    RunConfigSpec(
        name="Test Integration",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--integration -q",
    ),
    RunConfigSpec(
        name="Test Runtime",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--runtime -q",
    ),
    RunConfigSpec(
        name="Test Native",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--native -q",
    ),
    RunConfigSpec(
        name="Test Native Contracts",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_TESTS,
        command="run_pytest.py",
        parameters="--native-contracts -q",
    ),
    RunConfigSpec(
        name="Test Workflow Guards",
        runner=PYTHON_RUNNER,
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
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/dev/validate_project.py",
        parameters="docs",
    ),
    RunConfigSpec(
        name="Build Equations PDF",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/docs/build_equations_pdf.ps1",
    ),
    RunConfigSpec(
        name="Sync Equation Registry",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/docs/sync_equation_registry.py",
    ),
    RunConfigSpec(
        name="Sync Algorithm Registry",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_DOCS_REPORTS,
        command="scripts/docs/sync_algorithm_registry.py",
    ),
    RunConfigSpec(
        name="Generate Equilibrium Activation",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_ANALYSIS_FIGURES,
        command="scripts/dev/generate_equilibrium_activation.py",
    ),
    RunConfigSpec(
        name="Check IntelliJ Contract",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/configure_jetbrains_project.py",
        parameters="--check",
    ),
    RunConfigSpec(
        name="Configure IntelliJ Runs (Dry Run)",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/configure_jetbrains_project.py",
        parameters="--dry-run",
    ),
    RunConfigSpec(
        name="Configure IntelliJ Runs (Apply)",
        runner=PYTHON_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/configure_jetbrains_project.py",
        parameters="--apply",
    ),
    RunConfigSpec(
        name="Clean Build Artifacts",
        runner=SHELL_RUNNER,
        folder_name=FOLDER_MAINTENANCE,
        command="scripts/dev/clean_build.ps1",
    ),
)


def canonical_run_config_names() -> frozenset[str]:
    return frozenset(spec.name for spec in CANONICAL_RUN_CONFIGS)
