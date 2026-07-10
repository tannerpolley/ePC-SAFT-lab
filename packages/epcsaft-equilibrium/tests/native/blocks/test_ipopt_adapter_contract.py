from __future__ import annotations

import math
import re
from pathlib import Path

import epcsaft_equilibrium
import pytest
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()


IPOPT_ADAPTER_SOURCE = (
    Path(__file__).resolve().parents[3]
    / "src"
    / "epcsaft_equilibrium"
    / "native"
    / "equilibrium"
    / "solvers"
    / "ipopt_adapter.cpp"
)


def test_native_ipopt_smoke_reports_generic_adapter_contract() -> None:
    smoke = _core._native_ipopt_smoke()

    assert smoke["backend"] == "ipopt"
    assert smoke["adapter_source_available"] is True
    assert smoke["adapter_kind"] == "native_tnlp_adapter"
    assert smoke["requires_exact_gradient"] is True
    assert smoke["requires_exact_jacobian"] is True
    assert smoke["available"] is smoke["compiled"]
    assert smoke["adapter_available"] is smoke["compiled"]


def test_runtime_capabilities_report_public_ipopt_routes() -> None:
    equilibrium = epcsaft_equilibrium.capabilities()
    ipopt = equilibrium["optimizer"]["ipopt"]

    assert ipopt["adapter_source_available"] is True
    assert ipopt["adapter_kind"] == "native_tnlp_adapter"
    assert ipopt["public_routes"] == equilibrium["activation_matrix"]["public_routes"]
    assert equilibrium["activation_matrix"]["public_route_family_map"] == {
        "bubble_pressure": "bubble_dew_derived_routes",
        "dew_pressure": "bubble_dew_derived_routes",
        "single_component_vle": "single_component_vle",
    }


def test_native_ipopt_quadratic_smoke_is_gated_by_compiled_dependency() -> None:
    smoke = _core._native_ipopt_quadratic_smoke()

    assert smoke["backend"] == "ipopt"
    assert smoke["adapter_kind"] == "native_tnlp_adapter"
    assert smoke["problem"] == "quadratic_linear_constraint_smoke"
    if not smoke["compiled"]:
        assert smoke["ran"] is False
        assert smoke["accepted"] is False
        assert smoke["status"] == "ipopt_dependency_required"
    else:
        assert smoke["ran"] is True
        assert smoke["accepted"] is True
        assert smoke["exact_gradient_required"] is True
        assert smoke["exact_jacobian_required"] is True
        assert smoke["hessian_approximation"] == "exact"
        assert smoke["hessian_backend"] == "analytic"
        assert smoke["eval_h_calls"] > 0
        assert abs(smoke["variables"][0] - 1.0) < 1.0e-6
        assert abs(smoke["variables"][1] - 2.0) < 1.0e-6
        assert abs(smoke["constraints"][0] - 3.0) < 1.0e-6


def test_native_second_order_assembler_smoke_covers_lagrangian_residual_and_transform_blocks() -> None:
    smoke = _core._native_second_order_assembly_smoke()

    assert smoke["nonzero_count"] == 3
    assert smoke["lagrangian_lower"] == pytest.approx([1.0, 6.5, 2.0])
    assert smoke["weighted_symmetry_lower"] == pytest.approx([0.0, 1.0e12, 0.0])
    assert smoke["residual_quadratic_lower"] == pytest.approx([12.0, 13.0, 24.0])
    assert smoke["transformed_lower"] == pytest.approx([118.0, 44.0, 13.0])


def test_native_variable_transform_smoke_exposes_solver_to_physical_chain_rule_contract() -> None:
    smoke = _core._native_variable_transform_smoke()

    assert smoke["method_names"] == ["solver_to_physical", "dx_du", "d2x_du2"]
    assert smoke["identity_policy"] == "identity_physical_coordinates"
    assert smoke["identity_backend"] == "analytic_identity"
    assert smoke["identity_physical"] == pytest.approx([1.0, 2.0, 3.0])
    assert smoke["identity_dx_du"] == pytest.approx(
        [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        ]
    )
    assert smoke["identity_d2x_du2"] == pytest.approx([0.0] * 27)
    assert smoke["identity_second_order_backend"] == "analytic_identity"

    assert smoke["positive_log_policy"] == "positive_log_coordinates"
    assert smoke["positive_log_backend"] == "analytic_positive_log"
    assert smoke["positive_log_physical"] == pytest.approx([2.0, 3.0])
    assert smoke["positive_log_dx_du"] == pytest.approx([2.0, 0.0, 0.0, 3.0])
    assert smoke["positive_log_d2x_du2"] == pytest.approx(
        [
            2.0, 0.0,
            0.0, 0.0,
            0.0, 0.0,
            0.0, 3.0,
        ]
    )
    assert smoke["positive_log_chain_rule_gradient"] == pytest.approx([4.0, 9.0])
    assert smoke["positive_log_chain_rule_lower"] == pytest.approx([8.0, 0.0, 18.0])


