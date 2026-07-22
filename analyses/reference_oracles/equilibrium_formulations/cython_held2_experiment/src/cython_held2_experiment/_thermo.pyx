from __future__ import annotations

import hashlib
import json
import math
from importlib.resources import files

import cppad_py
import numpy as np


_PARAMETER_RESOURCE = "data/figiel_2025_h2o_nacl.json"
_PARAMETER_SHA256 = "1212c1e15a2ee2d8747b178e34e848dd6ba171268ed237675f5b26c16f839029"
_PARAMETERS = None

_AVOGADRO = 6.02214076e23
_GAS_CONSTANT = 8.31446261815324
_ELEMENTARY_CHARGE = 1.602176634e-19
_VACUUM_PERMITTIVITY = 8.8541878128e-12
_BOLTZMANN = 1.380649e-23
_PI = 3.141592653589793238462643383279502884
_NUMBER_DENSITY_FACTOR = 6.02214076e-7

_A0 = (
    0.9105631445,
    0.6361281449,
    2.6861347891,
    -26.547362491,
    97.759208784,
    -159.59154087,
    91.297774084,
)
_A1 = (
    -0.3084016918,
    0.1860531159,
    -2.5030047259,
    21.419793629,
    -65.255885330,
    83.318680481,
    -33.746922930,
)
_A2 = (
    -0.0906148351,
    0.4527842806,
    0.5962700728,
    -1.7241829131,
    -4.1302112531,
    13.776631870,
    -8.6728470368,
)
_B0 = (
    0.7240946941,
    2.2382791861,
    -4.0025849485,
    -21.003576815,
    26.855641363,
    206.55133841,
    -355.60235612,
)
_B1 = (
    -0.5755498075,
    0.6995095521,
    3.8925673390,
    -17.215471648,
    192.67226447,
    -161.82646165,
    -165.20769346,
)
_B2 = (
    0.0976883116,
    -0.2557574982,
    -9.1558561530,
    20.642075974,
    -38.804430052,
    93.626774077,
    -29.666905585,
)


def _load_parameters():
    global _PARAMETERS
    if _PARAMETERS is None:
        payload = files(__package__).joinpath(_PARAMETER_RESOURCE).read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != _PARAMETER_SHA256:
            raise RuntimeError("Figiel parameter packet hash mismatch")
        _PARAMETERS = json.loads(payload)
    return _PARAMETERS


def source_identity():
    parameters = _load_parameters()
    subject = parameters["provider_subject"]
    return {
        "model_id": parameters["model_id"],
        "parameter_sha256": _PARAMETER_SHA256,
        "provider_commit": subject["commit"],
        "provider_tree": subject["tree"],
        "selected_model_fingerprint": subject["selected_model_fingerprint"],
        "provider_bundle": subject["bundle"],
        "diameter_mixing_rule": parameters["diameter_mixing_rule"],
        "species_order": ("water", "sodium-cation", "chloride-anion"),
        "source_domain": dict(parameters["domain"]),
        "authority_effect": "none",
    }


def _validate_state(temperature, amounts, volume, parameters):
    if not math.isfinite(temperature) or not math.isfinite(volume):
        raise ValueError("temperature and volume must be finite")
    if volume <= 0.0:
        raise ValueError("volume must be positive")
    if len(amounts) != 3:
        raise ValueError("amounts must follow water, sodium-cation, chloride-anion order")
    values = tuple(float(value) for value in amounts)
    if any(not math.isfinite(value) or value <= 0.0 for value in values):
        raise ValueError("amounts must be positive and finite")
    domain = parameters["domain"]
    if not (
        domain["temperature_min_k"] <= temperature
        <= domain["temperature_max_k"]
    ):
        raise ValueError("temperature is outside the Figiel source domain")
    total = sum(values)
    if abs(values[1] - values[2]) / total > 1.0e-12:
        raise ValueError("electrolyte amounts must be electroneutral")
    ion_fraction = (values[1] + values[2]) / total
    if ion_fraction > domain["ion_mole_fraction_max"] + 1.0e-12:
        raise ValueError("ion mole fraction exceeds the Figiel source domain")
    return values


