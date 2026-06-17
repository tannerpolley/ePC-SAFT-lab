from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = (
    REPO_ROOT
    / "docs"
    / "superpowers"
    / "milestones"
    / "M4-equilibrium"
    / "registries"
    / "equilibrium-benchmark-registry.yaml"
)
GFPE_PATH = (
    REPO_ROOT
    / "docs"
    / "superpowers"
    / "milestones"
    / "M4-equilibrium"
    / "generalized-fluid-phase-equilibrium.md"
)
STAGE_PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "superpowers"
    / "specs"
    / "2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md"
)

EXPECTED_FAMILY_LABELS = {
    "PE-Neutral TP Flash",
    "PE-Associating TP Flash",
    "PE-Electrolyte LLE/TP Flash",
    "PE-Generalized Multiphase",
    "CE Chemical Equilibrium Placeholder",
    "CPE Combined Phase-Chemical Placeholder",
}
DERIVED_LABELS = {"Bubble point", "Dew point", "Cloud point", "Shadow point"}
FORBIDDEN_NUMERIC_ROW_RE = re.compile(r"\b(?:PE|CE|CPE)-\d{2}\b")


def _registry() -> dict[str, Any]:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def _family_rows() -> list[dict[str, Any]]:
    return _registry()["family_rows"]


def _family_by_label() -> dict[str, dict[str, Any]]:
    return {row["family_label"]: row for row in _family_rows()}


def test_registry_uses_collapsed_schema_v2_family_labels() -> None:
    registry = _registry()
    rows = _family_by_label()

    assert registry["schema_version"] == 2
    assert "activation_rows" not in registry
    assert set(rows) == EXPECTED_FAMILY_LABELS
    assert registry["policy"]["label_policy"].endswith("not runtime keys or public route strings.")


def test_family_labels_replace_numeric_matrix_ids() -> None:
    registry_text = REGISTRY_PATH.read_text(encoding="utf-8")
    gfpe_text = GFPE_PATH.read_text(encoding="utf-8")

    assert "key: PE-" not in registry_text
    assert "key: CE-" not in registry_text
    assert "key: CPE-" not in registry_text
    assert "PE-01" not in registry_text
    assert "CE-01" not in registry_text
    assert "CPE-01" not in registry_text

    assert "PE-01" not in gfpe_text
    assert "CE-01" not in gfpe_text
    assert "CPE-01" not in gfpe_text
    assert "planning labels only" in gfpe_text


def test_gfpe_plan_is_pretreatment_centered() -> None:
    stage_text = STAGE_PLAN_PATH.read_text(encoding="utf-8")

    assert "GFPE is the organizing spine for this file." in stage_text
    assert "`PROJECT_CONTEXT.md` is a boundary" in stage_text
    assert "document: it explains package identity" in stage_text
    assert (
        "Package-wide milestones are intentionally not used as stage names." in stage_text
    )
    assert "Pereira 2012 System III remains HELD/SAFT-VR literature context" in stage_text
    assert "first neutral validation target must be a source-backed ePC-SAFT-compatible" in stage_text
    assert "## GFPE Pretreatment Pipeline" in stage_text
    assert "public request\n  -> request-shape record" in stage_text
    assert "parameter and EOS-contribution suitability record" in stage_text
    assert "bounds, scaling, and transform record" in stage_text
    assert "## Stage 8 - Shared NLP And Ipopt Infrastructure Gate" in stage_text
    assert "complete Ipopt numerics gate" in stage_text
    assert "`proof`, `continuation_trace`, `held_refinement`, and `diagnostic`" in stage_text
    assert "`profile_exact_hessian_gate`" in stage_text
    assert "Stage 9 cannot use real-mixture HELD validation cases" in stage_text
    assert "## Stage 17 - Registry, Capability, And Benchmark Closure" in stage_text
    assert stage_text.index("## Stage 9 - Continuous TPD And HELD Stage Ladder") < stage_text.index(
        "## Stage 10 - Neutral TP Flash Source-Backed Fixture"
    )
    assert stage_text.index("## Stage 10 - Neutral TP Flash Source-Backed Fixture") < stage_text.index(
        "## Stage 11 - Derived Boundary Workflows And Diagram Traces"
    )


def test_stage9_phase_discovery_checker_requires_complete_exit_status() -> None:
    stage_text = STAGE_PLAN_PATH.read_text(encoding="utf-8")

    required_command = (
        "uv run python scripts/validation/check_phase_discovery.py "
        "--json --include-route-refinement --require-complete"
    )

    assert required_command in stage_text


