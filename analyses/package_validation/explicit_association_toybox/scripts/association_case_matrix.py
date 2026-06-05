from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .association_models import AssociationSystem
from .topology_reductions import topology_system


@dataclass(frozen=True)
class AssociationEvidenceCase:
    case_id: str
    topology_id: str
    component_family: str
    mixture_family: str
    system: AssociationSystem | None
    composition: np.ndarray
    delta_matrix: np.ndarray
    density_grid: tuple[float, ...]
    temperature_grid: tuple[float, ...]
    strength_scale: float
    source_status: str
    note: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "composition", _vector("composition", self.composition))
        object.__setattr__(self, "delta_matrix", np.asarray(self.delta_matrix, dtype=float))
        if not self.case_id:
            raise ValueError("case_id is required.")
        if not self.topology_id:
            raise ValueError("topology_id is required.")
        if self.system is None:
            if self.delta_matrix.shape != (0, 0):
                raise ValueError("nonassociating cases must use an empty delta matrix.")
            if self.composition.ndim != 1 or self.composition.size < 1:
                raise ValueError("nonassociating cases require a composition vector.")
        else:
            if self.composition.shape != (self.system.component_count,):
                raise ValueError("composition must match the association system component count.")
            if self.delta_matrix.shape != (self.system.site_count, self.system.site_count):
                raise ValueError("delta_matrix must match the association system site count.")
            if np.any(self.delta_matrix < 0.0):
                raise ValueError("delta_matrix must be nonnegative.")
        if not np.isclose(float(np.sum(self.composition)), 1.0):
            raise ValueError("composition must sum to one.")
        if np.any(self.composition < 0.0):
            raise ValueError("composition must be nonnegative.")
        if self.strength_scale < 0.0 or not np.isfinite(self.strength_scale):
            raise ValueError("strength_scale must be finite and nonnegative.")
        _positive_grid("density_grid", self.density_grid)
        _positive_grid("temperature_grid", self.temperature_grid)

    @property
    def site_count(self) -> int:
        return 0 if self.system is None else self.system.site_count

    @property
    def component_count(self) -> int:
        return int(self.composition.size)

    def scaled_delta(self, strength_scale: float) -> np.ndarray:
        if self.strength_scale == 0.0:
            return np.zeros_like(self.delta_matrix)
        if strength_scale < 0.0 or not np.isfinite(strength_scale):
            raise ValueError("strength_scale must be finite and nonnegative.")
        return self.delta_matrix * (float(strength_scale) / self.strength_scale)

    def strength_matrix_text(self) -> str:
        if self.delta_matrix.size == 0:
            return ""
        return ";".join(
            ",".join(f"{float(value):.12g}" for value in row)
            for row in self.delta_matrix
        )

    def composition_text(self) -> str:
        return ";".join(f"{float(value):.12g}" for value in self.composition)


