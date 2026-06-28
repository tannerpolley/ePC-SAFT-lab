from __future__ import annotations

import math

import epcsaft_equilibrium
import pytest
from epcsaft import InputError, SolutionError
from epcsaft_equilibrium import workflows
from epcsaft_equilibrium.chemical_equilibrium import (
    ChemicalReaction,
    ChemicalSpecies,
    EquilibriumConstantRecord,
    StandardStateRecord,
)


def _species() -> list[ChemicalSpecies]:
    return [ChemicalSpecies("A", {"X": 1.0}), ChemicalSpecies("B", {"X": 1.0})]


def _reaction() -> list[ChemicalReaction]:
    return [ChemicalReaction("a_to_b", {"A": -1.0, "B": 1.0})]


def _constant() -> EquilibriumConstantRecord:
    standard_state = StandardStateRecord(
        label="mole_fraction_standard_state",
        activity_convention="mole_fraction_activity",
        temperature_K=298.15,
        pressure_Pa=101325.0,
    )
    return EquilibriumConstantRecord(
        reaction_label="a_to_b",
        value=math.log(3.0),
        form="ln_K",
        units="dimensionless",
        standard_state=standard_state,
        source="API contract fixture",
        source_constant_label="ln_K",
    )


def _native_payload() -> dict[str, object]:
    return {
        "native_binding": "_native_chemical_equilibrium_nlp_activation",
        "route": "reactive_speciation",
        "activation_compiler": "activation_plan",
        "thermodynamic_block": "homogeneous_chemical_equilibrium",
        "accepted": True,
        "amounts": [0.25, 0.75],
        "mole_fractions": [0.25, 0.75],
        "standard_mu_rt": [0.0, -math.log(3.0)],
        "objective_value": -0.5623351446188083,
        "balance_residuals": [0.0],
        "reaction_residuals": [0.0],
        "reaction_affinities": [0.0],
        "balance_inf_norm": 0.0,
        "reaction_stationarity_inf_norm": 0.0,
        "selector_contract": {
            "selector_family": "reactive_speciation",
            "route": "reactive_speciation",
            "activation_compiler": "activation_plan",
            "problem_name": "reactive_speciation_ideal_gibbs_nlp",
        },
        "activation": {"key": "reactive_speciation", "public_routes": []},
        "activation_plan": {
            "family_key": "reactive_speciation",
            "route": "reactive_speciation",
            "variable_blocks": ["species_amounts"],
            "constraint_blocks": ["conserved_balance"],
            "residual_blocks": ["conserved_balance", "reaction_stationarity"],
        },
        "variable_layout": {
            "variable_model": "single_phase_species_amounts",
            "phase_keys": ["homogeneous"],
            "phase_kinds": ["homogeneous"],
        },
        "solver_diagnostics": {
            "solver_backend": "ipopt",
            "solver_status": "success",
            "application_status": "solve_succeeded",
            "solver_accepted": True,
            "hessian_backend": "analytic",
        },
    }


def test_reactive_speciation_public_api_returns_ce_only_result_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_solve(compiled, standard_states, **kwargs):
        calls.append(
            {
                "species": compiled.species_labels,
                "reactions": compiled.reaction_labels,
                "standard_states": standard_states.reaction_labels,
                "initial_amounts": kwargs["initial_amounts"],
            }
        )
        return _native_payload()

    monkeypatch.setattr(workflows, "solve_chemical_equilibrium_nlp_activation", fake_solve)

    result = epcsaft_equilibrium.reactive_speciation(
        species=_species(),
        reactions=_reaction(),
        feed_amounts={"A": 1.0, "B": 0.0},
        equilibrium_constants=[_constant()],
        initial_amounts=[0.5, 0.5],
    )

    assert calls == [
        {
            "species": ("A", "B"),
            "reactions": ("a_to_b",),
            "standard_states": ("a_to_b",),
            "initial_amounts": [0.5, 0.5],
        }
    ]
    assert isinstance(result, epcsaft_equilibrium.ReactiveSpeciationResult)
    assert result.route == "reactive_speciation"
    assert result.problem_kind == "standalone_chemical_equilibrium"
    assert result.phase_scope == "homogeneous"
    assert result.coupling_scope == "chemical_equilibrium_only"
    assert result.species_labels == ("A", "B")
    assert result.reaction_labels == ("a_to_b",)
    assert result.amounts.tolist() == pytest.approx([0.25, 0.75])
    assert result.mole_fractions.tolist() == pytest.approx([0.25, 0.75])
    assert result.species_amounts == {"A": pytest.approx(0.25), "B": pytest.approx(0.75)}
    assert result.activities == {"A": pytest.approx(0.25), "B": pytest.approx(0.75)}
    assert set(result.reduced_chemical_potentials) == {"A", "B"}
    assert result.reaction_extents == {"a_to_b": pytest.approx(0.75)}
    assert result.balances == {"X": pytest.approx(0.0)}
    assert result.affinities == {"a_to_b": pytest.approx(0.0)}
    assert result.standard_state_metadata["a_to_b"]["activity_convention"] == "mole_fraction_activity"
    assert result.diagnostics["native_binding"] == "_native_chemical_equilibrium_nlp_activation"
    assert result.diagnostics["solver_backend"] == "ipopt"

    payload = result.to_dict()
    assert payload["route"] == "reactive_speciation"
    assert payload["capability_scope"] == "standalone_ce_only"
    assert payload["phase_scope"] == "homogeneous"
    assert payload["closed_surfaces"] == ["reactive_lle", "reactive_electrolyte_lle", "cpe"]
    assert "phases" not in payload


def test_reactive_speciation_rejects_alternate_native_or_route_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_solve(*_args, **_kwargs):
        payload = _native_payload()
        payload["native_binding"] = "_native_chemical_equilibrium_algorithm_lanes"
        return payload

    monkeypatch.setattr(workflows, "solve_chemical_equilibrium_nlp_activation", fake_solve)

    with pytest.raises(SolutionError, match="single activation-matrix NLP"):
        epcsaft_equilibrium.reactive_speciation(
            species=_species(),
            reactions=_reaction(),
            feed_amounts={"A": 1.0, "B": 0.0},
            equilibrium_constants=[_constant()],
            initial_amounts=[0.5, 0.5],
        )


def test_reactive_speciation_rejects_non_mole_fraction_activity_until_supported() -> None:
    fugacity = StandardStateRecord(
        label="fugacity_standard_state",
        activity_convention="fugacity",
        temperature_K=298.15,
        pressure_Pa=101325.0,
        standard_fugacity_Pa=101325.0,
    )

    with pytest.raises(InputError, match="mole_fraction_activity"):
        epcsaft_equilibrium.reactive_speciation(
            species=_species(),
            reactions=_reaction(),
            feed_amounts={"A": 1.0, "B": 0.0},
            equilibrium_constants=[
                EquilibriumConstantRecord(
                    reaction_label="a_to_b",
                    value=math.log(3.0),
                    form="ln_K",
                    units="dimensionless",
                    standard_state=fugacity,
                    source="API contract fixture",
                    source_constant_label="ln_K",
                )
            ],
            initial_amounts=[0.5, 0.5],
        )
