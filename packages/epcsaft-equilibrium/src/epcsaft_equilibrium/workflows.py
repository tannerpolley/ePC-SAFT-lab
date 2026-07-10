"""Selector-backed production equilibrium workflow helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from numbers import Integral, Real
from types import MappingProxyType
from typing import Any, Literal

import numpy as np
from epcsaft import InputError, SolutionError
from epcsaft.runtime import RouteDiagnosticsView

from ._native import extension_native_core
from .chemical_equilibrium import (
    ChemicalReaction,
    ChemicalSpecies,
    CompiledChemicalEquilibrium,
    EquilibriumConstantRecord,
    StandardStateRegistry,
    _solve_closed_chemical_equilibrium_nlp_activation,
    _unsupported_standard_state_request_diagnostics,
    build_standard_state_registry,
    compile_reaction_set,
)
from .core.native_requests import (
    EQUILIBRIUM_ROUTE_SPECS,
    NativeSelectorRouteSpec,
    chemical_equilibrium_schema_payload,
    selector_request_payload,
    selector_route_solver_tolerances,
)
from .core.native_results import (
    chemical_equilibrium_result_diagnostics,
    native_route_diagnostics,
    native_route_solved_pressure,
    native_route_solved_temperature,
    native_selector_route_to_result,
    raise_native_route_rejected,
)


@dataclass(frozen=True, slots=True)
class EquilibriumSolverOptions:
    """Numerical controls for the production selector equilibrium route."""

    max_iterations: int = 180
    tolerance: float = 1.0e-6
    min_composition: float = 1.0e-12
    timeout_seconds: float | None = None
    hessian_mode: Literal["auto", "exact", "limited-memory"] = "auto"
    ipopt_iteration_history_limit: int = 20
    ipopt_print_level: int = 0
    ipopt_linear_solver: str = "auto"
    ipopt_acceptable_tolerance: float | None = None
    ipopt_constraint_violation_tolerance: float | None = None
    ipopt_dual_infeasibility_tolerance: float | None = None
    ipopt_complementarity_tolerance: float | None = None
    continuation_state: Mapping[str, Any] | None = None


def compile_chemical_equilibrium_schema(
    *,
    species: Sequence[ChemicalSpecies],
    reactions: Sequence[ChemicalReaction],
    feed_amounts: Mapping[str, float],
) -> CompiledChemicalEquilibrium:
    """Compile standalone CE schema inputs without entering native solver code."""

    return compile_reaction_set(species=species, reactions=reactions, feed_amounts=feed_amounts)


def chemical_equilibrium_native_payload(compiled: CompiledChemicalEquilibrium) -> dict[str, Any]:
    """Return the native-boundary payload for a compiled standalone CE schema."""

    return chemical_equilibrium_schema_payload(compiled)


def _run_standalone_ce_validation(
    *,
    species: Sequence[ChemicalSpecies],
    reactions: Sequence[ChemicalReaction],
    feed_amounts: Mapping[str, float],
    equilibrium_constants: Sequence[EquilibriumConstantRecord],
    initial_amounts: Sequence[float] | None = None,
    eos_mixture: Any | None = None,
    solver_options: EquilibriumSolverOptions | Mapping[str, Any] | None = None,
) -> _StandaloneCEValidationResult:
    """Run the retained standalone-CE diagnostic through the internal NLP path."""

    compiled = compile_reaction_set(species=species, reactions=reactions, feed_amounts=feed_amounts)
    standard_states = build_standard_state_registry(equilibrium_constants)
    native_eos_mixture = _reactive_speciation_eos_context(standard_states, eos_mixture)
    options = _normalize_options(solver_options)
    initial_seed = _optional_positive_initial_amounts(initial_amounts, compiled.species_count)
    payload = _solve_closed_chemical_equilibrium_nlp_activation(
        compiled,
        standard_states,
        initial_amounts=initial_seed,
        eos_mixture=native_eos_mixture,
        max_iterations=options.max_iterations,
        tolerance=options.tolerance,
        timeout_seconds=options.timeout_seconds,
        hessian_mode=options.hessian_mode,
        ipopt_iteration_history_limit=options.ipopt_iteration_history_limit,
        balance_tolerance=options.tolerance,
        reaction_stationarity_tolerance=options.tolerance,
        continuation_state=options.continuation_state,
        ipopt_linear_solver=options.ipopt_linear_solver,
    )
    return _reactive_speciation_result_from_payload(compiled, standard_states, payload)


def _optional_positive_initial_amounts(
    initial_amounts: Sequence[float] | None,
    species_count: int,
) -> list[float] | None:
    if initial_amounts is None:
        return None
    values = np.asarray(initial_amounts, dtype=float)
    if values.shape != (species_count,):
        raise InputError(f"initial_amounts must contain exactly {species_count} values.")
    if not np.all(np.isfinite(values)):
        raise InputError("initial_amounts must be finite.")
    if np.any(values <= 0.0):
        raise InputError("initial_amounts must be strictly positive.")
    return values.tolist()


def _reactive_speciation_eos_context(
    standard_states: StandardStateRegistry,
    eos_mixture: Any | None,
) -> Any | None:
    conventions = {record.standard_state.activity_convention for record in standard_states.records.values()}
    if len(conventions) != 1:
        raise InputError("reactive_speciation requires a single activity convention.")
    convention = next(iter(conventions))
    if convention == "mole_fraction_activity":
        if eos_mixture is not None:
            raise InputError("reactive_speciation eos_mixture is only valid with EOS activity standard states.")
        return None
    if convention not in {"eos_x_phi", "eos_x_gamma"}:
        raise InputError(
            f"reactive_speciation unsupported activity convention '{convention}'.",
            _unsupported_standard_state_request_diagnostics(convention),
        )
    if eos_mixture is None:
        raise InputError(f"reactive_speciation {convention} standard states require eos_mixture.")
    _require_single_eos_activity_context(standard_states)
    return getattr(eos_mixture, "native", eos_mixture)


def _require_single_eos_activity_context(standard_states: StandardStateRegistry) -> None:
    records = list(standard_states.records.values())
    first = records[0].standard_state
    for record in records[1:]:
        state = record.standard_state
        if (
            state.eos_reference_phase != first.eos_reference_phase
            or state.temperature_K != first.temperature_K
            or state.pressure_Pa != first.pressure_Pa
        ):
            raise InputError("reactive_speciation EOS activity standard states require one shared EOS context.")


def _reactive_speciation_result_from_payload(
    compiled: CompiledChemicalEquilibrium,
    standard_states: StandardStateRegistry,
    payload: Mapping[str, Any],
) -> _StandaloneCEValidationResult:
    diagnostics = chemical_equilibrium_result_diagnostics(payload)
    if payload.get("accepted") is not True:
        raise SolutionError("reactive_speciation native solve was not accepted.", diagnostics)

    amounts = _required_float_vector(payload, "amounts", compiled.species_count, diagnostics)
    mole_fractions = _required_float_vector(payload, "mole_fractions", compiled.species_count, diagnostics)
    activities = _optional_float_vector(payload, "activities", compiled.species_count, diagnostics)
    if activities is None:
        activities = mole_fractions
    standard_mu_rt = _required_float_vector(payload, "standard_mu_rt", compiled.species_count, diagnostics)
    if np.any(mole_fractions <= 0.0):
        raise SolutionError("reactive_speciation native payload returned nonpositive mole fractions.", diagnostics)
    if np.any(activities <= 0.0):
        raise SolutionError("reactive_speciation native payload returned nonpositive activities.", diagnostics)
    reduced_mu = standard_mu_rt + np.log(activities)

    return _StandaloneCEValidationResult(
        species_labels=compiled.species_labels,
        reaction_labels=compiled.reaction_labels,
        amounts=amounts,
        mole_fractions=mole_fractions,
        species_amounts=_labeled_float_map(compiled.species_labels, amounts, "amounts", diagnostics),
        activities=_labeled_float_map(compiled.species_labels, activities, "activities", diagnostics),
        reduced_chemical_potentials=_labeled_float_map(
            compiled.species_labels,
            reduced_mu,
            "reduced_chemical_potentials",
            diagnostics,
        ),
        reaction_extents=_reaction_extent_map(compiled, amounts, diagnostics),
        balances=_labeled_float_map(
            compiled.conservation_labels,
            _required_float_vector(payload, "balance_residuals", len(compiled.conservation_labels), diagnostics),
            "balance_residuals",
            diagnostics,
        ),
        affinities=_labeled_float_map(
            compiled.reaction_labels,
            _required_float_vector(payload, "reaction_affinities", compiled.reaction_count, diagnostics),
            "reaction_affinities",
            diagnostics,
        ),
        standard_state_metadata={
            label: record.standard_state.to_payload() for label, record in standard_states.records.items()
        },
        diagnostics=diagnostics,
    )


def _validate_internal_activation(
    activation: object,
    *,
    family_key: str,
    diagnostics: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(activation, Mapping):
        raise SolutionError(f"{family_key} native payload omitted its internal activation contract.", diagnostics)
    normalized = dict(activation)
    if (
        normalized.get("key") != family_key
        or normalized.get("production_exposed") is not False
        or normalized.get("public_routes") != []
        or normalized.get("proof_routes") != []
    ):
        raise SolutionError(f"{family_key} native payload attempted to open a closed production surface.", diagnostics)
    return normalized


def _internal_activation_from_native(native_core: Any, family_key: str) -> dict[str, Any]:
    rows = native_core._native_equilibrium_activation_matrix()
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        raise SolutionError(
            f"Native activation registry did not return rows for {family_key}.",
            {"family_key": family_key},
        )
    matches = [row for row in rows if isinstance(row, Mapping) and row.get("key") == family_key]
    if len(matches) != 1:
        raise SolutionError(
            f"Native activation registry must contain exactly one {family_key} row.",
            {"family_key": family_key, "matching_row_count": len(matches)},
        )
    return _validate_internal_activation(
        matches[0],
        family_key=family_key,
        diagnostics={"family_key": family_key},
    )


def _required_float_vector(
    payload: Mapping[str, Any],
    key: str,
    expected_size: int,
    diagnostics: Mapping[str, Any],
) -> np.ndarray:
    if key not in payload:
        raise SolutionError(f"reactive_speciation native payload missing {key}.", diagnostics)
    values = _readonly_float_array(payload[key])
    if values.shape != (expected_size,):
        raise SolutionError(
            f"reactive_speciation native payload field {key} has shape {values.shape}, expected {(expected_size,)}.",
            diagnostics,
        )
    if not np.all(np.isfinite(values)):
        raise SolutionError(f"reactive_speciation native payload field {key} must be finite.", diagnostics)
    return values


def _optional_float_vector(
    payload: Mapping[str, Any],
    key: str,
    expected_size: int,
    diagnostics: Mapping[str, Any],
) -> np.ndarray | None:
    if key not in payload:
        return None
    return _required_float_vector(payload, key, expected_size, diagnostics)


def _labeled_float_map(
    labels: Sequence[str],
    values: Sequence[float],
    field: str,
    diagnostics: Mapping[str, Any],
) -> dict[str, float]:
    if len(labels) != len(values):
        raise SolutionError(f"reactive_speciation cannot label {field}.", diagnostics)
    return {str(label): float(value) for label, value in zip(labels, values)}


def _reaction_extent_map(
    compiled: CompiledChemicalEquilibrium,
    amounts: np.ndarray,
    diagnostics: Mapping[str, Any],
) -> dict[str, float]:
    if compiled.reaction_rank != compiled.reaction_count:
        raise SolutionError("reactive_speciation reaction extents require an independent reaction set.", diagnostics)
    delta = np.asarray(amounts, dtype=float) - np.asarray(compiled.feed_amounts, dtype=float)
    stoichiometry_by_species = np.asarray(compiled.stoichiometric_matrix, dtype=float).T
    extents, *_ = np.linalg.lstsq(stoichiometry_by_species, delta, rcond=None)
    residual = stoichiometry_by_species @ extents - delta
    if float(np.max(np.abs(residual))) > 1.0e-8:
        raise SolutionError("reactive_speciation native amounts are inconsistent with reaction extents.", diagnostics)
    return _labeled_float_map(compiled.reaction_labels, extents, "reaction_extents", diagnostics)


def _readonly_float_array(value: Any) -> np.ndarray:
    array = np.array(value, dtype=float, copy=True)
    array.setflags(write=False)
    return array


def _freeze_fixed_spec_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _readonly_float_array(value)
    return value


def _freeze_metadata_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        array = np.array(value, copy=True)
        array.setflags(write=False)
        return array
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze_metadata_value(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_metadata_value(item) for item in value)
    if isinstance(value, np.generic):
        return value.item()
    return value


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
    diagnostics: Mapping[str, Any] | None = None

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
        diagnostics: Mapping[str, Any] | None = None,
    ) -> None:
        if ln_fugacity_coefficient is None:
            if fugacity_coefficient is None:
                ln_fugacity_coefficient = None
            else:
                ln_fugacity_coefficient = np.log(np.asarray(fugacity_coefficient, dtype=float))
        object.__setattr__(self, "label", str(label))
        object.__setattr__(self, "composition", _readonly_float_array(composition))
        object.__setattr__(self, "density", float(density))
        object.__setattr__(self, "temperature", float(temperature))
        object.__setattr__(self, "pressure", float(pressure))
        object.__setattr__(self, "phase_fraction", float(phase_fraction))
        if ln_fugacity_coefficient is not None:
            ln_fugacity_coefficient = _readonly_float_array(ln_fugacity_coefficient)
        object.__setattr__(self, "ln_fugacity_coefficient", ln_fugacity_coefficient)
        object.__setattr__(self, "diagnostics", None if diagnostics is None else _freeze_metadata_value(diagnostics))

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


def _phase_mapping(
    phases: Mapping[str, EquilibriumPhase] | Sequence[EquilibriumPhase],
) -> Mapping[str, EquilibriumPhase]:
    if isinstance(phases, Mapping):
        return MappingProxyType({str(label): phase for label, phase in phases.items()})
    return MappingProxyType({phase.label: phase for phase in phases})


def _required_single_component_residual(
    diagnostics: Mapping[str, Any], field: str
) -> float:
    if field not in diagnostics:
        raise SolutionError(
            f"single_component_vle diagnostics missing required field '{field}'.",
            diagnostics,
        )
    raw_value = diagnostics[field]
    if isinstance(raw_value, bool) or not isinstance(raw_value, Real):
        raise SolutionError(
            f"single_component_vle diagnostic '{field}' must be finite and non-negative.",
            diagnostics,
        )
    value = float(raw_value)
    if not np.isfinite(value) or value < 0.0:
        raise SolutionError(
            f"single_component_vle diagnostic '{field}' must be finite and non-negative.",
            diagnostics,
        )
    return value


@dataclass(frozen=True, slots=True)
class EquilibriumResult:
    """Structured result returned by the production equilibrium route."""

    backend: str
    problem_kind: str
    phases: Mapping[str, EquilibriumPhase] | Sequence[EquilibriumPhase]
    stable: bool
    split_detected: bool
    diagnostics: Mapping[str, Any]
    route: str = ""
    selector_route: str = ""
    composition_role: str = ""
    feed_composition: Any = None

    def __post_init__(self) -> None:
        phases = _phase_mapping(self.phases)
        object.__setattr__(self, "backend", str(self.backend))
        object.__setattr__(self, "problem_kind", str(self.problem_kind))
        object.__setattr__(self, "phases", phases)
        object.__setattr__(self, "stable", bool(self.stable))
        object.__setattr__(self, "split_detected", bool(self.split_detected))
        object.__setattr__(self, "diagnostics", _freeze_metadata_value(self.diagnostics))
        object.__setattr__(self, "route", str(self.route))
        object.__setattr__(self, "selector_route", str(self.selector_route))
        object.__setattr__(self, "composition_role", str(self.composition_role))
        if self.feed_composition is None:
            object.__setattr__(self, "feed_composition", None)
        else:
            object.__setattr__(self, "feed_composition", _readonly_float_array(self.feed_composition))

    @property
    def phase_labels(self) -> list[str]:
        """Return phase labels in result order."""

        return list(self.phases.keys())

    @property
    def pressure(self) -> float:
        """Return the common phase pressure."""

        return float(next(iter(self.phases.values())).pressure)

    @property
    def temperature(self) -> float:
        """Return the common phase temperature."""

        return float(next(iter(self.phases.values())).temperature)

    def phase(self, label: str) -> EquilibriumPhase:
        """Return one named phase."""

        return self.phases[str(label)]

    @property
    def phase_compositions(self) -> Mapping[str, np.ndarray]:
        """Return compositions keyed by phase label."""

        return MappingProxyType(
            {label: np.asarray(phase.composition, dtype=float) for label, phase in self.phases.items()}
        )

    @property
    def phase_fractions(self) -> Mapping[str, float]:
        """Return phase fractions keyed by phase label."""

        return MappingProxyType({label: float(phase.phase_fraction) for label, phase in self.phases.items()})

    @property
    def x(self) -> np.ndarray:
        """Return the liquid composition."""

        if "liquid" not in self.phases:
            raise AttributeError("x is available only for VLE routes with a 'liquid' phase.")
        return np.asarray(self.phases["liquid"].composition, dtype=float)

    @property
    def y(self) -> np.ndarray:
        """Return the vapor composition."""

        if "vapor" not in self.phases:
            raise AttributeError("y is available only for VLE routes with a 'vapor' phase.")
        return np.asarray(self.phases["vapor"].composition, dtype=float)

    @property
    def z(self) -> np.ndarray:
        """Return the feed composition for feed routes."""

        if self.feed_composition is None:
            raise AttributeError("z is available only for feed routes.")
        return np.asarray(self.feed_composition, dtype=float)

    @property
    def liquid_fraction(self) -> float:
        """Return the liquid phase fraction."""

        if "liquid" not in self.phases:
            raise AttributeError("liquid_fraction is available only for VLE routes.")
        return float(self.phases["liquid"].phase_fraction)

    @property
    def vapor_fraction(self) -> float:
        """Return the vapor phase fraction."""

        if "vapor" not in self.phases:
            raise AttributeError("vapor_fraction is available only for VLE routes.")
        return float(self.phases["vapor"].phase_fraction)

    @property
    def saturation_pressure(self) -> float:
        """Return the common saturation pressure for single-component VLE."""

        if self.route != "single_component_vle":
            raise AttributeError("saturation_pressure is available only for single_component_vle.")
        return self.pressure

    @property
    def P_sat(self) -> float:
        """Return the common saturation pressure for single-component VLE."""

        return self.saturation_pressure

    @property
    def vapor_density(self) -> float:
        """Return the vapor density for single-component VLE."""

        if self.route != "single_component_vle" or "vapor" not in self.phases:
            raise AttributeError("vapor_density is available only for single_component_vle.")
        return float(self.phases["vapor"].density)

    @property
    def liquid_density(self) -> float:
        """Return the liquid density for single-component VLE."""

        if self.route != "single_component_vle" or "liquid" not in self.phases:
            raise AttributeError("liquid_density is available only for single_component_vle.")
        return float(self.phases["liquid"].density)

    @property
    def route_diagnostics(self) -> RouteDiagnosticsView:
        """Return a typed view over route diagnostics."""

        return RouteDiagnosticsView(self.diagnostics)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-like result payload."""

        payload = {
            "backend": self.backend,
            "problem_kind": self.problem_kind,
            "route": self.route,
            "selector_route": self.selector_route,
            "phase_labels": self.phase_labels,
            "phases": {label: phase.to_dict() for label, phase in self.phases.items()},
            "stable": self.stable,
            "split_detected": self.split_detected,
            "x": self.x.tolist() if "liquid" in self.phases else None,
            "y": self.y.tolist() if "vapor" in self.phases else None,
            "z": None if self.feed_composition is None else self.z.tolist(),
            "phase_compositions": {label: phase.composition.tolist() for label, phase in self.phases.items()},
            "phase_fractions": {label: phase.phase_fraction for label, phase in self.phases.items()},
            "liquid_fraction": self.liquid_fraction if "liquid" in self.phases else None,
            "vapor_fraction": self.vapor_fraction if "vapor" in self.phases else None,
            "diagnostics": _json_like(self.diagnostics),
        }
        if self.route == "single_component_vle":
            payload["P_sat"] = self.P_sat
            payload["vapor_density"] = self.vapor_density
            payload["liquid_density"] = self.liquid_density
            payload["saturation_residuals"] = {
                "pressure_consistency_norm": _required_single_component_residual(
                    self.diagnostics, "pressure_consistency_norm"
                ),
                "chemical_potential_consistency_norm": _required_single_component_residual(
                    self.diagnostics, "chemical_potential_consistency_norm"
                ),
                "ln_fugacity_consistency_norm": _required_single_component_residual(
                    self.diagnostics, "ln_fugacity_consistency_norm"
                ),
            }
        return payload


