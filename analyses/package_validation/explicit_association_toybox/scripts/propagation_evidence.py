from __future__ import annotations

import csv
from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np
import yaml

from .association_models import AssociationSystem, association_helmholtz, mass_action_residual
from .closure_models import ClosureResult, _diagonal_polish, _picard, evaluate_closure
from .exact_baseline import ExactAssociationResult, solve_exact_site_fractions
from .metrics import timed_closure

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_THRESHOLDS = ANALYSIS_ROOT / "config" / "propagation_evidence.yaml"
EPS = 1.0e-14


def load_propagation_thresholds(path: Path = DEFAULT_THRESHOLDS) -> dict[str, dict[str, float | str]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping) or not isinstance(data.get("evidence_bands"), Mapping):
        raise ValueError(f"{path} must define an evidence_bands mapping.")
    return {str(key): dict(value) for key, value in data["evidence_bands"].items()}


def classify_propagated_evidence_band(
    *,
    association_model: str,
    assoc_ares_rel_error: float,
    derivative_rel_error: float,
    property_rel_error: float,
    mass_action_residual_inf: float,
    speedup_vs_exact_implicit: float,
    information_loss: str,
    thresholds: Mapping[str, Mapping[str, float | str]],
) -> str:
    reject = thresholds["reject_for_provider_path"]
    values = [assoc_ares_rel_error, derivative_rel_error, property_rel_error, mass_action_residual_inf]
    if not np.all(np.isfinite(values)):
        return "reject_for_provider_path"
    if mass_action_residual_inf > float(reject["max_mass_action_residual_inf"]):
        return "reject_for_provider_path"
    if information_loss != "none":
        return "diagnostic_only"
    if association_model == "implicit_exact":
        exact = thresholds["exact_reference"]
        if (
            assoc_ares_rel_error <= float(exact["max_assoc_ares_rel_error"])
            and derivative_rel_error <= float(exact["max_derivative_rel_error"])
            and property_rel_error <= float(exact["max_property_rel_error"])
        ):
            return "exact_reference"
    candidate = thresholds["candidate_accuracy"]
    if (
        assoc_ares_rel_error <= float(candidate["max_assoc_ares_rel_error"])
        and derivative_rel_error <= float(candidate["max_derivative_rel_error"])
        and property_rel_error <= float(candidate["max_property_rel_error"])
        and speedup_vs_exact_implicit >= float(candidate["min_speedup_vs_exact_implicit"])
    ):
        return "candidate_accuracy"
    speed = thresholds["speed_only_candidate"]
    if (
        assoc_ares_rel_error <= float(speed["max_assoc_ares_rel_error"])
        and speedup_vs_exact_implicit >= float(speed["min_speedup_vs_exact_implicit"])
    ):
        return "speed_only_candidate"
    return "diagnostic_only"


def evaluate_named_closure(
    closure_name: str,
    *,
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> ClosureResult:
    x_assoc = system.x_assoc(composition)
    if closure_name == "implicit_exact_mass_action":
        exact = solve_exact_site_fractions(density=density, x_assoc=x_assoc, delta=delta)
        return ClosureResult(
            name=closure_name,
            xa=exact.xa,
            association_model="implicit_exact",
            association_closure=closure_name,
            exact_derivative_of="exact_mass_action",
            information_loss="none",
        )
    variant_map = {
        "damped_picard_3_05": (3, 0.5, False),
        "damped_picard_5_05": (5, 0.5, False),
        "damped_picard_7_05": (7, 0.5, False),
        "picard3_diag_newton1": (3, 0.5, True),
    }
    if closure_name in variant_map:
        steps, damping, polish = variant_map[closure_name]
        xa = _picard(density, x_assoc, delta, steps=steps, damping=damping)
        if polish:
            xa = _diagonal_polish(xa, density, x_assoc, delta, damping=0.5)
        return ClosureResult(
            name=closure_name,
            xa=xa,
            association_model="explicit_approx",
            association_closure=closure_name,
            exact_derivative_of="approximate_association_closure",
            information_loss="none",
        )
    return evaluate_closure(
        closure_name,
        system=system,
        density=density,
        composition=composition,
        delta=delta,
    )


def exact_association_value(
    *,
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> tuple[ExactAssociationResult, float, float]:
    exact, elapsed = timed_closure(
        lambda: solve_exact_site_fractions(
            density=density,
            x_assoc=system.x_assoc(composition),
            delta=delta,
        )
    )
    value = association_helmholtz(exact.xa, composition, system.site_component_index)
    return exact, value, elapsed


def closure_association_value(
    closure_name: str,
    *,
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> tuple[ClosureResult, float, float]:
    closure, elapsed = timed_closure(
        lambda: evaluate_named_closure(
            closure_name,
            system=system,
            density=density,
            composition=composition,
            delta=delta,
        )
    )
    value = association_helmholtz(closure.xa, composition, system.site_component_index)
    return closure, value, elapsed


def mass_residual_inf(
    closure: ClosureResult,
    *,
    system: AssociationSystem,
    density: float,
    composition: np.ndarray,
    delta: np.ndarray,
) -> float:
    residual = mass_action_residual(closure.xa, density=density, x_assoc=system.x_assoc(composition), delta=delta)
    return float(np.linalg.norm(residual, ord=np.inf))


def relative_error(actual: float, reference: float) -> float:
    return float(abs(actual - reference) / max(abs(reference), EPS))


def write_rows_csv(rows: Sequence[Mapping[str, object]], output_path: Path) -> Path:
    if not rows:
        raise ValueError("rows are required.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path
