"""Mixture definition for public ePC-SAFT workflows."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .._types import InputError
from ..model.options import ModelOptions
from ..model.parameters import ParameterSet
from ..model.resolved_input import ResolvedModelInput
from ..state.native_adapter import ePCSAFTMixture


class Mixture:
    """A configured set of components, parameters, and model options."""

    def __init__(
        self,
        parameters: ParameterSet,
        *,
        model_options: ModelOptions,
        components: Sequence[str] | None = None,
    ) -> None:
        if not isinstance(parameters, ParameterSet):
            raise InputError("Mixture requires a ParameterSet.")
        if not isinstance(model_options, ModelOptions):
            raise InputError("Mixture requires an explicit ModelOptions selection.")
        self.model_options = model_options
        self.resolved_model_input = ResolvedModelInput.resolve(
            parameters,
            model_options,
            components=components,
        )
        self.components = self.resolved_model_input.components
        self._runtime_mixture = ePCSAFTMixture(self.resolved_model_input)

    @classmethod
    def from_folder(
        cls,
        path: str | Path,
        *,
        components: Sequence[str],
        model_options: ModelOptions | str | Path | None = None,
    ) -> Mixture:
        """Load a configured mixture from a parameter/options folder."""

        labels = tuple(str(component) for component in components)
        if not labels:
            raise InputError("Mixture.from_folder requires at least one component.")
        root = Path(path).expanduser()
        options = ModelOptions.from_user_options(root if model_options is None else model_options)
        params = ParameterSet.from_folder(root, components=labels)
        return cls(params, model_options=options, components=labels)

    @property
    def ncomp(self) -> int:
        """Return the number of components in the mixture."""

        return len(self.components)

    @property
    def configuration_receipt(self) -> dict[str, Any]:
        """Return a detached receipt for the compiled provider definition."""

        return self.resolved_model_input.configuration_receipt
