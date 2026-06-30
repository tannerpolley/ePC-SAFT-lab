from __future__ import annotations

import math

import epcsaft
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


def _eos_constant() -> EquilibriumConstantRecord:
    standard_state = StandardStateRecord(
        label="liquid_eos_x_phi_standard_state",
        activity_convention="eos_x_phi",
        temperature_K=233.15,
        pressure_Pa=1_276_369.4735856401,
        eos_reference_phase="liquid",
    )
    return EquilibriumConstantRecord(
        reaction_label="a_to_b",
        value=math.log(3.0),
        form="ln_K",
        units="dimensionless",
        standard_state=standard_state,
        source="API EOS activity contract fixture",
        source_constant_label="ln_K",
    )


def _eos_gamma_constant() -> EquilibriumConstantRecord:
    standard_state = StandardStateRecord(
        label="liquid_eos_x_gamma_standard_state",
        activity_convention="eos_x_gamma",
        temperature_K=233.15,
        pressure_Pa=1_276_369.4735856401,
        eos_reference_phase="liquid",
    )
    return EquilibriumConstantRecord(
        reaction_label="a_to_b",
        value=math.log(3.0),
        form="ln_K",
        units="dimensionless",
        standard_state=standard_state,
        source="API EOS activity coefficient contract fixture",
        source_constant_label="ln_K",
    )