def _sigma_double(temperature, parameters):
    sigma = []
    for component in parameters["components"]:
        value = component["sigma_constant_angstrom"]
        for amplitude, exponent in component["sigma_terms"]:
            value += amplitude * math.exp(exponent * temperature)
        sigma.append(value)
    return sigma


def _diameter_double(temperature, parameters, sigma):
    diameter = []
    for component, sigma_i in zip(parameters["components"], sigma, strict=True):
        if component["charge_number"] == 0:
            value = sigma_i * (
                1.0
                - 0.12
                * math.exp(-3.0 * component["dispersion_energy_over_k"] / temperature)
            )
        else:
            value = 0.88 * sigma_i
        diameter.append(value)
    return diameter


def _packing_fraction_double(temperature, amounts, volume, parameters):
    total = sum(amounts)
    fractions = [value / total for value in amounts]
    sigma = _sigma_double(temperature, parameters)
    diameter = _diameter_double(temperature, parameters, sigma)
    moment = sum(
        fraction * component["segment_count"] * diameter_i**3
        for fraction, component, diameter_i in zip(
            fractions, parameters["components"], diameter, strict=True
        )
    )
    return _PI / 6.0 * total / volume * _AVOGADRO / 1.0e30 * moment


def _association_delta_double(temperature, amounts, volume, parameters):
    total = sum(amounts)
    fractions = [value / total for value in amounts]
    density = total / volume
    sigma = _sigma_double(temperature, parameters)
    diameter = _diameter_double(temperature, parameters, sigma)
    number_density = density * _NUMBER_DENSITY_FACTOR
    zeta_2 = 0.0
    zeta_3 = 0.0
    for fraction, component, diameter_i in zip(
        fractions, parameters["components"], diameter, strict=True
    ):
        weight = fraction * component["segment_count"]
        zeta_2 += _PI / 6.0 * number_density * weight * diameter_i**2
        zeta_3 += _PI / 6.0 * number_density * weight * diameter_i**3
    reduced_diameter = diameter[0] / 2.0
    one_minus_eta = 1.0 - zeta_3
    contact = (
        1.0 / one_minus_eta
        + 3.0 * reduced_diameter * zeta_2 / one_minus_eta**2
        + 2.0 * reduced_diameter**2 * zeta_2**2 / one_minus_eta**3
    )
    association = parameters["association"]
    delta = (
        contact
        * math.expm1(association["energy_over_k"] / temperature)
        * sigma[0] ** 3
        * association["volume"]
    )
    return density, fractions, delta


def _association_residuals(site_fractions, density, fractions, delta):
    number_density = density * _NUMBER_DENSITY_FACTOR
    coupling = number_density * fractions[0] * delta
    x_a, x_b = site_fractions
    return np.array(
        [x_a * (1.0 + coupling * x_b) - 1.0,
         x_b * (1.0 + coupling * x_a) - 1.0],
        dtype=float,
    )


def _solve_site_fractions(temperature, amounts, volume, parameters):
    density, fractions, delta = _association_delta_double(
        temperature, amounts, volume, parameters
    )
    association = parameters["association"]
    values = np.ones(2, dtype=float)
    number_density = density * _NUMBER_DENSITY_FACTOR
    coupling = number_density * fractions[0] * delta
    for iteration in range(1, association["solver_max_iterations"] + 1):
        fixed = np.array(
            [1.0 / (1.0 + coupling * values[1]),
             1.0 / (1.0 + coupling * values[0])],
            dtype=float,
        )
        values = 0.5 * (values + fixed)
        residuals = _association_residuals(values, density, fractions, delta)
        if np.any(~np.isfinite(values)) or np.any(values <= 0.0) or np.any(values > 1.0):
            raise RuntimeError("association solve left the physical site-fraction domain")
        if float(np.max(np.abs(residuals))) <= association["solver_tolerance"]:
            return values, iteration, residuals
    raise RuntimeError("association solve did not converge")


