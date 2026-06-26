"""Chemical-equilibrium schema and conservation-basis compilation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np

from epcsaft import InputError


_BASIS_TOLERANCE = 1.0e-10


@dataclass(frozen=True, slots=True)
class ChemicalSpecies:
    """True species entry for standalone homogeneous chemical equilibrium."""

    label: str
    conservation: Mapping[str, float]
    charge: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", _clean_label(self.label, "species label"))
        object.__setattr__(
            self,
            "conservation",
            MappingProxyType(
                {
                    _clean_label(label, "conservation label"): _finite_float(value, "conservation coefficient")
                    for label, value in self.conservation.items()
                }
            ),
        )
        object.__setattr__(self, "charge", _finite_float(self.charge, "species charge"))


@dataclass(frozen=True, slots=True)
class ChemicalReaction:
    """Stoichiometric reaction entry using true species labels."""

    label: str
    stoichiometry: Mapping[str, float]

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", _clean_label(self.label, "reaction label"))
        object.__setattr__(
            self,
            "stoichiometry",
            MappingProxyType(
                {
                    _clean_label(label, "stoichiometric species label"): _finite_float(
                        value,
                        "stoichiometric coefficient",
                    )
                    for label, value in self.stoichiometry.items()
                    if _finite_float(value, "stoichiometric coefficient") != 0.0
                }
            ),
        )
        if not self.stoichiometry:
            raise InputError(f"reaction '{self.label}' must contain at least one nonzero stoichiometric coefficient.")


@dataclass(frozen=True, slots=True)
class CompiledChemicalEquilibrium:
    """Solver-entry schema payload for homogeneous chemical equilibrium."""

    species_labels: tuple[str, ...]
    reaction_labels: tuple[str, ...]
    conservation_labels: tuple[str, ...]
    conservation_matrix: np.ndarray
    charge_vector: np.ndarray
    stoichiometric_matrix: np.ndarray
    feed_amounts: np.ndarray
    conservation_totals: np.ndarray
    reaction_rank: int
    conservation_rank: int
    diagnostics: Mapping[str, Any]

    def __post_init__(self) -> None:
        for field in ("conservation_matrix", "charge_vector", "stoichiometric_matrix", "feed_amounts", "conservation_totals"):
            array = np.array(getattr(self, field), dtype=float, copy=True)
            array.setflags(write=False)
            object.__setattr__(self, field, array)
        object.__setattr__(self, "diagnostics", MappingProxyType(dict(self.diagnostics)))

    @property
    def reaction_count(self) -> int:
        """Return the number of declared reactions."""

        return len(self.reaction_labels)

    @property
    def species_count(self) -> int:
        """Return the number of true species."""

        return len(self.species_labels)

    def to_native_payload(self) -> dict[str, Any]:
        """Return a JSON-like payload that can cross the native request boundary."""

        return {
            "species_labels": list(self.species_labels),
            "reaction_labels": list(self.reaction_labels),
            "conservation_labels": list(self.conservation_labels),
            "conservation_matrix": self.conservation_matrix.tolist(),
            "charge_vector": self.charge_vector.tolist(),
            "stoichiometric_matrix": self.stoichiometric_matrix.tolist(),
            "feed_amounts": self.feed_amounts.tolist(),
            "conservation_totals": self.conservation_totals.tolist(),
            "reaction_rank": int(self.reaction_rank),
            "conservation_rank": int(self.conservation_rank),
            "diagnostics": dict(self.diagnostics),
        }


def compile_reaction_set(
    *,
    species: Sequence[ChemicalSpecies],
    reactions: Sequence[ChemicalReaction],
    feed_amounts: Mapping[str, float],
) -> CompiledChemicalEquilibrium:
    """Compile true-species reactions into conservation and stoichiometric matrices."""

    species_tuple = tuple(species)
    reaction_tuple = tuple(reactions)
    if not species_tuple:
        raise InputError("chemical equilibrium requires at least one true species.")
    if not reaction_tuple:
        raise InputError("chemical equilibrium requires at least one reaction.")

    species_labels = tuple(item.label for item in species_tuple)
    _require_unique(species_labels, "species")
    species_index = {label: index for index, label in enumerate(species_labels)}

    reaction_labels = tuple(item.label for item in reaction_tuple)
    _require_unique(reaction_labels, "reaction")

    conservation_labels = _conservation_labels(species_tuple)
    conservation_matrix = _conservation_matrix(species_tuple, conservation_labels)
    charge_vector = np.asarray([item.charge for item in species_tuple], dtype=float)
    stoichiometric_matrix = _stoichiometric_matrix(reaction_tuple, species_index)
    _reject_duplicate_reactions(stoichiometric_matrix)
    _require_reactions_conserve_basis(conservation_matrix, stoichiometric_matrix, reaction_labels)

    feed = _feed_vector(feed_amounts, species_index)
    conservation_totals = conservation_matrix @ feed
    reaction_rank = _matrix_rank(stoichiometric_matrix)
    conservation_rank = _matrix_rank(conservation_matrix)
    dependent_reaction_count = len(reaction_labels) - reaction_rank

    diagnostics = {
        "reaction_count": len(reaction_labels),
        "species_count": len(species_labels),
        "reaction_rank": reaction_rank,
        "conservation_rank": conservation_rank,
        "rank_deficient_reactions": dependent_reaction_count > 0,
        "dependent_reaction_count": dependent_reaction_count,
        "conservation_residual_max_abs": float(
            np.max(np.abs(conservation_matrix @ stoichiometric_matrix.T))
            if stoichiometric_matrix.size
            else 0.0
        ),
    }
    return CompiledChemicalEquilibrium(
        species_labels=species_labels,
        reaction_labels=reaction_labels,
        conservation_labels=conservation_labels,
        conservation_matrix=conservation_matrix,
        charge_vector=charge_vector,
        stoichiometric_matrix=stoichiometric_matrix,
        feed_amounts=feed,
        conservation_totals=conservation_totals,
        reaction_rank=reaction_rank,
        conservation_rank=conservation_rank,
        diagnostics=diagnostics,
    )


def _clean_label(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise InputError(f"{label} must be a string.")
    out = value.strip()
    if not out:
        raise InputError(f"{label} must be non-empty.")
    return out


def _finite_float(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise InputError(f"{label} must be a finite real number.")
    out = float(value)
    if not np.isfinite(out):
        raise InputError(f"{label} must be finite.")
    return out


def _require_unique(labels: Sequence[str], kind: str) -> None:
    seen: set[str] = set()
    for label in labels:
        if label in seen:
            raise InputError(f"duplicate {kind} label '{label}'.")
        seen.add(label)


def _conservation_labels(species: Sequence[ChemicalSpecies]) -> tuple[str, ...]:
    labels: list[str] = []
    for item in species:
        for label in item.conservation:
            if label not in labels:
                labels.append(label)
    if not labels:
        raise InputError("chemical equilibrium species require at least one conservation basis label.")
    if any(abs(item.charge) > _BASIS_TOLERANCE for item in species) and "charge" not in labels:
        labels.append("charge")
    return tuple(labels)


def _conservation_matrix(species: Sequence[ChemicalSpecies], labels: Sequence[str]) -> np.ndarray:
    matrix = np.zeros((len(labels), len(species)), dtype=float)
    for column, item in enumerate(species):
        for row, label in enumerate(labels):
            if label == "charge":
                matrix[row, column] = item.charge
            else:
                matrix[row, column] = float(item.conservation.get(label, 0.0))
    return matrix


def _stoichiometric_matrix(
    reactions: Sequence[ChemicalReaction],
    species_index: Mapping[str, int],
) -> np.ndarray:
    matrix = np.zeros((len(reactions), len(species_index)), dtype=float)
    for row, reaction in enumerate(reactions):
        has_reactant = False
        has_product = False
        for label, coefficient in reaction.stoichiometry.items():
            if label not in species_index:
                raise InputError(f"reaction '{reaction.label}' references unknown species '{label}'.")
            matrix[row, species_index[label]] = float(coefficient)
            has_reactant = has_reactant or coefficient < 0.0
            has_product = has_product or coefficient > 0.0
        if not has_reactant or not has_product:
            raise InputError(f"reaction '{reaction.label}' must contain at least one reactant and one product.")
    return matrix


def _reject_duplicate_reactions(stoichiometric_matrix: np.ndarray) -> None:
    signatures: set[tuple[float, ...]] = set()
    for row in stoichiometric_matrix:
        scale = float(np.max(np.abs(row)))
        if scale <= 0.0:
            raise InputError("reaction stoichiometry must contain a nonzero vector.")
        normalized = row / scale
        first_nonzero = next(value for value in normalized if abs(float(value)) > _BASIS_TOLERANCE)
        if first_nonzero < 0.0:
            normalized = -normalized
        signature = tuple(round(float(value), 12) for value in normalized)
        if signature in signatures:
            raise InputError("duplicate reaction stoichiometry is not allowed.")
        signatures.add(signature)


def _require_reactions_conserve_basis(
    conservation_matrix: np.ndarray,
    stoichiometric_matrix: np.ndarray,
    reaction_labels: Sequence[str],
) -> None:
    residuals = conservation_matrix @ stoichiometric_matrix.T
    for column, label in enumerate(reaction_labels):
        residual = residuals[:, column]
        if np.max(np.abs(residual)) > _BASIS_TOLERANCE:
            raise InputError(f"reaction '{label}' violates the declared conservation basis.")


def _feed_vector(feed_amounts: Mapping[str, float], species_index: Mapping[str, int]) -> np.ndarray:
    feed = np.zeros(len(species_index), dtype=float)
    for label, value in feed_amounts.items():
        clean_label = _clean_label(label, "feed species label")
        if clean_label not in species_index:
            raise InputError(f"feed amount references unknown species '{clean_label}'.")
        amount = _finite_float(value, "feed amount")
        if amount < 0.0:
            raise InputError("feed amount values must be non-negative.")
        feed[species_index[clean_label]] = amount
    if float(np.sum(feed)) <= 0.0:
        raise InputError("feed amount values must contain positive material.")
    return feed


def _matrix_rank(matrix: np.ndarray) -> int:
    if matrix.size == 0:
        return 0
    return int(np.linalg.matrix_rank(matrix, tol=_BASIS_TOLERANCE))
