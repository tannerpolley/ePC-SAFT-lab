from __future__ import annotations

from epcsaft_equilibrium.core.native_results import native_route_diagnostics


def test_native_route_diagnostics_normalizes_solver_route_and_seed_contract() -> None:
    route = {
        "compiled": True,
        "adapter_available": True,
        "ran": True,
        "accepted": False,
        "status": "postsolve_rejected",
        "rejection_reason": "phase_distance",
        "solver_accepted": True,
        "postsolve_accepted": False,
        "solver_status": "success",
        "application_status": "solve_succeeded",
        "gradient_approximation": "exact",
        "jacobian_approximation": "exact",
        "hessian_approximation": "exact",
        "exact_gradient_required": True,
        "exact_jacobian_required": True,
        "exact_hessian_available": True,
        "ipopt_print_level": 5,
        "max_iterations": 200,
        "seed_name": "mirrored_formula_shift",
        "seed_attempts": [
            {
                "seed_name": "canonical_formula_shift",
                "status": "solver_rejected",
                "solver_accepted": False,
                "accepted": False,
                "max_iterations": 200,
            },
            {
                "seed_name": "mirrored_formula_shift",
                "status": "postsolve_rejected",
                "solver_accepted": True,
                "accepted": False,
                "max_iterations": 200,
            },
        ],
        "postsolve": {
            "accepted": False,
            "rejection_reason": "phase_distance",
        },
        "physical_evidence": {
            "available": True,
            "phase_labels": ["liquid", "vapor"],
            "phase_roles": ["liquid", "vapor"],
            "material_balance_norm": 1.0e-9,
            "pressure_consistency_norm": 2.0e-3,
            "ln_fugacity_consistency_norm": 4.0e-7,
            "stability_checked": False,
            "phases": [
                {"label": "liquid", "role": "liquid", "composition": [0.4, 0.6]},
                {"label": "vapor", "role": "vapor", "composition": [0.7, 0.3]},
            ],
        },
    }

    diagnostics = native_route_diagnostics(route)

    assert diagnostics["compiled"] is True
    assert diagnostics["adapter_available"] is True
    assert diagnostics["solver_ran"] is True
    assert diagnostics["route_accepted"] is False
    assert diagnostics["postsolve_accepted"] is False
    assert diagnostics["rejection_reason"] == "phase_distance"
    assert diagnostics["gradient_is_exact"] is True
    assert diagnostics["jacobian_is_exact"] is True
    assert diagnostics["hessian_is_exact"] is True
    assert diagnostics["exact_derivatives_required"] is True
    assert diagnostics["ipopt_print_level"] == 5
    assert diagnostics["max_iterations"] == 200
    assert diagnostics["seed_attempt_count"] == 2
    assert diagnostics["seed_attempt_solver_accepted_count"] == 1
    assert diagnostics["seed_attempt_route_accepted_count"] == 0
    assert diagnostics["seed_attempts"][0]["route_status"] == "solver_rejected"
    assert diagnostics["seed_attempts"][0]["max_iterations"] == 200
    assert diagnostics["seed_attempts"][0]["selected_seed"] is False
    assert diagnostics["seed_attempts"][1]["route_status"] == "postsolve_rejected"
    assert diagnostics["seed_attempts"][1]["selected_seed"] is True
    assert diagnostics["seed_attempts"][1]["gradient_is_exact"] is True
    assert diagnostics["physical_evidence"]["phase_labels"] == ["liquid", "vapor"]
    assert diagnostics["phase_labels"] == ["liquid", "vapor"]
    assert diagnostics["phase_roles"] == ["liquid", "vapor"]


def test_native_route_diagnostics_preserves_route_metadata_contract() -> None:
    route = {
        "accepted": True,
        "status": "accepted",
        "postsolve_accepted": True,
        "rejection_reason": "accepted",
        "variable_model": "log_phase_species_amounts_plus_log_density",
        "density_backend": "explicit_log_density_pressure_constraint",
        "residual_families": [
            "conserved_balance",
            "reaction_stationarity",
            "phase_equilibrium",
            "phase_charge",
        ],
        "constraint_families": [
            "conserved_balance",
            "phase_charge",
            "phase_pressure_consistency",
            "phase_distance",
        ],
        "postsolve": {
            "accepted": True,
        },
    }

    diagnostics = native_route_diagnostics(route)

    assert diagnostics["variable_model"] == "log_phase_species_amounts_plus_log_density"
    assert diagnostics["density_backend"] == "explicit_log_density_pressure_constraint"
    assert diagnostics["postsolve_accepted"] is True
    assert diagnostics["rejection_reason"] == "accepted"
    assert diagnostics["residual_families"] == [
        "conserved_balance",
        "reaction_stationarity",
        "phase_equilibrium",
        "phase_charge",
    ]
    assert diagnostics["constraint_families"] == [
        "conserved_balance",
        "phase_charge",
        "phase_pressure_consistency",
        "phase_distance",
    ]


def test_native_route_diagnostics_preserves_stage8_ipopt_evidence_contract() -> None:
    route = {
        "accepted": True,
        "status": "accepted",
        "solver_accepted": True,
        "postsolve_accepted": True,
        "profile_exact_hessian_gate": True,
        "variable_scaling_quality_passed": True,
        "constraint_scaling_quality_passed": True,
        "restoration_phase_observed": False,
        "active_lower_bound_count": 1,
        "active_upper_bound_count": 2,
        "active_variable_bound_count": 3,
        "step_trial_count_max": 4,
        "bound_push": 1.0e-8,
        "bound_frac": 1.0e-7,
        "postsolve": {
            "accepted": True,
        },
    }

    diagnostics = native_route_diagnostics(route)

    assert diagnostics["profile_exact_hessian_gate"] is True
    assert diagnostics["variable_scaling_quality_passed"] is True
    assert diagnostics["constraint_scaling_quality_passed"] is True
    assert diagnostics["restoration_phase_observed"] is False
    assert diagnostics["active_lower_bound_count"] == 1
    assert diagnostics["active_upper_bound_count"] == 2
    assert diagnostics["active_variable_bound_count"] == 3
    assert diagnostics["step_trial_count_max"] == 4
    assert diagnostics["bound_push"] == 1.0e-8
    assert diagnostics["bound_frac"] == 1.0e-7
