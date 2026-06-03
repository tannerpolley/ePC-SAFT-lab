from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .association_models import AssociationSystem
from .closure_models import ClosureResult


@dataclass(frozen=True)
class HuangRadoszTopology:
    topology_type: str
    site_kind: tuple[str, ...]
    active_pairs: tuple[tuple[int, int], ...]
    topology_gate: str
    derivation_relationship: str


@dataclass(frozen=True)
class TopologyReductionResult:
    name: str
    xa: np.ndarray
    source_formula_family: str
    source_formula_id: str
    derivation_family: str
    comparison_role: str
    topology_gate: str
    exactness_claim: str
    derivation_relationship: str

    def as_closure_result(self) -> ClosureResult:
        return ClosureResult(
            name=self.name,
            xa=self.xa,
            association_model="implicit_exact",
            association_closure=self.name,
            exact_derivative_of="exact_mass_action",
            information_loss="topology_assumption",
        )


HUANG_RADOSZ_TOPOLOGIES: dict[str, HuangRadoszTopology] = {
    "1": HuangRadoszTopology(
        topology_type="1",
        site_kind=("D",),
        active_pairs=((0, 0),),
        topology_gate="one equivalent self-associating site; delta_AA nonzero",
        derivation_relationship="topology_reduction_not_closure_a",
    ),
    "2A": HuangRadoszTopology(
        topology_type="2A",
        site_kind=("D", "A"),
        active_pairs=((0, 0), (0, 1), (1, 0), (1, 1)),
        topology_gate="two equivalent sites with every pair interaction active and equal",
        derivation_relationship="topology_reduction_not_closure_a",
    ),
    "2B": HuangRadoszTopology(
        topology_type="2B",
        site_kind=("D", "A"),
        active_pairs=((0, 1), (1, 0)),
        topology_gate="two donor-acceptor sites with only unlike interactions active and equal",
        derivation_relationship="matches_closure_a_when_one_associating_component_da",
    ),
    "3A": HuangRadoszTopology(
        topology_type="3A",
        site_kind=("D", "A", "A"),
        active_pairs=tuple((i, j) for i in range(3) for j in range(3)),
        topology_gate="three equivalent sites with every pair interaction active and equal",
        derivation_relationship="topology_reduction_not_closure_a",
    ),
    "3B": HuangRadoszTopology(
        topology_type="3B",
        site_kind=("A", "A", "D"),
        active_pairs=((0, 2), (2, 0), (1, 2), (2, 1)),
        topology_gate="two equivalent acceptor-like sites and one donor-like site; only AC and BC active",
        derivation_relationship="topology_reduction_not_closure_a",
    ),
    "4A": HuangRadoszTopology(
        topology_type="4A",
        site_kind=("D", "D", "A", "A"),
        active_pairs=tuple((i, j) for i in range(4) for j in range(4)),
        topology_gate="four equivalent sites with every pair interaction active and equal",
        derivation_relationship="topology_reduction_not_closure_a",
    ),
    "4B": HuangRadoszTopology(
        topology_type="4B",
        site_kind=("A", "A", "A", "D"),
        active_pairs=((0, 3), (3, 0), (1, 3), (3, 1), (2, 3), (3, 2)),
        topology_gate="three equivalent acceptor-like sites and one donor-like site; only AD, BD, and CD active",
        derivation_relationship="topology_reduction_not_closure_a",
    ),
    "4C": HuangRadoszTopology(
        topology_type="4C",
        site_kind=("A", "A", "D", "D"),
        active_pairs=((0, 2), (2, 0), (0, 3), (3, 0), (1, 2), (2, 1), (1, 3), (3, 1)),
        topology_gate="two equivalent acceptor-like and two donor-like sites; only cross-class interactions active",
        derivation_relationship="topology_reduction_not_closure_a",
    ),
}


def topology_system(topology: HuangRadoszTopology | str) -> AssociationSystem:
    if isinstance(topology, str):
        topology = _topology(topology)
    return AssociationSystem(
        component_count=1,
        site_component_index=np.zeros(len(topology.site_kind), dtype=int),
        site_kind=topology.site_kind,
        active_pairs=topology.active_pairs,
    )


def evaluate_topology_reduction(topology_type: str, *, density: float, strength: float) -> TopologyReductionResult:
    topology = _topology(topology_type)
    c = _reduced_strength(density=density, strength=strength)
    xa = _site_fractions_for_topology(topology.topology_type, c)
    return TopologyReductionResult(
        name=f"topology_reduction_huang_radosz_{topology.topology_type.lower()}",
        xa=xa,
        source_formula_family="huang_radosz_table_vii",
        source_formula_id=f"huang_radosz_table_vii_{topology.topology_type.lower()}",
        derivation_family="topology_reduction",
        comparison_role="exact_topology_reduction",
        topology_gate=topology.topology_gate,
        exactness_claim="exact_under_table_vii_topology_assumptions",
        derivation_relationship=topology.derivation_relationship,
    )


def _topology(topology_type: str) -> HuangRadoszTopology:
    token = str(topology_type).strip().upper()
    if token not in HUANG_RADOSZ_TOPOLOGIES:
        raise ValueError(f"Unknown Huang/Radosz topology type: {topology_type}")
    return HUANG_RADOSZ_TOPOLOGIES[token]


def _reduced_strength(*, density: float, strength: float) -> float:
    c = float(density) * float(strength)
    if not np.isfinite(c) or c < 0.0:
        raise ValueError("density*strength must be finite and nonnegative.")
    return c


def _equivalent_site_fraction(c: float, active_neighbor_count: int) -> float:
    if active_neighbor_count <= 0:
        raise ValueError("active_neighbor_count must be positive.")
    if c == 0.0:
        return 1.0
    n = float(active_neighbor_count)
    return float((-1.0 + np.sqrt(1.0 + 4.0 * n * c)) / (2.0 * n * c))


def _site_fractions_for_topology(topology_type: str, c: float) -> np.ndarray:
    if topology_type == "1":
        return np.array([_equivalent_site_fraction(c, 1)], dtype=float)
    if topology_type == "2A":
        value = _equivalent_site_fraction(c, 2)
        return np.array([value, value], dtype=float)
    if topology_type == "2B":
        value = _equivalent_site_fraction(c, 1)
        return np.array([value, value], dtype=float)
    if topology_type == "3A":
        value = _equivalent_site_fraction(c, 3)
        return np.array([value, value, value], dtype=float)
    if topology_type == "3B":
        if c == 0.0:
            return np.ones(3, dtype=float)
        xa = float((-(1.0 - c) + np.sqrt((1.0 + c) ** 2 + 4.0 * c)) / (4.0 * c))
        return np.array([xa, xa, 2.0 * xa - 1.0], dtype=float)
    if topology_type == "4A":
        value = _equivalent_site_fraction(c, 4)
        return np.array([value, value, value, value], dtype=float)
    if topology_type == "4B":
        if c == 0.0:
            return np.ones(4, dtype=float)
        xa = float((-(1.0 - 2.0 * c) + np.sqrt((1.0 + 2.0 * c) ** 2 + 4.0 * c)) / (6.0 * c))
        return np.array([xa, xa, xa, 3.0 * xa - 2.0], dtype=float)
    if topology_type == "4C":
        value = _equivalent_site_fraction(c, 2)
        return np.array([value, value, value, value], dtype=float)
    raise ValueError(f"Unknown Huang/Radosz topology type: {topology_type}")
