from __future__ import annotations

import argparse
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np

from .derivative_agreement import (
    _target_derivative,
    pressure_proxy_from_ares,
)
from .dispersion import ares_disp as dispersion_ares
from .dispersion import mixed_dispersion_moments
from .hard_chain import ares_hc as hard_chain_ares
from .hard_chain import hard_chain_state
from .pcsaft_inputs import ToyPCSAFTState
from .propagation_evidence import (
    classify_propagated_evidence_band,
    closure_association_value,
    exact_association_value,
    load_propagation_thresholds,
    mass_residual_inf,
    relative_error,
    write_rows_csv,
)
from .topology_reductions import topology_system

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "total_eos_impact" / "output" / "total_eos_impact.csv"
DEFAULT_CLOSURES = ("damped_picard_3_05", "damped_picard_5_05", "damped_picard_7_05", "picard3_diag_newton1")


def summarize_total_eos_impact(samples: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for sample in samples:
        row = dict(sample)
        exact_elapsed = float(row["exact_implicit_elapsed_seconds"])
        closure_elapsed = float(row["closure_elapsed_seconds"])
        row["speedup_vs_exact_implicit"] = exact_elapsed / closure_elapsed if closure_elapsed > 0.0 else np.nan
        rows.append(row)
    return rows


def run_total_eos_impact(*, closure_names: Iterable[str] = DEFAULT_CLOSURES) -> list[dict[str, object]]:
    thresholds = load_propagation_thresholds()
    samples: list[dict[str, object]] = []
    for case in _impact_cases():
        system = topology_system(str(case["topology_id"]))
        composition = np.array([1.0], dtype=float)
        density = float(case["association_density"])
        strength = float(case["association_strength"])
        delta = system.delta_matrix(strength)
        pcsaft_state = _pcsaft_state(float(case["temperature"]), float(case["pcsaft_density"]))
        hc = hard_chain_state(pcsaft_state)
        ares_hc_value = hard_chain_ares(pcsaft_state, hc)
        ares_disp_value = dispersion_ares(pcsaft_state, hc, mixed_dispersion_moments(pcsaft_state))
        exact, exact_assoc, exact_elapsed = exact_association_value(
            system=system,
            density=density,
            composition=composition,
            delta=delta,
        )
        exact_total = ares_hc_value + ares_disp_value + exact_assoc
        exact_density_slope = _target_derivative(
            "a_assoc_density",
            exact=True,
            closure_name="damped_picard_3_05",
            system=system,
            density=density,
            strength=strength,
            composition=composition,
        )
        exact_pressure_proxy = pressure_proxy_from_ares(
            density=density,
            ares_value=exact_total,
            density_slope=exact_density_slope,
        )
        for closure_name in closure_names:
            closure, closure_assoc, closure_elapsed = closure_association_value(
                closure_name,
                system=system,
                density=density,
                composition=composition,
                delta=delta,
            )
            closure_total = ares_hc_value + ares_disp_value + closure_assoc
            closure_density_slope = _target_derivative(
                "a_assoc_density",
                exact=False,
                closure_name=closure_name,
                system=system,
                density=density,
                strength=strength,
                composition=composition,
            )
            closure_pressure_proxy = pressure_proxy_from_ares(
                density=density,
                ares_value=closure_total,
                density_slope=closure_density_slope,
            )
            assoc_rel = relative_error(closure_assoc, exact_assoc)
            total_rel = relative_error(closure_total, exact_total)
            pressure_rel = relative_error(closure_pressure_proxy, exact_pressure_proxy)
            residual = mass_residual_inf(closure, system=system, density=density, composition=composition, delta=delta)
            speedup = exact_elapsed / closure_elapsed if closure_elapsed > 0.0 else np.nan
            mu_error = abs(closure_density_slope - exact_density_slope)
            fugacity_error = abs(np.exp(np.clip(closure_density_slope, -50.0, 50.0)) - np.exp(np.clip(exact_density_slope, -50.0, 50.0)))
            samples.append(
                {
                    "case_id": case["case_id"],
                    "topology_id": case["topology_id"],
                    "closure_name": closure_name,
                    "ares_assoc_rel_error": assoc_rel,
                    "ares_total_abs_error": abs(closure_total - exact_total),
                    "ares_total_rel_error": total_rel,
                    "pressure_proxy_abs_error": abs(closure_pressure_proxy - exact_pressure_proxy),
                    "pressure_proxy_rel_error": pressure_rel,
                    "mu_proxy_max_abs_error": mu_error,
                    "fugacity_proxy_max_abs_error": fugacity_error,
                    "exact_implicit_elapsed_seconds": exact_elapsed,
                    "closure_elapsed_seconds": closure_elapsed,
                    "speedup_vs_exact_implicit": speedup,
                    "exact_iteration_count": exact.iteration_count,
                    "evidence_band": classify_propagated_evidence_band(
                        association_model=closure.association_model,
                        assoc_ares_rel_error=assoc_rel,
                        derivative_rel_error=relative_error(closure_density_slope, exact_density_slope),
                        property_rel_error=max(total_rel, pressure_rel),
                        mass_action_residual_inf=residual,
                        speedup_vs_exact_implicit=speedup,
                        information_loss=closure.information_loss,
                        thresholds=thresholds,
                    ),
                }
            )
    return summarize_total_eos_impact(samples)


def generate_total_eos_impact(output_path: Path = DEFAULT_OUTPUT) -> Path:
    return write_rows_csv(run_total_eos_impact(), output_path)


def _pcsaft_state(temperature: float, density: float) -> ToyPCSAFTState:
    return ToyPCSAFTState(
        temperature=temperature,
        density=density,
        composition=np.array([1.0], dtype=float),
        segments=np.array([1.5], dtype=float),
        sigma=np.array([3.0], dtype=float),
        epsilon_over_k=np.array([200.0], dtype=float),
        k_ij=np.zeros((1, 1), dtype=float),
    )


def _impact_cases() -> tuple[dict[str, object], ...]:
    return (
        {
            "case_id": "pure_2b_low_total_context",
            "topology_id": "2B",
            "association_density": 0.03,
            "association_strength": 4.0,
            "temperature": 303.15,
            "pcsaft_density": 0.012,
        },
        {
            "case_id": "pure_3b_moderate_total_context",
            "topology_id": "3B",
            "association_density": 0.05,
            "association_strength": 10.0,
            "temperature": 323.15,
            "pcsaft_density": 0.014,
        },
        {
            "case_id": "pure_4c_moderate_total_context",
            "topology_id": "4C",
            "association_density": 0.05,
            "association_strength": 10.0,
            "temperature": 323.15,
            "pcsaft_density": 0.014,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank total EOS impact for explicit association closures.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(generate_total_eos_impact(args.output))


if __name__ == "__main__":
    main()