def test_native_nlp_shape_validation_rejects_sparse_value_mismatches() -> None:
    smoke = _core._native_nlp_shape_validation_smoke()

    assert smoke["valid"]["accepted"] is True
    assert smoke["gradient_value_size"]["accepted"] is False
    assert "NLP objective gradient has size" in smoke["gradient_value_size"]["message"]
    assert smoke["jacobian_value_size"]["accepted"] is False
    assert "NLP Jacobian values has size" in smoke["jacobian_value_size"]["message"]
    assert smoke["jacobian_value_nonfinite"]["accepted"] is False
    assert "NLP Jacobian values must be finite" in smoke["jacobian_value_nonfinite"]["message"]
    assert smoke["hessian_value_size"]["accepted"] is False
    assert "NLP Hessian values has size" in smoke["hessian_value_size"]["message"]


def test_native_ipopt_quadratic_exact_hessian_reports_callback_and_bounded_history() -> None:
    smoke = _core._native_ipopt_quadratic_smoke(hessian_mode="exact", iteration_history_limit=2)

    assert smoke["backend"] == "ipopt"
    assert smoke["adapter_kind"] == "native_tnlp_adapter"
    if not smoke["compiled"]:
        assert smoke["status"] == "ipopt_dependency_required"
        return

    assert smoke["accepted"] is True
    assert smoke["hessian_approximation"] == "exact"
    assert smoke["hessian_backend"] == "analytic"
    assert smoke["exact_hessian_available"] is True
    assert smoke["eval_h_calls"] > 0
    assert smoke["iteration_count"] >= len(smoke["iteration_history"])
    assert len(smoke["iteration_history"]) <= 2
    assert smoke["iteration_history_limit"] == 2
    assert smoke["scaling_method"] == "user-scaling"
    assert smoke["option_profile"] == "proof"
    assert smoke["solver_acceptance_policy"] == "success_status_and_scaled_kkt_required"
    assert smoke["acceptable_iteration_limit"] == 0
    assert smoke["exact_hessian_policy"] == "required_by_profile"
    assert smoke["profile_exact_hessian_gate"] is True
    assert smoke["scaling_contract"] == "adapter_enforced_nlp_objective_variable_constraint_scaling"
    assert smoke["residual_scaling_policy"] == "nlp_provided_nondimensional_or_extensive_reference_scales"
    assert smoke["linear_solver_policy"] == "ipopt_default_recorded"
    assert smoke["barrier_policy"] == "ipopt_internal_barrier_for_declared_bounds"
    assert smoke["variable_scaling_count"] == 2
    assert smoke["constraint_scaling_count"] == 1
    assert smoke["objective_scaling"] == pytest.approx(1.0)
    assert smoke["variable_scaling_min"] == pytest.approx(1.0)
    assert smoke["variable_scaling_max"] == pytest.approx(1.0)
    assert smoke["constraint_scaling_min"] == pytest.approx(1.0)
    assert smoke["constraint_scaling_max"] == pytest.approx(1.0)
    assert smoke["variable_scaling_ratio"] == pytest.approx(1.0)
    assert smoke["constraint_scaling_ratio"] == pytest.approx(1.0)
    assert smoke["variable_scaling_quality_passed"] is True
    assert smoke["constraint_scaling_quality_passed"] is True
    assert smoke["scaled_constraint_violation_inf_norm"] <= smoke["constraint_violation_tolerance"]
    assert smoke["ipopt_unscaled_constraint_violation_tolerance"] >= smoke["constraint_violation_tolerance"]
    assert smoke["scaled_stationarity_inf_norm"] <= smoke["dual_infeasibility_tolerance"]
    assert smoke["scaled_complementarity_inf_norm"] <= smoke["complementarity_tolerance"]
    assert smoke["bound_complementarity_inf_norm"] <= smoke["complementarity_tolerance"]
    assert smoke["scaled_acceptance_passed"] is True
    assert smoke["active_lower_bound_count"] >= 0
    assert smoke["active_upper_bound_count"] >= 0
    assert smoke["active_variable_bound_count"] == (
        smoke["active_lower_bound_count"] + smoke["active_upper_bound_count"]
    )
    assert smoke["step_trial_count_max"] >= 0
    assert math.isfinite(smoke["barrier_parameter_final"])
    assert math.isfinite(smoke["regularization_size_final"])
    assert math.isfinite(smoke["regularization_size_max"])
    assert smoke["restoration_phase_observed"] in {False, True}


def test_native_ipopt_quadratic_limited_memory_is_diagnostic_only() -> None:
    smoke = _core._native_ipopt_quadratic_smoke(
        hessian_mode="limited-memory",
        option_profile="diagnostic",
    )

    assert smoke["backend"] == "ipopt"
    if not smoke["compiled"]:
        assert smoke["status"] == "ipopt_dependency_required"
        return

    assert smoke["accepted"] is True
    assert smoke["option_profile"] == "diagnostic"
    assert smoke["solver_acceptance_policy"] == "diagnostic_status_and_scaled_kkt_recorded"
    assert smoke["acceptable_iteration_limit"] == 15
    assert smoke["exact_hessian_policy"] == "diagnostic_profile_allows_limited_memory"
    assert smoke["profile_exact_hessian_gate"] is False
    assert smoke["hessian_approximation"] == "limited-memory"
    assert smoke["hessian_backend"] == "limited-memory"
    assert smoke["eval_h_calls"] == 0


