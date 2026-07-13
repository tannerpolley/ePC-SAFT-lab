"""Mixture definition for public ePC-SAFT workflows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .._types import InputError
from ..model.options import ModelOptions
from ..model.parameters import ParameterSet, ParameterSource


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
        self.model_options = ModelOptions._from_stage4_legacy_runtime_options(model_options)
        self.components = tuple(str(component) for component in (components or parameters.components))
        if not self.components:
            raise InputError("Mixture requires at least one component.")
        if set(self.components) != set(parameters.components):
            raise InputError("Mixture components must match the ParameterSet components.")
        charged = any(abs(float(record.charge)) > 0.0 for record in parameters.pure_records)
        self._runtime_parameters = ParameterSource(parameters).to_runtime_dict()
        resolved_runtime_options = (
            ModelOptions._to_stage4_legacy_runtime_options(self.model_options, parameters)
            if charged
            else None
        )
        if resolved_runtime_options is not None:
            self._runtime_parameters.update(resolved_runtime_options)
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
        options = ModelOptions._from_stage4_legacy_runtime_options(root if model_options is None else model_options)
        params = ParameterSet.from_folder(
            root,
            components=labels,
            user_options=ModelOptions._to_stage4_legacy_runtime_options(options),
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