def _ad_polynomial(coefficients, eta):
    value = coefficients[-1]
    for coefficient in reversed(coefficients[:-1]):
        value = value * eta + coefficient
    return value


def _ad_finite_size_chi(reduced, use_series):
    if use_series:
        reduced_2 = reduced * reduced
        reduced_3 = reduced_2 * reduced
        reduced_4 = reduced_3 * reduced
        reduced_5 = reduced_4 * reduced
        reduced_6 = reduced_5 * reduced
        return (
            1.0
            - 0.75 * reduced
            + 0.6 * reduced_2
            - 0.5 * reduced_3
            + (3.0 / 7.0) * reduced_4
            - 0.375 * reduced_5
            + (1.0 / 3.0) * reduced_6
        )
    return 3.0 * ((1.0 + reduced).log() - reduced + 0.5 * reduced * reduced) / (
        reduced * reduced * reduced
    )


def _ad_model(independent, parameters, series_flags):
    temperature = independent[0]
    amounts = [independent[1], independent[2], independent[3]]
    volume = independent[4]
    site_fractions = [independent[5], independent[6]]
    total = amounts[0] + amounts[1] + amounts[2]
    density = total / volume
    fractions = [amount / total for amount in amounts]
    components = parameters["components"]

    sigma = []
    diameter = []
    for component in components:
        sigma_i = component["sigma_constant_angstrom"]
        for amplitude, exponent in component["sigma_terms"]:
            sigma_i += amplitude * (exponent * temperature).exp()
        sigma.append(sigma_i)
        if component["charge_number"] == 0:
            diameter.append(
                sigma_i
                * (
                    1.0
                    - 0.12
                    * (-3.0 * component["dispersion_energy_over_k"] / temperature).exp()
                )
            )
        else:
            diameter.append(0.88 * sigma_i)

    number_density = density * (_AVOGADRO / 1.0e30)
    mean_segment_count = sum(
        fractions[index] * components[index]["segment_count"] for index in range(3)
    )
    zeta = []
    for order in range(3):
        moment = sum(
            fractions[index]
            * components[index]["segment_count"]
            * diameter[index] ** order
            for index in range(3)
        )
        zeta.append(_PI / 6.0 * number_density * moment)
    zeta_3 = _PI / 6.0 * number_density * sum(
        fractions[index] * components[index]["segment_count"] * diameter[index] ** 3
        for index in range(3)
    )
    zeta.append(zeta_3)
    one_minus_eta = 1.0 - zeta_3
    hard_sphere = (
        3.0 * zeta[1] * zeta[2] / one_minus_eta
        + zeta[2] ** 3 / (zeta_3 * one_minus_eta**2)
        + (zeta[2] ** 3 / zeta_3**2 - zeta[0]) * one_minus_eta.log()
    ) / zeta[0]
    hard_chain = mean_segment_count * hard_sphere
    for index in range(3):
        contact_diameter = diameter[index] / 2.0
        contact = (
            1.0 / one_minus_eta
            + contact_diameter * 3.0 * zeta[2] / one_minus_eta**2
            + contact_diameter**2 * 2.0 * zeta[2] ** 2 / one_minus_eta**3
        )
        hard_chain -= (
            fractions[index]
            * (components[index]["segment_count"] - 1.0)
            * contact.log()
        )

    chain_factor_1 = (mean_segment_count - 1.0) / mean_segment_count
    chain_factor_2 = chain_factor_1 * (mean_segment_count - 2.0) / mean_segment_count
    coefficients_a = [
        _A0[index] + chain_factor_1 * _A1[index] + chain_factor_2 * _A2[index]
        for index in range(7)
    ]
    coefficients_b = [
        _B0[index] + chain_factor_1 * _B1[index] + chain_factor_2 * _B2[index]
        for index in range(7)
    ]
    integral_1 = _ad_polynomial(coefficients_a, zeta_3)
    integral_2 = _ad_polynomial(coefficients_b, zeta_3)
    eta_2 = zeta_3 * zeta_3
    eta_3 = eta_2 * zeta_3
    eta_4 = eta_3 * zeta_3
    c1 = 1.0 / (
        1.0
        + mean_segment_count * (8.0 * zeta_3 - 2.0 * eta_2) / one_minus_eta**4
        + (1.0 - mean_segment_count)
        * (20.0 * zeta_3 - 27.0 * eta_2 + 12.0 * eta_3 - 2.0 * eta_4)
        / ((one_minus_eta * (2.0 - zeta_3)) ** 2)
    )
    first_moment = 0.0
    second_moment = 0.0
    for left in range(3):
        for right in range(3):
            sigma_ij = 0.5 * (sigma[left] + sigma[right])
            charge_product = (
                components[left]["charge_number"] * components[right]["charge_number"]
            )
            if charge_product > 0:
                epsilon_ij = 0.0
            else:
                epsilon_ij = math.sqrt(
                    components[left]["dispersion_energy_over_k"]
                    * components[right]["dispersion_energy_over_k"]
                ) * (1.0 - parameters["k_ij"][left][right])
            weight = (
                fractions[left]
                * fractions[right]
                * components[left]["segment_count"]
                * components[right]["segment_count"]
                * sigma_ij**3
            )
            first_moment += weight * epsilon_ij / temperature
            second_moment += weight * epsilon_ij**2 / temperature**2
    dispersion = (
        -2.0 * _PI * number_density * integral_1 * first_moment
        - _PI * number_density * mean_segment_count * c1 * integral_2 * second_moment
    )

    association_data = parameters["association"]
    reduced_diameter = diameter[0] / 2.0
    contact = (
        1.0 / one_minus_eta
        + 3.0 * reduced_diameter * zeta[2] / one_minus_eta**2
        + 2.0 * reduced_diameter**2 * zeta[2] ** 2 / one_minus_eta**3
    )
    delta = (
        contact
        * ((association_data["energy_over_k"] / temperature).exp() - 1.0)
        * sigma[0] ** 3
        * association_data["volume"]
    )
    association = fractions[0] * sum(
        site_fraction.log() - site_fraction / 2.0 + 0.5
        for site_fraction in site_fractions
    )
    association_number_density = density * _NUMBER_DENSITY_FACTOR
    coupling = association_number_density * fractions[0] * delta
    mass_action = [
        site_fractions[0] * (1.0 + coupling * site_fractions[1]) - 1.0,
        site_fractions[1] * (1.0 + coupling * site_fractions[0]) - 1.0,
    ]

    ion_fraction = fractions[1] + fractions[2]
    bulk_permittivity = components[0]["relative_permittivity"] / (
        1.0
        + parameters["electrolyte"]["dielectric_ion_suppression_coefficient"]
        * ion_fraction
    )
    charge_square_sum = fractions[1] + fractions[2]
    kappa = (
        density
        * _AVOGADRO
        * _ELEMENTARY_CHARGE**2
        * charge_square_sum
        / (_VACUUM_PERMITTIVITY * bulk_permittivity * _BOLTZMANN * temperature)
    ).sqrt()
    weighted_chi = 0.0
    for index in (1, 2):
        reduced = kappa * (0.88e-10 * sigma[index])
        weighted_chi += fractions[index] * _ad_finite_size_chi(
            reduced, series_flags[index]
        )
    debye_huckel = (
        -kappa
        * _ELEMENTARY_CHARGE**2
        * weighted_chi
        / (12.0 * _PI * _VACUUM_PERMITTIVITY * bulk_permittivity * _BOLTZMANN * temperature)
    )

    mixture_solvation = sum(
        fractions[index] * components[index]["solvation_factor"]
        for index in range(3)
    )
    radial_work = 0.0
    for index in (1, 2):
        born_diameter = components[index]["born_diameter_angstrom"] * 1.0e-10
        shell_diameter = born_diameter * (1.0 + mixture_solvation - 1.0)
        radial_work += fractions[index] * (
            (1.0 - 1.0 / bulk_permittivity) / shell_diameter
            + (
                1.0
                - 1.0 / parameters["electrolyte"]["ionic_region_relative_permittivity"]
            )
            * (1.0 / born_diameter - 1.0 / shell_diameter)
        )
    born_ssm_ds = (
        -_ELEMENTARY_CHARGE**2
        * radial_work
        / (4.0 * _PI * _VACUUM_PERMITTIVITY * _BOLTZMANN * temperature)
    )

    ideal = sum(amount * ((amount / volume).log() - 1.0) for amount in amounts)
    extensive = [
        ideal,
        total * hard_chain,
        total * dispersion,
        total * association,
        total * debye_huckel,
        total * born_ssm_ds,
    ]
    total_helmholtz = sum(extensive)
    return [total_helmholtz, *extensive, *mass_action], zeta_3, bulk_permittivity


