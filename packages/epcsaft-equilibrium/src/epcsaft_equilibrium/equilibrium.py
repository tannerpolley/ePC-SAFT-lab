"""Public equilibrium workflow object."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from epcsaft import InputError, Mixture

from ._native import provider_contract


class Equilibrium:
    """A constructor-configured equilibrium workflow for a mixture."""

    __slots__ = ("mixture", "_problem")

    def __init__(
        self,
        mixture: Mixture,
        *,
        route: str,
        T: float | None = None,
        P: float | None = None,
        x: Sequence[float] | None = None,
        y: Sequence[float] | None = None,
        z: Sequence[float] | None = None,
    ) -> None:
        if not isinstance(mixture, Mixture):
            raise InputError("Equilibrium requires a Mixture.")

        from .workflows import configure_equilibrium_problem

        provider_contract()
        self.mixture = mixture
        self._problem = configure_equilibrium_problem(mixture.native, route=route, T=T, P=P, x=x, y=y, z=z)

    @property
    def problem(self) -> Any:
        """Return read-only configured problem metadata."""

        return self._problem

    def structure(self) -> Any:
        """Return immutable selector structure metadata for the configured problem."""

        from .workflows import equilibrium_structure

        return equilibrium_structure(self.mixture.native, self._problem)

    def solve(self, *, solver_options: Mapping[str, Any] | Any = None) -> Any:
        """Solve the already configured equilibrium problem."""

        from .workflows import _solve_selector_route

        result = _solve_selector_route(self.mixture.native, self._problem, options=solver_options)
        return _require_exact_hessian(result, method=f"Equilibrium(route='{self._problem.route}').solve()")


def _require_exact_hessian(result: Any, *, method: str) -> Any:
    diagnostics = getattr(result, "diagnostics", {})
    if str(diagnostics.get("hessian_approximation", "")) != "exact":
        raise InputError(f"{method} requires the exact Hessian route.")
    if diagnostics.get("exact_hessian_available") is not True:
        raise InputError(f"{method} did not report exact Hessian availability.")
    return result
