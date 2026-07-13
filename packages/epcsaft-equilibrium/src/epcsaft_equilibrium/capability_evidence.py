"""Evidence registry for production equilibrium selector capabilities.

The registry is pure data. Native activation decides which selector routes are
open; this module decides whether the retained proof for each open family is
complete enough to support a production capability claim.
"""

from __future__ import annotations

import shlex
from collections.abc import Collection, Mapping, Sequence
from pathlib import Path
from typing import Final

_OWNER = "epcsaft-equilibrium / M4"

_GROSS_FULL_CHECKER = (
    "uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py "
    "--json --require-complete --require-exact-association-hessian --require-fresh-native"
)
_GROSS_ASSOCIATION_CHECKER = (
    "uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py "
    "--json --require-complete --require-exact-association-hessian --require-fresh-native"
)
_SINGLE_COMPONENT_CHECKER = (
    "uv run --no-sync python scripts/validation/check_single_component_vle_nist_saturation.py "
    "--json --require-complete --require-fresh-native"
)

_GROSS_FULL_CHECKER_NODE = (
    "tests/native/contracts/test_gross_2002_full_replication_checker.py::"
    "test_cli_require_complete_accepts_committed_manifest"
)

PROOF_EVIDENCE_BY_ID: Final[dict[str, dict[str, object]]] = {
    "associating_neutral_vle_gross_2002_bubble_pressure_figures_2_9_public_exact_hessian": {
        "admission": "production_complete",
        "proof_nodes": (
            _GROSS_FULL_CHECKER_NODE,
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::"
            "test_equilibrium_vle_admits_source_backed_gross_2002_associating_binary"
            "[_gross_2002_figure2_associating_vle_parameter_set-bubble_pressure-kwargs0-neutral_bubble_p]",
        ),
        "strict_checkers": (_GROSS_FULL_CHECKER,),
        "data_sources": (
            "Gross/Sadowski 2002 Figures 2-9 retained source bundle",
            "analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json",
        ),
        "artifact_paths": (
            "analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json",
            "analyses/paper_validation/2002_gross/figures/figure_02/results/model_curve.csv",
            "analyses/paper_validation/2002_gross/figures/figure_02/results/plotted_data.csv",
            "analyses/paper_validation/2002_gross/figures/figure_02/results/figure_02.png",
        ),
        "acceptance_metrics": {
            "normalized_plot_score_min": 8.0,
            "branch_coverage_score_min": 1.0,
            "derivative_status": "verified_exact",
            "route_status": "accepted",
            "postsolve_accepted": True,
        },
    },
    "associating_neutral_vle_gross_2002_dew_pressure_figures_2_9_public_exact_hessian": {
        "admission": "production_complete",
        "proof_nodes": (
            _GROSS_FULL_CHECKER_NODE,
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::"
            "test_equilibrium_vle_admits_source_backed_gross_2002_associating_binary"
            "[_gross_2002_figure2_associating_vle_parameter_set-dew_pressure-kwargs1-neutral_dew_p]",
        ),
        "strict_checkers": (_GROSS_FULL_CHECKER,),
        "data_sources": (
            "Gross/Sadowski 2002 Figures 2-9 retained source bundle",
            "analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json",
        ),
        "artifact_paths": (
            "analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json",
            "analyses/paper_validation/2002_gross/figures/figure_02/results/model_curve.csv",
            "analyses/paper_validation/2002_gross/figures/figure_02/results/plotted_data.csv",
            "analyses/paper_validation/2002_gross/figures/figure_02/results/figure_02.png",
        ),
        "acceptance_metrics": {
            "normalized_plot_score_min": 8.0,
            "branch_coverage_score_min": 1.0,
            "derivative_status": "verified_exact",
            "route_status": "accepted",
            "postsolve_accepted": True,
        },
    },
    "neutral_lle_matsuda_2011_nist_sampled_candidate_diagnostic": {
        "admission": "internal_validation",
        "proof_nodes": (
            "packages/epcsaft-equilibrium/tests/native/results/"
            "test_neutral_lle_reference_values.py::"
            "test_neutral_tpd_phase_discovery_reports_candidate_set_for_lle_binary",
        ),
        "strict_checkers": (),
        "data_sources": (
            "Matsuda 2011 perfluorohexane/hexane LLE via retained NIST ThermoML dataset 2",
            "data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane",
        ),
        "artifact_paths": (),
        "acceptance_metrics": {
            "diagnostic_status": "internal_diagnostic_complete",
            "held_stage_ii_status": "sampled_candidate_audit_complete",
            "held_stage_ii_dual_loop_status": "not_performed",
            "phase_set_status": (
                "sampled_candidate_audit_complete_global_completeness_unproven"
            ),
            "candidate_completeness_accepted": False,
            "production_route_admitted": False,
            "global_phase_set_certified": False,
            "source_comparison_disposition": "validation_findings_only",
        },
    },
    "associating_neutral_lle_gross_2002_internal_exact_hessian": {
        "admission": "internal_validation",
        "proof_nodes": (
            "packages/epcsaft-equilibrium/tests/native/results/"
            "test_associating_lle_reference_values.py::"
            "test_internal_gross_2002_associating_lle_source_pair_is_certified",
        ),
        "strict_checkers": (_GROSS_ASSOCIATION_CHECKER,),
        "data_sources": (
            "Gross/Sadowski 2002 Figure 8 methanol/cyclohexane LLE",
            "data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane",
        ),
        "artifact_paths": (
            "analyses/paper_validation/2002_gross/figures/figure_08/results/model_curve.csv",
            "analyses/paper_validation/2002_gross/figures/figure_08/results/plotted_data.csv",
            "analyses/paper_validation/2002_gross/figures/figure_08/results/figure_08.png",
        ),
        "acceptance_metrics": {
            "normalized_plot_score_min": 7.0,
            "branch_coverage_score_min": 1.0,
            "mass_action_residual_max": 1.0e-8,
            "derivative_status": "verified_exact",
            "phase_distance_min": 0.5,
        },
    },
    "associating_neutral_lle_gross_2002_figure_10_internal_exact_hessian": {
        "admission": "internal_validation",
        "proof_nodes": (
            "packages/epcsaft-equilibrium/tests/api/test_associating_lle_gross_2002_certification.py::"
            "test_associating_lle_gross_2002_certification_retains_source_margins_and_overlay_gaps",
            _GROSS_FULL_CHECKER_NODE,
        ),
        "strict_checkers": (_GROSS_ASSOCIATION_CHECKER, _GROSS_FULL_CHECKER),
        "data_sources": (
            "Gross/Sadowski 2002 Figure 10 water/1-pentanol LLE boundary",
            "analyses/paper_validation/2002_gross/figures/figure_10/source/source_points.csv",
        ),
        "artifact_paths": (
            "analyses/paper_validation/2002_gross/figures/figure_10/results/model_curve.csv",
            "analyses/paper_validation/2002_gross/figures/figure_10/results/plotted_data.csv",
            "analyses/paper_validation/2002_gross/figures/figure_10/results/figure_10.png",
        ),
        "acceptance_metrics": {
            "normalized_plot_score_min": 7.0,
            "branch_coverage_score_min": 1.0,
            "mass_action_residual_max": 1.0e-8,
            "derivative_status": "verified_exact",
        },
    },
    "single_component_vle_hydrocarbon_nist_saturation_exact_hessian": {
        "admission": "production_complete",
        "proof_nodes": (
            "packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py::"
            "test_single_component_vle_route_returns_saturation_payload",
            "tests/native/contracts/test_single_component_vle_nist_saturation_checker.py::"
            "test_evaluate_live_rows_accepts_exact_32_point_nist_campaign",
            "tests/native/contracts/test_single_component_vle_nist_saturation_checker.py::"
            "test_run_live_validation_executes_solver_row_provider_and_records_loaded_native",
        ),
        "strict_checkers": (_SINGLE_COMPONENT_CHECKER,),
        "data_sources": (
            "NIST Chemistry WebBook saturation-pressure and saturated-liquid-density tables",
            "data/reference/pure_component/saturation_properties/methane/saturation_properties.csv",
            "data/reference/pure_component/saturation_properties/ethane/saturation_properties.csv",
            "data/reference/pure_component/saturation_properties/propane/saturation_properties.csv",
        ),
        "artifact_paths": (
            "analyses/package_validation/equilibrium_single_component_vle/figures/hydrocarbon_saturation_pressure/results/hydrocarbon_saturation_pressure.csv",
            "analyses/package_validation/equilibrium_single_component_vle/figures/hydrocarbon_saturation_pressure/results/hydrocarbon_saturation_pressure_summary.csv",
            "analyses/package_validation/equilibrium_single_component_vle/figures/hydrocarbon_saturation_pressure/results/hydrocarbon_saturation_pressure_plotted_data.csv",
            "analyses/package_validation/equilibrium_single_component_vle/figures/hydrocarbon_saturation_pressure/results/hydrocarbon_saturation_pressure.png",
        ),
        "acceptance_metrics": {
            "joined_source_row_count": 32,
            "max_pressure_absolute_relative_error_percent": 4.0,
            "max_liquid_density_absolute_relative_error_percent": 2.0,
            "max_pressure_consistency_norm": 1.0e-2,
            "max_chemical_potential_consistency_norm": 1.0e-6,
            "min_phase_distance": 1.0e-2,
            "route_status": "accepted",
            "solver_status": "success",
        },
    },
}

