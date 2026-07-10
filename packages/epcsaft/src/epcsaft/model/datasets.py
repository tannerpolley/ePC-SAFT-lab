"""Dataset-driven parameter loader for the ePC-SAFT runtime.

This module reads external parameter dataset directories with the expected
on-disk layout. The historical ``data/reference/epcsaft_parameters`` source
tree is now a pointer-only location; full paper-validation bundles live under
``analyses/paper_validation/<paper_id>/parameters``.

Public API:
    - get_prop_dict(dataset_name, species, x, T, user_options=None)
    - default_user_options()
    - minimize_user_options(user_options)
    - _resolve_runtime_options(user_options)
    - molality_to_molefraction(...)
    - molefraction_to_molality(...)
"""

from __future__ import annotations

import copy
import csv
import math
import re
from collections.abc import Iterable, Mapping
from pathlib import Path

import numpy as np

from .._types import InputError
from .sources import (
    deep_update_parameter_mapping as _deep_update,
)
from .sources import (
    load_canonical_user_options as _load_canonical_user_options,
)

BASE_KEYS = ["MW", "m", "s", "e", "e_assoc", "vol_a", "assoc_scheme", "z", "dielc"]
OPTIONAL_KEYS = ["d_born", "f_solv"]
METADATA_KEYS = ["source"]

COMPONENT_ALIASES = {
    "H2O-2B-Li": "H2O",
    "H2O-2B-NaCl": "H2O",
    "H2O-Salt-2001": "H2O",
    "Water": "H2O",
    "water": "H2O",
    "methanol": "Methanol",
    "ethanol": "Ethanol",
    "1-Butanol": "Butanol",
    "butanol": "Butanol",
    "Isobutanol": "Butanol",
    "isobutanol": "Butanol",
    "benzene": "Benzene",
    "toluene": "Toluene",
    "glycine": "Glycine",
    "alanine": "Alanine",
    "propanol": "Propanol",
}

PURE_SET_KEY_ALIASES = {
    "water": "water",
    "h2o": "water",
    "methanol": "methanol",
    "ethanol": "ethanol",
    "any": "any_solvent",
    "default": "any_solvent",
    "any_solvent": "any_solvent",
}

_LINEAR_T_RE = re.compile(
    r"^\s*([+\-]?\d*\.?\d+(?:[eE][+\-]?\d+)?(?:\*10\^[+\-]?\d+)?)\s*\*?\s*T(?:\s*/\s*K)?\s*([+\-]\s*\d*\.?\d+(?:[eE][+\-]?\d+)?)\s*$",
    flags=re.IGNORECASE,
)
_LOG_T_RE = re.compile(
    r"^\s*([+\-]?\d*\.?\d+(?:[eE][+\-]?\d+)?)\s*\*?\s*ln\s*\(\s*T\s*\)\s*([+\-]\s*\d*\.?\d+(?:[eE][+\-]?\d+)?)\s*$",
    flags=re.IGNORECASE,
)

_REL_PERM_RULE_ALIASES = {
    "constant": 0,
    "rule0": 0,
    "linear": 1,
    "linear-molefraction": 1,
    "linear-mixing-mole": 1,
    "rule1": 1,
    "rule1a": 7,
    "linear-saltfraction": 7,
    "linear-mixing-salt": 7,
    "linear-massfraction": 2,
    "linear-mixing-weight": 2,
    "rule2": 2,
    "combined": 3,
    "rule3": 3,
    "salt-free-massfraction": 9,
    "salt_free_massfraction": 9,
    "salt-free-solvent-massfraction": 9,
    "salt_free_solvent_massfraction": 9,
    "salt-free-solvent-weight": 9,
    "salt_free_solvent_weight": 9,
    "rule9": 9,
    "empirical": 4,
    "rule4": 4,
    "rule5": 5,
    "rule6": 6,
    "aqueous-organic": 8,
    "aqueous_organic": 8,
    "mixed-aqueous-organic": 8,
    "mixed_aqueous_organic": 8,
    "rule8": 8,
}

SOLVENT_COMPONENT_TO_TOKEN = {
    "H2O": "water",
    "Methanol": "methanol",
    "Ethanol": "ethanol",
    "Propanol": "propanol",
    "Butanol": "butanol",
}

SOLVENT_TOKEN_ORDER = {"water": 0, "methanol": 1, "ethanol": 2, "propanol": 3, "butanol": 4}
_DIFF_MODE_ALIASES = {
    "auto": 3,
    "automatic": 3,
    "implicit": 3,
    "analytic_implicit": 3,
    "cppad_implicit": 3,
    "cppad_implicit_association": 3,
    "analytic": 0,
    "analytical": 0,
    "cppad": 2,
}
_D_ION_MODE_ALIASES = {
    "t_indep": 0,
    "t_dep_1": 1,
    "t_dep_2": 2,
}
_D_BORN_MODE_ALIASES = {
    "t_indep": 0,
    "t_dep_1": 1,
    "t_dep_2": 2,
    "fitted_param": 3,
}
_BULK_MODE_ALIASES = {
    "mix": 0,
    "bulk": 0,
    "solvent": 1,
}
_CANONICAL_CONTRIBUTION_MODEL = {
    "dadx_differential_mode": "auto",
}
_CANONICAL_ELEC_MODEL = {
    "rel_perm": {
        "rule": 1,
        "differential_mode": "auto",
    },
    "hc_model": dict(_CANONICAL_CONTRIBUTION_MODEL),
    "disp_model": dict(_CANONICAL_CONTRIBUTION_MODEL),
    "assoc_model": dict(_CANONICAL_CONTRIBUTION_MODEL),
    "DH_model": {
        # Preserve current behavior (ionic diameter uses 0.88*sigma by default).
        "d_ion_mode": 1,
        "bjeruum_treatment": False,
        "mu_DH_model": {
            "differential_mode": "auto",
            "comp_dep_rel_perm": True,
            "include_sum_term": True,
        },
    },
    "include_born_model": True,
    "born_model": {
        "d_Born_mode": 0,
        "solvation_shell_model": True,
        "dielectric_saturation": True,
        "bulk_mode": "mix",
        "mu_born_model": {
            "differential_mode": "auto",
            "comp_dep_rel_perm": True,
            "include_sum_term": True,
            "comp_dep_delta_d": True,
        },
    },
}
_DEFAULT_USER_OPTIONS = {
    "solvated_ion_diameter_mixing_rule": False,
    "ion_dispersion_mixing_rule": True,
    "elec_model": {
        "differential_mode": "autodiff",
        "relative_permittivity_rule": "component_linear",
        "born_model": {
            "enabled": True,
            "born_diameter_rule": "sigma",
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "bulk_mode": "mix",
        },
    },
}

_DATASET_CACHE: dict[str, dict] = {}
_MISSING = object()


def _coerce_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, np.integer)):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"1", "true", "yes", "y", "on"}:
            return True
        if v in {"0", "false", "no", "n", "off"}:
            return False
    raise ValueError(f"Cannot coerce value '{value}' to bool.")


def _prune_default_overrides(payload, defaults):
    if isinstance(payload, dict):
        if not isinstance(defaults, dict):
            return copy.deepcopy(payload)
        pruned = {}
        for key, value in payload.items():
            default_value = defaults.get(key, _MISSING)
            if default_value is _MISSING:
                pruned[key] = copy.deepcopy(value)
                continue
            candidate = _prune_default_overrides(value, default_value)
            if candidate is not _MISSING:
                pruned[key] = candidate
        return pruned if pruned else _MISSING
    return _MISSING if payload == defaults else copy.deepcopy(payload)


def default_user_options() -> dict:
    """Return a deep copy of the package's canonical user-option defaults."""

    return copy.deepcopy(_DEFAULT_USER_OPTIONS)


def minimize_user_options(user_options: dict | None) -> dict:
    """Drop any user-option entries that are identical to package defaults."""

    if user_options is None:
        return {}
    if not isinstance(user_options, dict):
        raise TypeError("user_options must be a dict.")
    _resolve_runtime_options(user_options)
    pruned = _prune_default_overrides(user_options, _DEFAULT_USER_OPTIONS)
    return {} if pruned is _MISSING else pruned


def _normalize_component(name: str) -> str:
    return COMPONENT_ALIASES.get(name, name)


