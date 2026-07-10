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


def complete_evidence_families() -> set[str]:
    """Return families satisfying the complete production evidence contract."""

    _validate_registry()
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