CAPABILITY_EVIDENCE_BY_FAMILY: Final[dict[str, dict[str, object]]] = {
    "bubble_dew_derived_routes": {
        "family": "bubble_dew_derived_routes",
        "owner": _OWNER,
        "public_entrypoint": (
            "Equilibrium(mixture, route='bubble_pressure'/'dew_pressure', "
            "T=..., x=.../y=...).solve()"
        ),
        "native_owner": (
            "packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/"
            "core/selector_core.cpp"
        ),
        "input_scope": (
            "neutral non-reactive non-electrolyte pressure-boundary VLE; associating "
            "inputs are restricted to source-backed Gross/Sadowski 2002 Figures 2-9 "
            "fixtures; temperature-boundary routes are closed"
        ),
        "proof_ids": (
            "associating_neutral_vle_gross_2002_bubble_pressure_figures_2_9_public_exact_hessian",
            "associating_neutral_vle_gross_2002_dew_pressure_figures_2_9_public_exact_hessian",
        ),
    },
    "single_component_vle": {
        "family": "single_component_vle",
        "owner": _OWNER,
        "public_entrypoint": (
            "Equilibrium(mixture, route='single_component_vle', T=...).solve()"
        ),
        "native_owner": (
            "packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/"
            "core/two_phase_eos_route.cpp"
        ),
        "input_scope": (
            "nonassociating methane, ethane, and propane within the retained NIST "
            "saturation-property ranges"
        ),
        "proof_ids": (
            "single_component_vle_hydrocarbon_nist_saturation_exact_hessian",
        ),
    },
}

