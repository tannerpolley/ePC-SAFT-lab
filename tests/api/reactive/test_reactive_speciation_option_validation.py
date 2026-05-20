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


def test_reactive_speciation_options_public_surface_is_current_fields() -> None:
    assert {field.name for field in fields(epcsaft.ReactiveSpeciationOptions)} == {
        "max_iterations",
        "tolerance",
        "min_mole_fraction",
        "jacobian_backend",
        "solver_backend",
        "hessian_mode",
        "ipopt_iteration_history_limit",
        "ipopt_linear_solver",
        "ipopt_acceptable_tolerance",
        "ipopt_constraint_violation_tolerance",
        "ipopt_dual_infeasibility_tolerance",
        "ipopt_complementarity_tolerance",
        "continuation_state",
        "phase",
        "error_mode",
        "activity_output",
        "mass_tolerance",
        "charge_tolerance",
        "reaction_tolerance",
    }

@pytest.mark.parametrize(
    ("options", "message"),
    [
        (epcsaft.ReactiveSpeciationOptions(solver_backend="python_ipopt"), "solver_backend"),
        (epcsaft.ReactiveSpeciationOptions(jacobian_backend="autodiff"), "jacobian_backend"),
        (epcsaft.ReactiveSpeciationOptions(hessian_mode="unsupported-mode"), "hessian_mode"),
        (epcsaft.ReactiveSpeciationOptions(ipopt_iteration_history_limit=-1), "ipopt_iteration_history_limit"),
        (epcsaft.ReactiveSpeciationOptions(ipopt_iteration_history_limit=True), "ipopt_iteration_history_limit"),
        (epcsaft.ReactiveSpeciationOptions(ipopt_linear_solver=""), "ipopt_linear_solver"),
        (epcsaft.ReactiveSpeciationOptions(ipopt_acceptable_tolerance=0.0), "ipopt_acceptable_tolerance"),
        (
            epcsaft.ReactiveSpeciationOptions(ipopt_constraint_violation_tolerance=float("nan")),
            "ipopt_constraint_violation_tolerance",
        ),
        (
            epcsaft.ReactiveSpeciationOptions(ipopt_dual_infeasibility_tolerance=-1.0),
            "ipopt_dual_infeasibility_tolerance",
        ),
        (
            epcsaft.ReactiveSpeciationOptions(ipopt_complementarity_tolerance=True),
            "ipopt_complementarity_tolerance",
        ),
        (epcsaft.ReactiveSpeciationOptions(continuation_state=1), "continuation_state"),
    ],
)
def test_reactive_speciation_rejects_invalid_optimizer_options(options, message) -> None:
    species = ["H2O", "NaCl", "Na+", "Cl-"]
    mix = _salt_speciation_mixture()

    with pytest.raises(epcsaft.InputError, match=message):
        epcsaft.solve_reactive_speciation(
            species=species,
            mixture_factory=lambda x, T, P: mix,
            T=298.15,
            P=1.0e5,
            balances={
                "water_total": {"H2O": 1.0},
                "sodium_total": {"NaCl": 1.0, "Na+": 1.0},
                "chloride_total": {"NaCl": 1.0, "Cl-": 1.0},
            },
            totals={"water_total": 0.998, "sodium_total": 0.0015, "chloride_total": 0.0015},
            reactions=[
                epcsaft.ReactionDefinition(
                    stoichiometry={"NaCl": -1.0, "Na+": 1.0, "Cl-": 1.0},
                    log_equilibrium_constant=0.0,
                )
            ],
            initial_x=[0.998, 0.001, 0.0005, 0.0005],
            options=options,
        )

def test_reactive_speciation_rejects_incompatible_continuation_state_species_order() -> None:
    mix = epcsaft.ePCSAFTMixture.from_params(
        {
            "m": np.asarray([1.0, 1.0]),
            "s": np.asarray([3.0, 3.0]),
            "e": np.asarray([200.0, 200.0]),
        },
        species=["A", "B"],
    )

    with pytest.raises(epcsaft.InputError, match="species_order"):
        epcsaft.solve_reactive_speciation(
            species=["A", "B"],
            mixture_factory=lambda x, T, P: mix,
            T=298.15,
            P=1.0e5,
            balances={"total": {"A": 1.0, "B": 1.0}},
            totals={"total": 1.0},
            reactions=[
                epcsaft.ReactionDefinition(
                    {"A": -1.0, "B": 1.0},
                    log_equilibrium_constant=math.log(3.0),
                    standard_state="ideal_mole_fraction",
                )
            ],
            initial_x=[0.5, 0.5],
            options=epcsaft.ReactiveSpeciationOptions(
                solver_backend="ipopt",
                continuation_state={
                    "variables": [0.5, 0.5],
                    "species_order": ["B", "A"],
                },
            ),
        )