@dataclass(frozen=True, slots=True)
class _StandaloneCEValidationResult:
    """Internal structured result for retained standalone-CE validation."""

    species_labels: tuple[str, ...]
    reaction_labels: tuple[str, ...]
    amounts: Any
    mole_fractions: Any
    species_amounts: Mapping[str, float]
    activities: Mapping[str, float]
    reduced_chemical_potentials: Mapping[str, float]
    reaction_extents: Mapping[str, float]
    balances: Mapping[str, float]
    affinities: Mapping[str, float]
    standard_state_metadata: Mapping[str, Mapping[str, Any]]
    diagnostics: Mapping[str, Any]
    route: str = "reactive_speciation"
    problem_kind: str = "standalone_chemical_equilibrium"
    phase_scope: str = "homogeneous"
    coupling_scope: str = "chemical_equilibrium_only"
    capability_scope: str = "standalone_ce_only"
    closed_surfaces: tuple[str, ...] = ("reactive_lle", "reactive_electrolyte_lle", "cpe")

    def __post_init__(self) -> None:
        object.__setattr__(self, "species_labels", tuple(str(item) for item in self.species_labels))
        object.__setattr__(self, "reaction_labels", tuple(str(item) for item in self.reaction_labels))
        object.__setattr__(self, "amounts", _readonly_float_array(self.amounts))
        object.__setattr__(self, "mole_fractions", _readonly_float_array(self.mole_fractions))
        for name in (
            "species_amounts",
            "activities",
            "reduced_chemical_potentials",
            "reaction_extents",
            "balances",
            "affinities",
        ):
            object.__setattr__(
                self,
                name,
                MappingProxyType({str(key): float(value) for key, value in getattr(self, name).items()}),
            )
        object.__setattr__(
            self,
            "standard_state_metadata",
            MappingProxyType(
                {str(key): MappingProxyType(dict(value)) for key, value in self.standard_state_metadata.items()}
            ),
        )
        object.__setattr__(self, "diagnostics", _freeze_metadata_value(self.diagnostics))
        object.__setattr__(self, "closed_surfaces", tuple(str(item) for item in self.closed_surfaces))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-like standalone CE payload."""

        return {
            "route": self.route,
            "problem_kind": self.problem_kind,
            "capability_scope": self.capability_scope,
            "phase_scope": self.phase_scope,
            "coupling_scope": self.coupling_scope,
            "closed_surfaces": list(self.closed_surfaces),
            "species_labels": list(self.species_labels),
            "reaction_labels": list(self.reaction_labels),
            "amounts": self.amounts.tolist(),
            "mole_fractions": self.mole_fractions.tolist(),
            "species_amounts": dict(self.species_amounts),
            "activities": dict(self.activities),
            "reduced_chemical_potentials": dict(self.reduced_chemical_potentials),
            "reaction_extents": dict(self.reaction_extents),
            "balances": dict(self.balances),
            "affinities": dict(self.affinities),
            "standard_state_metadata": _json_like(self.standard_state_metadata),
            "diagnostics": _json_like(self.diagnostics),
        }


@dataclass(frozen=True, slots=True)
class EquilibriumProblem:
    """Read-only configured equilibrium problem metadata."""

    route: str
    selector_route: str
    knowns: tuple[str, ...]
    unknowns: tuple[str, ...]
    composition_role: str
    activation_key: str
    expected_phase_keys: tuple[str, ...]
    fixed_specs: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "knowns", tuple(str(item) for item in self.knowns))
        object.__setattr__(self, "unknowns", tuple(str(item) for item in self.unknowns))
        object.__setattr__(self, "expected_phase_keys", tuple(str(item) for item in self.expected_phase_keys))
        object.__setattr__(
            self,
            "fixed_specs",
            MappingProxyType({str(key): _freeze_fixed_spec_value(value) for key, value in self.fixed_specs.items()}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-like configured-problem payload."""

        return {
            "route": self.route,
            "selector_route": self.selector_route,
            "knowns": list(self.knowns),
            "unknowns": list(self.unknowns),
            "composition_role": self.composition_role,
            "activation_key": self.activation_key,
            "expected_phase_keys": list(self.expected_phase_keys),
            "fixed_specs": _json_like(dict(self.fixed_specs)),
        }