def _resolve_dataset_dir(dataset_name_or_path) -> tuple[str, Path]:
    path = Path(dataset_name_or_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Dataset path '{path}' does not exist.")
    resolved = path.resolve()
    return f"path::{resolved}", resolved


def _normalize_pure_set_key(name: str) -> str:
    return PURE_SET_KEY_ALIASES.get(name.strip().lower(), name.strip().lower())


def _solvent_token_for_component(name: str) -> str | None:
    component = _normalize_component(name.strip())
    return SOLVENT_COMPONENT_TO_TOKEN.get(component)


def _canonical_solvent_tokens(tokens: Iterable[str]) -> list[str]:
    unique = {str(token).strip().lower() for token in tokens if str(token).strip()}
    return sorted(unique, key=lambda token: (SOLVENT_TOKEN_ORDER.get(token, 999), token))


def _solvent_system_data_key(tokens: Iterable[str]) -> str:
    canonical = _canonical_solvent_tokens(tokens)
    return "-".join(canonical)


def _solvent_fraction_aliases(token: str, basis: str) -> tuple[str, ...]:
    token = str(token).strip().lower()
    if token == "water":
        names = ("water", "h2o")
    elif token == "methanol":
        names = ("methanol", "meoh")
    elif token == "ethanol":
        names = ("ethanol", "etoh")
    else:
        names = (token,)
    aliases: list[str] = []
    for name in names:
        aliases.append(f"{basis}_{name}")
        aliases.append(f"{basis}_{name}_salt_free")
    return tuple(aliases)


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row_number, row in enumerate(reader, start=2):
            if row.get(None):
                raise ValueError(f"CSV file '{path}' row {row_number} contains surplus cells.")
            rows.append(row)
        return rows


def _load_component_rows(path: Path) -> dict[str, dict[str, str]]:
    rows = _read_csv(path)
    if rows:
        allowed_columns = {"component", *BASE_KEYS, *OPTIONAL_KEYS, *METADATA_KEYS}
        forbidden_columns = {"dipm", "dip_num"}
        present_columns = {str(key).strip() for key in rows[0].keys() if key}
        legacy_columns = sorted(present_columns & forbidden_columns)
        if legacy_columns:
            raise ValueError(
                f"Dataset file '{path}' uses removed polar column(s): {legacy_columns}. Update the active package schema."
            )
        unknown_columns = sorted(present_columns - allowed_columns)
        if unknown_columns:
            raise ValueError(f"Dataset file '{path}' contains unsupported column(s): {unknown_columns}.")
    mapping: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        comp = _normalize_component(str(row.get("component", "")).strip())
        if not comp:
            raise ValueError(f"Dataset file '{path}' row {row_number} has a blank component identifier.")
        if comp in mapping:
            raise ValueError(f"Dataset file '{path}' contains duplicate component row '{comp}'.")
        mapping[comp] = {k: str(v or "").strip() for k, v in row.items()}
    return mapping


def _load_pure_sets(pure_dir: Path) -> dict[str, dict[str, dict[str, str]]]:
    pure_sets: dict[str, dict[str, dict[str, str]]] = {}
    if not pure_dir.exists():
        return pure_sets
    for pure_file in sorted(pure_dir.glob("*.csv")):
        set_key = _normalize_pure_set_key(pure_file.stem)
        set_map = _load_component_rows(pure_file)
        if set_map:
            pure_sets[set_key] = set_map
    return pure_sets


def _sole_pure_set_key(pure_sets: dict[str, dict[str, dict[str, str]]]) -> str | None:
    if len(pure_sets) == 1:
        return next(iter(pure_sets))
    return None


def _ion_pure_set_key(dataset: dict, solvent: str) -> str:
    pure_sets = dataset.get("pure_sets", {})
    requested_key = _normalize_pure_set_key(solvent)
    if requested_key in pure_sets:
        return requested_key
    if dataset.get("sole_pure_set_key") == "any_solvent":
        return "any_solvent"
    raise KeyError(
        f"Dataset '{dataset['dataset_name']}' has no explicit ion parameter set for solvent "
        f"'{solvent}' and no sole pure/any_solvent.csv set."
    )


_INTERACTION_SOURCE_FILES = {
    "k_ij": ("k_ij.csv",),
    "l_ij": ("l_ij.csv",),
    "k_hb_ij": ("k_hb_ij.csv", "khb_ij.csv"),
}
_INTERACTION_PROVENANCE_STATUS_KIND = {
    "": "literature",
    "source_backed": "literature",
    "fitted": "fitted",
}


def _load_source_interactions(
    dataset_root: str | Path,
    components: Iterable[str],
):
    """Load a complete typed interaction graph from matrices and their source manifest."""

    from .parameters import (
        ConstantInteractionRecord,
        InteractionProvenance,
        LinearTemperatureInteractionRecord,
    )

    root = Path(dataset_root).expanduser()
    binary_root = root / "mixed" / "binary_interaction"
    requested = tuple(str(component) for component in components)
    normalized = tuple(_normalize_component(component) for component in requested)
    if len(set(requested)) != len(requested):
        raise InputError("Interaction components must be unique.")
    if len(set(normalized)) != len(normalized):
        raise InputError("Interaction component aliases must resolve to unique dataset identities.")
    if len(requested) < 2:
        return ()
    requested_by_normalized = dict(zip(normalized, requested, strict=True))

    matrices = {
        family: _load_strict_interaction_matrix(
            _interaction_source_path(binary_root, family),
            family,
        )
        for family in _INTERACTION_SOURCE_FILES
    }
    manifest, wildcard_families = _load_interaction_source_manifest(binary_root / "source_manifest.csv")
    _validate_interaction_manifest_matrix_identity(manifest, matrices)
    records = []
    wildcard_gaps: list[str] = []
    missing_gaps: list[str] = []
    for left_index, left in enumerate(normalized):
        for right in normalized[left_index + 1 :]:
            requested_pair = (requested_by_normalized[left], requested_by_normalized[right])
            for family in _INTERACTION_SOURCE_FILES:
                matrix_signature = _matrix_pair_signature(
                    matrices[family],
                    family=family,
                    left=left,
                    right=right,
                    display_pair=requested_pair,
                )
                manifest_entry = manifest.get((family, frozenset((left, right))))
                if manifest_entry is None:
                    gap = f"{family} pair {requested_pair[0]}|{requested_pair[1]}"
                    if family in wildcard_families:
                        wildcard_gaps.append(gap)
                    else:
                        missing_gaps.append(gap)
                    continue
                manifest_signature, source, provenance_status = manifest_entry
                provenance_kind = _INTERACTION_PROVENANCE_STATUS_KIND.get(provenance_status)
                if provenance_kind is None:
                    raise InputError(
                        f"Interaction {family} pair {requested_pair[0]}|{requested_pair[1]} has unresolved "
                        f"provenance status '{provenance_status}'."
                    )
                if manifest_signature != matrix_signature:
                    raise InputError(
                        f"Interaction source manifest value does not match matrix {family} pair "
                        f"{requested_pair[0]}|{requested_pair[1]}."
                    )
                provenance = InteractionProvenance(kind=provenance_kind, source=source)
                if manifest_signature[0] == "constant":
                    records.append(
                        ConstantInteractionRecord(
                            family=family,
                            components=requested_pair,
                            value=manifest_signature[1],
                            provenance=provenance,
                        )
                    )
                else:
                    records.append(
                        LinearTemperatureInteractionRecord(
                            family=family,
                            components=requested_pair,
                            slope=manifest_signature[1],
                            intercept=manifest_signature[2],
                            temperature_units="K",
                            provenance=provenance,
                        )
                    )
    if wildcard_gaps:
        raise InputError(
            "Wildcard interaction rows cannot supply explicit evidence for "
            + "; ".join(wildcard_gaps)
            + "."
        )
    if missing_gaps:
        raise InputError("Missing source-manifest interaction records for " + "; ".join(missing_gaps) + ".")
    return tuple(records)


def _interaction_source_path(binary_root: Path, family: str) -> Path:
    candidates = [binary_root / name for name in _INTERACTION_SOURCE_FILES[family] if (binary_root / name).is_file()]
    if len(candidates) != 1:
        expected = ", ".join(_INTERACTION_SOURCE_FILES[family])
        raise InputError(
            f"Interaction family {family} requires exactly one source matrix ({expected}) in '{binary_root}'."
        )
    return candidates[0]


def _load_strict_interaction_matrix(path: Path, family: str) -> dict[tuple[str, str], tuple]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or ())
        rows = list(reader)
    for row_number, row in enumerate(rows, start=2):
        if row.get(None):
            raise InputError(f"Interaction matrix '{path}' row {row_number} contains surplus cells.")
    if len(fieldnames) < 2 or fieldnames[0] != "component":
        raise InputError(f"Interaction matrix '{path}' must begin with a component column.")
    columns = tuple(_normalize_component(str(value).strip()) for value in fieldnames[1:])
    if any(not component for component in columns) or len(set(columns)) != len(columns):
        raise InputError(f"Interaction matrix '{path}' has blank or duplicate component columns.")
    if len(rows) != len(columns):
        raise InputError(
            f"Interaction matrix '{path}' has invalid dimensions: {len(rows)} rows for {len(columns)} components."
        )
    row_labels = tuple(_normalize_component(str(row.get("component", "")).strip()) for row in rows)
    if any(not component for component in row_labels) or len(set(row_labels)) != len(row_labels):
        raise InputError(f"Interaction matrix '{path}' has blank or duplicate component rows.")
    if set(row_labels) != set(columns):
        raise InputError(f"Interaction matrix '{path}' row and column component identities differ.")
    matrix: dict[tuple[str, str], tuple] = {}
    original_columns = fieldnames[1:]
    for row, row_component in zip(rows, row_labels, strict=True):
        for original_column, column_component in zip(original_columns, columns, strict=True):
            matrix[(row_component, column_component)] = _interaction_value_signature(
                row.get(original_column),
                family=family,
                pair=(row_component, column_component),
            )
    for component in columns:
        diagonal = matrix[(component, component)]
        if diagonal != ("constant", 0.0):
            raise InputError(f"Interaction matrix {family} diagonal for {component} must be explicit zero.")
    for left_index, left in enumerate(columns):
        for right in columns[left_index + 1 :]:
            if matrix[(left, right)] != matrix[(right, left)]:
                raise InputError(f"Interaction matrix has asymmetric {family} values for pair {left}|{right}.")
    return matrix