DEVELOPMENT_COMPONENT_EVIDENCE: Final[tuple[dict[str, object], ...]] = (
    {
        "evidence_id": "neutral_tp_flash_hydrocarbon_workbook_component_check",
        "family": "neutral_tp_flash",
        "production_admissible": False,
        "blocking_reason": (
            "The retained hydrocarbon workbook is explicitly not a literature benchmark."
        ),
        "source_paths": (
            "data/reference/equilibrium_benchmarks/neutral_tp_flash/methane_ethane_propane",
            "analyses/package_validation/issue_0188_neutral_tp_flash",
        ),
    },
    {
        "evidence_id": "neutral_lle_sampled_candidate_validation",
        "family": "neutral_lle",
        "production_admissible": False,
        "blocking_reason": (
            "The retained Matsuda and Gross checks validate local formulations against a "
            "sampled candidate audit; they do not implement a global HELD dual loop."
        ),
        "source_paths": (
            "data/reference/equilibrium_benchmarks/neutral_lle/perfluorohexane_hexane",
            "data/reference/equilibrium_benchmarks/associating_lle/methanol_cyclohexane",
            "packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py",
        ),
    },
    {
        "evidence_id": "bubble_temperature_hydrocarbon_inverse_component_check",
        "family": "bubble_dew_derived_routes",
        "production_admissible": False,
        "blocking_reason": (
            "Only an inverse hydrocarbon-workbook point exists; no retained literature join "
            "supports the temperature-boundary route."
        ),
        "source_paths": (
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
        ),
    },
    {
        "evidence_id": "dew_temperature_hydrocarbon_inverse_component_check",
        "family": "bubble_dew_derived_routes",
        "production_admissible": False,
        "blocking_reason": (
            "Only an inverse hydrocarbon-workbook point exists; no retained literature join "
            "supports the temperature-boundary route."
        ),
        "source_paths": (
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
        ),
    },
    {
        "evidence_id": "single_component_vle_pure_2b_source_scope",
        "family": "single_component_vle",
        "production_admissible": False,
        "blocking_reason": (
            "The retained 2B scope artifact records NIST source rows and route eligibility, "
            "but it contains no model predictions joined to those rows."
        ),
        "source_paths": (
            "analyses/package_validation/equilibrium_single_component_vle/figures/"
            "associating_saturation_scope",
        ),
    },
)

_CAPABILITY_FIELDS = (
    "family",
    "owner",
    "public_entrypoint",
    "native_owner",
    "input_scope",
    "proof_ids",
)
_PROOF_FIELDS = (
    "proof_nodes",
    "strict_checkers",
    "data_sources",
    "artifact_paths",
    "acceptance_metrics",
)


def _nonempty(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Collection):
        return bool(value)
    return value is not None


_PACKAGE_SOURCE_ROOT = "packages/epcsaft-equilibrium/src/epcsaft_equilibrium"
_NATIVE_EQUILIBRIUM_ROOT = f"{_PACKAGE_SOURCE_ROOT}/native/equilibrium"
_REQUEST_OWNER = f"{_PACKAGE_SOURCE_ROOT}/core/native_requests.py"
_WORKFLOW_OWNER = f"{_PACKAGE_SOURCE_ROOT}/workflows.py"
_ACTIVATION_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/core/activation_matrix.h"
_BOUNDARY_FORMULATION_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/routes/derived/bubble_dew.cpp"
_TWO_PHASE_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/core/two_phase_eos_route.cpp"
_IPOPT_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/solvers/ipopt_adapter.cpp"
_RESULT_CERTIFICATION_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/results/result_builder.cpp"
_HELD_CERTIFICATION_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/results/held_certification.cpp"
_PYTHON_RESULT_OWNER = f"{_PACKAGE_SOURCE_ROOT}/core/native_results.py"
_BINDING_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/register_bindings.cpp"
_ASSOCIATION_FORMULATION_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/blocks/eos_phase_block.cpp"
_ASSOCIATION_DERIVATIVE_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/derivatives/phase_block_derivatives.cpp"
_ELECTROLYTE_FORMULATION_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/blocks/electrolyte_block.cpp"
_CHEMICAL_EQUILIBRIUM_REQUEST_OWNER = f"{_PACKAGE_SOURCE_ROOT}/chemical_equilibrium.py"
_CHEMICAL_EQUILIBRIUM_NLP_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/core/chemical_equilibrium_nlp.cpp"
_CHEMICAL_EQUILIBRIUM_RESULT_OWNER = f"{_NATIVE_EQUILIBRIUM_ROOT}/core/activated_equilibrium_nlp.cpp"

_OWNERSHIP_OWNER_FIELDS = (
    "request_owner",
    "condition_resolution_owner",
    "activation_owner",
    "formulation_owner",
    "nlp_owner",
    "solver_owner",
    "discovery_owner",
    "certification_owner",
    "result_owner",
    "binding_owner",
)
_OWNERSHIP_REQUIRED_FIELDS = (
    "record_id",
    "package",
    "milestone",
    "responsibility",
    "visibility",
    "public_entrypoint",
    "selector_families",
    "public_routes",
    "supported_scope",
    *_OWNERSHIP_OWNER_FIELDS,
    "proof_ids",
    "proof_nodes",
    "strict_checkers",
    "retained_artifacts",
    "evidence_disposition",
    "scientific_guard",
)
_OWNERSHIP_VISIBILITIES = {"production", "internal_validation", "declared_not_exposed"}
_NOT_APPLICABLE_PREFIX = "not_applicable:"


def _proof_values_tuple(proof_ids: Sequence[str], field: str) -> tuple[str, ...]:
    values: list[str] = []
    for proof_id in proof_ids:
        for value in PROOF_EVIDENCE_BY_ID[proof_id][field]:
            string_value = str(value)
            if string_value not in values:
                values.append(string_value)
    return tuple(values)


