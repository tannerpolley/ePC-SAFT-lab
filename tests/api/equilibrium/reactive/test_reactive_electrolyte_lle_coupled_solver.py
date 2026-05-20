from __future__ import annotations

import numpy as np
import pytest

import epcsaft
from epcsaft import _core, ePCSAFTMixture


def _reactive_electrolyte_lle_fixture() -> tuple[
    ePCSAFTMixture,
    np.ndarray,
    epcsaft.ReactionDefinition,
]:
    species = ["H2O", "Butanol", "Na+", "Cl-"]
    aq = np.asarray([0.798324680201737, 0.016320352824141723, 0.09267748348706063, 0.09267748348706063])
    org = np.asarray([0.37006036048879404, 0.6214918588210971, 0.004223890345054407, 0.004223890345054407])
    beta_org = 0.613766575013417
    feed = (1.0 - beta_org) * aq + beta_org * org
    mix = ePCSAFTMixture.from_dataset("2022_Ascani", species, feed, 298.15)
    reaction = epcsaft.ReactionDefinition.from_literature_constant(
        {"H2O": -1.0, "Butanol": 1.0},
        log_equilibrium_constant=-1.265500953237746,
        name="water_to_butanol",
        standard_state="mole_fraction_activity",
        source="repo-contained model-consistent reactive electrolyte LLE fixture",
    )
    return mix, feed, reaction


def _assert_reactive_phase_native_ipopt_gate(excinfo: pytest.ExceptionInfo[epcsaft.InputError]) -> None:
    assert "native Ipopt reactive phase-equilibrium NLP route" in str(excinfo.value)


