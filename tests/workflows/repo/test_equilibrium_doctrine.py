from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
M4_ROOT = REPO_ROOT / "docs" / "superpowers" / "milestones" / "M4-equilibrium"
ARCHITECTURE_PATH = M4_ROOT / "generalized-fluid-phase-equilibrium.md"

DOCTRINE_SOURCES = {
    "algorithms/neutral-held.md": (
        "docs/papers/md/Equilibrium/"
        "Pereira et al. - 2012 - The HELD algorithm for multicomponent, multiphase "
        "equilibrium calculations with generic equations of.md"
    ),
    "algorithms/strong-electrolyte-held2.md": (
        "docs/papers/md/Equilibrium/"
        "Perdomo et al. - 2025 - Phase stability criteria and fluid-phase equilibria "
        "in strong-electrolyte systems.md"
    ),
    "algorithms/ascani-electrolyte-equilibrium.md": (
        "docs/papers/md/Equilibrium/"
        "Ascani, Sadowski, Held - 2022 - Calculation of Multiphase Equilibria "
        "Containing Mixed Solvents and M.md"
    ),
    "algorithms/chemical-and-coupled-equilibrium.md": (
        "docs/papers/md/Equilibrium/"
        "Ascani - 2023 - Simultaneous Predictions of Chemical and Phase Equilibria "
        "in Systems with an Esterif.md"
    ),
}

DOCTRINE_ANCHORS = {
    "algorithms/neutral-held.md": {
        "figure-1-table-1-three-stage-scheme",
        "section-3.1-stage-i-stability",
        "section-3.2-stage-ii-dual-loop",
        "section-3.3-stage-iii-free-energy-minimization",
    },
    "algorithms/strong-electrolyte-held2.md": {
        "section-2.2-electroneutrality-and-eliminated-species",
        "section-3.2-modified-mole-coordinates",
        "section-4-algorithm-1-three-stage-scheme",
        "section-4.4-stage-iii-free-energy-minimization",
    },
    "algorithms/ascani-electrolyte-equilibrium.md": {
        "section-2-equations-13-25-equilibrium-conditions",
        "section-3.1-equations-26-27-independent-counterion-pairs",
        "section-3.2-equations-28-32-electroneutral-variables",
        "section-3.3-equations-33-35-tangent-plane-distance",
        "figure-1-successive-phase-addition",
    },
    "algorithms/chemical-and-coupled-equilibrium.md": {
        "section-2.1-equations-1-10-ce-cpe-thermodynamics",
        "section-2.2-equations-13-17-coupled-residual-solve",
        "algorithmic-structure-steps-1-4",
        "figure-7-cpe-procedure",
    },
}

EXPECTED_ALGORITHM_IDS = {
    "pereira-held",
    "perdomo-held2",
    "ascani-counterion-pair-equilibrium",
    "standalone-chemical-equilibrium",
    "simultaneous-chemical-phase-equilibrium",
}


def _front_matter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"missing YAML front matter: {path.relative_to(REPO_ROOT)}"
    _, raw, _ = text.split("---", maxsplit=2)
    metadata = yaml.safe_load(raw)
    assert isinstance(metadata, dict), path.relative_to(REPO_ROOT)
    return metadata


def test_stage_one_doctrine_files_have_distinct_source_backed_algorithm_identities() -> None:
    observed_ids: set[str] = set()

    for relative_path, source_path in DOCTRINE_SOURCES.items():
        doctrine_path = M4_ROOT / relative_path
        metadata = _front_matter(doctrine_path)

        assert metadata["doctrine_schema_version"] == 1
        assert metadata["source_local_path"] == source_path
        assert (REPO_ROOT / source_path).is_file(), source_path
        assert set(metadata["source_anchors"]) == DOCTRINE_ANCHORS[relative_path]
        assert metadata["runtime_status"] == "closed"
        assert metadata["algorithm_parity_status"] == "incomplete"
        observed_ids.update(metadata["algorithm_ids"])

    assert observed_ids == EXPECTED_ALGORITHM_IDS


def test_held_stage_three_is_direct_total_free_energy_minimization() -> None:
    for relative_path in (
        "algorithms/neutral-held.md",
        "algorithms/strong-electrolyte-held2.md",
    ):
        metadata = _front_matter(M4_ROOT / relative_path)

        assert metadata["stage_iii_primary_problem"] == "direct-total-free-energy-minimization"
        assert metadata["residual_solve_role"] == "optional-corrector-or-diagnostic"


def test_source_faithful_held_controllers_have_not_executed_stage_two_or_three() -> None:
    for relative_path in (
        "algorithms/neutral-held.md",
        "algorithms/strong-electrolyte-held2.md",
    ):
        metadata = _front_matter(M4_ROOT / relative_path)

        assert metadata["stage_ii_status"] == "not-executed"
        assert metadata["stage_iii_status"] == "not-executed"


def test_electrolyte_formulations_keep_independent_stationarity_conditions() -> None:
    held2 = _front_matter(M4_ROOT / "algorithms" / "strong-electrolyte-held2.md")
    ascani = _front_matter(M4_ROOT / "algorithms" / "ascani-electrolyte-equilibrium.md")

    assert held2["interphase_stationarity"] == "independent-modified-potential-equality"
    assert ascani["interphase_stationarity"] == "independent-mean-ionic-or-pair-equality"
    assert held2["individual_ionic_potential_comparison_requires"] == "explicit-galvani-convention"
    assert ascani["individual_ionic_potential_comparison_requires"] == "explicit-galvani-convention"


def test_coupled_equilibrium_conserves_elemental_inventory() -> None:
    chemical = _front_matter(M4_ROOT / "algorithms" / "chemical-and-coupled-equilibrium.md")

    assert chemical["conservation_basis"] == "fixed-elemental-inventory"


def test_public_boundary_routes_are_direct_local_problems() -> None:
    metadata = _front_matter(ARCHITECTURE_PATH)

    assert metadata["current_public_routes"] == [
        "bubble_pressure",
        "dew_pressure",
        "single_component_vle",
    ]
    assert metadata["public_boundary_routes"] == {
        "bubble_pressure": {"algorithm_family": "direct-boundary", "executes_held_discovery": False},
        "dew_pressure": {"algorithm_family": "direct-boundary", "executes_held_discovery": False},
    }


def test_architecture_authority_links_every_stage_one_doctrine_file() -> None:
    metadata = _front_matter(ARCHITECTURE_PATH)

    assert metadata["doctrine_documents"] == list(DOCTRINE_SOURCES)


def test_active_doctrine_has_no_sampled_candidate_dual_completion_status() -> None:
    active_paths = [
        ARCHITECTURE_PATH,
        M4_ROOT / "README.md",
        REPO_ROOT
        / "docs"
        / "superpowers"
        / "specs"
        / "2026-05-26-m4-equilibrium-stage-by-stage-implementation-plan.md",
        *(M4_ROOT / path for path in DOCTRINE_SOURCES),
    ]
    forbidden_statuses = {
        "dual_loop_verified",
        "held_stage_ii_complete",
        "held2_stage_ii_complete",
        "verified_current_route_refinement_consumed_stage_ii_replay",
        "verified_dual_loop_replayable",
    }

    offenders = {
        path.relative_to(REPO_ROOT).as_posix(): sorted(
            status for status in forbidden_statuses if status in path.read_text(encoding="utf-8")
        )
        for path in active_paths
        if path.is_file()
        and any(status in path.read_text(encoding="utf-8") for status in forbidden_statuses)
    }

    assert offenders == {}
