from __future__ import annotations

import csv
import importlib.util
import math
import shutil
from pathlib import Path

import numpy as np
import pytest
from epcsaft import SolutionError
from epcsaft_equilibrium._native import extension_native_core
from epcsaft_equilibrium.workflows import (
    EquilibriumSolverOptions,
    _electrolyte_lle_validation_result,
)

from scripts.validation.khudaida_parameter_provenance import (
    evaluate_khudaida_parameter_provenance,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
FIGURE_ROOT = REPO_ROOT / "analyses" / "paper_validation" / "2026_khudaida" / "figures" / "figure_02"
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_khudaida_2026_figure_validation.py"
RUNNER_PATH = REPO_ROOT / "analyses" / "paper_validation" / "2026_khudaida" / "scripts" / "run_all.py"
COMMON_PATH = RUNNER_PATH.parent / "_common.py"
FEED = np.asarray(
    [
        0.7295582904360921,
        0.013336215598851259,
        0.20495308450174898,
        0.026076204731653927,
        0.026076204731653927,
    ],
    dtype=float,
)
INTERNAL_SOURCE = "epcsaft_internal_electrolyte_lle_validation"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _copy_khudaida_parameter_evidence(tmp_path: Path) -> Path:
    source_root = REPO_ROOT / "analyses" / "paper_validation" / "2026_khudaida"
    copied_root = tmp_path / "2026_khudaida"
    shutil.copytree(source_root / "parameters", copied_root / "parameters")
    (copied_root / "shared").mkdir()
    shutil.copytree(source_root / "shared" / "source", copied_root / "shared" / "source")
    return copied_root


def _rewrite_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def _plain(value):
    if hasattr(value, "items"):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    return value


def _checker_module():
    spec = importlib.util.spec_from_file_location("khudaida_2026_checker", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _runner_module():
    spec = importlib.util.spec_from_file_location("khudaida_2026_runner", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _common_module():
    spec = importlib.util.spec_from_file_location("khudaida_2026_common", COMMON_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_khudaida_internal_electrolyte_validation_activation_is_closed() -> None:
    native_activation = {row["key"]: row for row in extension_native_core()._native_equilibrium_activation_matrix()}[
        "electrolyte_lle"
    ]
    assert native_activation["production_exposed"] is False
    assert native_activation["public_routes"] == []
    assert native_activation["proof_routes"] == []


@pytest.mark.parametrize(
    "activation",
    [
        {"key": "electrolyte_lle", "production_exposed": True, "public_routes": [], "proof_routes": []},
        {
            "key": "electrolyte_lle",
            "production_exposed": False,
            "public_routes": ["electrolyte_lle"],
            "proof_routes": [],
        },
        {
            "key": "electrolyte_lle",
            "production_exposed": False,
            "public_routes": [],
            "proof_routes": ["stale_proof"],
        },
        None,
    ],
)
def test_internal_electrolyte_adapter_rejects_stale_activation(activation: object) -> None:
    with pytest.raises(SolutionError, match=r"activation contract|closed production surface"):
        _electrolyte_lle_validation_result(
            T=293.15,
            P=100000.0,
            feed=FEED,
            certification={},
            activation=activation,  # type: ignore[arg-type]
            options=EquilibriumSolverOptions(),
        )


def test_khudaida_figure_02_artifacts_are_internal_diagnostics_not_public_proof() -> None:
    model_rows = _rows(FIGURE_ROOT / "results" / "data" / "model_tielines.csv")

    assert len(model_rows) == 16
    assert {row["source"] for row in model_rows} == {INTERNAL_SOURCE}
    assert {row["phase"] for row in model_rows} == {"organic", "aqueous"}
    assert all(math.isfinite(float(row["feed_x_water"])) for row in model_rows)
    for row in model_rows:
        assert row["converged"] == "False"
        assert row["status"] == "rejected_parameter_provenance"
        assert row["route_status"] == "internal_validation_rejected"
        assert row["application_status"] == "rejected_parameter_provenance"
        assert row["postsolve_accepted"] == "False"
        assert "unresolved interaction provenance" in row["message"]


def test_checker_flags_mutated_rejected_rows_that_restore_acceptance_status(tmp_path: Path) -> None:
    checker = _checker_module()
    rows = _rows(FIGURE_ROOT / "results" / "data" / "model_tielines.csv")[:2]
    for row in rows:
        row["converged"] = "False"
        row["status"] = "rejected_collapsed_split"
        row["route_status"] = "internal_validation_accepted"
        row["postsolve_accepted"] = "True"

    model_path = tmp_path / "results" / "data" / "model_tielines.csv"
    model_path.parent.mkdir(parents=True)
    with model_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    failures = checker._model_row_failures(tmp_path)
    assert failures
    assert {failure["failure_kind"] for failure in failures} == {"rejected_status_contract"}


def test_checker_audits_rejected_statuses_in_retained_model_curve(tmp_path: Path) -> None:
    checker = _checker_module()
    source = (
        REPO_ROOT
        / "analyses"
        / "paper_validation"
        / "2026_khudaida"
        / "figures"
        / "figure_11"
        / "results"
        / "model_curve.csv"
    )
    rows = _rows(source)[:2]
    for row in rows:
        row["converged"] = "False"
        row["status"] = "rejected_solver_failure"
        row["route_status"] = "internal_validation_accepted"
        row["postsolve_accepted"] = "True"

    model_path = tmp_path / "results" / "model_curve.csv"
    model_path.parent.mkdir(parents=True)
    with model_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    failures = checker._model_row_failures(tmp_path)
    assert failures
    assert {failure["failure_kind"] for failure in failures} == {"rejected_status_contract"}


def test_checker_reports_partial_khudaida_binary_source_coverage() -> None:
    checker = _checker_module()
    payload = checker.evaluate(("figure_02",))

    provenance = payload.get("parameter_provenance", {})
    assert provenance.get("status") == "partial_source_coverage"
    assert provenance.get("source_backed_pair_count") == 8
    assert provenance.get("total_pair_count") == 10
    assert provenance.get("unresolved_pairs") == ["Butanol/Na+", "Butanol/Cl-"]
    assert provenance.get("unresolved_families") == ["k_hb_ij", "l_ij"]
    assert provenance["families"]["l_ij"]["status"] == "unresolved_parameter_family"
    assert provenance["families"]["k_hb_ij"]["status"] == "unresolved_parameter_family"
    assert provenance["families"]["l_ij"]["executable_values_present"] is False
    assert provenance["families"]["k_hb_ij"]["executable_values_present"] is False
    assert provenance.get("blocking") is True
    assert any(blocker.get("failure_kind") == "parameter_provenance" for blocker in payload.get("model_blockers", []))
    assert {failure["failure_kind"] for failure in payload["figures"][0]["model_row_failures"]} == {
        "parameter_provenance"
    }


def test_khudaida_provenance_value_joins_manifest_to_literature_rows(tmp_path: Path) -> None:
    analysis_root = _copy_khudaida_parameter_evidence(tmp_path)
    manifest_path = analysis_root / "parameters" / "mixed" / "binary_interaction" / "source_manifest.csv"
    rows = _rows(manifest_path)
    row = next(item for item in rows if item["component_i"] == "Ethanol" and item["component_j"] == "H2O")
    row["value"] = "-0.2"
    _rewrite_rows(manifest_path, rows)

    receipt = evaluate_khudaida_parameter_provenance(analysis_root)

    assert "parameter_provenance:source_manifest_value_mismatch:H2O/Ethanol" in receipt["blockers"]


def test_khudaida_provenance_value_joins_executable_matrix_to_manifest(tmp_path: Path) -> None:
    analysis_root = _copy_khudaida_parameter_evidence(tmp_path)
    matrix_path = analysis_root / "parameters" / "mixed" / "binary_interaction" / "k_ij.csv"
    rows = _rows(matrix_path)
    row = next(item for item in rows if item["component"] == "H2O")
    row["Ethanol"] = "-0.2"
    _rewrite_rows(matrix_path, rows)

    receipt = evaluate_khudaida_parameter_provenance(analysis_root)

    assert "parameter_provenance:asymmetric_executable_matrix:H2O/Ethanol" in receipt["blockers"]
    assert "parameter_provenance:matrix_manifest_value_mismatch:H2O/Ethanol" in receipt["blockers"]


def test_khudaida_provenance_value_joins_literature_rows_to_executable_matrix(tmp_path: Path) -> None:
    analysis_root = _copy_khudaida_parameter_evidence(tmp_path)
    source_path = analysis_root / "shared" / "source" / "table_7_epcsaft_kij.csv"
    rows = _rows(source_path)
    row = next(item for item in rows if item["component_i"] == "Ethanol" and item["component_j"] == "H2O")
    row["k_ij"] = "-0.2"
    _rewrite_rows(source_path, rows)

    receipt = evaluate_khudaida_parameter_provenance(analysis_root)

    assert "parameter_provenance:source_manifest_value_mismatch:H2O/Ethanol" in receipt["blockers"]
    assert "parameter_provenance:matrix_source_value_mismatch:H2O/Ethanol" in receipt["blockers"]


def test_khudaida_runner_forces_data_generation_but_not_rendering(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = _runner_module()
    captured: list[dict[str, str]] = []

    def _capture_run(*_args, **kwargs):
        captured.append(dict(kwargs["env"]))

    monkeypatch.setenv("KHUDAIDA_FORCE_RECOMPUTE", "1")
    monkeypatch.setattr(runner.subprocess, "run", _capture_run)

    runner._run(Path("generate_data.py"), allow_force_recompute=True)
    runner._run(Path("render_figure.py"), allow_force_recompute=False)

    assert captured[0]["KHUDAIDA_FORCE_RECOMPUTE"] == "1"
    assert "KHUDAIDA_FORCE_RECOMPUTE" not in captured[1]


@pytest.mark.parametrize("figure_number", range(2, 8))
def test_khudaida_lle_figures_separate_data_generation_from_rendering(figure_number: int) -> None:
    scripts = (
        REPO_ROOT
        / "analyses"
        / "paper_validation"
        / "2026_khudaida"
        / "figures"
        / f"figure_{figure_number:02d}"
        / "scripts"
    )
    generate_source = (scripts / "generate_data.py").read_text(encoding="utf-8")
    render_source = (scripts / "render_figure.py").read_text(encoding="utf-8")
    common_source = (RUNNER_PATH.parent / "_common.py").read_text(encoding="utf-8")

    assert "common.write_lle_figure_data" in generate_source
    assert "force_recompute=True" in generate_source
    assert "common.plot_lle_figure" in render_source
    plot_body = common_source.split("def plot_lle_figure", maxsplit=1)[1].split("\ndef ", maxsplit=1)[0]
    assert "load_lle_figure_data" in plot_body
    assert "write_lle_figure_data" not in plot_body


def test_khudaida_render_loader_consumes_current_retained_rows_without_solving() -> None:
    common = _common_module()
    data = common.load_lle_figure_data(FIGURE_ROOT / "scripts", 2, 293.15, 0.05)

    assert len(data["model"]) == 8
    assert all(common._model_row_rejection_contract_is_current(row) for row in data["model"])


@pytest.mark.parametrize("figure_number", (11, 12))
def test_khudaida_supporting_figures_render_without_rewriting_data(figure_number: int) -> None:
    scripts = (
        REPO_ROOT
        / "analyses"
        / "paper_validation"
        / "2026_khudaida"
        / "figures"
        / f"figure_{figure_number:02d}"
        / "scripts"
    )
    generate_source = (scripts / "generate_data.py").read_text(encoding="utf-8")
    render_source = (scripts / "render_figure.py").read_text(encoding="utf-8")
    common_source = COMMON_PATH.read_text(encoding="utf-8")

    assert "common.write_supporting_figure_data" in generate_source
    assert "common.plot_supporting_figure_grid" in render_source
    panel_body = common_source.split("def _supporting_panel_rows", maxsplit=1)[1].split("\ndef ", maxsplit=1)[0]
    plot_body = common_source.split("def plot_supporting_figure_grid", maxsplit=1)[1].split("\ndef ", maxsplit=1)[0]
    assert "load_lle_figure_data" in panel_body
    assert "write_supporting_figure_data" not in plot_body
    assert "_write_supporting_contract_outputs" not in plot_body


def test_khudaida_tables_generate_retained_rows_before_rendering() -> None:
    scripts = RUNNER_PATH.parent / "tables_009_010"
    generate_source = (scripts / "generate_data.py").read_text(encoding="utf-8")
    render_source = (scripts / "plot_tables_9_10.py").read_text(encoding="utf-8")
    common_source = COMMON_PATH.read_text(encoding="utf-8")

    assert "common.write_tables_9_10_data" in generate_source
    assert "common.plot_tables_9_10" in render_source
    rows_body = common_source.split("def _table_rows_for_png", maxsplit=1)[1].split("\ndef ", maxsplit=1)[0]
    plot_body = common_source.split("def plot_tables_9_10", maxsplit=1)[1].split("\ndef ", maxsplit=1)[0]
    assert "load_lle_figure_data" in rows_body
    assert "get_or_build_model_rows" not in rows_body
    assert "_load_table_rows" in plot_body
    assert "_table_rows_for_png" not in plot_body


@pytest.mark.parametrize(
    "rejected_status",
    ["rejected_solver_failure", "rejected_unclassified_condition"],
)
def test_explicit_rejection_status_cannot_be_counted_or_serialized_as_accepted(
    rejected_status: str,
) -> None:
    common = _common_module()
    row = {
        "tie_line": 1,
        "temperature_K": 293.15,
        "salt_wtfrac": 0.05,
        "organic_formula": np.asarray([0.7, 0.1, 0.15, 0.05]),
        "aqueous_formula": np.asarray([0.4, 0.2, 0.3, 0.1]),
        "feed_formula": np.asarray([0.55, 0.15, 0.225, 0.075]),
        "beta_organic": 0.5,
        "beta_aqueous": 0.5,
        "residual_norm": 1.0e-8,
        "objective": 0.1,
        "converged": True,
        "status": rejected_status,
        "message": "rejected",
        "route_status": "internal_validation_accepted",
        "solver_status": "success",
        "application_status": "solve_succeeded",
        "postsolve_accepted": True,
        "phase_distance": 0.3,
        "source": INTERNAL_SOURCE,
    }

    assert common._accepted_model_rows([row]) == []
    serialized = common._model_rows_for_csv([row])
    assert all(item["converged"] is False for item in serialized)
    assert {item["status"] for item in serialized} == {rejected_status}
    assert {item["route_status"] for item in serialized} == {"internal_validation_rejected"}
    assert {item["application_status"] for item in serialized} == {rejected_status}
    assert {item["postsolve_accepted"] for item in serialized} == {False}


def test_khudaida_model_execution_stops_before_native_solve_when_interactions_are_unresolved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    common = _common_module()

    def _unexpected_native_construction(*_args, **_kwargs):
        pytest.fail("native mixture construction must not run with unresolved interaction provenance")

    monkeypatch.setattr(common.epcsaft.Mixture, "from_folder", _unexpected_native_construction)
    result = common._solve_formula_feed_direct(293.15, np.asarray([0.75, 0.01, 0.21, 0.03]))

    assert result["converged"] is False
    assert result["status"] == "rejected_parameter_provenance"
    assert result["route_status"] == "internal_validation_rejected"
    assert result["postsolve_accepted"] is False
    assert "unresolved interaction provenance" in result["message"]
