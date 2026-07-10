from __future__ import annotations

import numpy as np
from epcsaft import ParameterSet

HYDROCARBON_COMPONENTS = ("Methane", "Ethane", "Propane")
HYDROCARBON_LIQUID_X = (0.1, 0.3, 0.6)
HYDROCARBON_T = 233.15
HYDROCARBON_BUBBLE_P = 1_276_369.4735856401
HYDROCARBON_LIQUID_RHO = 14_330.417109760687
HYDROCARBON_VAPOR_RHO = 728.5617203262267
HYDROCARBON_VAPOR_Y = np.asarray([0.7246628928343289, 0.20293191372324873, 0.0724051934424223])
HYDROCARBON_FLASH_Z = tuple((0.5 * (np.asarray(HYDROCARBON_LIQUID_X) + HYDROCARBON_VAPOR_Y)).tolist())


def hydrocarbon_parameter_set() -> ParameterSet:
    return ParameterSet.from_dict(
        {
            "m": np.asarray([1.0, 1.6069, 2.0020]),
            "s": np.asarray([3.7039, 3.5206, 3.6184]),
            "e": np.asarray([150.03, 191.42, 208.11]),
            "MW": np.asarray([16.043e-3, 30.070e-3, 44.097e-3]),
            "k_ij": np.asarray(
                [
                    [0.0, 3.0e-4, 1.15e-2],
                    [3.0e-4, 0.0, 5.10e-3],
                    [1.15e-2, 5.10e-3, 0.0],
                ]
            ),
        },
        species=HYDROCARBON_COMPONENTS,
    )
