import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import epcsaft.runtime.capability_evidence as capability_evidence
import run_pytest
from scripts.dev import doctor, validate_project

EQUILIBRIUM_API_TEST_FILE = "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py"
EQUILIBRIUM_BUBBLE_DERIVATIVE_TEST_FILE = "packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py"
EQUILIBRIUM_CAPABILITY_TEST_FILE = "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py"
EQUILIBRIUM_NATIVE_TEST_ROOT = "packages/epcsaft-equilibrium/tests/native"
EQUILIBRIUM_NATIVE_RESULTS_ROOT = "packages/epcsaft-equilibrium/tests/native/results"
EQUILIBRIUM_NATIVE_LLE_RESULTS_TEST = (
    "packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py"
)
EQUILIBRIUM_NATIVE_VLE_RESULTS_TEST = (
    "packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py"
)
EQUILIBRIUM_SELECTOR_CONTRACT_TEST = (
    "packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py"
)
PROVIDER_API_IMPORTS_TEST = "packages/epcsaft/tests/api/frontend/test_imports.py"
PROVIDER_API_STATE_PROPERTIES_TEST = "packages/epcsaft/tests/api/frontend/test_state_properties.py"
PROVIDER_NATIVE_CONTRIBUTIONS_TEST = (
    "packages/epcsaft/tests/native/state/test_contributions.py::"
    "test_native_residual_helmholtz_and_compressibility_contributions_match_neutral_contract"
)
REGRESSION_API_TEST_FILE = "packages/epcsaft-regression/tests/api/test_regression.py"
REGRESSION_NATIVE_PURE_TEST = "packages/epcsaft-regression/tests/native/test_pure.py"
REGRESSION_NATIVE_BINARY_TEST = "packages/epcsaft-regression/tests/native/test_binary.py"


def test_confidence_slice_extends_generic_targets_without_changing_generic():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    generic_args = run_pytest._pytest_args(["-q"], pytest_temp, generic=True)
    confidence_args = run_pytest._pytest_args(["-q"], pytest_temp, confidence=True)

    assert generic_args[: len(run_pytest.GENERIC_TEST_TARGETS)] == list(run_pytest.GENERIC_TEST_TARGETS)
    assert "packages/epcsaft/tests/native/state/test_properties.py" not in generic_args
    assert "tests/api/frontend" not in generic_args
    assert "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py" not in generic_args
    assert confidence_args[: len(run_pytest.CONFIDENCE_TEST_TARGETS)] == list(run_pytest.CONFIDENCE_TEST_TARGETS)
    assert PROVIDER_NATIVE_CONTRIBUTIONS_TEST in confidence_args
    assert confidence_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]


def test_default_pytest_route_uses_fast_contracts_not_exhaustive_suite():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    default_args = run_pytest._pytest_args(["-q"], pytest_temp)

    assert default_args[: len(run_pytest.FAST_TEST_TARGETS)] == list(run_pytest.FAST_TEST_TARGETS)
    assert "tests" not in default_args
    assert "tests/api/frontend" not in default_args
    assert "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py" not in default_args
    assert not any(target.startswith("tests/plots/") for target in default_args)
    assert "tests/workflows/validation/equilibrium_core/test_electrolyte_lle_confidence.py" not in default_args
    assert default_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]


def test_predefined_pytest_targets_reference_existing_files():
    repo_root = Path(__file__).resolve().parents[3]
    missing: set[str] = set()

    for targets in run_pytest.SLICE_TARGETS.values():
        for target in targets:
            if target in {"tests", "packages/epcsaft/tests"}:
                continue
            target_path = target.split("::", 1)[0]
            if not (repo_root / target_path).exists():
                missing.add(target_path)

    assert not sorted(missing)


def test_all_shortcut_is_the_explicit_exhaustive_pytest_route():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    all_args = run_pytest._pytest_args(["-q"], pytest_temp, all_tests=True)

    assert all_args[: len(run_pytest.ALL_TEST_TARGETS)] == list(run_pytest.ALL_TEST_TARGETS)
    assert all_args == [
        "tests",
        "packages/epcsaft/tests",
        "packages/epcsaft-equilibrium/tests",
        "packages/epcsaft-regression/tests",
        "-q",
        "--basetemp",
        str(pytest_temp),
    ]


