"""Public equilibrium workflow object."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

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

    def bubble_pressure(self, *, T: float, x: Sequence[float], **overrides: Any) -> Any:
        """Solve a bubble-pressure equilibrium at fixed temperature and liquid composition."""

        options = self._options(overrides)
        result = self.mixture.native.bubble_p(T=T, x=np.asarray(x, dtype=float), options=options)
        diagnostics = getattr(result, "diagnostics", {})
        if str(diagnostics.get("hessian_approximation", "")) != "exact":
            raise InputError("Equilibrium.bubble_pressure requires the exact Hessian route.")
        if diagnostics.get("exact_hessian_available") is not True:
            raise InputError("Equilibrium.bubble_pressure did not report exact Hessian availability.")
        return result

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
