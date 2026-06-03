from __future__ import annotations

import csv
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import numpy as np
from .paper_systems import load_paper_systems, load_provider_property_cases

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ANALYSIS_ROOT / "shared" / "source" / "public_saturation_properties.csv"
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "property_residuals" / "output" / "property_residuals.csv"
DEFAULT_CASES = ANALYSIS_ROOT / "config" / "paper_systems.yaml"
GAS_CONSTANT = 8.31446261815324


ProviderEvaluator = Callable[[dict[str, object], dict[str, object]], dict[str, float]]


def load_public_saturation_rows(path: Path = DEFAULT_SOURCE) -> list[dict[str, object]]:
    if not path.exists():
        raise FileNotFoundError(
            "shared/source/public_saturation_properties.csv is required before fixed-state residual generation: "
            f"{path}"
        )
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key in ("T_K", "p_sat_Pa", "rho_sat_liq_mol_m3"):
            row[key] = float(row[key])
    return rows


def load_provider_cases(path: Path = DEFAULT_CASES) -> dict[str, dict[str, object]]:
    return load_provider_property_cases(path)


def fixed_state_property_residual_rows(
    source_rows: Sequence[Mapping[str, object]],
    *,
    provider_cases: Mapping[str, Mapping[str, object]],
    evaluator: ProviderEvaluator | None = None,
) -> list[dict[str, object]]:
    evaluator = evaluator or _default_provider_evaluator
    rows: list[dict[str, object]] = []
    for raw_row in source_rows:
        row = dict(raw_row)
        component = str(row["component"]).lower()
        case = dict(provider_cases.get(component, {}))
        if not case:
            continue
        evaluated = evaluator(case, row)
        p_exp = float(row["p_sat_Pa"])
        rho_exp = float(row["rho_sat_liq_mol_m3"])
        p_calc = float(evaluated["provider_pressure_at_exp_density_Pa"])
        rho_calc = float(evaluated["provider_density_at_exp_pressure_mol_m3"])
        temperature = float(row["T_K"])
        pressure_residual = p_calc - p_exp
        density_residual = rho_calc - rho_exp
        z_exp = p_exp / (rho_exp * GAS_CONSTANT * temperature)
        z_provider = p_calc / (rho_exp * GAS_CONSTANT * temperature)
        rows.append(
            {
                "property_workflow": "fixed_state_saturation_property_residual",
                "component": component,
                "T_K": temperature,
                "source_p_sat_Pa": p_exp,
                "source_rho_sat_liq_mol_m3": rho_exp,
                "provider_pressure_at_exp_density_Pa": p_calc,
                "provider_density_at_exp_pressure_mol_m3": rho_calc,
                "pressure_absolute_residual_Pa": pressure_residual,
                "pressure_relative_residual": pressure_residual / max(abs(p_exp), 1.0),
                "density_absolute_residual_mol_m3": density_residual,
                "density_relative_residual": density_residual / max(abs(rho_exp), 1.0),
                "pressure_residual_pa": pressure_residual,
                "pressure_residual_mpa": pressure_residual / 1_000_000.0,
                "pressure_residual_rel": pressure_residual / max(abs(p_exp), 1.0),
                "z_experimental": z_exp,
                "z_provider": z_provider,
                "z_residual_abs": abs(z_provider - z_exp),
                "density_residual_abs": density_residual,
                "density_residual_rel": density_residual / max(abs(rho_exp), 1.0),
                "provider_ares_at_exp_density": float(evaluated["provider_ares_at_exp_density"]),
                "phase": str(row.get("phase", "liquid")),
                "source_url": str(row.get("source_url", "")),
                "parameter_source": str(case.get("parameter_source", "inline_provider_case")),
                "status": "ok",
                "message": "",
            }
        )
    if not rows:
        raise ValueError("no public saturation rows matched configured provider cases.")
    return rows


def write_property_residual_csv(rows: list[dict[str, object]], output_path: Path = DEFAULT_OUTPUT) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def generate_property_residuals(
    *,
    source_path: Path = DEFAULT_SOURCE,
    cases_path: Path = DEFAULT_CASES,
    output_path: Path = DEFAULT_OUTPUT,
) -> Path:
    source_rows = load_public_saturation_rows(source_path)
    provider_cases = load_provider_cases(cases_path)
    source_rows = _sample_source_rows(source_rows, cases_path=cases_path)
    rows = fixed_state_property_residual_rows(source_rows, provider_cases=provider_cases)
    return write_property_residual_csv(rows, output_path)


def _default_provider_evaluator(case: dict[str, object], row: dict[str, object]) -> dict[str, float]:
    from epcsaft.state.native_adapter import ePCSAFTMixture

    params = _runtime_params(case)
    species = [str(item) for item in case["species"]]
    x = np.ones(len(species), dtype=float) / float(len(species))
    temperature = float(row["T_K"])
    pressure = float(row["p_sat_Pa"])
    density = float(row["rho_sat_liq_mol_m3"])
    mix = ePCSAFTMixture.from_params(params, species=species)
    density_state = mix.state(T=temperature, x=x, rho=density, phase="liq")
    pressure_state = mix.state(T=temperature, x=x, P=pressure, phase="liq", rho_guess=density)
    return {
        "provider_pressure_at_exp_density_Pa": float(density_state.pressure()),
        "provider_density_at_exp_pressure_mol_m3": float(pressure_state.molar_density()),
        "provider_ares_at_exp_density": float(density_state.ares()),
    }


def _runtime_params(case: Mapping[str, object]) -> dict[str, object]:
    raw = case.get("parameters")
    if not isinstance(raw, Mapping):
        raise ValueError("provider case must include a parameters mapping.")
    params: dict[str, object] = {}
    for key, value in raw.items():
        if key == "assoc_scheme":
            params[key] = list(value) if isinstance(value, list) else [value]
        elif isinstance(value, list):
            params[key] = np.asarray(value, dtype=float)
        else:
            params[key] = np.asarray([value], dtype=float)
    return params


def _sample_source_rows(rows: list[dict[str, object]], *, cases_path: Path) -> list[dict[str, object]]:
    data = load_paper_systems(cases_path)
    sampling = data.get("property_residual_sampling", {})
    if not isinstance(sampling, Mapping) or "max_rows_per_component" not in sampling:
        return rows
    max_rows = int(sampling["max_rows_per_component"])
    if max_rows <= 0:
        raise ValueError("property_residual_sampling.max_rows_per_component must be positive.")
    counts: dict[str, int] = {}
    selected: list[dict[str, object]] = []
    for row in rows:
        component = str(row["component"]).lower()
        count = counts.get(component, 0)
        if count >= max_rows:
            continue
        selected.append(row)
        counts[component] = count + 1
    return selected
