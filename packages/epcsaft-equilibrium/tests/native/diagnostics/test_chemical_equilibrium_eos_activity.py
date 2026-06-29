from __future__ import annotations

import math

import epcsaft
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
