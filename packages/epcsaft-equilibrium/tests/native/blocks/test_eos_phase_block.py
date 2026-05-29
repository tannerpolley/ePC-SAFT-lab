from __future__ import annotations

import numpy as np
import pytest

import epcsaft
from epcsaft.state.native_adapter import ePCSAFTMixture
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()
from equilibrium_support.runtime_cases import _ionic_params


def _neutral_binary_mixture() -> ePCSAFTMixture:
    params = {
        "m": np.asarray([1.0, 1.6069]),
        "s": np.asarray([3.7039, 3.5206]),
        "e": np.asarray([150.03, 191.42]),
        "k_ij": np.asarray([[0.0, 3.0e-4], [3.0e-4, 0.0]]),
    }
    return ePCSAFTMixture.from_params(params, species=["Methane", "Ethane"])


def _methanol_cyclohexane_mixture() -> ePCSAFTMixture:
    params = {
        "MW": np.asarray([32.042e-3, 84.147e-3]),
        "m": np.asarray([1.5255, 2.5303]),
        "s": np.asarray([3.2300, 3.8499]),
        "e": np.asarray([188.90, 278.11]),
        "e_assoc": np.asarray([2899.5, 0.0]),
        "vol_a": np.asarray([0.035176, 0.0]),
        "assoc_scheme": ["2B", None],
        "k_ij": np.asarray([[0.0, 0.051], [0.051, 0.0]]),
        "z": np.asarray([0.0, 0.0]),
        "dielc": np.asarray([33.05, 2.02]),
    }
    return ePCSAFTMixture.from_params(params, species=["Methanol", "Cyclohexane"])


def _binary_two_site_associating_mixture() -> ePCSAFTMixture:
    temperature = 298.15
    water_sigma = 2.7927 + 10.11 * np.exp(-0.01775 * temperature) - 1.417 * np.exp(-0.01146 * temperature)
    params = {
        "m": np.asarray([1.2047, 1.6069]),
        "s": np.asarray([water_sigma, 3.5206]),
        "e": np.asarray([353.95, 191.42]),
        "e_assoc": np.asarray([2425.7, 1200.0]),
        "vol_a": np.asarray([0.04509, 0.025]),
        "assoc_scheme": ["2B", "2B"],
        "k_ij": np.asarray([[0.0, 0.01], [0.01, 0.0]]),
        "l_ij": np.asarray([[0.0, 2.0e-4], [2.0e-4, 0.0]]),
        "k_hb": np.asarray([[0.0, 0.03], [0.03, 0.0]]),
    }
    return ePCSAFTMixture.from_params(params, species=["Water", "B"])


def _ionic_mixture() -> ePCSAFTMixture:
    params = _ionic_params()
    params["assoc_scheme"] = [None, None, None]
    params["e_assoc"] = np.zeros(3)
    params["vol_a"] = np.zeros(3)
    return ePCSAFTMixture.from_params(params, species=["water", "Na+", "Cl-"])


def _two_phase_binary_case() -> tuple[
    ePCSAFTMixture,
    float,
    list[np.ndarray],
    list[float],
    np.ndarray,
    float,
]:
    mix = _neutral_binary_mixture()
    temperature = 300.0
    phase_amounts = [
        np.asarray([0.7, 0.3], dtype=float),
        np.asarray([0.1, 0.9], dtype=float),
    ]
    volumes = [float(phase_amounts[0].sum() / 80.0), float(phase_amounts[1].sum() / 140.0)]
    feed_amounts = phase_amounts[0] + phase_amounts[1]
    target_pressure = mix.state(
        T=temperature,
        rho=phase_amounts[0].sum() / volumes[0],
        x=phase_amounts[0] / phase_amounts[0].sum(),
        phase="liquid",
    ).pressure()
    return mix, temperature, phase_amounts, volumes, feed_amounts, target_pressure


