from __future__ import annotations

import pytest
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()
import epcsaft_equilibrium
from epcsaft_equilibrium.workflows import _EQUILIBRIUM_ROUTE_SPECS

EXPECTED_PUBLIC_ROUTE_FAMILIES = {
    "bubble_pressure": "bubble_dew_derived_routes",
    "bubble_temperature": "bubble_dew_derived_routes",
    "dew_pressure": "bubble_dew_derived_routes",
    "dew_temperature": "bubble_dew_derived_routes",
    "electrolyte_lle": "electrolyte_lle",
    "flash": "neutral_tp_flash",
    "lle": "neutral_lle",
    "multiphase": "neutral_multiphase_nonassoc",
    "single_component_vle": "single_component_vle",
}


def _admitted_public_route_map(rows: list[dict[str, object]]) -> dict[str, str]:
    route_map: dict[str, str] = {}
    for row in rows:
        family_key = str(row["key"])
        if not bool(row["production_exposed"]):
            assert row["public_routes"] == []
            continue
        for route in row["public_routes"]:
            assert str(route) not in route_map
            route_map[str(route)] = family_key
    return route_map


def test_generated_activation_mirror_matches_native_source_of_truth() -> None:
    try:
        from epcsaft_equilibrium.equilibrium_activation import EQUILIBRIUM_ACTIVATION_MATRIX
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing generated activation mirror: {exc}")

    native_rows = list(_core._native_equilibrium_activation_matrix())

    assert EQUILIBRIUM_ACTIVATION_MATRIX == native_rows