def test_validate_project_modes_route_to_standard_validation_bundles():
    assert validate_project.CHECK_COMMANDS == {
        name: capability_evidence.validation_lane_commands(name)
        for name in capability_evidence.VALIDATION_LANES
    }
    assert validate_project.CHECK_COMMANDS["quick"] == (
        ("scripts/dev/doctor.py",),
        ("run_pytest.py", "-q"),
    )
    assert validate_project.CHECK_COMMANDS["provider"] == (
        ("scripts/dev/doctor.py",),
        ("run_pytest.py", "--provider-api", "-q"),
    )
    assert validate_project.CHECK_COMMANDS["equilibrium"] == (
        ("scripts/dev/doctor.py",),
        ("run_pytest.py", "--equilibrium-api", "-q"),
    )
    assert validate_project.CHECK_COMMANDS["regression"] == (
        ("scripts/dev/doctor.py",),
        ("run_pytest.py", "--regression", "-q"),
    )
    assert validate_project.CHECK_COMMANDS["integration"] == (
        ("scripts/dev/doctor.py",),
        ("run_pytest.py", "--integration", "-q"),
    )
    assert all(
        "build_plot_" + "manifest.py" not in command
        for mode in validate_project.CHECK_COMMANDS.values()
        for command in mode
    )
    assert "plots" not in validate_project.CHECK_COMMANDS
    assert validate_project.CHECK_COMMANDS["full"] == (
        ("scripts/dev/doctor.py",),
        ("run_pytest.py", "--all", "-q"),
    )
    assert validate_project.CHECK_COMMANDS["ceres-cppad"] == (
        ("scripts/dev/build_epcsaft.py", "--profile", "full"),
        (
            "run_pytest.py",
            REGRESSION_NATIVE_PURE_TEST,
            REGRESSION_NATIVE_BINARY_TEST,
            "-q",
        ),
    )
    assert validate_project.CHECK_COMMANDS["equilibrium-confidence"] == (
        ("scripts/dev/doctor.py",),
        ("run_pytest.py", "--equilibrium-confidence", "-q", "-s"),
    )
    assert validate_project.CHECK_COMMANDS["equilibrium-debug"] == (
        ("scripts/dev/doctor.py",),
        (
            "scripts/validation/check_phase_discovery.py",
            "--debug",
            "--include-route-refinement",
            "--require-complete",
        ),
    )
    assert all(command[0] != "run_pytest.py" for command in validate_project.CHECK_COMMANDS["equilibrium-debug"])