def test_eos_phase_block_builds_amount_volume_variables_and_pressure_gate() -> None:
    mix = _neutral_binary_mixture()
    amounts = np.asarray([0.8, 1.2], dtype=float)
    temperature = 300.0
    density = 120.0
    volume = float(amounts.sum() / density)
    composition = amounts / amounts.sum()
    state = mix.state(T=temperature, rho=density, x=composition, phase="vapor")
    pressure = state.pressure()

    payload = _core._native_eos_phase_block(mix._native, temperature, pressure, amounts.tolist(), volume)

    assert payload["block"] == "eos_phase"
    assert payload["variable_names"] == ["n_0", "n_1", "volume"]
    assert payload["constraint_names"] == ["pressure_consistency"]
    assert payload["derivative_backend"] == "analytic"
    assert payload["composition"] == pytest.approx(composition.tolist(), abs=1.0e-14)
    assert payload["density"] == pytest.approx(density, rel=1.0e-14)
    assert payload["eos_pressure"] == pytest.approx(pressure, rel=1.0e-14)
    assert abs(payload["pressure_consistency_residual"]) <= 1.0e-8
    assert abs(payload["gradient"][-1]) <= 1.0e-10
    assert payload["objective_terms"]["pressure_work"] == pytest.approx(
        pressure * volume / payload["gas_constant_temperature"]
    )


def test_eos_phase_block_gradient_matches_chemical_potential_and_pressure_identities() -> None:
    mix = _neutral_binary_mixture()
    amounts = np.asarray([0.8, 1.2], dtype=float)
    temperature = 300.0
    density = 120.0
    volume = float(amounts.sum() / density)
    composition = amounts / amounts.sum()
    state = mix.state(T=temperature, rho=density, x=composition, phase="vapor")
    eos_pressure = state.pressure()
    target_pressure = eos_pressure + 2500.0

    payload = _core._native_eos_phase_block(mix._native, temperature, target_pressure, amounts.tolist(), volume)

    residual_mu = np.asarray(state.residual_chemical_potential(), dtype=float)
    expected_amount_gradient = np.log(amounts / volume) + residual_mu
    expected_volume_gradient = (target_pressure - eos_pressure) / payload["gas_constant_temperature"]

    assert payload["gradient"][:-1] == pytest.approx(expected_amount_gradient.tolist(), rel=1.0e-12, abs=1.0e-12)
    assert payload["gradient"][-1] == pytest.approx(expected_volume_gradient, rel=1.0e-12, abs=1.0e-12)
    assert payload["pressure_consistency_residual"] == pytest.approx(eos_pressure - target_pressure, abs=1.0e-8)
    assert np.isfinite(payload["objective"])


def test_eos_phase_block_pressure_jacobian_uses_exact_cppad_homogeneity_identity() -> None:
    mix = _neutral_binary_mixture()
    amounts = np.asarray([0.8, 1.2], dtype=float)
    temperature = 300.0
    density = 120.0
    volume = float(amounts.sum() / density)
    composition = amounts / amounts.sum()
    state = mix.state(T=temperature, rho=density, x=composition, phase="vapor")
    target_pressure = state.pressure() + 2500.0

    payload = _core._native_eos_phase_block(mix._native, temperature, target_pressure, amounts.tolist(), volume)

    jacobian = np.asarray(payload["pressure_jacobian"], dtype=float)
    assert payload["pressure_jacobian_backend"] == "cppad"
    assert payload["pressure_jacobian_shape"] == (1, 3)
    assert jacobian.size == 3
    assert jacobian[-1] == pytest.approx(
        -payload["pressure_density_derivative"] * payload["density"] / payload["volume"],
        rel=1.0e-12,
        abs=1.0e-8,
    )
    assert float(np.dot(amounts, jacobian[:-1]) + volume * jacobian[-1]) == pytest.approx(0.0, abs=1.0e-8)


