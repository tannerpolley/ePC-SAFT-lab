from __future__ import annotations

import math
from dataclasses import fields

import numpy as np
import pytest

import epcsaft
from tests.api.reactive.reactive_speciation_cases import (
    _assert_reactive_speciation_native_ipopt_dependency_required,
    _native_ipopt_compiled,
    _salt_speciation_mixture,
)


@pytest.mark.parametrize("standard_state", ["ideal_mole_fraction", "concentration", "mole_fraction_activity"])
def test_reaction_definition_accepts_supported_standard_states(standard_state: str) -> None:
    reaction = epcsaft.ReactionDefinition(
        stoichiometry={"NaCl": -1.0, "Na+": 1.0, "Cl-": 1.0},
        log_equilibrium_constant=0.0,
        standard_state=standard_state,
    )

    assert reaction.standard_state == standard_state

def test_reaction_definition_rejects_unknown_standard_state() -> None:
    with pytest.raises(epcsaft.InputError, match=r"ReactionDefinition\.standard_state"):
        epcsaft.ReactionDefinition(
            stoichiometry={"NaCl": -1.0, "Na+": 1.0, "Cl-": 1.0},
            log_equilibrium_constant=0.0,
            standard_state="unknown_basis",
        )
