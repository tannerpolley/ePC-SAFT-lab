"""Public equilibrium workflow object."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .._types import InputError
from .mixture import Mixture


@dataclass(slots=True)
class Equilibrium:
    """A configured equilibrium workflow for a mixture."""

    mixture: Mixture
    defaults: dict[str, Any] = field(default_factory=dict)

    def __init__(self, mixture: Mixture, **defaults: Any) -> None:
        if not isinstance(mixture, Mixture):
            raise InputError("Equilibrium requires a Mixture.")
        self.mixture = mixture
        self.defaults = _reject_backend_options(defaults, context="Equilibrium")

    def solve(
        self,
        *,
        route: str,
        T: float | None = None,
        P: float | None = None,
        x: Sequence[float] | None = None,
        y: Sequence[float] | None = None,
        z: Sequence[float] | None = None,
        **overrides: Any,
    ) -> Any:
        """Solve one selector-admitted neutral VLE route spec."""

        from ..equilibrium.workflows import _solve_selector_vle

        options = self._options(overrides)
        result = _solve_selector_vle(self.mixture.native, route=route, T=T, P=P, x=x, y=y, z=z, options=options)
        return _require_exact_hessian(result, method=f"Equilibrium.solve(route='{route}')")

    def _options(self, overrides: Mapping[str, Any] | None = None) -> Any:
        from ..equilibrium import EquilibriumOptions

        payload = dict(self.defaults)
        payload.update(_reject_backend_options(overrides or {}, context="Equilibrium"))
        payload["jacobian_backend"] = "cppad"
        payload["solver_backend"] = "ipopt"
        payload["hessian_mode"] = "exact"
        return EquilibriumOptions(**payload)


def _reject_backend_options(options: Mapping[str, Any], *, context: str) -> dict[str, Any]:
    blocked = sorted(set(options) & {"backend", "derivative_backend", "jacobian_backend", "solver_backend", "hessian_mode"})
    if blocked:
        raise InputError(f"{context} does not expose backend-selection option(s): {', '.join(blocked)}.")
    return dict(options)


def _require_exact_hessian(result: Any, *, method: str) -> Any:
    diagnostics = getattr(result, "diagnostics", {})
    if str(diagnostics.get("hessian_approximation", "")) != "exact":
        raise InputError(f"{method} requires the exact Hessian route.")
    if diagnostics.get("exact_hessian_available") is not True:
        raise InputError(f"{method} did not report exact Hessian availability.")
    return result