def _two_component_parameter_set() -> epcsaft.ParameterSet:
    return epcsaft.ParameterSet.from_dict(
        {
            "m": [1.0, 1.6069],
            "s": [3.7039, 3.5206],
            "e": [150.03, 191.42],
            "MW": [16.043e-3, 30.070e-3],
            "k_ij": [[0.0, 3.0e-4], [3.0e-4, 0.0]],
        },
        species=("A", "B"),
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
        "proof_metrics": {
            "reaction_scaling_factors": [0.5],
            "reaction_row_norms": [math.sqrt(2.0)],
            "reaction_scaling_min": 0.5,
            "reaction_scaling_max": 0.5,
            "reaction_basis_condition_estimate": 1.0,
            "scaled_reaction_stationarity_inf_norm": 0.0,
            "unscaled_reaction_stationarity_inf_norm": 0.0,
            "proof_stationarity_norm": 0.0,
        },
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
    assert result.diagnostics["proof_metrics"]["reaction_scaling_factors"] == pytest.approx([0.5])
    assert result.diagnostics["proof_metrics"]["unscaled_reaction_stationarity_inf_norm"] == pytest.approx(
        result.diagnostics["reaction_stationarity_inf_norm"]
    )

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


def test_reactive_speciation_good_caller_seed_reports_seed_attempt_order() -> None:
    core = extension_native_core()
    if not core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    result = epcsaft_equilibrium.reactive_speciation(
        species=_species(),
        reactions=_reaction(),
        feed_amounts={"A": 1.0, "B": 0.0},
        equilibrium_constants=[_constant()],
        initial_amounts=[0.25, 0.75],
    )

    initialization = result.diagnostics["initialization"]
    assert initialization["seed_attempt_order"] == ("caller_initial_amounts",)
    assert initialization["accepted_seed_source"] == "caller_initial_amounts"
    assert initialization["caller_seed_final_proof_attempted"] is True
    assert initialization["caller_seed_final_proof_accepted"] is True
    assert initialization["caller_seed_escalated"] is False


def test_reactive_speciation_bad_positive_seed_escalates_to_ce_owned_initialization() -> None:
    core = extension_native_core()
    if not core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    poor_seed = [1.0e-300] * len(_mea_species())
    result = epcsaft_equilibrium.reactive_speciation(
        species=_mea_species(),
        reactions=_mea_reactions(),
        feed_amounts={
            "CO2": 0.8,
            "H2O": 6.0,
            "MEA": 1.0,
            "MEAH+": 1.0e-18,
            "MEACOO-": 1.0e-18,
            "HCO3-": 1.0e-18,
            "CO3^2-": 1.0e-18,
            "H3O+": 1.0e-18,
            "OH-": 1.0e-18,
        },
        equilibrium_constants=_mea_constants(),
        initial_amounts=poor_seed,
        solver_options=epcsaft_equilibrium.EquilibriumSolverOptions(max_iterations=600, tolerance=1.0e-8),
    )

    initialization = result.diagnostics["initialization"]
    assert initialization["seed_attempt_order"] == (
        "caller_initial_amounts",
        "max_min_feasible_interior",
    )
    assert initialization["accepted_seed_source"] == "max_min_feasible_interior"
    assert initialization["caller_seed_final_proof_attempted"] is True
    assert initialization["caller_seed_final_proof_accepted"] is False
    assert initialization["caller_seed_escalated"] is True
    assert initialization["source_oracle_initial_amounts"] is False
    assert result.diagnostics["balance_inf_norm"] < 1.0e-8
    assert result.diagnostics["reaction_stationarity_inf_norm"] < 1.0e-6


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


@pytest.mark.parametrize(
    ("payload_updates", "expected_failure_class"),
    [
        (
            {
                "initialization": {
                    "seed_source": "max_min_feasible_interior",
                    "source_oracle_initial_amounts": False,
                    "feasible_initialization": {
                        "accepted": False,
                        "rejection_reason": "extent_nullspace_conservation_residual",
                    },
                },
            },
            "infeasible_conservation",
        ),
        (
            {
                "initialization": {
                    "seed_source": "max_min_feasible_interior",
                    "source_oracle_initial_amounts": False,
                    "feasible_initialization": {
                        "accepted": False,
                        "rejection_reason": "initializer_solve_rejected",
                    },
                },
            },
            "initialization_failure",
        ),
        (
            {
                "solver_diagnostics": {
                    "solver_backend": "ipopt",
                    "solver_status": "restoration_failure",
                    "application_status": "ipopt_application_status_-2",
                    "solver_accepted": False,
                    "hessian_backend": "analytic",
                },
            },
            "ipopt_failure",
        ),
        (
            {
                "continuation": {
                    "direct_final_proof_attempted": True,
                    "direct_final_proof_accepted": False,
                    "final_proof_status": "rejected",
                    "final_lambda": 1.0,
                    "lambda_values": [1.0],
                    "stage_count": 0,
                    "trace": [],
                    "physical_proof_corrector": {
                        "attempted": True,
                        "accepted": False,
                        "status": "rejected_iteration_limit",
                        "rejection_reason": "rejected_iteration_limit",
                    },
                },
            },
            "proof_correction_failure",
        ),
        ({"reaction_stationarity_inf_norm": 1.0e-3}, "stationarity_failure"),
        ({"balance_inf_norm": 1.0e-3, "balance_residuals": [1.0e-3]}, "balance_failure"),
        (
            {
                "activity_model": "eos_x_gamma",
                "activity_derivative_backend": "cppad_phase_state_activity_coefficient",
                "solver_diagnostics": {
                    "solver_backend": "ipopt",
                    "solver_status": "restoration_failure",
                    "application_status": "ipopt_application_status_-2",
                    "solver_accepted": False,
                    "hessian_backend": "cppad_phase_state_activity_coefficient",
                },
            },
            "eos_activity_failure",
        ),
    ],
)
def test_reactive_speciation_classifies_native_failure_gate(
    monkeypatch: pytest.MonkeyPatch,
    payload_updates: dict[str, object],
    expected_failure_class: str,
) -> None:
    def merge_payload(base: dict[str, object], updates: dict[str, object]) -> dict[str, object]:
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                merge_payload(base[key], value)  # type: ignore[arg-type]
            else:
                base[key] = value
        return base

    def fake_solve(*_args, **_kwargs):
        payload = _native_payload()
        payload["accepted"] = False
        return merge_payload(payload, payload_updates)

    monkeypatch.setattr(workflows, "solve_chemical_equilibrium_nlp_activation", fake_solve)

    with pytest.raises(SolutionError) as exc_info:
        epcsaft_equilibrium.reactive_speciation(
            species=_species(),
            reactions=_reaction(),
            feed_amounts={"A": 1.0, "B": 0.0},
            equilibrium_constants=[_constant()],
            initial_amounts=[0.5, 0.5],
        )

    diagnostics = exc_info.value.diagnostics
    payload = fake_solve()
    assert diagnostics["failure_class"] == expected_failure_class
    assert diagnostics["failure_gate"]
    assert diagnostics["solver_status"] == payload["solver_diagnostics"]["solver_status"]


def test_reactive_speciation_rejects_non_mole_fraction_activity_until_supported() -> None:
    fugacity = StandardStateRecord(
        label="fugacity_standard_state",
        activity_convention="fugacity",
        temperature_K=298.15,
        pressure_Pa=101325.0,
        standard_fugacity_Pa=101325.0,
    )

    with pytest.raises(InputError, match="unsupported activity convention") as exc_info:
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
    assert exc_info.value.diagnostics["failure_class"] == "unsupported_standard_state_request"


def test_reactive_speciation_rejects_eos_x_phi_without_eos_mixture() -> None:
    with pytest.raises(InputError, match="eos_mixture"):
        epcsaft_equilibrium.reactive_speciation(
            species=_species(),
            reactions=_reaction(),
            feed_amounts={"A": 1.0, "B": 0.0},
            equilibrium_constants=[_eos_constant()],
            initial_amounts=[0.5, 0.5],
        )


def test_reactive_speciation_passes_eos_context_to_native(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_solve(compiled, standard_states, **kwargs):
        captured["species"] = compiled.species_labels
        captured["standard_states"] = standard_states.reaction_labels
        captured["eos_mixture"] = kwargs["eos_mixture"]
        payload = _native_payload()
        payload["activity_model"] = "eos_x_phi"
        payload["activity_derivative_backend"] = "cppad_implicit"
        payload["ln_activity_coefficients"] = [0.01, -0.02]
        payload["activities"] = [0.2525125417714178, 0.7351490043780079]
        payload["solver_diagnostics"]["hessian_backend"] = "cppad_phase_state_fugacity"
        return payload

    monkeypatch.setattr(workflows, "solve_chemical_equilibrium_nlp_activation", fake_solve)
    mixture = epcsaft.Mixture(_two_component_parameter_set())

    result = epcsaft_equilibrium.reactive_speciation(
        species=_species(),
        reactions=_reaction(),
        feed_amounts={"A": 1.0, "B": 0.0},
        equilibrium_constants=[_eos_constant()],
        initial_amounts=[0.5, 0.5],
        eos_mixture=mixture,
    )

    assert captured["eos_mixture"] is mixture.native
    assert result.activities == pytest.approx(
        {"A": 0.2525125417714178, "B": 0.7351490043780079}
    )
    assert result.diagnostics["activity_model"] == "eos_x_phi"
    assert result.diagnostics["activity_derivative_backend"] == "cppad_implicit"
    assert result.diagnostics["hessian_backend"] == "cppad_phase_state_fugacity"


def test_reactive_speciation_passes_eos_gamma_context_to_native(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_solve(compiled, standard_states, **kwargs):
        captured["species"] = compiled.species_labels
        captured["standard_states"] = standard_states.reaction_labels
        captured["eos_mixture"] = kwargs["eos_mixture"]
        payload = _native_payload()
        payload["activity_model"] = "eos_x_gamma"
        payload["activity_derivative_backend"] = "cppad_implicit_activity_coefficient"
        payload["ln_activity_coefficients"] = [0.01, -0.02]
        payload["activities"] = [0.2525125417714178, 0.7351490043780079]
        payload["solver_diagnostics"]["hessian_backend"] = "cppad_phase_state_activity_coefficient"
        payload["continuation"] = {
            "direct_final_proof_attempted": False,
            "direct_final_proof_accepted": False,
            "parameter_name": "activity_lambda",
            "final_proof_status": "accepted",
            "final_stage_id": "activity_lambda_1",
            "lambda_values": [0.0, 0.5, 1.0],
            "final_lambda": 1.0,
            "activity_lambda_values": [0.0, 0.5, 1.0],
            "final_activity_lambda": 1.0,
            "stage_count": 3,
            "trace": [
                {"stage_id": "activity_lambda_0", "parameter_value": 0.0, "final_proof": False},
                {"stage_id": "activity_lambda_half", "parameter_value": 0.5, "final_proof": False},
                {"stage_id": "activity_lambda_1", "parameter_value": 1.0, "final_proof": True},
            ],
        }
        return payload

    monkeypatch.setattr(workflows, "solve_chemical_equilibrium_nlp_activation", fake_solve)
    mixture = epcsaft.Mixture(_two_component_parameter_set())

    result = epcsaft_equilibrium.reactive_speciation(
        species=_species(),
        reactions=_reaction(),
        feed_amounts={"A": 1.0, "B": 0.0},
        equilibrium_constants=[_eos_gamma_constant()],
        initial_amounts=[0.5, 0.5],
        eos_mixture=mixture,
    )

    assert captured["eos_mixture"] is mixture.native
    assert result.activities == pytest.approx(
        {"A": 0.2525125417714178, "B": 0.7351490043780079}
    )
    assert result.diagnostics["activity_model"] == "eos_x_gamma"
    assert result.diagnostics["activity_derivative_backend"] == "cppad_implicit_activity_coefficient"
    assert result.diagnostics["hessian_backend"] == "cppad_phase_state_activity_coefficient"
    assert result.diagnostics["continuation"]["parameter_name"] == "activity_lambda"
    assert result.diagnostics["continuation"]["activity_lambda_values"] == pytest.approx((0.0, 0.5, 1.0))
    assert result.diagnostics["continuation"]["final_activity_lambda"] == pytest.approx(1.0)


def test_reactive_speciation_solves_mea_co2_h2o_loading_sweep_against_retained_fixture() -> None:
    core = extension_native_core()
    if not core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    species = _mea_species()
    reactions = _mea_reactions()
    constants = _mea_constants()
    solver_options = epcsaft_equilibrium.EquilibriumSolverOptions(max_iterations=600, tolerance=1.0e-8)
    results = []
    max_mole_fraction_error = 0.0
    corrected_stationarity_cases = []

    for loading, expected in _MEA_EXPECTED_MOLE_FRACTIONS.items():
        result = epcsaft_equilibrium.reactive_speciation(
            species=species,
            reactions=reactions,
            feed_amounts={"MEA": 1.0, "H2O": _MEA_WATER_PER_AMINE, "CO2": loading},
            equilibrium_constants=constants,
            initial_amounts=None,
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
        assert result.diagnostics["initialization"]["source_oracle_initial_amounts"] is False
        assert result.diagnostics["initialization"]["seed_source"] == "max_min_feasible_interior"
        assert result.diagnostics["initialization"]["feasible_initialization"]["accepted"] is True
        assert result.diagnostics["continuation"]["final_proof_status"] == "accepted"
        assert result.diagnostics["continuation"]["final_lambda"] == pytest.approx(1.0)
        continuation = result.diagnostics["continuation"]
        corrector = continuation["physical_proof_corrector"]
        if continuation["direct_final_proof_accepted"]:
            assert corrector["attempted"] is False
            assert continuation["stage_count"] == 0
        else:
            assert corrector["attempted"] is True or continuation["stage_count"] >= 3
        assert corrector["corrector"] == "physical_residual_newton"
        if corrector["attempted"]:
            assert corrector["accepted"] is True
            assert corrector["status"] == "accepted"
            assert corrector["rejection_reason"] == ""
            assert corrector["initial_reaction_stationarity_inf_norm"] > corrector["reaction_stationarity_inf_norm"]
            assert corrector["final_reaction_stationarity_inf_norm"] == pytest.approx(
                corrector["reaction_stationarity_inf_norm"]
            )
            assert corrector["final_balance_inf_norm"] == pytest.approx(corrector["balance_inf_norm"])
            assert corrector["initial_reaction_stationarity_inf_norm"] > 1.0e-6
            assert corrector["final_reaction_stationarity_inf_norm"] <= 1.0e-6
            assert corrector["final_balance_inf_norm"] <= 1.0e-8
            corrected_stationarity_cases.append((loading, corrector))
        assert result.balances == pytest.approx({key: 0.0 for key in ("C", "O", "H", "N", "charge")}, abs=1.0e-8)
        assert result.affinities == pytest.approx({reaction.label: 0.0 for reaction in reactions}, abs=1.0e-6)
        expected_mole_fractions = [expected[label] for label in result.species_labels]
        point_errors = [
            abs(actual - target)
            for actual, target in zip(result.mole_fractions.tolist(), expected_mole_fractions)
        ]
        max_mole_fraction_error = max(max_mole_fraction_error, max(point_errors))
        assert max(point_errors) <= 1.0e-8

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
    assert corrected_stationarity_cases
    assert max_mole_fraction_error <= 1.0e-8