def test_reactive_electrolyte_lle_public_route_requires_native_ipopt(monkeypatch) -> None:
    mix, feed, reaction = _reactive_electrolyte_lle_fixture()
    captured: dict[str, object] = {}

    def native_gate(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return {
            "backend": "ipopt",
            "compiled": False,
            "adapter_available": False,
            "problem_name": "reactive_two_phase_eos",
            "derivative_backend": "analytic_cppad",
            "accepted": False,
            "status": "ipopt_dependency_required",
            "postsolve": {},
        }

    monkeypatch.setattr(_core, "_native_reactive_electrolyte_lle_eos_route_result", native_gate)
    with pytest.raises(epcsaft.InputError) as excinfo:
        mix.equilibrium(
            kind="reactive_electrolyte_lle",
            T=298.15,
            P=1.013e5,
            z=feed,
            balances={
                "solvent_total": {"H2O": 1.0, "Butanol": 1.0},
                "sodium": {"Na+": 1.0},
                "chloride": {"Cl-": 1.0},
            },
            totals={
                "solvent_total": float(feed[0] + feed[1]),
                "sodium": float(feed[2]),
                "chloride": float(feed[3]),
            },
            reactions=[reaction],
            phase_options=epcsaft.EquilibriumOptions(
                max_iterations=80,
                tolerance=1.0e-8,
                min_composition=1.0e-12,
                ipopt_linear_solver="mumps",
                ipopt_dual_infeasibility_tolerance=5.0e-8,
            ),
        )

    _assert_reactive_phase_native_ipopt_gate(excinfo)
    args = captured["args"]
    assert args[0] is mix._native
    assert args[3] == pytest.approx(feed.tolist())
    assert args[4] == 3
    assert args[5] == pytest.approx([1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    assert args[6] == pytest.approx([float(feed[0] + feed[1]), float(feed[2]), float(feed[3])])
    assert args[7] == 1
    assert args[8] == pytest.approx([-1.0, 1.0, 0.0, 0.0])
    assert captured["kwargs"]["linear_solver"] == "mumps"
    assert captured["kwargs"]["acceptable_tolerance"] == pytest.approx(1.0e-6)
    assert captured["kwargs"]["constraint_violation_tolerance"] == pytest.approx(1.0e-8)
    assert captured["kwargs"]["dual_infeasibility_tolerance"] == pytest.approx(5.0e-8)
    assert captured["kwargs"]["complementarity_tolerance"] == pytest.approx(1.0e-8)


def test_reactive_electrolyte_lle_public_route_certifies_accepted_native_split(monkeypatch) -> None:
    mix, feed, reaction = _reactive_electrolyte_lle_fixture()
    stability_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
    aq = [0.798324680201737, 0.016320352824141723, 0.09267748348706063, 0.09267748348706063]
    org = [0.37006036048879404, 0.6214918588210971, 0.004223890345054407, 0.004223890345054407]

    def accepted_native_route(*_args, **_kwargs):
        return {
            "backend": "ipopt",
            "compiled": True,
            "adapter_available": True,
            "ran": True,
            "accepted": True,
            "status": "accepted",
            "solver_accepted": True,
            "solver_status": "success",
            "application_status": "solve_succeeded",
            "problem_name": "reactive_liquid_root_eos",
            "variable_model": "log_phase_species_amounts_plus_log_density",
            "density_backend": "explicit_log_density_pressure_constraint",
            "residual_families": [
                "conserved_balance",
                "reaction_stationarity",
                "phase_equilibrium",
            ],
            "constraint_families": [
                "conserved_balance",
                "phase_pressure_consistency",
                "phase_distance",
            ],
            "postsolve": {
                "accepted": True,
                "density_backend": "explicit_log_density_pressure_constraint",
                "phase_eligibility_mask": [1.0] * 8,
                "phase_compositions": [aq, org],
                "phase_amount_totals": [0.4, 0.6],
                "phase_volumes": [0.01, 0.015],
                "phase_ln_fugacity_coefficients": [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]],
                "phase_distance": 0.48,
            },
        }

    def accepted_stability_route(*args, **kwargs):
        stability_calls.append((args, kwargs))
        return {
            "backend": "ipopt",
            "compiled": True,
            "adapter_available": True,
            "ran": True,
            "accepted": True,
            "stable": True,
            "status": "accepted",
            "solver_accepted": True,
            "solver_status": "success",
            "application_status": "solve_succeeded",
            "problem_name": "electrolyte_stability_tpd",
            "parent_phase": "liq",
            "trial_phase": "liq",
            "min_tpd": 0.0,
            "objective": 0.0,
            "trial_composition": list(args[3]),
            "variables": list(args[3]),
        }

    monkeypatch.setattr(_core, "_native_reactive_electrolyte_lle_eos_route_result", accepted_native_route)
    monkeypatch.setattr(_core, "_native_electrolyte_stability_tpd_route_result", accepted_stability_route)

    result = mix.equilibrium(
        kind="reactive_electrolyte_lle",
        T=298.15,
        P=1.013e5,
        z=feed,
        balances={
            "solvent_total": {"H2O": 1.0, "Butanol": 1.0},
            "sodium": {"Na+": 1.0},
            "chloride": {"Cl-": 1.0},
        },
        totals={
            "solvent_total": float(feed[0] + feed[1]),
            "sodium": float(feed[2]),
            "chloride": float(feed[3]),
        },
        reactions=[reaction],
    )

    assert len(stability_calls) == 2
    assert result.diagnostics["reactive_route_status"] == "accepted"
    assert result.diagnostics["stability_certificate"]["accepted"] is True
    assert result.diagnostics["stability_certificate"]["stability_source"] == "reactive_phase_tpd"
    assert result.diagnostics["postsolve_certification"]["accepted"] is True
    assert result.diagnostics["postsolve_certification"]["stability_checked"] is True
    assert result.diagnostics["postsolve_certification"]["phase_eligibility_reported"] is True


def test_reactive_electrolyte_lle_public_route_threads_phase_models(monkeypatch) -> None:
    mix, feed, _reaction = _reactive_electrolyte_lle_fixture()
    aq_model = ePCSAFTMixture.from_params(
        {
            "MW": np.asarray([18.0e-3, 23.0e-3, 35.5e-3]),
            "m": np.asarray([1.1, 1.0, 1.0]),
            "s": np.asarray([3.0, 3.0, 3.0]),
            "e": np.asarray([180.0, 150.0, 150.0]),
            "k_ij": np.zeros((3, 3)),
            "z": np.asarray([0.0, 1.0, -1.0]),
            "dielc": np.asarray([80.0, 1.0, 1.0]),
        },
        species=["H2O", "Na+", "Cl-"],
    )
    org_model = ePCSAFTMixture.from_params(
        {
            "MW": np.asarray([74.0e-3]),
            "m": np.asarray([1.4]),
            "s": np.asarray([3.4]),
            "e": np.asarray([220.0]),
            "k_ij": np.zeros((1, 1)),
            "z": np.asarray([0.0]),
            "dielc": np.asarray([12.0]),
        },
        species=["Butanol"],
    )
    reaction = epcsaft.ReactionDefinition.from_literature_constant(
        {"H2O": -1.0, "Butanol": 1.0},
        log_equilibrium_constant=-1.265500953237746,
        name="phase_model_water_to_butanol",
        standard_state="mole_fraction_activity",
        phase_stoichiometry={
            "aq": {"H2O": -1.0},
            "org": {"Butanol": 1.0},
        },
        source="phase_models public route smoke fixture",
    )
    captured: dict[str, object] = {}

    def native_gate(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return {
            "backend": "ipopt",
            "compiled": False,
            "adapter_available": False,
            "problem_name": "reactive_liquid_root_eos",
            "derivative_backend": "cppad_implicit",
            "accepted": False,
            "status": "ipopt_dependency_required",
            "postsolve": {},
        }

    monkeypatch.setattr(_core, "_native_reactive_electrolyte_lle_phase_model_eos_route_result", native_gate)
    with pytest.raises(epcsaft.InputError, match="native Ipopt reactive phase-equilibrium NLP route"):
        mix.equilibrium(
            kind="reactive_electrolyte_lle",
            T=298.15,
            P=1.013e5,
            z=feed,
            balances={
                "solvent_total": {"H2O": 1.0, "Butanol": 1.0},
                "sodium": {"Na+": 1.0},
                "chloride": {"Cl-": 1.0},
            },
            totals={
                "solvent_total": float(feed[0] + feed[1]),
                "sodium": float(feed[2]),
                "chloride": float(feed[3]),
            },
            reactions=[reaction],
            phase_models={"aq": aq_model, "org": org_model},
            phase_options=epcsaft.EquilibriumOptions(
                max_iterations=80,
                tolerance=1.0e-8,
                min_composition=1.0e-12,
                ipopt_linear_solver="ma57",
                ipopt_constraint_violation_tolerance=7.0e-8,
            ),
        )

    args = captured["args"]
    assert args[0] is mix._native
    assert args[1] is aq_model._native
    assert args[2] is org_model._native
    assert args[3] == [0, 2, 3]
    assert args[4] == [1]
    assert args[8] == 3
    assert args[11] == 1
    assert args[12] == pytest.approx([-1.0, 1.0, 0.0, 0.0])
    assert captured["kwargs"]["linear_solver"] == "ma57"
    assert captured["kwargs"]["acceptable_tolerance"] == pytest.approx(1.0e-6)
    assert captured["kwargs"]["constraint_violation_tolerance"] == pytest.approx(7.0e-8)
    assert captured["kwargs"]["dual_infeasibility_tolerance"] == pytest.approx(1.0e-8)
    assert captured["kwargs"]["complementarity_tolerance"] == pytest.approx(1.0e-8)
