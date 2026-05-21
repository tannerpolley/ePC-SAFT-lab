from __future__ import annotations

from typing import Any

import pytest

import epcsaft
import epcsaft._core as _core
from tests.support.hydrocarbon_cases import (
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


def _equilibrium() -> epcsaft.Equilibrium:
    return epcsaft.Equilibrium(
        epcsaft.Mixture(hydrocarbon_parameter_set()),
        max_iterations=200,
        tolerance=1.0e-8,
        ipopt_iteration_history_limit=4,
    )


def _format_vector(values: object) -> str:
    return "[" + ", ".join(f"{float(value):.12g}" for value in values) + "]"


def test_neutral_vle_reference_values_are_reported_and_verified(capsys: pytest.CaptureFixture[str]) -> None:
    if not _core._native_ipopt_smoke()["compiled"]:
        pytest.skip("native Ipopt is not compiled")

    expected_x = tuple(float(value) for value in HYDROCARBON_LIQUID_X)
    expected_y = tuple(float(value) for value in HYDROCARBON_VAPOR_Y)
    rows: list[dict[str, object]] = []
    equilibrium = _equilibrium()

    for route, kwargs, problem_kind, selector_family in ROUTE_CASES:
        result = equilibrium.solve(route=route, **kwargs)
        liquid, vapor = result.phases
        diagnostics = result.diagnostics
        certification = diagnostics["postsolve_certification"]

        assert result.problem_kind == problem_kind
        assert certification["accepted"] is True
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

        rows.append(
            {
                "route": route,
                "problem": problem_kind,
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
        print("\nNeutral VLE selector reference results")
        print(f"Expected T / K: {HYDROCARBON_T:.12g}")
        print(f"Expected P / Pa: {HYDROCARBON_BUBBLE_P:.12g}")
        print(f"Expected liquid x: {_format_vector(expected_x)}")
        print(f"Expected vapor y:  {_format_vector(expected_y)}")
        print(f"Expected rho_liq / mol m^-3: {HYDROCARBON_LIQUID_RHO:.12g}")
        print(f"Expected rho_vap / mol m^-3: {HYDROCARBON_VAPOR_RHO:.12g}")
        print(
            "| route | problem | P / Pa | T / K | liquid x | vapor y | "
            "rho_liq / mol m^-3 | rho_vap / mol m^-3 | beta_liq | beta_vap | family | accepted |"
        )
        print(
            "| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | --- |"
        )
        for row in rows:
            print(
                f"| {row['route']} "
                f"| {row['problem']} "
                f"| {float(row['pressure']):.9g} "
                f"| {float(row['temperature']):.9g} "
                f"| {_format_vector(row['liquid_x'])} "
                f"| {_format_vector(row['vapor_y'])} "
                f"| {float(row['liquid_density']):.9g} "
                f"| {float(row['vapor_density']):.9g} "
                f"| {float(row['liquid_fraction']):.9g} "
                f"| {float(row['vapor_fraction']):.9g} "
                f"| {row['selector_family']} "
                f"| {row['accepted']} |"
            )
