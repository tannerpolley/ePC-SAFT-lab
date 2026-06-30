from __future__ import annotations

import math

import epcsaft
import numpy as np
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
from epcsaft.state.native_adapter import ePCSAFTMixture

_core = extension_native_core()

pytestmark = pytest.mark.native_contract


def _require_ipopt() -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")


def _mixture() -> epcsaft.Mixture:
    return epcsaft.Mixture(
        epcsaft.ParameterSet.from_dict(
            {
                "m": [1.0, 1.6069],
                "s": [3.7039, 3.5206],
                "e": [150.03, 191.42],
                "MW": [16.043e-3, 30.070e-3],
                "k_ij": [[0.0, 3.0e-4], [3.0e-4, 0.0]],
            },
            species=("A", "B"),
        )
    )


def _ionic_mixture() -> ePCSAFTMixture:
    temperature = 298.15
    water_segment_diameter = (
        2.7927 + 10.11 * math.exp(-0.01775 * temperature) - 1.417 * math.exp(-0.01146 * temperature)
    )
    return ePCSAFTMixture.from_params(
        {
            "MW": np.asarray([18.01528e-3, 22.98e-3, 35.45e-3]),
            "m": np.asarray([1.2047, 1.0, 1.0]),
            "s": np.asarray([water_segment_diameter, 2.8232, 2.7560]),
            "e": np.asarray([353.95, 230.0, 170.0]),
            "e_assoc": np.asarray([2425.7, 0.0, 0.0]),
            "vol_a": np.asarray([0.04509, 0.0, 0.0]),
            "assoc_scheme": ["2B", None, None],
            "z": np.asarray([0.0, 1.0, -1.0]),
            "dielc": np.asarray([78.09, 8.0, 8.0]),
            "d_born": np.asarray([0.0, 3.445, 4.1]),
            "f_solv": np.asarray([1.5, 1.0, 1.0]),
            "k_ij": np.asarray(
                [
                    [0.0, 0.0045, -0.25],
                    [0.0045, 0.0, 0.317],
                    [-0.25, 0.317, 0.0],
                ]
            ),
            "l_ij": np.zeros((3, 3)),
            "k_hb": np.zeros((3, 3)),
        },
        species=("water", "Na+", "Cl-"),
    )


def _eos_payload(log_k: float = math.log(3.0)):
    standard_state = StandardStateRecord(
        label="liquid_eos_x_phi",
        activity_convention="eos_x_phi",
        temperature_K=233.15,
        pressure_Pa=1_276_369.4735856401,
        eos_reference_phase="liquid",
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
                source="native EOS activity contract fixture",
                source_constant_label="ln_K",
            )
        ]
    )
    return compiled.to_native_payload(), registry.to_native_payload()


def _eos_gamma_payload():
    species = ("water", "Na+", "Cl-")
    target_mole_fractions = np.asarray([0.9998, 1.0e-4, 1.0e-4])
    mixture = _ionic_mixture()
    state = mixture.state(T=298.15, x=target_mole_fractions, P=1.0e5, phase="liq")
    gamma = state.activity_coefficient(species=species)
    log_activities = np.log(target_mole_fractions) + np.log([gamma[label] for label in species])
    log_k = float(2.0 * log_activities[0] - log_activities[1] - log_activities[2])
    standard_state = StandardStateRecord(
        label="liquid_eos_x_gamma",
        activity_convention="eos_x_gamma",
        temperature_K=298.15,
        pressure_Pa=1.0e5,
        eos_reference_phase="liquid",
    )
    compiled = compile_reaction_set(
        species=[
            ChemicalSpecies("water", {"X": 1.0, "charge": 0.0}, charge=0.0),
            ChemicalSpecies("Na+", {"X": 1.0, "charge": 1.0}, charge=1.0),
            ChemicalSpecies("Cl-", {"X": 1.0, "charge": -1.0}, charge=-1.0),
        ],
        reactions=[ChemicalReaction("ion_pair_to_water", {"water": 2.0, "Na+": -1.0, "Cl-": -1.0})],
        feed_amounts={
            "water": target_mole_fractions[0],
            "Na+": target_mole_fractions[1],
            "Cl-": target_mole_fractions[2],
        },
    )
    registry = build_standard_state_registry(
        [
            EquilibriumConstantRecord(
                reaction_label="ion_pair_to_water",
                value=log_k,
                form="ln_K",
                units="dimensionless",
                standard_state=standard_state,
                source="native EOS activity coefficient contract fixture",
                source_constant_label="ln_K",
            )
        ]
    )
    return (
        compiled.to_native_payload(),
        registry.to_native_payload(),
        mixture,
        target_mole_fractions,
        np.exp(log_activities),
    )


def test_native_ce_eos_x_phi_uses_cppad_fugacity_activity_objective() -> None:
    _require_ipopt()

    schema, standard_states = _eos_payload()
    result = _core._native_chemical_equilibrium_nlp_activation(
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
        eos_mixture=_mixture().native,
    )

    assert result["accepted"] is True
    assert result["activity_model"] == "eos_x_phi"
    assert result["activity_derivative_backend"] == "cppad_implicit"
    assert result["solver_diagnostics"]["hessian_backend"] == "cppad_phase_state_fugacity"
    context = result["eos_activity_context"]
    assert context["temperature_K"] == pytest.approx(233.15)
    assert context["pressure_Pa"] == pytest.approx(1_276_369.4735856401)
    assert context["reference_phase"] == "liquid"
    assert context["phase_kind"] == 0
    assert context["density_mol_m3"] > 0.0
    assert len(result["ln_activity_coefficients"]) == 2
    assert len(result["activities"]) == 2
    assert result["activities"][0] != pytest.approx(result["mole_fractions"][0], abs=1.0e-5)
    assert result["activities"][1] != pytest.approx(result["mole_fractions"][1], abs=1.0e-5)
    assert result["balance_inf_norm"] < 1.0e-9
    assert result["reaction_stationarity_inf_norm"] < 1.0e-8


def test_native_ce_eos_x_gamma_uses_cppad_activity_coefficient_objective() -> None:
    _require_ipopt()

    schema, standard_states, mixture, target_mole_fractions, target_activities = _eos_gamma_payload()
    result = _core._native_chemical_equilibrium_nlp_activation(
        schema,
        standard_states,
        target_mole_fractions.tolist(),
        300,
        1.0e-10,
        0.0,
        "auto",
        20,
        1.0e-9,
        1.0e-8,
        None,
        eos_mixture=mixture,
    )

    assert result["accepted"] is True
    assert result["activity_model"] == "eos_x_gamma"
    assert result["activity_derivative_backend"] == "cppad_implicit_activity_coefficient"
    assert result["solver_diagnostics"]["hessian_backend"] == "cppad_phase_state_activity_coefficient"
    assert result["mole_fractions"] == pytest.approx(target_mole_fractions, rel=1.0e-8, abs=1.0e-12)
    assert result["activities"] == pytest.approx(target_activities, rel=1.0e-8, abs=1.0e-12)
    assert result["balance_inf_norm"] < 1.0e-9
    assert result["reaction_stationarity_inf_norm"] < 1.0e-8


def test_native_ce_eos_x_phi_requires_native_mixture_context() -> None:
    _require_ipopt()

    schema, standard_states = _eos_payload()

    with pytest.raises(Exception, match="eos_x_phi"):
        _core._native_chemical_equilibrium_nlp_activation(
            schema,
            standard_states,
            [0.5, 0.5],
            100,
            1.0e-8,
            0.0,
            "auto",
            20,
            1.0e-9,
            1.0e-8,
            None,
        )