def test_native_ipopt_quadratic_production_profile_rejects_limited_memory() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        return

    with pytest.raises(Exception, match="production option_profile requires exact Hessian support"):
        _core._native_ipopt_quadratic_smoke(hessian_mode="limited-memory", option_profile="proof")


def test_native_ipopt_quadratic_option_profiles_apply_contract_defaults() -> None:
    smoke = _core._native_ipopt_quadratic_smoke(
        hessian_mode="exact",
        option_profile="continuation_trace",
        iteration_history_limit=2,
    )

    assert smoke["backend"] == "ipopt"
    if not smoke["compiled"]:
        assert smoke["status"] == "ipopt_dependency_required"
        return

    assert smoke["accepted"] is True
    assert smoke["option_profile"] == "continuation_trace"
    assert smoke["solver_acceptance_policy"] == "success_status_and_scaled_kkt_required"
    assert smoke["acceptable_iteration_limit"] == 0
    assert smoke["profile_exact_hessian_gate"] is True
    assert smoke["iteration_history_limit"] == 50
    assert len(smoke["iteration_history"]) <= 50
    assert smoke["bound_push"] >= 1.0e-9
    assert smoke["bound_frac"] >= 1.0e-9
    assert smoke["scaled_acceptance_passed"] is True


def test_native_ipopt_quadratic_reports_linear_solver_and_tolerance_controls() -> None:
    smoke = _core._native_ipopt_quadratic_smoke(
        linear_solver="mumps",
        acceptable_tolerance=9.0e-7,
        constraint_violation_tolerance=8.0e-8,
        dual_infeasibility_tolerance=7.0e-8,
        complementarity_tolerance=6.0e-8,
    )

    assert smoke["backend"] == "ipopt"
    if not smoke["compiled"]:
        assert smoke["status"] == "ipopt_dependency_required"
        return

    assert smoke["accepted"] is True
    assert smoke["linear_solver_requested"] == "mumps"
    assert smoke["acceptable_tolerance"] == pytest.approx(9.0e-7)
    assert smoke["constraint_violation_tolerance"] == pytest.approx(8.0e-8)
    assert smoke["ipopt_unscaled_constraint_violation_tolerance"] == pytest.approx(8.0e-8)
    assert smoke["dual_infeasibility_tolerance"] == pytest.approx(7.0e-8)
    assert smoke["complementarity_tolerance"] == pytest.approx(6.0e-8)


def test_native_ipopt_rejects_an_unregistered_required_option_value() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        return

    with pytest.raises(Exception, match="requires unsupported option 'linear_solver'"):
        _core._native_ipopt_quadratic_smoke(linear_solver="definitely_unknown")


def test_old_ipopt_compatibility_uses_checked_supported_interfaces() -> None:
    source = IPOPT_ADAPTER_SOURCE.read_text(encoding="utf-8")
    option_setter = r"app->Options\(\)->Set(?:Integer|Numeric|String)Value\("
    checked_option_setter = rf"require_option\(\s*{option_setter}"

    assert len(re.findall(option_setter, source)) == len(re.findall(checked_option_setter, source))
    assert 'SetStringValue("gradient_approximation"' not in source
    assert 'SetNumericValue("max_wall_time"' not in source
    assert "get_curr_violations(" not in source
    assert "curr_nlp_constraint_violation(Ipopt::NORM_MAX)" in source
    assert "curr_dual_infeasibility(Ipopt::NORM_MAX)" in source
    assert "curr_complementarity(0.0, Ipopt::NORM_MAX)" in source


def test_native_ipopt_quadratic_warm_start_round_trips_primal_and_multipliers() -> None:
    first = _core._native_ipopt_quadratic_smoke(hessian_mode="exact")
    if not first["compiled"]:
        assert first["status"] == "ipopt_dependency_required"
        return

    continuation_state = first["continuation_state"]
    second = _core._native_ipopt_quadratic_smoke(
        hessian_mode="exact",
        continuation_state=continuation_state,
    )

    assert second["accepted"] is True
    assert second["warm_start_requested"] is True
    assert second["warm_start_used"] is True
    assert second["continuation_state"]["variables"] == second["variables"]
    assert len(second["continuation_state"]["bound_lower_multipliers"]) == 2
    assert len(second["continuation_state"]["bound_upper_multipliers"]) == 2
    assert len(second["continuation_state"]["constraint_multipliers"]) == 1


def test_native_ipopt_quadratic_rejects_incompatible_continuation_state() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        return

    bad_state = {
        "variables": [1.0],
        "bound_lower_multipliers": [0.0],
        "bound_upper_multipliers": [0.0],
        "constraint_multipliers": [0.0],
    }

    try:
        _core._native_ipopt_quadratic_smoke(continuation_state=bad_state)
    except Exception as exc:  # pybind exposes native ValueError as a module exception type.
        assert "continuation_state.variables" in str(exc)
    else:
        raise AssertionError("incompatible continuation_state was accepted")