def test_validate_project_script_runs_when_invoked_by_path():
    repo_root = Path(__file__).resolve().parents[3]

    result = subprocess.run(
        [sys.executable, "scripts/dev/validate_project.py", "--help"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "standard validation modes" in result.stdout


def test_pytest_slices_are_adapted_from_capability_evidence_registry():
    assert run_pytest.SLICE_TARGETS == {
        name: capability_evidence.registry_targets(name)
        for name in capability_evidence.TEST_SLICES
    }
    assert run_pytest.GENERIC_TEST_TARGETS == capability_evidence.registry_targets("generic")
    assert run_pytest.CONFIDENCE_TEST_TARGETS == capability_evidence.registry_targets("confidence")
    assert run_pytest.PROVIDER_API_TEST_TARGETS == capability_evidence.registry_targets("provider-api")
    assert run_pytest.REGRESSION_TEST_TARGETS == capability_evidence.registry_targets("regression")
    assert run_pytest.INTEGRATION_TEST_TARGETS == capability_evidence.registry_targets("integration")
    assert run_pytest.NATIVE_CONTRACT_TEST_TARGETS == capability_evidence.registry_targets("native-contracts")


def test_equilibrium_debug_flag_sets_opt_in_test_environment():
    env: dict[str, str] = {}

    run_pytest._apply_equilibrium_debug_env(env, enabled=False)
    assert "EPCSAFT_EQUILIBRIUM_DEBUG" not in env

    run_pytest._apply_equilibrium_debug_env(env, enabled=True)
    assert env["EPCSAFT_EQUILIBRIUM_DEBUG"] == "1"


def test_continuous_tpd_debug_trace_is_gated_by_equilibrium_debug_env():
    source = Path(
        "packages/epcsaft-equilibrium/native/equilibrium/core/two_phase_eos_route.cpp"
    ).read_text(encoding="utf-8")

    assert "EPCSAFT_EQUILIBRIUM_DEBUG" in source
    assert "[EPCSAFT_TPD_DEBUG]" in source
    assert "continuous_coordinate_search" in source


def test_doctor_tracks_native_symbols_added_by_recent_workflows():
    required = set(doctor.REQUIRED_CORE_SYMBOLS)

    assert "_native_cppad_smoke" in required
    assert "NativeSolutionError" in required
    assert "_fit_pure_neutral_native_ceres" not in required
    assert "_fit_pure_neutral_native_least" + "_squares" not in required
    assert "_fit_generic_native_least" + "_squares" not in required
    assert "_fit_generic_native_ceres" not in required
    assert "_evaluate_generic_native_debug" not in required
    assert "_native_ipopt_smoke" not in required


def test_native_regression_source_has_no_eigen_nonlinear_optimizer_route():
    source = Path("packages/epcsaft-regression/native/regression/ceres_regression.cpp").read_text(encoding="utf-8")

    blocked_terms = (
        "unsupported/Eigen/" + "Levenberg" + "Marquardt",
        "Levenberg" + "Marquardt",
        "Numerical" + "Diff",
    )
    for term in blocked_terms:
        assert term not in source


def test_native_ceres_sources_have_no_ceres_nonexact_derivative_route():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for root in (Path("packages/epcsaft/src/epcsaft/native"), Path("packages/epcsaft-regression/native"))
        for path in sorted(root.rglob("*"))
        if path.suffix in {".cpp", ".h", ".hpp"}
    )
    source_lower = source.lower()

    blocked_terms = (
        "Numeric" + "Diff",
        "Numeric" + "DiffCostFunction",
        "Dynamic" + "Numeric" + "DiffCostFunction",
        "CERES_" + "NUMERIC" + "_DIFF",
        "numeric" + "_diff",
        "finite" + "_difference",
    )
    for term in blocked_terms:
        assert term.lower() not in source_lower


def test_doctor_recommends_ninja_migration_for_mingw_build_tree():
    command = doctor._ninja_migration_recommendation("MinGW Makefiles", "C:/tools/ninja.exe")

    assert command == "uv run python scripts\\dev\\build_epcsaft.py --clean --generator ninja"


def test_doctor_does_not_recommend_ninja_migration_when_already_ninja():
    command = doctor._ninja_migration_recommendation("Ninja", "C:/tools/ninja.exe")

    assert command is None


def test_named_shortcuts_expand_to_expected_targets_and_keep_pytest_arg_ordering():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    runtime_args = run_pytest._pytest_args(["-q"], pytest_temp, runtime=True)
    api_args = run_pytest._pytest_args(["-q"], pytest_temp, api=True)
    native_args = run_pytest._pytest_args(["-q"], pytest_temp, native=True)
    native_contract_args = run_pytest._pytest_args(["-q"], pytest_temp, native_contracts=True)
    provider_api_args = run_pytest._pytest_args(["-q"], pytest_temp, provider_api=True)
    regression_args = run_pytest._pytest_args(["-q"], pytest_temp, regression=True)
    integration_args = run_pytest._pytest_args(["-q"], pytest_temp, integration=True)
    equilibrium_confidence_args = run_pytest._pytest_args(["-q"], pytest_temp, equilibrium_confidence=True)
    equilibrium_api_args = run_pytest._pytest_args(["-q"], pytest_temp, equilibrium_api=True)

    assert runtime_args[: len(run_pytest.RUNTIME_TEST_TARGETS)] == list(run_pytest.RUNTIME_TEST_TARGETS)
    assert api_args[: len(run_pytest.API_TEST_TARGETS)] == list(run_pytest.API_TEST_TARGETS)
    assert native_args[: len(run_pytest.NATIVE_TEST_TARGETS)] == list(run_pytest.NATIVE_TEST_TARGETS)
    assert native_contract_args[: len(run_pytest.NATIVE_CONTRACT_TEST_TARGETS)] == list(
        run_pytest.NATIVE_CONTRACT_TEST_TARGETS
    )
    assert provider_api_args[: len(run_pytest.PROVIDER_API_TEST_TARGETS)] == list(
        run_pytest.PROVIDER_API_TEST_TARGETS
    )
    assert regression_args[: len(run_pytest.REGRESSION_TEST_TARGETS)] == list(run_pytest.REGRESSION_TEST_TARGETS)
    assert integration_args[: len(run_pytest.INTEGRATION_TEST_TARGETS)] == list(run_pytest.INTEGRATION_TEST_TARGETS)
    assert equilibrium_confidence_args[: len(run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS)] == list(
        run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS
    )
    assert equilibrium_api_args[: len(run_pytest.EQUILIBRIUM_API_TEST_TARGETS)] == list(
        run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    )
    assert runtime_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]
    assert api_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]
    assert native_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]
    assert native_contract_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]
    assert provider_api_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]
    assert regression_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]
    assert integration_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]
    assert equilibrium_confidence_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]
    assert equilibrium_api_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]


