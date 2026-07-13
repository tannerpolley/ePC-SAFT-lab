from __future__ import annotations

import json
import re
from pathlib import Path

import epcsaft_equilibrium
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
PRESERVATION_MANIFEST = (
    REPO_ROOT
    / "docs/superpowers/milestones/M4-equilibrium/equilibrium-preservation-manifest.yaml"
)
BINDING_SOURCE = (
    REPO_ROOT
    / "packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp"
)
CAPABILITY_BASELINE = Path(__file__).with_name("fixtures") / (
    "stage4_activation_capability_baseline.json"
)

X_RHO = ["mole_fraction", "molar_density"]
T_X_RHO = ["temperature_K", "mole_fraction", "molar_density"]
RHO_P = ["molar_density", "pressure_Pa"]
SELECTOR_SOLVE_VARYING = {
    "bubble_pressure": ["mole_fraction", "molar_density", "pressure_Pa"],
    "dew_pressure": ["mole_fraction", "molar_density", "pressure_Pa"],
    "bubble_temperature": T_X_RHO,
    "dew_temperature": T_X_RHO,
    "neutral_tp_flash": X_RHO,
    "neutral_lle": X_RHO,
    "single_component_vle": RHO_P,
}


def _entry(
    binding: str,
    disposition: str,
    varying: list[str] | dict[str, list[str]],
    owners: list[str],
    proofs: list[str],
) -> dict[str, object]:
    varying_field = (
        "solve_varying_independent_variables_by_route"
        if isinstance(varying, dict)
        else "solve_varying_independent_variables"
    )
    return {
        "binding": binding,
        "disposition": disposition,
        varying_field: varying,
        "preservation_item_ids": owners,
        "focused_proof_paths": proofs,
        "trial_phase_composition_invariant_required": (
            isinstance(varying, dict)
            or "mole_fraction" in varying
        ),
    }


EXPECTED_STAGE_4_DISPOSITIONS = [
    _entry(
        "_native_equilibrium_activation_plan_contract",
        "migrate_public_handle",
        X_RHO,
        ["activation_selector_core", "local_nlp_ipopt_adapter"],
        [
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_internal_multiphase_activation_contracts.py"
        ],
    ),
    _entry(
        "_native_equilibrium_selector_contract",
        "migrate_public_handle",
        SELECTOR_SOLVE_VARYING,
        ["activation_selector_core"],
        [
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_selector_core_contracts.py"
        ],
    ),
    _entry(
        "_native_equilibrium_selector_route_result",
        "migrate_public_handle",
        SELECTOR_SOLVE_VARYING,
        [
            "activation_selector_core",
            "public_pressure_boundary_routes",
            "public_single_component_saturation",
        ],
        [
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
            "packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py",
        ],
    ),
    _entry(
        "_native_activated_neutral_tp_flash_nlp_contract",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["local_nlp_ipopt_adapter", "exact_phase_derivative_assembly"],
        [
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_selector_core_contracts.py"
        ],
    ),
    _entry(
        "_native_equilibrium_cloud_shadow_route_result",
        "migrate_const_handle_preserve_concept",
        T_X_RHO,
        ["local_nlp_ipopt_adapter", "neutral_phase_discovery"],
        ["tests/native/contracts/test_cloud_shadow_route_admission_checker.py"],
    ),
    _entry(
        "_native_eos_phase_system",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["exact_phase_derivative_assembly"],
        ["packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py"],
    ),
    _entry(
        "_native_phase_equilibrium_residual_block_contract",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["exact_phase_derivative_assembly"],
        [
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_phase_equilibrium_residual_block_contract.py"
        ],
    ),
    _entry(
        "_native_neutral_two_phase_eos_nlp_contract",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["local_nlp_ipopt_adapter", "exact_phase_derivative_assembly"],
        [
            "packages/epcsaft-equilibrium/tests/contracts/"
            "test_provider_resolved_input_integration.py",
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_selector_core_contracts.py",
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_phase_equilibrium_residual_block_contract.py",
        ],
    ),
    _entry(
        "_native_neutral_multiphase_eos_nlp_contract",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["local_nlp_ipopt_adapter", "exact_phase_derivative_assembly"],
        [
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_internal_multiphase_activation_contracts.py"
        ],
    ),
    _entry(
        "_native_neutral_two_phase_eos_postsolve",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["native_postsolve_certification"],
        ["packages/epcsaft-equilibrium/tests/native/results/test_result_builder.py"],
    ),
    _entry(
        "_native_neutral_multiphase_eos_postsolve",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["native_postsolve_certification"],
        [
            "packages/epcsaft-equilibrium/tests/contracts/"
            "test_provider_resolved_input_integration.py"
        ],
    ),
    _entry(
        "_native_neutral_multiphase_fugacity_residual_route_result",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["neutral_phase_discovery", "local_nlp_ipopt_adapter"],
        [
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_internal_multiphase_activation_contracts.py",
            "scripts/validation/check_generalized_phase_set.py",
        ],
    ),
    _entry(
        "_native_neutral_tpd_phase_discovery",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["neutral_phase_discovery"],
        [
            "packages/epcsaft-equilibrium/tests/native/results/"
            "test_neutral_lle_reference_values.py",
            "scripts/validation/check_generalized_phase_set.py",
        ],
    ),
    _entry(
        "_native_associating_single_component_vle_validation_result",
        "migrate_const_handle_preserve_concept",
        RHO_P,
        ["association_components", "local_nlp_ipopt_adapter"],
        ["tests/native/contracts/test_gross_2002_figure01_internal_saturation.py"],
    ),
    _entry(
        "_native_eos_phase_block",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["exact_phase_derivative_assembly"],
        ["packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py"],
    ),
    _entry(
        "_native_saturation_block",
        "migrate_const_handle_preserve_concept",
        RHO_P,
        ["public_single_component_saturation", "exact_phase_derivative_assembly"],
        [
            "packages/epcsaft-equilibrium/tests/native/blocks/"
            "test_single_component_vle_block.py"
        ],
    ),
    _entry(
        "_native_electrolyte_contribution_block",
        "migrate_const_handle_preserve_concept",
        [],
        ["electrolyte_counterion_pair_components"],
        ["packages/epcsaft-equilibrium/tests/native/blocks/test_eos_phase_block.py"],
    ),
    _entry(
        "_native_chemical_equilibrium_nlp_activation:eos_activity",
        "optional_eos_activity_handle_or_reject",
        X_RHO,
        ["standalone_chemical_equilibrium_components", "failed_nonideal_mea_ce_output"],
        [
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_chemical_equilibrium_eos_activity.py",
            "tests/native/contracts/test_standalone_ce_gate.py",
        ],
    ),
    _entry(
        "_native_electrolyte_bubble_t_reduced_nlp_probe",
        "migrate_const_handle_preserve_concept",
        T_X_RHO,
        ["electrolyte_counterion_pair_components", "exact_phase_derivative_assembly"],
        [
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_electrolyte_held2_flash_validation.py"
        ],
    ),
    _entry(
        "_native_electrolyte_bubble_t_route_result",
        "migrate_const_handle_preserve_concept",
        T_X_RHO,
        ["electrolyte_counterion_pair_components", "local_nlp_ipopt_adapter"],
        [
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_electrolyte_held2_flash_validation.py"
        ],
    ),
    _entry(
        "_native_electrolyte_tpd_phase_discovery",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["electrolyte_counterion_pair_components"],
        ["tests/native/contracts/test_electrolyte_tpd_gate.py"],
    ),
    _entry(
        "_native_electrolyte_held2_continuous_tpd_minimizer",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["electrolyte_counterion_pair_components"],
        [
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_electrolyte_held2_continuous_tpd.py"
        ],
    ),
    _entry(
        "_native_electrolyte_held2_phase_discovery",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["electrolyte_counterion_pair_components"],
        ["tests/native/contracts/test_electrolyte_held2_phase_discovery.py"],
    ),
    _entry(
        "_native_electrolyte_stage_iii_refinement",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["electrolyte_counterion_pair_components", "local_nlp_ipopt_adapter"],
        ["tests/native/contracts/test_electrolyte_stage_iii_refinement.py"],
    ),
    _entry(
        "_native_electrolyte_postsolve_certification",
        "migrate_const_handle_preserve_concept",
        X_RHO,
        ["native_postsolve_certification", "electrolyte_counterion_pair_components"],
        ["tests/native/contracts/test_electrolyte_postsolve_certification.py"],
    ),
]

