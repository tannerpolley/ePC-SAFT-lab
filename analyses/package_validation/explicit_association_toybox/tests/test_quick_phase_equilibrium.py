from __future__ import annotations

import math

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.closure_models import (
    EXACT_MASS_ACTION_BASELINE,
    PICARD7_CLOSURE,
)
from analyses.package_validation.explicit_association_toybox.scripts.quick_phase_equilibrium import (
    quick_phase_equilibrium_rows,
    reduced_chemical_potential,
    solve_pure_phase_pair,
)
from analyses.package_validation.explicit_association_toybox.scripts.toy_property_eos import (
    pressure_result_from_state,
    state_from_provider_case,
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


def test_reduced_chemical_potential_uses_same_pressure_path() -> None:
    case = _methanol_case()
    state = state_from_provider_case(case, temperature=350.0, density=12_000.0)

    _, ares, z_terms = pressure_result_from_state(state, case, closure_name=EXACT_MASS_ACTION_BASELINE)
    value = reduced_chemical_potential(state, case, closure_name=EXACT_MASS_ACTION_BASELINE)

    assert value == pytest.approx(math.log(state.density) + ares + z_terms.total)


def test_phase_pair_solver_reduces_residual_from_experimental_like_seed() -> None:
    case = _methanol_case()
    temperature = 450.0
    source_pressure = 2.0e6
    source_liquid_density = 18_000.0
    vapor_seed = source_pressure / (8.31446261815324 * temperature)

    result = solve_pure_phase_pair(
        case,
        temperature=temperature,
        closure_name=PICARD7_CLOSURE,
        vapor_density_seed_mol_m3=vapor_seed,
        liquid_density_seed_mol_m3=source_liquid_density,
        pressure_scale_Pa=source_pressure,
    )

    assert result.status in {
        "converged_phase_pair",
        "iteration_limit_phase_pair",
        "phase_pair_line_search_stalled",
        "singular_phase_pair_linearization",
    }
    assert result.vapor_density_mol_m3 < result.liquid_density_mol_m3
    assert result.scaled_residual_norm <= result.initial_scaled_residual_norm
    assert result.pressure_scale_Pa == pytest.approx(source_pressure)


def test_quick_phase_equilibrium_rows_compare_exact_and_picard() -> None:
    source_rows = [
        {
            "component": "methanol",
            "T_K": 450.0,
            "p_sat_Pa": 2.0e6,
            "rho_sat_liq_mol_m3": 18_000.0,
        }
    ]

    rows = quick_phase_equilibrium_rows(
        source_rows,
        provider_cases={"methanol": _methanol_case()},
        closure_names=(EXACT_MASS_ACTION_BASELINE, PICARD7_CLOSURE),
        max_rows_per_component=1,
    )

    assert {row["model_label"] for row in rows} == {"Exact implicit", "Picard"}
    assert all(row["diagnostic_scope"] == "toy_pure_phase_pair_pressure_mu_equality" for row in rows)
    assert all(float(row["residual_reduction_factor"]) >= 1.0 for row in rows)
    assert all("saturation claim" in str(row["message"]) for row in rows)
