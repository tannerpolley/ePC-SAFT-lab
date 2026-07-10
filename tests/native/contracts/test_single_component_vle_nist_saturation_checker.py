from __future__ import annotations

import csv
import math
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from analyses.package_validation.equilibrium_single_component_vle.figures.hydrocarbon_saturation_pressure.scripts import (
    generate_data,
)
from scripts.validation import check_single_component_vle_nist_saturation as checker

REPO_ROOT = Path(__file__).resolve().parents[3]
REFERENCE_ROOT = REPO_ROOT / "data" / "reference" / "pure_component" / "saturation_properties"


def _retained_source_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for species in ("methane", "ethane", "propane"):
        path = REFERENCE_ROOT / species / "saturation_properties.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows.extend(csv.DictReader(handle))
    species_order = {"Methane": 0, "Ethane": 1, "Propane": 2}
    return sorted(rows, key=lambda row: (species_order[row["species"]], float(row["T_K"])))


NIST_SOURCE_URLS = {row["species"]: row["source"] for row in _retained_source_rows()}


def _recompute_stored_errors(row: dict[str, object]) -> None:
    pressure_absolute_error = float(row["p_sat_route_Pa"]) - float(row["p_sat_nist_Pa"])
    pressure_relative_error = 100.0 * pressure_absolute_error / float(row["p_sat_nist_Pa"])
    density_absolute_error = float(row["rho_liquid_route_kg_m3"]) - float(row["rho_sat_liq_nist_kg_m3"])
    density_relative_error = 100.0 * density_absolute_error / float(row["rho_sat_liq_nist_kg_m3"])
    row.update(
        {
            "absolute_error_Pa": pressure_absolute_error,
            "relative_error_percent": pressure_relative_error,
            "absolute_relative_error_percent": abs(pressure_relative_error),
            "rho_sat_liq_absolute_error_kg_m3": density_absolute_error,
            "rho_sat_liq_relative_error_percent": density_relative_error,
            "rho_sat_liq_absolute_relative_error_percent": abs(density_relative_error),
        }
    )


def _accepted_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in _retained_source_rows():
        reference_pressure = float(source["p_sat_Pa"])
        reference_density = float(source["rho_sat_liq_kg_m3"])
        row: dict[str, object] = {
            "species": source["species"],
            "T_K": float(source["T_K"]),
            "p_sat_nist_Pa": reference_pressure,
            "p_sat_route_Pa": reference_pressure * 1.02,
            "rho_sat_liq_nist_kg_m3": reference_density,
            "rho_liquid_route_kg_m3": reference_density * 1.01,
            "route_status": "accepted",
            "solver_status": "success",
            "phase_distance": 0.25,
            "pressure_consistency_norm": 1.0e-4,
            "chemical_potential_consistency_norm": 1.0e-8,
            "ln_fugacity_consistency_norm": 1.0e-8,
            "exact_hessian_available": True,
            "hessian_approximation": "exact",
            "jacobian_approximation": "exact",
            "hessian_backend": "cppad_phase_pressure_route",
            "eval_h_calls": 4,
            "solver_tolerance": 1.0e-7,
            "max_iterations": 500,
            "source": source["source"],
        }
        _recompute_stored_errors(row)
        rows.append(row)
    return rows


def _receipt(native_path: Path) -> dict[str, object]:
    current_identity = checker.native_freshness.equilibrium_native_source_identity()
    return {
        "git_commit": "0123456789abcdef",
        "native_module_name": "epcsaft_equilibrium._native._core",
        "native_module_path": str(native_path),
        "checker_command": [
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/validation/check_single_component_vle_nist_saturation.py",
            "--json",
            "--require-complete",
            "--require-fresh-native",
        ],
        "build_refresh_command": "uv run --no-sync python scripts/dev/build_epcsaft.py --profile equilibrium --build-only --parallel 4",
        "freshness_mode": "embedded_source_identity",
        "source_identity_algorithm": current_identity["algorithm"],
        "source_identity_scope": current_identity["scope"],
        "source_identity_limit": current_identity["scope_limit"],
        "source_identity_file_count": current_identity["file_count"],
        "current_source_identity": current_identity["source_identity"],
        "embedded_source_identity_algorithm": current_identity["algorithm"],
        "embedded_source_identity_scope": current_identity["scope"],
        "embedded_source_identity_limit": current_identity["scope_limit"],
        "embedded_source_identity_file_count": current_identity["file_count"],
        "embedded_source_identity": current_identity["source_identity"],
        "source_identity_matches": True,
    }


