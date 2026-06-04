from __future__ import annotations

import numpy as np

from analyses.package_validation.explicit_association_toybox.scripts.association_models import (
    AssociationSystem,
    mass_action_residual,
)
from analyses.package_validation.explicit_association_toybox.scripts.closure_models import (
    evaluate_closure,
)
from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import (
    solve_exact_site_fractions,
)


def _system() -> AssociationSystem:
    return AssociationSystem(
        component_count=1,
        site_component_index=np.array([0, 0], dtype=int),
        site_kind=("D", "A"),
        active_pairs=((0, 1), (1, 0)),
    )


def test_exact_2b_reduction_matches_exact_symmetric_2b_baseline() -> None:
    system = _system()
    density = 0.2
    composition = np.array([1.0])
    delta = system.delta_matrix(strength=3.0)
    exact = solve_exact_site_fractions(density=density, x_assoc=system.x_assoc(composition), delta=delta)

    closure = evaluate_closure(
        "exact_2b_reduction",
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )

    np.testing.assert_allclose(closure.xa, exact.xa, atol=1.0e-12, rtol=1.0e-12)
    assert closure.association_model == "implicit_exact"
    assert closure.exact_derivative_of == "exact_mass_action"


def test_approximate_closures_are_bounded_and_labeled() -> None:
    system = _system()
    density = 0.2
    composition = np.array([1.0])
    delta = system.delta_matrix(strength=3.0)

    name = "damped_picard_7_05"
    closure = evaluate_closure(name, system=system, density=density, composition=composition, delta=delta)
    assert np.all(closure.xa > 0.0)
    assert np.all(closure.xa <= 1.0)
    assert closure.association_model == "explicit_approx"
    assert closure.exact_derivative_of == "approximate_association_closure"
    residual = mass_action_residual(closure.xa, density=density, x_assoc=system.x_assoc(composition), delta=delta)
    assert np.isfinite(np.linalg.norm(residual, ord=np.inf))