EXPECTED_STAGE_4_BINDINGS = {
    str(row["binding"]) for row in EXPECTED_STAGE_4_DISPOSITIONS
}


def _live_payload_consuming_bindings() -> set[str]:
    source = BINDING_SOURCE.read_text(encoding="utf-8")
    matches = list(re.finditer(r'm\.def\(\s*"([^"]+)"', source))
    bindings = {
        match.group(1)
        for index, match in enumerate(matches)
        if "native_args_from_mixture_object("
        in source[match.start() : matches[index + 1].start() if index + 1 < len(matches) else None]
    }
    chemical_helper = source[
        source.index("ChemicalEquilibriumNlpInput chemical_equilibrium_input_from_payloads") :
        source.index("FeasibleInitializationInput feasible_initialization_input_from_payload")
    ]
    if "native_args_from_mixture_object(" in chemical_helper:
        bindings.add("_native_chemical_equilibrium_nlp_activation:eos_activity")
    return bindings


def test_stage4_disposition_matrix_matches_manifest_and_all_live_payload_consumers() -> None:
    payload = yaml.safe_load(PRESERVATION_MANIFEST.read_text(encoding="utf-8"))
    rows = payload["checkpoint"]["stage_4_provider_input_binding_dispositions"]

    assert rows == EXPECTED_STAGE_4_DISPOSITIONS
    assert {str(row["binding"]) for row in rows} == EXPECTED_STAGE_4_BINDINGS
    assert _live_payload_consuming_bindings() == EXPECTED_STAGE_4_BINDINGS
    assert len(rows) == 25

    for row in rows:
        varying = row.get("solve_varying_independent_variables")
        varying_by_route = row.get("solve_varying_independent_variables_by_route")
        assert (varying is None) is not (varying_by_route is None)
        if varying_by_route is not None:
            assert varying_by_route == SELECTOR_SOLVE_VARYING
        elif "mole_fraction" in varying:
            assert row["trial_phase_composition_invariant_required"] is True


def test_stage4_equilibrium_activation_and_capability_baseline_is_exact() -> None:
    baseline = json.loads(CAPABILITY_BASELINE.read_text(encoding="utf-8"))

    current = json.loads(json.dumps(epcsaft_equilibrium.capabilities(), sort_keys=True))
    assert current == baseline