def _series_flags(temperature, amounts, volume, parameters):
    total = sum(amounts)
    fractions = [value / total for value in amounts]
    density = total / volume
    sigma = _sigma_double(temperature, parameters)
    bulk_permittivity = parameters["components"][0]["relative_permittivity"] / (
        1.0
        + parameters["electrolyte"]["dielectric_ion_suppression_coefficient"]
        * (fractions[1] + fractions[2])
    )
    kappa = math.sqrt(
        density
        * _AVOGADRO
        * _ELEMENTARY_CHARGE**2
        * (fractions[1] + fractions[2])
        / (_VACUUM_PERMITTIVITY * bulk_permittivity * _BOLTZMANN * temperature)
    )
    return [False, kappa * 0.88e-10 * sigma[1] < 1.0e-3,
            kappa * 0.88e-10 * sigma[2] < 1.0e-3]


def _build_reduced_bundle(temperature, amounts, volume):
    parameters = _load_parameters()
    amounts = _validate_state(float(temperature), amounts, float(volume), parameters)
    eta = _packing_fraction_double(temperature, amounts, volume, parameters)
    if not math.isfinite(eta) or eta <= 0.0 or eta >= _PI / (3.0 * math.sqrt(2.0)):
        raise ValueError("packing fraction is outside the model domain")
    site_fractions, iterations, residuals = _solve_site_fractions(
        temperature, amounts, volume, parameters
    )
    point = np.array(
        [temperature, amounts[0], amounts[1], amounts[2], volume,
         site_fractions[0], site_fractions[1]],
        dtype=float,
    )
    independent = cppad_py.independent(point)
    dependents, _, _ = _ad_model(
        independent, parameters, _series_flags(temperature, amounts, volume, parameters)
    )
    recorded = np.empty(len(dependents), dtype=cppad_py.a_double)
    for index, value in enumerate(dependents):
        recorded[index] = value
    function = cppad_py.d_fun(independent, recorded)
    values = np.asarray(function.forward(0, point), dtype=float)
    jacobian = np.asarray(function.jacobian(point), dtype=float)

    physical_coordinates = 5
    residual_start = 7
    association_jacobian = jacobian[residual_start:, physical_coordinates:]
    association_physical = jacobian[residual_start:, :physical_coordinates]
    condition = float(np.linalg.cond(association_jacobian))
    if not math.isfinite(condition) or condition > parameters["association"]["jacobian_condition_max"]:
        raise RuntimeError("association Jacobian is singular or ill-conditioned")
    site_sensitivity = np.linalg.solve(association_jacobian, -association_physical)
    directions = np.zeros((physical_coordinates, len(point)), dtype=float)
    directions[:, :physical_coordinates] = np.eye(physical_coordinates)
    directions[:, physical_coordinates:] = site_sensitivity.T

    gradient = jacobian[0, :physical_coordinates] + (
        jacobian[0, physical_coordinates:] @ site_sensitivity
    )
    total_weights = np.zeros(len(dependents), dtype=float)
    total_weights[0] = 1.0
    total_hessian = np.asarray(function.hessian(point, total_weights), dtype=float)
    residual_hessians = []
    for residual in range(2):
        weights = np.zeros(len(dependents), dtype=float)
        weights[residual_start + residual] = 1.0
        residual_hessians.append(np.asarray(function.hessian(point, weights), dtype=float))
    hessian = np.empty((physical_coordinates, physical_coordinates), dtype=float)
    for left in range(physical_coordinates):
        for right in range(physical_coordinates):
            second_rhs = np.array(
                [
                    -(directions[left] @ residual_hessians[site] @ directions[right])
                    for site in range(2)
                ],
                dtype=float,
            )
            site_second = np.linalg.solve(association_jacobian, second_rhs)
            hessian[left, right] = (
                directions[left] @ total_hessian @ directions[right]
                + jacobian[0, physical_coordinates:] @ site_second
            )
    if not (
        np.all(np.isfinite(values))
        and np.all(np.isfinite(gradient))
        and np.all(np.isfinite(hessian))
    ):
        raise RuntimeError("thermodynamic tape produced nonfinite values")
    asymmetry = float(np.max(np.abs(hessian - hessian.T)))
    if asymmetry > 1.0e-8 * max(1.0, float(np.max(np.abs(hessian)))):
        raise RuntimeError("reduced Hessian is not symmetric")
    return {
        "values": values,
        "gradient": gradient,
        "hessian": hessian,
        "site_fractions": site_fractions,
        "association_iterations": iterations,
        "association_residuals": residuals,
        "association_jacobian_condition": condition,
        "packing_fraction": eta,
        "bulk_relative_permittivity": float(
            parameters["components"][0]["relative_permittivity"]
            / (
                1.0
                + parameters["electrolyte"]["dielectric_ion_suppression_coefficient"]
                * ((amounts[1] + amounts[2]) / sum(amounts))
            )
        ),
    }