def test_pytest_slice_dispatch_rejects_multiple_programmatic_flags():
    with pytest.raises(ValueError, match="mutually exclusive"):
        run_pytest._pytest_args(["-q"], Path("build") / "pytest-temp" / "run-test", generic=True, api=True)


def test_plot_output_tests_have_no_named_slice():
    assert "plots" not in run_pytest.SLICE_TARGETS
    assert all(
        not target.startswith("tests/plots/") for targets in run_pytest.SLICE_TARGETS.values() for target in targets
    )


def test_slice_targets_use_grouped_test_subpackages():
    all_targets = [
        *run_pytest.GENERIC_TEST_TARGETS,
        *run_pytest.CONFIDENCE_TEST_TARGETS,
        *run_pytest.RUNTIME_TEST_TARGETS,
        *run_pytest.API_TEST_TARGETS,
        *run_pytest.NATIVE_TEST_TARGETS,
        *run_pytest.NATIVE_CONTRACT_TEST_TARGETS,
        *run_pytest.PROVIDER_API_TEST_TARGETS,
        *run_pytest.REGRESSION_TEST_TARGETS,
        *run_pytest.INTEGRATION_TEST_TARGETS,
        *run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS,
        *run_pytest.EQUILIBRIUM_API_TEST_TARGETS,
    ]

    assert all(
        target.startswith(
            (
                "tests/",
                "packages/epcsaft/tests/",
                "packages/epcsaft-equilibrium/tests/",
                "packages/epcsaft-regression/tests/",
            )
        )
        for target in all_targets
    )
    assert all(target.count("/") >= 2 for target in all_targets)
    assert "tests/api/frontend" not in run_pytest.API_TEST_TARGETS
    assert "tests/api/frontend" not in run_pytest.GENERIC_TEST_TARGETS
    assert "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py" not in run_pytest.API_TEST_TARGETS
    assert "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py" not in run_pytest.GENERIC_TEST_TARGETS
    assert PROVIDER_API_IMPORTS_TEST in run_pytest.API_TEST_TARGETS
    assert "tests/api/frontend/test_regression.py" not in run_pytest.API_TEST_TARGETS
    assert "tests/api/frontend/test_regression.py" not in run_pytest.REGRESSION_TEST_TARGETS
    assert REGRESSION_API_TEST_FILE in run_pytest.REGRESSION_TEST_TARGETS
    assert "packages/epcsaft-equilibrium/tests/api/test_imports.py" in run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    assert EQUILIBRIUM_CAPABILITY_TEST_FILE in run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    assert PROVIDER_API_STATE_PROPERTIES_TEST in run_pytest.GENERIC_TEST_TARGETS
    assert "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py" not in run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    assert (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::test_equilibrium_constructor_configures_route_before_solve"
        in run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    )
    assert (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::test_equilibrium_lle_route_returns_named_liquid_phase_helpers"
        not in run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    )
    assert all(
        "recovers_shared" not in target and "returns_named" not in target
        for target in run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    )
    assert EQUILIBRIUM_BUBBLE_DERIVATIVE_TEST_FILE in run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    assert EQUILIBRIUM_BUBBLE_DERIVATIVE_TEST_FILE not in run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS
    assert (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route"
    ) in run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS
    assert (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::"
        "test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point"
    ) in run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS
    assert (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::test_equilibrium_lle_route_returns_named_liquid_phase_helpers"
    ) in run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS
    assert all(
        "packages/epcsaft-equilibrium/tests/native/results" not in target
        for target in run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS
    )
    assert "tests/native/contracts/test_equation_registry.py::test_equation_registry_outputs_are_synced" in (
        run_pytest.GENERIC_TEST_TARGETS
    )
    assert "packages/epcsaft/tests/api/frontend/test_state_properties.py::test_cppad_state_proves_hydrocarbon_values_and_derivatives" in (
        run_pytest.RUNTIME_TEST_TARGETS
    )
    assert "tests/workflows/repo/test_run_pytest.py" not in run_pytest.GENERIC_TEST_TARGETS


