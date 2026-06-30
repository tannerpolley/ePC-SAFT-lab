"""Chemical-equilibrium schema and conservation-basis compilation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np
from epcsaft import InputError

_BASIS_TOLERANCE = 1.0e-10
GAS_CONSTANT_J_PER_MOL_K = 8.31446261815324
_ACTIVITY_CONVENTIONS = frozenset({"mole_fraction_activity", "molality", "fugacity", "eos_x_phi", "eos_x_gamma"})
_EOS_ACTIVITY_CONVENTIONS = frozenset({"eos_x_phi", "eos_x_gamma"})
_EQUILIBRIUM_CONSTANT_FORMS = frozenset({"K", "ln_K", "log_K", "log10_K", "delta_g_standard"})


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
class StandardStateRecord:
    """Explicit standard-state convention for a standalone CE reaction constant."""

    label: str
    activity_convention: str
    temperature_K: float
    pressure_Pa: float
    standard_molality_mol_kg: float | None = None
    standard_fugacity_Pa: float | None = None
    eos_reference_phase: str | None = None
    metadata: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", _clean_label(self.label, "standard-state label"))
        convention = _clean_label(self.activity_convention, "activity convention")
        if convention not in _ACTIVITY_CONVENTIONS:
            raise InputError(f"unsupported activity convention '{convention}'.")
        object.__setattr__(self, "activity_convention", convention)
        object.__setattr__(self, "temperature_K", _positive_finite_float(self.temperature_K, "temperature_K"))
        object.__setattr__(self, "pressure_Pa", _positive_finite_float(self.pressure_Pa, "pressure_Pa"))

        molality = _optional_positive_float(self.standard_molality_mol_kg, "standard molality")
        fugacity = _optional_positive_float(self.standard_fugacity_Pa, "standard fugacity")
        object.__setattr__(self, "standard_molality_mol_kg", molality)
        object.__setattr__(self, "standard_fugacity_Pa", fugacity)

        reference_phase = self.eos_reference_phase
        if reference_phase is not None:
            reference_phase = _clean_label(reference_phase, "EOS reference phase")
        object.__setattr__(self, "eos_reference_phase", reference_phase)

        if convention == "molality" and molality is None:
            raise InputError("molality standard states require standard molality metadata.")
        if convention == "fugacity" and fugacity is None:
            raise InputError("fugacity standard states require standard fugacity metadata.")
        if convention in _EOS_ACTIVITY_CONVENTIONS and reference_phase is None:
            raise InputError(f"{convention} standard states require an EOS reference phase.")

        metadata = (
            {} if self.metadata is None else {str(key): _json_scalar(value) for key, value in self.metadata.items()}
        )
        object.__setattr__(self, "metadata", MappingProxyType(metadata))

    def to_payload(self) -> dict[str, Any]:
        """Return a JSON-like standard-state payload."""

        payload: dict[str, Any] = {
            "label": self.label,
            "activity_convention": self.activity_convention,
            "temperature_K": float(self.temperature_K),
            "pressure_Pa": float(self.pressure_Pa),
        }
        if self.standard_molality_mol_kg is not None:
            payload["standard_molality_mol_kg"] = float(self.standard_molality_mol_kg)
        if self.standard_fugacity_Pa is not None:
            payload["standard_fugacity_Pa"] = float(self.standard_fugacity_Pa)
        if self.eos_reference_phase is not None:
            payload["eos_reference_phase"] = self.eos_reference_phase
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload


@dataclass(frozen=True, slots=True)
class EquilibriumConstantRecord:
    """Equilibrium constant with explicit units and standard-state convention."""

    reaction_label: str
    value: float
    form: str
    units: str
    standard_state: StandardStateRecord
    source: str
    source_constant_label: str
    metadata: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "reaction_label", _clean_label(self.reaction_label, "reaction label"))
        object.__setattr__(self, "value", _finite_float(self.value, "equilibrium constant value"))
        form = _clean_label(self.form, "equilibrium constant form")
        if form not in _EQUILIBRIUM_CONSTANT_FORMS:
            raise InputError(f"unsupported equilibrium constant form '{form}'.")
        object.__setattr__(self, "form", form)
        if form == "K" and self.value <= 0.0:
            raise InputError("dimensionless equilibrium constants must be positive.")
        units = _clean_label(self.units, "equilibrium constant units")
        _require_units_for_form(form, units)
        object.__setattr__(self, "units", units)
        if not isinstance(self.standard_state, StandardStateRecord):
            raise InputError("equilibrium constant records require a standard-state record.")
        object.__setattr__(self, "source", _clean_label(self.source, "equilibrium constant source"))
        object.__setattr__(
            self,
            "source_constant_label",
            _clean_label(self.source_constant_label, "source constant label"),
        )
        metadata = (
            {} if self.metadata is None else {str(key): _json_scalar(value) for key, value in self.metadata.items()}
        )
        object.__setattr__(self, "metadata", MappingProxyType(metadata))

    def ln_equilibrium_constant(self) -> float:
        """Convert the declared constant to natural-log form."""

        if self.form == "K":
            if self.value <= 0.0:
                raise InputError("dimensionless equilibrium constants must be positive.")
            return float(np.log(self.value))
        if self.form == "ln_K":
            return float(self.value)
        if self.form in {"log_K", "log10_K"}:
            return float(self.value * np.log(10.0))
        if self.form == "delta_g_standard":
            return float(-self.value / (GAS_CONSTANT_J_PER_MOL_K * self.standard_state.temperature_K))
        raise InputError(f"unsupported equilibrium constant form '{self.form}'.")

    def to_payload(self) -> dict[str, Any]:
        """Return a JSON-like equilibrium-constant payload."""

        payload: dict[str, Any] = {
            "reaction_label": self.reaction_label,
            "value": float(self.value),
            "form": self.form,
            "units": self.units,
            "ln_equilibrium_constant": self.ln_equilibrium_constant(),
            "standard_state": self.standard_state.to_payload(),
            "source": self.source,
            "source_constant_label": self.source_constant_label,
        }
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload


@dataclass(frozen=True, slots=True)
class StandardStateRegistry:
    """Ordered registry of reaction constants for standalone CE preparation."""

    records: Mapping[str, EquilibriumConstantRecord]

    def __post_init__(self) -> None:
        object.__setattr__(self, "records", MappingProxyType(dict(self.records)))

    @property
    def reaction_labels(self) -> tuple[str, ...]:
        """Return registry reaction labels in insertion order."""

        return tuple(self.records)

    def to_native_payload(self) -> dict[str, Any]:
        """Return a JSON-like payload that can cross the native request boundary."""

        return {
            "reaction_labels": list(self.reaction_labels),
            "records": [record.to_payload() for record in self.records.values()],
        }


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
        for field in (
            "conservation_matrix",
            "charge_vector",
            "stoichiometric_matrix",
            "feed_amounts",
            "conservation_totals",
        ):
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
            np.max(np.abs(conservation_matrix @ stoichiometric_matrix.T)) if stoichiometric_matrix.size else 0.0
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


def build_standard_state_registry(records: Sequence[EquilibriumConstantRecord]) -> StandardStateRegistry:
    """Build a deterministic registry keyed by reaction label."""

    registry: dict[str, EquilibriumConstantRecord] = {}
    for record in records:
        if not isinstance(record, EquilibriumConstantRecord):
            raise InputError("standard-state registry entries must be equilibrium constant records.")
        if record.reaction_label in registry:
            raise InputError(f"duplicate equilibrium constant for reaction '{record.reaction_label}'.")
        registry[record.reaction_label] = record
    if not registry:
        raise InputError("standard-state registry requires at least one equilibrium constant record.")
    return StandardStateRegistry(registry)


def solve_chemical_equilibrium_nlp_activation(
    compiled: CompiledChemicalEquilibrium,
    standard_states: StandardStateRegistry,
    *,
    initial_amounts: Sequence[float] | None = None,
    max_iterations: int = 100,
    tolerance: float = 1.0e-8,
    timeout_seconds: float | None = None,
    hessian_mode: str = "auto",
    ipopt_iteration_history_limit: int = 20,
    balance_tolerance: float = 1.0e-9,
    reaction_stationarity_tolerance: float = 1.0e-8,
    continuation_state: Mapping[str, Any] | None = None,
    ipopt_linear_solver: str = "auto",
    eos_mixture: Any | None = None,
) -> dict[str, Any]:
    """Solve standalone CE through the internal activation-matrix NLP/Ipopt path."""

    if not isinstance(compiled, CompiledChemicalEquilibrium):
        raise InputError("chemical equilibrium NLP activation requires a compiled CE schema.")
    if not isinstance(standard_states, StandardStateRegistry):
        raise InputError("chemical equilibrium NLP activation requires a standard-state registry.")
    if tuple(standard_states.reaction_labels) != tuple(compiled.reaction_labels):
        raise InputError("standard-state registry reaction order must match the compiled CE schema.")
    if hessian_mode not in {"auto", "exact", "limited-memory"}:
        raise InputError("hessian_mode must be 'auto', 'exact', or 'limited-memory'.")
    iterations = int(max_iterations)
    if iterations <= 0:
        raise InputError("max_iterations must be positive.")
    history_limit = int(ipopt_iteration_history_limit)
    if history_limit < 0:
        raise InputError("ipopt_iteration_history_limit must be non-negative.")
    solve_tolerance = _positive_finite_float(tolerance, "tolerance")
    balance_tol = _positive_finite_float(balance_tolerance, "balance_tolerance")
    reaction_tol = _positive_finite_float(reaction_stationarity_tolerance, "reaction_stationarity_tolerance")
    timeout = 0.0 if timeout_seconds is None else _positive_finite_float(timeout_seconds, "timeout_seconds")
    initial = (
        []
        if initial_amounts is None
        else _positive_amount_vector(initial_amounts, compiled.species_count, "initial_amounts").tolist()
    )

    from ._native import extension_native_core

    core = extension_native_core()
    return core._native_chemical_equilibrium_nlp_activation(
        compiled.to_native_payload(),
        standard_states.to_native_payload(),
        initial,
        iterations,
        solve_tolerance,
        timeout,
        hessian_mode,
        history_limit,
        balance_tol,
        reaction_tol,
        continuation_state,
        eos_mixture,
        linear_solver=str(ipopt_linear_solver),
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


def _positive_finite_float(value: Any, label: str) -> float:
    if value is None:
        raise InputError(f"{label} metadata is required.")
    out = _finite_float(value, label)
    if out <= 0.0:
        raise InputError(f"{label} must be positive.")
    return out


def _optional_positive_float(value: Any, label: str) -> float | None:
    if value is None:
        return None
    out = _finite_float(value, label)
    if out <= 0.0:
        raise InputError(f"{label} must be positive.")
    return out


def _require_units_for_form(form: str, units: str) -> None:
    if form in {"K", "ln_K", "log_K", "log10_K"} and units != "dimensionless":
        raise InputError(f"{form} equilibrium constants require dimensionless units.")
    if form == "delta_g_standard" and units != "J/mol":
        raise InputError("delta_g_standard equilibrium constants require J/mol units.")


def _json_scalar(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Mapping):
        return {str(key): _json_scalar(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_scalar(item) for item in value]
    return value


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


def _positive_amount_vector(values: Sequence[float], expected_size: int, label: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.shape != (expected_size,):
        raise InputError(f"{label} must contain one amount per species.")
    if not np.all(np.isfinite(array)):
        raise InputError(f"{label} must be finite.")
    if np.any(array <= 0.0):
        raise InputError(f"{label} must be strictly positive.")
    return array.copy()


def _matrix_rank(matrix: np.ndarray) -> int:
    if matrix.size == 0:
        return 0
    return int(np.linalg.matrix_rank(matrix, tol=_BASIS_TOLERANCE))
