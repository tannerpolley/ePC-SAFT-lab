from __future__ import annotations

import numpy as np
import pytest

from analyses.package_validation.explicit_association_toybox.scripts.association_models import AssociationSystem
from analyses.package_validation.explicit_association_toybox.scripts.derivative_agreement import centered_slope
from analyses.package_validation.explicit_association_toybox.scripts.implicit_sensitivity import (
    exact_binary_composition_sensitivity,
    exact_density_sensitivity,
    exact_strength_sensitivity,
    mass_action_jacobian,
)
from analyses.package_validation.explicit_association_toybox.scripts.propagation_evidence import (
    exact_association_value,
)


def _pure_2b_system() -> AssociationSystem:
    return AssociationSystem(
        component_count=1,
        site_component_index=np.array([0, 0], dtype=int),
        site_kind=("D", "A"),
        active_pairs=((0, 1), (1, 0)),
    )


def _binary_cross_system() -> AssociationSystem:
    return AssociationSystem(
        component_count=2,
        site_component_index=np.array([0, 1], dtype=int),
        site_kind=("D", "A"),
        active_pairs=((0, 1), (1, 0)),
    )


def test_mass_action_jacobian_matches_finite_difference_columns() -> None:
    system = _pure_2b_system()
    density = 0.05
    composition = np.array([1.0], dtype=float)
    delta = system.delta_matrix(10.0)
    exact, _, _ = exact_association_value(
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )

    jacobian = mass_action_jacobian(
        xa=exact.xa,
        density=density,
        x_assoc=system.x_assoc(composition),
        delta=delta,
    )

    step = 1.0e-6
    for column in range(system.site_count):
        perturb = np.zeros(system.site_count, dtype=float)
        perturb[column] = step
        plus = _mass_action(system, exact.xa + perturb, density, composition, delta)
        minus = _mass_action(system, exact.xa - perturb, density, composition, delta)
        assert jacobian[:, column] == pytest.approx((plus - minus) / (2.0 * step), rel=1.0e-7)


def test_exact_density_sensitivity_matches_centered_value_slope() -> None:
    system = _pure_2b_system()
    density = 0.05
    strength = 10.0
    composition = np.array([1.0], dtype=float)

    sensitivity = exact_density_sensitivity(
        system=system,
        density=density,
        composition=composition,
        delta=system.delta_matrix(strength),
    )
    slope = centered_slope(
        lambda value: _exact_a_assoc(system, value, composition, strength),
        base_value=density,
        step_size=density * 1.0e-4,
    )

    assert sensitivity.da_dtheta == pytest.approx(slope, rel=5.0e-6, abs=1.0e-8)
    assert sensitivity.mass_action_residual_inf <= 1.0e-10
    assert sensitivity.jacobian_condition_number >= 1.0


def test_exact_strength_sensitivity_matches_centered_value_slope() -> None:
    system = _pure_2b_system()
    density = 0.05
    strength = 10.0
    composition = np.array([1.0], dtype=float)

    sensitivity = exact_strength_sensitivity(
        system=system,
        density=density,
        composition=composition,
        delta=system.delta_matrix(strength),
        strength=strength,
    )
    slope = centered_slope(
        lambda value: _exact_a_assoc(system, density, composition, value),
        base_value=strength,
        step_size=strength * 1.0e-4,
    )

    assert sensitivity.da_dtheta == pytest.approx(slope, rel=5.0e-6, abs=1.0e-8)


def test_exact_binary_composition_sensitivity_matches_centered_value_slope() -> None:
    system = _binary_cross_system()
    density = 0.05
    strength = 10.0
    composition = np.array([0.35, 0.65], dtype=float)

    sensitivity = exact_binary_composition_sensitivity(
        system=system,
        density=density,
        composition=composition,
        delta=system.delta_matrix(strength),
    )
    slope = centered_slope(
        lambda x0: _exact_a_assoc(system, density, np.array([x0, 1.0 - x0], dtype=float), strength),
        base_value=float(composition[0]),
        step_size=1.0e-5,
    )

    assert sensitivity.da_dtheta == pytest.approx(slope, rel=5.0e-5, abs=1.0e-8)


def _exact_a_assoc(
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    strength: float,
) -> float:
    _, value, _ = exact_association_value(
        system=system,
        density=density,
        composition=composition,
        delta=system.delta_matrix(strength),
    )
    return value


def _mass_action(
    system: AssociationSystem,
    xa: np.ndarray,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> np.ndarray:
    from analyses.package_validation.explicit_association_toybox.scripts.association_models import (
        mass_action_residual,
    )

    return mass_action_residual(xa, density=density, x_assoc=system.x_assoc(composition), delta=delta)
