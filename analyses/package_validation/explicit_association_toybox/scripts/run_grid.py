from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Iterable
from pathlib import Path

import numpy as np
import yaml

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from analyses.package_validation.explicit_association_toybox.scripts.association_models import AssociationSystem
    from analyses.package_validation.explicit_association_toybox.scripts.closure_models import evaluate_closure
    from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import solve_exact_site_fractions
    from analyses.package_validation.explicit_association_toybox.scripts.metrics import metric_row, timed_closure
else:
    from .association_models import AssociationSystem
    from .closure_models import evaluate_closure
    from .exact_baseline import solve_exact_site_fractions
    from .metrics import metric_row, timed_closure

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "closure_accuracy" / "output" / "closure_metrics.csv"


def _load_yaml(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping.")
    return data


def _system_from_config(config: dict[str, object]) -> AssociationSystem:
    return AssociationSystem(
        component_count=int(config["component_count"]),
        site_component_index=np.array(config["site_component_index"], dtype=int),
        site_kind=tuple(str(value) for value in config["site_kind"]),
        active_pairs=tuple(tuple(int(item) for item in pair) for pair in config["active_pairs"]),
    )


def _closure_applies(closure_name: str, system: AssociationSystem) -> bool:
    if closure_name == "closure_2b_exact_reduction":
        return system.site_count == 2 and tuple(system.site_kind) == ("D", "A")
    return True


def run_grid(
    *,
    output_path: Path = DEFAULT_OUTPUT,
    system_names: Iterable[str] | None = None,
    closure_names: Iterable[str] | None = None,
) -> Path:
    systems_doc = _load_yaml(ANALYSIS_ROOT / "config" / "systems.yaml")
    closures_doc = _load_yaml(ANALYSIS_ROOT / "config" / "closure_sweep.yaml")
    systems = systems_doc["systems"]
    closures = closures_doc["closures"]
    thresholds = closures_doc["evidence_bands"]
    if not isinstance(systems, dict) or not isinstance(closures, list) or not isinstance(thresholds, dict):
        raise ValueError("toybox configuration has an invalid schema.")
    selected_systems = set(system_names) if system_names is not None else set(systems)
    selected_closures = set(closure_names) if closure_names is not None else {str(closure["name"]) for closure in closures}
    rows: list[dict[str, object]] = []
    for system_name, raw_system_config in systems.items():
        if system_name not in selected_systems:
            continue
        if not isinstance(raw_system_config, dict):
            raise ValueError(f"{system_name} must be a mapping.")
        system = _system_from_config(raw_system_config)
        for composition_values in raw_system_config["composition_grid"]:
            composition = np.array(composition_values, dtype=float)
            for density in raw_system_config["density_grid"]:
                for strength in raw_system_config["strength_grid"]:
                    delta = system.delta_matrix(float(strength))
                    exact = solve_exact_site_fractions(
                        density=float(density),
                        x_assoc=system.x_assoc(composition),
                        delta=delta,
                    )
                    for closure_config in closures:
                        closure_name = str(closure_config["name"])
                        if closure_name not in selected_closures:
                            continue
                        if not _closure_applies(closure_name, system):
                            continue
                        closure, elapsed = timed_closure(
                            lambda closure_name=closure_name: evaluate_closure(
                                closure_name,
                                system=system,
                                density=float(density),
                                composition=composition,
                                delta=delta,
                            )
                        )
                        rows.append(
                            metric_row(
                                system_name=str(system_name),
                                system=system,
                                density=float(density),
                                strength=float(strength),
                                composition=composition,
                                delta=delta,
                                exact=exact,
                                closure=closure,
                                thresholds=thresholds,
                                elapsed_seconds=elapsed,
                            )
                        )
    if not rows:
        raise ValueError("grid selection produced no rows.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run explicit association closure accuracy grids.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    path = run_grid(output_path=args.output)
    print(path)


if __name__ == "__main__":
    main()
