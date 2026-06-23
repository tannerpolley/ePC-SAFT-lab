from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest

import epcsaft
import epcsaft_equilibrium as equilibrium_module
from scripts.validation import check_boundary_workflows as checker


REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "neutral_lle"
    / "perfluorohexane_hexane"
)
SOURCE_TEMPERATURE_K = 293.895
PRESSURE_PA = 101300.0
PARENT_LIQUID = [0.2, 0.8]
SHADOW_LIQUID = [0.5497, 0.4503]
MODEL_PARENT_LIQUID = [0.19253198692922618, 0.8074680130707738]
MODEL_SHADOW_LIQUID = [0.5397660336131663, 0.46023396638683367]
PUBLIC_TEST_PRESSURE_PA = 1_276_369.4735856401
PUBLIC_TEST_COMPOSITION = [0.1, 0.9]


def _neutral_parameter_set() -> epcsaft.ParameterSet:
    return epcsaft.ParameterSet.from_dict(
        {
            "m": np.asarray([1.0, 1.6069]),
            "s": np.asarray([3.7039, 3.5206]),
            "e": np.asarray([150.03, 191.42]),
            "MW": np.asarray([16.043e-3, 30.070e-3]),
            "k_ij": np.zeros((2, 2)),
        },
        species=("methane", "ethane"),
    )


class _MissingCloudShadowCore:
    pass


