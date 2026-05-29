from __future__ import annotations

from collections.abc import Mapping, Sequence
from numbers import Real
import os
from time import perf_counter
from typing import Any

import pytest

import epcsaft
from epcsaft_equilibrium._native import extension_native_core

_core = extension_native_core()
import epcsaft_equilibrium
from equilibrium_support.hydrocarbon_cases import (
    HYDROCARBON_BUBBLE_P,
    HYDROCARBON_FLASH_Z,
    HYDROCARBON_LIQUID_RHO,
    HYDROCARBON_LIQUID_X,
    HYDROCARBON_T,
    HYDROCARBON_VAPOR_RHO,
    HYDROCARBON_VAPOR_Y,
    hydrocarbon_parameter_set,
)


ROUTE_CASES: tuple[tuple[str, dict[str, Any], str, str], ...] = (
    (
        "bubble_pressure",
        {"T": HYDROCARBON_T, "x": HYDROCARBON_LIQUID_X},
        "neutral_bubble_p",
        "bubble_dew_derived_routes",
    ),
    (
        "bubble_temperature",
        {"P": HYDROCARBON_BUBBLE_P, "x": HYDROCARBON_LIQUID_X},
        "neutral_bubble_t",
        "bubble_dew_derived_routes",
    ),
    (
        "dew_pressure",
        {"T": HYDROCARBON_T, "y": HYDROCARBON_VAPOR_Y},
        "neutral_dew_p",
        "bubble_dew_derived_routes",
    ),
    (
        "dew_temperature",
        {"P": HYDROCARBON_BUBBLE_P, "y": HYDROCARBON_VAPOR_Y},
        "neutral_dew_t",
        "bubble_dew_derived_routes",
    ),
    (
        "flash",
        {"T": HYDROCARBON_T, "P": HYDROCARBON_BUBBLE_P, "z": HYDROCARBON_FLASH_Z},
        "neutral_tp_flash",
        "neutral_tp_flash",
    ),
)

ROUTE_REPORT_SPECS: Mapping[str, Mapping[str, str]] = {
    "bubble_pressure": {
        "knowns": "T, fixed liquid composition x",
        "unknowns": "P, vapor composition y, liquid/vapor phase volumes",
        "composition_role": "liquid",
        "activation_key": "bubble_dew_derived_routes",
        "fixed_composition": "x",
        "feed_basis": "not a feed route; the native feed vector is reconstructed from solved phase amounts",
    },
    "bubble_temperature": {
        "knowns": "P, fixed liquid composition x",
        "unknowns": "T, vapor composition y, liquid/vapor phase volumes",
        "composition_role": "liquid",
        "activation_key": "bubble_dew_derived_routes",
        "fixed_composition": "x",
        "feed_basis": "not a feed route; the native feed vector is reconstructed from solved phase amounts",
    },
    "dew_pressure": {
        "knowns": "T, fixed vapor composition y",
        "unknowns": "P, liquid composition x, liquid/vapor phase volumes",
        "composition_role": "vapor",
        "activation_key": "bubble_dew_derived_routes",
        "fixed_composition": "y",
        "feed_basis": "not a feed route; the native feed vector is reconstructed from solved phase amounts",
    },
    "dew_temperature": {
        "knowns": "P, fixed vapor composition y",
        "unknowns": "T, liquid composition x, liquid/vapor phase volumes",
        "composition_role": "vapor",
        "activation_key": "bubble_dew_derived_routes",
        "fixed_composition": "y",
        "feed_basis": "not a feed route; the native feed vector is reconstructed from solved phase amounts",
    },
    "flash": {
        "knowns": "T, P, feed composition z",
        "unknowns": "liquid composition x, vapor composition y, phase amounts, liquid/vapor phase volumes",
        "composition_role": "feed",
        "activation_key": "neutral_tp_flash",
        "fixed_composition": "z",
        "feed_basis": "input feed composition z",
    },
}


def _mixture() -> epcsaft.Mixture:
    return epcsaft.Mixture(hydrocarbon_parameter_set())


def _solver_options() -> dict[str, object]:
    options = {
        "max_iterations": 200,
        "tolerance": 1.0e-8,
        "ipopt_iteration_history_limit": 4,
    }
    if _equilibrium_debug_enabled():
        options["ipopt_print_level"] = 5
        options["ipopt_iteration_history_limit"] = 50
    return options


