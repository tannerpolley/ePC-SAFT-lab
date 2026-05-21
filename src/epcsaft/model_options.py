"""Public model configuration for the reset frontend."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np

from ._types import InputError
from .parameter_schema import ParameterSet


class MissingModelParameterError(InputError):
    """Raised when an enabled model formulation lacks required parameters."""


RelativePermittivityRule = Literal["component_linear", "linear", "constant"]
BornFormulation = Literal["disabled", "born", "ssm", "ds", "ssm_ds"]


@dataclass(frozen=True, slots=True)
class ModelOptions:
    """Formulation choices owned by :class:`epcsaft.Mixture`.

    CppAD is the only public derivative substrate in the reset API. This class
    intentionally has no analytic, automatic, or backend-selection option.
    """

    relative_permittivity_rule: RelativePermittivityRule = "component_linear"
    born_formulation: BornFormulation = "disabled"

    def __post_init__(self) -> None:
        rel_perm = str(self.relative_permittivity_rule).strip().lower().replace("-", "_")
        if rel_perm not in {"component_linear", "linear", "constant"}:
            raise InputError(
                "ModelOptions.relative_permittivity_rule must be 'component_linear', 'linear', or 'constant'."
            )
        born = str(self.born_formulation).strip().lower().replace("-", "_")
        if born not in {"disabled", "born", "ssm", "ds", "ssm_ds"}:
            raise InputError("ModelOptions.born_formulation must be 'disabled', 'born', 'ssm', 'ds', or 'ssm_ds'.")
        object.__setattr__(self, "relative_permittivity_rule", rel_perm)
        object.__setattr__(self, "born_formulation", born)

    def validate_parameters(self, parameters: ParameterSet) -> None:
        """Validate that enabled formulations have required parameter data."""

        if not isinstance(parameters, ParameterSet):
            raise InputError("ModelOptions validation requires a ParameterSet.")
        if self.born_formulation == "disabled":
            return
        charged = [record for record in parameters.pure_records if abs(float(record.charge)) > 0.0]
        missing = [record.component for record in charged if float(record.born_diameter) <= 0.0]
        if missing:
            joined = ", ".join(missing)
            raise MissingModelParameterError(
                f"Born-family formulation '{self.born_formulation}' requires positive born_diameter for: {joined}."
            )

    def to_runtime_options(self, parameters: ParameterSet | None = None) -> dict[str, object]:
        """Return the existing native runtime option payload for this model."""

        if parameters is not None:
            self.validate_parameters(parameters)
        rel_rule = "linear" if self.relative_permittivity_rule in {"component_linear", "linear"} else "constant"
        include_born = self.born_formulation != "disabled"
        return {
            "elec_model": {
                "rel_perm": {
                    "rule": rel_rule,
                    "differential_mode": "cppad",
                },
                "hc_model": {"dadx_differential_mode": "cppad"},
                "disp_model": {"dadx_differential_mode": "cppad"},
                "assoc_model": {"dadx_differential_mode": "cppad"},
                "DH_model": {
                    "d_ion_mode": "t_dep_1",
                    "bjeruum_treatment": False,
                    "mu_DH_model": {
                        "differential_mode": "cppad",
                        "comp_dep_rel_perm": True,
                        "include_sum_term": True,
                    },
                },
                "include_born_model": include_born,
                "born_model": {
                    "d_Born_mode": "t_indep",
                    "solvation_shell_model": self.born_formulation in {"ssm", "ssm_ds"},
                    "dielectric_saturation": self.born_formulation in {"ds", "ssm_ds"},
                    "bulk_mode": "mix",
                    "mu_born_model": {
                        "differential_mode": "cppad",
                        "comp_dep_rel_perm": True,
                        "include_sum_term": True,
                        "comp_dep_delta_d": self.born_formulation in {"ssm", "ssm_ds"},
                    },
                },
            },
            "solvated_ion_diameter_mixing_rule": False,
            "ion_dispersion_mixing_rule": True,
        }

    def to_json_dict(self) -> dict[str, object]:
        return asdict(self)


def coerce_model_options(value: ModelOptions | Mapping[str, object] | None) -> ModelOptions:
    if value is None:
        return ModelOptions()
    if isinstance(value, ModelOptions):
        return value
    if isinstance(value, Mapping):
        return ModelOptions(**dict(value))
    raise InputError("model_options must be a ModelOptions instance or mapping.")


def require_cppad_backend(result: Mapping[str, object], *, label: str) -> None:
    backend = str(result.get("derivative_backend", result.get("jacobian_backend", result.get("backend", ""))))
    if not backend.startswith("cppad"):
        raise InputError(f"{label} requires CppAD derivative coverage; got backend {backend!r}.")


def as_float_array(value: object) -> np.ndarray:
    return np.asarray(value, dtype=float)