class _AcceptedCloudShadowCore:
    def _native_equilibrium_selector_route_result(self, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return {
            "accepted": True,
            "status": "production_accepted",
            "solver_status": "success",
            "application_status": "solve_succeeded",
            "postsolve": {
                "accepted": True,
                "phase_compositions": [MODEL_PARENT_LIQUID, MODEL_SHADOW_LIQUID],
                "phase_amount_totals": [0.47494200291734767, 0.5250579970826523],
            },
        }

    def _native_equilibrium_cloud_shadow_route_result(self, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return {
            "accepted": True,
            "status": "accepted",
            "solver_status": "success",
            "application_status": "solve_succeeded",
            "problem_name": "neutral_cloud_t_eos",
            "route": "cloud_temperature",
            "selector_family": "cloud_shadow_derived_routes",
            "public_route_admission": "closed",
            "phase_labels": ["parent_liquid", "shadow_liquid"],
            "phase_roles": ["parent_liquid", "incipient_liquid"],
            "variable_model": "phase_species_amounts_plus_phase_volume_plus_route_scalar",
            "density_backend": "explicit_phase_volume_pressure_constraint",
            "residual_families": [
                "fixed_composition",
                "phase_amount_total",
                "phase_pressure_consistency",
                "phase_equilibrium",
                "phase_distance",
            ],
            "constraint_families": [
                "fixed_composition",
                "phase_amount_total",
                "phase_pressure_consistency",
                "phase_equilibrium",
                "phase_volume_gap",
            ],
            "phase_amounts": [MODEL_PARENT_LIQUID, MODEL_SHADOW_LIQUID],
            "phase_volumes": [1.45e-4, 1.70e-4],
            "variables": [*MODEL_PARENT_LIQUID, 1.45e-4, *MODEL_SHADOW_LIQUID, 1.70e-4, SOURCE_TEMPERATURE_K],
            "seed_name": "source_pair_seed",
            "seed_attempts": [
                {
                    "seed_name": "source_pair_seed",
                    "status": "accepted",
                    "solver_status": "success",
                    "application_status": "solve_succeeded",
                    "accepted": True,
                    "iteration_count": 5,
                    "max_iterations": 260,
                }
            ],
            "postsolve": {
                "accepted": True,
                "material_balance_norm": 0.0,
                "pressure_consistency_norm": 0.0,
                "ln_fugacity_consistency_norm": 0.0,
                "phase_equilibrium_norm": 0.0,
                "phase_distance": abs(MODEL_SHADOW_LIQUID[0] - MODEL_PARENT_LIQUID[0]),
                "scaled_constraint_violation_inf_norm": 0.0,
            },
            "physical_evidence": {
                "phase_labels": ["parent_liquid", "shadow_liquid"],
                "phase_roles": ["parent_liquid", "incipient_liquid"],
                "phase_distance": abs(MODEL_SHADOW_LIQUID[0] - MODEL_PARENT_LIQUID[0]),
                "material_balance_norm": 0.0,
                "pressure_consistency_norm": 0.0,
                "ln_fugacity_consistency_norm": 0.0,
                "phases": [
                    {"label": "parent_liquid", "composition": MODEL_PARENT_LIQUID},
                    {"label": "shadow_liquid", "composition": MODEL_SHADOW_LIQUID},
                ],
            },
        }


def _evaluate_cloud_shadow_route(case_dir: Path = CASE_DIR, *, run_native: bool = True) -> dict[str, Any]:
    evaluator = getattr(checker, "evaluate_cloud_shadow_route_evidence", None)
    assert evaluator is not None, "checker must expose evaluate_cloud_shadow_route_evidence"
    return dict(evaluator(case_dir, run_native=run_native))


def test_cloud_shadow_route_evidence_reports_missing_private_native_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(checker, "_core", _MissingCloudShadowCore())

    payload = _evaluate_cloud_shadow_route()

    assert payload["complete"] is False
    assert payload["source_gate_complete"] is True
    assert payload["status"] == "native_route_blocked"
    assert "native_cloud_temperature_route_missing" in payload["route_evidence_blockers"]
    assert payload["public_route_admission"] == "closed"


def test_cloud_shadow_route_evidence_payload_matches_source_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(checker, "_core", _AcceptedCloudShadowCore())

    payload = _evaluate_cloud_shadow_route()

    required_fields = {
        "complete",
        "status",
        "source_fixture",
        "route",
        "pressure_Pa",
        "parent_liquid_composition",
        "source_temperature_K",
        "solved_temperature_K",
        "temperature_abs_error_K",
        "source_shadow_composition",
        "solved_shadow_composition",
        "shadow_composition_abs_error",
        "residuals",
        "strict_convergence",
        "solver_status",
        "application_status",
        "seed_attempts",
        "route_trace",
        "public_route_admission",
    }
    assert required_fields.issubset(payload)
    assert payload["complete"] is True
    assert payload["status"] == "native_route_complete"
    assert payload["route"] == "cloud_temperature"
    assert payload["pressure_Pa"] == PRESSURE_PA
    assert payload["source_parent_liquid_composition"] == PARENT_LIQUID
    assert payload["parent_liquid_composition"] == MODEL_PARENT_LIQUID
    assert payload["source_parent_composition_abs_error"] == pytest.approx([0.007468013070773831, 0.007468013070773831])
    assert payload["source_temperature_K"] == SOURCE_TEMPERATURE_K
    assert payload["solved_temperature_K"] == pytest.approx(SOURCE_TEMPERATURE_K)
    assert payload["temperature_abs_error_K"] == pytest.approx(0.0)
    assert payload["source_shadow_composition"] == SHADOW_LIQUID
    assert payload["solved_shadow_composition"] == pytest.approx(MODEL_SHADOW_LIQUID)
    assert payload["shadow_composition_abs_error"] == pytest.approx([0.009933966386833692, 0.009933966386833636])
    assert payload["model_reference"]["status"] == "model_reference_complete"
    assert payload["strict_convergence"] is True
    assert payload["solver_status"] == "success"
    assert payload["application_status"] == "solve_succeeded"
    assert payload["public_route_admission"] == "closed"
    assert payload["route_trace"]["selector_family"] == "cloud_shadow_derived_routes"
    assert payload["route_trace"]["problem_name"] == "neutral_cloud_t_eos"


@pytest.mark.parametrize(
    "route",
    ["cloud_temperature", "cloud_point", "shadow_point", "shadow_temperature"],
)
def test_public_equilibrium_route_strings_remain_closed(route: str) -> None:
    mixture = epcsaft.Mixture(_neutral_parameter_set())

    with pytest.raises(epcsaft.InputError, match="Unknown equilibrium route"):
        equilibrium_module.Equilibrium(mixture, route=route, P=PUBLIC_TEST_PRESSURE_PA, x=PUBLIC_TEST_COMPOSITION)