def test_eos_phase_block_reports_pressure_constraint_jacobian_from_exact_curvature_identity() -> None:
    mix = _neutral_binary_mixture()
    amounts = np.asarray([0.8, 1.2], dtype=float)
    temperature = 300.0
    density = 120.0
    volume = float(amounts.sum() / density)
    composition = amounts / amounts.sum()
    state = mix.state(T=temperature, rho=density, x=composition, phase="vapor")

    payload = _core._native_eos_phase_block(mix._native, temperature, state.pressure(), amounts.tolist(), volume)

    assert payload["objective_curvature_backend"] == "cppad"
    assert payload["constraint_jacobian_backend"] == "cppad"
    assert payload["objective_curvature_shape"] == (3, 3)
    assert payload["constraint_jacobian_shape"] == (1, 3)
    objective_curvature = np.asarray(payload["objective_curvature_row_major"], dtype=float).reshape((3, 3))
    constraint_jacobian = np.asarray(payload["constraint_jacobian_row_major"], dtype=float).reshape((1, 3))
    pressure_hessian = np.asarray(payload["pressure_hessian_row_major"], dtype=float).reshape((3, 3))
    expected_pressure_jacobian = -payload["gas_constant_temperature"] * objective_curvature[-1, :]

    assert np.all(np.isfinite(objective_curvature))
    assert np.all(np.isfinite(constraint_jacobian))
    assert payload["pressure_hessian_backend"] == "cppad"
    assert payload["pressure_hessian_shape"] == (3, 3)
    assert np.all(np.isfinite(pressure_hessian))
    assert pressure_hessian == pytest.approx(pressure_hessian.T, rel=1.0e-12, abs=1.0e-8)
    assert constraint_jacobian[0, :] == pytest.approx(expected_pressure_jacobian, rel=1.0e-11, abs=1.0e-8)


def test_eos_phase_block_reports_association_implicit_second_order_data() -> None:
    mix = _methanol_cyclohexane_mixture()
    amounts = np.asarray([0.5, 0.5], dtype=float)
    temperature = 298.15
    density = 1000.0
    volume = float(amounts.sum() / density)
    composition = amounts / amounts.sum()
    state = mix.state(T=temperature, rho=density, x=composition, phase="liquid")

    payload = _core._native_eos_phase_block(mix._native, temperature, state.pressure(), amounts.tolist(), volume)

    objective_curvature = np.asarray(payload["objective_curvature_row_major"], dtype=float).reshape((3, 3))
    constraint_jacobian = np.asarray(payload["constraint_jacobian_row_major"], dtype=float).reshape((1, 3))
    pressure_hessian = np.asarray(payload["pressure_hessian_row_major"], dtype=float).reshape((3, 3))
    expected_pressure_jacobian = -payload["gas_constant_temperature"] * objective_curvature[-1, :]

    assert payload["objective_curvature_backend"] == "cppad_implicit_association"
    assert payload["objective_curvature_shape"] == (3, 3)
    assert payload["constraint_jacobian_backend"] == "cppad_implicit"
    assert payload["pressure_hessian_backend"] == "cppad_implicit_association"
    assert payload["pressure_hessian_shape"] == (3, 3)
    assert np.all(np.isfinite(objective_curvature))
    assert np.all(np.isfinite(pressure_hessian))
    assert objective_curvature == pytest.approx(objective_curvature.T, rel=1.0e-11, abs=1.0e-8)
    assert pressure_hessian == pytest.approx(pressure_hessian.T, rel=1.0e-11, abs=1.0e-8)
    assert constraint_jacobian[0, :] == pytest.approx(expected_pressure_jacobian, rel=1.0e-8, abs=1.0e-6)


def test_eos_phase_system_assembles_two_phase_material_balance_and_objective() -> None:
    mix, temperature, phase_amounts, volumes, feed_amounts, target_pressure = _two_phase_binary_case()

    payload = _core._native_eos_phase_system(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
    )
    phase_blocks = [
        _core._native_eos_phase_block(mix._native, temperature, target_pressure, phase.tolist(), volume)
        for phase, volume in zip(phase_amounts, volumes, strict=True)
    ]

    assert payload["block"] == "eos_phase_system"
    assert payload["phase_count"] == 2
    assert payload["species_count"] == 2
    assert payload["variable_names"] == [
        "phase_0.n_0",
        "phase_0.n_1",
        "phase_0.volume",
        "phase_1.n_0",
        "phase_1.n_1",
        "phase_1.volume",
    ]
    assert payload["constraint_names"] == [
        "material_balance_0",
        "material_balance_1",
        "phase_0.pressure_consistency",
        "phase_1.pressure_consistency",
    ]
    assert payload["constraints"][:2] == pytest.approx([0.0, 0.0], abs=1.0e-14)
    assert payload["objective"] == pytest.approx(sum(block["objective"] for block in phase_blocks))
    assert payload["gradient"] == pytest.approx(
        phase_blocks[0]["gradient"] + phase_blocks[1]["gradient"],
        rel=1.0e-12,
        abs=1.0e-12,
    )