def test_native_contract_slice_uses_small_metadata_files_not_full_route_builder_suite():
    assert "tests/native/contracts/test_generalized_equilibrium_registry.py" in (
        run_pytest.NATIVE_CONTRACT_TEST_TARGETS
    )
    assert "tests/native/contracts/test_equilibrium_benchmark_registry.py" in run_pytest.NATIVE_CONTRACT_TEST_TARGETS
    assert EQUILIBRIUM_CAPABILITY_TEST_FILE not in run_pytest.NATIVE_CONTRACT_TEST_TARGETS
    assert EQUILIBRIUM_CAPABILITY_TEST_FILE in run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    assert EQUILIBRIUM_SELECTOR_CONTRACT_TEST in run_pytest.NATIVE_CONTRACT_TEST_TARGETS
    assert all("test_route_builders_" not in target for target in run_pytest.NATIVE_CONTRACT_TEST_TARGETS)


def test_package_local_equilibrium_native_tests_are_labeled() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    root_conftest = Path("tests/conftest.py").read_text(encoding="utf-8")
    package_conftest = Path("packages/epcsaft-equilibrium/tests/conftest.py").read_text(encoding="utf-8")

    assert "equilibrium_native_transition" in pyproject
    assert "tests/native/equilibrium/" not in root_conftest
    assert "test_equilibrium_native_contracts.py" not in root_conftest
    assert "test_equilibrium_benchmark_registry.py" in root_conftest
    assert "test_generalized_equilibrium_registry.py" in root_conftest
    assert "packages/epcsaft-equilibrium/tests/native/" in package_conftest
    assert "test_equilibrium_native_contracts.py" in package_conftest


def test_provider_slice_does_not_import_equilibrium_extension() -> None:
    assert set(run_pytest.API_TEST_TARGETS) == set(run_pytest.PROVIDER_API_TEST_TARGETS)
    assert all("epcsaft-equilibrium" not in target for target in run_pytest.PROVIDER_API_TEST_TARGETS)
    assert all("test_equilibrium" not in target for target in run_pytest.PROVIDER_API_TEST_TARGETS)

    for target in run_pytest.PROVIDER_API_TEST_TARGETS:
        source = Path(target.split("::", 1)[0]).read_text(encoding="utf-8")
        assert "epcsaft_equilibrium" not in source
        assert "from epcsaft import Equilibrium" not in source
        assert "epcsaft.Equilibrium" not in source