def _ownership_record(
    record_id: str,
    *,
    responsibility: str,
    visibility: str,
    public_entrypoint: str,
    selector_families: tuple[str, ...],
    public_routes: tuple[str, ...],
    supported_scope: str,
    request_owner: str,
    condition_resolution_owner: str,
    activation_owner: str,
    formulation_owner: str,
    nlp_owner: str,
    solver_owner: str,
    discovery_owner: str,
    certification_owner: str,
    result_owner: str,
    binding_owner: str,
    proof_ids: tuple[str, ...] = (),
    proof_nodes: tuple[str, ...] = (),
    strict_checkers: tuple[str, ...] = (),
    retained_artifacts: tuple[str, ...] = (),
    evidence_disposition: str,
    scientific_guard: str,
) -> dict[str, object]:
    if proof_ids:
        proof_nodes = tuple(
            dict.fromkeys((*proof_nodes, *_proof_values_tuple(proof_ids, "proof_nodes")))
        )
        strict_checkers = tuple(
            dict.fromkeys(
                (*strict_checkers, *_proof_values_tuple(proof_ids, "strict_checkers"))
            )
        )
        retained_artifacts = tuple(
            dict.fromkeys(
                (*retained_artifacts, *_proof_values_tuple(proof_ids, "artifact_paths"))
            )
        )
    return {
        "record_id": record_id,
        "package": "epcsaft-equilibrium",
        "milestone": "M4 - Equilibrium",
        "responsibility": responsibility,
        "visibility": visibility,
        "public_entrypoint": public_entrypoint,
        "selector_families": selector_families,
        "public_routes": public_routes,
        "supported_scope": supported_scope,
        "request_owner": request_owner,
        "condition_resolution_owner": condition_resolution_owner,
        "activation_owner": activation_owner,
        "formulation_owner": formulation_owner,
        "nlp_owner": nlp_owner,
        "solver_owner": solver_owner,
        "discovery_owner": discovery_owner,
        "certification_owner": certification_owner,
        "result_owner": result_owner,
        "binding_owner": binding_owner,
        "proof_ids": proof_ids,
        "proof_nodes": proof_nodes,
        "strict_checkers": strict_checkers,
        "retained_artifacts": retained_artifacts,
        "evidence_disposition": evidence_disposition,
        "scientific_guard": scientific_guard,
    }