def _interaction_value_signature(raw, *, family: str, pair: tuple[str, str]) -> tuple:
    text = "" if raw is None else str(raw).strip()
    if not text:
        raise InputError(f"Blank interaction cell for {family} pair {pair[0]}|{pair[1]}.")
    try:
        value = float(text)
    except ValueError:
        linear = _parse_linear_t_correlation(text)
        if linear is None:
            raise InputError(
                f"Unsupported interaction value '{text}' for {family} pair {pair[0]}|{pair[1]}."
            ) from None
        return ("linear_temperature", linear[0], linear[1])
    if not math.isfinite(value):
        raise InputError(f"Non-finite interaction cell for {family} pair {pair[0]}|{pair[1]}.")
    return ("constant", value)


def _parse_linear_t_correlation(raw: str) -> tuple[float, float] | None:
    text = str(raw).replace(" ", "").replace("/K", "").replace("/k", "")
    match = _LINEAR_T_RE.match(text)
    if not match:
        return None
    slope = _parse_t_coefficient(match.group(1))
    intercept = float(match.group(2).replace(" ", ""))
    if not math.isfinite(slope) or not math.isfinite(intercept):
        return None
    return slope, intercept


def _matrix_pair_signature(
    matrix: Mapping[tuple[str, str], tuple],
    *,
    family: str,
    left: str,
    right: str,
    display_pair: tuple[str, str],
) -> tuple:
    try:
        return matrix[(left, right)]
    except KeyError as exc:
        raise InputError(
            f"Interaction matrix {family} does not contain pair {display_pair[0]}|{display_pair[1]}."
        ) from exc


def _validate_interaction_manifest_matrix_identity(
    manifest: Mapping[tuple[str, frozenset[str]], tuple[tuple, str, str]],
    matrices: Mapping[str, Mapping[tuple[str, str], tuple]],
) -> None:
    for (family, component_set), (manifest_signature, _source, _status) in manifest.items():
        components = sorted(component_set)
        if len(components) != 2:
            raise InputError(f"Interaction source manifest has an invalid {family} component identity.")
        left, right = components
        matrix = matrices[family]
        if (left, right) not in matrix:
            raise InputError(
                f"Interaction source manifest pair {left}|{right} does not exist in the {family} matrix."
            )
        if matrix[(left, right)] != manifest_signature:
            raise InputError(
                f"Interaction source manifest value does not match matrix {family} pair {left}|{right}."
            )


def _load_interaction_source_manifest(
    path: Path,
) -> tuple[dict[tuple[str, frozenset[str]], tuple[tuple, str, str]], set[str]]:
    if not path.is_file():
        raise InputError(f"Interaction source manifest '{path}' does not exist.")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or ())
        rows = list(reader)
    for row_number, row in enumerate(rows, start=2):
        if row.get(None):
            raise InputError(f"Interaction source manifest '{path}' row {row_number} contains surplus cells.")
    required_columns = {"parameter", "component_i", "component_j", "value", "source"}
    allowed_columns = required_columns | {"provenance_status"}
    missing_columns = sorted(required_columns - fieldnames)
    if missing_columns:
        raise InputError(
            f"Interaction source manifest '{path}' is missing required column(s): {', '.join(missing_columns)}."
        )
    unknown_columns = sorted(fieldnames - allowed_columns)
    if unknown_columns:
        raise InputError(
            f"Interaction source manifest '{path}' contains unsupported column(s): {', '.join(unknown_columns)}."
        )
    manifest: dict[tuple[str, frozenset[str]], tuple[tuple, str, str]] = {}
    wildcard_families: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        family = str(row.get("parameter", "")).strip()
        if family == "k_hb":
            family = "k_hb_ij"
        if family not in _INTERACTION_SOURCE_FILES:
            raise InputError(f"Interaction source manifest row {row_number} has unknown family '{family}'.")
        left_raw = str(row.get("component_i", "")).strip()
        right_raw = str(row.get("component_j", "")).strip()
        if (left_raw == "*") != (right_raw == "*"):
            raise InputError(f"Interaction source manifest row {row_number} has a partial wildcard pair.")
        if left_raw == "*":
            if family in wildcard_families:
                raise InputError(f"Interaction source manifest has duplicate wildcard rows for {family}.")
            wildcard_signature = _interaction_value_signature(
                row.get("value"),
                family=family,
                pair=(left_raw, right_raw),
            )
            if wildcard_signature != ("constant", 0.0):
                raise InputError(f"Interaction source manifest wildcard for {family} must be explicit zero.")
            wildcard_families.add(family)
            continue
        left = _normalize_component(left_raw)
        right = _normalize_component(right_raw)
        if not left or not right or left == right:
            raise InputError(f"Interaction source manifest row {row_number} has an invalid component pair.")
        key = (family, frozenset((left, right)))
        if key in manifest:
            ordered = sorted((left_raw, right_raw))
            raise InputError(
                f"Duplicate interaction source record for {family} pair {ordered[0]}|{ordered[1]}."
            )
        signature = _interaction_value_signature(
            row.get("value"),
            family=family,
            pair=(left_raw, right_raw),
        )
        source = str(row.get("source", "")).strip()
        status = str(row.get("provenance_status", "")).strip()
        manifest[key] = (signature, source, status)
    return manifest, wildcard_families


def _load_mixed_rel_perm(path: Path) -> dict[str, dict[str, float]]:
    if not path.exists():
        return {}
    rows = _read_csv(path)
    mixed: dict[str, dict[str, float]] = {}
    for row in rows:
        organic = _normalize_component(str(row.get("organic", row.get("component", ""))).strip())
        if not organic:
            continue
        params: dict[str, float] = {}
        for key in ("a", "b", "c"):
            value = _maybe_float(row.get(key))
            if value is None:
                raise ValueError(f"Missing mixed rel_perm coefficient '{key}' for organic '{organic}'.")
            params[key] = float(value)
        mixed[organic] = params
    return mixed


