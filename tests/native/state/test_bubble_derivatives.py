from __future__ import annotations

from tests.support.native_cases import _neutral_state


def test_cppad_pressure_derivative_api_underpins_bubble_policy() -> None:
    mix, _species, _pressure, density, temperature, composition = _neutral_state()
    state = mix.state(T=temperature, x=composition, rho=density)

    pressure_density = state.pressure_density_derivative_result()

    assert pressure_density["backend"] == "cppad"
    assert pressure_density["shape"] == [1, 1]
