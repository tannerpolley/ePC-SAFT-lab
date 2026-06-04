from __future__ import annotations

import csv
import sys
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyses.package_validation.explicit_association_toybox.scripts.fixed_state_property_residuals import (
    DEFAULT_CASES,
    DEFAULT_SOURCE,
    fixed_state_property_residual_rows,
    load_provider_cases,
    load_public_saturation_rows,
)

OUTPUT = ANALYSIS_ROOT / "figures" / "pressure_density_validation" / "output"
RAW_OUTPUT = OUTPUT / "pressure_density_validation.csv"


def build_pressure_density_validation_rows() -> list[dict[str, object]]:
    source_rows = load_public_saturation_rows(DEFAULT_SOURCE)
    provider_cases = load_provider_cases(DEFAULT_CASES)
    residual_rows = fixed_state_property_residual_rows(source_rows, provider_cases=provider_cases)
    rows: list[dict[str, object]] = []
    for row in residual_rows:
        rows.append(_reference_row(row))
        rows.append(
            _model_row(
                row,
                model_name="exact_implicit",
                model_label="Exact implicit",
                model_role=row["toy_exact_model_role"],
                pressure_key="toy_exact_pressure_at_exp_density_Pa",
                density_key="toy_exact_density_at_exp_pressure_mol_m3",
                root_status_key="toy_exact_density_root_status",
                root_residual_key="toy_exact_density_root_residual_Pa",
                bracket_policy_key="toy_exact_density_bracket_policy",
                pressure_count_key="toy_exact_density_pressure_evaluation_count",
                root_count_key="toy_exact_density_root_bracket_count",
                ares_key="toy_exact_ares_at_exp_density",
                z_key="toy_exact_z_at_exp_density",
            )
        )
        rows.append(
            _model_row(
                row,
                model_name="picard",
                model_label="Picard",
                model_role=row["picard_model_role"],
                pressure_key="picard_pressure_at_exp_density_Pa",
                density_key="picard_density_at_exp_pressure_mol_m3",
                root_status_key="picard_density_root_status",
                root_residual_key="picard_density_root_residual_Pa",
                bracket_policy_key="picard_density_bracket_policy",
                pressure_count_key="picard_density_pressure_evaluation_count",
                root_count_key="picard_density_root_bracket_count",
                ares_key="picard_ares_at_exp_density",
                z_key="picard_z_at_exp_density",
            )
        )
    if not rows:
        raise ValueError("pressure-density validation produced no rows.")
    return rows


def write_pressure_density_validation_rows(rows: list[dict[str, object]], output_path: Path = RAW_OUTPUT) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def _reference_row(row: dict[str, object]) -> dict[str, object]:
    base = _base_row(row)
    base.update(
        {
            "row_role": "reference_data",
            "model_name": "reference_data",
            "model_label": "Data",
            "model_role": "experimental_saturation_data",
            "model_pressure_Pa": row["source_p_sat_Pa"],
            "model_liquid_density_mol_m3": row["source_rho_sat_liq_mol_m3"],
            "pressure_residual_Pa": 0.0,
            "density_residual_mol_m3": 0.0,
            "density_root_status": "reference_data",
            "root_branch": "reference_saturated_liquid_density",
            "density_root_residual_Pa": "",
            "bracket_policy": "",
            "pressure_evaluation_count": "",
            "density_root_bracket_count": "",
            "ares_at_density": "",
            "z_at_density": "",
        }
    )
    return base


def _model_row(
    row: dict[str, object],
    *,
    model_name: str,
    model_label: str,
    model_role: object,
    pressure_key: str,
    density_key: str,
    root_status_key: str,
    root_residual_key: str,
    bracket_policy_key: str,
    pressure_count_key: str,
    root_count_key: str,
    ares_key: str,
    z_key: str,
) -> dict[str, object]:
    reference_pressure = float(row["source_p_sat_Pa"])
    reference_density = float(row["source_rho_sat_liq_mol_m3"])
    model_pressure = _optional_float(row[pressure_key])
    model_density = _optional_float(row[density_key])
    base = _base_row(row)
    base.update(
        {
            "row_role": "model_curve",
            "model_name": model_name,
            "model_label": model_label,
            "model_role": model_role,
            "model_pressure_Pa": "" if model_pressure is None else model_pressure,
            "model_liquid_density_mol_m3": "" if model_density is None else model_density,
            "pressure_residual_Pa": "" if model_pressure is None else model_pressure - reference_pressure,
            "density_residual_mol_m3": "" if model_density is None else model_density - reference_density,
            "density_root_status": row[root_status_key],
            "root_branch": "liquid_density_root_at_reference_pressure",
            "density_root_residual_Pa": row[root_residual_key],
            "bracket_policy": row[bracket_policy_key],
            "pressure_evaluation_count": row[pressure_count_key],
            "density_root_bracket_count": row[root_count_key],
            "ares_at_density": row[ares_key],
            "z_at_density": row[z_key],
        }
    )
    return base


def _base_row(row: dict[str, object]) -> dict[str, object]:
    return {
        "component": row["component"],
        "T_K": row["T_K"],
        "reference_pressure_Pa": row["source_p_sat_Pa"],
        "reference_liquid_density_mol_m3": row["source_rho_sat_liq_mol_m3"],
        "phase": row["phase"],
        "source_url": row["source_url"],
        "parameter_source": row["parameter_source"],
        "saturation_validation_status": row["saturation_validation_status"],
    }


def _optional_float(value: object) -> float | None:
    if value in {"", None}:
        return None
    return float(value)


def main() -> None:
    rows = build_pressure_density_validation_rows()
    output = write_pressure_density_validation_rows(rows)
    print(output)


if __name__ == "__main__":
    main()