def _load_specific_mixed_dielc_table(path: Path) -> list[dict]:
    if not path.exists():
        return []
    solvent_tokens = [token for token in path.stem.split("-") if token]
    rows = _read_csv(path)
    entries: list[dict] = []
    for row in rows:
        row_norm = {str(key).strip().lower(): value for key, value in row.items() if key}
        dielc = None
        for key in ("dielc", "rel_perm", "epsilon", "eps_r"):
            dielc = _maybe_float(row_norm.get(key))
            if dielc is not None:
                break
        if dielc is None:
            continue

        x_map: dict[str, float] = {}
        w_map: dict[str, float] = {}
        for token in solvent_tokens:
            x_val = None
            for alias in _solvent_fraction_aliases(token, "x"):
                x_val = _maybe_float(row_norm.get(alias.lower()))
                if x_val is not None:
                    break
            if x_val is not None:
                x_map[token] = float(x_val)

            w_val = None
            for alias in _solvent_fraction_aliases(token, "w"):
                w_val = _maybe_float(row_norm.get(alias.lower()))
                if w_val is not None:
                    break
            if w_val is not None:
                w_map[token] = float(w_val)

        if len(x_map) != len(solvent_tokens):
            raise ValueError(f"Mixed-permittivity table '{path}' requires explicit mole fractions for every solvent.")

        x_total = float(sum(x_map.values()))
        if x_total <= 0.0:
            continue
        x_norm = {token: value / x_total for token, value in x_map.items()}

        if len(w_map) != len(solvent_tokens):
            raise ValueError(
                f"Mixed-permittivity table '{path}' requires explicit mass fractions for every solvent."
            )

        w_total = float(sum(w_map.values()))
        if w_total <= 0.0:
            continue
        w_norm = {token: value / w_total for token, value in w_map.items()}

        entries.append(
            {
                "x": x_norm,
                "w": w_norm,
                "dielc": float(dielc),
            }
        )
    return entries


def _load_mixed_rel_perm_tables(rel_perm_dir: Path) -> dict[str, list[dict]]:
    tables: dict[str, list[dict]] = {}
    if not rel_perm_dir.exists():
        return tables
    for table_file in sorted(rel_perm_dir.glob("*.csv")):
        if table_file.stem.lower() == "parameters":
            continue
        table = _load_specific_mixed_dielc_table(table_file)
        if table:
            tables[table_file.stem] = table
    return tables


def _load_dataset(dataset_name_or_path) -> dict:
    cache_key, dataset_dir = _resolve_dataset_dir(dataset_name_or_path)
    if cache_key in _DATASET_CACHE:
        return _DATASET_CACHE[cache_key]

    dataset_name = str(dataset_name_or_path)
    if cache_key.startswith("path::"):
        dataset_name = str(dataset_dir)

    pure_dir = dataset_dir / "pure"
    pure_sets = _load_pure_sets(pure_dir)

    sole_pure_set_key = _sole_pure_set_key(pure_sets)
    pure_map: dict[str, dict[str, str]] = {}
    if sole_pure_set_key is not None:
        pure_map = pure_sets[sole_pure_set_key]

    if not pure_map and not pure_sets:
        raise FileNotFoundError(f"Dataset '{dataset_name}' must include pure/*.csv component-parameter files.")

    mixed_dir = dataset_dir / "mixed"
    rel_perm_dir = mixed_dir / "rel_perm"
    rel_perm_coeff_path = rel_perm_dir / "parameters.csv"
    data = {
        "dataset_name": dataset_name,
        "dataset_dir": dataset_dir,
        "pure": pure_map,
        "pure_sets": pure_sets,
        "sole_pure_set_key": sole_pure_set_key,
        "mixed_rel_perm": _load_mixed_rel_perm(rel_perm_coeff_path),
        "mixed_rel_perm_tables": _load_mixed_rel_perm_tables(rel_perm_dir),
        "canonical_user_options": _load_canonical_user_options(dataset_dir),
    }
    _DATASET_CACHE[cache_key] = data
    return data


def _invalidate_dataset_cache(dataset_name_or_path) -> None:
    cache_key, _dataset_dir = _resolve_dataset_dir(dataset_name_or_path)
    _DATASET_CACHE.pop(cache_key, None)


def _maybe_float(raw) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, (float, int, np.floating, np.integer)):
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError(f"Non-finite numeric value '{raw}'.")
        return value
    text = str(raw).strip()
    if not text:
        return None
    try:
        value = float(text)
        if not math.isfinite(value):
            raise ValueError(f"Non-finite numeric value '{text}'.")
        return value
    except ValueError as exc:
        if text.lower() in {"nan", "+nan", "-nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"}:
            raise ValueError(f"Non-finite numeric value '{text}'.") from exc
        return None


def _parse_t_coefficient(token: str) -> float:
    text = token.replace(" ", "")
    if "*10^" in text:
        mantissa, exponent = text.split("*10^", 1)
        return float(mantissa) * (10 ** int(exponent))
    return float(text)


def _parse_linear_t_expression(raw: str, T: float) -> float | None:
    text = raw.replace(" ", "")
    text = text.replace("/K", "").replace("/k", "")
    match = _LINEAR_T_RE.match(text)
    if not match:
        return None
    slope = _parse_t_coefficient(match.group(1))
    intercept = float(match.group(2).replace(" ", ""))
    return slope * T + intercept


def _parse_log_t_expression(raw: str, T: float) -> float | None:
    text = raw.replace(" ", "")
    match = _LOG_T_RE.match(text)
    if not match:
        return None
    coeff = float(match.group(1))
    intercept = float(match.group(2).replace(" ", ""))
    return coeff * np.log(T) + intercept


def _parse_association_scheme(raw: str) -> str | None:
    text = str(raw or "").strip()
    if not text:
        return None
    if text.lower() in {"nan", "none", "null"}:
        raise ValueError("Association topology must use a concrete scheme or a blank cell.")
    return text


def _parse_cell_value(raw, *, dataset: str, component: str, field: str, T: float):
    if field == "assoc_scheme":
        return _parse_association_scheme(raw)

    try:
        numeric = _maybe_float(raw)
    except ValueError as exc:
        raise ValueError(
            f"Dataset '{dataset}', component '{component}', field '{field}' must be finite."
        ) from exc
    if numeric is not None:
        return numeric

    text = str(raw or "").strip()
    if not text:
        return None

    if field == "dielc":
        log_t = _parse_log_t_expression(text, T)
        if log_t is not None:
            return log_t
        linear = _parse_linear_t_expression(text, T)
        if linear is not None:
            return linear

    raise ValueError(f"Unsupported value in dataset '{dataset}', component '{component}', field '{field}': '{text}'.")


def _resolve_component_field(dataset: dict, component: str, field: str, T: float, pure_set_key: str | None = None):
    selected_key = _normalize_pure_set_key(pure_set_key) if pure_set_key else dataset.get("sole_pure_set_key")
    if selected_key is None:
        raise ValueError(
            f"Dataset '{dataset['dataset_name']}' contains multiple pure parameter sets and requires "
            "an explicit versioned model configuration."
        )
    row = dataset.get("pure_sets", {}).get(selected_key, {}).get(component)
    if row is None:
        raise KeyError(
            f"Component '{component}' is missing in dataset '{dataset['dataset_name']}' pure set '{selected_key}'."
        )

    parsed = _parse_cell_value(
        row.get(field, ""),
        dataset=dataset["dataset_name"],
        component=component,
        field=field,
        T=T,
    )
    if field == "assoc_scheme" or parsed is not None:
        return parsed

    raise KeyError(
        f"Missing required value in dataset '{dataset['dataset_name']}', component '{component}', field '{field}'."
    )


def _resolve_component_field_with_source(
    dataset: dict,
    component: str,
    field: str,
    T: float,
    pure_set_key: str | None = None,
):
    source_key = _normalize_pure_set_key(pure_set_key) if pure_set_key else dataset.get("sole_pure_set_key")
    value = _resolve_component_field(dataset, component, field, T, pure_set_key=source_key)
    return value, source_key


def _as_rule_number(value, aliases: dict[str, int]) -> int:
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, str):
        key = value.strip().lower()
        if key.isdigit() or (key.startswith("-") and key[1:].isdigit()):
            return int(key)
        if key in aliases:
            return int(aliases[key])
    if not aliases and isinstance(value, str):
        key = value.strip().lower()
        if key.isdigit() or (key.startswith("-") and key[1:].isdigit()):
            return int(key)
    raise ValueError(f"Unknown rule option '{value}'. Supported aliases: {sorted(aliases.keys())}.")


def _resolve_born_bulk_mode(value) -> int:
    if isinstance(value, (int, np.integer)):
        mode = int(value)
        if mode in (0, 1):
            return mode
    key = str(value).strip().lower()
    if key in _BULK_MODE_ALIASES:
        return int(_BULK_MODE_ALIASES[key])
    raise ValueError("born bulk_mode must be one of {'mix','solvent'} (or 0/1).")


def _resolve_d_ion_mode(value) -> int:
    if isinstance(value, (int, np.integer)):
        mode = int(value)
    else:
        key = str(value).strip().lower()
        if key.isdigit() or (key.startswith("-") and key[1:].isdigit()):
            mode = int(key)
        elif key in _D_ION_MODE_ALIASES:
            mode = int(_D_ION_MODE_ALIASES[key])
        else:
            raise ValueError(
                f"Unknown d_ion_mode '{value}'. Supported values are 0,1,2 and aliases {sorted(_D_ION_MODE_ALIASES.keys())}."
            )
    if mode < 0 or mode > 2:
        raise ValueError("d_ion_mode must be in {0,1,2}.")
    return mode