EQUILIBRIUM_OWNERSHIP_BY_ID: Final[dict[str, dict[str, object]]] = {
    "public_pressure_boundary_routes": _ownership_record(
        "public_pressure_boundary_routes",
        responsibility="public bubble-pressure and dew-pressure selector workflow",
        visibility="production",
        public_entrypoint=str(
            CAPABILITY_EVIDENCE_BY_FAMILY["bubble_dew_derived_routes"]["public_entrypoint"]
        ),
        selector_families=("bubble_dew_derived_routes",),
        public_routes=("bubble_pressure", "dew_pressure"),
        supported_scope=str(
            CAPABILITY_EVIDENCE_BY_FAMILY["bubble_dew_derived_routes"]["input_scope"]
        ),
        request_owner=_REQUEST_OWNER,
        condition_resolution_owner=_WORKFLOW_OWNER,
        activation_owner=_ACTIVATION_OWNER,
        formulation_owner=_BOUNDARY_FORMULATION_OWNER,
        nlp_owner=_BOUNDARY_FORMULATION_OWNER,
        solver_owner=_IPOPT_OWNER,
        discovery_owner="not_applicable:direct_boundary_route",
        certification_owner=_RESULT_CERTIFICATION_OWNER,
        result_owner=_PYTHON_RESULT_OWNER,
        binding_owner=_BINDING_OWNER,
        proof_ids=tuple(
            str(value)
            for value in CAPABILITY_EVIDENCE_BY_FAMILY["bubble_dew_derived_routes"][
                "proof_ids"
            ]
        ),
        evidence_disposition="accepted_production_behavior",
        scientific_guard=(
            "Direct boundary routes do not borrow HELD phase-discovery completion."
        ),
    ),
    "public_single_component_saturation": _ownership_record(
        "public_single_component_saturation",
        responsibility="public scoped single-component saturation workflow",
        visibility="production",
        public_entrypoint=str(
            CAPABILITY_EVIDENCE_BY_FAMILY["single_component_vle"]["public_entrypoint"]
        ),
        selector_families=("single_component_vle",),
        public_routes=("single_component_vle",),
        supported_scope=str(
            CAPABILITY_EVIDENCE_BY_FAMILY["single_component_vle"]["input_scope"]
        ),
        request_owner=_REQUEST_OWNER,
        condition_resolution_owner=_WORKFLOW_OWNER,
        activation_owner=_ACTIVATION_OWNER,
        formulation_owner=_BOUNDARY_FORMULATION_OWNER,
        nlp_owner=_BOUNDARY_FORMULATION_OWNER,
        solver_owner=_IPOPT_OWNER,
        discovery_owner="not_applicable:scoped_pure_saturation_route",
        certification_owner=_RESULT_CERTIFICATION_OWNER,
        result_owner=_PYTHON_RESULT_OWNER,
        binding_owner=_BINDING_OWNER,
        proof_ids=tuple(
            str(value)
            for value in CAPABILITY_EVIDENCE_BY_FAMILY["single_component_vle"]["proof_ids"]
        ),
        evidence_disposition="accepted_production_behavior",
        scientific_guard="The record does not extend the component or temperature scope.",
    ),
    "neutral_local_equilibrium_components": _ownership_record(
        "neutral_local_equilibrium_components",
        responsibility="closed neutral local equilibrium and sampled-candidate components",
        visibility="internal_validation",
        public_entrypoint="not_applicable:closed_internal_validation",
        selector_families=("neutral_tp_flash", "neutral_lle", "neutral_multiphase_nonassoc"),
        public_routes=(),
        supported_scope=(
            "local neutral phase-set NLP, deterministic candidate screening, sampled-candidate "
            "audit, and postsolve characterization"
        ),
        request_owner="not_applicable:direct_native_internal_validation_inputs",
        condition_resolution_owner=_TWO_PHASE_OWNER,
        activation_owner=_ACTIVATION_OWNER,
        formulation_owner=_TWO_PHASE_OWNER,
        nlp_owner=_TWO_PHASE_OWNER,
        solver_owner=_IPOPT_OWNER,
        discovery_owner=_TWO_PHASE_OWNER,
        certification_owner=_HELD_CERTIFICATION_OWNER,
        result_owner=_RESULT_CERTIFICATION_OWNER,
        binding_owner=_BINDING_OWNER,
        proof_ids=("neutral_lle_matsuda_2011_nist_sampled_candidate_diagnostic",),
        proof_nodes=(
            "packages/epcsaft-equilibrium/tests/native/results/"
            "test_neutral_lle_reference_values.py::"
            "test_neutral_tpd_phase_discovery_reports_candidate_set_for_lle_binary",
        ),
        strict_checkers=(
            "uv run --no-sync python scripts/validation/check_neutral_lle_showcase.py "
            "--json --require-complete --require-fresh-native",
            "uv run --no-sync python scripts/validation/check_generalized_phase_set.py "
            "--json --require-complete",
        ),
        evidence_disposition="accepted_components_global_phase_completeness_unproven",
        scientific_guard=(
            "Sampled candidates and local refinement do not establish a completed HELD dual loop."
        ),
    ),
    "associating_equilibrium_components": _ownership_record(
        "associating_equilibrium_components",
        responsibility="association mass action and implicit derivative components",
        visibility="internal_validation",
        public_entrypoint="not_applicable:component_record",
        selector_families=("bubble_dew_derived_routes", "neutral_lle"),
        public_routes=(),
        supported_scope=(
            "association mass action, implicit first and second sensitivities, and exact "
            "association Hessian assembly"
        ),
        request_owner="not_applicable:thermodynamic_component",
        condition_resolution_owner=_ASSOCIATION_FORMULATION_OWNER,
        activation_owner=_ACTIVATION_OWNER,
        formulation_owner=_ASSOCIATION_FORMULATION_OWNER,
        nlp_owner=_ASSOCIATION_DERIVATIVE_OWNER,
        solver_owner=_IPOPT_OWNER,
        discovery_owner=_TWO_PHASE_OWNER,
        certification_owner=_RESULT_CERTIFICATION_OWNER,
        result_owner=_PYTHON_RESULT_OWNER,
        binding_owner=_BINDING_OWNER,
        proof_ids=(
            "associating_neutral_lle_gross_2002_internal_exact_hessian",
            "associating_neutral_lle_gross_2002_figure_10_internal_exact_hessian",
        ),
        evidence_disposition="accepted_internal_component_behavior",
        scientific_guard=(
            "Association extends phase evaluation and does not create a second HELD controller."
        ),
    ),
    "electrolyte_equilibrium_components": _ownership_record(
        "electrolyte_equilibrium_components",
        responsibility="closed electrolyte charge-neutral and counterion-pair components",
        visibility="internal_validation",
        public_entrypoint="not_applicable:closed_internal_validation",
        selector_families=("electrolyte_lle",),
        public_routes=(),
        supported_scope=(
            "charge blocks, electrolyte Helmholtz contributions, counterion-pair coordinates, "
            "local residual correction, and formulation-specific postsolve diagnostics"
        ),
        request_owner="not_applicable:direct_native_internal_validation_inputs",
        condition_resolution_owner=_TWO_PHASE_OWNER,
        activation_owner=_ACTIVATION_OWNER,
        formulation_owner=_ELECTROLYTE_FORMULATION_OWNER,
        nlp_owner=_TWO_PHASE_OWNER,
        solver_owner=_IPOPT_OWNER,
        discovery_owner=_TWO_PHASE_OWNER,
        certification_owner=_RESULT_CERTIFICATION_OWNER,
        result_owner=_RESULT_CERTIFICATION_OWNER,
        binding_owner=_BINDING_OWNER,
        proof_nodes=(
            "tests/native/contracts/test_electrolyte_held2_phase_discovery.py",
            "tests/native/contracts/test_electrolyte_stage_iii_refinement.py",
            "tests/native/contracts/test_electrolyte_postsolve_certification.py",
        ),
        strict_checkers=(
            "uv run --no-sync python scripts/validation/"
            "check_electrolyte_held2_phase_discovery.py --json --require-complete",
            "uv run --no-sync python scripts/validation/"
            "check_electrolyte_stage_iii_refinement.py --json --require-complete",
            "uv run --no-sync python scripts/validation/"
            "check_electrolyte_postsolve_certification.py --json --require-complete",
        ),
        retained_artifacts=(
            "data/reference/equilibrium_benchmarks/electrolyte_lle/"
            "water_ethanol_isobutanol_nacl",
        ),
        evidence_disposition="accepted_components_failed_model_reproduction_retained",
        scientific_guard=(
            "Current counterion-pair and mean-ionic mechanics are Ascani-family component "
            "evidence, not Perdomo modified-mole HELD2; certification must use independent "
            "formulation-specific modified-potential or mean-ionic conditions, not generic "
            "individual-ion chemical-potential equality without an explicit Galvani convention."
        ),
    ),
    "standalone_chemical_equilibrium_components": _ownership_record(
        "standalone_chemical_equilibrium_components",
        responsibility="closed standalone chemical-equilibrium schema and local NLP",
        visibility="internal_validation",
        public_entrypoint="not_applicable:closed_internal_validation",
        selector_families=("reactive_speciation",),
        public_routes=(),
        supported_scope=(
            "homogeneous species/reaction schema, conservation, standard-state records, "
            "Gibbs NLP, exact derivatives, and proof diagnostics"
        ),
        request_owner=_CHEMICAL_EQUILIBRIUM_REQUEST_OWNER,
        condition_resolution_owner=_CHEMICAL_EQUILIBRIUM_REQUEST_OWNER,
        activation_owner=_ACTIVATION_OWNER,
        formulation_owner=_CHEMICAL_EQUILIBRIUM_NLP_OWNER,
        nlp_owner=_CHEMICAL_EQUILIBRIUM_NLP_OWNER,
        solver_owner=_IPOPT_OWNER,
        discovery_owner="not_applicable:homogeneous_single_phase_problem",
        certification_owner=_CHEMICAL_EQUILIBRIUM_NLP_OWNER,
        result_owner=_CHEMICAL_EQUILIBRIUM_RESULT_OWNER,
        binding_owner=_BINDING_OWNER,
        proof_nodes=(
            "packages/epcsaft-equilibrium/tests/native/diagnostics/"
            "test_chemical_equilibrium_nlp_activation.py::"
            "test_internal_standalone_ce_validation_uses_single_activation_nlp_path",
            "tests/native/contracts/test_standalone_ce_gate.py",
        ),
        strict_checkers=(
            "uv run --no-sync python scripts/validation/check_standalone_ce_gate.py "
            "--json --require-single-nlp-path --require-oracles --require-complete",
        ),
        retained_artifacts=(
            "analyses/package_validation/standalone_ce/shared/results/summary.json",
        ),
        evidence_disposition="accepted_components_failed_nonideal_output_retained",
        scientific_guard=(
            "The failed nonideal MEA balance and stationarity result is evidence, not target parity."
        ),
    ),
}