def _equilibrium_debug_enabled() -> bool:
    return os.environ.get("EPCSAFT_EQUILIBRIUM_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


def _format_vector(values: Sequence[object]) -> str:
    if all(isinstance(value, Real) and not isinstance(value, bool) for value in values):
        return "[" + ", ".join(f"{float(value):.12g}" for value in values) + "]"
    return "[" + ", ".join(str(value) for value in values) + "]"


def _to_report_sequence(value: object) -> Sequence[object] | None:
    if isinstance(value, (list, tuple)):
        return value
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        converted = tolist()
        if isinstance(converted, (list, tuple)):
            return tuple(converted)
    return None


def _format_value(value: object) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, Real):
        return f"{float(value):.12g}"
    sequence = _to_report_sequence(value)
    if sequence is not None:
        return _format_vector(sequence)
    return str(value)


def _sequence_item(values: object, index: int) -> object:
    if isinstance(values, (list, tuple)) and index < len(values):
        return values[index]
    return None


def _print_section(title: str) -> None:
    print("\n" + "=" * 96)
    print(title)
    print("=" * 96)


def _print_key_values(title: str, rows: Sequence[tuple[str, object]]) -> None:
    print(f"\n{title}")
    label_width = max(len(label) for label, _value in rows)
    for label, value in rows:
        print(f"  {label:<{label_width}} : {_format_value(value)}")