@dataclass(frozen=True, slots=True)
class EquilibriumStructure:
    """Immutable programmatic selector structure metadata."""

    route: str
    selector_route: str
    knowns: tuple[str, ...]
    unknowns: tuple[str, ...]
    composition_role: str
    activation_key: str
    residual_families: tuple[str, ...]
    hard_constraint_families: tuple[str, ...]
    expected_phase_keys: tuple[str, ...]
    dof: Mapping[str, Any]
    variable_model: str = ""
    density_backend: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "knowns", tuple(str(item) for item in self.knowns))
        object.__setattr__(self, "unknowns", tuple(str(item) for item in self.unknowns))
        object.__setattr__(self, "residual_families", tuple(str(item) for item in self.residual_families))
        object.__setattr__(
            self,
            "hard_constraint_families",
            tuple(str(item) for item in self.hard_constraint_families),
        )
        object.__setattr__(self, "expected_phase_keys", tuple(str(item) for item in self.expected_phase_keys))
        object.__setattr__(self, "dof", _freeze_metadata_value(self.dof))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-like structure payload."""

        return {
            "route": self.route,
            "selector_route": self.selector_route,
            "knowns": list(self.knowns),
            "unknowns": list(self.unknowns),
            "composition_role": self.composition_role,
            "activation_key": self.activation_key,
            "residual_families": list(self.residual_families),
            "hard_constraint_families": list(self.hard_constraint_families),
            "expected_phase_keys": list(self.expected_phase_keys),
            "dof": dict(self.dof),
            "variable_model": self.variable_model,
            "density_backend": self.density_backend,
        }


_EQUILIBRIUM_ROUTE_SPECS: dict[str, NativeSelectorRouteSpec] = EQUILIBRIUM_ROUTE_SPECS
_SINGLE_COMPONENT_VLE_NIST_TEMPERATURE_RANGES_K = {
    "methane": (100.0, 180.0),
    "ethane": (100.0, 280.0),
    "propane": (100.0, 340.0),
}
_ELECTROLYTE_LLE_VALIDATION_SPECIES = ("H2O", "Ethanol", "Butanol", "Na+", "Cl-")
_ELECTROLYTE_LLE_VALIDATION_CHARGES = np.asarray([0.0, 0.0, 0.0, 1.0, -1.0], dtype=float)
_ELECTROLYTE_CHARGE_TOLERANCE = 1.0e-8
_ELECTROLYTE_TPD_TOLERANCE = 1.0e-8
_ELECTROLYTE_CANDIDATE_MASS_BALANCE_TOLERANCE = 1.0e-8
_ELECTROLYTE_RESIDUAL_TOLERANCE = 1.0e-4
_ELECTROLYTE_PHASE_DISTANCE_TOLERANCE = 1.0e-8
_ELECTROLYTE_ACTIVE_BOUND_TOLERANCE = 1.0e-8
_ELECTROLYTE_LLE_VALIDATION_SCOPE = "source-backed Khudaida 2026 NaCl mixed-solvent LLE"
_GROSS_2002_PARAMETER_SOURCE_LABEL = "Gross/Sadowski 2002 Figure 8"
_GROSS_2002_ASSOCIATING_VLE_CASES: tuple[dict[str, Any], ...] = (
    {
        "source_label": "Gross/Sadowski 2002 Figure 2",
        "vectors": {
            "m": [1.5255, 2.2616],
            "s": [3.2300, 3.7574],
            "e": [188.90, 216.53],
            "e_assoc": [2899.5, 0.0],
            "vol_a": [0.035176, 0.0],
            "assoc_num": [2, 0],
        },
        "k_ij": [[0.0, 0.05], [0.05, 0.0]],
    },
    {
        "source_label": "Gross/Sadowski 2002 Figure 3",
        "vectors": {
            "m": [2.9997, 3.0799],
            "s": [3.2522, 3.7974],
            "e": [233.40, 287.35],
            "e_assoc": [2276.8, 0.0],
            "vol_a": [0.015268, 0.0],
            "assoc_num": [2, 0],
        },
        "k_ij": [[0.0, 0.023], [0.023, 0.0]],
    },
    {
        "source_label": "Gross/Sadowski 2002 Figure 4",
        "vectors": {
            "m": [3.6260, 2.4653],
            "s": [3.4508, 3.6478],
            "e": [247.28, 287.35],
            "e_assoc": [2252.1, 0.0],
            "vol_a": [0.010319, 0.0],
            "assoc_num": [2, 0],
        },
        "k_ij": [[0.0, 0.0135], [0.0135, 0.0]],
    },
    {
        "source_label": "Gross/Sadowski 2002 Figure 5",
        "vectors": {
            "m": [2.9997, 2.4653],
            "s": [3.2522, 3.6478],
            "e": [233.40, 287.35],
            "e_assoc": [2276.8, 0.0],
            "vol_a": [0.015268, 0.0],
            "assoc_num": [2, 0],
        },
        "k_ij": [[0.0, 0.020], [0.020, 0.0]],
    },
    {
        "source_label": "Gross/Sadowski 2002 Figure 5",
        "vectors": {
            "m": [3.0929, 2.4653],
            "s": [3.2085, 3.6478],
            "e": [208.42, 287.35],
            "e_assoc": [2253.9, 0.0],
            "vol_a": [0.024675, 0.0],
            "assoc_num": [2, 0],
        },
        "k_ij": [[0.0, 0.021], [0.021, 0.0]],
    },
    {
        "source_label": "Gross/Sadowski 2002 Figure 6",
        "vectors": {
            "m": [2.7515, 2.3316],
            "s": [3.6139, 3.7086],
            "e": [259.59, 222.88],
            "e_assoc": [2544.6, 0.0],
            "vol_a": [0.006692, 0.0],
            "assoc_num": [2, 0],
        },
        "k_ij": [[0.0, 0.015], [0.015, 0.0]],
    },
    {
        "source_label": "Gross/Sadowski 2002 Figure 7",
        "vectors": {
            "m": [2.3827, 2.3316],
            "s": [3.1771, 3.7086],
            "e": [198.24, 222.88],
            "e_assoc": [2653.4, 0.0],
            "vol_a": [0.032384, 0.0],
            "assoc_num": [2, 0],
        },
        "k_ij": [[0.0, 0.028], [0.028, 0.0]],
    },
    {
        "source_label": "Gross/Sadowski 2002 Figure 8",
        "vectors": {
            "m": [1.5255, 2.5303],
            "s": [3.2300, 3.8499],
            "e": [188.90, 278.11],
            "e_assoc": [2899.5, 0.0],
            "vol_a": [0.035176, 0.0],
            "assoc_num": [2, 0],
        },
        "k_ij": [[0.0, 0.051], [0.051, 0.0]],
    },
    {
        "source_label": "Gross/Sadowski 2002 Figure 9",
        "vectors": {
            "m": [1.5255, 4.3555],
            "s": [3.2300, 3.7145],
            "e": [188.90, 262.74],
            "e_assoc": [2899.5, 2754.8],
            "vol_a": [0.035176, 0.002197],
            "assoc_num": [2, 2],
        },
        "assoc_matrix": [0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0],
        "k_ij": [[0.0, 0.020], [0.020, 0.0]],
    },
)


def configure_equilibrium_problem(
    mixture: Any,
    *,
    route: str,
    T: Any = None,
    P: Any = None,
    x: Any = None,
    y: Any = None,
    z: Any = None,
) -> EquilibriumProblem:
    """Validate and freeze a constructor-configured equilibrium problem."""

    try:
        spec = _EQUILIBRIUM_ROUTE_SPECS[str(route)]
    except KeyError as exc:
        allowed = ", ".join(sorted(_EQUILIBRIUM_ROUTE_SPECS))
        raise InputError(f"Unknown equilibrium route '{route}'. Expected one of: {allowed}.") from exc

    provided_compositions = {key for key, value in {"x": x, "y": y, "z": z}.items() if value is not None}
    if spec.implicit_pure_composition:
        if provided_compositions:
            raise InputError(f"{spec.route_label} must not specify x, y, or z.")
        if int(mixture.ncomp) != 1:
            raise InputError(f"{spec.route_label} requires exactly one component.")
        composition = np.ones(1, dtype=float)
    else:
        composition_value = {"x": x, "y": y, "z": z}[spec.composition_key]
        if provided_compositions != {spec.composition_key}:
            expected = spec.composition_key
            provided = ", ".join(sorted(provided_compositions)) or "none"
            raise InputError(f"{spec.route_label} requires only composition '{expected}', got {provided}.")
        composition = _normalize_feed(
            composition_value,
            mixture.ncomp,
            EquilibriumSolverOptions().min_composition,
            spec.route_label,
        )
    if spec.requires_temperature and T is None:
        raise InputError(f"{spec.route_label} requires T.")
    if not spec.requires_temperature and T is not None:
        raise InputError(f"{spec.route_label} must not specify T.")
    if spec.requires_pressure and P is None:
        raise InputError(f"{spec.route_label} requires P.")
    if not spec.requires_pressure and P is not None:
        raise InputError(f"{spec.route_label} must not specify P.")
    _reject_ion_containing_mixture(mixture)
    _reject_associating_mixture(mixture, spec.route_label)
    temperature = _positive_scalar(T, "T", spec.route_label) if spec.requires_temperature else None
    pressure = _positive_scalar(P, "P", spec.route_label) if spec.requires_pressure else None
    if spec.route_label == "single_component_vle":
        if temperature is None:
            raise RuntimeError("single_component_vle validated without a temperature.")
        _require_single_component_vle_nist_scope(mixture, temperature)
    fixed_specs: dict[str, Any] = {spec.composition_key: composition}
    if temperature is not None:
        fixed_specs["T"] = temperature
    if pressure is not None:
        fixed_specs["P"] = pressure
    return EquilibriumProblem(
        route=spec.route_label,
        selector_route=spec.selector_route,
        knowns=spec.knowns,
        unknowns=spec.unknowns,
        composition_role=spec.composition_role,
        activation_key=spec.selector_family,
        expected_phase_keys=spec.phase_labels,
        fixed_specs=fixed_specs,
    )


# AlgID: bubble_dew_ipopt
def _solve_selector_route(
    mixture: Any,
    problem: EquilibriumProblem,
    *,
    options: EquilibriumSolverOptions | Mapping[str, Any] | None = None,
) -> EquilibriumResult:
    """Solve one configured selector-admitted neutral two-phase route through the shared core."""

    opts = _normalize_options(options)
    spec = _EQUILIBRIUM_ROUTE_SPECS[problem.route]
    return _native_selector_route(
        mixture,
        request=_selector_request_from_problem(problem),
        options=opts,
        public_route=problem.route,
        problem_kind=spec.problem_kind,
        route_label=spec.route_label,
        selector_family=spec.selector_family,
        composition_role=spec.composition_role,
        feed_composition=problem.fixed_specs.get("z"),
    )


def _run_associating_single_component_vle_validation(
    mixture: Any,
    *,
    temperature_K: Any,
    solver_options: EquilibriumSolverOptions | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the private exact-Hessian associating saturation validation route."""

    options = _normalize_options(solver_options)
    if options.hessian_mode == "limited-memory":
        raise InputError("Associating single-component VLE validation requires the exact Hessian route.")
    temperature = _positive_scalar(
        temperature_K,
        "temperature_K",
        "internal_associating_single_component_vle_validation",
    )
    core = extension_native_core()
    route = dict(core._native_associating_single_component_vle_validation_result(
        mixture._native,
        temperature,
        options.max_iterations,
        options.tolerance,
        _native_timeout_seconds(options),
        options.ipopt_iteration_history_limit,
        *selector_route_solver_tolerances(options),
        dict(options.continuation_state or {}),
        **_native_ipopt_control_kwargs(options),
    ))
    expected_scope = "internal_associating_single_component_vle_validation"
    if (
        route.get("validation_scope") != expected_scope
        or route.get("public_route_admission") != "closed"
        or route.get("production_exposed") is not False
    ):
        raise SolutionError("Native associating saturation validation returned invalid scope metadata.", dict(route))

    if route.get("accepted") is not True:
        raise_native_route_rejected(
            route,
            "Internal associating single-component VLE validation was rejected.",
        )
    association_receipt = route.get("association_derivative_receipt", {})
    if (
        route.get("route") != expected_scope
        or route.get("validation_route") != expected_scope
        or route.get("solver_route") != "single_component_vle_eos"
        or route.get("selector_dispatch_used") is not False
        or route.get("global_phase_set_certified") is not False
        or route.get("hessian_approximation") != "exact"
        or route.get("exact_hessian_available") is not True
        or association_receipt.get("derivative_mode") != "cppad_implicit_association"
        or association_receipt.get("exact_site_fraction_jacobian_available") is not True
        or association_receipt.get("exact_site_fraction_hessian_available") is not True
    ):
        raise SolutionError("Associating saturation validation returned incomplete derivative evidence.", route)
    return route


