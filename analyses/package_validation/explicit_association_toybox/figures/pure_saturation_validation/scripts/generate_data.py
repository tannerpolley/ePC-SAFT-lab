from __future__ import annotations

import csv
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.closure_models import (
    EXACT_MASS_ACTION_BASELINE,
    PICARD7_CLOSURE,
)
from analyses.package_validation.explicit_association_toybox.scripts.fixed_state_property_residuals import (
    DEFAULT_CASES,
    DEFAULT_SOURCE,
    load_provider_cases,
    load_public_saturation_rows,
)
from analyses.package_validation.explicit_association_toybox.scripts.pure_saturation import (
    PureSaturationResult,
    solve_pure_saturation,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "pure_saturation_validation" / "output"
RAW_OUTPUT = OUTPUT / "pure_saturation_validation.csv"

REQUIRED_RETAINED_COLUMNS = (
    "component",
    "T_K",
    "reference_p_sat_Pa",
    "reference_rho_liq_mol_m3",
    "row_role",
    "closure_name",
    "model_label",
    "model_role",
    "model_p_sat_Pa",
    "model_rho_vap_mol_m3",
    "model_rho_liq_mol_m3",
    "pressure_vap_residual_Pa",
    "pressure_liq_residual_Pa",
    "log_fugacity_residual",
    "solver_status",
    "solver_iteration_count",
    "pressure_evaluation_count",
    "initial_guess_policy",
    "parameter_source",
    "source_url",
    "message",
)


def build_pure_saturation_validation_rows(
    source_rows: Sequence[Mapping[str, object]],
    *,
    provider_cases: Mapping[str, Mapping[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for raw_row in source_rows:
        source_row = dict(raw_row)
        component = str(source_row["component"]).lower()
        case = provider_cases.get(component)
        if case is None:
            continue
        rows.append(_reference_row(source_row, case))
        for closure_name, label in (
            (EXACT_MASS_ACTION_BASELINE, "Exact implicit"),
            (PICARD7_CLOSURE, "Picard"),
        ):
            rows.append(_model_row(source_row, case, closure_name=closure_name, model_label=label))
    if not rows:
        raise ValueError("pure saturation validation produced no retained rows.")
    return rows


def write_pure_saturation_validation_rows(
    rows: list[dict[str, object]],
    output_path: Path = RAW_OUTPUT,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(REQUIRED_RETAINED_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def generate_pure_saturation_validation_rows(
    *,
    source_path: Path = DEFAULT_SOURCE,
    cases_path: Path = DEFAULT_CASES,
    output_path: Path = RAW_OUTPUT,
) -> Path:
    source_rows = load_public_saturation_rows(source_path)
    provider_cases = load_provider_cases(cases_path)
    rows = build_pure_saturation_validation_rows(source_rows, provider_cases=provider_cases)
    return write_pure_saturation_validation_rows(rows, output_path)


def _reference_row(source_row: Mapping[str, object], case: Mapping[str, object]) -> dict[str, object]:
    row = _base_row(source_row, case)
    row.update(
        {
            "row_role": "reference_data",
            "closure_name": "reference_data",
            "model_label": "Data",
            "model_role": "experimental_saturation_data",
            "model_p_sat_Pa": float(source_row["p_sat_Pa"]),
            "model_rho_vap_mol_m3": "",
            "model_rho_liq_mol_m3": float(source_row["rho_sat_liq_mol_m3"]),
            "pressure_vap_residual_Pa": "",
            "pressure_liq_residual_Pa": "",
            "log_fugacity_residual": "",
            "solver_status": "reference_data",
            "solver_iteration_count": "",
            "pressure_evaluation_count": "",
            "initial_guess_policy": "",
            "message": "Reference saturation row retained from public source data.",
        }
    )
    return row


def _model_row(
    source_row: Mapping[str, object],
    case: Mapping[str, object],
    *,
    closure_name: str,
    model_label: str,
) -> dict[str, object]:
    row = _base_row(source_row, case)
    try:
        result = solve_pure_saturation(
            case,
            temperature=float(source_row["T_K"]),
            closure_name=closure_name,
            pressure_seed_Pa=float(source_row["p_sat_Pa"]),
            liquid_density_seed_mol_m3=float(source_row["rho_sat_liq_mol_m3"]),
        )
        row.update(_result_fields(result))
    except Exception as exc:
        row.update(_failure_fields(closure_name=closure_name, model_label=model_label, message=str(exc)))
        return row
    row["row_role"] = "model_curve"
    row["model_label"] = model_label
    return row


def _base_row(source_row: Mapping[str, object], case: Mapping[str, object]) -> dict[str, object]:
    return {
        "component": str(source_row["component"]).lower(),
        "T_K": float(source_row["T_K"]),
        "reference_p_sat_Pa": float(source_row["p_sat_Pa"]),
        "reference_rho_liq_mol_m3": float(source_row["rho_sat_liq_mol_m3"]),
        "parameter_source": str(case.get("parameter_source", "inline_provider_case")),
        "source_url": str(source_row.get("source_url", "")),
    }


def _result_fields(result: PureSaturationResult) -> dict[str, object]:
    return {
        "closure_name": result.closure_name,
        "model_role": result.model_role,
        "model_p_sat_Pa": result.p_sat_Pa,
        "model_rho_vap_mol_m3": result.rho_vap_mol_m3,
        "model_rho_liq_mol_m3": result.rho_liq_mol_m3,
        "pressure_vap_residual_Pa": result.pressure_vap_residual_Pa,
        "pressure_liq_residual_Pa": result.pressure_liq_residual_Pa,
        "log_fugacity_residual": result.log_fugacity_residual,
        "solver_status": result.status,
        "solver_iteration_count": result.solver_iteration_count,
        "pressure_evaluation_count": result.pressure_evaluation_count,
        "initial_guess_policy": result.initial_guess_policy,
        "message": result.message,
    }


def _failure_fields(*, closure_name: str, model_label: str, message: str) -> dict[str, object]:
    return {
        "row_role": "solver_failure",
        "closure_name": closure_name,
        "model_label": model_label,
        "model_role": _model_role(closure_name),
        "model_p_sat_Pa": "",
        "model_rho_vap_mol_m3": "",
        "model_rho_liq_mol_m3": "",
        "pressure_vap_residual_Pa": "",
        "pressure_liq_residual_Pa": "",
        "log_fugacity_residual": "",
        "solver_status": "pure_saturation_solver_failed",
        "solver_iteration_count": "",
        "pressure_evaluation_count": "",
        "initial_guess_policy": "",
        "message": message,
    }


def _model_role(closure_name: str) -> str:
    if closure_name == EXACT_MASS_ACTION_BASELINE:
        return "toy_pcsaft_exact_implicit_association"
    if closure_name == PICARD7_CLOSURE:
        return "toy_pcsaft_picard_association"
    return f"toy_pcsaft_{closure_name}"


def main() -> None:
    output = generate_pure_saturation_validation_rows()
    print(output)


if __name__ == "__main__":
    main()
