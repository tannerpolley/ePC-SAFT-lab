import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import epcsaft.runtime.capability_evidence as capability_evidence
import run_pytest
from scripts.dev import doctor, validate_project


def test_confidence_slice_extends_generic_targets_without_changing_generic():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    generic_args = run_pytest._pytest_args(["-q"], pytest_temp, generic=True)
    confidence_args = run_pytest._pytest_args(["-q"], pytest_temp, confidence=True)

    assert generic_args[: len(run_pytest.GENERIC_TEST_TARGETS)] == list(run_pytest.GENERIC_TEST_TARGETS)
    assert "tests/native/state/test_properties.py" not in generic_args
    assert "tests/api/frontend" in generic_args
    assert confidence_args[: len(run_pytest.CONFIDENCE_TEST_TARGETS)] == list(run_pytest.CONFIDENCE_TEST_TARGETS)
    assert "tests/native/state/test_contributions.py::test_native_residual_helmholtz_and_compressibility_contributions_match_neutral_contract" in confidence_args
    assert confidence_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]


def test_default_pytest_route_uses_fast_contracts_not_exhaustive_suite():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    default_args = run_pytest._pytest_args(["-q"], pytest_temp)

    assert default_args[: len(run_pytest.FAST_TEST_TARGETS)] == list(run_pytest.FAST_TEST_TARGETS)
    assert "tests" not in default_args
    assert not any(target.startswith("tests/plots/") for target in default_args)
    assert "tests/workflows/validation/equilibrium_core/test_electrolyte_lle_confidence.py" not in default_args
    assert default_args[-3:] == ["-q", "--basetemp", str(pytest_temp)]


def test_predefined_pytest_targets_reference_existing_files():
    repo_root = Path(__file__).resolve().parents[3]
    missing: set[str] = set()

    for targets in run_pytest.SLICE_TARGETS.values():
        for target in targets:
            if target == "tests":
                continue
            target_path = target.split("::", 1)[0]
            if not (repo_root / target_path).exists():
                missing.add(target_path)

    assert not sorted(missing)


def test_all_shortcut_is_the_explicit_exhaustive_pytest_route():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"

    all_args = run_pytest._pytest_args(["-q"], pytest_temp, all_tests=True)

    assert all_args[: len(run_pytest.ALL_TEST_TARGETS)] == list(run_pytest.ALL_TEST_TARGETS)
    assert all_args == ["tests", "-q", "--basetemp", str(pytest_temp)]


def test_validate_project_modes_route_to_standard_validation_bundles():
    assert validate_project.CHECK_COMMANDS == {
        name: capability_evidence.validation_lane_commands(name)
        for name in capability_evidence.VALIDATION_LANES
    }
    assert validate_project.CHECK_COMMANDS["quick"] == (
        ("scripts/dev/doctor.py",),
        ("run_pytest.py", "-q"),
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
            "tests/native/regression/test_pure.py",
            "tests/native/regression/test_binary.py",
            "-q",
        ),
    )


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
    assert run_pytest.NATIVE_CONTRACT_TEST_TARGETS == capability_evidence.registry_targets("native-contracts")


def test_doctor_tracks_native_symbols_added_by_recent_workflows():
    required = set(doctor.REQUIRED_CORE_SYMBOLS)

    assert "_fit_pure_neutral_native_ceres" in required
    assert "_fit_pure_neutral_native_least" + "_squares" not in required
    assert "_fit_generic_native_least" + "_squares" not in required
    assert "_fit_generic_native_ceres" in required
    assert "_evaluate_generic_native_debug" in required
    assert "_native_ipopt_smoke" in required