def _print_table(title: str, columns: Sequence[str], rows: Sequence[Sequence[object]]) -> None:
    print(f"\n{title}")
    string_rows = [[_format_value(value) for value in row] for row in rows]
    widths = [
        max(len(column), *(len(row[index]) for row in string_rows))
        for index, column in enumerate(columns)
    ]
    print("  " + " | ".join(column.ljust(width) for column, width in zip(columns, widths)))
    print("  " + "-+-".join("-" * width for width in widths))
    for row in string_rows:
        print("  " + " | ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


def _composition_input(kwargs: Mapping[str, Any]) -> tuple[str, object]:
    for key in ("x", "y", "z"):
        if key in kwargs:
            return key, kwargs[key]
    return "composition", None


def _print_constraint_report(diagnostics: Mapping[str, Any]) -> None:
    constraints = diagnostics.get("constraints", ())
    families = diagnostics.get("constraint_families", ())
    if not isinstance(constraints, (list, tuple)):
        return

    rows: list[tuple[object, ...]] = []
    families_match_rows = isinstance(families, (list, tuple)) and len(families) == len(constraints)
    for index, residual in enumerate(constraints):
        family = _sequence_item(families, index) if families_match_rows else "active constraint row"
        rows.append((f"c[{index}]", family, residual, abs(float(residual))))

    _print_table(
        "Constraint residual rows",
        ("row", "constraint family", "residual", "absolute residual"),
        rows,
    )


def _print_seed_attempts(diagnostics: Mapping[str, Any]) -> None:
    _print_key_values(
        "Initialization and seed sweep",
        (
            ("initial point strategy", diagnostics.get("initial_point_strategy")),
            ("selected seed", diagnostics.get("seed_name")),
            ("full initial vector exposed", "no; native diagnostics report seed names and attempt outcomes"),
            ("seed attempt count", diagnostics.get("seed_attempt_count")),
            ("route-accepted attempts", diagnostics.get("seed_attempt_route_accepted_count")),
            ("solver-accepted attempts", diagnostics.get("seed_attempt_solver_accepted_count")),
            ("warm start requested", diagnostics.get("warm_start_requested")),
            ("warm start used", diagnostics.get("warm_start_used")),
        ),
    )

    seed_attempts = diagnostics.get("seed_attempts", ())
    if not isinstance(seed_attempts, (list, tuple)) or not seed_attempts:
        return

    rows: list[tuple[object, ...]] = []
    for attempt in seed_attempts:
        if not isinstance(attempt, Mapping):
            continue
        rows.append(
            (
                attempt.get("seed_name"),
                attempt.get("selected_seed"),
                attempt.get("accepted"),
                attempt.get("route_status"),
                attempt.get("solver_status"),
                attempt.get("iteration_count"),
                attempt.get("objective"),
                attempt.get("pressure_consistency_norm"),
                attempt.get("chemical_potential_consistency_norm"),
                attempt.get("phase_distance"),
            )
        )

    _print_table(
        "Seed attempts",
        (
            "seed",
            "selected",
            "accepted",
            "route status",
            "solver status",
            "iters",
            "objective",
            "P norm",
            "mu norm",
            "distance",
        ),
        rows,
    )


def _print_tpd_candidate_report(diagnostics: Mapping[str, Any]) -> None:
    certification = diagnostics.get("postsolve_certification", {})
    if not isinstance(certification, Mapping):
        certification = {}
    _print_key_values(
        "TPD phase-discovery diagnostics",
        (
            ("phase discovery backend", certification.get("phase_discovery_backend")),
            ("deterministic screening status", certification.get("deterministic_screening_status")),
            ("continuous TPD status", certification.get("continuous_tpd_status")),
            ("continuous TPD backend", certification.get("continuous_tpd_backend")),
            ("continuous TPD starts", certification.get("continuous_tpd_start_count")),
            ("continuous TPD solves", certification.get("continuous_tpd_solve_count")),
            ("continuous TPD converged", certification.get("continuous_tpd_converged_count")),
            ("continuous TPD max iterations", certification.get("continuous_tpd_iteration_count_max")),
            ("continuous TPD final step max", certification.get("continuous_tpd_step_final_max")),
            ("HELD Stage I status", certification.get("held_stage_i_status")),
            ("HELD Stage II status", certification.get("held_stage_ii_status")),
            ("HELD Stage III status", certification.get("held_stage_iii_status")),
        ),
    )

    sources = _to_report_sequence(diagnostics.get("tpd_candidate_sources"))
    if not sources:
        return

    values = _to_report_sequence(diagnostics.get("tpd_candidate_values")) or ()
    phase_kinds = _to_report_sequence(diagnostics.get("tpd_candidate_phase_kinds")) or ()
    compositions = _to_report_sequence(diagnostics.get("tpd_candidate_compositions")) or ()
    pressure_residuals = _to_report_sequence(diagnostics.get("tpd_candidate_pressure_residuals")) or ()
    iteration_counts = _to_report_sequence(diagnostics.get("tpd_candidate_iteration_counts")) or ()
    step_finals = _to_report_sequence(diagnostics.get("tpd_candidate_step_finals")) or ()
    ranks = _to_report_sequence(diagnostics.get("tpd_candidate_ranks")) or ()
    feasibility = _to_report_sequence(diagnostics.get("tpd_candidate_feasibility_statuses")) or ()
    selected = _to_report_sequence(diagnostics.get("tpd_candidate_selected")) or ()

    rows: list[tuple[object, ...]] = []
    for index, source in enumerate(sources):
        rows.append(
            (
                _sequence_item(ranks, index),
                source,
                _sequence_item(selected, index),
                _sequence_item(phase_kinds, index),
                _sequence_item(values, index),
                _sequence_item(iteration_counts, index),
                _sequence_item(step_finals, index),
                _sequence_item(pressure_residuals, index),
                _sequence_item(feasibility, index),
                _sequence_item(compositions, index),
            )
        )
    _print_table(
        "TPD candidate rows",
        (
            "rank",
            "source",
            "selected",
            "phase",
            "TPD",
            "iters",
            "final step",
            "P residual",
            "feasibility",
            "composition",
        ),
        rows,
    )


def _print_iteration_history(diagnostics: Mapping[str, Any]) -> None:
    iteration_history = diagnostics.get("iteration_history", ())
    if not isinstance(iteration_history, (list, tuple)) or not iteration_history:
        return

    rows: list[tuple[object, ...]] = []
    for entry in iteration_history:
        if not isinstance(entry, Mapping):
            continue
        rows.append(
            (
                entry.get("iteration"),
                entry.get("objective"),
                entry.get("primal_infeasibility"),
                entry.get("dual_infeasibility"),
                entry.get("barrier_parameter"),
                entry.get("step_size_primal"),
                entry.get("step_size_dual"),
                entry.get("step_trial_count"),
                entry.get("restoration_phase"),
            )
        )

    _print_table(
        "Last Ipopt iterations",
        (
            "iter",
            "objective",
            "primal inf",
            "dual inf",
            "barrier",
            "alpha pr",
            "alpha du",
            "trials",
            "resto",
        ),
        rows,
    )


def _print_route_report(report: Mapping[str, Any]) -> None:
    route = str(report["route"])
    kwargs = report["kwargs"]
    diagnostics = report["diagnostics"]
    certification = report["certification"]
    spec = ROUTE_REPORT_SPECS[route]
    composition_key, composition_value = _composition_input(kwargs)

    _print_section(f"{route} / {report['problem']}")
    _print_key_values(
        "Request and fixed values",
        (
            ("public call", f'Equilibrium(mixture, route="{route}", ...).solve()'),
            ("T input / K", kwargs.get("T", "solved by route")),
            ("P input / Pa", kwargs.get("P", "solved by route")),
            (f"{composition_key} input", composition_value),
            ("feed basis", spec["feed_basis"]),
            ("native feed/phase-total vector", diagnostics.get("feed_amounts")),
        ),
    )
    _print_key_values(
        "Reference target",
        (
            ("T_ref / K", HYDROCARBON_T),
            ("P_ref / Pa", HYDROCARBON_BUBBLE_P),
            ("liquid x_ref", tuple(float(value) for value in HYDROCARBON_LIQUID_X)),
            ("vapor y_ref", tuple(float(value) for value in HYDROCARBON_VAPOR_Y)),
            ("rho_liq_ref / mol m^-3", HYDROCARBON_LIQUID_RHO),
            ("rho_vap_ref / mol m^-3", HYDROCARBON_VAPOR_RHO),
        ),
    )
    _print_key_values(
        "Route variables and activation",
        (
            ("knowns", spec["knowns"]),
            ("unknowns", spec["unknowns"]),
            ("composition role", spec["composition_role"]),
            ("fixed composition row", spec["fixed_composition"]),
            ("activation key", spec["activation_key"]),
            ("selector family", report["selector_family"]),
            ("native problem name", diagnostics.get("problem_name")),
            ("variable model", diagnostics.get("variable_model")),
            ("density backend", diagnostics.get("density_backend")),
            ("residual families", diagnostics.get("residual_families")),
            ("constraint families", diagnostics.get("constraint_families")),
        ),
    )

    phase_volumes = diagnostics.get("phase_volumes")
    phase_amount_totals = diagnostics.get("phase_amount_totals")
    _print_table(
        "Solved phase state",
        ("phase", "P / Pa", "T / K", "composition", "rho / mol m^-3", "beta", "amount total", "volume / m^3"),
        (
            (
                "liquid",
                report["pressure"],
                report["temperature"],
                report["liquid_x"],
                report["liquid_density"],
                report["liquid_fraction"],
                _sequence_item(phase_amount_totals, 0),
                _sequence_item(phase_volumes, 0),
            ),
            (
                "vapor",
                report["pressure"],
                report["temperature"],
                report["vapor_y"],
                report["vapor_density"],
                report["vapor_fraction"],
                _sequence_item(phase_amount_totals, 1),
                _sequence_item(phase_volumes, 1),
            ),
        ),
    )
    _print_constraint_report(diagnostics)
    _print_key_values(
        "Certification and residual norms",
        (
            ("accepted", certification.get("accepted")),
            ("route accepted", diagnostics.get("route_accepted")),
            ("solver accepted", diagnostics.get("solver_accepted")),
            ("postsolve accepted", diagnostics.get("postsolve_accepted")),
            ("stability checked", certification.get("stability_checked")),
            ("stability accepted", certification.get("stability_accepted")),
            ("pressure consistency norm", diagnostics.get("pressure_consistency_norm")),
            ("material balance norm", diagnostics.get("material_balance_norm")),
            ("phase equilibrium norm", diagnostics.get("phase_equilibrium_norm")),
            ("chemical potential consistency norm", diagnostics.get("chemical_potential_consistency_norm")),
            ("ln fugacity consistency norm", diagnostics.get("ln_fugacity_consistency_norm")),
            ("fixed composition norm", diagnostics.get("fixed_composition_norm")),
            ("charge balance norm", diagnostics.get("charge_balance_norm")),
            ("phase distance", diagnostics.get("phase_distance")),
            ("minimum phase fraction", diagnostics.get("minimum_phase_fraction")),
        ),
    )
    _print_seed_attempts(diagnostics)
    _print_tpd_candidate_report(diagnostics)
    _print_key_values(
        "Runtime and solver",
        (
            ("wall time / s", report["elapsed_seconds"]),
            ("solver backend", diagnostics.get("solver_backend")),
            ("solver status", diagnostics.get("solver_status")),
            ("application status", diagnostics.get("application_status")),
            ("solver ran", diagnostics.get("solver_ran")),
            ("iteration count", diagnostics.get("iteration_count")),
            ("eval_h calls", diagnostics.get("eval_h_calls")),
            ("linear solver requested", diagnostics.get("linear_solver_requested")),
            ("linear solver selected", diagnostics.get("linear_solver_selected")),
            ("scaling method", diagnostics.get("scaling_method")),
            ("objective", diagnostics.get("objective")),
            ("hessian backend", diagnostics.get("hessian_backend")),
            ("derivative backend", diagnostics.get("derivative_backend")),
            ("gradient exact", diagnostics.get("gradient_is_exact")),
            ("jacobian exact", diagnostics.get("jacobian_is_exact")),
            ("hessian exact", diagnostics.get("hessian_is_exact")),
        ),
    )
    _print_iteration_history(diagnostics)


def test_neutral_flash_reference_values_are_reported_and_verified(capsys: pytest.CaptureFixture[str]) -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    expected_x = tuple(float(value) for value in HYDROCARBON_LIQUID_X)
    expected_y = tuple(float(value) for value in HYDROCARBON_VAPOR_Y)
    reports: list[dict[str, object]] = []
    mixture = _mixture()

    for route, kwargs, problem_kind, selector_family in (ROUTE_CASES[-1],):
        started_at = perf_counter()
        result = epcsaft_equilibrium.Equilibrium(mixture, route=route, **kwargs).solve(solver_options=_solver_options())
        elapsed_seconds = perf_counter() - started_at
        liquid = result.phases["liquid"]
        vapor = result.phases["vapor"]
        diagnostics = result.diagnostics
        certification = diagnostics["postsolve_certification"]

        assert result.problem_kind == problem_kind
        assert certification["accepted"] is True
        assert diagnostics["solver_status"] == "success"
        assert diagnostics["application_status"] == "solve_succeeded"
        assert diagnostics["solver_accepted"] is True
        assert diagnostics["max_iterations"] == _solver_options()["max_iterations"]
        assert diagnostics["hessian_approximation"] == "exact"
        assert diagnostics["exact_hessian_available"] is True
        assert liquid.temperature == pytest.approx(HYDROCARBON_T, rel=5.0e-5)
        assert vapor.temperature == pytest.approx(HYDROCARBON_T, rel=5.0e-5)
        assert liquid.pressure == pytest.approx(HYDROCARBON_BUBBLE_P, rel=5.0e-5)
        assert vapor.pressure == pytest.approx(HYDROCARBON_BUBBLE_P, rel=5.0e-5)
        assert liquid.composition == pytest.approx(expected_x, rel=1.0e-4, abs=5.0e-7)
        assert vapor.composition == pytest.approx(expected_y, rel=1.0e-4, abs=5.0e-7)
        assert liquid.density == pytest.approx(HYDROCARBON_LIQUID_RHO, rel=1.0e-4)
        assert vapor.density == pytest.approx(HYDROCARBON_VAPOR_RHO, rel=1.0e-4)
        if route == "flash":
            assert result.split_detected is True
            assert liquid.phase_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)
            assert vapor.phase_fraction == pytest.approx(0.5, rel=1.0e-4, abs=1.0e-6)
            assert diagnostics["route_status"] == "production_accepted"
            assert diagnostics["stability_certificate"]["method"] == "tpd_postsolve"
            assert (
                diagnostics["stability_certificate"]["phase_discovery_backend"]
                == "deterministic_tpd_candidate_screening"
            )
            assert diagnostics["stability_certificate"]["accepted"] is True
            assert diagnostics["stability_certificate"]["candidate_set_complete"] is True
            assert diagnostics["stability_checked"] is True
            assert diagnostics["stability_accepted"] is True
            assert diagnostics["candidate_completeness_accepted"] is True
            assert diagnostics["selected_candidate_count"] == 2
            assert certification["continuous_tpd_status"] == "not_requested"
            assert certification["continuous_tpd_solve_count"] == 0
            assert certification["held_stage_i_status"] == "not_requested"

        reports.append(
            {
                "route": route,
                "kwargs": kwargs,
                "problem": problem_kind,
                "diagnostics": diagnostics,
                "certification": certification,
                "elapsed_seconds": elapsed_seconds,
                "pressure": liquid.pressure,
                "temperature": liquid.temperature,
                "liquid_x": tuple(float(value) for value in liquid.composition),
                "vapor_y": tuple(float(value) for value in vapor.composition),
                "liquid_density": liquid.density,
                "vapor_density": vapor.density,
                "liquid_fraction": liquid.phase_fraction,
                "vapor_fraction": vapor.phase_fraction,
                "selector_family": selector_family,
                "accepted": certification["accepted"],
            }
        )

    with capsys.disabled():
        print("\nNeutral flash selector reference result")
        print("This section reports the route request, fixed values, solved variables, active constraints,")
        print("native certification, deterministic seed sweep, and Ipopt runtime diagnostics.")
        print("Wall time is measured inside this pytest run; the first Ipopt call can include one-time setup cost.")
        for report in reports:
            _print_route_report(report)