def association_evidence_cases() -> tuple[AssociationEvidenceCase, ...]:
    return (
        _case(
            case_id="pure_nonassociating_control",
            topology_id="none",
            component_family="synthetic_nonassociating",
            mixture_family="pure_component",
            system=None,
            composition=[1.0],
            delta=[],
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=0.0,
            source_status="synthetic_control",
            note="No association sites; used to prove zero-association rows stay explicit.",
        ),
        _case(
            case_id="pure_one_site_self",
            topology_id="1",
            component_family="synthetic_one_site",
            mixture_family="pure_component",
            system=topology_system("1"),
            composition=[1.0],
            delta=[[3.0]],
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=3.0,
            source_status="synthetic_topology",
            note="One equivalent self-associating site from the topology algebra.",
        ),
        _case(
            case_id="pure_2b_self",
            topology_id="2B",
            component_family="synthetic_2b_self",
            mixture_family="pure_component",
            system=topology_system("2B"),
            composition=[1.0],
            delta=_full_delta(topology_system("2B"), 8.0),
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=8.0,
            source_status="synthetic_topology",
            note="Two-site donor-acceptor self-association.",
        ),
        _case(
            case_id="pure_3b_labeled",
            topology_id="3B",
            component_family="synthetic_3b",
            mixture_family="pure_component",
            system=topology_system("3B"),
            composition=[1.0],
            delta=_full_delta(topology_system("3B"), 5.0),
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=5.0,
            source_status="synthetic_topology",
            note="3B topology stress case; not a compound-specific validation row.",
        ),
        _case(
            case_id="pure_4c_labeled",
            topology_id="4C",
            component_family="synthetic_4c",
            mixture_family="pure_component",
            system=topology_system("4C"),
            composition=[1.0],
            delta=_full_delta(topology_system("4C"), 4.0),
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=4.0,
            source_status="synthetic_topology",
            note="4C topology stress case; not a compound-specific validation row.",
        ),
        _case(
            case_id="inert_plus_associating_binary",
            topology_id="2B+none",
            component_family="synthetic_2b_plus_inert",
            mixture_family="binary_inert_associating",
            system=_binary_system(
                site_component_index=[0, 0],
                site_kind=("D", "A"),
                active_pairs=((0, 1), (1, 0)),
            ),
            composition=[0.4, 0.6],
            delta=[[0.0, 7.0], [7.0, 0.0]],
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=7.0,
            source_status="synthetic_mixture",
            note="Associating component diluted by an inert component.",
        ),
        _case(
            case_id="two_self_associating_binary",
            topology_id="2B+2B",
            component_family="synthetic_two_self_associating",
            mixture_family="binary_self_associating",
            system=_binary_system(
                site_component_index=[0, 0, 1, 1],
                site_kind=("D", "A", "D", "A"),
                active_pairs=((0, 1), (1, 0), (2, 3), (3, 2)),
            ),
            composition=[0.45, 0.55],
            delta=_delta_from_pairs(4, ((0, 1, 7.0), (1, 0, 7.0), (2, 3, 5.0), (3, 2, 5.0))),
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=6.0,
            source_status="synthetic_mixture",
            note="Two self-associating components without cross-association pairs.",
        ),
        _case(
            case_id="cross_associating_binary",
            topology_id="D+A",
            component_family="synthetic_cross_association",
            mixture_family="binary_cross_associating",
            system=_binary_system(
                site_component_index=[0, 1],
                site_kind=("D", "A"),
                active_pairs=((0, 1), (1, 0)),
            ),
            composition=[0.35, 0.65],
            delta=[[0.0, 9.0], [9.0, 0.0]],
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=9.0,
            source_status="synthetic_mixture",
            note="Asymmetric composition cross-association case.",
        ),
        _case(
            case_id="asymmetric_donor_acceptor_binary",
            topology_id="DD+A",
            component_family="synthetic_asymmetric_donor_acceptor",
            mixture_family="binary_asymmetric_donor_acceptor",
            system=_binary_system(
                site_component_index=[0, 0, 1],
                site_kind=("D", "D", "A"),
                active_pairs=((0, 2), (2, 0), (1, 2), (2, 1)),
            ),
            composition=[0.7, 0.3],
            delta=_delta_from_pairs(3, ((0, 2, 10.0), (2, 0, 7.0), (1, 2, 4.0), (2, 1, 3.0))),
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=6.0,
            source_status="synthetic_mixture",
            note="Unequal donor/acceptor matrix for CppAD-shaped branch and sparsity stress.",
        ),
        _case(
            case_id="water_like_3b_topology",
            topology_id="water-like-3B",
            component_family="synthetic_water_like",
            mixture_family="pure_component_topology_fork",
            system=topology_system("3B"),
            composition=[1.0],
            delta=_full_delta(topology_system("3B"), 6.0),
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=6.0,
            source_status="synthetic_topology_fork",
            note="Water-like 3B topology label for contrast only.",
        ),
        _case(
            case_id="water_like_4c_topology",
            topology_id="water-like-4C",
            component_family="synthetic_water_like",
            mixture_family="pure_component_topology_fork",
            system=topology_system("4C"),
            composition=[1.0],
            delta=_full_delta(topology_system("4C"), 5.0),
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=5.0,
            source_status="synthetic_topology_fork",
            note="Water-like 4C topology label for contrast only.",
        ),
        _case(
            case_id="mixed_2b_3b_binary",
            topology_id="2B+3B",
            component_family="synthetic_mixed_2b_3b",
            mixture_family="binary_mixed_topology",
            system=_binary_system(
                site_component_index=[0, 0, 1, 1, 1],
                site_kind=("D", "A", "A", "A", "D"),
                active_pairs=(
                    (0, 1),
                    (1, 0),
                    (2, 4),
                    (4, 2),
                    (3, 4),
                    (4, 3),
                    (0, 2),
                    (2, 0),
                    (0, 3),
                    (3, 0),
                    (4, 1),
                    (1, 4),
                ),
            ),
            composition=[0.5, 0.5],
            delta=_delta_from_pairs(
                5,
                (
                    (0, 1, 4.0),
                    (1, 0, 4.0),
                    (2, 4, 3.0),
                    (4, 2, 3.0),
                    (3, 4, 3.0),
                    (4, 3, 3.0),
                    (0, 2, 2.5),
                    (2, 0, 2.0),
                    (0, 3, 2.5),
                    (3, 0, 2.0),
                    (4, 1, 2.0),
                    (1, 4, 2.0),
                ),
            ),
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=3.0,
            source_status="synthetic_mixed_topology",
            note="Synthetic 2B+3B binary for mixed-topology derivative stress.",
        ),
        _case(
            case_id="mixed_2b_4c_binary",
            topology_id="2B+4C",
            component_family="synthetic_mixed_2b_4c",
            mixture_family="binary_mixed_topology",
            system=_binary_system(
                site_component_index=[0, 0, 1, 1, 1, 1],
                site_kind=("D", "A", "A", "A", "D", "D"),
                active_pairs=(
                    (0, 1),
                    (1, 0),
                    (2, 4),
                    (4, 2),
                    (2, 5),
                    (5, 2),
                    (3, 4),
                    (4, 3),
                    (3, 5),
                    (5, 3),
                    (0, 2),
                    (2, 0),
                    (0, 3),
                    (3, 0),
                    (4, 1),
                    (1, 4),
                    (5, 1),
                    (1, 5),
                ),
            ),
            composition=[0.45, 0.55],
            delta=_delta_from_pairs(
                6,
                (
                    (0, 1, 4.0),
                    (1, 0, 4.0),
                    (2, 4, 3.0),
                    (4, 2, 3.0),
                    (2, 5, 3.0),
                    (5, 2, 3.0),
                    (3, 4, 3.0),
                    (4, 3, 3.0),
                    (3, 5, 3.0),
                    (5, 3, 3.0),
                    (0, 2, 2.5),
                    (2, 0, 2.0),
                    (0, 3, 2.5),
                    (3, 0, 2.0),
                    (4, 1, 2.0),
                    (1, 4, 2.0),
                    (5, 1, 2.0),
                    (1, 5, 2.0),
                ),
            ),
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=3.0,
            source_status="synthetic_mixed_topology",
            note="Synthetic 2B+4C binary for mixed-topology derivative stress.",
        ),
        _case(
            case_id="mixed_4c_4c_binary",
            topology_id="4C+4C",
            component_family="synthetic_mixed_4c_4c",
            mixture_family="binary_mixed_topology",
            system=_mixed_4c_4c_system(),
            composition=[0.5, 0.5],
            delta=_full_delta(
                _mixed_4c_4c_system(),
                2.5,
            ),
            density_grid=(0.02, 0.05, 0.08),
            temperature_grid=(300.0, 320.0, 340.0),
            strength_scale=2.5,
            source_status="synthetic_mixed_topology",
            note="Synthetic 4C+4C binary with cross-class site graph for mixed-topology stress.",
        ),
    )