def test_regression_slice_is_package_owned() -> None:
    assert REGRESSION_API_TEST_FILE in run_pytest.REGRESSION_TEST_TARGETS
    assert REGRESSION_NATIVE_PURE_TEST in run_pytest.REGRESSION_TEST_TARGETS
    assert REGRESSION_NATIVE_BINARY_TEST in run_pytest.REGRESSION_TEST_TARGETS
    assert all("epcsaft-equilibrium" not in target for target in run_pytest.REGRESSION_TEST_TARGETS)
    assert "tests/api/frontend/test_regression.py" not in run_pytest.PROVIDER_API_TEST_TARGETS
    assert "tests/api/frontend/test_regression.py" not in run_pytest.REGRESSION_TEST_TARGETS


def test_broad_native_route_builder_targets_require_explicit_opt_in():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"
    route_builder_target = EQUILIBRIUM_NATIVE_TEST_ROOT

    try:
        run_pytest._pytest_args([route_builder_target, "-q"], pytest_temp)
    except SystemExit as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected broad route-builder file target to be rejected")

    assert "--native-contracts" in message
    allowed = run_pytest._pytest_args(
        [route_builder_target, "-q"],
        pytest_temp,
        allow_long_native_tests=True,
    )
    single_node = run_pytest._pytest_args(
        [
            f"{EQUILIBRIUM_SELECTOR_CONTRACT_TEST}::"
            "test_selector_core_contract_owns_production_vle_metadata",
            "-q",
        ],
        pytest_temp,
    )

    assert allowed[:2] == [route_builder_target, "-q"]
    assert single_node[0].endswith("::test_selector_core_contract_owns_production_vle_metadata")


def test_broad_frontend_equilibrium_route_file_requires_explicit_opt_in():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"
    route_solve_target = "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py"

    try:
        run_pytest._pytest_args([route_solve_target, "-q"], pytest_temp)
    except SystemExit as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected broad frontend equilibrium route file target to be rejected")

    assert "--equilibrium-confidence" in message
    assert "--allow-long-equilibrium-tests" in message

    allowed = run_pytest._pytest_args(
        [route_solve_target, "-q"],
        pytest_temp,
        allow_long_equilibrium_tests=True,
    )
    single_node = run_pytest._pytest_args(
        [
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::"
            "test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point",
            "-q",
        ],
        pytest_temp,
    )

    assert allowed[:2] == [route_solve_target, "-q"]
    assert single_node[0].endswith("::test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point")


def test_broad_native_equilibrium_result_targets_require_explicit_opt_in():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"
    result_targets = (
        EQUILIBRIUM_NATIVE_RESULTS_ROOT,
        EQUILIBRIUM_NATIVE_VLE_RESULTS_TEST,
        EQUILIBRIUM_NATIVE_LLE_RESULTS_TEST,
    )

    for target in result_targets:
        with pytest.raises(SystemExit, match="--allow-long-equilibrium-tests"):
            run_pytest._pytest_args([target, "-q"], pytest_temp)

    allowed = run_pytest._pytest_args(
        [EQUILIBRIUM_NATIVE_LLE_RESULTS_TEST, "-q"],
        pytest_temp,
        allow_long_equilibrium_tests=True,
    )
    single_node = run_pytest._pytest_args(
        [
            f"{EQUILIBRIUM_NATIVE_LLE_RESULTS_TEST}::"
            "test_neutral_tpd_phase_discovery_can_run_deterministic_screening_without_continuous_tpd",
            "-q",
        ],
        pytest_temp,
    )

    assert allowed[:2] == [EQUILIBRIUM_NATIVE_LLE_RESULTS_TEST, "-q"]
    assert single_node[0].endswith(
        "::test_neutral_tpd_phase_discovery_can_run_deterministic_screening_without_continuous_tpd"
    )