def _resolve_d_born_mode(value) -> int:
    if isinstance(value, (int, np.integer)):
        mode = int(value)
    else:
        key = str(value).strip().lower()
        if key.isdigit() or (key.startswith("-") and key[1:].isdigit()):
            mode = int(key)
        elif key in _D_BORN_MODE_ALIASES:
            mode = int(_D_BORN_MODE_ALIASES[key])
        else:
            raise ValueError(
                f"Unknown d_Born_mode '{value}'. Supported values are 0,1,2,3 and aliases {sorted(_D_BORN_MODE_ALIASES.keys())}."
            )
    if mode < 0 or mode > 3:
        raise ValueError("d_Born_mode must be in {0,1,2,3}.")
    return mode


def _ensure_allowed_keys(mapping: dict, allowed: set[str], label: str) -> None:
    unknown = sorted(set(mapping) - set(allowed))
    if unknown:
        raise KeyError(f"{label} contains unsupported key(s): {unknown}.")


def _normalize_elec_model(model) -> dict:
    out = copy.deepcopy(_CANONICAL_ELEC_MODEL)
    if model is None:
        return out
    if not isinstance(model, dict):
        raise TypeError(f"elec_model must be a dict, got {type(model).__name__}.")

    _ensure_allowed_keys(
        model,
        {"rel_perm", "hc_model", "disp_model", "assoc_model", "DH_model", "include_born_model", "born_model"},
        "elec_model",
    )

    if "rel_perm" in model:
        if not isinstance(model["rel_perm"], dict):
            raise TypeError("elec_model['rel_perm'] must be a dict.")
        _ensure_allowed_keys(model["rel_perm"], {"rule", "differential_mode"}, "elec_model['rel_perm']")
        out["rel_perm"] = _deep_update(out["rel_perm"], model["rel_perm"])

    for key in ("hc_model", "disp_model", "assoc_model"):
        if key in model:
            if not isinstance(model[key], dict):
                raise TypeError(f"elec_model['{key}'] must be a dict.")
            _ensure_allowed_keys(model[key], {"dadx_differential_mode"}, f"elec_model['{key}']")
            out[key] = _deep_update(out[key], model[key])

    if "DH_model" in model:
        if not isinstance(model["DH_model"], dict):
            raise TypeError("elec_model['DH_model'] must be a dict.")
        _ensure_allowed_keys(
            model["DH_model"], {"d_ion_mode", "bjeruum_treatment", "mu_DH_model"}, "elec_model['DH_model']"
        )
        out["DH_model"] = _deep_update(out["DH_model"], model["DH_model"])

    if "include_born_model" in model:
        out["include_born_model"] = _coerce_bool(model["include_born_model"])

    if "born_model" in model:
        if not isinstance(model["born_model"], dict):
            raise TypeError("elec_model['born_model'] must be a dict.")
        _ensure_allowed_keys(
            model["born_model"],
            {"d_Born_mode", "solvation_shell_model", "dielectric_saturation", "bulk_mode", "mu_born_model"},
            "elec_model['born_model']",
        )
        out["born_model"] = _deep_update(out["born_model"], model["born_model"])

    # Canonical coercions.
    out["rel_perm"]["rule"] = _as_rule_number(out["rel_perm"]["rule"], _REL_PERM_RULE_ALIASES)
    out["rel_perm"]["differential_mode"] = _as_rule_number(out["rel_perm"]["differential_mode"], _DIFF_MODE_ALIASES)
    for key in ("hc_model", "disp_model", "assoc_model"):
        out[key]["dadx_differential_mode"] = _as_rule_number(out[key]["dadx_differential_mode"], _DIFF_MODE_ALIASES)
    out["DH_model"]["d_ion_mode"] = _resolve_d_ion_mode(out["DH_model"]["d_ion_mode"])
    out["DH_model"]["bjeruum_treatment"] = _coerce_bool(out["DH_model"]["bjeruum_treatment"])
    mu_dh_model = out["DH_model"].get("mu_DH_model", {})
    if not isinstance(mu_dh_model, dict):
        raise TypeError("elec_model['DH_model']['mu_DH_model'] must be a dict.")
    _ensure_allowed_keys(
        mu_dh_model,
        {"differential_mode", "comp_dep_rel_perm", "include_sum_term"},
        "elec_model['DH_model']['mu_DH_model']",
    )
    out["DH_model"]["mu_DH_model"] = _deep_update(_CANONICAL_ELEC_MODEL["DH_model"]["mu_DH_model"], mu_dh_model)
    out["DH_model"]["mu_DH_model"]["differential_mode"] = _as_rule_number(
        out["DH_model"]["mu_DH_model"]["differential_mode"], _DIFF_MODE_ALIASES
    )
    out["DH_model"]["mu_DH_model"]["comp_dep_rel_perm"] = _coerce_bool(
        out["DH_model"]["mu_DH_model"]["comp_dep_rel_perm"]
    )
    out["DH_model"]["mu_DH_model"]["include_sum_term"] = _coerce_bool(
        out["DH_model"]["mu_DH_model"]["include_sum_term"]
    )
    out["include_born_model"] = _coerce_bool(out["include_born_model"])

    born = out["born_model"]
    born["d_Born_mode"] = _resolve_d_born_mode(born["d_Born_mode"])
    born["solvation_shell_model"] = _coerce_bool(born["solvation_shell_model"])
    born["dielectric_saturation"] = _coerce_bool(born["dielectric_saturation"])
    born["bulk_mode"] = "solvent" if _resolve_born_bulk_mode(born["bulk_mode"]) == 1 else "mix"

    mu_born_model = born.get("mu_born_model", {})
    if not isinstance(mu_born_model, dict):
        raise TypeError("elec_model['born_model']['mu_born_model'] must be a dict.")
    _ensure_allowed_keys(
        mu_born_model,
        {"differential_mode", "comp_dep_rel_perm", "include_sum_term", "comp_dep_delta_d"},
        "elec_model['born_model']['mu_born_model']",
    )
    born["mu_born_model"] = _deep_update(_CANONICAL_ELEC_MODEL["born_model"]["mu_born_model"], mu_born_model)
    born["mu_born_model"]["differential_mode"] = _as_rule_number(
        born["mu_born_model"]["differential_mode"], _DIFF_MODE_ALIASES
    )
    born["mu_born_model"]["comp_dep_rel_perm"] = _coerce_bool(born["mu_born_model"]["comp_dep_rel_perm"])
    born["mu_born_model"]["include_sum_term"] = _coerce_bool(born["mu_born_model"]["include_sum_term"])
    born["mu_born_model"]["comp_dep_delta_d"] = _coerce_bool(born["mu_born_model"]["comp_dep_delta_d"])

    return out


def _flatten_model_to_runtime(model: dict) -> dict:
    rel_perm = model["rel_perm"]
    dh_model = model["DH_model"]
    mu_dh = dh_model["mu_DH_model"]
    born = model["born_model"]
    mu_born = born["mu_born_model"]

    include_born_model = _coerce_bool(model["include_born_model"])
    solvation_shell_model = _coerce_bool(born["solvation_shell_model"])
    dielectric_saturation = _coerce_bool(born["dielectric_saturation"])
    born_bulk_mode = _resolve_born_bulk_mode(born["bulk_mode"])
    mu_dh_diff_mode = _as_rule_number(mu_dh["differential_mode"], _DIFF_MODE_ALIASES)
    mu_born_diff_mode = _as_rule_number(mu_born["differential_mode"], _DIFF_MODE_ALIASES)

    return {
        "dielc_rule": int(rel_perm["rule"]),
        "dielc_diff_mode": int(rel_perm["differential_mode"]),
        "hc_dadx_diff_mode": int(_as_rule_number(model["hc_model"]["dadx_differential_mode"], _DIFF_MODE_ALIASES)),
        "disp_dadx_diff_mode": int(_as_rule_number(model["disp_model"]["dadx_differential_mode"], _DIFF_MODE_ALIASES)),
        "assoc_dadx_diff_mode": int(
            _as_rule_number(model["assoc_model"]["dadx_differential_mode"], _DIFF_MODE_ALIASES)
        ),
        "d_ion_mode": int(_resolve_d_ion_mode(dh_model["d_ion_mode"])),
        "bjeruum_treatment": _coerce_bool(dh_model["bjeruum_treatment"]),
        "mu_DH_diff_mode": int(mu_dh_diff_mode),
        "mu_DH_comp_dep_rel_perm": _coerce_bool(mu_dh["comp_dep_rel_perm"]),
        "mu_DH_include_sum_term": _coerce_bool(mu_dh["include_sum_term"]),
        "include_born_model": include_born_model,
        "d_Born_mode": int(_resolve_d_born_mode(born["d_Born_mode"])),
        "born_solvation_shell_model": solvation_shell_model,
        "born_dielectric_saturation": dielectric_saturation,
        "born_bulk_mode": int(born_bulk_mode),
        "mu_born_diff_mode": int(mu_born_diff_mode),
        "mu_born_comp_dep_rel_perm": _coerce_bool(mu_born["comp_dep_rel_perm"]),
        "mu_born_include_sum_term": _coerce_bool(mu_born["include_sum_term"]),
        "mu_born_comp_dep_delta_d": _coerce_bool(mu_born["comp_dep_delta_d"]),
    }