def _selector_request_from_problem(problem: EquilibriumProblem) -> dict[str, Any]:
    composition_key = _EQUILIBRIUM_ROUTE_SPECS[problem.route].composition_key
    return selector_request_payload(
        route=problem.selector_route,
        temperature=problem.fixed_specs.get("T"),
        pressure=problem.fixed_specs.get("P"),
        composition=np.asarray(problem.fixed_specs[composition_key], dtype=float),
        composition_role=problem.composition_role,
    )


def equilibrium_structure(mixture: Any, problem: EquilibriumProblem) -> EquilibriumStructure:
    """Return immutable native selector structure metadata for a configured problem."""

    _core = extension_native_core()

    request = _selector_request_from_problem(problem)
    contract = _core._native_equilibrium_selector_contract(mixture._native, request)
    activation = contract["activation"]
    return EquilibriumStructure(
        route=problem.route,
        selector_route=problem.selector_route,
        knowns=problem.knowns,
        unknowns=problem.unknowns,
        composition_role=problem.composition_role,
        activation_key=problem.activation_key,
        residual_families=tuple(str(item) for item in activation["residual_families"]),
        hard_constraint_families=tuple(str(item) for item in activation["constraint_families"]),
        expected_phase_keys=tuple(str(item) for item in contract.get("phase_labels", problem.expected_phase_keys)),
        dof={
            "available": False,
            "reason": "not_generally_owned_by_route_metadata",
        },
        variable_model=str(activation["variable_model"]),
        density_backend=str(activation["density_backend"]),
    )