def test_only_generalized_neutral_multiphase_claims_public_admission() -> None:
    for row in _family_rows():
        assert "required_gates" in row, row["family_label"]
        if row["family_label"] == "PE-Generalized Multiphase":
            assert row["activation_status"] == "neutral_public_admitted"
            assert row["production_exposed"] is True
            assert row["existing_public_utility_routes"] == ["multiphase"]
        else:
            assert row["activation_status"] == "planned_not_public", row["family_label"]
            assert row["production_exposed"] is False, row["family_label"]

    neutral = _family_by_label()["PE-Neutral TP Flash"]
    assert "continuous_tpd_minimization" in neutral["required_gates"]
    assert "held_stage_ii_dual_phase_discovery" in neutral["required_gates"]
    assert (
        neutral["phase_discovery_status"]
        == "continuous_tpd_stage_i_stage_ii_dual_loop_replay_verified_current_fixture"
    )
    assert neutral["phase_discovery_gate_status"]["deterministic_screening"].endswith("not_full_held")
    assert (
        neutral["phase_discovery_gate_status"]["continuous_tpd_minimization"]
        == "implemented_neutral_coordinate_search_convergence_required"
    )
    expected_stage_i_status = "implemented_neutral_multi_start_convergence_required"
    assert neutral["phase_discovery_gate_status"]["held_stage_i_stability"] == expected_stage_i_status
    assert (
        neutral["phase_discovery_gate_status"]["held_stage_ii_candidate_bound_audit"]
        == "current_neutral_candidate_bound_audit_closed"
    )
    assert (
        neutral["phase_discovery_gate_status"]["held_stage_ii_dual_phase_discovery"]
        == "current_neutral_dual_loop_replay_verified_current_fixture"
    )
    assert (
        neutral["phase_discovery_gate_status"]["held_stage_iii_ipopt_refinement"]
        == "current_route_refinement_consumes_stage_ii_replay_with_ipopt_success"
    )


def test_bubble_dew_cloud_shadow_are_derived_subworkflows_not_family_rows() -> None:
    registry = _registry()
    family_labels = set(_family_by_label())
    subworkflows = {row["label"]: row for row in registry["derived_subworkflows"]}

    assert set(subworkflows) == DERIVED_LABELS
    assert not (DERIVED_LABELS & family_labels)

    for label, row in subworkflows.items():
        assert row["activation_family_row"] is False, label
        assert row["planned_after_family"] == "PE-Neutral TP Flash", label
        assert set(row["diagram_targets"]) == {"P-x", "T-x"}, label
        assert row["vlle_test_required"] is False, label
        assert "ePC-SAFT-compatible neutral TP flash mixture" in row["shared_mixture_policy"], label
        assert "Pereira 2012 System III remains HELD/SAFT-VR context" in row["shared_mixture_policy"], label
        assert "contract-only" in row["diagnostic_policy"], label
        assert "explicit sweep opt-in" in row["diagnostic_policy"], label
        assert "Ipopt success" in row["strict_convergence_gate"], label
        assert "no max_iterations_exceeded seed attempt" in row["strict_convergence_gate"], label
        assert "strict_ipopt_convergence" in row["acceptance_checks"], label
        assert "no_implicit_route_sweep" in row["acceptance_checks"], label

    assert subworkflows["Bubble point"]["current_convergence_status"] == (
        "current_fixture_strict_route_points_verified"
    )
    assert subworkflows["Dew point"]["current_convergence_status"] == (
        "current_fixture_strict_route_points_verified"
    )
    assert subworkflows["Cloud point"]["current_convergence_status"] == (
        "checker_gated_native_route_evidence_verified_public_routes_closed"
    )
    assert subworkflows["Shadow point"]["current_convergence_status"] == (
        "checker_gated_native_route_evidence_verified_public_routes_closed"
    )
    for label in ("Cloud point", "Shadow point"):
        row = subworkflows[label]
        assert row["current_runtime_routes"] == [], label
        assert "source_backed_cloud_binodal_rows" in row["acceptance_checks"], label
        assert "source_backed_cloud_shadow_pair" in row["acceptance_checks"], label
        assert "model_refined_source_branch_reference" in row["acceptance_checks"], label
        assert "checker_gated_native_cloud_temperature_route" in row["acceptance_checks"], label
        assert "public_route_admission_closed" in row["acceptance_checks"], label
        assert "native_route_admission_blockers_declared" not in row["acceptance_checks"], label


def test_deterministic_screening_is_not_called_full_held() -> None:
    registry = _registry()
    gfpe_text = GFPE_PATH.read_text(encoding="utf-8")

    assert registry["policy"]["deterministic_screening_policy"].endswith("not full HELD.")
    assert "Current deterministic TPD/candidate screening" in gfpe_text
    assert "must not be described as full HELD" in gfpe_text

    for row in _family_rows():
        status = str(row.get("phase_discovery_status", ""))
        if "deterministic_screening" in status:
            assert "full_held_planned" in status, row["family_label"]
            assert row["production_exposed"] is False, row["family_label"]