_PUBLIC_MODEL_OPTION_KEYS = {"differential_mode", "relative_permittivity_rule", "born_model"}


def _looks_like_public_model_options(user_options: dict) -> bool:
    if not user_options:
        return True
    if set(user_options) & _PUBLIC_MODEL_OPTION_KEYS:
        return True
    elec_model = user_options.get("elec_model")
    if isinstance(elec_model, dict):
        internal_elec_keys = {
            "rel_perm",
            "hc_model",
            "disp_model",
            "assoc_model",
            "DH_model",
            "include_born_model",
        }
        if set(elec_model) & internal_elec_keys:
            return False
        if set(elec_model) & _PUBLIC_MODEL_OPTION_KEYS:
            return True
        born_model = elec_model.get("born_model")
        if isinstance(born_model, dict) and set(born_model) & {"d_Born_mode", "mu_born_model"}:
            return False
        if isinstance(born_model, dict) and set(born_model) & {
            "enabled",
            "born_diameter_rule",
            "solvation_shell_model",
            "dielectric_saturation",
        }:
            return True
    return False


def _public_model_options_to_internal(user_options: dict) -> dict:
    from .options import ModelOptions

    model_payload: dict
    if "elec_model" in user_options:
        model_payload = {"elec_model": copy.deepcopy(user_options.get("elec_model", {}))}
    else:
        model_payload = {
            key: copy.deepcopy(user_options[key])
            for key in user_options
            if key in _PUBLIC_MODEL_OPTION_KEYS
        }
    internal = ModelOptions.from_user_options(model_payload).to_runtime_options()
    internal["elec_model"]["assoc_model"]["dadx_differential_mode"] = "auto"
    if "solvated_ion_diameter_mixing_rule" in user_options:
        internal["solvated_ion_diameter_mixing_rule"] = _coerce_bool(user_options["solvated_ion_diameter_mixing_rule"])
    if "ion_dispersion_mixing_rule" in user_options:
        internal["ion_dispersion_mixing_rule"] = _coerce_bool(user_options["ion_dispersion_mixing_rule"])
    return internal


def _resolve_runtime_options(user_options=None) -> dict:
    """Normalize user options into the canonical runtime model schema."""
    if user_options is None:
        user_options = {}
    if not isinstance(user_options, dict):
        raise TypeError("user_options must be a dict.")

    if _looks_like_public_model_options(user_options):
        user_options = _public_model_options_to_internal(user_options)

    allowed = {
        "elec_model",
        "solvated_ion_diameter_mixing_rule",
        "ion_dispersion_mixing_rule",
    }
    unknown = set(user_options) - allowed
    if unknown:
        raise KeyError(f"Unknown user_options key(s): {sorted(unknown)}")

    model = _normalize_elec_model(user_options.get("elec_model", {}))
    runtime = _flatten_model_to_runtime(model)
    runtime["solvated_ion_diameter_mixing_rule"] = _coerce_bool(
        user_options.get("solvated_ion_diameter_mixing_rule", False)
    )
    runtime["ion_dispersion_mixing_rule"] = _coerce_bool(user_options.get("ion_dispersion_mixing_rule", True))

    return {
        "runtime": runtime,
        "model": model,
        "preset_key": "dataset_canonical",
        "preset": {},
        "catalog": None,
    }


def _as_composition_array(x, size: int) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    if x_arr.ndim != 1 or x_arr.size != size:
        raise ValueError(f"x must be a 1D array-like vector with length {size}.")
    if not np.all(np.isfinite(x_arr)):
        raise ValueError("x contains non-finite values.")
    return x_arr


def _salt_free_neutral_fractions(x, charges) -> tuple[np.ndarray, np.ndarray]:
    x_arr = np.asarray(x, dtype=float)
    z_arr = np.asarray(charges, dtype=float)
    neutral_idx = np.flatnonzero(np.abs(z_arr) <= 1e-12)
    if neutral_idx.size == 0:
        return neutral_idx, np.array([], dtype=float)
    neutral_x = np.clip(x_arr[neutral_idx], 0.0, None)
    total = float(np.sum(neutral_x))
    if total <= 0.0:
        return neutral_idx, np.array([], dtype=float)
    return neutral_idx, neutral_x / total


def _lookup_specific_mixed_rel_perm(
    dataset: dict,
    components: list[str],
    charges,
    x,
    *,
    atol: float = 5.0e-6,
) -> tuple[float | None, str | None]:
    neutral_idx, neutral_sf = _salt_free_neutral_fractions(x, charges)
    if neutral_idx.size < 2 or neutral_sf.size != neutral_idx.size:
        return None, None

    token_fractions: dict[str, float] = {}
    tokens: list[str] = []
    for idx, frac in zip(neutral_idx, neutral_sf):
        token = _solvent_token_for_component(components[int(idx)])
        if token is None:
            return None, None
        tokens.append(token)
        token_fractions[token] = float(frac)

    system_key = _solvent_system_data_key(tokens)
    if not system_key:
        return None, None

    entries = dataset.get("mixed_rel_perm_tables", {}).get(system_key, [])
    if not entries:
        return None, None

    for entry in entries:
        entry_x = entry["x"]
        if set(entry_x) != set(token_fractions):
            continue
        if all(abs(float(entry_x[token]) - float(token_fractions[token])) <= atol for token in token_fractions):
            return float(entry["dielc"]), system_key
    return None, system_key


def _compute_constant_mixed_rel_perm(
    components: list[str],
    charges,
    dielc,
    x,
    mixed_rel_perm: dict[str, dict[str, float]],
) -> float | None:
    neutral_idx, neutral_sf = _salt_free_neutral_fractions(x, charges)
    if neutral_idx.size < 2 or neutral_sf.size != neutral_idx.size:
        return None

    water_pos = None
    for pos, idx in enumerate(neutral_idx):
        if components[idx] == "H2O":
            water_pos = pos
            break
    if water_pos is None:
        return None

    xw_sf = float(neutral_sf[water_pos])
    water_eps = float(dielc[neutral_idx[water_pos]])
    if xw_sf >= 1.0 - 1e-12:
        return water_eps

    x_org = 0.0
    eps_org_num = 0.0
    a_num = 0.0
    b_num = 0.0
    c_num = 0.0
    for pos, idx in enumerate(neutral_idx):
        if pos == water_pos:
            continue
        frac = float(neutral_sf[pos])
        if frac <= 0.0:
            continue
        coeffs = mixed_rel_perm.get(components[idx])
        if coeffs is None:
            return None
        x_org += frac
        eps_org_num += frac * float(dielc[idx])
        a_num += frac * float(coeffs["a"])
        b_num += frac * float(coeffs["b"])
        c_num += frac * float(coeffs["c"])

    if x_org <= 1e-12:
        return water_eps

    eps_org = eps_org_num / x_org
    if xw_sf <= 1e-12:
        return eps_org

    a_eff = a_num / x_org
    b_eff = b_num / x_org
    c_eff = c_num / x_org
    return eps_org + ((a_eff * xw_sf + b_eff) * xw_sf + c_eff) * xw_sf