def test_eos_phase_system_reports_exact_material_and_pressure_jacobian_rows() -> None:
    mix, temperature, phase_amounts, volumes, feed_amounts, target_pressure = _two_phase_binary_case()

    payload = _core._native_eos_phase_system(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
    )
    phase_blocks = [
        _core._native_eos_phase_block(mix._native, temperature, target_pressure, phase.tolist(), volume)
        for phase, volume in zip(phase_amounts, volumes, strict=True)
    ]

    assert payload["constraint_jacobian_backend"] == "analytic_cppad"
    assert payload["constraint_jacobian_shape"] == (4, 6)
    jacobian = np.asarray(payload["constraint_jacobian_row_major"], dtype=float).reshape((4, 6))
    assert np.array_equal(
        jacobian[:2, :],
        np.asarray(
            [
                [1.0, 0.0, 0.0, 1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0, 1.0, 0.0],
            ],
            dtype=float,
        ),
    )
    assert jacobian[2, :3] == pytest.approx(phase_blocks[0]["pressure_jacobian"], rel=1.0e-12, abs=1.0e-8)
    assert jacobian[2, 3:] == pytest.approx([0.0, 0.0, 0.0], abs=0.0)
    assert jacobian[3, :3] == pytest.approx([0.0, 0.0, 0.0], abs=0.0)
    assert jacobian[3, 3:] == pytest.approx(phase_blocks[1]["pressure_jacobian"], rel=1.0e-12, abs=1.0e-8)


def test_eos_phase_system_reports_objective_and_pressure_constraint_hessians() -> None:
    mix, temperature, phase_amounts, volumes, feed_amounts, target_pressure = _two_phase_binary_case()

    payload = _core._native_eos_phase_system(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
    )
    phase_blocks = [
        _core._native_eos_phase_block(mix._native, temperature, target_pressure, phase.tolist(), volume)
        for phase, volume in zip(phase_amounts, volumes, strict=True)
    ]

    objective_hessian = np.asarray(payload["objective_hessian_row_major"], dtype=float).reshape((6, 6))
    constraint_hessians = np.asarray(payload["constraint_hessian_tensor_row_major"], dtype=float).reshape((4, 6, 6))
    first_objective = np.asarray(phase_blocks[0]["objective_curvature_row_major"], dtype=float).reshape((3, 3))
    second_objective = np.asarray(phase_blocks[1]["objective_curvature_row_major"], dtype=float).reshape((3, 3))
    first_pressure = np.asarray(phase_blocks[0]["pressure_hessian_row_major"], dtype=float).reshape((3, 3))
    second_pressure = np.asarray(phase_blocks[1]["pressure_hessian_row_major"], dtype=float).reshape((3, 3))

    assert payload["objective_hessian_backend"] == "cppad_phase_blocks"
    assert payload["objective_hessian_shape"] == (6, 6)
    assert payload["constraint_hessian_backend"] == "cppad_phase_blocks"
    assert payload["constraint_hessian_shape"] == (4, 6)
    assert payload["constraint_has_hessian"] == [False, False, True, True]
    assert np.all(np.isfinite(objective_hessian))
    assert objective_hessian[:3, :3] == pytest.approx(first_objective, rel=1.0e-12, abs=1.0e-8)
    assert objective_hessian[3:, 3:] == pytest.approx(second_objective, rel=1.0e-12, abs=1.0e-8)
    assert objective_hessian[:3, 3:] == pytest.approx(np.zeros((3, 3)), abs=0.0)
    assert objective_hessian[3:, :3] == pytest.approx(np.zeros((3, 3)), abs=0.0)
    assert constraint_hessians[0] == pytest.approx(np.zeros((6, 6)), abs=0.0)
    assert constraint_hessians[1] == pytest.approx(np.zeros((6, 6)), abs=0.0)
    assert constraint_hessians[2, :3, :3] == pytest.approx(first_pressure, rel=1.0e-12, abs=1.0e-8)
    assert constraint_hessians[2, 3:, :] == pytest.approx(np.zeros((3, 6)), abs=0.0)
    assert constraint_hessians[3, 3:, 3:] == pytest.approx(second_pressure, rel=1.0e-12, abs=1.0e-8)
    assert constraint_hessians[3, :3, :] == pytest.approx(np.zeros((3, 6)), abs=0.0)