def test_gfpe_ipopt_layer_requires_shared_scaling_and_profile_gates() -> None:
    gfpe_text = GFPE_PATH.read_text(encoding="utf-8")
    flattened = gfpe_text.replace("\n", " ")

    assert "Ipopt must receive the route-owned scaling as user scaling." in gfpe_text
    assert "Automatic Ipopt scaling" in flattened
    assert "not the production contract for GFPE routes" in flattened
    assert "scaled constraint violation" in gfpe_text
    assert "scaled stationarity" in gfpe_text
    assert "bound complementarity" in gfpe_text
    assert "`proof`" in gfpe_text
    assert "`continuation_trace`" in gfpe_text
    assert "`held_refinement`" in gfpe_text
    assert "`diagnostic`" in gfpe_text
    assert "`profile_exact_hessian_gate`" in gfpe_text
    assert "Stage 9 must not test real mixtures" in flattened


def test_charged_and_associating_families_declare_required_gates() -> None:
    associating = _family_by_label()["PE-Associating TP Flash"]
    electrolyte = _family_by_label()["PE-Electrolyte LLE/TP Flash"]

    assert "association_mass_action" in associating["hard_constraints"]
    assert "exact_association_derivatives" in associating["required_gates"]
    assert "explicit_approx_final_production" in associating["forbidden_shortcuts"]

    assert "charge_balance" in electrolyte["hard_constraints"]
    assert "electrochemical_potential_equality" in electrolyte["hard_constraints"]
    assert "born_ssm_ds_exact_hessian" in electrolyte["required_gates"]
    expected_derivative_contract = (
        "born_ssm_ds_exact_hessian_"
        + "required_before_electrolyte_validation"
    )
    assert electrolyte["derivative_contract"] == expected_derivative_contract


def test_generalized_multiphase_records_public_admission_evidence() -> None:
    generalized = _family_by_label()["PE-Generalized Multiphase"]
    evidence = {
        row["evidence_label"]: row
        for row in generalized["admission_evidence"]
    }

    assert generalized["production_exposed"] is True
    assert generalized["existing_public_utility_routes"] == ["multiphase"]
    strict = evidence["Strict neutral multiphase fugacity-residual refinement"]
    assert strict["command"] == (
        "uv run --no-sync python scripts/validation/check_generalized_phase_set.py "
        "--json --phase-kinds liquid,liquid,liquid --run-route-refinement "
        "--require-route-refinement --require-complete"
    )
    assert "strict_multiphase_fugacity_residual_route" in strict["result_requirement"]
    assert "exact_reduced_fugacity_residual_derivatives" in strict["result_requirement"]
    assert "stage_ii_candidate_set_replay_consumed" in strict["result_requirement"]
    assert "public_route_admission_closed" not in strict["result_requirement"]
    public = evidence["Public neutral multiphase admission checker"]
    assert public["command"] == (
        "uv run --no-sync python scripts/validation/check_generalized_phase_set.py "
        "--json --phase-kinds liquid,liquid,liquid --run-route-refinement "
        "--require-route-refinement --require-public-admission --require-complete"
    )
    assert "public_multiphase_route" in public["result_requirement"]
    assert "neutral_multiphase_nonassoc selector family" in public["result_requirement"]
    assert "generalized_phase_set_public_admission_checker" in public["result_requirement"]
    assert "strict_multiphase_fugacity_residual_route" in generalized["required_gates"]
    assert "exact_reduced_fugacity_residual_derivatives" in generalized["required_gates"]
    assert "stage_ii_candidate_set_replay_consumed" in generalized["required_gates"]
    assert "public_multiphase_route" in generalized["required_gates"]
    assert "generalized_phase_set_public_admission_checker" in generalized["required_gates"]


def test_benchmark_cases_reference_descriptive_family_labels() -> None:
    family_labels = set(_family_by_label())

    for row in _family_rows():
        assert row["reference_cases"], row["family_label"]
        assert FORBIDDEN_NUMERIC_ROW_RE.search(row["family_label"]) is None
        for case in row["reference_cases"]:
            assert case["case_label"], row["family_label"]
            assert case["evidence_tier"] in _registry()["evidence_tiers"], case["case_label"]
            assert case["fixture_status"], case["case_label"]
            assert case["acceptance_checks"], case["case_label"]

    for case in _registry()["benchmark_cases"]:
        assert set(case["family_labels"]) <= family_labels, case["case_label"]
