"""Reset public frontend objects for ePC-SAFT workflows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ._types import InputError
from .model_options import ModelOptions, as_float_array, coerce_model_options, require_cppad_backend
from .parameter_schema import ParameterSet

R_GAS = 8.31446261815324


class Mixture:
    """Configured public ePC-SAFT mixture."""

    def __init__(
        self,
        parameters: ParameterSet,
        *,
        model_options: ModelOptions | Mapping[str, object] | None = None,
        components: Sequence[str] | None = None,
    ) -> None:
        if not isinstance(parameters, ParameterSet):
            raise InputError("Mixture requires a ParameterSet.")
        self.parameters = parameters
        self.model_options = coerce_model_options(model_options)
        self.model_options.validate_parameters(parameters)
        self.components = tuple(str(component) for component in (components or parameters.components))
        if not self.components:
            raise InputError("Mixture requires at least one component.")
        if set(self.components) != set(parameters.components):
            raise InputError("Mixture components must match the ParameterSet components.")
        self._runtime_parameters = _runtime_payload(parameters, self.components, self.model_options)
        self._runtime = None

    @property
    def ncomp(self) -> int:
        return len(self.components)

    @property
    def native(self) -> Any:
        if self._runtime is None:
            from .epcsaft import ePCSAFTMixture as _RuntimeMixture

            self._runtime = _RuntimeMixture.from_params(self._runtime_parameters, species=self.components)
        return self._runtime

    def state(
        self,
        *,
        T: float,
        x: Sequence[float],
        P: float | None = None,
        rho: float | None = None,
        phase: str = "liq",
        rho_guess: float | None = None,
    ) -> State:
        runtime_state = self.native.state(T=T, x=np.asarray(x, dtype=float), P=P, rho=rho, phase=phase, rho_guess=rho_guess)
        return State(self, runtime_state)

    def equilibrium(self, **defaults: Any) -> Equilibrium:
        return Equilibrium(self, **defaults)

    def regression(self, **defaults: Any) -> Regression:
        return Regression(self, **defaults)


class State:
    """CppAD-backed public thermodynamic state view."""

    def __init__(self, mixture: Mixture, runtime_state: Any) -> None:
        self.mixture = mixture
        self._runtime = runtime_state
        self._pressure_density_result: dict[str, Any] | None = None
        self._ln_fugacity_composition_result: dict[str, Any] | None = None

    @property
    def temperature(self) -> float:
        return float(self._runtime._T)

    @property
    def composition(self) -> np.ndarray:
        return np.asarray(self._runtime._x, dtype=float)

    def molar_density(self) -> float:
        return float(self._runtime.molar_density())

    def density(self) -> float:
        return self.molar_density()

    def pressure_density_derivative(self) -> dict[str, Any]:
        if self._pressure_density_result is None:
            result = dict(self._runtime.pressure_density_derivative_result())
            require_cppad_backend(result, label="State.pressure_density_derivative")
            self._pressure_density_result = result
        return _copy_derivative_result(self._pressure_density_result)

    def pressure(self) -> float:
        value = as_float_array(self.pressure_density_derivative()["value"])
        return float(value.reshape(-1)[0])

    def compressibility_factor(self) -> float:
        return self.pressure() / (self.molar_density() * R_GAS * self.temperature)

    def ln_fugacity_composition_derivative(self) -> dict[str, Any]:
        if self._ln_fugacity_composition_result is None:
            result = dict(self._runtime.ln_fugacity_composition_derivative_result())
            require_cppad_backend(result, label="State.ln_fugacity_composition_derivative")
            self._ln_fugacity_composition_result = result
        return _copy_derivative_result(self._ln_fugacity_composition_result)

    def ln_fugacity_coefficients(self) -> np.ndarray:
        return as_float_array(self.ln_fugacity_composition_derivative()["value"])

    def fugacity_coefficients(self) -> np.ndarray:
        return np.exp(self.ln_fugacity_coefficients())


@dataclass(slots=True)
class Equilibrium:
    """Configured equilibrium workflow."""

    mixture: Mixture
    defaults: dict[str, Any] = field(default_factory=dict)

    def __init__(self, mixture: Mixture, **defaults: Any) -> None:
        self.mixture = mixture
        self.defaults = _reject_backend_options(defaults, context="Equilibrium")

    def bubble_pressure(self, *, T: float, x: Sequence[float], **overrides: Any) -> Any:
        options = self._options(overrides)
        result = self.mixture.native.bubble_p(T=T, x=np.asarray(x, dtype=float), options=options)
        diagnostics = getattr(result, "diagnostics", {})
        if str(diagnostics.get("hessian_approximation", "")) != "exact":
            raise InputError("Equilibrium.bubble_pressure requires the exact CppAD Hessian route.")
        if diagnostics.get("exact_hessian_available") is not True:
            raise InputError("Equilibrium.bubble_pressure did not report exact Hessian availability.")
        return result

    def _options(self, overrides: Mapping[str, Any] | None = None) -> Any:
        from .equilibrium import EquilibriumOptions

        payload = dict(self.defaults)
        payload.update(_reject_backend_options(overrides or {}, context="Equilibrium"))
        payload["jacobian_backend"] = "cppad"
        payload["solver_backend"] = "ipopt"
        payload["hessian_mode"] = "exact"
        return EquilibriumOptions(**payload)


@dataclass(slots=True)
class Regression:
    """Configured regression workflow."""

    mixture: Mixture
    defaults: dict[str, Any] = field(default_factory=dict)

    def __init__(self, mixture: Mixture, **defaults: Any) -> None:
        self.mixture = mixture
        self.defaults = _reject_backend_options(defaults, context="Regression")

    def evaluate_pure_neutral_derivatives(self, records: Any, *, component: str, **overrides: Any) -> dict[str, Any]:
        from .regression import evaluate_pure_neutral_derivatives as _evaluate

        payload = dict(self.defaults)
        payload.update(_reject_backend_options(overrides, context="Regression"))
        result = dict(_evaluate(records, component, **payload))
        require_cppad_backend(result, label="Regression.evaluate_pure_neutral_derivatives")
        return result

    def fit_pure_neutral(self, records: Any, *, component: str, **overrides: Any) -> Any:
        from .regression import fit_pure_neutral as _fit

        payload = dict(self.defaults)
        payload.update(_reject_backend_options(overrides, context="Regression"))
        result = _fit(records, component, optimizer_backend="ceres", **payload)
        if not str(getattr(result, "jacobian_backend", "")).startswith("cppad"):
            raise InputError("Regression.fit_pure_neutral requires CppAD Jacobian coverage.")
        return result


def _reject_backend_options(options: Mapping[str, Any], *, context: str) -> dict[str, Any]:
    blocked = sorted(set(options) & {"backend", "derivative_backend", "jacobian_backend", "solver_backend", "hessian_mode"})
    if blocked:
        raise InputError(f"{context} does not expose backend-selection option(s): {', '.join(blocked)}.")
    return dict(options)


def _copy_derivative_result(result: Mapping[str, Any]) -> dict[str, Any]:
    copied = dict(result)
    for key in ("value", "jacobian"):
        if key in copied:
            copied[key] = np.asarray(copied[key], dtype=float).copy()
    return copied


def _runtime_payload(parameters: ParameterSet, components: Sequence[str], model_options: ModelOptions) -> dict[str, Any]:
    records = {str(record.component): record for record in parameters.pure_records}
    ordered = [records[str(component)] for component in components]
    charges = np.asarray([record.charge for record in ordered], dtype=float)
    payload: dict[str, Any] = {
        "m": np.asarray([record.m for record in ordered], dtype=float),
        "s": np.asarray([record.sigma for record in ordered], dtype=float),
        "e": np.asarray([record.epsilon_k for record in ordered], dtype=float),
    }
    if np.any(np.abs(charges) > 0.0):
        payload["MW"] = np.asarray([record.molar_mass for record in ordered], dtype=float)
        payload["z"] = charges
        payload["dielc"] = np.asarray([record.relative_permittivity for record in ordered], dtype=float)
        payload["d_born"] = np.asarray([record.born_diameter for record in ordered], dtype=float)
        payload["f_solv"] = np.asarray([record.solvation_factor for record in ordered], dtype=float)
        payload.update(model_options.to_runtime_options(parameters))
    if any(float(record.epsilon_k_ab) != 0.0 for record in ordered):
        payload["e_assoc"] = np.asarray([record.epsilon_k_ab for record in ordered], dtype=float)
    if any(float(record.kappa_ab) != 0.0 for record in ordered):
        payload["vol_a"] = np.asarray([record.kappa_ab for record in ordered], dtype=float)
    schemes = [record.association_scheme for record in ordered]
    if any(scheme not in (None, "") for scheme in schemes):
        payload["assoc_scheme"] = schemes
    matrices = _binary_matrices(parameters, components)
    payload.update(matrices)
    return payload


def _binary_matrices(parameters: ParameterSet, components: Sequence[str]) -> dict[str, np.ndarray]:
    labels = tuple(str(component) for component in components)
    index = {component: i for i, component in enumerate(labels)}
    matrices = {
        "k_ij": np.zeros((len(labels), len(labels)), dtype=float),
        "l_ij": np.zeros((len(labels), len(labels)), dtype=float),
        "k_hb": np.zeros((len(labels), len(labels)), dtype=float),
    }
    for record in parameters.binary_records:
        left, right = record.components
        i = index[left]
        j = index[right]
        matrices["k_ij"][i, j] = matrices["k_ij"][j, i] = float(record.k_ij)
        matrices["l_ij"][i, j] = matrices["l_ij"][j, i] = float(record.l_ij)
        matrices["k_hb"][i, j] = matrices["k_hb"][j, i] = float(record.k_hb_ij)
    return {key: value for key, value in matrices.items() if np.any(np.abs(value) > 0.0)}
