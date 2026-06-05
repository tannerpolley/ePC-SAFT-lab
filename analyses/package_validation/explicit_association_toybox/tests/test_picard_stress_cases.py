from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.picard_stress_cases import (
    load_picard_stress_specs,
    materialize_picard_stress_cases,
)


def test_picard_stress_specs_cover_required_case_families() -> None:
    specs = load_picard_stress_specs()
    families = {spec.case_family for spec in specs}

    assert {
        "pure_self_association",
        "associating_plus_inert",
        "unequal_associating_binary",
        "cross_association",
        "water_like_strong_association",
        "asymmetric_composition",
    }.issubset(families)


def test_picard_stress_cases_materialize_axes_and_roles() -> None:
    cases = materialize_picard_stress_cases()

    assert cases
    assert all(case.case_id for case in cases)
    assert all(case.decision_role for case in cases)
    assert all(case.density > 0.0 for case in cases)
    assert all(case.temperature > 0.0 for case in cases)
    assert all(case.strength_scale >= 0.0 for case in cases)
    assert {case.axis_id for case in cases} >= {"density", "temperature", "association_strength"}
