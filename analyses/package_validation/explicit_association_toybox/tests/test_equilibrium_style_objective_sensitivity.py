from __future__ import annotations

import numpy as np
import pytest

from analyses.package_validation.explicit_association_toybox.scripts.equilibrium_style_objective_sensitivity import (
    local_objective_value,
    max_symmetric_matrix_abs_error,
)


def test_local_objective_value_combines_total_ares_and_pressure_proxy() -> None:
    assert local_objective_value(ares_total=2.0, pressure_proxy=3.0, pressure_weight=0.25) == pytest.approx(2.75)


def test_max_symmetric_matrix_abs_error() -> None:
    exact = np.array([[1.0, 0.5], [0.5, 2.0]])
    closure = np.array([[1.1, 0.4], [0.6, 1.8]])

    assert max_symmetric_matrix_abs_error(exact, closure) == pytest.approx(0.2)