def _compute_constant_salt_free_weight_avg_rel_perm(
    charges,
    dielc,
    mw,
    x,
) -> float | None:
    neutral_idx, neutral_sf = _salt_free_neutral_fractions(x, charges)
    if neutral_idx.size < 2 or neutral_sf.size != neutral_idx.size:
        return None

    mw_neutral = np.asarray(mw, dtype=float)[neutral_idx]
    if mw_neutral.size != neutral_sf.size or np.any(~np.isfinite(mw_neutral)) or np.any(mw_neutral <= 0.0):
        return None

    dielc_neutral = np.asarray(dielc, dtype=float)[neutral_idx]
    if dielc_neutral.size != neutral_sf.size or np.any(~np.isfinite(dielc_neutral)):
        return None

    mass_weights = neutral_sf * mw_neutral
    total_mass = float(np.sum(mass_weights))
    if total_mass <= 0.0:
        return None
    mass_weights = mass_weights / total_mass
    return float(np.dot(mass_weights, dielc_neutral))


def _apply_constant_mixed_rel_perm_precompute(
    prop_dic: dict,
    dataset: dict,
    components: list[str],
    x,
    rel_perm_rule: int,
) -> None:
    if int(rel_perm_rule) != 0:
        return
    exact_eps, exact_source = _lookup_specific_mixed_rel_perm(
        dataset=dataset,
        components=components,
        charges=prop_dic["z"],
        x=x,
    )
    if exact_eps is not None:
        mixed_eps = float(exact_eps)
        source = "specific"
    else:
        mixed_rel_perm = dataset.get("mixed_rel_perm", {})
        mixed_eps = None
        if mixed_rel_perm:
            mixed_eps = _compute_constant_mixed_rel_perm(
                components=components,
                charges=prop_dic["z"],
                dielc=prop_dic["dielc"],
                x=x,
                mixed_rel_perm=mixed_rel_perm,
            )
        if mixed_eps is None:
            mixed_eps = _compute_constant_salt_free_weight_avg_rel_perm(
                charges=prop_dic["z"],
                dielc=prop_dic["dielc"],
                mw=prop_dic["MW"],
                x=x,
            )
            if mixed_eps is None:
                return
            source = "salt_free_weight_average"
        else:
            source = "empirical"

    neutral_idx, _ = _salt_free_neutral_fractions(x, prop_dic["z"])
    if neutral_idx.size < 2:
        return

    dielc = np.asarray(prop_dic["dielc"], dtype=float).copy()
    dielc[neutral_idx] = float(mixed_eps)
    prop_dic["dielc"] = dielc
    prop_dic["mixed_solvent_rel_perm"] = float(mixed_eps)
    prop_dic["mixed_solvent_rel_perm_applied"] = True
    prop_dic["mixed_solvent_rel_perm_source"] = source
    if exact_source is not None:
        prop_dic["mixed_solvent_rel_perm_dataset"] = exact_source


def _apply_mixed_solvent_ion_sigma(
    prop_dic: dict,
    dataset: dict,
    components: list[str],
    x,
    T: float,
    enabled: bool,
) -> None:
    if not enabled:
        return

    neutral_idx, neutral_sf = _salt_free_neutral_fractions(x, prop_dic["z"])
    if neutral_idx.size < 2 or neutral_sf.size != neutral_idx.size:
        return

    pure_sets = dataset.get("pure_sets", {})
    if not pure_sets:
        raise ValueError(
            f"Dataset '{dataset['dataset_name']}' requires pure/*.csv solvent parameter sets for mixed ion sigma precompute."
        )

    sigma = np.asarray(prop_dic["s"], dtype=float).copy()
    mixed_sigmas: dict[str, float] = {}
    source_weights: dict[str, float] = {}
    for i, comp in enumerate(components):
        if abs(float(prop_dic["z"][i])) <= 1e-12:
            continue
        sigma_mix = 0.0
        for idx, frac in zip(neutral_idx, neutral_sf):
            solvent = components[int(idx)]
            pure_key = _ion_pure_set_key(dataset, solvent)
            sigma_value, source_key = _resolve_component_field_with_source(dataset, comp, "s", T, pure_set_key=pure_key)
            sigma_mix += float(frac) * float(sigma_value)
            resolved_key = source_key or pure_key
            source_name = f"pure/{resolved_key}.csv"
            source_weights[source_name] = source_weights.get(source_name, 0.0) + float(frac)
        sigma[i] = sigma_mix
        mixed_sigmas[comp] = float(sigma_mix)

    if mixed_sigmas:
        prop_dic["s"] = sigma
        prop_dic["mixed_ion_sigma"] = mixed_sigmas
        prop_dic["mixed_ion_sigma_applied"] = True
        prop_dic["mixed_ion_sigma_sources"] = source_weights


def _apply_mixed_solvent_ion_dispersion(
    prop_dic: dict,
    dataset: dict,
    components: list[str],
    x,
    T: float,
    enabled: bool,
) -> None:
    if not enabled:
        return

    neutral_idx, neutral_sf = _salt_free_neutral_fractions(x, prop_dic["z"])
    if neutral_idx.size < 2 or neutral_sf.size != neutral_idx.size:
        return

    pure_sets = dataset.get("pure_sets", {})
    if not pure_sets:
        raise ValueError(
            f"Dataset '{dataset['dataset_name']}' requires pure/*.csv solvent parameter sets for mixed ion dispersion precompute."
        )

    dispersion = np.asarray(prop_dic["e"], dtype=float).copy()
    mixed_dispersion: dict[str, float] = {}
    source_weights: dict[str, float] = {}
    for i, comp in enumerate(components):
        if abs(float(prop_dic["z"][i])) <= 1e-12:
            continue
        e_mix = 0.0
        for idx, frac in zip(neutral_idx, neutral_sf):
            solvent = components[int(idx)]
            pure_key = _ion_pure_set_key(dataset, solvent)
            e_value, source_key = _resolve_component_field_with_source(dataset, comp, "e", T, pure_set_key=pure_key)
            e_mix += float(frac) * float(e_value)
            resolved_key = source_key or pure_key
            source_name = f"pure/{resolved_key}.csv"
            source_weights[source_name] = source_weights.get(source_name, 0.0) + float(frac)
        dispersion[i] = e_mix
        mixed_dispersion[comp] = float(e_mix)

    if mixed_dispersion:
        prop_dic["e"] = dispersion
        prop_dic["mixed_ion_dispersion"] = mixed_dispersion
        prop_dic["mixed_ion_dispersion_applied"] = True
        prop_dic["mixed_ion_dispersion_sources"] = source_weights


def _explicit_component_values(
    species: tuple[str, ...],
    values: Mapping[str, float],
    *,
    field: str,
    positive: bool,
) -> dict[str, float]:
    if not isinstance(values, Mapping):
        raise TypeError(f"{field} must be a component-to-value mapping.")
    missing = [label for label in species if label not in values]
    if missing:
        raise ValueError(f"{field} is missing explicit values for: {', '.join(missing)}.")
    parsed = {label: float(values[label]) for label in species}
    invalid = [
        label
        for label, value in parsed.items()
        if not math.isfinite(value) or (positive and value <= 0.0)
    ]
    if invalid:
        condition = "finite and positive" if positive else "finite"
        raise ValueError(f"{field} must be {condition} for: {', '.join(invalid)}.")
    return parsed


def _electrolyte_stoichiometry(charges: Mapping[str, float]) -> tuple[str, str, int, int]:
    cations = [label for label, charge in charges.items() if charge > 0.0]
    anions = [label for label, charge in charges.items() if charge < 0.0]
    if len(cations) != 1 or len(anions) != 1:
        raise ValueError("Explicit charges must identify exactly one cation and one anion.")
    cation, anion = cations[0], anions[0]
    z_cat = abs(charges[cation])
    z_an = abs(charges[anion])
    z_cat_integer = round(z_cat)
    z_an_integer = round(z_an)
    if z_cat_integer <= 0 or z_an_integer <= 0 or not (
        math.isclose(z_cat, z_cat_integer, rel_tol=0.0, abs_tol=1.0e-12)
        and math.isclose(z_an, z_an_integer, rel_tol=0.0, abs_tol=1.0e-12)
    ):
        raise ValueError("Electrolyte stoichiometry requires nonzero integer component charges.")
    common = math.gcd(z_cat_integer, z_an_integer)
    return cation, anion, z_an_integer // common, z_cat_integer // common