def test_runtime_equilibrium_capabilities_are_activation_matrix_driven() -> None:
    native_rows = list(_core._native_equilibrium_activation_matrix())
    capabilities = epcsaft_equilibrium.capabilities()
    activation = capabilities["activation_matrix"]
    public_route_map = _admitted_public_route_map(native_rows)

    assert activation["source"] == "native_cpp"
    assert activation["rows"] == native_rows
    assert activation["production_families"] == [
        "neutral_tp_flash",
        "neutral_lle",
        "single_component_vle",
        "neutral_multiphase_nonassoc",
        "electrolyte_lle",
        "bubble_dew_derived_routes",
    ]
    assert activation["declared_not_exposed_families"] == [
        "reactive_speciation",
        "reactive_lle",
        "reactive_electrolyte_lle",
    ]
    assert capabilities["production_families"] == [
        "neutral_tp_flash",
        "neutral_lle",
        "single_component_vle",
        "neutral_multiphase_nonassoc",
        "electrolyte_lle",
        "bubble_dew_derived_routes",
    ]
    assert public_route_map == EXPECTED_PUBLIC_ROUTE_FAMILIES
    assert capabilities["public_routes"] == sorted(EXPECTED_PUBLIC_ROUTE_FAMILIES)
    assert activation["public_routes"] == [
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
        "electrolyte_lle",
        "flash",
        "lle",
        "multiphase",
        "single_component_vle",
    ]
    assert activation["public_route_family_map"] == EXPECTED_PUBLIC_ROUTE_FAMILIES
    assert activation["public_routes_by_family"] == {
        "neutral_tp_flash": ["flash"],
        "neutral_lle": ["lle"],
        "single_component_vle": ["single_component_vle"],
        "neutral_multiphase_nonassoc": ["multiphase"],
        "electrolyte_lle": ["electrolyte_lle"],
        "bubble_dew_derived_routes": [
            "bubble_pressure",
            "bubble_temperature",
            "dew_pressure",
            "dew_temperature",
        ],
    }
    assert {
        route: spec.selector_family for route, spec in _EQUILIBRIUM_ROUTE_SPECS.items()
    } == EXPECTED_PUBLIC_ROUTE_FAMILIES
    assert capabilities["bubble_dew_derived_routes"]["entrypoint"] == ("Equilibrium(mixture, route=..., ...).solve()")
    assert capabilities["bubble_dew_derived_routes"]["public_routes"] == [
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
    ]
    assert (
        capabilities["bubble_dew_derived_routes"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    )
    assert (
        capabilities["neutral_tp_flash"]["entrypoint"]
        == "Equilibrium(mixture, route='flash', T=..., P=..., z=...).solve()"
    )
    assert capabilities["neutral_tp_flash"]["public_routes"] == ["flash"]
    assert capabilities["neutral_tp_flash"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    assert capabilities["neutral_lle"]["entrypoint"] == "Equilibrium(mixture, route='lle', T=..., P=..., z=...).solve()"
    assert capabilities["neutral_lle"]["public_routes"] == ["lle"]
    assert capabilities["neutral_lle"]["input_scope"] == (
        "neutral non-reactive non-electrolyte liquid/liquid mixtures: non-associating mixtures plus "
        "the source-backed Gross/Sadowski 2002 methanol/cyclohexane and water/1-pentanol associating proof fixtures"
    )
    assert capabilities["neutral_lle"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    assert (
        capabilities["neutral_multiphase_nonassoc"]["entrypoint"]
        == "Equilibrium(mixture, route='multiphase', T=..., P=..., z=..., phase_kinds=[...]).solve()"
    )
    assert capabilities["neutral_multiphase_nonassoc"]["public_routes"] == ["multiphase"]
    assert (
        capabilities["neutral_multiphase_nonassoc"]["input_scope"]
        == "neutral non-reactive non-electrolyte non-associating explicit phase-kind sets"
    )
    assert capabilities["neutral_multiphase_nonassoc"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    assert (
        capabilities["single_component_vle"]["entrypoint"]
        == "Equilibrium(mixture, route='single_component_vle', T=...).solve()"
    )
    assert capabilities["single_component_vle"]["public_routes"] == ["single_component_vle"]
    assert (
        capabilities["single_component_vle"]["input_scope"]
        == "single neutral non-reactive non-electrolyte component, including pure 2B associating components for the retained Gross/Sadowski 2002 Figure 1 saturation proof"
    )
    assert capabilities["single_component_vle"]["available"] is capabilities["activation_matrix"]["ipopt_available"]
    assert capabilities["problem_objects"]["available"] is True
    assert capabilities["problem_objects"]["entrypoint"] == "Equilibrium(mixture, route=..., ...)"
    assert capabilities["standalone_reactive_speciation"] == {
        "available": capabilities["activation_matrix"]["ipopt_available"],
        "production": False,
        "entrypoint": "reactive_speciation(species=..., reactions=..., feed_amounts=..., equilibrium_constants=...)",
        "route": "reactive_speciation",
        "native_binding": "_native_chemical_equilibrium_nlp_activation",
        "capability_scope": "standalone_ce_only",
        "phase_scope": "homogeneous",
        "coupling_scope": "chemical_equilibrium_only",
        "public_routes": [],
        "closed_surfaces": ["reactive_lle", "reactive_electrolyte_lle", "cpe"],
        "activation_gate": "issue_0330",
        "requires": ["cppad", "ipopt"],
        "result_fields": [
            "species_amounts",
            "activities",
            "reduced_chemical_potentials",
            "reaction_extents",
            "balances",
            "affinities",
            "standard_state_metadata",
            "diagnostics",
        ],
    }
    assert {row["quantity"] for row in capabilities["route_derivative_evidence"]["rows"]} == {
        "bubble_dew_derived_routes",
        "neutral_tp_flash",
        "neutral_lle",
        "associating_neutral_lle_gross_2002_public_exact_hessian",
        "associating_neutral_lle_gross_2002_figure_10_public_exact_hessian",
        "associating_neutral_vle_gross_2002_figure_10_public_exact_hessian",
        "neutral_multiphase_nonassoc",
        "single_component_vle",
        "electrolyte_held2_readiness_born_ssm_ds_exactness",
        "electrolyte_held2_counterion_pair_phase_discovery",
        "electrolyte_held2_stage_iii_reduced_variable_refinement",
        "electrolyte_held2_postsolve_phase_set_certification",
        "electrolyte_lle_khudaida_public_admission",
    }
    associating_proof = next(
        row
        for row in capabilities["route_derivative_evidence"]["rows"]
        if row["quantity"] == "associating_neutral_lle_gross_2002_public_exact_hessian"
    )
    assert associating_proof["classification"] == "production_supported"
    assert associating_proof["backend"] == "cppad_implicit_association"
    assert associating_proof["public_admission_state"] == "public_route_open"
    assert associating_proof["public_route"] == "lle"
    assert associating_proof["selector_family"] == "neutral_lle"
    assert associating_proof["source_configuration"] == "Gross2002 Figure8 methanol-cyclohexane"
    assert associating_proof["component_pair"] == ["methanol", "cyclohexane"]
    assert associating_proof["assoc_scheme"] == "2B"
    assert associating_proof["k_ij"] == pytest.approx(0.051)
    assert (
        associating_proof["source_fixture"]
        == "data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane"
    )
    figure10_lle_proof = next(
        row
        for row in capabilities["route_derivative_evidence"]["rows"]
        if row["quantity"] == "associating_neutral_lle_gross_2002_figure_10_public_exact_hessian"
    )
    assert figure10_lle_proof["public_route"] == "lle"
    assert figure10_lle_proof["source_configuration"] == "Gross2002 Figure10 water-1-pentanol"
    assert figure10_lle_proof["component_pair"] == ["water", "1-pentanol"]
    assert figure10_lle_proof["k_ij"] == pytest.approx(0.016)
    figure10_vle_proof = next(
        row
        for row in capabilities["route_derivative_evidence"]["rows"]
        if row["quantity"] == "associating_neutral_vle_gross_2002_figure_10_public_exact_hessian"
    )
    assert figure10_vle_proof["public_route"] == "bubble_pressure/dew_pressure"
    assert figure10_vle_proof["source_configuration"] == "Gross2002 Figure10 water-1-pentanol"
    assert figure10_vle_proof["component_pair"] == ["water", "1-pentanol"]
    assert figure10_vle_proof["k_ij"] == pytest.approx(0.016)
    electrolyte_readiness = next(
        row
        for row in capabilities["route_derivative_evidence"]["rows"]
        if row["quantity"] == "electrolyte_held2_readiness_born_ssm_ds_exactness"
    )
    assert electrolyte_readiness["classification"] == "prerequisite_evidence"
    assert electrolyte_readiness["backend"] == "cppad_born_ssm_ds"
    assert electrolyte_readiness["public_admission_state"] == "prerequisite_evidence_only"
    assert electrolyte_readiness["selector_family"] == "electrolyte_lle"
    assert electrolyte_readiness["source_configuration"] == "Khudaida 2026 electrolyte LLE readiness"
    assert electrolyte_readiness["component_set"] == ["water", "ethanol", "isobutanol", "NaCl"]
    assert electrolyte_readiness["reduced_basis"] == "charge_neutral_NaCl_amount_lift"
    assert (
        electrolyte_readiness["source_fixture"]
        == "data/reference/equilibrium_benchmarks/electrolyte_lle/water_ethanol_isobutanol_nacl"
    )
    electrolyte_discovery = next(
        row
        for row in capabilities["route_derivative_evidence"]["rows"]
        if row["quantity"] == "electrolyte_held2_counterion_pair_phase_discovery"
    )
    assert electrolyte_discovery["classification"] == "phase_discovery_evidence"
    assert electrolyte_discovery["backend"] == "native_counterion_pair_phase_discovery"
    assert electrolyte_discovery["public_admission_state"] == "prerequisite_evidence_only"
    assert electrolyte_discovery["selector_family"] == "electrolyte_lle"
    assert electrolyte_discovery["reduced_basis"] == "independent_counterion_pair_matrix"
    assert electrolyte_discovery["stage_status"] == "phase_discovery_complete_stage_iii_pending"
    assert "Ascani 2022 mixed-electrolyte counterion fixtures" in electrolyte_discovery["source_configuration"]
    electrolyte_stage_iii = next(
        row
        for row in capabilities["route_derivative_evidence"]["rows"]
        if row["quantity"] == "electrolyte_held2_stage_iii_reduced_variable_refinement"
    )
    assert electrolyte_stage_iii["classification"] == "stage_iii_refinement_evidence"
    assert electrolyte_stage_iii["backend"] == "native_electrolyte_stage_iii_refinement"
    assert electrolyte_stage_iii["public_admission_state"] == "prerequisite_evidence_only"
    assert electrolyte_stage_iii["selector_family"] == "electrolyte_lle"
    assert electrolyte_stage_iii["reduced_basis"] == "independent_counterion_pair_matrix"
    assert electrolyte_stage_iii["stage_status"] == "stage_iii_refinement_complete_postsolve_pending"
    assert electrolyte_stage_iii["route_hessian_mode"] == "limited_memory_charged_born_route"
    electrolyte_postsolve = next(
        row
        for row in capabilities["route_derivative_evidence"]["rows"]
        if row["quantity"] == "electrolyte_held2_postsolve_phase_set_certification"
    )
    assert electrolyte_postsolve["classification"] == "postsolve_certification_evidence"
    assert electrolyte_postsolve["backend"] == "native_electrolyte_postsolve_certification"
    assert electrolyte_postsolve["public_admission_state"] == "prerequisite_evidence_only"
    assert electrolyte_postsolve["selector_family"] == "electrolyte_lle"
    assert electrolyte_postsolve["reduced_basis"] == "independent_counterion_pair_matrix"
    assert electrolyte_postsolve["stage_status"] == "postsolve_certified_public_admission_pending"
    assert electrolyte_postsolve["route_hessian_mode"] == "limited_memory_charged_born_route"
    electrolyte_public = next(
        row
        for row in capabilities["route_derivative_evidence"]["rows"]
        if row["quantity"] == "electrolyte_lle_khudaida_public_admission"
    )
    assert electrolyte_public["classification"] == "production_supported"
    assert electrolyte_public["backend"] == "native_electrolyte_postsolve_certification"
    assert electrolyte_public["public_admission_state"] == "public_route_open"
    assert electrolyte_public["public_route"] == "electrolyte_lle"
    assert electrolyte_public["selector_family"] == "electrolyte_lle"
    assert electrolyte_public["source_configuration"] == "Khudaida 2026 NaCl mixed-solvent electrolyte LLE"
    assert electrolyte_public["native_component_set"] == ["H2O", "Ethanol", "Butanol", "Na+", "Cl-"]
    assert electrolyte_public["stage_status"] == "public_admission_complete"
    assert "electrolyte_lle" in activation["public_routes"]
    assert "electrolyte_lle" in activation["production_families"]
    electrolyte_activation = next(
        row for row in capabilities["activation_matrix"]["rows"] if row["key"] == "electrolyte_lle"
    )
    assert electrolyte_activation["production_exposed"] is True
    assert electrolyte_activation["public_routes"] == ["electrolyte_lle"]
    assert electrolyte_activation["proof_routes"] == ["electrolyte_held2_public_route_admission"]
    assert activation["public_route_family_map"]["lle"] == "neutral_lle"
    assert activation["public_route_family_map"]["electrolyte_lle"] == "electrolyte_lle"

    deleted_route_keys = {
        "neutral_lle_flash",
        "neutral_stability",
        "electrolyte_bubble_pressure",
        "electrolyte_stability",
        "reactive_speciation",
        "reactive_stability",
    }
    assert deleted_route_keys.isdisjoint(capabilities)
    assert set(capabilities["standalone_reactive_speciation"]["closed_surfaces"]).isdisjoint(
        capabilities["public_routes"]
    )
