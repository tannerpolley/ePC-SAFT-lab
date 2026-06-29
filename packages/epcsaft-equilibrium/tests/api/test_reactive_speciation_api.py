from __future__ import annotations

import math

import epcsaft_equilibrium
import pytest
from epcsaft import InputError, SolutionError
from epcsaft_equilibrium import workflows
from epcsaft_equilibrium._native import extension_native_core
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


def _mea_standard_state() -> StandardStateRecord:
    return StandardStateRecord(
        label="smith_missen_mole_fraction_standard_state",
        activity_convention="mole_fraction_activity",
        temperature_K=313.15,
        pressure_Pa=101325.0,
        metadata={
            "source_project": "MEA-Thermodynamics",
            "source_module": "MEA.smith_missen.ideal_speciation",
            "temperature_label": "40 C",
        },
    )


def _mea_species() -> list[ChemicalSpecies]:
    return [
        ChemicalSpecies("CO2", {"C": 1.0, "O": 2.0}),
        ChemicalSpecies("MEA", {"C": 2.0, "H": 7.0, "N": 1.0, "O": 1.0}),
        ChemicalSpecies("H2O", {"H": 2.0, "O": 1.0}),
        ChemicalSpecies("MEAH+", {"C": 2.0, "H": 8.0, "N": 1.0, "O": 1.0}, charge=1.0),
        ChemicalSpecies("MEACOO-", {"C": 3.0, "H": 6.0, "N": 1.0, "O": 3.0}, charge=-1.0),
        ChemicalSpecies("HCO3-", {"H": 1.0, "C": 1.0, "O": 3.0}, charge=-1.0),
        ChemicalSpecies("CO3^2-", {"C": 1.0, "O": 3.0}, charge=-2.0),
        ChemicalSpecies("H3O+", {"H": 3.0, "O": 1.0}, charge=1.0),
        ChemicalSpecies("OH-", {"H": 1.0, "O": 1.0}, charge=-1.0),
    ]


def _mea_reactions() -> list[ChemicalReaction]:
    return [
        ChemicalReaction("R1_water_autoionization", {"H2O": -2.0, "H3O+": 1.0, "OH-": 1.0}),
        ChemicalReaction("R2_CO2_to_HCO3", {"CO2": -1.0, "H2O": -2.0, "HCO3-": 1.0, "H3O+": 1.0}),
        ChemicalReaction("R3_HCO3_to_CO3", {"H2O": -1.0, "HCO3-": -1.0, "CO3^2-": 1.0, "H3O+": 1.0}),
        ChemicalReaction("R4_MEACOO_hydrolysis", {"MEA": 1.0, "H2O": -1.0, "MEACOO-": -1.0, "HCO3-": 1.0}),
        ChemicalReaction("R5_MEAH_dissociation", {"MEA": 1.0, "H2O": -1.0, "MEAH+": -1.0, "H3O+": 1.0}),
    ]


def _mea_constants() -> list[EquilibriumConstantRecord]:
    standard_state = _mea_standard_state()
    ln_k_by_reaction = {
        "R1_water_autoionization": -39.20847211814555,
        "R2_CO2_to_HCO3": -18.52157205941222,
        "R3_HCO3_to_CO3": -27.55307337666852,
        "R4_MEACOO_hydrolysis": -6.79989583266805,
        "R5_MEAH_dissociation": -26.37413522909149,
    }
    return [
        EquilibriumConstantRecord(
            reaction_label=label,
            value=ln_k,
            form="ln_K",
            units="dimensionless",
            standard_state=standard_state,
            source="MEA-Thermodynamics Smith-Missen Phase 1 retained fixture",
            source_constant_label=label,
            metadata={"basis": "mole fraction", "temperature_K": 313.15},
        )
        for label, ln_k in ln_k_by_reaction.items()
    ]