def test_eos_phase_system_can_append_phase_charge_balance_rows() -> None:
    mix, temperature, phase_amounts, volumes, feed_amounts, target_pressure = _two_phase_binary_case()
    charges = np.asarray([1.0, -1.0], dtype=float)

    payload = _core._native_eos_phase_system(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
        charges.tolist(),
    )

    assert payload["phase_charge_residuals"] == pytest.approx(
        [float(phase @ charges) for phase in phase_amounts],
        abs=1.0e-14,
    )
    assert payload["constraint_names"][-2:] == ["phase_0.charge_balance", "phase_1.charge_balance"]
    assert payload["constraint_jacobian_shape"] == (6, 6)
    jacobian = np.asarray(payload["constraint_jacobian_row_major"], dtype=float).reshape((6, 6))
    assert jacobian[4, :] == pytest.approx([1.0, -1.0, 0.0, 0.0, 0.0, 0.0], abs=0.0)
    assert jacobian[5, :] == pytest.approx([0.0, 0.0, 0.0, 1.0, -1.0, 0.0], abs=0.0)


def test_eos_phase_block_embeds_electrolyte_contribution_terms() -> None:
    mix = _ionic_mixture()
    temperature = 298.15
    composition = np.asarray([0.9998, 1.0e-4, 1.0e-4], dtype=float)
    amounts = composition.copy()
    density = 55344.274540081075
    volume = float(amounts.sum() / density)
    state = mix.state(T=temperature, rho=density, x=composition, phase="liq")
    helmholtz = state.residual_helmholtz(return_contribution_terms=True)

    standalone = _core._native_electrolyte_contribution_block(
        mix._native,
        temperature,
        density,
        composition.tolist(),
        amounts.tolist(),
    )
    payload = _core._native_eos_phase_block(
        mix._native,
        temperature,
        state.pressure(),
        amounts.tolist(),
        volume,
    )

    for block in (standalone, payload["electrolyte_terms"]):
        assert block["block"] == "electrolyte_contribution"
        assert block["value_backend"] == "native_eos"
        assert block["term_basis"] == "dimensionless_residual_helmholtz"
        assert block["active"] is True
        assert block["charges"] == pytest.approx([0.0, 1.0, -1.0])
        assert block["phase_charge_residual"] == pytest.approx(0.0, abs=1.0e-14)
        assert block["ion_residual_helmholtz"] == pytest.approx(helmholtz["terms"]["ion"])
        assert block["born_residual_helmholtz"] == pytest.approx(helmholtz["terms"]["born"])
        assert block["electrolyte_residual_helmholtz"] == pytest.approx(
            helmholtz["terms"]["ion"] + helmholtz["terms"]["born"]
        )
        assert block["total_residual_helmholtz"] == pytest.approx(helmholtz["total"])


