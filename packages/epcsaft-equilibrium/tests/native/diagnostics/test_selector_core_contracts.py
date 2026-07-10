from __future__ import annotations

import epcsaft._core as _provider_core
import numpy as np
import pytest
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()
from epcsaft.frontend import Mixture
from epcsaft.model.parameters import (
    InteractionProvenance,
    ParameterSet,
    PureRecord,
    StructuralZeroPolicy,
)
from epcsaft.state.native_adapter import ePCSAFTMixture
from equilibrium_support.equilibrium_cases import (
    GROSS_2002_PRESSURE_PA,
    _ionic_mixture,
    _methanol_cyclohexane_mixture,
    _neutral_binary_mixture,
    _nonideal_lle_binary_mixture,
    gross_2002_figure10_public_mixture,
)


def _skip_without_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("Ipopt native adapter is not compiled.")


def _pure_ethane_mixture() -> ePCSAFTMixture:
    params = {
        "MW": np.asarray([30.070e-3]),
        "m": np.asarray([1.6069]),
        "s": np.asarray([3.5206]),
        "e": np.asarray([191.42]),
    }
    return ePCSAFTMixture.from_params(params, species=["Ethane"])


def _unproven_pure_mixture() -> ePCSAFTMixture:
    params = {
        "MW": np.asarray([20.180e-3]),
        "m": np.asarray([1.2]),
        "s": np.asarray([3.1]),
        "e": np.asarray([120.0]),
    }
    return ePCSAFTMixture.from_params(params, species=["UnprovenPureComponent"])