EQUILIBRIUM_CHARACTERIZATION_RECEIPT: Final[dict[str, object]] = {
    "schema_version": 1,
    "ownership_schema_basis": (
        "docs/superpowers/specs/"
        "2026-07-10-m0-characterized-ownership-and-maintainability-ratchets.md#ownership-records"
    ),
    "preservation_manifest": (
        "docs/superpowers/milestones/M4-equilibrium/equilibrium-preservation-manifest.yaml"
    ),
    "native_source_manifest": (
        "packages/epcsaft-equilibrium/cmake/equilibrium_native_sources.json"
    ),
    "build_refresh_command": (
        "uv run --no-sync python scripts/dev/build_epcsaft.py "
        "--profile equilibrium --build-only --parallel 4"
    ),
    "runtime_receipt_required_fields": (
        "git_commit",
        "native_module_path",
        "checker_command",
        "build_refresh_command",
        "freshness_mode",
        "source_identity_algorithm",
        "source_identity_scope",
        "source_identity_limit",
        "source_identity_file_count",
        "current_source_identity",
        "embedded_source_identity_algorithm",
        "embedded_source_identity_scope",
        "embedded_source_identity_limit",
        "embedded_source_identity_file_count",
        "embedded_source_identity",
        "source_identity_matches",
    ),
    "public_routes_unchanged": (
        "bubble_pressure",
        "dew_pressure",
        "single_component_vle",
    ),
    "ownership_record_ids": tuple(EQUILIBRIUM_OWNERSHIP_BY_ID),
}


def validate_equilibrium_ownership_records(
    records: Mapping[str, Mapping[str, object]] | None = None,
) -> None:
    """Validate the M4 records against the documented inactive ownership contract."""

    selected = EQUILIBRIUM_OWNERSHIP_BY_ID if records is None else records
    diagnostics: list[str] = []
    public_route_owners: dict[str, str] = {}
    for record_id, record in selected.items():
        unknown = sorted(set(record) - set(_OWNERSHIP_REQUIRED_FIELDS))
        missing = sorted(set(_OWNERSHIP_REQUIRED_FIELDS) - set(record))
        diagnostics.extend(f"unknown_field:{record_id}:{field}" for field in unknown)
        diagnostics.extend(f"missing_field:{record_id}:{field}" for field in missing)
        if missing:
            continue
        if record.get("record_id") != record_id:
            diagnostics.append(f"record_id_mismatch:{record_id}")
        if record.get("package") != "epcsaft-equilibrium":
            diagnostics.append(f"package_mismatch:{record_id}")
        if record.get("milestone") != "M4 - Equilibrium":
            diagnostics.append(f"milestone_mismatch:{record_id}")
        visibility = str(record.get("visibility", ""))
        if visibility not in _OWNERSHIP_VISIBILITIES:
            diagnostics.append(f"invalid_visibility:{record_id}:{visibility}")
        if not _nonempty(record.get("responsibility")):
            diagnostics.append(f"responsibility_missing:{record_id}")
        if not _nonempty(record.get("supported_scope")):
            diagnostics.append(f"supported_scope_missing:{record_id}")
        if not _nonempty(record.get("evidence_disposition")):
            diagnostics.append(f"evidence_disposition_missing:{record_id}")
        if not _nonempty(record.get("scientific_guard")):
            diagnostics.append(f"scientific_guard_missing:{record_id}")

        for field in _OWNERSHIP_OWNER_FIELDS:
            owner = record.get(field)
            if not isinstance(owner, str) or not owner.strip():
                diagnostics.append(f"exactly_one_owner:{record_id}:{field}")
                continue
            if not owner.startswith((_PACKAGE_SOURCE_ROOT + "/", _NOT_APPLICABLE_PREFIX)):
                diagnostics.append(f"non_package_runtime_owner:{record_id}:{field}:{owner}")

        discovery_owner = str(record.get("discovery_owner", ""))
        certification_owner = str(record.get("certification_owner", ""))
        if (
            not discovery_owner.startswith(_NOT_APPLICABLE_PREFIX)
            and discovery_owner == certification_owner
        ):
            diagnostics.append(f"discovery_owned_certification:{record_id}")
        binding_owner = str(record.get("binding_owner", ""))
        if binding_owner in {
            str(record.get("solver_owner", "")),
            str(record.get("certification_owner", "")),
        }:
            diagnostics.append(f"binding_owned_solver_or_certification:{record_id}")

        selector_families = record.get("selector_families")
        if (
            not isinstance(selector_families, tuple)
            or not selector_families
            or len(selector_families) != len(set(selector_families))
        ):
            diagnostics.append(f"invalid_selector_families:{record_id}")
        public_routes = record.get("public_routes")
        if not isinstance(public_routes, tuple):
            diagnostics.append(f"invalid_public_routes:{record_id}")
            public_routes = ()
        if visibility == "production":
            if not public_routes:
                diagnostics.append(f"production_routes_missing:{record_id}")
            public_entrypoint = str(record.get("public_entrypoint", ""))
            if not public_entrypoint.strip() or public_entrypoint.startswith(
                _NOT_APPLICABLE_PREFIX
            ):
                diagnostics.append(f"production_entrypoint_missing:{record_id}")
        else:
            if public_routes:
                diagnostics.append(f"internal_record_publishes_routes:{record_id}")
            if not str(record.get("public_entrypoint", "")).startswith(_NOT_APPLICABLE_PREFIX):
                diagnostics.append(f"internal_record_publishes_entrypoint:{record_id}")
        for route in public_routes:
            route_name = str(route)
            previous = public_route_owners.get(route_name)
            if previous is not None:
                diagnostics.append(f"duplicate_public_route_owner:{route_name}:{previous}:{record_id}")
            else:
                public_route_owners[route_name] = record_id

        for field in ("proof_ids", "proof_nodes", "strict_checkers", "retained_artifacts"):
            if not isinstance(record.get(field), tuple):
                diagnostics.append(f"invalid_evidence_sequence:{record_id}:{field}")
        if not _nonempty(record.get("proof_nodes")):
            diagnostics.append(f"proof_nodes_missing:{record_id}")
        for proof_id in record.get("proof_ids", ()):
            proof = PROOF_EVIDENCE_BY_ID.get(str(proof_id))
            if proof is None:
                diagnostics.append(f"unknown_proof_id:{record_id}:{proof_id}")
            elif visibility == "production" and proof.get("admission") != "production_complete":
                diagnostics.append(f"nonproduction_proof_for_public_owner:{record_id}:{proof_id}")

    if diagnostics:
        raise RuntimeError("Equilibrium ownership records are invalid: " + ", ".join(sorted(diagnostics)))