_MEA_WATER_PER_AMINE = 7.909507954125047
_MEA_EXPECTED_MOLE_FRACTIONS = {
    0.1: {
        "CO2": 6.683924651954811e-09,
        "MEA": 0.08989223566464728,
        "H2O": 0.8873375669739914,
        "MEAH+": 0.011527775080012528,
        "MEACOO-": 0.010819632394452237,
        "HCO3-": 0.00011896575214617932,
        "CO3^2-": 0.00028535948338821623,
        "H3O+": 3.999178474611162e-13,
        "OH-": 1.845796703766678e-05,
    },
    0.4: {
        "CO2": 1.4322412188376851e-06,
        "MEA": 0.02419700925042081,
        "H2O": 0.88572243609252,
        "MEAH+": 0.04518349608467077,
        "MEACOO-": 0.042858977799977424,
        "HCO3-": 0.001747513447705002,
        "CO3^2-": 0.000287869765126298,
        "H3O+": 5.812652925262093e-12,
        "OH-": 1.265312548334571e-06,
    },
    0.8: {
        "CO2": 0.005192618263938971,
        "MEA": 0.00043545843921396094,
        "H2O": 0.8260154916473321,
        "MEAH+": 0.08422357694784907,
        "MEACOO-": 0.026997790877452618,
        "HCO3-": 0.057044328501079176,
        "CO3^2-": 9.072336914185697e-05,
        "H3O+": 5.614793231095988e-10,
        "OH-": 1.1392512989995421e-08,
    },
}