def test_eos_phase_system_can_append_association_mass_action_rows() -> None:
    mix = _binary_two_site_associating_mixture()
    temperature = 298.15
    phase_amounts = [
        np.asarray([0.7, 0.3], dtype=float),
        np.asarray([0.1, 0.9], dtype=float),
    ]
    volumes = [float(phase_amounts[0].sum() / 80.0), float(phase_amounts[1].sum() / 140.0)]
    feed_amounts = phase_amounts[0] + phase_amounts[1]
    target_pressure = 1.0e5
    site_component_index = np.asarray([0, 0, 1, 1], dtype=int)
    site_count = site_component_index.size
    site_fractions = [
        np.asarray([0.8, 0.6, 0.7, 0.5], dtype=float),
        np.asarray([0.9, 0.7, 0.65, 0.55], dtype=float),
    ]
    delta = np.asarray(
        [
            [0.0, 2.0, 1.2, 0.0],
            [3.0, 0.0, 0.0, 1.1],
            [1.4, 0.0, 0.0, 2.2],
            [0.0, 1.3, 2.5, 0.0],
        ],
        dtype=float,
    )

    payload = _core._native_eos_phase_system(
        mix._native,
        temperature,
        target_pressure,
        [phase.tolist() for phase in phase_amounts],
        volumes,
        feed_amounts.tolist(),
        [],
        [values.tolist() for values in site_fractions],
        delta.ravel().tolist(),
    )

    assert payload["association_site_count"] == site_count
    assert payload["association_site_component_index"] == site_component_index.tolist()
    assert payload["variable_names"] == [
        "phase_0.n_0",
        "phase_0.n_1",
        "phase_0.volume",
        "phase_0.association_site_0",
        "phase_0.association_site_1",
        "phase_0.association_site_2",
        "phase_0.association_site_3",
        "phase_1.n_0",
        "phase_1.n_1",
        "phase_1.volume",
        "phase_1.association_site_0",
        "phase_1.association_site_1",
        "phase_1.association_site_2",
        "phase_1.association_site_3",
    ]
    assert payload["constraint_names"][-8:] == [
        "phase_0.association_site_0",
        "phase_0.association_site_1",
        "phase_0.association_site_2",
        "phase_0.association_site_3",
        "phase_1.association_site_0",
        "phase_1.association_site_1",
        "phase_1.association_site_2",
        "phase_1.association_site_3",
    ]
    assert payload["constraint_jacobian_shape"] == (12, 14)
    assert payload["constraint_has_hessian"][-8:] == [True] * 8
    expected_phase_objectives = [
        float(
            np.sum(
                amounts[site_component_index]
                * (np.log(fractions) - 0.5 * fractions + 0.5)
            )
        )
        for amounts, fractions in zip(phase_amounts, site_fractions, strict=True)
    ]
    expected_association_objective = sum(expected_phase_objectives)
    base_objective = sum(block["objective"] for block in payload["phase_blocks"])
    gradient = np.asarray(payload["gradient"], dtype=float)

    assert payload["phase_association_objectives"] == pytest.approx(expected_phase_objectives)
    assert payload["association_objective"] == pytest.approx(expected_association_objective)
    assert payload["objective"] == pytest.approx(base_objective + expected_association_objective)

    jacobian = np.asarray(payload["constraint_jacobian_row_major"], dtype=float).reshape((12, 14))
    objective_hessian = np.asarray(payload["objective_hessian_row_major"], dtype=float).reshape((14, 14))
    constraint_hessians = np.asarray(payload["constraint_hessian_tensor_row_major"], dtype=float).reshape((12, 14, 14))
    association_rows = jacobian[4:, :]
    assert association_rows[:site_count, 7:] == pytest.approx(np.zeros((site_count, 7)), abs=0.0)
    assert association_rows[site_count:, :7] == pytest.approx(np.zeros((site_count, 7)), abs=0.0)

    for phase_index, (amounts, volume, fractions) in enumerate(
        zip(phase_amounts, volumes, site_fractions, strict=True)
    ):
        composition = amounts / amounts.sum()
        density = amounts.sum() / volume
        site_composition = composition[site_component_index]
        block = _core._native_association_mass_action_block(
            density,
            fractions.tolist(),
            site_composition.tolist(),
            delta.ravel().tolist(),
        )
        row_offset = phase_index * site_count
        col_offset = phase_index * 7
        site_col_offset = col_offset + 3
        expected_site_terms = np.log(fractions) - 0.5 * fractions + 0.5
        expected_amount_gradient = np.asarray(
            [expected_site_terms[site_component_index == component].sum() for component in range(amounts.size)],
            dtype=float,
        )
        expected_site_gradient = amounts[site_component_index] * (1.0 / fractions - 0.5)

        assert gradient[col_offset : col_offset + amounts.size] == pytest.approx(
            np.asarray(payload["phase_blocks"][phase_index]["gradient"], dtype=float)[:2]
            + expected_amount_gradient,
            rel=1.0e-14,
            abs=1.0e-14,
        )
        assert gradient[site_col_offset : site_col_offset + site_count] == pytest.approx(
            expected_site_gradient,
            rel=1.0e-14,
            abs=1.0e-14,
        )
        assert payload["phase_association_residuals"][row_offset : row_offset + site_count] == pytest.approx(
            block["residuals"],
            rel=1.0e-14,
            abs=1.0e-14,
        )
        assert payload["constraints"][4 + row_offset : 4 + row_offset + site_count] == pytest.approx(
            block["residuals"],
            rel=1.0e-14,
            abs=1.0e-14,
        )

        expected_site_jacobian = np.asarray(block["site_fraction_jacobian_row_major"], dtype=float).reshape(
            (site_count, site_count)
        )
        assert association_rows[row_offset : row_offset + site_count, site_col_offset : site_col_offset + site_count] == pytest.approx(
            expected_site_jacobian,
            rel=1.0e-14,
            abs=1.0e-14,
        )
        for site in range(site_count):
            expected_amount_derivative = np.asarray(
                [
                    fractions[site] * np.sum(fractions[site_component_index == component] * delta[site, site_component_index == component]) / volume
                    for component in range(amounts.size)
                ],
                dtype=float,
            )
            amount_sum = float(np.sum(amounts[site_component_index] * fractions * delta[site, :]))
            expected_volume_derivative = -fractions[site] * amount_sum / (volume * volume)
            assert association_rows[row_offset + site, col_offset : col_offset + amounts.size] == pytest.approx(
                expected_amount_derivative,
                rel=1.0e-14,
                abs=1.0e-14,
            )
            assert association_rows[row_offset + site, col_offset + 2] == pytest.approx(
                expected_volume_derivative,
                rel=1.0e-14,
                abs=1.0e-14,
            )
            target_row = 4 + row_offset + site
            local_hessian = constraint_hessians[
                target_row,
                col_offset : col_offset + 7,
                col_offset : col_offset + 7,
            ]
            expected_hessian = np.zeros((7, 7), dtype=float)
            for component in range(amounts.size):
                owned = site_component_index == component
                component_delta = float(np.sum(fractions[owned] * delta[site, owned]))
                expected_hessian[component, 2] = -fractions[site] * component_delta / (volume * volume)
                expected_hessian[2, component] = expected_hessian[component, 2]
                for other_site in range(site_count):
                    value = 0.0
                    if site == other_site:
                        value += component_delta / volume
                    if site_component_index[other_site] == component:
                        value += fractions[site] * delta[site, other_site] / volume
                    expected_hessian[component, 3 + other_site] = value
                    expected_hessian[3 + other_site, component] = value
            expected_hessian[2, 2] = 2.0 * fractions[site] * amount_sum / (volume ** 3)
            for left_site in range(site_count):
                value = -(
                    (amount_sum if site == left_site else 0.0)
                    + fractions[site] * amounts[site_component_index[left_site]] * delta[site, left_site]
                ) / (volume * volume)
                expected_hessian[2, 3 + left_site] = value
                expected_hessian[3 + left_site, 2] = value
                for right_site in range(site_count):
                    site_value = 0.0
                    if site == left_site:
                        site_value += amounts[site_component_index[right_site]] * delta[site, right_site] / volume
                    if site == right_site:
                        site_value += amounts[site_component_index[left_site]] * delta[site, left_site] / volume
                    expected_hessian[3 + left_site, 3 + right_site] = site_value
            assert local_hessian == pytest.approx(expected_hessian, rel=1.0e-14, abs=1.0e-14)
            assert np.all(np.isfinite(local_hessian))
            assert local_hessian == pytest.approx(local_hessian.T, rel=1.0e-14, abs=1.0e-14)

        for site in range(site_count):
            owner = site_component_index[site]
            site_term = 1.0 / fractions[site] - 0.5
            assert objective_hessian[col_offset + owner, site_col_offset + site] == pytest.approx(site_term)
            assert objective_hessian[site_col_offset + site, col_offset + owner] == pytest.approx(site_term)
            assert objective_hessian[site_col_offset + site, site_col_offset + site] == pytest.approx(
                -amounts[owner] / (fractions[site] ** 2)
            )
