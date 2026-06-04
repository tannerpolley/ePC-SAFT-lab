from __future__ import annotations

import numpy as np

from analyses.package_validation.explicit_association_toybox.scripts.association_models import mass_action_residual
from analyses.package_validation.explicit_association_toybox.scripts.closure_models import evaluate_closure
from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import (
    stable_two_class_2b_solution,
)
from analyses.package_validation.explicit_association_toybox.scripts.topology_reductions import (
    HUANG_RADOSZ_TOPOLOGIES,
    evaluate_topology_reduction,
    topology_system,
)


def test_huang_radosz_table_vii_reductions_satisfy_mass_action() -> None:
    density = 0.2
    strength = 3.0
    composition = np.array([1.0])

    assert set(HUANG_RADOSZ_TOPOLOGIES) == {"1", "2A", "2B", "3A", "3B", "4A", "4B", "4C"}

    for topology_type, topology in HUANG_RADOSZ_TOPOLOGIES.items():
        system = topology_system(topology)
        result = evaluate_topology_reduction(topology_type, density=density, strength=strength)
        residual = mass_action_residual(
            result.xa,
            density=density,
            x_assoc=system.x_assoc(composition),
            delta=system.delta_matrix(strength),
        )

        assert np.linalg.norm(residual, ord=np.inf) < 1.0e-11, topology_type
        assert result.source_formula_family == "huang_radosz_table_vii"
        assert result.derivation_family == "topology_reduction"
        assert result.comparison_role == "exact_topology_reduction"
        assert result.exactness_claim == "exact_under_table_vii_topology_assumptions"


def test_huang_radosz_2b_reduction_matches_exact_2b_for_one_component_da_topology() -> None:
    density = 0.2
    strength = 3.0
    composition = np.array([1.0])
    topology = HUANG_RADOSZ_TOPOLOGIES["2B"]
    system = topology_system(topology)

    result = evaluate_topology_reduction("2B", density=density, strength=strength)
    closure = evaluate_closure(
        "exact_2b_reduction",
        system=system,
        density=density,
        composition=composition,
        delta=system.delta_matrix(strength),
    )

    expected = stable_two_class_2b_solution(density=density, x_assoc=1.0, delta_da=strength)
    np.testing.assert_allclose(result.xa, expected, atol=1.0e-12, rtol=1.0e-12)
    np.testing.assert_allclose(result.xa, closure.xa, atol=1.0e-12, rtol=1.0e-12)
    assert result.derivation_relationship == "matches_exact_2b_reduction_when_one_associating_component_da"