@pytest.mark.parametrize(
    (
        "selector_request",
        "family",
        "problem_name",
        "composition_role",
        "phase_labels",
        "phase_roles",
        "specified_temperature",
        "specified_pressure",
    ),
    [
        (
            {
                "route": "bubble_pressure",
                "temperature": 300.0,
                "composition": [0.35, 0.65],
                "composition_role": "liquid",
            },
            "bubble_dew_derived_routes",
            "neutral_bubble_p_eos",
            "liquid",
            ["liquid", "vapor"],
            ["liquid", "vapor"],
            True,
            False,
        ),
        (
            {
                "route": "dew_pressure",
                "temperature": 300.0,
                "composition": [0.35, 0.65],
                "composition_role": "vapor",
            },
            "bubble_dew_derived_routes",
            "neutral_dew_p_eos",
            "vapor",
            ["liquid", "vapor"],
            ["liquid", "vapor"],
            True,
            False,
        ),
        (
            {
                "route": "single_component_vle",
                "temperature": 233.15,
                "composition": [1.0],
                "composition_role": "pure",
            },
            "single_component_vle",
            "single_component_vle_eos",
            "pure",
            ["liquid", "vapor"],
            ["liquid", "vapor"],
            True,
            False,
        ),
    ],
)
def test_selector_core_contract_owns_production_vle_metadata(
    selector_request: dict[str, object],
    family: str,
    problem_name: str,
    composition_role: str,
    phase_labels: list[str],
    phase_roles: list[str],
    specified_temperature: bool,
    specified_pressure: bool,
) -> None:
    if selector_request["route"] == "single_component_vle":
        mix = _pure_ethane_mixture()
    else:
        mix = _neutral_binary_mixture()
    payload = _core._native_equilibrium_selector_contract(mix._native, selector_request)
    matrix = {row["key"]: row for row in _core._native_equilibrium_activation_matrix()}
    activation = matrix[family]

    assert payload["selector_family"] == family
    assert payload["route"] == selector_request["route"]
    assert payload["problem_name"] == problem_name
    assert payload["composition_role"] == composition_role
    assert payload["phase_labels"] == phase_labels
    assert payload["phase_roles"] == phase_roles
    assert payload["specified_temperature"] is specified_temperature
    assert payload["specified_pressure"] is specified_pressure
    assert payload["production_exposed"] is True
    assert payload["certification_required"] is True
    assert payload["density_closure_required"] is True
    assert payload["exact_derivatives_required"] is True
    classification = payload["input_classification"]
    assert classification["neutral"] is True
    assert classification["nonreactive"] is True
    assert classification["nonelectrolyte"] is True
    assert classification["nonassociating"] is True
    expected_species_indices = [0] if selector_request["route"] == "single_component_vle" else [0, 1]
    assert classification["neutral_species_indices"] == expected_species_indices
    assert classification["ionic_species_indices"] == []
    assert classification["associating_species_indices"] == []
    assert classification["phase_eligible_species_indices"] == expected_species_indices
    assert classification["transferable_species_indices"] == expected_species_indices
    assert classification["fixed_species_indices"] == []
    assert classification["active_family_markers"] == ["neutral", "nonreactive"]

    request_pretreatment = payload["request_pretreatment"]
    assert request_pretreatment["route_shape_validated"] is True
    assert request_pretreatment["finite_numeric_inputs"] is True
    assert request_pretreatment["species_count"] == len(expected_species_indices)
    assert request_pretreatment["composition_length"] == len(expected_species_indices)
    assert request_pretreatment["composition_normalized_sum"] == pytest.approx(1.0)
    assert request_pretreatment["composition_basis"] == "mole_fraction"

    thermodynamic_input = payload["thermodynamic_input"]
    assert thermodynamic_input["species_indices"] == expected_species_indices
    assert thermodynamic_input["composition_role"] == composition_role
    assert thermodynamic_input["normalized_composition"] == pytest.approx(selector_request["composition"])
    assert thermodynamic_input["extensive_amounts"] == pytest.approx(selector_request["composition"])
    assert thermodynamic_input["amount_basis"] == "unit_total_moles"

    parameter_readiness = payload["parameter_readiness"]
    assert parameter_readiness["pure_neutral_parameters_present"] is True
    assert parameter_readiness["binary_interaction_matrix_present"] is True
    assert parameter_readiness["parameter_provenance_status"] == "runtime_payload_without_source_provenance"
    assert parameter_readiness["source_backed_parameter_provenance_present"] is False
    assert parameter_readiness["explicit_zero_binary_interaction_convention"] is False
    assert parameter_readiness["required_parameter_families_present"] is True
    assert parameter_readiness["missing_required_parameter_families"] == []
    assert parameter_readiness["association_parameters_active"] is False
    assert parameter_readiness["electrolyte_parameters_active"] is False
    assert payload["residual_families"] == activation["residual_families"]
    assert payload["constraint_families"] == activation["constraint_families"]
    assert payload["variable_model"] == activation["variable_model"]
    assert payload["density_backend"] == activation["density_backend"]


def test_selector_core_rejects_single_component_vle_for_binary_payload() -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(_provider_core.NativeValueError, match="single_component_vle requires exactly one component"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "single_component_vle",
                "temperature": 233.15,
                "composition": [1.0, 0.0],
                "composition_role": "pure",
            },
        )


def test_selector_core_rejects_old_scalar_composition_boundary() -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(TypeError):
        _core._native_equilibrium_selector_contract(
            mix._native,
            "bubble_pressure",
            300.0,
            [0.35, 0.65],
        )


def test_selector_core_rejects_invalid_route_family_before_solver_dispatch() -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(_provider_core.NativeValueError, match="selector-ineligible"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "electrolyte_lle",
                "temperature": 300.0,
                "composition": [0.35, 0.65],
                "composition_role": "feed",
            },
        )


def test_selector_core_rejects_single_component_vle_outside_nist_hydrocarbon_scope() -> None:
    mix = _unproven_pure_mixture()

    with pytest.raises(_provider_core.NativeValueError, match="NIST-backed methane, ethane, or propane"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "single_component_vle",
                "temperature": 233.15,
                "composition": [1.0],
                "composition_role": "pure",
            },
        )


