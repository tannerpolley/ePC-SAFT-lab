from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

REFERENCE_PATH = Path(__file__).with_name("cantera_pope_reference_cases.json")
SCHEMA_VERSION = "epcsaft.ce_reference_oracles.v1"


def _a_to_b_case(
    *,
    case_id: str,
    source_label: str,
    source_reference: str,
    source_scope_note: str,
    source_constant_label: str,
    log_k: float,
    initial_amounts: list[float],
    amount_tolerance: float,
    affinity_tolerance: float,
) -> dict[str, Any]:
    k_value = math.exp(log_k)
    amount_a = 1.0 / (1.0 + k_value)
    amount_b = k_value / (1.0 + k_value)

    return {
        "case_id": case_id,
        "source": {
            "label": source_label,
            "reference": source_reference,
            "scope_note": source_scope_note,
        },
        "oracle_role": "reference_only",
        "ce_only": True,
        "phase_scope": "homogeneous_single_phase",
        "claimed_equilibrium_scopes": ["standalone_chemical_equilibrium"],
        "species_order": ["A", "B"],
        "reaction_set": {
            "species": [
                {"label": "A", "elements": {"X": 1.0}, "charge": 0.0},
                {"label": "B", "elements": {"X": 1.0}, "charge": 0.0},
            ],
            "reactions": [
                {
                    "label": "a_to_b",
                    "stoichiometry": {"A": -1.0, "B": 1.0},
                }
            ],
            "feed_amounts": {"A": 1.0, "B": 0.0},
        },
        "standard_state_registry": {
            "records": [
                {
                    "reaction_label": "a_to_b",
                    "value": log_k,
                    "form": "ln_K",
                    "units": "dimensionless",
                    "source": source_label,
                    "source_constant_label": source_constant_label,
                    "standard_state": {
                        "label": "mole_fraction_standard_state",
                        "activity_convention": "mole_fraction_activity",
                        "temperature_K": 298.15,
                        "pressure_Pa": 101325.0,
                    },
                }
            ]
        },
        "solver": {
            "name": "closed_form_ideal_gibbs_minimization",
            "method": "ideal mole-fraction mass-action solution",
            "runtime_dependency": "none",
            "compared_runtime_path": "#326 activation-matrix native NLP/Ipopt path",
        },
        "initial_amounts": initial_amounts,
        "expected": {
            "amounts": [amount_a, amount_b],
            "mole_fractions": [amount_a, amount_b],
        },
        "balances": {
            "conservation_labels": ["X"],
            "conservation_totals": [1.0],
            "balance_residuals": [0.0],
            "balance_inf_norm": 0.0,
        },
        "affinities": {
            "reaction_labels": ["a_to_b"],
            "reaction_affinities": [0.0],
            "stationarity_inf_norm": 0.0,
            "convention": "ln(x_B/x_A) - ln_K",
        },
        "tolerances": {
            "amount_abs": amount_tolerance,
            "mole_fraction_abs": amount_tolerance,
            "balance_abs": 1.0e-9,
            "affinity_abs": affinity_tolerance,
        },
    }


def build_reference_payload() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": "standalone_chemical_equilibrium_only",
        "runtime_dependencies": [],
        "generated_by": "analyses/reference_oracles/chemical_equilibrium/generate_reference_cases.py",
        "cases": [
            _a_to_b_case(
                case_id="cantera_compatible_ideal_a_to_b",
                source_label="Cantera-compatible ideal equilibrium fixture",
                source_reference="Cantera ideal chemical-equilibrium documentation pattern",
                source_scope_note="Analytic two-species ideal fixture shaped for Cantera-style element-balance comparison; not a Cantera runtime output.",
                source_constant_label="ln_K_cantera_compatible_fixture",
                log_k=math.log(3.0),
                initial_amounts=[0.5, 0.5],
                amount_tolerance=1.0e-7,
                affinity_tolerance=1.0e-8,
            ),
            _a_to_b_case(
                case_id="pope_2004_tiny_species_ideal_a_to_b",
                source_label="Pope 2004 Gibbs-continuation stress fixture",
                source_reference="Pope 2004 constrained Gibbs chemical-equilibrium continuation method",
                source_scope_note="Analytic ideal tiny-species fixture for continuation-style stress; not a Pope implementation or alternate solve path.",
                source_constant_label="ln_K_tiny_species_fixture",
                log_k=math.log(1.0e-6),
                initial_amounts=[0.999, 0.001],
                amount_tolerance=1.0e-7,
                affinity_tolerance=1.0e-5,
            ),
        ],
    }


def write_reference_payload(path: Path = REFERENCE_PATH) -> None:
    payload = build_reference_payload()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate retained CE reference oracle records.")
    parser.add_argument("--output", type=Path, default=REFERENCE_PATH)
    args = parser.parse_args()
    write_reference_payload(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
