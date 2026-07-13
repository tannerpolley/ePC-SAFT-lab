"""External dataset bundle validation helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from .._types import InputError
from .parameters import ParameterSet


def validate_dataset_bundle(
    dataset: Mapping[str, Any] | str | Path,
    *,
    species: Sequence[str],
    x: Any | None = None,
    T: float = 298.15,
    reactions: Sequence[Any] | None = None,
    user_options: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a structured validation report for a canonical parameter bundle."""

    labels = [str(item) for item in species]
    errors: list[str] = []
    warnings: list[str] = []
    provenance = {
        "dataset": str(dataset) if not isinstance(dataset, Mapping) else "canonical_mapping",
        "temperature": float(T),
    }
    try:
        parameter_set = _load_parameter_set(dataset, labels, x=x, T=T, user_options=user_options)
        parameter_set.validate()
    except (InputError, FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
        return _validation_report(labels, errors, warnings, provenance)

    _check_reactions(labels, reactions or (), errors)
    provenance["parameter_metadata"] = dict(parameter_set.metadata)
    return _validation_report(labels, errors, warnings, provenance)


def _validation_report(
    labels: list[str],
    errors: list[str],
    warnings: list[str],
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "valid": not errors,
        "species": labels,
        "component_count": len(labels),
        "errors": errors,
        "warnings": warnings,
        "provenance": dict(provenance),
    }


def _load_parameter_set(
    dataset: Mapping[str, Any] | str | Path,
    species: list[str],
    *,
    x: Any | None,
    T: float,
    user_options: Mapping[str, Any] | None,
) -> ParameterSet:
    if isinstance(dataset, Mapping):
        if user_options:
            raise InputError("Canonical mapping validation does not accept separate user_options.")
        return ParameterSet.from_dict(dataset, species=species)
    if x is not None or T != 298.15 or user_options is not None:
        raise InputError("schema-3 bundle validation does not accept runtime conditions or options.")
    return ParameterSet.from_dataset(dataset, species)


def _check_vector_lengths(params: Mapping[str, Any], species: list[str], errors: list[str]) -> None:
    n = len(species)
    for key in ("m", "s", "e"):
        if key not in params:
            errors.append(f"missing required parameter vector '{key}'")
            continue
        values = np.asarray(params[key], dtype=float).flatten()
        if values.size != n:
            errors.append(f"parameter vector '{key}' length {values.size} does not match species length {n}")
        elif np.any(~np.isfinite(values)):
            errors.append(f"parameter vector '{key}' contains non-finite values")


def _check_charges(
    params: Mapping[str, Any],
    species: list[str],
    errors: list[str],
) -> np.ndarray:
    if "z" not in params or np.asarray(params.get("z"), dtype=float).size == 0:
        errors.append("missing required charge vector 'z'")
        return np.zeros(len(species), dtype=float)
    charges = np.asarray(params["z"], dtype=float).flatten()
    if charges.size != len(species):
        errors.append(f"charge vector 'z' length {charges.size} does not match species length {len(species)}")
        return np.zeros(len(species), dtype=float)
    if np.any(~np.isfinite(charges)):
        errors.append("charge vector 'z' contains non-finite values")
    return charges


def _check_born(
    params: Mapping[str, Any],
    species: list[str],
    charges: np.ndarray,
    errors: list[str],
) -> None:
    if not np.any(np.abs(charges) > 1.0e-12):
        return
    if "d_born" not in params:
        errors.append("charged species present but d_born vector is missing")
        return
    values = np.asarray(params["d_born"], dtype=float).flatten()
    if values.size != len(species):
        errors.append(f"d_born length {values.size} does not match species length {len(species)}")
        return
    for label, charge, value in zip(species, charges, values):
        if abs(charge) > 1.0e-12 and (not np.isfinite(value) or value <= 0.0):
            errors.append(f"d_born for charged species {label} must be finite and positive")


def _check_binary_matrices(
    params: Mapping[str, Any],
    species: list[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    n = len(species)
    for key in ("k_ij", "l_ij", "k_hb", "k_hb_ij"):
        if key not in params:
            if key == "k_ij":
                warnings.append("binary interaction matrix 'k_ij' is missing")
            continue
        matrix = np.asarray(params[key], dtype=float)
        if matrix.shape != (n, n):
            errors.append(f"binary interaction matrix '{key}' shape {matrix.shape} does not match ({n}, {n})")
        elif np.any(~np.isfinite(matrix)):
            errors.append(f"binary interaction matrix '{key}' contains non-finite values")


def _check_reactions(species: list[str], reactions: Sequence[Any], errors: list[str]) -> None:
    species_set = set(species)
    for reaction in reactions:
        stoich = getattr(reaction, "stoichiometry", {})
        for label in stoich:
            if str(label) not in species_set:
                errors.append(f"Unknown species '{label}' in reaction stoichiometry")