def molality_to_molefraction(
    molality,
    *,
    species: Iterable[str],
    solvent: str,
    charges: Mapping[str, float],
    molar_masses: Mapping[str, float],
    basis_mass_kg: float = 1.0,
):
    """Convert molality using explicit component charges and molar masses."""

    labels = tuple(str(label) for label in species)
    if len(set(labels)) != len(labels):
        raise ValueError("species must contain unique component labels.")
    if solvent not in labels:
        raise ValueError(f"Solvent '{solvent}' is not present in species.")
    charge_values = _explicit_component_values(labels, charges, field="charges", positive=False)
    mass_values = _explicit_component_values(labels, molar_masses, field="molar_masses", positive=True)
    if charge_values[solvent] != 0.0:
        raise ValueError(f"Solvent '{solvent}' must have explicit zero charge.")
    cation, anion, cation_count, anion_count = _electrolyte_stoichiometry(charge_values)
    molality_value = float(molality)
    basis_value = float(basis_mass_kg)
    if not math.isfinite(molality_value) or molality_value < 0.0:
        raise ValueError("molality must be finite and non-negative.")
    if not math.isfinite(basis_value) or basis_value <= 0.0:
        raise ValueError("basis_mass_kg must be finite and positive.")

    amounts = {label: 0.0 for label in labels}
    amounts[solvent] = basis_value / mass_values[solvent]
    amounts[cation] = molality_value * basis_value * cation_count
    amounts[anion] = molality_value * basis_value * anion_count
    total = sum(amounts.values())
    return np.asarray([amounts[label] / total for label in labels], dtype=float)


def molefraction_to_molality(
    x,
    *,
    species: Iterable[str],
    solvent: str,
    charges: Mapping[str, float],
    molar_masses: Mapping[str, float],
):
    """Convert mole fractions to molality using explicit component data."""

    labels = tuple(str(label) for label in species)
    charge_values = _explicit_component_values(labels, charges, field="charges", positive=False)
    mass_values = _explicit_component_values(labels, molar_masses, field="molar_masses", positive=True)
    if solvent not in labels:
        raise ValueError(f"Solvent '{solvent}' is not present in species.")
    if charge_values[solvent] != 0.0:
        raise ValueError(f"Solvent '{solvent}' must have explicit zero charge.")
    cation, _anion, cation_count, _anion_count = _electrolyte_stoichiometry(charge_values)
    fractions = _as_composition_array(x, len(labels))
    if np.any(fractions < 0.0):
        raise ValueError("x must contain non-negative mole fractions.")
    solvent_fraction = float(fractions[labels.index(solvent)])
    if solvent_fraction <= 0.0:
        raise ValueError("Solvent mole fraction must be positive to compute molality.")
    cation_fraction = float(fractions[labels.index(cation)])
    return cation_fraction / (cation_count * solvent_fraction * mass_values[solvent])


def _resolve_dataset_runtime_payload(
    dataset_name: str | Path, species: Iterable[str], x, T: float, user_options: dict | None = None
) -> dict:
    """Resolve source-backed pure data and runtime options without interaction serialization."""
    dataset = _load_dataset(dataset_name)
    species = list(species)
    components = [_normalize_component(s) for s in species]
    x_arr = _as_composition_array(x, len(components))
    pure_set_key = dataset.get("sole_pure_set_key")

    merged_options = _deep_update(dataset["canonical_user_options"], user_options or {})
    resolved = _resolve_runtime_options(merged_options)
    runtime = resolved["runtime"]

    prop_dic: dict = {}
    for field in BASE_KEYS:
        values = [_resolve_component_field(dataset, comp, field, T, pure_set_key=pure_set_key) for comp in components]
        if field == "assoc_scheme":
            prop_dic[field] = [None if not str(value or "").strip() else str(value) for value in values]
        else:
            prop_dic[field] = np.asarray(values, dtype=float)

    for field in OPTIONAL_KEYS:
        values = [_resolve_component_field(dataset, comp, field, T, pure_set_key=pure_set_key) for comp in components]
        prop_dic[field] = np.asarray(values, dtype=float)

    n = len(species)
    mixed_rel_perm = dataset.get("mixed_rel_perm", {})
    if mixed_rel_perm:
        prop_dic["mixed_rel_perm_a"] = np.zeros(n, dtype=float)
        prop_dic["mixed_rel_perm_b"] = np.zeros(n, dtype=float)
        prop_dic["mixed_rel_perm_c"] = np.zeros(n, dtype=float)
        prop_dic["mixed_rel_perm_mask"] = np.zeros(n, dtype=int)
        water_index = -1
        for i, comp in enumerate(components):
            if comp == "H2O":
                water_index = i
            coeffs = mixed_rel_perm.get(comp)
            if coeffs is None:
                continue
            prop_dic["mixed_rel_perm_a"][i] = float(coeffs["a"])
            prop_dic["mixed_rel_perm_b"][i] = float(coeffs["b"])
            prop_dic["mixed_rel_perm_c"][i] = float(coeffs["c"])
            prop_dic["mixed_rel_perm_mask"][i] = 1
        prop_dic["mixed_rel_perm_water_index"] = int(water_index)

    _apply_constant_mixed_rel_perm_precompute(
        prop_dic=prop_dic,
        dataset=dataset,
        components=components,
        x=x_arr,
        rel_perm_rule=runtime["dielc_rule"],
    )
    _apply_mixed_solvent_ion_sigma(
        prop_dic=prop_dic,
        dataset=dataset,
        components=components,
        x=x_arr,
        T=T,
        enabled=bool(runtime["solvated_ion_diameter_mixing_rule"]),
    )
    _apply_mixed_solvent_ion_dispersion(
        prop_dic=prop_dic,
        dataset=dataset,
        components=components,
        x=x_arr,
        T=T,
        enabled=bool(runtime["ion_dispersion_mixing_rule"]),
    )

    if np.all(np.abs(prop_dic["z"]) < 1e-12):
        prop_dic["z"] = np.array([])

    prop_dic["elec_model"] = copy.deepcopy(resolved["model"])
    prop_dic["elec_model_dataset"] = dataset_name
    prop_dic["solvated_ion_diameter_mixing_rule"] = bool(runtime["solvated_ion_diameter_mixing_rule"])
    prop_dic["ion_dispersion_mixing_rule"] = bool(runtime["ion_dispersion_mixing_rule"])
    return prop_dic


def load_parameter_set(
    dataset_name: str | Path,
    species: Iterable[str],
    x,
    T: float,
    user_options: dict | None = None,
):
    """Resolve an explicit dataset path into canonical parameter records."""

    from .parameters import ParameterSet, PureRecord

    labels = tuple(str(label) for label in species)
    payload = _resolve_dataset_runtime_payload(dataset_name, labels, x, T, user_options=user_options)
    schemes = list(payload["assoc_scheme"])
    pure_records = tuple(
        PureRecord(
            component=label,
            molar_mass=float(payload["MW"][index]),
            m=float(payload["m"][index]),
            sigma=float(payload["s"][index]),
            epsilon_k=float(payload["e"][index]),
            charge=(float(payload["z"][index]) if np.asarray(payload["z"]).size else 0.0),
            epsilon_k_ab=float(payload["e_assoc"][index]),
            kappa_ab=float(payload["vol_a"][index]),
            association_scheme=schemes[index],
            relative_permittivity=float(payload["dielc"][index]),
            born_diameter=float(payload["d_born"][index]),
            solvation_factor=float(payload["f_solv"][index]),
        )
        for index, label in enumerate(labels)
    )
    interactions = _load_source_interactions(dataset_name, labels)

    parameter_keys = {
        "MW",
        "m",
        "s",
        "e",
        "e_assoc",
        "vol_a",
        "assoc_scheme",
        "z",
        "dielc",
        "d_born",
        "f_solv",
    }
    runtime_options = {key: value for key, value in payload.items() if key not in parameter_keys}
    dataset = _load_dataset(dataset_name)
    source_key = dataset.get("sole_pure_set_key")
    rows = dataset.get("pure_sets", {}).get(source_key, {}) if source_key else {}
    normalized_labels = tuple(_normalize_component(label) for label in labels)
    sources = [str(rows[label].get("source", "")).strip() for label in normalized_labels if label in rows]
    metadata = {
        "dataset": str(dataset_name),
        "source": "; ".join(dict.fromkeys(source for source in sources if source)),
        "source_backed": len(sources) == len(labels) and all(sources),
        "T": float(T),
    }
    return ParameterSet.from_records(
        pure_records,
        interactions,
        metadata=metadata,
        runtime_options=runtime_options,
    )


def get_prop_dict(
    dataset_name: str | Path,
    species: Iterable[str],
    x,
    T: float,
    user_options: dict | None = None,
) -> dict:
    """Build a runtime payload through the canonical typed ParameterSet owner."""

    return load_parameter_set(dataset_name, species, x, T, user_options=user_options).to_runtime_dict()