def _mixed_4c_4c_system() -> AssociationSystem:
    site_kind = ("A", "A", "D", "D", "A", "A", "D", "D")
    return _binary_system(
        site_component_index=[0, 0, 0, 0, 1, 1, 1, 1],
        site_kind=site_kind,
        active_pairs=tuple(
            (i, j)
            for i, kind_i in enumerate(site_kind)
            for j, kind_j in enumerate(site_kind)
            if i != j and kind_i != kind_j
        ),
    )


def association_evidence_case_ids() -> tuple[str, ...]:
    return tuple(case.case_id for case in association_evidence_cases())


def association_case_by_id(case_id: str) -> AssociationEvidenceCase:
    for case in association_evidence_cases():
        if case.case_id == case_id:
            return case
    raise ValueError(f"Unknown association evidence case_id: {case_id}")


def jax_supported_cases(cases: Iterable[AssociationEvidenceCase] | None = None) -> tuple[AssociationEvidenceCase, ...]:
    return tuple(case for case in (cases or association_evidence_cases()) if case.system is not None)


def _case(
    *,
    case_id: str,
    topology_id: str,
    component_family: str,
    mixture_family: str,
    system: AssociationSystem | None,
    composition: Iterable[float],
    delta: Iterable[Iterable[float]],
    density_grid: tuple[float, ...],
    temperature_grid: tuple[float, ...],
    strength_scale: float,
    source_status: str,
    note: str,
) -> AssociationEvidenceCase:
    delta_rows = tuple(tuple(row) for row in delta)
    delta_matrix = np.zeros((0, 0), dtype=float) if system is None and not delta_rows else np.asarray(delta_rows, dtype=float)
    return AssociationEvidenceCase(
        case_id=case_id,
        topology_id=topology_id,
        component_family=component_family,
        mixture_family=mixture_family,
        system=system,
        composition=np.asarray(tuple(composition), dtype=float),
        delta_matrix=delta_matrix,
        density_grid=density_grid,
        temperature_grid=temperature_grid,
        strength_scale=strength_scale,
        source_status=source_status,
        note=note,
    )


def _binary_system(
    *,
    site_component_index: Iterable[int],
    site_kind: tuple[str, ...],
    active_pairs: tuple[tuple[int, int], ...],
) -> AssociationSystem:
    return AssociationSystem(
        component_count=2,
        site_component_index=np.asarray(tuple(site_component_index), dtype=int),
        site_kind=site_kind,
        active_pairs=active_pairs,
    )


def _full_delta(system: AssociationSystem, strength: float) -> np.ndarray:
    delta = np.zeros((system.site_count, system.site_count), dtype=float)
    for i, j in system.active_pairs:
        delta[i, j] = float(strength)
    return delta


def _delta_from_pairs(site_count: int, pairs: Iterable[tuple[int, int, float]]) -> np.ndarray:
    delta = np.zeros((site_count, site_count), dtype=float)
    for i, j, value in pairs:
        delta[int(i), int(j)] = float(value)
    return delta


def _positive_grid(name: str, values: tuple[float, ...]) -> None:
    if not values:
        raise ValueError(f"{name} is required.")
    array = np.asarray(values, dtype=float)
    if np.any(array <= 0.0) or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain positive finite values.")


def _vector(name: str, value: object) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain finite values.")
    return array
