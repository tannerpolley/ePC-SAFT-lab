from __future__ import annotations

import numpy as np
from epcsaft import ParameterSet
from epcsaft.model.parameters import (
    ConstantInteractionRecord,
    InteractionProvenance,
    PureRecord,
    StructuralZeroPolicy,
)
from epcsaft.state.native_adapter import ePCSAFTMixture


def _neutral_state():
    species = ["A", "B", "C"]
    params = {
        "m": np.asarray([1.0000, 1.6069, 2.0020]),
        "s": np.asarray([3.7039, 3.5206, 3.6184]),
        "e": np.asarray([150.03, 191.42, 208.11]),
        "k_ij": np.asarray(
            [
                [0.0, 3.0e-4, 1.15e-2],
                [3.0e-4, 0.0, 5.10e-3],
                [1.15e-2, 5.10e-3, 0.0],
            ]
        ),
    }
    mix = ePCSAFTMixture.from_params(params, species=species)
    state = mix.state(T=233.15, x=np.array([0.1, 0.3, 0.6]), rho=14330.417110)
    return state, species


def _ionic_params():
    t = 298.15
    s_water = 2.7927 + 10.11 * np.exp(-0.01775 * t) - 1.417 * np.exp(-0.01146 * t)
    return {
        "MW": np.asarray([18.01528e-3, 22.98e-3, 35.45e-3]),
        "m": np.asarray([1.2047, 1.0, 1.0]),
        "s": np.asarray([s_water, 2.8232, 2.7560]),
        "e": np.asarray([353.95, 230.0, 170.0]),
        "e_assoc": np.asarray([2425.7, 0.0, 0.0]),
        "vol_a": np.asarray([0.04509, 0.0, 0.0]),
        "assoc_scheme": ["2B", None, None],
        "z": np.asarray([0.0, 1.0, -1.0]),
        "dielc": np.asarray([78.09, 8.0, 8.0]),
        "d_born": np.asarray([0.0, 3.445, 4.1]),
        "f_solv": np.asarray([1.5, 1.0, 1.0]),
        "k_ij": np.asarray(
            [
                [0.0, 0.0045, -0.25],
                [0.0045, 0.0, 0.317],
                [-0.25, 0.317, 0.0],
            ]
        ),
        "l_ij": np.zeros((3, 3)),
        "k_hb": np.zeros((3, 3)),
    }


def ionic_parameter_set(*, association: bool = True) -> ParameterSet:
    params = _ionic_params()
    species = ("water", "Na+", "Cl-")
    pure_records = tuple(
        PureRecord(
            component=component,
            molar_mass=float(params["MW"][index]),
            m=float(params["m"][index]),
            sigma=float(params["s"][index]),
            epsilon_k=float(params["e"][index]),
            charge=float(params["z"][index]),
            epsilon_k_ab=float(params["e_assoc"][index]) if association else 0.0,
            kappa_ab=float(params["vol_a"][index]) if association else 0.0,
            association_scheme=params["assoc_scheme"][index] if association else None,
            relative_permittivity=float(params["dielc"][index]),
            born_diameter=float(params["d_born"][index]),
            solvation_factor=float(params["f_solv"][index]),
        )
        for index, component in enumerate(species)
    )
    return ParameterSet.from_records(
        pure_records,
        (
            ConstantInteractionRecord(
                "k_ij",
                ("water", "Na+"),
                0.0045,
                InteractionProvenance("literature", "Bülow, Ascani, and Held 2020 Table 2"),
            ),
            ConstantInteractionRecord(
                "k_ij",
                ("water", "Cl-"),
                -0.25,
                InteractionProvenance("literature", "Bülow, Ascani, and Held 2020 Table 2"),
            ),
            ConstantInteractionRecord(
                "k_ij",
                ("Na+", "Cl-"),
                0.317,
                InteractionProvenance("literature", "Bülow, Ascani, and Held 2020 Table 3"),
            ),
        ),
        interaction_policies=tuple(
            StructuralZeroPolicy(
                family,
                pair,
                reason,
                InteractionProvenance("model_structural_zero", source),
            )
            for pair in (("water", "Na+"), ("water", "Cl-"), ("Na+", "Cl-"))
            for family, reason, source in (
                (
                    "l_ij",
                    "The pair uses the uncorrected Lorentz diameter rule.",
                    "Lorentz diameter rule / EqID sigma_mixing",
                ),
                (
                    "k_hb_ij",
                    "Each pair contains an ion with no active association sites.",
                    "inactive association topology / EqID kappa_assoc_mixing",
                ),
            )
        ),
        metadata={
            "source": (
                "Bülow, Ascani, and Held 2020 Tables 1-3; "
                "Khudaida et al. 2026 Table 5 Born diameters"
            ),
            "source_backed": association,
            "model_variant": (
                "source_association_topology"
                if association
                else "test_nonassociating_topology"
            ),
        },
    )


def _ionic_state():
    t = 298.15
    species = ["water", "Na+", "Cl-"]
    params = _ionic_params()
    mix = ePCSAFTMixture.from_params(params, species=species)
    state = mix.state(T=t, x=np.array([0.9998, 1.0e-4, 1.0e-4]), P=1.0e5)
    return state, species


def _ionic_state_with_elec_model(elec_model):
    t = 298.15
    species = ["water", "Na+", "Cl-"]
    params = _ionic_params()
    params["elec_model"] = elec_model
    mix = ePCSAFTMixture.from_params(params, species=species)
    state = mix.state(T=t, x=np.array([0.9998, 1.0e-4, 1.0e-4]), P=1.0e5)
    return state, species


def _assert_array(actual, expected, rtol=1e-8, atol=1e-10):
    actual_array = np.asarray(actual, dtype=float)
    expected_array = np.asarray(expected, dtype=float)
    if actual_array.shape != expected_array.shape:
        raise AssertionError(f"shape mismatch: {actual_array.shape} != {expected_array.shape}")
    if not np.allclose(actual_array, expected_array, rtol=rtol, atol=atol):
        diff = np.max(np.abs(actual_array - expected_array)) if actual_array.size else 0.0
        raise AssertionError(f"array mismatch: max abs diff {diff}")


def _sum_term_arrays(terms):
    total = None
    for value in terms.values():
        arr = np.asarray(value, dtype=float)
        total = arr.copy() if total is None else total + arr
    return total
