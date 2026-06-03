from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .pcsaft_inputs import ToyPCSAFTState


@dataclass(frozen=True)
class HardChainState:
    zeta: np.ndarray
    ghs: np.ndarray
    eta: float


def hs_contact_value(pair_diameter: float, zeta2: float, zeta3: float) -> float:
    one_minus_eta = 1.0 - zeta3
    return float(
        1.0 / one_minus_eta
        + pair_diameter * 3.0 * zeta2 / one_minus_eta**2
        + pair_diameter**2 * 2.0 * zeta2**2 / one_minus_eta**3
    )


def hard_chain_state(state: ToyPCSAFTState) -> HardChainState:
    d = state.segment_diameter
    zeta = np.zeros(4, dtype=float)
    for order in range(4):
        zeta[order] = np.pi / 6.0 * state.number_density * np.sum(
            state.composition * state.segments * d**order
        )
    ghs = np.zeros((state.component_count, state.component_count), dtype=float)
    for i in range(state.component_count):
        for j in range(state.component_count):
            pair_diameter = d[i] * d[j] / (d[i] + d[j])
            ghs[i, j] = hs_contact_value(float(pair_diameter), float(zeta[2]), float(zeta[3]))
    return HardChainState(zeta=zeta, ghs=ghs, eta=float(zeta[3]))


def ares_hs(hc: HardChainState) -> float:
    z0, z1, z2, z3 = hc.zeta
    return float(
        (
            3.0 * z1 * z2 / (1.0 - z3)
            + z2**3 / (z3 * (1.0 - z3) ** 2)
            + (z2**3 / z3**2 - z0) * np.log(1.0 - z3)
        )
        / z0
    )


def ares_hc(state: ToyPCSAFTState, hc: HardChainState) -> float:
    chain_sum = float(np.sum(state.composition * (state.segments - 1.0) * np.log(np.diag(hc.ghs))))
    return float(state.m_bar * ares_hs(hc) - chain_sum)