def _native_selector_route(
    mixture: Any,
    *,
    request: Mapping[str, Any],
    options: EquilibriumSolverOptions,
    public_route: str,
    problem_kind: str,
    route_label: str,
    selector_family: str,
    composition_role: str,
    feed_composition: Any = None,
) -> EquilibriumResult:
    _core = extension_native_core()

    route = _core._native_equilibrium_selector_route_result(
        mixture._native,
        dict(request),
        options.max_iterations,
        options.tolerance,
        _native_timeout_seconds(options),
        *_native_ipopt_option_args(options),
        *selector_route_solver_tolerances(options),
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
    return _accepted_native_selector_two_phase_result(
        T=temperature,
        P=pressure,
        route=route,
        public_route=public_route,
        problem_kind=problem_kind,
        route_label=route_label,
        selector_family=selector_family,
        composition_role=composition_role,
        feed_composition=feed_composition,
    )


def _accepted_native_selector_two_phase_result(
    *,
    T: float,
    P: float,
    route: Mapping[str, Any],
    public_route: str,
    problem_kind: str,
    route_label: str,
    selector_family: str,
    composition_role: str,
    feed_composition: Any = None,
) -> EquilibriumResult:
    return native_selector_route_to_result(
        route,
        temperature=T,
        pressure=P,
        problem_kind=problem_kind,
        public_route=public_route,
        route_label=route_label,
        selector_family=selector_family,
        composition_role=composition_role,
        feed_composition=feed_composition,
    )


def _run_electrolyte_lle_validation(
    mixture: Any,
    *,
    T: Any,
    P: Any,
    z: Any,
    solver_options: EquilibriumSolverOptions | Mapping[str, Any] | None = None,
) -> EquilibriumResult:
    """Run the source-backed electrolyte LLE component diagnostic."""

    _core = extension_native_core()

    activation = _internal_activation_from_native(_core, "electrolyte_lle")
    options = _normalize_options(solver_options)
    temperature = _positive_scalar(T, "T", "internal electrolyte LLE validation")
    pressure = _positive_scalar(P, "P", "internal electrolyte LLE validation")
    feed = _normalize_feed(
        z,
        mixture.ncomp,
        options.min_composition,
        "internal electrolyte LLE validation",
    )
    _require_source_backed_electrolyte_lle_validation_scope(mixture, feed)
    route_mixture = _nonassociating_electrolyte_validation_mixture(mixture)
    certification = _core._native_electrolyte_postsolve_certification(
        route_mixture._native,
        temperature,
        pressure,
        feed.tolist(),
        _ELECTROLYTE_LLE_VALIDATION_CHARGES.tolist(),
        list(_ELECTROLYTE_LLE_VALIDATION_SPECIES),
        [0, 0],
        _ELECTROLYTE_CHARGE_TOLERANCE,
        _ELECTROLYTE_TPD_TOLERANCE,
        _ELECTROLYTE_CANDIDATE_MASS_BALANCE_TOLERANCE,
        _ELECTROLYTE_RESIDUAL_TOLERANCE,
        _ELECTROLYTE_PHASE_DISTANCE_TOLERANCE,
        _ELECTROLYTE_ACTIVE_BOUND_TOLERANCE,
    )
    return _electrolyte_lle_validation_result(
        T=temperature,
        P=pressure,
        feed=feed,
        certification=certification,
        activation=activation,
        options=options,
    )


def _electrolyte_lle_validation_result(
    *,
    T: float,
    P: float,
    feed: np.ndarray,
    certification: Mapping[str, Any],
    activation: Mapping[str, Any],
    options: EquilibriumSolverOptions,
) -> EquilibriumResult:
    activation_payload = _validate_internal_activation(
        activation,
        family_key="electrolyte_lle",
        diagnostics=certification,
    )
    certification_payload = dict(certification)
    if certification_payload.get("status") != "complete":
        raise SolutionError("Native electrolyte LLE postsolve certification did not complete.", certification_payload)

    stage_iii = certification_payload.get("electrolyte_stage_iii_refinement", {})
    if not isinstance(stage_iii, Mapping) or stage_iii.get("status") != "complete":
        raise SolutionError("Native electrolyte LLE Stage III evidence is not complete.", certification_payload)
    native_route = stage_iii.get("native_stage_iii_route_result", {})
    if not isinstance(native_route, Mapping) or native_route.get("accepted") is not True:
        raise SolutionError("Native electrolyte LLE route evidence was not accepted.", certification_payload)

    physical_evidence = native_route.get("physical_evidence", {})
    phase_payloads = physical_evidence.get("phases", ()) if isinstance(physical_evidence, Mapping) else ()
    if not isinstance(phase_payloads, Sequence) or isinstance(phase_payloads, (str, bytes)) or len(phase_payloads) != 2:
        raise SolutionError(
            "Native electrolyte LLE certification did not return two phase payloads.", certification_payload
        )

    labels = ("liquid1", "liquid2")
    phases: list[EquilibriumPhase] = []
    for index, payload in enumerate(phase_payloads):
        if not isinstance(payload, Mapping):
            raise SolutionError("Native electrolyte LLE phase payload is invalid.", certification_payload)
        phases.append(
            EquilibriumPhase(
                label=labels[index],
                composition=payload["composition"],
                density=float(payload["density"]),
                temperature=T,
                pressure=P,
                phase_fraction=float(payload["phase_fraction"]),
                ln_fugacity_coefficient=payload.get("ln_fugacity_coefficients"),
                diagnostics={
                    "native_label": payload.get("label", ""),
                    "role": payload.get("role", ""),
                    "phase_kind": payload.get("phase_kind", 0),
                    "amount_total": payload.get("amount_total"),
                    "volume": payload.get("volume"),
                },
            )
        )

    derivatives = stage_iii.get("derivative_receipts", {})
    if not isinstance(derivatives, Mapping):
        derivatives = {}
    route_hessian = str(derivatives.get("route_hessian_approximation", native_route.get("hessian_approximation", "")))
    diagnostics: dict[str, Any] = {
        "route_status": "internal_validation_accepted",
        "solver_accepted": True,
        "route_accepted": True,
        "solver_status": native_route.get("solver_status", ""),
        "application_status": native_route.get("application_status", ""),
        "postsolve_accepted": True,
        "postsolve_certification": {
            "accepted": True,
            "status": certification_payload.get("status"),
            "native_binding": certification_payload.get("native_binding"),
            "algorithm_scope": certification_payload.get("algorithm_scope"),
        },
        "validation_scope": {
            "status": "internal_component_diagnostic",
            "scope": _ELECTROLYTE_LLE_VALIDATION_SCOPE,
            "association_state": "disabled_for_pre_association_electrolyte_gate",
            "selector_family": "electrolyte_lle",
            "source_fixture": "data/reference/equilibrium_benchmarks/electrolyte_lle/water_ethanol_isobutanol_nacl",
            "parameter_bundle": "analyses/paper_validation/2026_khudaida/parameters",
        },
        "activation": activation_payload,
        "phase_labels": labels,
        "phase_roles": ("liquid", "liquid"),
        "charge_balance": certification_payload.get("charge_balance", {}),
        "transfer_residuals": certification_payload.get("transfer_residuals", {}),
        "pressure_consistency": certification_payload.get("pressure_consistency", {}),
        "phase_set": certification_payload.get("phase_set", {}),
        "domain_margins": certification_payload.get("domain_margins", {}),
        "explicit_ion_reconstruction": certification_payload.get("explicit_ion_reconstruction", {}),
        "projected_residual_route": stage_iii.get("projected_residual_route", {}),
        "electrolyte_stage_iii_refinement": stage_iii,
        "held2_phase_discovery": stage_iii.get("held2_phase_discovery", {}),
        "derivative_receipts": derivatives,
        "hessian_approximation": str(derivatives.get("hessian_approximation", "exact")),
        "exact_hessian_available": bool(derivatives.get("exact_reduced_hessian_available", False)),
        "jacobian_approximation": str(derivatives.get("jacobian_approximation", "exact")),
        "exact_jacobian_available": bool(derivatives.get("exact_reduced_jacobian_available", False)),
        "route_hessian_approximation": route_hessian,
        "route_hessian_backend": derivatives.get("route_hessian_backend"),
        "backend": native_route.get("backend", "ipopt"),
        "option_profile": native_route.get("option_profile", "electrolyte_stage_iii_refinement"),
        "max_iterations": options.max_iterations,
        "tolerance": options.tolerance,
        "ipopt_iteration_history_limit": options.ipopt_iteration_history_limit,
        "iteration_count": native_route.get("iteration_count", 0),
        "iteration_history_size": native_route.get("iteration_history_size", 0),
        "iteration_history": native_route.get("iteration_history", ()),
        "physical_evidence": physical_evidence,
    }
    if diagnostics["hessian_approximation"] != "exact" or diagnostics["exact_hessian_available"] is not True:
        raise SolutionError("Native electrolyte LLE route did not return exact reduced Hessian evidence.", diagnostics)

    return EquilibriumResult(
        backend=str(native_route.get("backend", "ipopt")),
        problem_kind="internal_electrolyte_lle_validation",
        phases=tuple(phases),
        stable=True,
        split_detected=True,
        diagnostics=diagnostics,
        route="internal_electrolyte_lle_validation",
        selector_route="electrolyte_lle",
        composition_role="feed_composition",
        feed_composition=feed,
    )


def _normalize_options(options: EquilibriumSolverOptions | Mapping[str, Any] | None) -> EquilibriumSolverOptions:
    if options is None:
        return EquilibriumSolverOptions()
    if isinstance(options, Mapping):
        raw = dict(options)
        allowed = {
            "max_iterations",
            "tolerance",
            "min_composition",
            "timeout_seconds",
            "hessian_mode",
            "ipopt_iteration_history_limit",
            "ipopt_print_level",
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
        options = EquilibriumSolverOptions(**raw)
    if not isinstance(options, EquilibriumSolverOptions):
        raise InputError("solver_options must be an EquilibriumSolverOptions instance or mapping.")
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
    if isinstance(options.ipopt_print_level, bool) or not isinstance(options.ipopt_print_level, Integral):
        raise InputError("options.ipopt_print_level must be an integer greater than or equal to zero.")
    ipopt_print_level = int(options.ipopt_print_level)
    if ipopt_print_level < 0:
        raise InputError("options.ipopt_print_level must be an integer greater than or equal to zero.")
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
    return EquilibriumSolverOptions(
        max_iterations=max_iterations,
        tolerance=tolerance,
        min_composition=min_composition,
        timeout_seconds=timeout_seconds,
        hessian_mode=hessian_mode,  # type: ignore[arg-type]
        ipopt_iteration_history_limit=ipopt_iteration_history_limit,
        ipopt_print_level=ipopt_print_level,
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


def _native_timeout_seconds(options: EquilibriumSolverOptions) -> float:
    return 0.0 if options.timeout_seconds is None else float(options.timeout_seconds)


def _native_ipopt_optional_tolerance(value: float | None) -> float:
    return 0.0 if value is None else float(value)


def _native_ipopt_option_args(options: EquilibriumSolverOptions) -> tuple[str, int]:
    return options.hessian_mode, int(options.ipopt_iteration_history_limit)


def _native_ipopt_control_kwargs(options: EquilibriumSolverOptions) -> dict[str, Any]:
    return {
        "linear_solver": str(options.ipopt_linear_solver),
        "print_level": int(options.ipopt_print_level),
        "acceptable_tolerance": _native_ipopt_optional_tolerance(options.ipopt_acceptable_tolerance),
        "constraint_violation_tolerance": _native_ipopt_optional_tolerance(
            options.ipopt_constraint_violation_tolerance
        ),
        "dual_infeasibility_tolerance": _native_ipopt_optional_tolerance(options.ipopt_dual_infeasibility_tolerance),
        "complementarity_tolerance": _native_ipopt_optional_tolerance(options.ipopt_complementarity_tolerance),
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


def _association_active(parameters: Mapping[str, Any]) -> bool:
    assoc_num = np.asarray(parameters.get("assoc_num", []), dtype=int).flatten()
    assoc_matrix = np.asarray(parameters.get("assoc_matrix", []), dtype=float).flatten()
    e_assoc = np.asarray(parameters.get("e_assoc", []), dtype=float).flatten()
    vol_a = np.asarray(parameters.get("vol_a", []), dtype=float).flatten()
    return (
        (assoc_num.size > 0 and np.any(assoc_num > 0))
        or (assoc_matrix.size > 0 and np.any(np.abs(assoc_matrix) > 0.0))
        or (e_assoc.size > 0 and np.any(np.abs(e_assoc) > 0.0))
        or (vol_a.size > 0 and np.any(np.abs(vol_a) > 0.0))
    )


def _require_source_backed_electrolyte_lle_validation_scope(mixture: Any, feed: np.ndarray) -> None:
    parameters = mixture.parameters
    species = tuple(str(item) for item in getattr(mixture, "species", ()))
    if species != _ELECTROLYTE_LLE_VALIDATION_SPECIES:
        raise InputError(
            "Internal electrolyte LLE validation is limited to the source-backed Khudaida 2026 "
            "H2O/Ethanol/Butanol/Na+/Cl- mixed-solvent LLE fixture."
        )
    charges = np.asarray(parameters.get("z", []), dtype=float).flatten()
    if charges.shape != _ELECTROLYTE_LLE_VALIDATION_CHARGES.shape or not np.allclose(
        charges,
        _ELECTROLYTE_LLE_VALIDATION_CHARGES,
        rtol=0.0,
        atol=1.0e-12,
    ):
        raise InputError("electrolyte_lle requires the certified explicit-ion Na+/Cl- charge basis.")
    if abs(float(feed @ charges)) > _ELECTROLYTE_CHARGE_TOLERANCE:
        raise InputError("electrolyte_lle requires a charge-neutral explicit-ion feed.")
    source_label = str(parameters.get("_parameter_source_label", "")).replace("\\", "/").lower()
    if not source_label.endswith("analyses/paper_validation/2026_khudaida/parameters"):
        raise InputError("electrolyte_lle requires the certified Khudaida 2026 parameter bundle.")
    if parameters.get("_binary_interaction_provenance_status") != "explicit_binary_records":
        raise InputError("electrolyte_lle requires explicit source-bundle binary interaction records.")
    elec_model = parameters.get("elec_model", {})
    if not isinstance(elec_model, Mapping):
        raise InputError("electrolyte_lle requires the certified electrolyte model options.")
    born_model = elec_model.get("born_model", {})
    if not isinstance(born_model, Mapping):
        raise InputError("electrolyte_lle requires the certified Born model options.")
    if elec_model.get("include_born_model") is not True:
        raise InputError("electrolyte_lle requires the Born contribution.")
    if born_model.get("solvation_shell_model") is not True or born_model.get("dielectric_saturation") is not True:
        raise InputError("electrolyte_lle requires the certified Born SSM/DS formulation.")


def _nonassociating_electrolyte_validation_mixture(mixture: Any) -> Any:
    from epcsaft.state.native_adapter import ePCSAFTMixture

    params = dict(mixture.parameters)
    ncomp = int(mixture.ncomp)
    params["assoc_scheme"] = [None] * ncomp
    params["e_assoc"] = np.zeros(ncomp, dtype=float)
    params["vol_a"] = np.zeros(ncomp, dtype=float)
    params.pop("assoc_num", None)
    params.pop("assoc_matrix", None)
    return ePCSAFTMixture.from_params(params, species=mixture.species)


def _reject_ion_containing_mixture(mixture: Any) -> None:
    charges = np.asarray(mixture.parameters.get("z", []), dtype=float).flatten()
    if charges.size and np.any(np.abs(charges) > 1.0e-12):
        raise InputError("Production equilibrium selector routes support only neutral mixtures.")


def _reject_associating_mixture(mixture: Any, route_label: str = "neutral_lle") -> None:
    parameters = mixture.parameters
    if not _association_active(parameters):
        return
    if route_label == "lle" and (
        _has_gross_2002_associating_lle_proof(parameters) or _has_gross_2002_figure10_associating_lle_proof(parameters)
    ):
        return
    if route_label in {"bubble_pressure", "dew_pressure"} and _has_gross_2002_associating_vle_proof(parameters):
        return
    if route_label == "lle":
        raise InputError(
            "Production lle associating GFPE admission requires source-backed Gross/Sadowski 2002 "
            "neutral two-phase LLE exact-Hessian proof."
        )
    if route_label == "single_component_vle":
        raise InputError(
            "single_component_vle requires a nonassociating pure-component input."
        )
    raise InputError(
        f"Production {route_label} associating GFPE admission only admits the source-backed Gross/Sadowski 2002 "
        "Figures 2-9 neutral binary VLE proofs; this route remains closed for associating inputs."
    )


def _require_single_component_vle_nist_scope(mixture: Any, temperature: float) -> None:
    species = tuple(str(label).strip().lower() for label in mixture.species)
    if len(species) != 1 or species[0] not in _SINGLE_COMPONENT_VLE_NIST_TEMPERATURE_RANGES_K:
        raise InputError(
            "single_component_vle requires NIST-backed methane, ethane, or propane."
        )
    lower, upper = _SINGLE_COMPONENT_VLE_NIST_TEMPERATURE_RANGES_K[species[0]]
    if not lower <= temperature <= upper:
        raise InputError(
            f"single_component_vle temperature must be within the retained NIST temperature range "
            f"for {species[0]}: {lower:g} K to {upper:g} K."
        )


def _has_gross_2002_associating_lle_proof(parameters: Mapping[str, Any]) -> bool:
    if parameters.get("_parameter_source_label") != _GROSS_2002_PARAMETER_SOURCE_LABEL:
        return False
    if parameters.get("_parameter_provenance_status") != "source_backed_parameter_metadata":
        return False
    if parameters.get("_binary_interaction_provenance_status") != "explicit_binary_records":
        return False
    fields = {str(field) for field in parameters.get("_parameter_provenance_fields", ())}
    if {"source", "paper", "table", "figure", "source_path"} - fields:
        return False
    expected_vectors = {
        "m": [1.5255, 2.5303],
        "s": [3.2300, 3.8499],
        "e": [188.90, 278.11],
        "e_assoc": [2899.5, 0.0],
        "vol_a": [0.035176, 0.0],
        "assoc_num": [2, 0],
    }
    for key, expected in expected_vectors.items():
        actual = np.asarray(parameters.get(key, []), dtype=float).flatten()
        if actual.shape != (len(expected),) or not np.allclose(actual, np.asarray(expected), rtol=0.0, atol=1.0e-10):
            return False
    assoc_matrix = np.asarray(parameters.get("assoc_matrix", []), dtype=float).flatten()
    if assoc_matrix.shape != (4,) or not np.allclose(assoc_matrix, [0.0, 1.0, 1.0, 0.0], rtol=0.0, atol=1.0e-12):
        return False
    k_ij = np.asarray(parameters.get("k_ij", []), dtype=float)
    if k_ij.shape != (2, 2) or not np.allclose(k_ij, [[0.0, 0.051], [0.051, 0.0]], rtol=0.0, atol=1.0e-12):
        return False
    z = np.asarray(parameters.get("z", []), dtype=float).flatten()
    return z.size == 0 or np.allclose(z, 0.0, rtol=0.0, atol=1.0e-12)


def _has_gross_2002_figure10_associating_lle_proof(parameters: Mapping[str, Any]) -> bool:
    if parameters.get("_parameter_source_label") != "Gross/Sadowski 2002 Figure 10":
        return False
    if parameters.get("_parameter_provenance_status") != "source_backed_parameter_metadata":
        return False
    if parameters.get("_binary_interaction_provenance_status") != "explicit_binary_records":
        return False
    fields = {str(field) for field in parameters.get("_parameter_provenance_fields", ())}
    if {"source", "paper", "table", "figure", "source_path"} - fields:
        return False
    expected_vectors = {
        "m": [1.0656, 3.6260],
        "s": [3.0007, 3.4508],
        "e": [366.51, 247.28],
        "e_assoc": [2500.7, 2252.1],
        "vol_a": [0.034868, 0.010319],
        "assoc_num": [2, 2],
    }
    for key, expected in expected_vectors.items():
        actual = np.asarray(parameters.get(key, []), dtype=float).flatten()
        if actual.shape != (len(expected),) or not np.allclose(actual, np.asarray(expected), rtol=0.0, atol=1.0e-10):
            return False
    assoc_matrix = np.asarray(parameters.get("assoc_matrix", []), dtype=float).flatten()
    if assoc_matrix.shape != (16,) or not np.allclose(
        assoc_matrix,
        [0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0],
        rtol=0.0,
        atol=1.0e-12,
    ):
        return False
    k_ij = np.asarray(parameters.get("k_ij", []), dtype=float)
    if k_ij.shape != (2, 2) or not np.allclose(k_ij, [[0.0, 0.016], [0.016, 0.0]], rtol=0.0, atol=1.0e-12):
        return False
    z = np.asarray(parameters.get("z", []), dtype=float).flatten()
    f_solv = np.asarray(parameters.get("f_solv", []), dtype=float).flatten()
    f_solv_ok = (
        f_solv.size == 0
        or np.allclose(f_solv, 0.0, rtol=0.0, atol=1.0e-12)
        or np.allclose(f_solv, 1.0, rtol=0.0, atol=1.0e-12)
    )
    return (z.size == 0 or np.allclose(z, 0.0, rtol=0.0, atol=1.0e-12)) and f_solv_ok


def _has_gross_2002_associating_vle_proof(parameters: Mapping[str, Any]) -> bool:
    source_label = parameters.get("_parameter_source_label")
    matching_cases = [case for case in _GROSS_2002_ASSOCIATING_VLE_CASES if case["source_label"] == source_label]
    if not matching_cases:
        return False
    if parameters.get("_parameter_provenance_status") != "source_backed_parameter_metadata":
        return False
    if parameters.get("_binary_interaction_provenance_status") != "explicit_binary_records":
        return False
    fields = {str(field) for field in parameters.get("_parameter_provenance_fields", ())}
    if {"source", "paper", "table", "figure", "source_path"} - fields:
        return False
    z = np.asarray(parameters.get("z", []), dtype=float).flatten()
    if z.size and not np.allclose(z, 0.0, rtol=0.0, atol=1.0e-12):
        return False
    k_ij = np.asarray(parameters.get("k_ij", []), dtype=float)
    for case in matching_cases:
        expected_vectors = case["vectors"]
        expected_assoc_matrix = np.asarray(case.get("assoc_matrix", [0.0, 1.0, 1.0, 0.0]), dtype=float)
        assoc_matrix = np.asarray(parameters.get("assoc_matrix", []), dtype=float).flatten()
        if assoc_matrix.shape != expected_assoc_matrix.shape or not np.allclose(
            assoc_matrix, expected_assoc_matrix, rtol=0.0, atol=1.0e-12
        ):
            continue
        if any(
            (actual := np.asarray(parameters.get(key, []), dtype=float).flatten()).shape != (len(expected),)
            or not np.allclose(actual, np.asarray(expected), rtol=0.0, atol=1.0e-10)
            for key, expected in expected_vectors.items()
        ):
            continue
        if k_ij.shape == (2, 2) and np.allclose(k_ij, np.asarray(case["k_ij"], dtype=float), rtol=0.0, atol=1.0e-12):
            return True
    return False


def _json_like(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Mapping):
        return {str(key): _json_like(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_like(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value