@pytest.mark.parametrize(
    ("route", "composition_role"),
    (
        ("bubble_temperature", "liquid"),
        ("dew_temperature", "vapor"),
        ("neutral_tp_flash", "feed"),
        ("neutral_lle", "feed"),
    ),
)
def test_selector_core_rejects_unproven_declared_routes_before_dispatch(
    route: str,
    composition_role: str,
) -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(_provider_core.NativeValueError, match="not production exposed"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": route,
                "temperature": 300.0,
                "pressure": 1.0e6,
                "composition": [0.35, 0.65],
                "composition_role": composition_role,
            },
        )


def test_selector_core_rejects_active_association_before_solver_dispatch() -> None:
    mix = _methanol_cyclohexane_mixture()

    with pytest.raises(_provider_core.NativeValueError, match="selector-ineligible"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "bubble_pressure",
                "temperature": 298.15,
                "composition": [0.35, 0.65],
                "composition_role": "liquid",
            },
        )


def test_selector_core_rejects_gross_2002_figure10_vle_without_route_proof() -> None:
    mix = gross_2002_figure10_public_mixture()

    with pytest.raises(_provider_core.NativeValueError, match="Figures 2-9"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "dew_pressure",
                "temperature": 381.15,
                "composition": [0.73, 0.27],
                "composition_role": "vapor",
            },
        )


def test_selector_core_rejects_closed_ionic_lle_before_solver_dispatch() -> None:
    mix = _ionic_mixture()

    with pytest.raises(_provider_core.NativeValueError, match="not production exposed"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "neutral_lle",
                "temperature": 300.0,
                "pressure": 1.0e5,
                "composition": [0.8, 0.1, 0.1],
                "composition_role": "feed",
            },
        )


def test_selector_core_rejects_missing_binary_interactions_before_solver_dispatch() -> None:
    mix = ePCSAFTMixture.from_params(
        {
            "m": [1.0, 1.6069],
            "s": [3.7039, 3.5206],
            "e": [150.03, 191.42],
        },
        species=["Methane", "Ethane"],
    )

    with pytest.raises(_provider_core.NativeValueError, match="binary_interaction_matrix"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "bubble_pressure",
                "temperature": 300.0,
                "composition": [0.35, 0.65],
                "composition_role": "liquid",
            },
        )


def test_selector_core_accepts_source_backed_explicit_zero_binary_convention() -> None:
    parameters = ParameterSet.from_records(
        [
            PureRecord(
                component="Methane",
                molar_mass=16.043e-3,
                m=1.0,
                sigma=3.7039,
                epsilon_k=150.03,
                charge=0.0,
                epsilon_k_ab=0.0,
                kappa_ab=0.0,
                association_scheme=None,
                relative_permittivity=1.0,
                born_diameter=0.0,
                solvation_factor=1.0,
            ),
            PureRecord(
                component="Ethane",
                molar_mass=30.070e-3,
                m=1.6069,
                sigma=3.5206,
                epsilon_k=191.42,
                charge=0.0,
                epsilon_k_ab=0.0,
                kappa_ab=0.0,
                association_scheme=None,
                relative_permittivity=1.0,
                born_diameter=0.0,
                solvation_factor=1.0,
            ),
        ],
        [],
        interaction_policies=[
            StructuralZeroPolicy(
                family,
                ("Methane", "Ethane"),
                reason,
                InteractionProvenance("model_structural_zero", source),
            )
            for family, reason, source in (
                (
                    "k_ij",
                    "The test selects the uncorrected Berthelot pair-dispersion rule.",
                    "Berthelot dispersion rule / EqID epsilon_mixing",
                ),
                (
                    "l_ij",
                    "The test selects the uncorrected Lorentz pair-diameter rule.",
                    "Lorentz diameter rule / EqID sigma_mixing",
                ),
                (
                    "k_hb_ij",
                    "The nonassociating pair has no active association topology.",
                    "inactive association topology / EqID kappa_assoc_mixing",
                ),
            )
        ],
        metadata={
            "source": "Gross and Sadowski (2001), Table 2",
            "table": "pure parameters; binary zero is an explicit selector-contract convention",
            "auxiliary_neutral_fields": "equation_structural_neutral_inactive",
            "source_backed": True,
        },
    )
    mix = Mixture(parameters).native

    payload = _core._native_equilibrium_selector_contract(
        mix._native,
        {
            "route": "bubble_pressure",
            "temperature": 300.0,
            "composition": [0.35, 0.65],
            "composition_role": "liquid",
        },
    )

    readiness = payload["parameter_readiness"]
    assert readiness["binary_interaction_matrix_present"] is True
    assert readiness["binary_interaction_provenance_status"] == "complete_interaction_graph"
    assert readiness["parameter_provenance_status"] == "source_backed_parameter_metadata"
    assert readiness["source_backed_parameter_provenance_present"] is True
    assert readiness["explicit_zero_binary_interaction_convention"] is True
    assert readiness["parameter_provenance_fields"] == ["source", "table"]
    assert readiness["required_parameter_families_present"] is True


