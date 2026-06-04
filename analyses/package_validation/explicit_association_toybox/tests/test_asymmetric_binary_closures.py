from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.asymmetric_binary_closures import (
    load_asymmetric_binary_cases,
    run_asymmetric_binary_closures,
)


def test_asymmetric_binary_cases_cover_required_roles() -> None:
    rows = load_asymmetric_binary_cases()
    roles = {row["case_role"] for row in rows}

    assert {
        "associating_plus_inert",
        "cross_associating_binary",
        "unequal_delta_binary",
        "non_equimolar_binary",
        "water_3b_4c_contrast",
    } <= roles


def test_asymmetric_binary_closure_rows_keep_required_columns() -> None:
    rows = run_asymmetric_binary_closures(closure_names=("damped_picard_7_05",))

    assert rows
    assert {
        "case_id",
        "case_role",
        "closure_name",
        "composition",
        "ares_assoc_rel_error",
        "mass_action_residual_inf",
        "exact_implicit_elapsed_seconds",
        "closure_elapsed_seconds",
        "evidence_band",
    } <= set(rows[0])