def validate_equilibrium_ownership_paths(
    repo_root: Path,
    records: Mapping[str, Mapping[str, object]] | None = None,
) -> None:
    """Resolve checkpoint-owned paths without burdening installed imports."""

    selected = EQUILIBRIUM_OWNERSHIP_BY_ID if records is None else records
    root = repo_root.resolve()
    missing: list[str] = []
    for record_id, record in selected.items():
        targets: list[tuple[str, str, bool]] = []
        targets.extend(
            (field, str(record.get(field, "")), True)
            for field in _OWNERSHIP_OWNER_FIELDS
            if not str(record.get(field, "")).startswith(_NOT_APPLICABLE_PREFIX)
        )
        targets.extend(
            ("proof_nodes", str(value).partition("::")[0], True)
            for value in record.get("proof_nodes", ())
        )
        targets.extend(
            ("retained_artifacts", str(value), False)
            for value in record.get("retained_artifacts", ())
        )
        for command in record.get("strict_checkers", ()):
            targets.extend(
                ("strict_checkers", token.partition("::")[0], True)
                for token in shlex.split(str(command))
                if ".py" in token and token.partition("::")[0].startswith(_REPO_PATH_PREFIXES)
            )
        for field, relative, must_be_file in targets:
            resolved = (root / relative).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                missing.append(f"{record_id}:{field}:{relative}:outside-repo")
                continue
            if not resolved.exists() or (must_be_file and not resolved.is_file()):
                missing.append(f"{record_id}:{field}:{relative}")
    if missing:
        raise RuntimeError(
            "missing equilibrium ownership target(s): " + ", ".join(sorted(missing))
        )


def _validate_registry() -> None:
    for family, record in CAPABILITY_EVIDENCE_BY_FAMILY.items():
        if record.get("family") != family:
            raise RuntimeError(f"Capability evidence key mismatch for '{family}'.")
        missing_fields = [field for field in _CAPABILITY_FIELDS if not _nonempty(record.get(field))]
        if missing_fields:
            raise RuntimeError(
                f"Capability evidence for '{family}' is incomplete: {', '.join(missing_fields)}."
            )
        for proof_id in record["proof_ids"]:
            proof = PROOF_EVIDENCE_BY_ID.get(str(proof_id))
            if proof is None:
                raise RuntimeError(
                    f"Capability evidence for '{family}' references unknown proof '{proof_id}'."
                )
            if proof.get("admission") != "production_complete":
                raise RuntimeError(
                    f"Capability evidence for '{family}' references non-production proof '{proof_id}'."
                )
            missing_proof_fields = [
                field for field in _PROOF_FIELDS if not _nonempty(proof.get(field))
            ]
            if missing_proof_fields:
                raise RuntimeError(
                    f"Proof evidence '{proof_id}' is incomplete: {', '.join(missing_proof_fields)}."
                )


_REPO_PATH_PREFIXES = ("analyses/", "data/", "docs/", "packages/", "scripts/", "tests/")


def validate_repo_evidence_targets(
    repo_root: Path,
    *,
    proof_evidence: Mapping[str, Mapping[str, object]] | None = None,
) -> None:
    """Resolve every repository-owned proof target without burdening installed imports."""

    records = PROOF_EVIDENCE_BY_ID if proof_evidence is None else proof_evidence
    missing: list[str] = []
    for proof_id, proof in records.items():
        targets: list[tuple[str, str, bool]] = []
        targets.extend(
            ("artifact_paths", str(value), True)
            for value in proof.get("artifact_paths", ())
        )
        targets.extend(
            ("data_sources", str(value), False)
            for value in proof.get("data_sources", ())
            if str(value).startswith(_REPO_PATH_PREFIXES)
        )
        targets.extend(
            ("proof_nodes", str(value).partition("::")[0], True)
            for value in proof.get("proof_nodes", ())
        )
        for command in proof.get("strict_checkers", ()):
            targets.extend(
                ("strict_checkers", token.partition("::")[0], True)
                for token in shlex.split(str(command))
                if ".py" in token and token.partition("::")[0].startswith(_REPO_PATH_PREFIXES)
            )
        for field, relative, must_be_file in targets:
            path = repo_root / relative
            resolved = path.resolve()
            try:
                resolved.relative_to(repo_root.resolve())
            except ValueError:
                missing.append(f"{proof_id}:{field}:{relative}:outside-repo")
                continue
            if not resolved.exists() or (must_be_file and not resolved.is_file()):
                missing.append(f"{proof_id}:{field}:{relative}")
    if missing:
        raise RuntimeError("missing repository evidence target(s): " + ", ".join(sorted(missing)))


