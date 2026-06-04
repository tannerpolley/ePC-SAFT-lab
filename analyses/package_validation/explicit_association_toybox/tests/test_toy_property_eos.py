from __future__ import annotations

import numpy as np
import pytest

from analyses.package_validation.explicit_association_toybox.scripts.closure_models import (
    EXACT_MASS_ACTION_BASELINE,
    PICARD7_CLOSURE,
)
from analyses.package_validation.explicit_association_toybox.scripts.toy_property_eos import (
    GAS_CONSTANT,
    association_system_from_case,
    liquid_density_initial_guess,
    pressure_from_state,
    pressure_result_from_state,
    solve_liquid_density_root,
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


def test_toy_pressure_density_root_recovers_known_exact_pressure() -> None:
    case = _methanol_case()
    density = 24_500.0
    temperature = 323.15
    pressure, _, z_value = pressure_from_state(
        state_from_provider_case(case, temperature=temperature, density=density),
        case,
        closure_name=EXACT_MASS_ACTION_BASELINE,
    )

    root = solve_liquid_density_root(
        case,
        temperature=temperature,
        target_pressure_Pa=pressure,
        closure_name=EXACT_MASS_ACTION_BASELINE,
        density_seed_mol_m3=density,
    )

    assert z_value > 0.0
    assert root.status == "computed_toy_liquid_density_root"
    assert root.rho_mol_m3 == pytest.approx(density, rel=1.0e-6)
    assert abs(root.residual_Pa or 0.0) <= max(1.0e-4, abs(pressure) * 1.0e-8)
    assert root.initial_guess_mol_m3 == pytest.approx(
        liquid_density_initial_guess(case, temperature=temperature)
    )
    assert root.initial_guess_policy == "legacy_pcsaft_liquid_eta_0_5"
    assert root.bracket_policy in {
        "experimental_density_center_exact",
        "experimental_density_center_local",
        "legacy_eta_guess_center_exact",
        "legacy_eta_guess_center_local",
        "coarse_density_scan",
    }
    assert root.pressure_evaluation_count > 0


def test_toy_picard_pressure_is_finite_for_associating_case() -> None:
    case = _methanol_case()
    pressure, ares, z_value = pressure_from_state(
        state_from_provider_case(case, temperature=323.15, density=24_500.0),
        case,
        closure_name=PICARD7_CLOSURE,
    )

    assert pressure > 0.0
    assert ares < 0.0
    assert z_value > 0.0


def test_pressure_result_exposes_reference_style_z_decomposition() -> None:
    case = _methanol_case()
    state = state_from_provider_case(case, temperature=323.15, density=24_500.0)

    pressure, ares, terms = pressure_result_from_state(
        state,
        case,
        closure_name=EXACT_MASS_ACTION_BASELINE,
    )

    assert ares < 0.0
    assert terms.ideal == pytest.approx(1.0)
    assert terms.total == pytest.approx(
        terms.ideal + terms.hard_chain + terms.dispersion + terms.association
    )
    assert pressure == pytest.approx(state.density * GAS_CONSTANT * state.temperature * terms.total)


def test_mixture_case_requires_explicit_composition() -> None:
    case = {
        "species": ["A", "B"],
        "parameters": {
            "m": [1.2, 1.6],
            "s": [3.1, 3.4],
            "e": [180.0, 220.0],
            "e_assoc": [1500.0, 1800.0],
            "vol_a": [0.02, 0.03],
            "assoc_scheme": ["2B", "2B"],
        },
    }

    with pytest.raises(ValueError, match="explicit composition"):
        state_from_provider_case(case, temperature=320.0, density=20_000.0)


def test_mixture_case_builds_cross_association_system_when_composition_is_explicit() -> None:
    case = {
        "species": ["A", "B"],
        "parameters": {
            "m": [1.2, 1.6],
            "s": [3.1, 3.4],
            "e": [180.0, 220.0],
            "e_assoc": [1500.0, 1800.0],
            "vol_a": [0.02, 0.03],
            "k_ij": [[0.0, 0.01], [0.01, 0.0]],
            "k_hb": [[0.0, 0.05], [0.05, 0.0]],
            "assoc_scheme": ["2B", "2B"],
        },
    }

    state = state_from_provider_case(
        case,
        temperature=320.0,
        density=3_000.0,
        composition=np.array([0.25, 0.75]),
    )
    system = association_system_from_case(case)
    pressure, _, terms = pressure_result_from_state(state, case, closure_name=PICARD7_CLOSURE)

    assert system is not None
    assert system.site_count == 4
    assert system.component_count == 2
    assert state.composition.tolist() == pytest.approx([0.25, 0.75])
    assert pressure > 0.0
    assert terms.association < 0.0
