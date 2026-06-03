from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from typing import TypeVar

import numpy as np

from .association_models import AssociationSystem, association_helmholtz, mass_action_residual
from .closure_models import ClosureResult
from .exact_baseline import ExactAssociationResult

T = TypeVar("T")


def classify_evidence_band(
    *,
    closure: ClosureResult,
    max_abs_x_error: float,
    mass_residual_inf: float,
    assoc_helmholtz_rel_error: float,
    thresholds: Mapping[str, float],
) -> str:
    if closure.association_model == "implicit_exact" and max_abs_x_error <= 1.0e-10 and mass_residual_inf <= 1.0e-10:
        return "exact_reduction_verified"
    if not np.isfinite(mass_residual_inf) or np.any(closure.xa <= 0.0) or np.any(closure.xa > 1.0):
        return "reject_for_provider_path"
    reference = float(thresholds.get("thermodynamic_relative_reference", 0.03))
    loose_residual = float(thresholds.get("mass_residual_loose", 1.0e-6))
    if assoc_helmholtz_rel_error <= reference and mass_residual_inf <= loose_residual:
        return "promising_eos_approximation"
    return "diagnostic_only"


def metric_row(
    *,
    system_name: str,
    system: AssociationSystem,
    density: float,
    strength: float,
    composition: np.ndarray,
    delta: np.ndarray,
    exact: ExactAssociationResult,
    closure: ClosureResult,
    thresholds: Mapping[str, float],
    elapsed_seconds: float | None = None,
    exact_elapsed_seconds: float | None = None,
    temperature: float | None = None,
    pcsaft_density: float | None = None,
    ares_hc: float | None = None,
    ares_disp: float | None = None,
) -> dict[str, object]:
    residual = mass_action_residual(closure.xa, density=density, x_assoc=system.x_assoc(composition), delta=delta)
    exact_a = association_helmholtz(exact.xa, composition, system.site_component_index)
    closure_a = association_helmholtz(closure.xa, composition, system.site_component_index)
    abs_a = abs(closure_a - exact_a)
    rel_a = abs_a / max(abs(exact_a), 1.0e-14)
    has_pcsaft_context = (
        temperature is not None
        and pcsaft_density is not None
        and ares_hc is not None
        and ares_disp is not None
    )
    if has_pcsaft_context:
        ares_total_exact = float(ares_hc + ares_disp + exact_a)
        ares_total_closure = float(ares_hc + ares_disp + closure_a)
        ares_total_abs_error = abs(ares_total_closure - ares_total_exact)
        ares_total_rel_error = ares_total_abs_error / max(abs(ares_total_exact), 1.0e-14)
    else:
        ares_total_exact = np.nan
        ares_total_closure = np.nan
        ares_total_abs_error = np.nan
        ares_total_rel_error = np.nan
    speedup_ratio = (
        exact_elapsed_seconds / elapsed_seconds
        if exact_elapsed_seconds is not None and elapsed_seconds is not None and elapsed_seconds > 0.0
        else np.nan
    )
    max_abs_x = float(np.max(np.abs(closure.xa - exact.xa)))
    mass_residual_inf = float(np.linalg.norm(residual, ord=np.inf))
    band = classify_evidence_band(
        closure=closure,
        max_abs_x_error=max_abs_x,
        mass_residual_inf=mass_residual_inf,
        assoc_helmholtz_rel_error=float(rel_a),
        thresholds=thresholds,
    )
    return {
        "system": system_name,
        "closure": closure.name,
        "association_model": closure.association_model,
        "association_closure": closure.association_closure,
        "exact_derivative_of": closure.exact_derivative_of,
        "information_loss": closure.information_loss,
        "density": density,
        "strength": strength,
        "temperature": temperature if temperature is not None else np.nan,
        "pcsaft_density": pcsaft_density if pcsaft_density is not None else np.nan,
        "ares_hc": ares_hc if ares_hc is not None else np.nan,
        "ares_disp": ares_disp if ares_disp is not None else np.nan,
        "ares_assoc_exact": exact_a,
        "ares_assoc_closure": closure_a,
        "ares_total_exact": ares_total_exact,
        "ares_total_closure": ares_total_closure,
        "ares_total_abs_error": ares_total_abs_error,
        "ares_total_rel_error": ares_total_rel_error,
        "composition": ";".join(f"{value:.12g}" for value in composition),
        "max_abs_x_error": max_abs_x,
        "max_rel_x_error": float(
            np.max(np.abs(closure.xa - exact.xa) / np.maximum(np.abs(exact.xa), 1.0e-14))
        ),
        "mass_residual_inf": mass_residual_inf,
        "assoc_helmholtz_exact": exact_a,
        "assoc_helmholtz_closure": closure_a,
        "assoc_helmholtz_abs_error": abs_a,
        "assoc_helmholtz_rel_error": float(rel_a),
        "assoc_compressibility_abs_error": np.nan,
        "assoc_mu_abs_error": np.nan,
        "assoc_fugacity_abs_error": np.nan,
        "exact_elapsed_seconds": exact_elapsed_seconds if exact_elapsed_seconds is not None else np.nan,
        "exact_iteration_count": exact.iteration_count,
        "exact_residual_norm": exact.residual_norm,
        "closure_elapsed_seconds": elapsed_seconds if elapsed_seconds is not None else np.nan,
        "speedup_ratio": speedup_ratio,
        "evidence_band": band,
    }


def timed_closure(callable_obj: Callable[[], T]) -> tuple[T, float]:
    start = time.perf_counter()
    result = callable_obj()
    return result, time.perf_counter() - start