def _mea_initial_amounts(mole_fractions: dict[str, float]) -> list[float]:
    amine_fraction = mole_fractions["MEA"] + mole_fractions["MEAH+"] + mole_fractions["MEACOO-"]
    scale = 1.0 / amine_fraction
    return [mole_fractions[species.label] * scale for species in _mea_species()]


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
        "activation": {"key": "reactive_speciation", "public_routes": ["reactive_speciation"]},
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
        "initialization": {
            "seed_source": "max_min_feasible_interior",
            "source_oracle_initial_amounts": False,
            "feasible_initialization": {"accepted": True, "margin": 0.5},
        },
        "continuation": {
            "direct_final_proof_attempted": True,
            "direct_final_proof_accepted": True,
            "final_proof_status": "accepted",
            "final_lambda": 1.0,
            "lambda_values": [0.0, 0.5, 1.0],
            "stage_count": 3,
            "trace": [
                {"stage_id": "lambda_0", "parameter_value": 0.0, "final_proof": False},
                {"stage_id": "lambda_half", "parameter_value": 0.5, "final_proof": False},
                {"stage_id": "lambda_1", "parameter_value": 1.0, "final_proof": True},
            ],
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


def test_reactive_speciation_initial_amounts_are_optional_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_solve(compiled, standard_states, **kwargs):
        calls.append(
            {
                "species": compiled.species_labels,
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
    )

    assert calls == [
        {
            "species": ("A", "B"),
            "standard_states": ("a_to_b",),
            "initial_amounts": None,
        }
    ]
    assert result.diagnostics["initialization"]["seed_source"] == "max_min_feasible_interior"
    assert result.diagnostics["initialization"]["source_oracle_initial_amounts"] is False
    assert result.diagnostics["continuation"]["final_lambda"] == pytest.approx(1.0)
    assert result.diagnostics["continuation"]["trace"][-1]["final_proof"] is True


def test_reactive_speciation_explicit_seed_reports_source_oracle_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_solve(*_args, **_kwargs):
        payload = _native_payload()
        payload["initialization"] = {
            "seed_source": "caller_initial_amounts",
            "source_oracle_initial_amounts": True,
            "feasible_initialization": {"accepted": False},
        }
        payload["continuation"] = {
            "direct_final_proof_attempted": True,
            "direct_final_proof_accepted": True,
            "final_proof_status": "accepted",
            "final_lambda": 1.0,
            "lambda_values": [1.0],
            "stage_count": 0,
            "trace": [],
        }
        return payload

    monkeypatch.setattr(workflows, "solve_chemical_equilibrium_nlp_activation", fake_solve)

    result = epcsaft_equilibrium.reactive_speciation(
        species=_species(),
        reactions=_reaction(),
        feed_amounts={"A": 1.0, "B": 0.0},
        equilibrium_constants=[_constant()],
        initial_amounts=[0.5, 0.5],
    )

    assert result.diagnostics["initialization"]["seed_source"] == "caller_initial_amounts"
    assert result.diagnostics["initialization"]["source_oracle_initial_amounts"] is True
    assert result.diagnostics["continuation"]["lambda_values"] == (1.0,)


def test_reactive_speciation_rejects_invalid_explicit_seed_before_native(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_solve(*_args, **_kwargs):
        raise AssertionError("native solve should not be called for invalid explicit seed")

    monkeypatch.setattr(workflows, "solve_chemical_equilibrium_nlp_activation", fail_solve)

    with pytest.raises(InputError, match="initial_amounts"):
        epcsaft_equilibrium.reactive_speciation(
            species=_species(),
            reactions=_reaction(),
            feed_amounts={"A": 1.0, "B": 0.0},
            equilibrium_constants=[_constant()],
            initial_amounts=[0.0, 1.0],
        )


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


def test_reactive_speciation_rejects_reactive_phase_route_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_solve(*_args, **_kwargs):
        payload = _native_payload()
        payload["activation"] = {"key": "reactive_speciation", "public_routes": ["reactive_lle"]}
        return payload

    monkeypatch.setattr(workflows, "solve_chemical_equilibrium_nlp_activation", fake_solve)

    with pytest.raises(SolutionError, match="reactive phase routes"):
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


def test_reactive_speciation_solves_mea_co2_h2o_loading_sweep_against_retained_fixture() -> None:
    core = extension_native_core()
    if not core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    species = _mea_species()
    reactions = _mea_reactions()
    constants = _mea_constants()
    solver_options = epcsaft_equilibrium.EquilibriumSolverOptions(max_iterations=300, tolerance=1.0e-6)
    results = []

    for loading, expected in _MEA_EXPECTED_MOLE_FRACTIONS.items():
        result = epcsaft_equilibrium.reactive_speciation(
            species=species,
            reactions=reactions,
            feed_amounts={"MEA": 1.0, "H2O": _MEA_WATER_PER_AMINE, "CO2": loading},
            equilibrium_constants=constants,
            initial_amounts=_mea_initial_amounts(expected),
            solver_options=solver_options,
        )
        results.append(result)

        assert result.route == "reactive_speciation"
        assert result.problem_kind == "standalone_chemical_equilibrium"
        assert result.phase_scope == "homogeneous"
        assert result.coupling_scope == "chemical_equilibrium_only"
        assert result.diagnostics["native_binding"] == "_native_chemical_equilibrium_nlp_activation"
        assert result.diagnostics["solver_status"] == "success"
        assert result.diagnostics["application_status"] == "solve_succeeded"
        assert result.diagnostics["accepted"] is True
        assert result.balances == pytest.approx({key: 0.0 for key in ("C", "O", "H", "N", "charge")}, abs=1.0e-8)
        assert result.affinities == pytest.approx({reaction.label: 0.0 for reaction in reactions}, abs=1.0e-6)
        assert result.mole_fractions.tolist() == pytest.approx(
            [expected[label] for label in result.species_labels],
            rel=2.0e-5,
            abs=5.0e-10,
        )

        amounts = result.species_amounts
        co2_loading = (
            amounts["CO2"]
            + amounts["MEACOO-"]
            + amounts["HCO3-"]
            + amounts["CO3^2-"]
        ) / (amounts["MEA"] + amounts["MEAH+"] + amounts["MEACOO-"])
        charge = (
            amounts["MEAH+"]
            + amounts["H3O+"]
            - amounts["MEACOO-"]
            - amounts["HCO3-"]
            - 2.0 * amounts["CO3^2-"]
            - amounts["OH-"]
        )
        assert co2_loading == pytest.approx(loading, abs=1.0e-8)
        assert charge == pytest.approx(0.0, abs=1.0e-8)

    assert [row.species_amounts["CO2"] for row in results] == sorted(row.species_amounts["CO2"] for row in results)
    assert [row.species_amounts["MEA"] for row in results] == sorted(
        (row.species_amounts["MEA"] for row in results),
        reverse=True,
    )
