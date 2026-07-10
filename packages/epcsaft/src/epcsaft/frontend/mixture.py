"""Mixture definition for public ePC-SAFT workflows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from .._types import InputError
from ..model.options import ModelOptions, coerce_model_options
from ..model.parameters import ParameterSet, _interaction_matrices, _runtime_parameter_provenance_payload


class Mixture:
    """A configured set of components, parameters, and model options."""

    def __init__(
        self,
        parameters: ParameterSet,
        *,
        model_options: ModelOptions | Mapping[str, object] | None = None,
        components: Sequence[str] | None = None,
    ) -> None:
        if not isinstance(parameters, ParameterSet):
            raise InputError("Mixture requires a ParameterSet.")
        self.parameters = parameters
        self.model_options = coerce_model_options(model_options)
        self.model_options.validate_parameters(parameters)
        self.components = tuple(str(component) for component in (components or parameters.components))
        if not self.components:
            raise InputError("Mixture requires at least one component.")
        if set(self.components) != set(parameters.components):
            raise InputError("Mixture components must match the ParameterSet components.")
        self._runtime_parameters = _runtime_payload(parameters, self.components, self.model_options)
        self._runtime = None

    @classmethod
    def from_folder(
        cls,
        path: str | Path,
        *,
        components: Sequence[str],
        model_options: ModelOptions | Mapping[str, object] | str | Path | None = None,
    ) -> Mixture:
        """Load a configured mixture from a parameter/options folder."""

        labels = tuple(str(component) for component in components)
        if not labels:
            raise InputError("Mixture.from_folder requires at least one component.")
        root = Path(path).expanduser()
        options = coerce_model_options(root if model_options is None else model_options)
        params = ParameterSet.from_folder(
            root,
            components=labels,
            user_options=options.to_json_dict(),
        )
        return cls(params, model_options=options, components=labels)

    @property
    def ncomp(self) -> int:
        """Return the number of components in the mixture."""

        return len(self.components)

    @property
    def native(self) -> Any:
        """Return the internal native mixture adapter."""

        if self._runtime is None:
            from ..state.native_adapter import ePCSAFTMixture as _RuntimeMixture

            self._runtime = _RuntimeMixture.from_params(self._runtime_parameters, species=self.components)
        return self._runtime


def _runtime_payload(parameters: ParameterSet, components: Sequence[str], model_options: ModelOptions) -> dict[str, Any]:
    records = {str(record.component): record for record in parameters.pure_records}
    ordered = [records[str(component)] for component in components]
    charges = np.asarray([record.charge for record in ordered], dtype=float)
    payload: dict[str, Any] = {
        "m": np.asarray([record.m for record in ordered], dtype=float),
        "s": np.asarray([record.sigma for record in ordered], dtype=float),
        "e": np.asarray([record.epsilon_k for record in ordered], dtype=float),
    }
    if np.any(np.abs(charges) > 0.0):
        payload["MW"] = np.asarray([record.molar_mass for record in ordered], dtype=float)
        payload["z"] = charges
        payload["dielc"] = np.asarray([record.relative_permittivity for record in ordered], dtype=float)
        payload["d_born"] = np.asarray([record.born_diameter for record in ordered], dtype=float)
        payload["f_solv"] = np.asarray([record.solvation_factor for record in ordered], dtype=float)
        payload.update(model_options.to_runtime_options(parameters))
    if any(float(record.epsilon_k_ab) != 0.0 for record in ordered):
        payload["e_assoc"] = np.asarray([record.epsilon_k_ab for record in ordered], dtype=float)
    if any(float(record.kappa_ab) != 0.0 for record in ordered):
        payload["vol_a"] = np.asarray([record.kappa_ab for record in ordered], dtype=float)
    schemes = [record.association_scheme for record in ordered]
    if any(scheme not in (None, "") for scheme in schemes):
        payload["assoc_scheme"] = schemes
    matrices, interaction_receipt = _interaction_matrices(parameters, components)
    payload.update(matrices)
    payload.update(_runtime_parameter_provenance_payload(parameters.metadata, interaction_receipt))
    return payload
