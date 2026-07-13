"""Definitions-only loading for strict Stage 4 source bundles."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .._types import InputError
from .configuration_catalog import MODEL_CONFIGURATION_FILENAME
from .correlations import ScientificInteractionRecord, ScientificRecord
from .options import ModelOptions
from .parameters import ParameterSet


@dataclass(frozen=True, slots=True)
class SourceBundleSelection:
    """Unresolved scientific definitions plus one explicit model configuration."""

    parameter_set: ParameterSet
    model_options: ModelOptions
    source_files: tuple[Path, ...]

    def pure_record(self, component: str, field: str) -> ScientificRecord:
        matches = [
            record
            for record in self.parameter_set.pure_records
            if isinstance(record, ScientificRecord)
            and record.component == component
            and record.field == field
        ]
        if len(matches) != 1:
            raise InputError(
                f"source bundle requires one unique pure record for {component}.{field}; found {len(matches)}."
            )
        return matches[0]

    def interaction_record(
        self,
        family: str,
        left: str,
        right: str,
    ) -> ScientificInteractionRecord:
        pair = frozenset((left, right))
        matches = [
            record
            for record in self.parameter_set.interactions
            if isinstance(record, ScientificInteractionRecord)
            and record.family == family
            and frozenset(record.components) == pair
        ]
        if len(matches) != 1:
            raise InputError(
                f"source bundle requires one unique interaction record for {family} {left}|{right}; "
                f"found {len(matches)}."
            )
        return matches[0]


def load_source_bundle_selection(
    path: str | Path,
    components: Sequence[str],
) -> SourceBundleSelection:
    """Load strict definitions and policy without evaluating a state condition."""

    root = Path(path).expanduser()
    if not root.is_dir():
        raise InputError(f"source bundle folder '{root}' does not exist.")
    retired = sorted(
        name
        for name in ("user_options.json", "model_options.json")
        if (root / name).exists()
    )
    if retired:
        raise InputError(f"source bundle contains retired filename(s): {', '.join(retired)}.")
    parameter_path = root / "parameter_set.json"
    configuration_path = root / MODEL_CONFIGURATION_FILENAME
    if not parameter_path.is_file():
        raise InputError("source bundle must contain parameter_set.json.")
    if not configuration_path.is_file():
        raise InputError(f"source bundle must contain {MODEL_CONFIGURATION_FILENAME}.")
    try:
        payload = json.loads(
            parameter_path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid parameter_set.json: {exc.msg}.") from exc
    parameters = ParameterSet.from_schema3(payload)
    requested = tuple(str(component) for component in components)
    if requested != parameters.components:
        raise InputError("source bundle component order must exactly match the requested component order.")
    model_options = ModelOptions.from_user_options(configuration_path)
    return SourceBundleSelection(
        parameter_set=parameters,
        model_options=model_options,
        source_files=(parameter_path, configuration_path),
    )


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"parameter-set JSON contains duplicate key: {key}.")
        result[key] = value
    return result
