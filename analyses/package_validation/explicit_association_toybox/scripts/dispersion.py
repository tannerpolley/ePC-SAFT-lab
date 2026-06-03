from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .hard_chain import HardChainState
from .pcsaft_inputs import ToyPCSAFTState

A0 = np.array([0.9105631445, 0.6361281449, 2.6861347891, -26.547362491, 97.759208784, -159.59154087, 91.297774084])
A1 = np.array([-0.3084016918, 0.1860531159, -2.5030047259, 21.419793629, -65.255885330, 83.318680481, -33.746922930])
A2 = np.array([-0.0906148351, 0.4527842806, 0.5962700728, -1.7241829131, -4.1302112531, 13.776631870, -8.6728470368])
B0 = np.array([0.7240946941, 2.2382791861, -4.0025849485, -21.003576815, 26.855641363, 206.55133841, -355.60235612])
B1 = np.array([-0.5755498075, 0.6995095521, 3.8925673390, -17.215471648, 192.67226447, -161.82646165, -165.20769346])
B2 = np.array([0.0976883116, -0.2557574982, -9.1558561530, 20.642075974, -38.804430052, 93.626774077, -29.666905585])


@dataclass(frozen=True)
class DispersionPolynomials:
    a: np.ndarray
    b: np.ndarray
    i1: float
    i2: float
    c1: float


@dataclass(frozen=True)
class MixedDispersionMoments:
    m2epssigma3: float
    m2eps2sigma3: float


def dispersion_polynomials(*, m_bar: float, eta: float) -> DispersionPolynomials:
    c1_m = (m_bar - 1.0) / m_bar
    c2_m = (m_bar - 2.0) / m_bar
    a = A0 + c1_m * A1 + c1_m * c2_m * A2
    b = B0 + c1_m * B1 + c1_m * c2_m * B2
    powers = eta ** np.arange(7, dtype=float)
    i1 = float(np.dot(a, powers))
    i2 = float(np.dot(b, powers))
    c1 = float(
        1.0
        / (
            1.0
            + m_bar * (8.0 * eta - 2.0 * eta**2) / (1.0 - eta) ** 4
            + (1.0 - m_bar)
            * (20.0 * eta - 27.0 * eta**2 + 12.0 * eta**3 - 2.0 * eta**4)
            / ((1.0 - eta) * (2.0 - eta)) ** 2
        )
    )
    return DispersionPolynomials(a=a, b=b, i1=i1, i2=i2, c1=c1)


def pair_sigma_matrix(state: ToyPCSAFTState) -> np.ndarray:
    sigma = state.sigma
    return 0.5 * (sigma[:, np.newaxis] + sigma[np.newaxis, :])


def pair_epsilon_over_k_matrix(state: ToyPCSAFTState) -> np.ndarray:
    epsilon = np.sqrt(state.epsilon_over_k[:, np.newaxis] * state.epsilon_over_k[np.newaxis, :])
    return epsilon * (1.0 - state.k_ij)


def mixed_dispersion_moments(state: ToyPCSAFTState) -> MixedDispersionMoments:
    x = state.composition
    m = state.segments
    sigma_ij = pair_sigma_matrix(state)
    epsilon_ij = pair_epsilon_over_k_matrix(state)
    weights = x[:, np.newaxis] * x[np.newaxis, :] * m[:, np.newaxis] * m[np.newaxis, :]
    e_over_t = epsilon_ij / state.temperature
    sigma3 = sigma_ij**3
    return MixedDispersionMoments(
        m2epssigma3=float(np.sum(weights * e_over_t * sigma3)),
        m2eps2sigma3=float(np.sum(weights * e_over_t**2 * sigma3)),
    )


def ares_disp(state: ToyPCSAFTState, hc: HardChainState, moments: MixedDispersionMoments) -> float:
    polynomials = dispersion_polynomials(m_bar=state.m_bar, eta=hc.eta)
    return float(
        -2.0 * np.pi * state.number_density * polynomials.i1 * moments.m2epssigma3
        - np.pi * state.number_density * state.m_bar * polynomials.c1 * polynomials.i2 * moments.m2eps2sigma3
    )
