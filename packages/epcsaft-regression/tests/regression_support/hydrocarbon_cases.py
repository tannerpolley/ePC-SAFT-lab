from __future__ import annotations

import numpy as np
from epcsaft import ParameterSet
from epcsaft.model.parameters import BinaryRecord, PureRecord

HYDROCARBON_COMPONENTS = ("Methane", "Ethane", "Propane")
HYDROCARBON_LIQUID_X = (0.1, 0.3, 0.6)
HYDROCARBON_T = 233.15
HYDROCARBON_BUBBLE_P = 1_276_369.4735856401
HYDROCARBON_LIQUID_RHO = 14_330.417109760687
HYDROCARBON_VAPOR_RHO = 728.5617203262267
HYDROCARBON_VAPOR_Y = np.asarray([0.7246628928343289, 0.20293191372324873, 0.0724051934424223])
HYDROCARBON_FLASH_Z = tuple((0.5 * (np.asarray(HYDROCARBON_LIQUID_X) + HYDROCARBON_VAPOR_Y)).tolist())


def hydrocarbon_parameter_set() -> ParameterSet:
    pure_records = tuple(
        PureRecord(
            component=component,
            molar_mass=molar_mass,
            m=m,
            sigma=sigma,
            epsilon_k=epsilon_k,
            charge=0.0,
            epsilon_k_ab=0.0,
            kappa_ab=0.0,
            association_scheme=None,
            relative_permittivity=1.0,
            born_diameter=0.0,
            solvation_factor=1.0,
        )
        for component, molar_mass, m, sigma, epsilon_k in zip(
            HYDROCARBON_COMPONENTS,
            (16.043e-3, 30.070e-3, 44.097e-3),
            (1.0, 1.6069, 2.0020),
            (3.7039, 3.5206, 3.6184),
            (150.03, 191.42, 208.11),
            strict=True,
        )
    )
    return ParameterSet.from_records(
        pure_records,
        (
            BinaryRecord(("Methane", "Ethane"), k_ij=3.0e-4),
            BinaryRecord(("Methane", "Propane"), k_ij=1.15e-2),
            BinaryRecord(("Ethane", "Propane"), k_ij=5.10e-3),
        ),
        metadata={
            "source": "Gross and Sadowski 2001 hydrocarbon parameters",
            "source_backed": True,
        },
    )
