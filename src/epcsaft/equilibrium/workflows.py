"""Selector-backed production equilibrium workflow helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Integral, Real
from typing import Any, Literal

import numpy as np

from .._types import InputError, SolutionError
from .core.native_requests import neutral_two_phase_eos_tolerances
from .core.native_results import (
    RouteDiagnosticsView,
    native_route_diagnostics,
    native_route_solved_pressure,
    native_route_solved_temperature,
    native_route_summed_phase_amounts,
    neutral_two_phase_payload_to_result,
    raise_native_route_rejected,
)


@dataclass(frozen=True, slots=True)
class EquilibriumOptions:
    """Numerical controls for the production selector equilibrium route."""

    max_iterations: int = 180
    tolerance: float = 1.0e-6
    min_composition: float = 1.0e-12
    jacobian_backend: Literal["auto", "analytic", "cppad"] = "auto"
    solver_backend: Literal["auto", "ipopt"] = "auto"
    timeout_seconds: float | None = None
    hessian_mode: Literal["auto", "exact", "limited-memory"] = "auto"
    ipopt_iteration_history_limit: int = 20
    ipopt_linear_solver: str = "auto"
    ipopt_acceptable_tolerance: float | None = None
    ipopt_constraint_violation_tolerance: float | None = None
    ipopt_dual_infeasibility_tolerance: float | None = None
    ipopt_complementarity_tolerance: float | None = None
    continuation_state: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class EquilibriumPhase:
    """One phase returned by a production equilibrium calculation."""

    label: str
    composition: np.ndarray
    density: float
    temperature: float
    pressure: float
    phase_fraction: float
    ln_fugacity_coefficient: np.ndarray | None = None
    diagnostics: dict[str, Any] | None = None

    def __init__(
        self,
        label: str,
        composition: Any,
        density: float,
        temperature: float,
        pressure: float,
        phase_fraction: float,
        ln_fugacity_coefficient: Any = None,
        fugacity_coefficient: Any = None,
        diagnostics: dict[str, Any] | None = None,
    ) -> None:
        if ln_fugacity_coefficient is None:
            if fugacity_coefficient is None:
                ln_fugacity_coefficient = None
            else:
                ln_fugacity_coefficient = np.log(np.asarray(fugacity_coefficient, dtype=float))
        object.__setattr__(self, "label", str(label))
        object.__setattr__(self, "composition", np.asarray(composition, dtype=float))
        object.__setattr__(self, "density", float(density))
        object.__setattr__(self, "temperature", float(temperature))
        object.__setattr__(self, "pressure", float(pressure))
        object.__setattr__(self, "phase_fraction", float(phase_fraction))
        if ln_fugacity_coefficient is not None:
            ln_fugacity_coefficient = np.asarray(ln_fugacity_coefficient, dtype=float)
        object.__setattr__(self, "ln_fugacity_coefficient", ln_fugacity_coefficient)
        object.__setattr__(self, "diagnostics", None if diagnostics is None else dict(diagnostics))

    @property
    def fugacity_coefficient(self) -> np.ndarray | None:
        """Return coefficient-form fugacity coefficients."""

        if self.ln_fugacity_coefficient is None:
            return None
        return np.exp(self.ln_fugacity_coefficient)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-like phase payload."""

        ln_fugacity = None if self.ln_fugacity_coefficient is None else self.ln_fugacity_coefficient.tolist()
        return {
            "label": self.label,
            "composition": self.composition.tolist(),
            "density": self.density,
            "temperature": self.temperature,
            "pressure": self.pressure,
            "phase_fraction": self.phase_fraction,
            "ln_fugacity_coefficient": ln_fugacity,
            "fugacity_coefficient": None if self.fugacity_coefficient is None else self.fugacity_coefficient.tolist(),
            "diagnostics": _json_like(self.diagnostics),
        }


