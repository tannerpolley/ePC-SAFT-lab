from __future__ import annotations

import epcsaft
import epcsaft_equilibrium.chemical_equilibrium as chemical_equilibrium
from epcsaft_equilibrium import Equilibrium


def test_equilibrium_import_is_owned_by_extension_package() -> None:
    assert not hasattr(epcsaft, "Equilibrium")
    assert Equilibrium.__module__.startswith("epcsaft_equilibrium")


def test_closed_chemical_equilibrium_has_no_public_named_solve_bypass() -> None:
    assert not hasattr(chemical_equilibrium, "solve_chemical_equilibrium_nlp_activation")