def test_neutral_lle_sampled_candidate_audit_reports_replayable_candidate_set() -> None:
    mix = _nonideal_lle_binary_mixture()

    discovery = _core._native_neutral_tpd_phase_discovery(
        mix._native,
        225.0,
        1.0e6,
        [0.5, 0.5],
        [0, 0],
        1.0e-6,
        1.0e-6,
    )

    assert discovery["phase_discovery_backend"] == "continuous_tpd_sampled_candidate_audit"
    assert discovery["stage9_phase_discovery_steps"] == [
        "deterministic_screening",
        "continuous_tpd_minimization",
        "held_stage_i_stability",
        "held_stage_ii_candidate_bound_audit",
        "sampled_candidate_bound_audit",
        "held_stage_iii_ipopt_refinement",
    ]
    assert discovery["held_stage_ii_candidate_bound_audit_status"] == "candidate_bound_gap_closed"
    assert discovery["held_stage_ii_status"] == "sampled_candidate_audit_complete"
    assert discovery["held_stage_ii_dual_loop_status"] == "not_performed"
    assert discovery["held_stage_ii_stopping_reason"] == "sampled_candidate_bound_gap_closed"
    assert discovery["held_stage_ii_bound_tolerance"] == pytest.approx(1.0e-6)
    assert discovery["held_stage_ii_lower_bound_history"]
    assert discovery["held_stage_ii_upper_bound_history"]
    assert discovery["held_stage_ii_bound_gap_history"]
    assert len(discovery["held_stage_ii_lower_bound_history"]) == discovery["held_stage_ii_major_iterations"]
    assert len(discovery["held_stage_ii_upper_bound_history"]) == discovery["held_stage_ii_major_iterations"]
    assert len(discovery["held_stage_ii_bound_gap_history"]) == discovery["held_stage_ii_major_iterations"]
    assert discovery["held_stage_ii_lower_bound_history"][-1] == pytest.approx(
        discovery["held_stage_ii_lower_bound"]
    )
    assert discovery["held_stage_ii_upper_bound_history"][-1] == pytest.approx(
        discovery["held_stage_ii_upper_bound"]
    )
    assert discovery["held_stage_ii_bound_gap_history"][-1] == pytest.approx(
        discovery["held_stage_ii_bound_gap"]
    )
    assert discovery["held_stage_ii_replay_ready"] is True
    assert discovery["held_stage_ii_replay_source"] == "sampled_candidate_audit_selected_candidates"
    assert discovery["held_stage_ii_replay_seed_name"] == "sampled_candidate_pair_replay"
    assert discovery["held_stage_ii_replay_phase_kinds"] == discovery["selected_phase_kinds"]
    assert discovery["held_stage_ii_replay_phase_fractions"] == pytest.approx(
        discovery["selected_phase_fractions"]
    )
    np.testing.assert_allclose(
        np.asarray(discovery["held_stage_ii_replay_phase_compositions"], dtype=float),
        np.asarray(discovery["selected_phase_compositions"], dtype=float),
    )

    candidates = [dict(candidate) for candidate in discovery["candidates"]]
    rejected = [candidate for candidate in candidates if not candidate["selected"]]
    assert candidates
    assert rejected
    assert discovery["held_stage_ii_replay_candidate_count"] == len(candidates)
    assert discovery["held_stage_ii_rejected_candidate_count"] == len(rejected)
    assert len(discovery["held_stage_ii_rejected_candidate_ranks"]) == len(rejected)
    assert len(discovery["held_stage_ii_rejected_candidate_reasons"]) == len(rejected)
    assert set(discovery["held_stage_ii_rejected_candidate_reasons"]) == {
        "not_selected_by_sampled_candidate_mass_balance_gate"
    }


