from __future__ import annotations

import pytest
from regression_support.native_problem_cases import native_core


@pytest.mark.parametrize(
    ("termination_type", "accepted"),
    (
        ("CONVERGENCE", True),
        ("USER_SUCCESS", True),
        ("NO_CONVERGENCE", False),
        ("FAILURE", False),
        ("USER_FAILURE", False),
    ),
)
def test_only_explicit_success_termination_enums_are_accepted(
    termination_type: str,
    accepted: bool,
) -> None:
    predicate = native_core()._regression_acceptance_from_summary

    assert predicate(termination_type, True, 10.0, 9.0, True, True) is accepted


@pytest.mark.parametrize("termination_type", ("CONVERGENCE", "USER_SUCCESS"))
def test_accepted_enum_still_requires_usable_finite_complete_solution(termination_type: str) -> None:
    predicate = native_core()._regression_acceptance_from_summary

    assert predicate(termination_type, False, 10.0, 9.0, True, True) is False
    assert predicate(termination_type, True, 10.0, 9.0, False, True) is False
    assert predicate(termination_type, True, 10.0, 9.0, True, False) is False


@pytest.mark.parametrize("termination_type", ("NO_CONVERGENCE", "FAILURE", "USER_FAILURE"))
def test_nonincreasing_cost_cannot_rescue_a_rejected_enum(termination_type: str) -> None:
    assert (
        native_core()._regression_acceptance_from_summary(
            termination_type,
            True,
            10.0,
            0.0,
            True,
            True,
        )
        is False
    )