@dataclass(frozen=True, slots=True)
class EquilibriumResult:
    """Structured result returned by the production equilibrium route."""

    backend: str
    problem_kind: str
    phases: tuple[EquilibriumPhase, ...]
    stable: bool
    split_detected: bool
    diagnostics: dict[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "backend", str(self.backend))
        object.__setattr__(self, "problem_kind", str(self.problem_kind))
        object.__setattr__(self, "phases", tuple(self.phases))
        object.__setattr__(self, "stable", bool(self.stable))
        object.__setattr__(self, "split_detected", bool(self.split_detected))
        object.__setattr__(self, "diagnostics", dict(self.diagnostics))

    @property
    def phase_labels(self) -> list[str]:
        """Return phase labels in result order."""

        return [phase.label for phase in self.phases]

    @property
    def route_diagnostics(self) -> RouteDiagnosticsView:
        """Return a typed view over route diagnostics."""

        return RouteDiagnosticsView(self.diagnostics)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-like result payload."""

        return {
            "backend": self.backend,
            "problem_kind": self.problem_kind,
            "phase_labels": self.phase_labels,
            "phases": [phase.to_dict() for phase in self.phases],
            "stable": self.stable,
            "split_detected": self.split_detected,
            "diagnostics": _json_like(self.diagnostics),
        }


@dataclass(frozen=True, slots=True)
class _VleRouteSpec:
    selector_route: str
    composition_key: str
    composition_role: str
    requires_temperature: bool
    requires_pressure: bool
    problem_kind: str
    route_label: str
    selector_family: str


_VLE_ROUTE_SPECS: dict[str, _VleRouteSpec] = {
    "bubble_pressure": _VleRouteSpec(
        selector_route="bubble_pressure",
        composition_key="x",
        composition_role="liquid",
        requires_temperature=True,
        requires_pressure=False,
        problem_kind="neutral_bubble_p",
        route_label="bubble_pressure",
        selector_family="bubble_dew_derived_routes",
    ),
    "bubble_temperature": _VleRouteSpec(
        selector_route="bubble_temperature",
        composition_key="x",
        composition_role="liquid",
        requires_temperature=False,
        requires_pressure=True,
        problem_kind="neutral_bubble_t",
        route_label="bubble_temperature",
        selector_family="bubble_dew_derived_routes",
    ),
    "dew_pressure": _VleRouteSpec(
        selector_route="dew_pressure",
        composition_key="y",
        composition_role="vapor",
        requires_temperature=True,
        requires_pressure=False,
        problem_kind="neutral_dew_p",
        route_label="dew_pressure",
        selector_family="bubble_dew_derived_routes",
    ),
    "dew_temperature": _VleRouteSpec(
        selector_route="dew_temperature",
        composition_key="y",
        composition_role="vapor",
        requires_temperature=False,
        requires_pressure=True,
        problem_kind="neutral_dew_t",
        route_label="dew_temperature",
        selector_family="bubble_dew_derived_routes",
    ),
    "flash": _VleRouteSpec(
        selector_route="neutral_tp_flash",
        composition_key="z",
        composition_role="feed",
        requires_temperature=True,
        requires_pressure=True,
        problem_kind="neutral_tp_flash",
        route_label="flash",
        selector_family="neutral_tp_flash",
    ),
}


# AlgID: bubble_dew_ipopt
def _solve_selector_vle(
    mixture: Any,
    *,
    route: str,
    T: Any = None,
    P: Any = None,
    x: Any = None,
    y: Any = None,
    z: Any = None,
    options: EquilibriumOptions | None = None,
) -> EquilibriumResult:
    """Solve one selector-admitted neutral VLE route spec through the shared core."""

    opts = _normalize_options(options)
    try:
        spec = _VLE_ROUTE_SPECS[str(route)]
    except KeyError as exc:
        allowed = ", ".join(sorted(_VLE_ROUTE_SPECS))
        raise InputError(f"Unknown equilibrium route '{route}'. Expected one of: {allowed}.") from exc

    composition_value = {"x": x, "y": y, "z": z}[spec.composition_key]
    provided_compositions = {key for key, value in {"x": x, "y": y, "z": z}.items() if value is not None}
    if provided_compositions != {spec.composition_key}:
        expected = spec.composition_key
        provided = ", ".join(sorted(provided_compositions)) or "none"
        raise InputError(f"{spec.route_label} requires only composition '{expected}', got {provided}.")
    if spec.requires_temperature and T is None:
        raise InputError(f"{spec.route_label} requires T.")
    if not spec.requires_temperature and T is not None:
        raise InputError(f"{spec.route_label} must not specify T.")
    if spec.requires_pressure and P is None:
        raise InputError(f"{spec.route_label} requires P.")
    if not spec.requires_pressure and P is not None:
        raise InputError(f"{spec.route_label} must not specify P.")

    composition = _normalize_feed(composition_value, mixture.ncomp, opts.min_composition, spec.route_label)
    _reject_ion_containing_mixture(mixture)
    temperature = _positive_scalar(T, "T", spec.route_label) if spec.requires_temperature else None
    pressure = _positive_scalar(P, "P", spec.route_label) if spec.requires_pressure else None
    return _native_selector_vle_route(
        mixture,
        request=_selector_request(
            route=spec.selector_route,
            temperature=temperature,
            pressure=pressure,
            composition=composition,
            composition_role=spec.composition_role,
        ),
        options=opts,
        problem_kind=spec.problem_kind,
        route_label=spec.route_label,
        selector_family=spec.selector_family,
    )


def _selector_request(
    *,
    route: str,
    composition: np.ndarray,
    composition_role: str,
    temperature: float | None = None,
    pressure: float | None = None,
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "route": route,
        "composition": composition.tolist(),
        "composition_role": composition_role,
    }
    if temperature is not None:
        request["temperature"] = float(temperature)
    if pressure is not None:
        request["pressure"] = float(pressure)
    return request


def _native_selector_vle_route(
    mixture: Any,
    *,
    request: Mapping[str, Any],
    options: EquilibriumOptions,
    problem_kind: str,
    route_label: str,
    selector_family: str,
) -> EquilibriumResult:
    from .. import _core

    route_tolerances = (
        options.tolerance,
        max(1.0e5 * options.tolerance, options.tolerance),
        options.tolerance,
        max(10.0 * options.min_composition, 1.0e-8),
    )
    route = _core._native_equilibrium_selector_route_result(
        mixture._native,
        dict(request),
        options.max_iterations,
        options.tolerance,
        _native_timeout_seconds(options),
        *_native_ipopt_option_args(options),
        *route_tolerances,
        dict(options.continuation_state or {}),
        **_native_ipopt_control_kwargs(options),
    )
    if str(route.get("status", "")) == "ipopt_dependency_required":
        raise InputError(f"{route_label} requires the native Ipopt selector equilibrium route.")

    accepted = bool(route.get("accepted", False))
    temperature = float(request.get("temperature", 0.0))
    pressure = float(request.get("pressure", 0.0))
    if accepted and request.get("temperature") is None:
        temperature = native_route_solved_temperature(route, route_label)
    if accepted and request.get("pressure") is None:
        pressure = native_route_solved_pressure(route, route_label)
    composition = np.asarray(request["composition"], dtype=float)
    feed = native_route_summed_phase_amounts(route, mixture.ncomp, route_label) if accepted else composition
    return _accepted_native_selector_two_phase_result(
        mixture,
        T=temperature,
        P=pressure,
        feed=feed,
        route=route,
        tolerances=neutral_two_phase_eos_tolerances(pressure, options),
        problem_kind=problem_kind,
        route_label=route_label,
        selector_family=selector_family,
    )


def _accepted_native_selector_two_phase_result(
    mixture: Any,
    *,
    T: float,
    P: float,
    feed: np.ndarray,
    route: Mapping[str, Any],
    tolerances: tuple[float, float, float, float],
    problem_kind: str,
    route_label: str,
    selector_family: str,
) -> EquilibriumResult:
    from .. import _core

    if not bool(route.get("accepted", False)):
        raise_native_route_rejected(route, f"Native selector {route_label} route was rejected.")

    material_tolerance, pressure_tolerance, chemical_potential_tolerance, phase_distance_tolerance = tolerances
    result_payload = _core._native_neutral_two_phase_eos_result(
        mixture._native,
        T,
        P,
        route["phase_amounts"],
        route["phase_volumes"],
        feed.tolist(),
        material_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance,
    )
    result = neutral_two_phase_payload_to_result(
        result_payload,
        problem_kind=problem_kind,
        phase_labels=("liq", "vap"),
    )
    diagnostics = native_route_diagnostics(route)
    diagnostics.update(result.diagnostics)
    certification = diagnostics.get("postsolve_certification", {})
    if str(route.get("selector_family", "")) != selector_family:
        raise SolutionError(f"Native selector {route_label} returned an unexpected route family.", diagnostics)
    if not isinstance(certification, Mapping) or not bool(certification.get("accepted", False)):
        raise SolutionError(f"Native selector {route_label} route failed postsolve certification.", diagnostics)
    return EquilibriumResult(
        backend=result.backend,
        problem_kind=result.problem_kind,
        phases=result.phases,
        stable=result.stable,
        split_detected=result.split_detected,
        diagnostics=diagnostics,
    )


def _normalize_options(options: EquilibriumOptions | Mapping[str, Any] | None) -> EquilibriumOptions:
    if options is None:
        return EquilibriumOptions()
    if isinstance(options, Mapping):
        raw = dict(options)
        allowed = {
            "max_iterations",
            "tolerance",
            "min_composition",
            "jacobian_backend",
            "solver_backend",
            "timeout_seconds",
            "hessian_mode",
            "ipopt_iteration_history_limit",
            "ipopt_linear_solver",
            "ipopt_acceptable_tolerance",
            "ipopt_constraint_violation_tolerance",
            "ipopt_dual_infeasibility_tolerance",
            "ipopt_complementarity_tolerance",
            "continuation_state",
        }
        unknown = sorted(set(raw) - allowed)
        if unknown:
            raise InputError("Unknown equilibrium option key(s): {}.".format(", ".join(unknown)))
        options = EquilibriumOptions(**raw)
    if not isinstance(options, EquilibriumOptions):
        raise InputError("options must be an EquilibriumOptions instance.")
    if isinstance(options.max_iterations, bool) or not isinstance(options.max_iterations, Integral):
        raise InputError("options.max_iterations must be an integer greater than zero.")
    max_iterations = int(options.max_iterations)
    if max_iterations <= 0:
        raise InputError("options.max_iterations must be an integer greater than zero.")
    tolerance = _finite_float_option(options.tolerance, "tolerance")
    if tolerance <= 0.0:
        raise InputError("options.tolerance must be positive.")
    min_composition = _finite_float_option(options.min_composition, "min_composition")
    if min_composition <= 0.0:
        raise InputError("options.min_composition must be positive.")
    jacobian_backend = str(options.jacobian_backend).strip().lower()
    if jacobian_backend not in {"auto", "analytic", "cppad"}:
        raise InputError("options.jacobian_backend must be 'auto', 'analytic', or 'cppad'.")
    solver_backend = str(options.solver_backend).strip().lower()
    if solver_backend not in {"auto", "ipopt"}:
        raise InputError("options.solver_backend must be 'auto' or 'ipopt'.")
    timeout_seconds = _optional_positive_float_option(options.timeout_seconds, "timeout_seconds")
    hessian_mode = str(options.hessian_mode).strip().lower().replace("_", "-")
    if hessian_mode not in {"auto", "exact", "limited-memory"}:
        raise InputError("options.hessian_mode must be 'auto', 'exact', or 'limited-memory'.")
    if isinstance(options.ipopt_iteration_history_limit, bool) or not isinstance(
        options.ipopt_iteration_history_limit, Integral
    ):
        raise InputError("options.ipopt_iteration_history_limit must be an integer greater than or equal to zero.")
    ipopt_iteration_history_limit = int(options.ipopt_iteration_history_limit)
    if ipopt_iteration_history_limit < 0:
        raise InputError("options.ipopt_iteration_history_limit must be an integer greater than or equal to zero.")
    ipopt_linear_solver = str(options.ipopt_linear_solver).strip().lower()
    if not ipopt_linear_solver:
        raise InputError("options.ipopt_linear_solver must be a non-empty string.")
    ipopt_acceptable_tolerance = _optional_positive_float_option(
        options.ipopt_acceptable_tolerance,
        "ipopt_acceptable_tolerance",
    )
    ipopt_constraint_violation_tolerance = _optional_positive_float_option(
        options.ipopt_constraint_violation_tolerance,
        "ipopt_constraint_violation_tolerance",
    )
    ipopt_dual_infeasibility_tolerance = _optional_positive_float_option(
        options.ipopt_dual_infeasibility_tolerance,
        "ipopt_dual_infeasibility_tolerance",
    )
    ipopt_complementarity_tolerance = _optional_positive_float_option(
        options.ipopt_complementarity_tolerance,
        "ipopt_complementarity_tolerance",
    )
    continuation_state = options.continuation_state
    if continuation_state is not None and not isinstance(continuation_state, Mapping):
        raise InputError("options.continuation_state must be a mapping when provided.")
    return EquilibriumOptions(
        max_iterations=max_iterations,
        tolerance=tolerance,
        min_composition=min_composition,
        jacobian_backend=jacobian_backend,  # type: ignore[arg-type]
        solver_backend=solver_backend,  # type: ignore[arg-type]
        timeout_seconds=timeout_seconds,
        hessian_mode=hessian_mode,  # type: ignore[arg-type]
        ipopt_iteration_history_limit=ipopt_iteration_history_limit,
        ipopt_linear_solver=ipopt_linear_solver,
        ipopt_acceptable_tolerance=ipopt_acceptable_tolerance,
        ipopt_constraint_violation_tolerance=ipopt_constraint_violation_tolerance,
        ipopt_dual_infeasibility_tolerance=ipopt_dual_infeasibility_tolerance,
        ipopt_complementarity_tolerance=ipopt_complementarity_tolerance,
        continuation_state=None if continuation_state is None else dict(continuation_state),
    )


def _finite_float_option(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputError(f"options.{label} must be a finite real number.")
    out = float(value)
    if not np.isfinite(out):
        raise InputError(f"options.{label} must be finite.")
    return out


def _optional_positive_float_option(value: Any, label: str) -> float | None:
    if value is None:
        return None
    out = _finite_float_option(value, label)
    if out <= 0.0:
        raise InputError(f"options.{label} must be positive when provided.")
    return out


def _native_timeout_seconds(options: EquilibriumOptions) -> float:
    return 0.0 if options.timeout_seconds is None else float(options.timeout_seconds)


def _resolved_ipopt_acceptable_tolerance(options: EquilibriumOptions) -> float:
    if options.ipopt_acceptable_tolerance is not None:
        return float(options.ipopt_acceptable_tolerance)
    return max(100.0 * float(options.tolerance), 1.0e-10)


def _resolved_ipopt_constraint_violation_tolerance(options: EquilibriumOptions) -> float:
    if options.ipopt_constraint_violation_tolerance is not None:
        return float(options.ipopt_constraint_violation_tolerance)
    return float(options.tolerance)


def _resolved_ipopt_dual_infeasibility_tolerance(options: EquilibriumOptions) -> float:
    if options.ipopt_dual_infeasibility_tolerance is not None:
        return float(options.ipopt_dual_infeasibility_tolerance)
    return float(options.tolerance)


def _resolved_ipopt_complementarity_tolerance(options: EquilibriumOptions) -> float:
    if options.ipopt_complementarity_tolerance is not None:
        return float(options.ipopt_complementarity_tolerance)
    return float(options.tolerance)


def _native_ipopt_option_args(options: EquilibriumOptions) -> tuple[str, int]:
    return options.hessian_mode, int(options.ipopt_iteration_history_limit)


def _native_ipopt_control_kwargs(options: EquilibriumOptions) -> dict[str, Any]:
    return {
        "linear_solver": str(options.ipopt_linear_solver),
        "acceptable_tolerance": _resolved_ipopt_acceptable_tolerance(options),
        "constraint_violation_tolerance": _resolved_ipopt_constraint_violation_tolerance(options),
        "dual_infeasibility_tolerance": _resolved_ipopt_dual_infeasibility_tolerance(options),
        "complementarity_tolerance": _resolved_ipopt_complementarity_tolerance(options),
    }


def _normalize_feed(z: Any, ncomp: int, min_composition: float, kind: str) -> np.ndarray:
    if z is None:
        raise InputError(f"z is required for kind='{kind}'.")
    feed = np.asarray(z, dtype=float).flatten()
    if feed.size != int(ncomp):
        raise InputError(f"Feed composition length ({feed.size}) must match mixture component count ({ncomp}).")
    if not np.all(np.isfinite(feed)):
        raise InputError("Feed composition z must contain only finite values.")
    if np.any(feed < 0.0):
        raise InputError("Feed composition z must be non-negative.")
    total = float(np.sum(feed))
    if total <= 0.0:
        raise InputError("Feed composition z must have a positive sum.")
    feed = feed / total
    if np.any(feed < min_composition):
        raise InputError(f"{kind} requires each feed composition entry to be >= min_composition.")
    return feed


def _positive_scalar(value: Any, label: str, kind: str) -> float:
    if value is None:
        raise InputError(f"{label} is required for kind='{kind}'.")
    out = float(value)
    if not np.isfinite(out) or out <= 0.0:
        raise InputError(f"{label} must be a positive finite scalar.")
    return out


def _reject_ion_containing_mixture(mixture: Any) -> None:
    charges = np.asarray(mixture.parameters.get("z", []), dtype=float).flatten()
    if charges.size and np.any(np.abs(charges) > 1.0e-12):
        raise InputError("Production VLE selector routes support only neutral mixtures.")


def _json_like(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {str(key): _json_like(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_like(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value
