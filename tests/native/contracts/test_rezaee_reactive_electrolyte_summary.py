from __future__ import annotations

import importlib.util
import sys
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_ROOT = REPO_ROOT / "analyses" / "paper_validation" / "2026_rezaee"
RUN_ALL_PATH = ANALYSIS_ROOT / "scripts" / "run_all.py"


def _run_all_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("rezaee_run_all_truth_contract", RUN_ALL_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    script_dir = str(RUN_ALL_PATH.parent)
    sys.path.insert(0, script_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(script_dir)
    return module


def _scalar_values(value: Any) -> Iterator[Any]:
    if isinstance(value, Mapping):
        for item in value.values():
            yield from _scalar_values(item)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            yield from _scalar_values(item)
    else:
        yield value


def test_rezaee_summary_derives_support_from_the_failed_model_gate() -> None:
    summary = _run_all_module()._build_summary([])

    assert summary["status"] == "internal_source_evidence_only"
    assert summary["source_evidence_complete"] is True
    assert summary["model_validation_complete"] is False
    assert summary["public_route_admitted"] is False
    assert summary["route_scope"] == "source_and_basis_diagnostics"
    assert summary["phase_models_supported"] is False
    assert "public_api" not in summary
    assert "phase_model_public_route_attempt" not in summary
    assert "phase_model_fitted_public_route" not in summary
    assert "phase_model_internal_attempt" not in summary
    assert "phase_model_fitted_internal_diagnostic" not in summary
    assert {row["kind"] for row in summary["blockers"]} == {
        "closed_public_surface",
        "model_validation_absent",
    }
    assert "accepted_public_native_ipopt" not in set(_scalar_values(summary))


def test_rezaee_current_analysis_docs_keep_the_route_internal() -> None:
    analysis = (ANALYSIS_ROOT / "analysis.yaml").read_text(encoding="utf-8")
    readme = (ANALYSIS_ROOT / "README.md").read_text(encoding="utf-8")

    assert "Exercises the public reactive_electrolyte_lle" not in analysis
    assert "public_api_supported_solver_rejected" not in analysis
    assert "The public `mix.equilibrium" not in readme
    assert "public_route_admitted: false" in analysis
    assert "source-evidence-only lane" in readme


def test_rezaee_source_lane_has_no_provider_era_model_path() -> None:
    script_names = {
        path.name
        for path in (ANALYSIS_ROOT / "scripts").glob("*.py")
        if path.is_file()
    }
    assert script_names == {
        "_paths.py",
        "rezaee_2025_target_summary.py",
        "rezaee_section32_basis_inference.py",
        "run_all.py",
    }
    assert not (ANALYSIS_ROOT / "parameters").exists()
    assert not (ANALYSIS_ROOT / "shared" / "results" / "smoke").exists()
    assert not (ANALYSIS_ROOT / "tables").exists()
    assert not list((ANALYSIS_ROOT / "figures").glob("*/results"))
    assert not list((ANALYSIS_ROOT / "figures").glob("*/scripts"))

    processed_names = {
        path.name
        for path in (ANALYSIS_ROOT / "shared" / "results" / "processed").iterdir()
        if path.is_file()
    }
    assert processed_names == {
        "rezaee_2025_extraction_equilibrium_summary.csv",
        "rezaee_2025_extraction_target_summary.csv",
        "rezaee_2026_section32_basis_inference_rows.csv",
    }
    reaction_names = {
        path.name
        for path in (
            ANALYSIS_ROOT / "shared" / "results" / "reaction_equilibrium"
        ).iterdir()
        if path.is_file()
    }
    assert reaction_names == {
        "rezaee_2026_section32_basis_inference.md",
        "rezaee_2026_section32_basis_inference_summary.json",
        "summary.json",
    }
