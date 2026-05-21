"""Thermodynamic state view for public ePC-SAFT workflows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from .._types import InputError
from ..eos_views import CONTRIBUTION_PUBLIC_NAMES
from ..model.options import as_float_array, require_cppad_backend
from .mixture import Mixture

R_GAS = 8.31446261815324


class State:
    """A thermodynamic state for a configured mixture."""

    def __init__(
        self,
        mixture: Mixture,
        *,
        T: float,
        x: Sequence[float],
        P: float | None = None,
        rho: float | None = None,
        phase: str = "liq",
        rho_guess: float | None = None,
    ) -> None:
        if not isinstance(mixture, Mixture):
            raise InputError("State requires a Mixture.")
        self.mixture = mixture
        self._runtime = mixture.native.state(
            T=float(T),
            x=np.asarray(x, dtype=float),
            P=P,
            rho=rho,
            phase=phase,
            rho_guess=rho_guess,
        )
        self._pressure_density_result: dict[str, Any] | None = None
        self._ln_fugacity_composition_result: dict[str, Any] | None = None

    @property
    def temperature(self) -> float:
        """Return the state temperature."""

        return float(self._runtime._T)

    @property
    def composition(self) -> np.ndarray:
        """Return the state mole-fraction composition."""

        return np.asarray(self._runtime._x, dtype=float)

    def molar_density(self) -> float:
        """Return the molar density."""

        return float(self._runtime.molar_density())

    def density(self) -> float:
        """Return the molar density."""

        return self.molar_density()

    def pressure_density_derivative(self) -> dict[str, Any]:
        """Return pressure and its density derivative for this state."""

        if self._pressure_density_result is None:
            result = dict(self._runtime.pressure_density_derivative_result())
            require_cppad_backend(result, label="State.pressure_density_derivative")
            self._pressure_density_result = result
        return _copy_derivative_result(self._pressure_density_result)

    def pressure(self) -> float:
        """Return the pressure."""

        value = as_float_array(self.pressure_density_derivative()["value"])
        return float(value.reshape(-1)[0])

    def z(self) -> float:
        """Return the compressibility factor."""

        return self.pressure() / (self.molar_density() * R_GAS * self.temperature)

    def compressibility_factor(self) -> float:
        """Return the compressibility factor."""

        return self.z()

    def residual_helmholtz(self) -> float:
        """Return the residual Helmholtz energy."""

        return float(self._runtime.residual_helmholtz())

    def ares(self) -> float:
        """Return the residual Helmholtz energy."""

        return self.residual_helmholtz()

    def ares_contributions(self) -> dict[str, float]:
        """Return residual Helmholtz contributions by contribution family."""

        payload = self._runtime.residual_helmholtz(return_contribution_terms=True)
        terms = payload["terms"]
        return {public: float(terms[internal]) for internal, public in CONTRIBUTION_PUBLIC_NAMES.items()}

    def ares_contribution(self, name: str) -> float:
        """Return one residual Helmholtz contribution by name."""

        normalized = str(name).strip().lower().replace("-", "_").replace(" ", "_")
        contributions = self.ares_contributions()
        if normalized not in contributions:
            known = ", ".join(sorted(contributions))
            raise InputError(f"Unknown residual Helmholtz contribution '{name}'. Expected one of: {known}.")
        return contributions[normalized]

    def residual_enthalpy(self) -> float:
        """Return the residual enthalpy."""

        return float(self._runtime.residual_enthalpy())

    def hres(self) -> float:
        """Return the residual enthalpy."""

        return self.residual_enthalpy()

    def residual_entropy(self) -> float:
        """Return the residual entropy."""

        return float(self._runtime.residual_entropy())

    def sres(self) -> float:
        """Return the residual entropy."""

        return self.residual_entropy()

    def residual_gibbs(self) -> float:
        """Return the residual Gibbs energy."""

        return float(self._runtime.residual_gibbs())

    def gres(self) -> float:
        """Return the residual Gibbs energy."""

        return self.residual_gibbs()

    def ln_fugacity_composition_derivative(self) -> dict[str, Any]:
        """Return fugacity-coefficient composition derivatives."""

        if self._ln_fugacity_composition_result is None:
            result = dict(self._runtime.ln_fugacity_composition_derivative_result())
            require_cppad_backend(result, label="State.ln_fugacity_composition_derivative")
            self._ln_fugacity_composition_result = result
        return _copy_derivative_result(self._ln_fugacity_composition_result)

    def ln_fugacity_coefficients(self) -> np.ndarray:
        """Return natural-log fugacity coefficients."""

        return as_float_array(self.ln_fugacity_composition_derivative()["value"])

    def fugacity_coefficients(self) -> np.ndarray:
        """Return fugacity coefficients."""

        return np.exp(self.ln_fugacity_coefficients())


def _copy_derivative_result(result: Mapping[str, Any]) -> dict[str, Any]:
    copied = dict(result)
    for key in ("value", "jacobian"):
        if key in copied:
            copied[key] = np.asarray(copied[key], dtype=float).copy()
    return copied