def derivative_bundle(temperature, amounts, volume):
    bundle = _build_reduced_bundle(temperature, amounts, volume)
    return {
        "coordinate_order": ("temperature", "n_water", "n_sodium", "n_chloride", "volume"),
        "gradient": bundle["gradient"].tolist(),
        "hessian": bundle["hessian"].tolist(),
        "association": {
            "site_fractions": bundle["site_fractions"].tolist(),
            "iterations": bundle["association_iterations"],
            "residual_inf_norm": float(
                np.max(np.abs(bundle["association_residuals"]))
            ),
            "jacobian_condition": bundle["association_jacobian_condition"],
        },
        "solver_convergence": "passed",
        "numerical_convergence": "passed",
        "physical_validity": "passed",
        "globality_certificate": "not_applicable",
        "source_identity": source_identity(),
    }


def evaluate_state(temperature, amounts, volume):
    bundle = _build_reduced_bundle(temperature, amounts, volume)
    values = bundle["values"]
    gradient = bundle["gradient"]
    return {
        "helmholtz_over_rt": float(values[0]),
        "contributions": {
            "ideal": float(values[1]),
            "hard_chain": float(values[2]),
            "dispersion": float(values[3]),
            "association": float(values[4]),
            "debye_huckel": float(values[5]),
            "born_ssm_ds": float(values[6]),
        },
        "pressure_pa": float(-_GAS_CONSTANT * temperature * gradient[4]),
        "chemical_potential_inputs_over_rt": gradient[1:4].tolist(),
        "packing_fraction": bundle["packing_fraction"],
        "bulk_relative_permittivity": bundle["bulk_relative_permittivity"],
        "association": {
            "site_fractions": bundle["site_fractions"].tolist(),
            "iterations": bundle["association_iterations"],
            "residual_inf_norm": float(
                np.max(np.abs(bundle["association_residuals"]))
            ),
            "jacobian_condition": bundle["association_jacobian_condition"],
        },
        "solver_convergence": "passed",
        "numerical_convergence": "passed",
        "physical_validity": "passed",
        "globality_certificate": "not_applicable",
        "source_identity": source_identity(),
    }
