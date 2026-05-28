"""Public regression workflow object."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from epcsaft import InputError, Mixture
from epcsaft.model.options import require_cppad_backend


@dataclass(slots=True)
class Regression:
    """A configured parameter-regression workflow for a mixture."""

    mixture: Mixture
    defaults: dict[str, Any] = field(default_factory=dict)

    def __init__(self, mixture: Mixture, **defaults: Any) -> None:
        if not isinstance(mixture, Mixture):
            raise InputError("Regression requires a Mixture.")
        self.mixture = mixture
        self.defaults = _reject_backend_options(defaults, context="Regression")

    def evaluate_pure_neutral_derivatives(self, records: Any, *, component: str, **overrides: Any) -> dict[str, Any]:
        """Evaluate pure-component neutral regression derivatives."""

        from . import evaluate_pure_neutral_derivatives as _evaluate

        payload = dict(self.defaults)
        payload.update(_reject_backend_options(overrides, context="Regression"))
        result = dict(_evaluate(records, component, **payload))
        require_cppad_backend(result, label="Regression.evaluate_pure_neutral_derivatives")
        return result

    def fit_pure_neutral(self, records: Any, *, component: str, **overrides: Any) -> Any:
        """Fit pure-component neutral parameters."""

        from . import fit_pure_neutral as _fit

        payload = dict(self.defaults)
        payload.update(_reject_backend_options(overrides, context="Regression"))
        result = _fit(records, component, optimizer_backend="ceres", **payload)
        if not str(getattr(result, "jacobian_backend", "")).startswith("cppad"):
            raise InputError("Regression.fit_pure_neutral requires Jacobian coverage.")
        return result


def _reject_backend_options(options: Mapping[str, Any], *, context: str) -> dict[str, Any]:
    blocked = sorted(set(options) & {"backend", "derivative_backend", "jacobian_backend", "solver_backend", "hessian_mode"})
    if blocked:
        raise InputError(f"{context} does not expose backend-selection option(s): {', '.join(blocked)}.")
    return dict(options)