def test_evaluate_live_rows_accepts_exact_32_point_nist_campaign(tmp_path: Path) -> None:
    result = checker.evaluate_live_rows(
        _accepted_rows(),
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is True
    assert result["blockers"] == []
    assert result["evidence_mode"] == "live_solver_execution"
    assert result["row_count"] == 32
    assert result["species_row_counts"] == {"Ethane": 10, "Methane": 9, "Propane": 13}
    assert result["metrics"] == pytest.approx(
        {
            "max_pressure_absolute_relative_error_percent": 2.0,
            "max_liquid_density_absolute_relative_error_percent": 1.0,
            "max_pressure_consistency_norm": 1.0e-4,
            "max_chemical_potential_consistency_norm": 1.0e-8,
            "max_ln_fugacity_consistency_norm": 1.0e-8,
            "min_phase_distance": 0.25,
        }
    )
    assert result["diagnostic_only_metrics"] == {
        "ln_fugacity_consistency_norm": {
            "summary_metric": "max_ln_fugacity_consistency_norm",
            "acceptance_role": "diagnostic_only",
            "rationale": (
                "The native pure-density saturation route certifies phase pressure and "
                "chemical-potential consistency; the logarithmic fugacity difference is "
                "retained separately to expose low-pressure conditioning."
            ),
        }
    }
    assert result["derivative_evidence"] == {
        "exact_hessian_row_count": 32,
        "hessian_approximation": "exact",
        "jacobian_approximation": "exact",
        "hessian_backend": "cppad_phase_pressure_route",
        "min_eval_h_calls": 4,
    }


@pytest.mark.parametrize(
    ("field", "value", "blocker"),
    [
        ("route_status", "rejected", "route_status_not_accepted:Methane:100K"),
        ("solver_status", "iteration_limit", "solver_status_not_success:Methane:100K"),
        (
            "absolute_relative_error_percent",
            4.01,
            "pressure_absolute_relative_error_above_threshold:Methane:100K",
        ),
        (
            "rho_sat_liq_absolute_relative_error_percent",
            2.01,
            "liquid_density_absolute_relative_error_above_threshold:Methane:100K",
        ),
        (
            "pressure_consistency_norm",
            1.01e-2,
            "pressure_consistency_norm_above_threshold:Methane:100K",
        ),
        (
            "chemical_potential_consistency_norm",
            1.01e-6,
            "chemical_potential_consistency_norm_above_threshold:Methane:100K",
        ),
        ("phase_distance", 9.9e-3, "phase_distance_below_threshold:Methane:100K"),
    ],
)
def test_evaluate_live_rows_fails_closed_on_route_or_threshold_violation(
    tmp_path: Path,
    field: str,
    value: object,
    blocker: str,
) -> None:
    rows = _accepted_rows()
    rows[0][field] = value

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert blocker in result["blockers"]


@pytest.mark.parametrize(
    ("field", "value", "blocker"),
    [
        (
            "exact_hessian_available",
            False,
            "exact_hessian_missing:Methane:100K",
        ),
        (
            "hessian_approximation",
            "limited-memory",
            "hessian_approximation_not_exact:Methane:100K",
        ),
        (
            "jacobian_approximation",
            "finite-difference-values",
            "jacobian_approximation_not_exact:Methane:100K",
        ),
        (
            "hessian_backend",
            "finite_difference",
            "hessian_backend_not_exact_pressure_route:Methane:100K",
        ),
        ("eval_h_calls", 0, "eval_h_calls_not_positive:Methane:100K"),
    ],
)
def test_evaluate_live_rows_rejects_mutated_exact_derivative_evidence(
    tmp_path: Path,
    field: str,
    value: object,
    blocker: str,
) -> None:
    rows = _accepted_rows()
    rows[0][field] = value

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert blocker in result["blockers"]


@pytest.mark.parametrize(
    "field",
    [
        "absolute_relative_error_percent",
        "rho_sat_liq_absolute_relative_error_percent",
        "pressure_consistency_norm",
        "chemical_potential_consistency_norm",
        "ln_fugacity_consistency_norm",
        "phase_distance",
    ],
)
def test_evaluate_live_rows_rejects_negative_absolute_error_or_norm_metric(
    tmp_path: Path,
    field: str,
) -> None:
    rows = _accepted_rows()
    rows[0][field] = -1.0e-12

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert f"negative_metric:{field}:Methane:100K" in result["blockers"]


def test_evaluate_live_rows_retains_low_pressure_ln_fugacity_as_diagnostic(
    tmp_path: Path,
) -> None:
    rows = _accepted_rows()
    rows[0]["ln_fugacity_consistency_norm"] = 1.226164024918188e-4

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is True
    assert result["metrics"]["max_ln_fugacity_consistency_norm"] == pytest.approx(1.226164024918188e-4)
    assert "max_ln_fugacity_consistency_norm" not in result["thresholds"]


def test_evaluate_live_rows_requires_exact_source_grid_and_fresh_native_receipt() -> None:
    rows = _accepted_rows()[1:]

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt={},
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert "nist_source_grid_mismatch" in result["blockers"]
    assert "native_freshness_receipt_missing" in result["blockers"]


def test_evaluate_live_rows_rejects_mutated_nist_source_url(tmp_path: Path) -> None:
    rows = _accepted_rows()
    rows[0]["source"] = NIST_SOURCE_URLS["Ethane"]

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert "nist_source_identity_mismatch:Methane:100K" in result["blockers"]


def test_evaluate_live_rows_rejects_species_source_join_mutation(tmp_path: Path) -> None:
    rows = _accepted_rows()
    rows[0]["species"] = "Ethane"

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert "nist_source_identity_mismatch:Ethane:100K" in result["blockers"]


def test_evaluate_live_rows_rejects_coordinated_species_and_url_swap(
    tmp_path: Path,
) -> None:
    rows = _accepted_rows()
    methane_index = next(index for index, row in enumerate(rows) if row["species"] == "Methane")
    ethane_index = next(index for index, row in enumerate(rows) if row["species"] == "Ethane")
    rows[methane_index]["species"], rows[ethane_index]["species"] = (
        rows[ethane_index]["species"],
        rows[methane_index]["species"],
    )
    rows[methane_index]["source"], rows[ethane_index]["source"] = (
        rows[ethane_index]["source"],
        rows[methane_index]["source"],
    )

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert any("nist_source_reference_mismatch" in blocker for blocker in result["blockers"])


def test_evaluate_live_rows_rejects_fabricated_source_values_with_recomputed_errors(
    tmp_path: Path,
) -> None:
    rows = _accepted_rows()
    rows[0]["p_sat_nist_Pa"] = float(rows[0]["p_sat_nist_Pa"]) * 1.1
    rows[0]["rho_sat_liq_nist_kg_m3"] = float(rows[0]["rho_sat_liq_nist_kg_m3"]) * 0.9
    _recompute_stored_errors(rows[0])

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert any("nist_source_reference_mismatch" in blocker for blocker in result["blockers"])


@pytest.mark.parametrize(
    "field",
    [
        "p_sat_nist_Pa",
        "p_sat_route_Pa",
        "rho_sat_liq_nist_kg_m3",
        "rho_liquid_route_kg_m3",
    ],
)
@pytest.mark.parametrize("value", [0.0, -1.0, float("nan"), float("inf")])
def test_evaluate_live_rows_rejects_nonpositive_or_nonfinite_raw_values(
    tmp_path: Path,
    field: str,
    value: float,
) -> None:
    rows = _accepted_rows()
    rows[0][field] = value

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert f"missing_or_nonpositive_or_nonfinite_raw_value:{field}:Methane:100K" in result["blockers"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("absolute_error_Pa", 0.0),
        ("relative_error_percent", 0.0),
        ("absolute_relative_error_percent", 0.0),
        ("rho_sat_liq_absolute_error_kg_m3", 0.0),
        ("rho_sat_liq_relative_error_percent", 0.0),
        ("rho_sat_liq_absolute_relative_error_percent", 0.0),
    ],
)
def test_evaluate_live_rows_rejects_tampered_stored_error_fields(
    tmp_path: Path,
    field: str,
    value: float,
) -> None:
    rows = _accepted_rows()
    rows[0][field] = value

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert f"stored_error_mismatch:{field}:Methane:100K" in result["blockers"]