def test_equilibrium_slices_are_listed():
    for flag, label in (
        ("--provider-api", "provider-api:"),
        ("--equilibrium-confidence", "equilibrium-confidence:"),
        ("--equilibrium-api", "equilibrium-api:"),
        ("--regression", "regression:"),
        ("--integration", "integration:"),
    ):
        result = subprocess.run(
            [sys.executable, "run_pytest.py", flag, "--list-slices"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0
        assert label in result.stdout


def test_equilibrium_confidence_shortcut_keeps_full_report_env_opt_in():
    source = Path(run_pytest.__file__).read_text(encoding="utf-8")

    assert 'env["EPCSAFT_EQUILIBRIUM_CONFIDENCE"] = "1"' not in source


def test_equilibrium_confidence_slice_uses_one_target_per_public_route_family():
    targets = run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS

    assert len(targets) == 3
    assert "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py" not in targets
    assert (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::"
        "test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route"
    ) in targets
    assert (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::"
        "test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point"
    ) in targets
    assert (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::"
        "test_equilibrium_flash_rejects_ipopt_iteration_limit_before_postsolve"
    ) not in targets
    assert (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::"
        "test_equilibrium_lle_route_returns_named_liquid_phase_helpers"
    ) in targets
    assert all("iteration_limit" not in target for target in targets)
    assert all("packages/epcsaft-equilibrium/tests/native/diagnostics" not in target for target in targets)
    assert "packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py" not in targets
    assert all("paper_validation" not in target for target in targets)
    assert all("tests/regression/literature" not in target for target in targets)
    assert all("tests/workflows/validation" not in target for target in targets)


def test_equilibrium_debug_without_explicit_target_requires_bounded_selection():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    with pytest.raises(SystemExit, match="requires one explicit equilibrium test node"):
        run_pytest._pytest_args(["-q", "-s"], pytest_temp, equilibrium_debug=True)


def test_equilibrium_debug_with_only_pytest_filter_requires_bounded_selection():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    with pytest.raises(SystemExit, match="requires one explicit equilibrium test node"):
        run_pytest._pytest_args(["-k", "flash", "-q", "-s"], pytest_temp, equilibrium_debug=True)


def test_equilibrium_debug_rejects_confidence_slice_sweeps():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    with pytest.raises(SystemExit, match="one explicit equilibrium test node"):
        run_pytest._pytest_args(["-q", "-s"], pytest_temp, equilibrium_confidence=True, equilibrium_debug=True)


def test_equilibrium_debug_accepts_exactly_one_equilibrium_test_node():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"
    target = (
        f"{EQUILIBRIUM_NATIVE_LLE_RESULTS_TEST}::"
        "test_neutral_tpd_phase_discovery_reports_candidate_set_for_lle_binary"
    )

    args = run_pytest._pytest_args([target, "-q", "-s"], pytest_temp, equilibrium_debug=True)

    assert args[0] == target
    assert args[-4:] == ["-q", "-s", "--basetemp", str(pytest_temp)]


def test_equilibrium_debug_rejects_sweeps_and_non_equilibrium_targets():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"
    first = (
        f"{EQUILIBRIUM_NATIVE_LLE_RESULTS_TEST}::"
        "test_neutral_tpd_phase_discovery_reports_candidate_set_for_lle_binary"
    )
    second = (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::"
        "test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point"
    )

    with pytest.raises(SystemExit, match="exactly one explicit equilibrium test node"):
        run_pytest._pytest_args([first, second, "-q"], pytest_temp, equilibrium_debug=True)

    with pytest.raises(SystemExit, match="must name one test node"):
        run_pytest._pytest_args(
            [EQUILIBRIUM_NATIVE_LLE_RESULTS_TEST, "-q"],
            pytest_temp,
            equilibrium_debug=True,
        )

    with pytest.raises(SystemExit, match="must be equilibrium tests"):
        run_pytest._pytest_args(
            ["packages/epcsaft/tests/api/frontend/test_state_properties.py::test_state_properties_use_molar_units", "-q"],
            pytest_temp,
            equilibrium_debug=True,
        )


def test_equilibrium_debug_rejects_confidence_plus_extra_targets():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"
    target = (
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::"
        "test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point"
    )

    with pytest.raises(SystemExit, match="do not use it with pytest slices"):
        run_pytest._pytest_args([target, "-q"], pytest_temp, equilibrium_confidence=True, equilibrium_debug=True)


def test_equilibrium_debug_rejects_non_equilibrium_slices():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    with pytest.raises(SystemExit, match="requires one explicit equilibrium test node"):
        run_pytest._pytest_args(["-q"], pytest_temp, generic=True, equilibrium_debug=True)

    with pytest.raises(SystemExit, match="requires one explicit equilibrium test node"):
        run_pytest._pytest_args(["-q"], pytest_temp, all_tests=True, equilibrium_debug=True)

    with pytest.raises(SystemExit, match="one explicit equilibrium test node"):
        run_pytest._pytest_args(["-q"], pytest_temp, equilibrium_confidence=True, equilibrium_debug=True)


def test_generic_and_api_slices_do_not_run_equilibrium_route_sweeps():
    blocked = {
        "tests/api/frontend",
        "packages/epcsaft/tests/api/frontend",
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
    }

    assert blocked.isdisjoint(run_pytest.GENERIC_TEST_TARGETS)
    assert blocked.isdisjoint(run_pytest.API_TEST_TARGETS)
    assert blocked.isdisjoint(run_pytest.EQUILIBRIUM_API_TEST_TARGETS)


def test_validation_lanes_do_not_smuggle_broad_equilibrium_sweeps_into_debug_paths():
    broad_equilibrium_targets = {
        "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
        EQUILIBRIUM_NATIVE_RESULTS_ROOT,
        EQUILIBRIUM_NATIVE_VLE_RESULTS_TEST,
        EQUILIBRIUM_NATIVE_LLE_RESULTS_TEST,
    }

    for lane_name, commands in validate_project.CHECK_COMMANDS.items():
        if lane_name == "full":
            continue
        flattened_commands = {" ".join(command) for command in commands}
        for command_text in flattened_commands:
            assert "--all" not in command_text
            for blocked_target in broad_equilibrium_targets:
                assert f" {blocked_target} " not in f" {command_text} "
        if lane_name == "equilibrium-debug":
            assert all(command[0] != "run_pytest.py" for command in commands)
            debug_command = commands[-1]
            assert debug_command == (
                "scripts/validation/check_phase_discovery.py",
                "--debug",
                "--include-route-refinement",
                "--require-complete",
            )


def test_pytest_temp_root_prefers_configured_root_and_normalizes_relative_paths(monkeypatch, tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.setenv("EPCSAFT_PYTEST_TEMP_ROOT", "external-temp")

    pytest_temp = run_pytest._pytest_temp(repo_root)

    assert pytest_temp.is_dir()
    assert pytest_temp.parent == repo_root / "external-temp" / "pytest-temp"
    shutil.rmtree(repo_root / "external-temp", ignore_errors=True)


def test_pytest_env_preserves_existing_perf_flags(monkeypatch):
    pytest_temp = Path("build") / "pytest-temp" / "run-test"
    monkeypatch.setenv("EPCSAFT_RUN_PERF", "0")
    monkeypatch.setenv("ePCSAFT_RUN_PERF", "0")

    normal_env = run_pytest._pytest_env(pytest_temp)

    assert normal_env.get("EPCSAFT_RUN_PERF", normal_env.get("ePCSAFT_RUN_PERF")) == "0"
    if sys.platform != "win32":
        assert normal_env["ePCSAFT_RUN_PERF"] == "0"


def test_slice_listing_text_names_all_targets():
    listing = run_pytest._slice_listing_text()

    assert run_pytest.SLICE_SELECTION_NOTE in listing
    for name, targets in run_pytest.SLICE_TARGETS.items():
        assert f"{name}:" in listing
        for target in targets:
            assert target in listing


def test_list_slices_exits_without_running_pytest():
    result = subprocess.run(
        [sys.executable, "run_pytest.py", "--list-slices"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Available slices:" in result.stdout
    assert "Running:" not in result.stdout


def test_slice_selection_note_uses_dev_validate_project_path():
    assert "`uv run python scripts/dev/validate_project.py quick`" in run_pytest.SLICE_SELECTION_NOTE
    assert "`uv run python scripts/validate_project.py quick`" not in run_pytest.SLICE_SELECTION_NOTE


def test_help_mentions_slice_append_semantics():
    result = subprocess.run(
        [sys.executable, "run_pytest.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Slice flags are mutually exclusive" in result.stdout
    assert "Extra positional pytest targets" in result.stdout
    assert "every retained pytest contract" in result.stdout
