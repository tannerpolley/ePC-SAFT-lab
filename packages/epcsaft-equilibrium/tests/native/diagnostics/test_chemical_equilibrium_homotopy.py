from __future__ import annotations

import math

import pytest
from epcsaft_equilibrium._native import extension_native_core
from epcsaft_equilibrium.chemical_equilibrium import (
    ChemicalReaction,
    ChemicalSpecies,
    EquilibriumConstantRecord,
    StandardStateRecord,
    build_standard_state_registry,
    compile_reaction_set,
)

_core = extension_native_core()

pytestmark = pytest.mark.native_contract


def _require_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")


def _ab_payload(log_k: float):
    standard_state = StandardStateRecord(
        label="mole_fraction_standard_state",
        activity_convention="mole_fraction_activity",
        temperature_K=298.15,
        pressure_Pa=101325.0,
    )
    compiled = compile_reaction_set(
        species=[
            ChemicalSpecies("A", {"X": 1.0}),
            ChemicalSpecies("B", {"X": 1.0}),
        ],
        reactions=[ChemicalReaction("a_to_b", {"A": -1.0, "B": 1.0})],
        feed_amounts={"A": 1.0, "B": 0.0},
    )
    registry = build_standard_state_registry(
        [
            EquilibriumConstantRecord(
                reaction_label="a_to_b",
                value=log_k,
                form="ln_K",
                units="dimensionless",
                standard_state=standard_state,
                source="native homotopy contract fixture",
                source_constant_label="ln_K",
            )
        ]
    )
    return compiled.to_native_payload(), registry.to_native_payload()


def _solve_without_seed(log_k: float) -> dict[str, object]:
    schema, standard_states = _ab_payload(log_k)
    return _core._native_chemical_equilibrium_nlp_activation(
        schema,
        standard_states,
        [],
        300,
        1.0e-10,
        0.0,
        "auto",
        20,
        1.0e-9,
        1.0e-8,
        None,
    )


def _assert_no_oracle_final_proof(result: dict[str, object]) -> None:
    initialization = result["initialization"]
    continuation = result["continuation"]

    assert initialization["seed_source"] == "max_min_feasible_interior"
    assert initialization["source_oracle_initial_amounts"] is False
    assert initialization["feasible_initialization"]["accepted"] is True
    assert continuation["direct_final_proof_attempted"] is True
    assert continuation["final_proof_status"] == "accepted"
    assert continuation["final_lambda"] == pytest.approx(1.0)
    assert continuation["lambda_values"][-1] == pytest.approx(1.0)
    assert continuation["stage_count"] == len(continuation["trace"])
    if continuation["direct_final_proof_accepted"]:
        assert continuation["lambda_values"] == pytest.approx([1.0])
        assert continuation["stage_count"] == 0
    else:
        assert continuation["lambda_values"][0] == pytest.approx(0.0)
        assert continuation["stage_count"] >= 3
        assert continuation["trace"][-1]["final_proof"] is True
        assert all(stage["final_proof"] is False for stage in continuation["trace"][:-1])


def test_ce_k_scaling_solves_ab_without_source_oracle_seed() -> None:
    _require_ipopt()

    result = _solve_without_seed(math.log(3.0))

    assert result["accepted"] is True
    _assert_no_oracle_final_proof(result)
    assert result["amounts"] == pytest.approx([0.25, 0.75], abs=1.0e-7)
    assert result["balance_inf_norm"] < 1.0e-9
    assert result["reaction_stationarity_inf_norm"] < 1.0e-8


def test_ce_k_scaling_solves_tiny_species_without_source_oracle_seed() -> None:
    _require_ipopt()

    result = _solve_without_seed(10.0)

    assert result["accepted"] is True
    _assert_no_oracle_final_proof(result)
    assert result["amounts"][0] < 1.0e-4
    assert result["amounts"][1] == pytest.approx(1.0, abs=1.0e-4)
    assert result["balance_inf_norm"] < 1.0e-9
    assert result["reaction_stationarity_inf_norm"] < 1.0e-7
