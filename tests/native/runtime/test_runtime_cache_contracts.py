"""Native runtime contracts for pressure-vs-density closure and contribution terms."""

from __future__ import annotations

import numpy as np
import pytest

from epcsaft import SolutionError
from tests.helpers.native_cases import _ionic_state


def _assert_finite_mapping_values(values: dict[str, float]) -> None:
    assert values
    assert all(np.isfinite(float(value)) for value in values.values())

def test_runtime_cache_stats_track_density_and_reference_state_reuse() -> None:
    mix, species, pressure, _, temperature, composition = _ionic_state()
    mix.clear_runtime_caches()
    mix.reset_runtime_cache_stats()

    first = mix.state(T=temperature, x=composition, P=pressure, phase="liq")
    second = mix.state(T=temperature, x=composition, P=pressure, phase="liq")

    assert first.density() == pytest.approx(second.density())
    stats = mix.runtime_cache_stats()
    assert stats["density_warm_start_hits"] >= 1
    assert stats["density_warm_start_rejections"] == 0

    for _ in range(3):
        second.activity_coefficient(species=species, mean_ionic_form=True, basis="molality")

    stats = mix.runtime_cache_stats()
    assert stats["reference_state_cache_misses"] == 1
    assert stats["reference_state_cache_hits"] >= 2

def test_activity_coefficient_cache_behavior_distinguishes_aux_cache_from_solvent_override() -> None:
    mix, species, pressure, _, temperature, composition = _ionic_state()
    state = mix.state(T=temperature, x=composition, P=pressure, phase="liq")
    mix.clear_runtime_caches()
    mix.reset_runtime_cache_stats()

    first_solvation = state.solvation_free_energy(species=species)
    after_first_solvation = mix.runtime_cache_stats()
    second_solvation = state.solvation_free_energy(species=species)
    after_second_solvation = mix.runtime_cache_stats()

    assert second_solvation == pytest.approx(first_solvation)
    assert after_second_solvation == after_first_solvation

    first_override = state.activity_coefficient(species=species, solvent="water")
    after_first_override = mix.runtime_cache_stats()
    second_override = state.activity_coefficient(species=species, solvent="water")
    after_second_override = mix.runtime_cache_stats()

    assert second_override == pytest.approx(first_override)
    assert after_first_override["reference_state_cache_hits"] > after_second_solvation["reference_state_cache_hits"]
    assert after_second_override["reference_state_cache_hits"] > after_first_override["reference_state_cache_hits"]
    assert after_second_override["reference_state_cache_misses"] == after_first_override["reference_state_cache_misses"]

def test_runtime_cache_stats_track_warm_start_rejections_without_hiding_failures() -> None:
    mix, _, pressure, _, temperature, composition = _ionic_state()
    mix.clear_runtime_caches()
    mix.reset_runtime_cache_stats()

    first = mix.state(T=temperature, x=composition, P=pressure, phase="liq")
    before_failure = mix.runtime_cache_stats()
    with pytest.raises(SolutionError):
        mix.state(T=temperature, x=composition, P=1.0e12, phase="liq")
    after_failure = mix.runtime_cache_stats()

    assert first.density() > 0.0
    assert before_failure == {
        "reference_state_cache_hits": 0,
        "reference_state_cache_misses": 0,
        "density_warm_start_hits": 0,
        "density_warm_start_rejections": 0,
    }
    assert after_failure["density_warm_start_rejections"] == 1

def test_ionic_runtime_surface_uses_compact_package_fixture() -> None:
    mix, species, pressure, _, temperature, composition = _ionic_state()
    state = mix.state(T=temperature, x=composition, P=pressure, phase="liq")

    component_activity = state.activity_coefficient(species=species)
    mean_molality = state.activity_coefficient(species=species, mean_ionic_form=True, basis="molality")
    mean_mole = state.activity_coefficient(species=species, mean_ionic_form=True, basis="mole")
    solvation_free_energy = state.solvation_free_energy(species=species)
    osmotic_coefficient = state.osmotic_coefficient()
    dadt = state.temperature_derivative_residual_helmholtz(return_contribution_terms=True)
    dadx = state.composition_derivative_residual_helmholtz()

    _assert_finite_mapping_values(component_activity)
    _assert_finite_mapping_values(mean_molality)
    _assert_finite_mapping_values(mean_mole)
    _assert_finite_mapping_values(solvation_free_energy)
    assert np.all(np.isfinite(np.asarray(osmotic_coefficient, dtype=float)))
    assert set(dadt["terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    assert set(dadx["terms"]) == {"hc", "disp", "assoc", "ion", "born"}
    assert "Na+Cl-" in mean_molality
    assert "Na+Cl-" in mean_mole
    assert state.pressure() == pytest.approx(pressure)


def test_ionic_activity_cache_reuse_keeps_results_stable() -> None:
    mix, species, pressure, _, temperature, composition = _ionic_state()

    mix.clear_runtime_caches()
    mix.reset_runtime_cache_stats()
    first = mix.state(T=temperature, x=composition, P=pressure, phase="liq")
    first_gamma = first.activity_coefficient(species=species, mean_ionic_form=True, basis="molality")
    second = mix.state(T=temperature, x=composition, P=pressure, phase="liq")
    second_gamma = second.activity_coefficient(species=species, mean_ionic_form=True, basis="molality")
    stats = mix.runtime_cache_stats()

    assert second.density() == pytest.approx(first.density())
    assert second_gamma == pytest.approx(first_gamma)
    assert stats["density_warm_start_hits"] >= 1
