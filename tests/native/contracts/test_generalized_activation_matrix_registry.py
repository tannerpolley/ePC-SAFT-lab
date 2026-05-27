from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "docs" / "roadmaps" / "equilibrium_benchmark_registry.yaml"
GFPE_PATH = REPO_ROOT / "docs" / "roadmaps" / "generalized_fluid_phase_equilibrium.md"
STAGE_PLAN_PATH = REPO_ROOT / "docs" / "roadmaps" / "stage_by_stage_implementation_plan.md"

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
    assert "roadmap labels only" in gfpe_text


def test_gfpe_plan_is_pretreatment_centered() -> None:
    stage_text = STAGE_PLAN_PATH.read_text(encoding="utf-8")

    assert "GFPE is the organizing spine for this file." in stage_text
    assert "`FULL_ROADMAP.md` is a boundary" in stage_text
    assert "document: it explains package identity" in stage_text
    assert (
        "Package-wide milestones are intentionally not used as stage names." in stage_text
    )
    assert "Pereira 2012 System III remains HELD/SAFT-VR literature context" in stage_text
    assert "first neutral proof target must be a source-backed ePC-SAFT-compatible" in stage_text
    assert "## GFPE Pretreatment Pipeline" in stage_text
    assert "public request\n  -> request-shape record" in stage_text
    assert "parameter and EOS-contribution readiness record" in stage_text
    assert "bounds, scaling, and transform record" in stage_text
    assert "## Stage 8 - Shared NLP And Ipopt Infrastructure Gate" in stage_text
    assert "complete Ipopt numerics gate" in stage_text
    assert "`proof`, `continuation_trace`, `held_refinement`, and `diagnostic`" in stage_text
    assert "`profile_exact_hessian_gate`" in stage_text
    assert "Stage 9 cannot use real-mixture HELD proof cases" in stage_text
    assert "## Stage 17 - Registry, Capability, And Benchmark Closure" in stage_text
    assert stage_text.index("## Stage 9 - Continuous TPD And HELD Stage Ladder") < stage_text.index(
        "## Stage 10 - Neutral TP Flash Source-Backed Proof"
    )
    assert stage_text.index("## Stage 10 - Neutral TP Flash Source-Backed Proof") < stage_text.index(
        "## Stage 11 - Derived Boundary Workflows And Diagram Traces"
    )


def test_no_generalized_family_claims_production_before_held_gates() -> None:
    for row in _family_rows():
        assert row["activation_status"] == "planned_not_public", row["family_label"]
        assert row["production_exposed"] is False, row["family_label"]
        assert "required_gates" in row, row["family_label"]

    neutral = _family_by_label()["PE-Neutral TP Flash"]
    assert "continuous_tpd_minimization" in neutral["required_gates"]
    assert "held_stage_ii_dual_phase_discovery" in neutral["required_gates"]
    assert (
        neutral["phase_discovery_status"]
        == "continuous_tpd_stage_i_stage_ii_candidate_bound_audit_closed_current_fixture"
    )
    assert neutral["stage9_status"]["deterministic_screening"].endswith("not_full_held")
    assert (
        neutral["stage9_status"]["continuous_tpd_minimization"]
        == "implemented_neutral_coordinate_search_convergence_required"
    )
    expected_stage_i_status = "implemented_neutral_multi_start_convergence_required"
    assert neutral["stage9_status"]["held_stage_i_stability"] == expected_stage_i_status
    assert (
        neutral["stage9_status"]["held_stage_ii_dual_phase_discovery"]
        == "current_neutral_candidate_bound_audit_closed_pending_full_dual_loop_generalization"
    )
    assert (
        neutral["stage9_status"]["held_stage_iii_ipopt_refinement"]
        == "current_route_refinement_verified_with_ipopt_success"
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
        assert "ePC-SAFT-compatible neutral mixture" in row["shared_mixture_policy"], label
        assert "Pereira 2012 System III remains HELD/SAFT-VR context" in row["shared_mixture_policy"], label
        assert "contract-only" in row["diagnostic_policy"], label
        assert "explicit sweep opt-in" in row["diagnostic_policy"], label
        assert "Ipopt success" in row["strict_convergence_gate"], label
        assert "no max_iterations_exceeded seed attempt" in row["strict_convergence_gate"], label
        assert "strict_ipopt_convergence" in row["acceptance_checks"], label
        assert "no_implicit_route_sweep" in row["acceptance_checks"], label

    assert subworkflows["Bubble point"]["current_convergence_status"] == (
        "stage11_current_fixture_strict_trace_verified"
    )
    assert subworkflows["Dew point"]["current_convergence_status"] == (
        "stage11_current_fixture_strict_trace_verified"
    )
    assert subworkflows["Cloud point"]["current_convergence_status"] == "planned_not_executable"
    assert subworkflows["Shadow point"]["current_convergence_status"] == "planned_not_executable"


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


def test_benchmark_cases_reference_descriptive_family_labels() -> None:
    family_labels = set(_family_by_label())

    for row in _family_rows():
        assert row["proof_cases"], row["family_label"]
        assert FORBIDDEN_NUMERIC_ROW_RE.search(row["family_label"]) is None
        for proof in row["proof_cases"]:
            assert proof["case_label"], row["family_label"]
            assert proof["evidence_tier"] in _registry()["evidence_tiers"], proof["case_label"]
            assert proof["fixture_status"], proof["case_label"]
            assert proof["acceptance_checks"], proof["case_label"]

    for case in _registry()["benchmark_cases"]:
        assert set(case["family_labels"]) <= family_labels, case["case_label"]