@pytest.mark.parametrize(
    "field",
    [
        "absolute_error_Pa",
        "relative_error_percent",
        "absolute_relative_error_percent",
        "rho_sat_liq_absolute_error_kg_m3",
        "rho_sat_liq_relative_error_percent",
        "rho_sat_liq_absolute_relative_error_percent",
    ],
)
def test_evaluate_live_rows_rejects_one_ulp_stored_error_fabrication(
    tmp_path: Path,
    field: str,
) -> None:
    rows = _accepted_rows()
    rows[0][field] = math.nextafter(float(rows[0][field]), math.inf)

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert f"stored_error_mismatch:{field}:Methane:100K" in result["blockers"]


@pytest.mark.parametrize(
    ("field", "value", "blocker"),
    [
        ("solver_tolerance", 1.0e-6, "solver_tolerance_mismatch:Methane:100K"),
        ("max_iterations", 499, "max_iterations_mismatch:Methane:100K"),
    ],
)
def test_evaluate_live_rows_rejects_solver_run_contract_mutation(
    tmp_path: Path,
    field: str,
    value: object,
    blocker: str,
) -> None:
    rows = _accepted_rows()
    rows[0][field] = value

    result = checker.evaluate_live_rows(
        rows,
        native_freshness_receipt=_receipt(tmp_path / "_native.so"),
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert blocker in result["blockers"]


def test_run_live_validation_executes_solver_row_provider_and_records_loaded_native(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    generated = _accepted_rows()
    calls: list[str] = []
    native_path = tmp_path / "live_native.so"
    native_path.write_text("native", encoding="utf-8")
    current_identity = checker.native_freshness.equilibrium_native_source_identity()

    def live_rows() -> list[dict[str, object]]:
        calls.append("live_solver_rows")
        return deepcopy(generated)

    monkeypatch.setattr(checker, "generate_validation_rows", live_rows)
    monkeypatch.setattr(
        checker,
        "extension_native_core",
        lambda: SimpleNamespace(
            __file__=str(native_path),
            __name__="live_native",
            _native_equilibrium_build_identity=lambda: {
                "algorithm": current_identity["algorithm"],
                "source_identity": current_identity["source_identity"],
                "source_scope": current_identity["scope"],
                "source_file_count": current_identity["file_count"],
                "scope_limit": current_identity["scope_limit"],
            },
        ),
    )
    monkeypatch.setattr(checker.native_freshness, "git_commit", lambda: "fedcba9876543210")

    result = checker.run_live_validation(
        checker_command=[
            "python",
            "scripts/validation/check_single_component_vle_nist_saturation.py",
            "--json",
        ],
        require_fresh_native=True,
    )

    assert calls == ["live_solver_rows"]
    assert result["complete"] is True
    assert result["row_count"] == len(generated)
    assert result["native_freshness_receipt"]["git_commit"] == "fedcba9876543210"
    assert result["native_freshness_receipt"]["native_module_path"] == str(native_path.resolve())
    assert result["native_freshness_receipt"]["source_identity_matches"] is True


def test_run_live_validation_rejects_stale_loaded_native_identity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    native_path = tmp_path / "stale_native.so"
    native_path.write_text("native", encoding="utf-8")
    current_identity = checker.native_freshness.equilibrium_native_source_identity()
    monkeypatch.setattr(checker, "generate_validation_rows", _accepted_rows)
    monkeypatch.setattr(
        checker,
        "extension_native_core",
        lambda: SimpleNamespace(
            __file__=str(native_path),
            __name__="stale_native",
            _native_equilibrium_build_identity=lambda: {
                "algorithm": current_identity["algorithm"],
                "source_identity": "0" * 64,
                "source_scope": current_identity["scope"],
                "source_file_count": current_identity["file_count"],
                "scope_limit": current_identity["scope_limit"],
            },
        ),
    )
    monkeypatch.setattr(checker.native_freshness, "git_commit", lambda: "fedcba9876543210")

    result = checker.run_live_validation(
        checker_command=["python", "scripts/validation/check_single_component_vle_nist_saturation.py"],
        require_fresh_native=True,
    )

    assert result["complete"] is False
    assert result["native_freshness_receipt"]["source_identity_matches"] is False
    assert "native_source_identity_mismatch" in result["blockers"]


def test_checker_strict_cli_requires_complete_and_fresh_native_flags() -> None:
    parser = checker.build_parser()
    args = parser.parse_args(["--json", "--require-complete", "--require-fresh-native"])

    assert args.json is True
    assert args.require_complete is True
    assert args.require_fresh_native is True


def test_reusable_live_row_generation_does_not_write_retained_artifacts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    diagnostics = {
        "route_status": "accepted",
        "solver_status": "success",
        "seed_name": "test-seed",
        "phase_distance": 0.25,
        "pressure_consistency_norm": 1.0e-4,
        "chemical_potential_consistency_norm": 1.0e-8,
        "ln_fugacity_consistency_norm": 1.0e-8,
        "exact_hessian_available": True,
        "hessian_approximation": "exact",
        "jacobian_approximation": "exact",
        "hessian_backend": "cppad_phase_pressure_route",
        "eval_h_calls": 4,
    }
    result = SimpleNamespace(
        P_sat=102_000.0,
        vapor_density=20.0,
        liquid_density=10_000.0,
        diagnostics=diagnostics,
    )
    monkeypatch.setattr(generate_data, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(generate_data, "_load_pcsaft_parameters", lambda: {})
    monkeypatch.setattr(generate_data, "_mixture_for_species", lambda species, parameters: object())
    monkeypatch.setattr(
        generate_data,
        "_reference_rows",
        lambda species: [
            {
                "species": species,
                "T_K": "120",
                "p_sat_Pa": "100000",
                "rho_sat_liq_kg_m3": "500",
                "source": NIST_SOURCE_URLS[species],
            }
        ],
    )
    monkeypatch.setattr(
        generate_data.epcsaft_equilibrium,
        "Equilibrium",
        lambda *args, **kwargs: SimpleNamespace(solve=lambda **solve_kwargs: result),
    )

    rows = generate_data.generate_validation_rows()

    assert len(rows) == 3
    for row in rows:
        assert row["exact_hessian_available"] is True
        assert row["hessian_approximation"] == "exact"
        assert row["jacobian_approximation"] == "exact"
        assert row["hessian_backend"] == "cppad_phase_pressure_route"
        assert row["eval_h_calls"] == 4
    assert not tmp_path.exists() or list(tmp_path.iterdir()) == []


def test_generate_validation_rows_rejects_reference_species_join_mutation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    diagnostics = {
        "route_status": "accepted",
        "solver_status": "success",
        "phase_distance": 0.25,
        "pressure_consistency_norm": 1.0e-4,
        "chemical_potential_consistency_norm": 1.0e-8,
        "ln_fugacity_consistency_norm": 1.0e-8,
        "exact_hessian_available": True,
        "hessian_approximation": "exact",
        "jacobian_approximation": "exact",
        "hessian_backend": "cppad_phase_pressure_route",
        "eval_h_calls": 4,
    }
    result = SimpleNamespace(
        P_sat=102_000.0,
        vapor_density=20.0,
        liquid_density=10_000.0,
        diagnostics=diagnostics,
    )
    monkeypatch.setattr(generate_data, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(generate_data, "_load_pcsaft_parameters", lambda: {})
    monkeypatch.setattr(generate_data, "_mixture_for_species", lambda species, parameters: object())

    def mutated_reference_rows(species: str) -> list[dict[str, str]]:
        reference_species = "Ethane" if species == "Methane" else species
        return [
            {
                "species": reference_species,
                "T_K": "120",
                "p_sat_Pa": "100000",
                "rho_sat_liq_kg_m3": "500",
                "source": NIST_SOURCE_URLS[reference_species],
            }
        ]

    monkeypatch.setattr(generate_data, "_reference_rows", mutated_reference_rows)
    monkeypatch.setattr(
        generate_data.epcsaft_equilibrium,
        "Equilibrium",
        lambda *args, **kwargs: SimpleNamespace(solve=lambda **solve_kwargs: result),
    )

    with pytest.raises(RuntimeError, match="reference species mismatch"):
        generate_data.generate_validation_rows()
