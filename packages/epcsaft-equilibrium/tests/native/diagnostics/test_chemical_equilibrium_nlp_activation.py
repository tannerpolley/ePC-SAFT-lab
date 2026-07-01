from __future__ import annotations

import math

import pytest
from epcsaft_equilibrium._native import extension_native_core
from epcsaft_equilibrium.chemical_equilibrium import (
    ChemicalReaction,
    ChemicalSpecies,
    EquilibriumConstantRecord,
    StandardStateRecord,
    build_standard_state_registry,
    compile_reaction_set,
    solve_chemical_equilibrium_nlp_activation,
)

_core = extension_native_core()

pytestmark = pytest.mark.native_contract


def _ideal_ab_problem():
    standard_state = StandardStateRecord(
        label="mole_fraction_standard_state",
        activity_convention="mole_fraction_activity",
        temperature_K=298.15,
        pressure_Pa=101325.0,
    )
    compiled = compile_reaction_set(
        species=[
            ChemicalSpecies("A", {"X": 1.0}),
            ChemicalSpecies("B", {"X": 1.0}),
        ],
        reactions=[ChemicalReaction("a_to_b", {"A": -1.0, "B": 1.0})],
        feed_amounts={"A": 1.0, "B": 0.0},
    )
    registry = build_standard_state_registry(
        [
            EquilibriumConstantRecord(
                reaction_label="a_to_b",
                value=math.log(3.0),
                form="ln_K",
                units="dimensionless",
                standard_state=standard_state,
                source="native contract fixture",
                source_constant_label="ln_K",
            )
        ]
    )
    return compiled, registry


def test_reactive_speciation_activation_matrix_declares_single_nlp_proof_only() -> None:
    rows = {row["key"]: row for row in _core._native_equilibrium_activation_matrix()}
    reactive = rows["reactive_speciation"]

    assert reactive["production_exposed"] is True
    assert reactive["exposure_status"] == "production_exposed"
    assert reactive["proof_routes"] == ["reactive_speciation_single_nlp_ipopt_exact_hessian"]
    assert reactive["public_routes"] == ["reactive_speciation"]
    assert reactive["solver_strategy"] == "ipopt_nlp_with_internal_continuation"
    assert reactive["initialization_strategy"] == "max_min_feasible_interior"
    assert reactive["continuation_strategy"] == "adaptive_k_scaling_homotopy"
    assert reactive["final_proof_policy"] == "true_gibbs_lambda_1_only"
    assert reactive["variable_model"] == "single_phase_species_amounts"
    assert reactive["density_backend"] == "homogeneous_standard_state_activity"
    assert reactive["constraint_families"] == ["conserved_balance"]
    assert reactive["residual_families"] == ["conserved_balance", "reaction_stationarity"]


def test_frontend_standalone_ce_uses_single_activation_nlp_path() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    compiled, registry = _ideal_ab_problem()
    result = solve_chemical_equilibrium_nlp_activation(
        compiled,
        registry,
        initial_amounts=[0.5, 0.5],
        max_iterations=100,
        tolerance=1.0e-10,
    )

    assert result["native_binding"] == "_native_chemical_equilibrium_nlp_activation"
    assert result["route"] == "reactive_speciation"
    assert result["activation_compiler"] == "activation_plan"
    assert result["selector_contract"] == {
        "selector_family": "reactive_speciation",
        "route": "reactive_speciation",
        "activation_compiler": "activation_plan",
        "problem_name": "reactive_speciation_ideal_gibbs_nlp",
    }

    activation = result["activation"]
    assert activation["key"] == "reactive_speciation"
    assert activation["public_routes"] == ["reactive_speciation"]
    assert activation["proof_routes"] == ["reactive_speciation_single_nlp_ipopt_exact_hessian"]
    assert activation["solver_strategy"] == "ipopt_nlp_with_internal_continuation"
    assert activation["initialization_strategy"] == "max_min_feasible_interior"
    assert activation["continuation_strategy"] == "adaptive_k_scaling_homotopy"
    assert activation["final_proof_policy"] == "true_gibbs_lambda_1_only"

    plan = result["activation_plan"]
    assert plan["family_key"] == "reactive_speciation"
    assert plan["route"] == "reactive_speciation"
    assert plan["variable_blocks"] == ["species_amounts"]
    assert plan["constraint_blocks"] == ["conserved_balance"]
    assert plan["residual_blocks"] == ["conserved_balance", "reaction_stationarity"]
    assert plan["postsolve_blocks"] == ["conserved_balance", "reaction_stationarity"]

    layout = result["variable_layout"]
    assert layout["variable_model"] == "single_phase_species_amounts"
    assert layout["solver_coordinate_basis"] == "log_species_amounts"
    assert layout["transform_policy"] == "positive_log_coordinates"
    assert layout["phase_keys"] == ["homogeneous"]
    assert layout["phase_kinds"] == ["homogeneous"]
    assert layout["variable_count"] == 2
    assert layout["phase_amount_indices"] == [[0, 1]]
    assert layout["phase_volume_indices"] == []

    activated = result["activated"]
    assert activated["problem_name"] == "reactive_speciation_ideal_gibbs_nlp"
    assert activated["activation_compiler"] == "activation_plan"
    assert activated["variable_model"] == "single_phase_species_amounts"
    assert activated["transform_policy"] == "positive_log_coordinates"
    assert activated["transform_backend"] == "analytic_positive_log"
    assert activated["density_backend"] == "homogeneous_standard_state_activity"
    assert activated["balance_row_count"] == 1
    assert activated["reaction_count"] == 1
    assert activated["constraint_count"] == 1
    assert activated["exact_hessian_available"] is True
    assert activated["derivatives"]["objective_gradient_exact"] is True
    assert activated["derivatives"]["constraint_jacobian_exact"] is True
    assert activated["derivatives"]["lagrangian_hessian_exact"] is True

    solver = result["solver_diagnostics"]
    assert solver["solver_backend"] == "ipopt"
    assert solver["solver_status"] == "success"
    assert solver["application_status"] == "solve_succeeded"
    assert solver["solver_accepted"] is True
    assert solver["profile_exact_hessian_gate"] is True
    assert solver["hessian_backend"] == "analytic"
    assert solver["activation_compiler"] == "activation_plan"

    assert result["accepted"] is True
    assert result["amounts"] == pytest.approx([0.25, 0.75], abs=1.0e-7)
    assert result["mole_fractions"] == pytest.approx([0.25, 0.75], abs=1.0e-7)
    assert result["balance_inf_norm"] < 1.0e-9
    assert result["reaction_stationarity_inf_norm"] < 1.0e-8


def test_no_side_channel_ce_solver_bindings_exist() -> None:
    expected = {
        "_native_chemical_equilibrium_block",
        "_native_chemical_equilibrium_nlp_activation",
    }
    chemical_equilibrium_bindings = {
        name for name in dir(_core) if name.startswith("_native_chemical_equilibrium")
    }

    assert chemical_equilibrium_bindings == expected
