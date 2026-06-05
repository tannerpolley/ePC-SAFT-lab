from __future__ import annotations

import csv
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import numpy as np
from .closure_models import EXACT_MASS_ACTION_BASELINE, PICARD7_CLOSURE
from .paper_systems import load_provider_property_cases
from .toy_property_eos import evaluate_toy_property_coupling

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
REFERENCE_SOURCE_DIR = REPO_ROOT / "data" / "reference" / "pure_component" / "saturation_density"
DEFAULT_SOURCE = REFERENCE_SOURCE_DIR / "water_methanol_nist_saturation.csv"
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "property_residuals" / "output" / "property_residuals.csv"
DEFAULT_CASES = ANALYSIS_ROOT / "config" / "paper_systems.yaml"
GAS_CONSTANT = 8.31446261815324


ProviderEvaluator = Callable[[dict[str, object], dict[str, object]], dict[str, float]]


def load_public_saturation_rows(path: Path = DEFAULT_SOURCE) -> list[dict[str, object]]:
    if not path.exists():
        raise FileNotFoundError(
            "data/reference/pure_component/saturation_density/water_methanol_nist_saturation.csv "
            "is required before fixed-state residual generation: "
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
        exact_toy = evaluate_toy_property_coupling(case, row, closure_name=EXACT_MASS_ACTION_BASELINE)
        picard_toy = evaluate_toy_property_coupling(case, row, closure_name=PICARD7_CLOSURE)
        pressure_residual = p_calc - p_exp
        density_residual = rho_calc - rho_exp
        toy_exact_pressure_residual = exact_toy.pressure_at_density_Pa - p_exp
        toy_picard_pressure_residual = picard_toy.pressure_at_density_Pa - p_exp
        z_exp = p_exp / (rho_exp * GAS_CONSTANT * temperature)
        z_provider = p_calc / (rho_exp * GAS_CONSTANT * temperature)
        rows.append(
            {
                "property_workflow": "fixed_state_provider_property_residual",
                "source_role": "experimental_saturation_data",
                "model_role": "provider_fixed_state_probe",
                "saturation_validation_status": str(
                    case.get("saturation_validation_status", "fixed_state_diagnostic")
                ),
                "component": component,
                "T_K": temperature,
                "source_p_sat_Pa": p_exp,
                "source_rho_sat_liq_mol_m3": rho_exp,
                "pressure_probe_input": "experimental_saturated_liquid_density",
                "density_inverse_input": "experimental_saturation_pressure",
                "pressure_probe_status": "computed",
                "density_inverse_status": "computed_provider_density_root",
                "provider_pressure_at_exp_density_Pa": p_calc,
                "provider_density_at_exp_pressure_mol_m3": rho_calc,
                "exact_implicit_pressure_at_exp_density_Pa": p_calc,
                "exact_implicit_density_at_exp_pressure_mol_m3": rho_calc,
                "toy_exact_model_role": exact_toy.model_role,
                "toy_exact_pressure_at_exp_density_Pa": exact_toy.pressure_at_density_Pa,
                "toy_exact_density_at_exp_pressure_mol_m3": _optional_root_value(
                    exact_toy.density_root.rho_mol_m3
                ),
                "toy_exact_density_root_status": exact_toy.density_root.status,
                "toy_exact_density_initial_guess_mol_m3": exact_toy.density_root.initial_guess_mol_m3,
                "toy_exact_density_initial_guess_policy": exact_toy.density_root.initial_guess_policy,
                "toy_exact_density_bracket_policy": exact_toy.density_root.bracket_policy,
                "toy_exact_density_pressure_evaluation_count": exact_toy.density_root.pressure_evaluation_count,
                "toy_exact_density_root_residual_Pa": _optional_root_value(exact_toy.density_root.residual_Pa),
                "toy_exact_density_root_bracket_count": exact_toy.density_root.bracket_count,
                "toy_exact_pressure_residual_Pa": toy_exact_pressure_residual,
                "toy_exact_density_residual_mol_m3": _optional_residual(
                    exact_toy.density_root.rho_mol_m3, rho_exp
                ),
                "toy_exact_ares_at_exp_density": exact_toy.ares_at_density,
                "toy_exact_z_at_exp_density": exact_toy.z_at_density,
                "toy_exact_z_ideal": exact_toy.z_terms.ideal,
                "toy_exact_z_hard_chain": exact_toy.z_terms.hard_chain,
                "toy_exact_z_dispersion": exact_toy.z_terms.dispersion,
                "toy_exact_z_association": exact_toy.z_terms.association,
                "picard_model_role": picard_toy.model_role,
                "picard_output_status": "computed_toy_pressure_density_coupling",
                "picard_message": "Toy PC-SAFT pressure-density coupling computed with seven damped Picard site-fraction updates.",
                "picard_pressure_at_exp_density_Pa": picard_toy.pressure_at_density_Pa,
                "picard_density_at_exp_pressure_mol_m3": _optional_root_value(
                    picard_toy.density_root.rho_mol_m3
                ),
                "picard_density_root_status": picard_toy.density_root.status,
                "picard_density_initial_guess_mol_m3": picard_toy.density_root.initial_guess_mol_m3,
                "picard_density_initial_guess_policy": picard_toy.density_root.initial_guess_policy,
                "picard_density_bracket_policy": picard_toy.density_root.bracket_policy,
                "picard_density_pressure_evaluation_count": picard_toy.density_root.pressure_evaluation_count,
                "picard_density_root_residual_Pa": _optional_root_value(picard_toy.density_root.residual_Pa),
                "picard_density_root_bracket_count": picard_toy.density_root.bracket_count,
                "picard_pressure_residual_Pa": toy_picard_pressure_residual,
                "picard_density_residual_mol_m3": _optional_residual(
                    picard_toy.density_root.rho_mol_m3, rho_exp
                ),
                "picard_ares_at_exp_density": picard_toy.ares_at_density,
                "picard_z_at_exp_density": picard_toy.z_at_density,
                "picard_z_ideal": picard_toy.z_terms.ideal,
                "picard_z_hard_chain": picard_toy.z_terms.hard_chain,
                "picard_z_dispersion": picard_toy.z_terms.dispersion,
                "picard_z_association": picard_toy.z_terms.association,
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
                "message": "Provider state probes use experimental saturated liquid density or pressure; no coexistence solve is performed.",
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


def _optional_residual(value: object, reference: float) -> object:
    if value in {"", None}:
        return ""
    return float(value) - reference


def _optional_root_value(value: float | None) -> object:
    return "" if value is None else float(value)


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