def _generated_execution_receipts() -> Mapping[str, Mapping[str, object]]:
    from epcsaft_equilibrium.equilibrium_activation import (
        EQUILIBRIUM_PROOF_EXECUTION_RECEIPTS,
    )

    return EQUILIBRIUM_PROOF_EXECUTION_RECEIPTS


def _validate_execution_receipts(
    execution_receipts: Mapping[str, Mapping[str, object]],
) -> None:
    production_proof_ids = {
        str(proof_id)
        for record in CAPABILITY_EVIDENCE_BY_FAMILY.values()
        for proof_id in record["proof_ids"]
    }
    if set(execution_receipts) != production_proof_ids:
        raise RuntimeError(
            "Production equilibrium evidence requires one passing strict-checker execution "
            "receipt for every admitted proof."
        )
    for proof_id in sorted(production_proof_ids):
        proof = PROOF_EVIDENCE_BY_ID[proof_id]
        receipt = execution_receipts[proof_id]
        expected_commands = [str(command) for command in proof["strict_checkers"]]
        checker_receipts = receipt.get("checker_receipts")
        digest = str(receipt.get("evidence_digest", ""))
        valid_digest = len(digest) == 64 and all(character in "0123456789abcdef" for character in digest)
        valid_checkers = (
            isinstance(checker_receipts, Sequence)
            and not isinstance(checker_receipts, str | bytes)
            and len(checker_receipts) == len(expected_commands)
        )
        if valid_checkers:
            for command, checker_receipt in zip(expected_commands, checker_receipts, strict=True):
                if not isinstance(checker_receipt, Mapping) or not (
                    checker_receipt.get("command") == command
                    and checker_receipt.get("complete") is True
                    and checker_receipt.get("status") == "passed"
                    and checker_receipt.get("blockers") == []
                    and checker_receipt.get("freshness_mode") == "embedded_source_identity"
                    and checker_receipt.get("source_identity_matches") is True
                    and str(checker_receipt.get("current_source_identity", ""))
                    == str(checker_receipt.get("embedded_source_identity", ""))
                    and bool(str(checker_receipt.get("current_source_identity", "")))
                ):
                    valid_checkers = False
                    break
        if not (
            receipt.get("status") == "passed"
            and receipt.get("strict_checkers") == expected_commands
            and valid_checkers
            and valid_digest
        ):
            raise RuntimeError(
                "Production equilibrium evidence requires a passing strict-checker execution "
                f"receipt for proof '{proof_id}'."
            )


def complete_evidence_families(
    *,
    execution_receipts: Mapping[str, Mapping[str, object]] | None = None,
) -> set[str]:
    """Return families satisfying the complete production evidence contract."""

    _validate_registry()
    _validate_execution_receipts(
        _generated_execution_receipts() if execution_receipts is None else execution_receipts
    )
    return set(CAPABILITY_EVIDENCE_BY_FAMILY)


def _unique_values(
    proof_ids: Sequence[object],
    field: str,
) -> list[object]:
    values: list[object] = []
    for proof_id in proof_ids:
        for value in PROOF_EVIDENCE_BY_ID[str(proof_id)][field]:
            if value not in values:
                values.append(value)
    return values


def production_capability_evidence(
    activation_rows: Sequence[Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    """Join complete evidence to the native production activation rows."""

    _validate_registry()
    rows_by_family = {str(row["key"]): row for row in activation_rows}
    native_families = {
        family
        for family, row in rows_by_family.items()
        if bool(row.get("production_exposed"))
    }
    evidence_families = complete_evidence_families()
    if native_families != evidence_families:
        raise RuntimeError(
            "Native production families do not match complete equilibrium evidence families: "
            f"native={sorted(native_families)}, evidence={sorted(evidence_families)}."
        )

    joined: dict[str, dict[str, object]] = {}
    for family, record in CAPABILITY_EVIDENCE_BY_FAMILY.items():
        activation = rows_by_family.get(family)
        if activation is None:
            raise RuntimeError(f"Native activation row is missing for evidence family '{family}'.")
        proof_ids = tuple(str(value) for value in record["proof_ids"])
        if list(activation.get("proof_routes", ())) != list(proof_ids):
            raise RuntimeError(
                f"Native proof routes do not match evidence for '{family}'."
            )
        public_routes = [str(value) for value in activation.get("public_routes", ())]
        if not public_routes:
            raise RuntimeError(f"Evidence-complete family '{family}' publishes no public routes.")
        joined[family] = {
            **record,
            "proof_ids": list(proof_ids),
            "public_routes": public_routes,
            "proof_nodes": _unique_values(proof_ids, "proof_nodes"),
            "strict_checkers": _unique_values(proof_ids, "strict_checkers"),
            "data_sources": _unique_values(proof_ids, "data_sources"),
            "artifact_paths": _unique_values(proof_ids, "artifact_paths"),
            "acceptance_metrics": {
                proof_id: dict(PROOF_EVIDENCE_BY_ID[proof_id]["acceptance_metrics"])
                for proof_id in proof_ids
            },
        }
    return joined


def validate_proof_collection(collected_nodes: Collection[str]) -> None:
    """Fail when any production proof node is absent from pytest collection."""

    _validate_registry()
    required_nodes = {
        str(node)
        for proof in PROOF_EVIDENCE_BY_ID.values()
        if proof.get("admission") == "production_complete"
        for node in proof["proof_nodes"]
    }
    missing = sorted(required_nodes - set(collected_nodes))
    if missing:
        raise RuntimeError("uncollected proof nodes: " + ", ".join(missing))