def test_closed_neutral_tp_flash_cannot_bypass_selector_with_activation_plan() -> None:
    mix = _neutral_binary_mixture()
    request = {
        "route": "neutral_tp_flash",
        "temperature": 300.0,
        "pressure": 1.0e6,
        "composition": [0.35, 0.65],
        "composition_role": "feed",
    }

    with pytest.raises(_provider_core.NativeValueError, match="not production exposed"):
        _core._native_equilibrium_selector_contract(mix._native, request)
    with pytest.raises(_provider_core.NativeValueError, match="not production exposed"):
        _core._native_equilibrium_activation_plan_contract(mix._native, request)


def test_closed_neutral_lle_cannot_bypass_selector_with_activation_plan() -> None:
    mix = _nonideal_lle_binary_mixture()
    request = {
        "route": "neutral_lle",
        "temperature": 300.0,
        "pressure": 1.0e6,
        "composition": [0.5, 0.5],
        "composition_role": "feed",
    }

    with pytest.raises(_provider_core.NativeValueError, match="not production exposed"):
        _core._native_equilibrium_selector_contract(mix._native, request)
    with pytest.raises(_provider_core.NativeValueError, match="not production exposed"):
        _core._native_equilibrium_activation_plan_contract(mix._native, request)


@pytest.mark.parametrize(
    ("route", "composition_role"),
    [
        ("bubble_pressure", "liquid"),
        ("bubble_temperature", "liquid"),
        ("dew_pressure", "vapor"),
        ("dew_temperature", "vapor"),
        ("electrolyte_lle", "feed"),
        ("reactive_speciation", "feed"),
        ("reactive_lle", "feed"),
        ("reactive_electrolyte_lle", "feed"),
    ],
)
def test_activation_plan_builder_rejects_non_activation_routes(route: str, composition_role: str) -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(_provider_core.NativeValueError, match="activation-plan-ineligible"):
        _core._native_equilibrium_activation_plan_contract(
            mix._native,
            {
                "route": route,
                "temperature": 300.0,
                "pressure": 1.0e6,
                "composition": [0.35, 0.65],
                "composition_role": composition_role,
            },
        )


def test_closed_neutral_tp_flash_cannot_reach_activated_nlp_contract() -> None:
    mix = _neutral_binary_mixture()
    request = {
        "route": "neutral_tp_flash",
        "temperature": 300.0,
        "pressure": 1.0e6,
        "composition": [0.35, 0.65],
        "composition_role": "feed",
    }

    with pytest.raises(_provider_core.NativeValueError, match="not production exposed"):
        _core._native_activated_neutral_tp_flash_nlp_contract(mix._native, request)


def test_selector_core_rejects_incompatible_composition_role_before_solver_dispatch() -> None:
    mix = _neutral_binary_mixture()

    with pytest.raises(_provider_core.NativeValueError, match="composition_role"):
        _core._native_equilibrium_selector_contract(
            mix._native,
            {
                "route": "bubble_pressure",
                "temperature": 300.0,
                "composition": [0.35, 0.65],
                "composition_role": "vapor",
            },
        )
