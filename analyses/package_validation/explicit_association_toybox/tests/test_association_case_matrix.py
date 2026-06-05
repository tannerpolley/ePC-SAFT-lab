from __future__ import annotations

import numpy as np

from analyses.package_validation.explicit_association_toybox.scripts.association_case_matrix import (
    association_case_by_id,
    association_evidence_cases,
    jax_supported_cases,
)


def test_association_case_matrix_covers_required_topology_families() -> None:
    cases = association_evidence_cases()
    case_ids = {case.case_id for case in cases}

    assert {
        "pure_nonassociating_control",
        "pure_one_site_self",
        "pure_2b_self",
        "pure_3b_labeled",
        "pure_4c_labeled",
        "inert_plus_associating_binary",
        "two_self_associating_binary",
        "cross_associating_binary",
        "asymmetric_donor_acceptor_binary",
        "water_like_3b_topology",
        "water_like_4c_topology",
    } <= case_ids
    assert any(case.mixture_family == "binary_cross_associating" for case in cases)
    assert any(case.mixture_family == "pure_component_topology_fork" for case in cases)


def test_association_case_matrix_rows_have_consistent_shapes() -> None:
    for case in association_evidence_cases():
        assert np.isclose(float(np.sum(case.composition)), 1.0)
        assert case.density_grid
        assert case.temperature_grid
        if case.system is None:
            assert case.delta_matrix.shape == (0, 0)
            continue
        assert case.delta_matrix.shape == (case.system.site_count, case.system.site_count)
        assert case.composition.shape == (case.system.component_count,)
        assert case.strength_matrix_text()


def test_jax_supported_cases_exclude_nonassociating_control() -> None:
    cases = jax_supported_cases()

    assert cases
    assert {case.case_id for case in cases}.isdisjoint({"pure_nonassociating_control"})
    assert all(case.system is not None for case in cases)


def test_association_case_lookup_fails_loudly_for_unknown_case() -> None:
    assert association_case_by_id("pure_2b_self").topology_id == "2B"

    try:
        association_case_by_id("missing")
    except ValueError as exc:
        assert "Unknown association evidence case_id" in str(exc)
    else:
        raise AssertionError("unknown case lookup should fail")