def test_native_regression_source_has_no_eigen_nonlinear_optimizer_route():
    source = Path("src/epcsaft/native/regression/ceres_regression.cpp").read_text(encoding="utf-8")

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
        for path in sorted(Path("src/epcsaft/native").rglob("*"))
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
    equilibrium_confidence_args = run_pytest._pytest_args(["-q"], pytest_temp, equilibrium_confidence=True)
    equilibrium_api_args = run_pytest._pytest_args(["-q"], pytest_temp, equilibrium_api=True)

    assert runtime_args[: len(run_pytest.RUNTIME_TEST_TARGETS)] == list(run_pytest.RUNTIME_TEST_TARGETS)
    assert api_args[: len(run_pytest.API_TEST_TARGETS)] == list(run_pytest.API_TEST_TARGETS)
    assert native_args[: len(run_pytest.NATIVE_TEST_TARGETS)] == list(run_pytest.NATIVE_TEST_TARGETS)
    assert native_contract_args[: len(run_pytest.NATIVE_CONTRACT_TEST_TARGETS)] == list(
        run_pytest.NATIVE_CONTRACT_TEST_TARGETS
    )
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
        *run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS,
        *run_pytest.EQUILIBRIUM_API_TEST_TARGETS,
    ]

    assert all(target.startswith("tests/") for target in all_targets)
    assert all(target.count("/") >= 2 for target in all_targets)
    assert "tests/api/frontend" in run_pytest.API_TEST_TARGETS
    assert "tests/api/frontend" in run_pytest.GENERIC_TEST_TARGETS
    assert "tests/api/frontend/test_equilibrium.py" in run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    assert "tests/native/state/test_bubble_derivatives.py" in run_pytest.EQUILIBRIUM_API_TEST_TARGETS
    assert "tests/native/state/test_bubble_derivatives.py" not in run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS
    assert "tests/native/equilibrium/results/test_neutral_vle_reference_values.py" not in (
        run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS
    )
    assert (
        "tests/native/equilibrium/results/test_neutral_vle_reference_values.py::"
        "test_neutral_flash_reference_values_are_reported_and_verified"
    ) in run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS
    assert "tests/native/contracts/test_equation_registry.py::test_equation_registry_outputs_are_synced" in (
        run_pytest.GENERIC_TEST_TARGETS
    )
    assert "tests/api/frontend/test_state_properties.py::test_cppad_state_proves_hydrocarbon_values_and_derivatives" in (
        run_pytest.RUNTIME_TEST_TARGETS
    )
    assert "tests/workflows/repo/test_run_pytest.py" not in run_pytest.GENERIC_TEST_TARGETS


def test_native_contract_slice_uses_small_metadata_files_not_full_route_builder_suite():
    assert "tests/native/contracts/test_generalized_activation_matrix_registry.py" in (
        run_pytest.NATIVE_CONTRACT_TEST_TARGETS
    )
    assert "tests/native/contracts/test_equilibrium_benchmark_registry.py" in run_pytest.NATIVE_CONTRACT_TEST_TARGETS
    assert "tests/native/contracts/test_equilibrium_activation_capabilities.py" in run_pytest.NATIVE_CONTRACT_TEST_TARGETS
    assert "tests/native/equilibrium/diagnostics/test_selector_core_contracts.py" in run_pytest.NATIVE_CONTRACT_TEST_TARGETS
    assert all("test_route_builders_" not in target for target in run_pytest.NATIVE_CONTRACT_TEST_TARGETS)


def test_broad_native_route_builder_targets_require_explicit_opt_in():
    pytest_temp = Path("build") / "pytest-temp" / "run-test"
    route_builder_target = "tests/native/equilibrium"

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
            "tests/native/equilibrium/diagnostics/test_selector_core_contracts.py::"
            "test_selector_core_contract_owns_production_vle_metadata",
            "-q",
        ],
        pytest_temp,
    )

    assert allowed[:2] == [route_builder_target, "-q"]
    assert single_node[0].endswith("::test_selector_core_contract_owns_production_vle_metadata")


def test_equilibrium_slices_are_listed():
    for flag, label in (
        ("--equilibrium-confidence", "equilibrium-confidence:"),
        ("--equilibrium-api", "equilibrium-api:"),
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


def test_equilibrium_confidence_slice_uses_trusted_route_contracts_not_paper_pytests():
    targets = run_pytest.EQUILIBRIUM_CONFIDENCE_TEST_TARGETS

    assert "tests/native/equilibrium/diagnostics/test_selector_core_contracts.py" in targets
    assert "tests/api/frontend/test_equilibrium.py" not in targets
    assert (
        "tests/api/frontend/test_equilibrium.py::"
        "test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point"
    ) in targets
    assert (
        "tests/api/frontend/test_equilibrium.py::"
        "test_equilibrium_flash_rejects_ipopt_iteration_limit_before_postsolve"
    ) in targets
    assert "tests/native/equilibrium/diagnostics/test_native_route_diagnostics_contract.py" in targets
    assert "tests/native/state/test_bubble_derivatives.py" not in targets
    assert all("paper_validation" not in target for target in targets)
    assert all("tests/regression/literature" not in target for target in targets)
    assert all("tests/workflows/validation" not in target for target in targets)


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
