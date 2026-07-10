from __future__ import annotations

import csv
from pathlib import Path

import epcsaft
import pytest
from epcsaft_equilibrium._native import extension_native_core
from equilibrium_support.equilibrium_cases import gross_2002_associating_parameter_set

from scripts.validation import check_associating_lle_gross_2002 as checker

REPO_ROOT = Path(__file__).resolve().parents[5]
CASE_DIR = (
    REPO_ROOT
    / "data"
    / "reference"
    / "equilibrium_benchmarks"
    / "associating_lle"
    / "methanol_cyclohexane"
)
FIGURE_08_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "figures" / "figure_08"
FIGURE_08_SOURCE = FIGURE_08_DIR / "source" / "source_points.csv"
FIGURE_08_PLOT = FIGURE_08_DIR / "results" / "figure_08.png"


def test_internal_gross_2002_associating_lle_source_pair_is_certified() -> None:
    payload = checker.evaluate_case_dir(
        CASE_DIR,
        require_source_data=True,
        require_exact_association_hessian=True,
        require_internal_route=True,
        require_route_closed=True,
    )

    assert payload["complete"] is True
    route = payload["internal_route"]
    assert route["status"] == "internal_source_pair_certified"
    assert route["phase_count"] == 2
    assert route["phase_branches"] == ["methanol_lean_liquid", "methanol_rich_liquid"]
    assert route["phase_distance"] > 0.5
    assert route["max_branch_composition_abs_error"] <= 0.10
    assert route["max_temperature_abs_error_K"] <= 5.0
    assert route["association_hessian_status"] == "verified_exact"
    postsolve = route["postsolve"]
    assert postsolve["neutral_held_tpd_contract_preserved"] is True
    assert postsolve["public_admission_state"] == "closed"
    assert postsolve["stability_certificate"] == "sampled_candidate_source_pair_component_evidence"
    assert postsolve["phase_set_status"] == "source_pair_certified"


def test_internal_sampled_candidate_diagnostic_resolves_figure_08_rich_branch() -> None:
    with FIGURE_08_SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    source_pair = {
        row["series"]: row
        for row in source_rows
        if row["series"] in {"lle_methanol_lean", "lle_methanol_rich"} and float(row["T_K"]) < 281.0
    }
    assert FIGURE_08_PLOT.is_file()

    mixture = epcsaft.Mixture(gross_2002_associating_parameter_set())
    discovery = extension_native_core()._native_neutral_tpd_phase_discovery(
        mixture.native._native,
        float(source_pair["lle_methanol_rich"]["T_K"]),
        float(source_pair["lle_methanol_rich"]["pressure_bar"]) * 1.0e5,
        [0.5, 0.5],
        [0, 0],
        1.0e-6,
        1.0e-6,
        True,
    )

    phase_compositions = sorted(
        (list(map(float, composition)) for composition in discovery["selected_phase_compositions"]),
        key=lambda composition: composition[0],
    )
    assert discovery["deterministic_screening_is_full_held"] is False
    assert discovery["held_stage_ii_dual_loop_status"] == "not_performed"
    assert discovery["continuous_tpd_start_count"] == 5
    assert discovery["selected_candidate_count"] == 2
    assert phase_compositions[0][0] == pytest.approx(
        float(source_pair["lle_methanol_lean"]["x_methanol"]),
        abs=0.10,
    )
    assert phase_compositions[-1][0] == pytest.approx(
        float(source_pair["lle_methanol_rich"]["x_methanol"]),
        abs=0.10,
    )

    middle_pair = {
        row["series"]: row
        for row in source_rows
        if row["series"] in {"lle_methanol_lean", "lle_methanol_rich"}
        and 309.0 < float(row["T_K"]) < 310.0
    }
    middle_discovery = extension_native_core()._native_neutral_tpd_phase_discovery(
        mixture.native._native,
        float(middle_pair["lle_methanol_rich"]["T_K"]),
        float(middle_pair["lle_methanol_rich"]["pressure_bar"]) * 1.0e5,
        [0.5, 0.5],
        [0, 0],
        1.0e-6,
        1.0e-6,
        True,
    )
    middle_compositions = sorted(
        (list(map(float, composition)) for composition in middle_discovery["selected_phase_compositions"]),
        key=lambda composition: composition[0],
    )
    assert middle_compositions[0][0] == pytest.approx(
        float(middle_pair["lle_methanol_lean"]["x_methanol"]),
        abs=0.05,
    )
    assert middle_compositions[-1][0] == pytest.approx(
        float(middle_pair["lle_methanol_rich"]["x_methanol"]),
        abs=0.05,
    )

    near_plait_pair = {
        row["series"]: row
        for row in source_rows
        if row["series"] in {"lle_methanol_lean", "lle_methanol_rich"}
        and float(row["T_K"]) > 319.0
    }
    near_plait_discovery = extension_native_core()._native_neutral_tpd_phase_discovery(
        mixture.native._native,
        float(near_plait_pair["lle_methanol_rich"]["T_K"]),
        float(near_plait_pair["lle_methanol_rich"]["pressure_bar"]) * 1.0e5,
        [0.5, 0.5],
        [0, 0],
        1.0e-6,
        1.0e-6,
        True,
    )
    near_plait_compositions = sorted(
        (list(map(float, composition)) for composition in near_plait_discovery["selected_phase_compositions"]),
        key=lambda composition: composition[0],
    )
    assert near_plait_compositions[0][0] == pytest.approx(
        float(near_plait_pair["lle_methanol_lean"]["x_methanol"]),
        abs=0.05,
    )
    assert near_plait_compositions[-1][0] == pytest.approx(
        float(near_plait_pair["lle_methanol_rich"]["x_methanol"]),
        abs=0.05,
    )
