from __future__ import annotations

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.closure_models import (
    EXACT_MASS_ACTION_BASELINE,
    PICARD7_CLOSURE,
)
from analyses.package_validation.explicit_association_toybox.scripts.pure_saturation import (
    solve_pure_saturation,
)


def _methanol_case() -> dict[str, object]:
    return {
        "species": ["Methanol"],
        "parameter_source": "test_case",
        "parameters": {
            "m": [1.5255],
            "s": [3.23],
            "e": [188.9],
            "e_assoc": [2899.5],
            "vol_a": [0.03518],
            "assoc_scheme": ["2B"],
        },
    }


def test_pure_saturation_solver_returns_coexistence_residual_schema() -> None:
    result = solve_pure_saturation(
        _methanol_case(),
        temperature=352.28,
        closure_name=EXACT_MASS_ACTION_BASELINE,
        pressure_seed_Pa=175_580.0,
        liquid_density_seed_mol_m3=22_891.0,
    )

    assert result.status == "computed_toy_pure_saturation"
    assert result.closure_name == EXACT_MASS_ACTION_BASELINE
    assert result.model_role == "toy_pcsaft_exact_implicit_association"
    assert result.p_sat_Pa > 0.0
    assert result.rho_vap_mol_m3 > 0.0
    assert result.rho_liq_mol_m3 > result.rho_vap_mol_m3
    assert abs(result.pressure_vap_residual_Pa) <= max(result.p_sat_Pa * 1.0e-6, 1.0)
    assert abs(result.pressure_liq_residual_Pa) <= max(result.p_sat_Pa * 1.0e-6, 1.0)
    assert abs(result.log_fugacity_residual) <= 1.0e-6
    assert result.solver_iteration_count > 0
    assert result.pressure_evaluation_count > 0
    assert result.initial_guess_policy == "reference_pressure_liquid_density_ideal_vapor_seed"


def test_picard_uses_same_pure_saturation_solver_contract() -> None:
    exact = solve_pure_saturation(
        _methanol_case(),
        temperature=352.28,
        closure_name=EXACT_MASS_ACTION_BASELINE,
        pressure_seed_Pa=175_580.0,
        liquid_density_seed_mol_m3=22_891.0,
    )
    picard = solve_pure_saturation(
        _methanol_case(),
        temperature=352.28,
        closure_name=PICARD7_CLOSURE,
        pressure_seed_Pa=175_580.0,
        liquid_density_seed_mol_m3=22_891.0,
    )

    assert picard.status == "computed_toy_pure_saturation"
    assert picard.closure_name == PICARD7_CLOSURE
    assert picard.model_role == "toy_pcsaft_picard_association"
    assert picard.initial_guess_policy == exact.initial_guess_policy
    assert picard.rho_liq_mol_m3 > picard.rho_vap_mol_m3
    assert picard.p_sat_Pa > 0.0


def test_pure_saturation_solver_fails_loudly_for_invalid_phase_density_seeds() -> None:
    with pytest.raises(ValueError, match="vapor density seed must be below liquid density seed"):
        solve_pure_saturation(
            _methanol_case(),
            temperature=352.28,
            closure_name=EXACT_MASS_ACTION_BASELINE,
            pressure_seed_Pa=175_580.0,
            vapor_density_seed_mol_m3=22_891.0,
            liquid_density_seed_mol_m3=22_891.0,
        )
