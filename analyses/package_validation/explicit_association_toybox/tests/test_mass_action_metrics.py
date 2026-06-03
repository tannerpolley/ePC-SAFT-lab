from __future__ import annotations

import numpy as np

from analyses.package_validation.explicit_association_toybox.scripts.association_models import (
    AssociationSystem,
    association_helmholtz,
    mass_action_residual,
)
from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import (
    solve_exact_site_fractions,
    stable_two_class_2b_solution,
)


def test_symmetric_2b_formula_satisfies_mass_action() -> None:
    system = AssociationSystem(
        component_count=1,
        site_component_index=np.array([0, 0], dtype=int),
        site_kind=("D", "A"),
        active_pairs=((0, 1), (1, 0)),
    )
    density = 0.25
    composition = np.array([1.0])
    delta = system.delta_matrix(strength=4.0)

    xa = stable_two_class_2b_solution(density=density, x_assoc=composition[0], delta_da=delta[0, 1])

    residual = mass_action_residual(xa, density=density, x_assoc=system.x_assoc(composition), delta=delta)
    assert np.linalg.norm(residual, ord=np.inf) < 1.0e-12


def test_exact_solver_returns_bounded_site_fractions_and_helmholtz() -> None:
    system = AssociationSystem(
        component_count=2,
        site_component_index=np.array([0, 0], dtype=int),
        site_kind=("D", "A"),
        active_pairs=((0, 1), (1, 0)),
    )
    density = 0.1
    composition = np.array([0.5, 0.5])
    delta = system.delta_matrix(strength=10.0)

    result = solve_exact_site_fractions(
        density=density,
        x_assoc=system.x_assoc(composition),
        delta=delta,
    )

    assert result.converged is True
    assert result.residual_norm <= 1.0e-10
    assert np.all(result.xa > 0.0)
    assert np.all(result.xa <= 1.0)
    assert association_helmholtz(result.xa, composition, system.site_component_index) <= 0.0
