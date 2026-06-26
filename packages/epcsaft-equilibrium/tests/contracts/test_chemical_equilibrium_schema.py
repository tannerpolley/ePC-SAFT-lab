from __future__ import annotations

import numpy as np
import pytest

from epcsaft import InputError
from epcsaft_equilibrium.chemical_equilibrium import (
    ChemicalReaction,
    ChemicalSpecies,
    compile_reaction_set,
)


def test_neutral_reaction_set_compiles_conservation_basis() -> None:
    compiled = compile_reaction_set(
        species=[
            ChemicalSpecies("H2", {"H": 2.0}),
            ChemicalSpecies("O2", {"O": 2.0}),
            ChemicalSpecies("H2O", {"H": 2.0, "O": 1.0}),
        ],
        reactions=[ChemicalReaction("water_formation", {"H2": -2.0, "O2": -1.0, "H2O": 2.0})],
        feed_amounts={"H2": 2.0, "O2": 1.0, "H2O": 0.0},
    )

    assert compiled.species_labels == ("H2", "O2", "H2O")
    assert compiled.conservation_labels == ("H", "O")
    assert compiled.reaction_labels == ("water_formation",)
    assert compiled.stoichiometric_matrix.tolist() == [[-2.0, -1.0, 2.0]]
    assert compiled.reaction_rank == 1
    assert compiled.diagnostics["rank_deficient_reactions"] is False
    assert np.allclose(compiled.conservation_matrix @ compiled.stoichiometric_matrix.T, 0.0)
    assert compiled.conservation_totals.tolist() == [4.0, 2.0]


def test_charged_reaction_set_adds_charge_balance_basis() -> None:
    compiled = compile_reaction_set(
        species=[
            ChemicalSpecies("H2O", {"H": 2.0, "O": 1.0}, charge=0.0),
            ChemicalSpecies("H+", {"H": 1.0}, charge=1.0),
            ChemicalSpecies("OH-", {"H": 1.0, "O": 1.0}, charge=-1.0),
        ],
        reactions=[ChemicalReaction("water_autoionization", {"H2O": -1.0, "H+": 1.0, "OH-": 1.0})],
        feed_amounts={"H2O": 1.0, "H+": 0.0, "OH-": 0.0},
    )

    assert compiled.conservation_labels == ("H", "O", "charge")
    assert compiled.charge_vector.tolist() == [0.0, 1.0, -1.0]
    assert compiled.conservation_matrix[-1].tolist() == compiled.charge_vector.tolist()
    assert np.allclose(compiled.conservation_matrix @ compiled.stoichiometric_matrix.T, 0.0)


def test_rank_deficient_reactions_report_deterministic_diagnostics() -> None:
    compiled = compile_reaction_set(
        species=[
            ChemicalSpecies("A", {"X": 1.0}),
            ChemicalSpecies("B", {"X": 1.0}),
            ChemicalSpecies("C", {"X": 1.0}),
        ],
        reactions=[
            ChemicalReaction("a_to_b", {"A": -1.0, "B": 1.0}),
            ChemicalReaction("b_to_c", {"B": -1.0, "C": 1.0}),
            ChemicalReaction("a_to_c", {"A": -1.0, "C": 1.0}),
        ],
        feed_amounts={"A": 1.0, "B": 0.0, "C": 0.0},
    )

    assert compiled.reaction_count == 3
    assert compiled.reaction_rank == 2
    assert compiled.diagnostics["rank_deficient_reactions"] is True
    assert compiled.diagnostics["dependent_reaction_count"] == 1


def test_unknown_species_fail_before_solver_entry() -> None:
    with pytest.raises(InputError, match="unknown species"):
        compile_reaction_set(
            species=[ChemicalSpecies("A", {"X": 1.0}), ChemicalSpecies("B", {"X": 1.0})],
            reactions=[ChemicalReaction("unknown", {"A": -1.0, "C": 1.0})],
            feed_amounts={"A": 1.0, "B": 0.0},
        )


def test_impossible_feed_amounts_fail_before_solver_entry() -> None:
    with pytest.raises(InputError, match="feed amount"):
        compile_reaction_set(
            species=[ChemicalSpecies("A", {"X": 1.0}), ChemicalSpecies("B", {"X": 1.0})],
            reactions=[ChemicalReaction("a_to_b", {"A": -1.0, "B": 1.0})],
            feed_amounts={"A": 1.0, "B": -1.0},
        )


def test_duplicate_reactions_fail_before_solver_entry() -> None:
    with pytest.raises(InputError, match="duplicate reaction"):
        compile_reaction_set(
            species=[ChemicalSpecies("A", {"X": 1.0}), ChemicalSpecies("B", {"X": 1.0})],
            reactions=[
                ChemicalReaction("a_to_b", {"A": -1.0, "B": 1.0}),
                ChemicalReaction("a_to_b_copy", {"A": -1.0, "B": 1.0}),
            ],
            feed_amounts={"A": 1.0, "B": 0.0},
        )
