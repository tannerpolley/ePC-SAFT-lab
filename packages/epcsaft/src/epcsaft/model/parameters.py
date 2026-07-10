"""Strict canonical parameter records and native-payload serialization."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from .._types import InputError
from .sources import (
    copy_parameter_mapping as _copy_payload_mapping,
)
from .sources import (
    copy_parameter_value as _copy_payload_value,
)
from .sources import (
    deep_update_parameter_mapping as _deep_update_mapping,
)
from .sources import (
    load_canonical_user_options as _load_canonical_user_options,
)

_PURE_PARAMETER_KEYS = {
    "MW",
    "molar_mass",
    "m",
    "s",
    "sigma",
    "e",
    "epsilon_k",
    "z",
    "charge",
    "e_assoc",
    "epsilon_k_ab",
    "vol_a",
    "kappa_ab",
    "assoc_scheme",
    "association_scheme",
    "dielc",
    "relative_permittivity",
    "d_born",
    "born_diameter",
    "f_solv",
    "solvation_factor",
}
_BINARY_PARAMETER_KEYS = {"k_ij", "l_ij", "k_hb", "k_hb_ij"}
_GENERATED_PARAMETER_KEYS = {"assoc_num", "assoc_matrix"}
_PROVENANCE_METADATA_KEYS = (
    "source",
    "dataset",
    "paper",
    "doi",
    "table",
    "figure",
    "source_file",
    "source_path",
)
_STRUCTURAL_KEYS = {
    "schema",
    "schema_version",
    "components",
    "pure_records",
    "binary_records",
    "metadata",
    "runtime_options",
}
_PARAMETER_PAYLOAD_KEYS = _PURE_PARAMETER_KEYS | _BINARY_PARAMETER_KEYS | _GENERATED_PARAMETER_KEYS | _STRUCTURAL_KEYS
_NATIVE_RUNTIME_PASSTHROUGH_KEYS = {
    "mixed_rel_perm_a",
    "mixed_rel_perm_b",
    "mixed_rel_perm_c",
    "mixed_rel_perm_mask",
    "mixed_rel_perm_water_index",
    "mixed_ion_sigma",
    "mixed_ion_sigma_applied",
    "mixed_ion_sigma_sources",
    "mixed_ion_dispersion",
    "mixed_ion_dispersion_applied",
    "mixed_ion_dispersion_sources",
}

PARAMETER_SET_SCHEMA = "epcsaft.parameter-set"
PARAMETER_SET_SCHEMA_VERSION = 1
_CANONICAL_TOP_LEVEL_KEYS = {
    "schema",
    "schema_version",
    "components",
    "pure_records",
    "binary_records",
    "metadata",
    "runtime_options",
}
_CANONICAL_PURE_RECORD_KEYS = {
    "component",
    "molar_mass",
    "molar_mass_units",
    "m",
    "sigma",
    "epsilon_k",
    "charge",
    "epsilon_k_ab",
    "kappa_ab",
    "association_scheme",
    "association_sites",
    "relative_permittivity",
    "born_diameter",
    "solvation_factor",
}
_REQUIRED_PURE_SCIENTIFIC_FIELDS = {
    "molar_mass",
    "molar_mass_units",
    "m",
    "sigma",
    "epsilon_k",
    "charge",
    "epsilon_k_ab",
    "kappa_ab",
    "association_scheme",
    "relative_permittivity",
    "born_diameter",
    "solvation_factor",
}


@dataclass(frozen=True, slots=True)
class ComponentIdentifier:
    """Stable component identifier for canonical parameter records."""

    name: str
    aliases: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _nonblank_identity(self.name, "component name"))
        object.__setattr__(
            self,
            "aliases",
            tuple(_nonblank_identity(alias, "component alias") for alias in self.aliases),
        )


@dataclass(frozen=True, slots=True)
class AssociationSite:
    """One named association site on a component."""

    label: str
    kind: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", _nonblank_identity(self.label, "association_sites.label"))
        object.__setattr__(self, "kind", _nonblank_identity(self.kind, "association_sites.kind"))


@dataclass(frozen=True, slots=True)
class PureRecord:
    """Canonical pure-component ePC-SAFT parameters.

    ``molar_mass`` is stored in kg/mol to match the native ``MW`` input.
    Use :meth:`from_g_per_mol` when source tables report g/mol.
    """

    component: str | ComponentIdentifier
    molar_mass: float
    m: float
    sigma: float
    epsilon_k: float
    charge: float
    epsilon_k_ab: float
    kappa_ab: float
    association_scheme: str | None
    relative_permittivity: float
    born_diameter: float
    solvation_factor: float
    association_sites: tuple[AssociationSite, ...] = ()

    def __post_init__(self) -> None:
        component = (
            self.component.name
            if isinstance(self.component, ComponentIdentifier)
            else _nonblank_identity(self.component, "component")
        )
        object.__setattr__(self, "component", component)
        object.__setattr__(self, "association_sites", tuple(self.association_sites))
        scheme = None if self.association_scheme is None else str(self.association_scheme).strip()
        object.__setattr__(self, "association_scheme", scheme or None)
        for field_name in (
            "molar_mass",
            "m",
            "sigma",
            "epsilon_k",
            "charge",
            "epsilon_k_ab",
            "kappa_ab",
            "relative_permittivity",
            "born_diameter",
            "solvation_factor",
        ):
            object.__setattr__(self, field_name, float(getattr(self, field_name)))
        if not np.isfinite(float(self.molar_mass)) or float(self.molar_mass) <= 0.0:
            raise InputError(f"{component}.molar_mass must be finite and positive in kg/mol.")
        if float(self.molar_mass) > 1.0:
            raise InputError(
                f"PureRecord.molar_mass is interpreted as kg/mol. Got {float(self.molar_mass)} for {component}. "
                "Use a kg/mol value such as 18.01528e-3, or use PureRecord.from_g_per_mol(...)."
            )
        for field_name in ("m", "sigma", "epsilon_k", "relative_permittivity", "solvation_factor"):
            value = float(getattr(self, field_name))
            if not np.isfinite(value) or value <= 0.0:
                raise InputError(f"{component}.{field_name} must be finite and positive.")
        if not np.isfinite(float(self.charge)):
            raise InputError(f"{component}.charge must be finite.")
        for field_name in ("epsilon_k_ab", "kappa_ab", "born_diameter"):
            value = float(getattr(self, field_name))
            if not np.isfinite(value) or value < 0.0:
                raise InputError(f"{component}.{field_name} must be finite and non-negative.")
        association_active = self.association_scheme is not None
        if association_active and (float(self.epsilon_k_ab) <= 0.0 or float(self.kappa_ab) <= 0.0):
            raise InputError(
                f"{component} association parameters epsilon_k_ab and kappa_ab must be finite and positive "
                "when association_scheme is active."
            )
        if not association_active and (float(self.epsilon_k_ab) != 0.0 or float(self.kappa_ab) != 0.0):
            raise InputError(
                f"{component}.association_scheme must identify the topology when association parameters are nonzero."
            )
        if not association_active and self.association_sites:
            raise InputError(f"{component}.association_sites require an active association_scheme.")
        if abs(float(self.charge)) > 0.0 and float(self.born_diameter) <= 0.0:
            raise InputError(f"{component}.born_diameter must be finite and positive for a charged component.")

    @classmethod
    def from_g_per_mol(
        cls,
        component: str | ComponentIdentifier,
        *,
        molar_mass_g_per_mol: float,
        m: float,
        sigma: float,
        epsilon_k: float,
        charge: float,
        epsilon_k_ab: float,
        kappa_ab: float,
        association_scheme: str | None,
        relative_permittivity: float,
        born_diameter: float,
        solvation_factor: float,
        association_sites: Sequence[AssociationSite] = (),
    ) -> PureRecord:
        """Construct a pure record from a source molar mass reported in g/mol."""
        value = float(molar_mass_g_per_mol)
        if not np.isfinite(value) or value <= 0.0:
            raise InputError("molar_mass_g_per_mol must be finite and positive.")
        return cls(
            component=component,
            molar_mass=value * 1.0e-3,
            m=m,
            sigma=sigma,
            epsilon_k=epsilon_k,
            charge=charge,
            epsilon_k_ab=epsilon_k_ab,
            kappa_ab=kappa_ab,
            association_scheme=association_scheme,
            association_sites=tuple(association_sites),
            relative_permittivity=relative_permittivity,
            born_diameter=born_diameter,
            solvation_factor=solvation_factor,
        )


@dataclass(frozen=True, slots=True)
class BinaryRecord:
    """Canonical binary interaction record."""

    components: tuple[str, str]
    k_ij: float = 0.0
    l_ij: float = 0.0
    k_hb_ij: float = 0.0

    def __post_init__(self) -> None:
        if len(self.components) != 2:
            raise InputError("BinaryRecord.components must contain exactly two component labels.")
        object.__setattr__(self, "components", (str(self.components[0]), str(self.components[1])))
        object.__setattr__(self, "k_ij", float(self.k_ij))
        object.__setattr__(self, "l_ij", float(self.l_ij))
        object.__setattr__(self, "k_hb_ij", float(self.k_hb_ij))


@dataclass(frozen=True, slots=True)
class PermittivityRecord:
    """Canonical relative-permittivity record for one component."""

    component: str
    relative_permittivity: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "component", str(self.component))
        object.__setattr__(self, "relative_permittivity", float(self.relative_permittivity))


@dataclass(frozen=True, slots=True)
class ParameterSet:
    """Canonical parameter set with one native-payload serializer."""

    components: tuple[str, ...]
    pure_records: tuple[PureRecord, ...]
    binary_records: tuple[BinaryRecord, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    runtime_options: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        components = tuple(str(component) for component in self.components)
        object.__setattr__(self, "components", components)
        object.__setattr__(self, "pure_records", tuple(self.pure_records))
        object.__setattr__(self, "binary_records", tuple(self.binary_records))
        object.__setattr__(self, "metadata", dict(self.metadata))
        object.__setattr__(self, "runtime_options", _copy_payload_mapping(self.runtime_options))
        self.validate()

    @classmethod
    def from_records(
        cls,
        pure_records: Sequence[PureRecord],
        binary_records: Sequence[BinaryRecord] | None = None,
        *,
        metadata: Mapping[str, Any] | None = None,
        runtime_options: Mapping[str, Any] | None = None,
    ) -> ParameterSet:
        pure = tuple(pure_records)
        return cls(
            components=tuple(str(record.component) for record in pure),
            pure_records=pure,
            binary_records=tuple(binary_records or ()),
            metadata=dict(metadata or {}),
            runtime_options=_copy_payload_mapping(runtime_options),
        )

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
        *,
        species: Sequence[str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ParameterSet:
        if not isinstance(payload, Mapping):
            raise InputError("ParameterSet.from_dict requires a mapping in the versioned canonical schema.")
        canonical = {str(key): value for key, value in payload.items()}
        schema_version = canonical.get("schema_version")
        if (
            canonical.get("schema") != PARAMETER_SET_SCHEMA
            or type(schema_version) is not int
            or schema_version != PARAMETER_SET_SCHEMA_VERSION
        ):
            raise InputError(
                "ParameterSet.from_dict accepts only the versioned canonical schema "
                "'epcsaft.parameter-set' with schema_version 1; "
                "parallel-array and unversioned payloads are rejected."
            )
        return cls._from_canonical_payload(canonical, species=species, metadata=metadata)

    @classmethod
    def _from_canonical_payload(
        cls,
        payload: Mapping[str, Any],
        *,
        species: Sequence[str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ParameterSet:
        unknown = sorted(set(payload) - _CANONICAL_TOP_LEVEL_KEYS)
        if unknown:
            raise InputError(f"canonical parameter payload contains unsupported key(s): {', '.join(unknown)}.")
        payload_components_raw = _canonical_array(payload, "components")
        pure_payloads = _canonical_array(payload, "pure_records")
        binary_payloads = _canonical_array(payload, "binary_records")
        if not pure_payloads:
            raise InputError("canonical parameter payload must include pure_records.")
        if not payload_components_raw:
            raise InputError("canonical parameter payload components must contain at least one component label.")
        payload_components = tuple(
            _nonblank_identity(item, f"components[{index}]")
            for index, item in enumerate(payload_components_raw)
        )
        if species is not None and tuple(str(item) for item in species) != payload_components:
            raise InputError("canonical parameter dataset species must match payload components in order.")
        payload_metadata_raw = payload.get("metadata", {})
        runtime_options_raw = payload.get("runtime_options", {})
        if not isinstance(payload_metadata_raw, Mapping):
            raise InputError("canonical parameter payload metadata must be a JSON object.")
        if not isinstance(runtime_options_raw, Mapping):
            raise InputError("canonical parameter payload runtime_options must be a JSON object.")
        if metadata is not None and not isinstance(metadata, Mapping):
            raise InputError("ParameterSet.from_dict metadata override must be a mapping.")
        payload_metadata = _copy_payload_mapping(payload_metadata_raw)
        payload_metadata.update(_copy_payload_mapping(metadata))
        return cls(
            components=payload_components,
            pure_records=tuple(_pure_record_from_canonical(item) for item in pure_payloads),
            binary_records=tuple(_binary_record_from_canonical(item) for item in binary_payloads),
            metadata=payload_metadata,
            runtime_options=_copy_payload_mapping(runtime_options_raw),
        )

    @classmethod
    def from_json(
        cls,
        path: str | Path,
        *,
        species: Sequence[str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ParameterSet:
        """Load a canonical parameter-set JSON file or folder."""
        json_path = Path(path).expanduser()
        if json_path.is_dir():
            json_path = json_path / "parameter_set.json"
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise InputError(f"Canonical parameter file '{json_path}' must contain a JSON object.")
        return cls.from_dict(payload, species=species, metadata=metadata)

    @classmethod
    def from_dataset(
        cls,
        dataset_name: str | Path,
        species: Sequence[str],
        x: Sequence[float] | None = None,
        T: float = 298.15,
        user_options: Mapping[str, Any] | None = None,
    ) -> ParameterSet:
        from .datasets import load_parameter_set

        dataset_path = Path(dataset_name).expanduser()
        canonical_path = dataset_path / "parameter_set.json"
        if dataset_path.is_dir() and canonical_path.exists():
            params = cls.from_json(
                canonical_path,
                species=species,
                metadata={"dataset": str(dataset_name), "T": float(T)},
            )
            runtime_options = _deep_update_mapping(
                params.runtime_options,
                _load_canonical_user_options(dataset_path),
            )
            runtime_options = _deep_update_mapping(runtime_options, user_options or {})
            return cls(
                components=params.components,
                pure_records=params.pure_records,
                binary_records=params.binary_records,
                metadata=params.metadata,
                runtime_options=runtime_options,
            )

        composition = x if x is not None else [1.0 / len(species)] * len(species)
        return load_parameter_set(dataset_name, species, composition, T, user_options=user_options)

    @classmethod
    def from_folder(
        cls,
        path: str | Path,
        *,
        components: Sequence[str] | None = None,
        user_options: Mapping[str, Any] | None = None,
    ) -> ParameterSet:
        """Load parameters from a canonical parameter-set folder."""

        root = Path(path).expanduser()
        if not root.is_dir():
            raise InputError(f"Parameter folder '{root}' does not exist.")
        canonical_path = root / "parameter_set.json"
        if not canonical_path.is_file():
            raise InputError(f"Parameter folder '{root}' must contain parameter_set.json.")
        params = cls.from_json(canonical_path, species=components)
        return _parameter_set_with_runtime_options(params, user_options)

    def validate(self) -> dict[str, Any]:
        errors: list[str] = []
        if len(set(self.components)) != len(self.components):
            errors.append("ParameterSet components must be unique.")
        seen = set()
        for record in self.pure_records:
            label = str(record.component)
            if label in seen:
                errors.append(f"Duplicate component record for {label}.")
            seen.add(label)
            for field_name in ("molar_mass", "m", "sigma", "epsilon_k"):
                value = float(getattr(record, field_name))
                if not np.isfinite(value) or value <= 0.0:
                    errors.append(f"{label}.{field_name} must be finite and positive.")
        missing = [label for label in self.components if label not in seen]
        if missing:
            errors.append(f"Missing pure records for components: {', '.join(missing)}.")
        known = set(self.components)
        undeclared = sorted(seen - known)
        if undeclared:
            errors.append(f"ParameterSet contains pure records for undeclared components: {', '.join(undeclared)}.")
        for record in self.binary_records:
            for label in record.components:
                if label not in known:
                    errors.append(f"BinaryRecord references unknown component {label}.")
        reserved = sorted(set(self.runtime_options) & _PARAMETER_PAYLOAD_KEYS)
        if reserved:
            errors.append(f"runtime_options cannot override parameter payload keys: {', '.join(reserved)}.")
        source_backed = self.metadata.get("source_backed", False)
        if "source_backed" in self.metadata and type(source_backed) is not bool:
            errors.append("metadata.source_backed must be a boolean.")
        elif source_backed and not _provenance_metadata_fields(self.metadata):
            errors.append("source_backed parameter metadata requires a nonblank source identity.")
        if errors:
            raise InputError("; ".join(errors))
        return {
            "valid": True,
            "component_count": len(self.components),
            "binary_count": len(self.binary_records),
            "runtime_option_count": len(self.runtime_options),
        }

    def to_runtime_dict(self, user_options: Mapping[str, Any] | None = None) -> dict[str, Any]:
        records = {str(record.component): record for record in self.pure_records}
        ordered = [records[label] for label in self.components]
        charge_vector = np.asarray([record.charge for record in ordered], dtype=float)
        payload: dict[str, Any] = {
            "MW": np.asarray([record.molar_mass for record in ordered], dtype=float),
            "m": np.asarray([record.m for record in ordered], dtype=float),
            "s": np.asarray([record.sigma for record in ordered], dtype=float),
            "e": np.asarray([record.epsilon_k for record in ordered], dtype=float),
            "e_assoc": np.asarray([record.epsilon_k_ab for record in ordered], dtype=float),
            "vol_a": np.asarray([record.kappa_ab for record in ordered], dtype=float),
            "assoc_scheme": [
                None if record.association_scheme in (None, "") else str(record.association_scheme)
                for record in ordered
            ],
            "z": charge_vector if np.any(np.abs(charge_vector) > 1.0e-12) else np.asarray([], dtype=float),
            "dielc": np.asarray([record.relative_permittivity for record in ordered], dtype=float),
            "d_born": np.asarray([record.born_diameter for record in ordered], dtype=float),
            "f_solv": np.asarray([record.solvation_factor for record in ordered], dtype=float),
        }
        ncomp = len(self.components)
        matrices = {
            "k_ij": np.zeros((ncomp, ncomp), dtype=float),
            "l_ij": np.zeros((ncomp, ncomp), dtype=float),
            "k_hb": np.zeros((ncomp, ncomp), dtype=float),
        }
        index = {label: idx for idx, label in enumerate(self.components)}
        for record in self.binary_records:
            i, j = index[record.components[0]], index[record.components[1]]
            matrices["k_ij"][i, j] = matrices["k_ij"][j, i] = record.k_ij
            matrices["l_ij"][i, j] = matrices["l_ij"][j, i] = record.l_ij
            matrices["k_hb"][i, j] = matrices["k_hb"][j, i] = record.k_hb_ij
        payload.update(matrices)
        runtime_options = _normalize_runtime_user_options(_deep_update_mapping(self.runtime_options, user_options or {}))
        reserved = sorted(set(runtime_options) & _PARAMETER_PAYLOAD_KEYS)
        if reserved:
            raise InputError(f"runtime_options cannot override parameter payload keys: {', '.join(reserved)}.")
        payload.update(runtime_options)
        payload.update(_runtime_parameter_provenance_payload(self.metadata, bool(self.binary_records)))
        return payload

    def to_json(self, path: str | Path | None = None) -> str:
        payload = {
            "schema": PARAMETER_SET_SCHEMA,
            "schema_version": PARAMETER_SET_SCHEMA_VERSION,
            "components": list(self.components),
            "pure_records": [_pure_record_json(record) for record in self.pure_records],
            "binary_records": [asdict(record) for record in self.binary_records],
            "metadata": _json_ready(self.metadata),
            "runtime_options": _json_ready(self.runtime_options),
        }
        text = json.dumps(payload, indent=2, sort_keys=True)
        if path is not None:
            Path(path).write_text(text + "\n", encoding="utf-8")
        return text


@dataclass(frozen=True, slots=True)
class ParameterSource:
    """Canonical resolver for parameter source labels and runtime payloads."""

    source: str | Path | Mapping[str, Any] | ParameterSet
    species: Sequence[str] | None = None

    def __post_init__(self) -> None:
        if self.species is not None:
            object.__setattr__(self, "species", tuple(str(label) for label in self.species))

    @property
    def label(self) -> str:
        """Return a stable human-readable label for reports and diagnostics."""
        if isinstance(self.source, ParameterSet):
            source = self.source.metadata.get("dataset", self.source.metadata.get("source"))
            return str(source) if source not in (None, "") else "ParameterSet"
        if isinstance(self.source, Mapping):
            metadata = self.source.get("metadata")
            if isinstance(metadata, Mapping):
                source = metadata.get("dataset", metadata.get("source"))
                if source not in (None, ""):
                    return str(source)
            source = self.source.get("dataset", self.source.get("source"))
            return str(source) if source not in (None, "") else "parameter-payload"
        return str(self.source)

    def to_parameter_set(
        self,
        species: Sequence[str] | None = None,
        x: Sequence[float] | None = None,
        T: float = 298.15,
        user_options: Mapping[str, Any] | None = None,
    ) -> ParameterSet:
        """Resolve this source into a canonical parameter set."""
        labels = _resolve_parameter_source_species(self.species, species)
        if isinstance(self.source, ParameterSet):
            _require_parameter_source_species(labels, self.source.components, "ParameterSet")
            return _parameter_set_with_runtime_options(self.source, user_options)
        if isinstance(self.source, Mapping):
            params = ParameterSet.from_dict(self.source, species=labels)
            return _parameter_set_with_runtime_options(params, user_options)
        if labels is None:
            raise InputError("ParameterSource species must be provided for dataset sources.")
        composition = x if x is not None else [1.0 / len(labels)] * len(labels)
        return ParameterSet.from_dataset(self.source, labels, composition, T, user_options=user_options)

    def to_runtime_dict(
        self,
        species: Sequence[str] | None = None,
        x: Sequence[float] | None = None,
        T: float = 298.15,
        user_options: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Resolve this source into the native runtime payload."""
        return self.to_parameter_set(species=species, x=x, T=T, user_options=user_options).to_runtime_dict()


def _pure_record_from_canonical(payload: Mapping[str, Any]) -> PureRecord:
    if not isinstance(payload, Mapping):
        raise InputError("canonical pure_records entries must be mappings.")
    component = str(payload.get("component", "")).strip()
    if not component:
        raise InputError("canonical pure record requires component.")
    unknown = sorted(set(payload) - _CANONICAL_PURE_RECORD_KEYS)
    if unknown:
        raise InputError(f"{component} canonical pure record contains unsupported key(s): {', '.join(unknown)}.")
    missing = sorted(field_name for field_name in _REQUIRED_PURE_SCIENTIFIC_FIELDS if field_name not in payload)
    if missing:
        raise InputError("; ".join(f"{component}.{field_name} must be explicit in canonical parameter data." for field_name in missing))
    molar_mass = _required_float(payload, "molar_mass", component)
    units = str(payload["molar_mass_units"]).strip().lower()
    if units in {"g/mol", "g per mol", "g mol^-1"}:
        molar_mass *= 1.0e-3
    elif units not in {"kg/mol", "kg per mol", "kg mol^-1"}:
        raise InputError(f"{component}.molar_mass_units must be 'kg/mol' or 'g/mol'.")
    association_sites_raw = payload.get("association_sites", [])
    if not isinstance(association_sites_raw, list):
        raise InputError(f"{component}.association_sites must be a JSON array.")
    association_sites = tuple(_association_site_from_canonical(item) for item in association_sites_raw)
    return PureRecord(
        component=component,
        molar_mass=molar_mass,
        m=_required_float(payload, "m", component),
        sigma=_required_float(payload, "sigma", component),
        epsilon_k=_required_float(payload, "epsilon_k", component),
        charge=_required_float(payload, "charge", component),
        epsilon_k_ab=_required_float(payload, "epsilon_k_ab", component),
        kappa_ab=_required_float(payload, "kappa_ab", component),
        association_scheme=_required_nullable_text(payload, "association_scheme", component),
        association_sites=association_sites,
        relative_permittivity=_required_float(payload, "relative_permittivity", component),
        born_diameter=_required_float(payload, "born_diameter", component),
        solvation_factor=_required_float(payload, "solvation_factor", component),
    )


def _association_site_from_canonical(payload: Any) -> AssociationSite:
    if not isinstance(payload, Mapping):
        raise InputError("association_sites entries must be mappings with explicit label and kind fields.")
    unknown = sorted(set(payload) - {"label", "kind"})
    if unknown:
        raise InputError(f"association_sites entry contains unsupported key(s): {', '.join(unknown)}.")
    missing = sorted({"label", "kind"} - set(payload))
    if missing:
        raise InputError(f"association_sites entry requires explicit field(s): {', '.join(missing)}.")
    return AssociationSite(label=payload["label"], kind=payload["kind"])


def _binary_record_from_canonical(payload: Mapping[str, Any]) -> BinaryRecord:
    return BinaryRecord(
        components=tuple(str(item) for item in payload.get("components", ())),
        k_ij=_optional_float(payload, "k_ij", 0.0),
        l_ij=_optional_float(payload, "l_ij", 0.0),
        k_hb_ij=_optional_float(payload, "k_hb_ij", 0.0),
    )


def _required_float(payload: Mapping[str, Any], key: str, component: str) -> float:
    value = payload.get(key)
    if value in (None, ""):
        raise InputError(f"{component}.{key} must be filled in canonical parameter data.")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise InputError(f"{component}.{key} must be a finite number.") from exc
    if not np.isfinite(parsed):
        raise InputError(f"{component}.{key} must be finite.")
    return parsed


def _required_nullable_text(payload: Mapping[str, Any], key: str, component: str) -> str | None:
    if key not in payload:
        raise InputError(f"{component}.{key} must be explicit in canonical parameter data.")
    value = payload[key]
    if value is None:
        return None
    if not isinstance(value, str):
        raise InputError(f"{component}.{key} must be a string or null.")
    text = value.strip()
    if not text:
        raise InputError(f"{component}.{key} must use null for a nonassociating component, not blank text.")
    return text


def _optional_float(payload: Mapping[str, Any], key: str, default: float) -> float:
    value = payload.get(key, default)
    if value in (None, ""):
        return float(default)
    return float(value)


def _resolve_parameter_source_species(
    base: Sequence[str] | None,
    override: Sequence[str] | None,
) -> tuple[str, ...] | None:
    if base is None and override is None:
        return None
    if base is None:
        return tuple(str(label) for label in override or ())
    labels = tuple(str(label) for label in base)
    if override is not None and tuple(str(label) for label in override) != labels:
        raise InputError("ParameterSource species override must match construction species.")
    return labels


def _require_parameter_source_species(
    requested: Sequence[str] | None,
    available: Sequence[str],
    label: str,
) -> None:
    if requested is None:
        return
    if tuple(str(item) for item in requested) != tuple(str(item) for item in available):
        raise InputError(f"{label} species order must match ParameterSource species.")


def _parameter_set_with_runtime_options(
    params: ParameterSet,
    user_options: Mapping[str, Any] | None,
) -> ParameterSet:
    if not user_options:
        return params
    return ParameterSet(
        components=params.components,
        pure_records=params.pure_records,
        binary_records=params.binary_records,
        metadata=params.metadata,
        runtime_options=_deep_update_mapping(params.runtime_options, user_options),
    )


def _normalize_runtime_user_options(runtime_options: Mapping[str, Any]) -> dict[str, Any]:
    if not runtime_options:
        return {}
    option_keys = {
        "elec_model",
        "solvated_ion_diameter_mixing_rule",
        "ion_dispersion_mixing_rule",
        "differential_mode",
        "relative_permittivity_rule",
        "born_model",
    }
    metadata_keys = {"elec_model_dataset"}
    if not (set(runtime_options) & option_keys):
        return _copy_payload_mapping(runtime_options)

    from .datasets import _resolve_runtime_options

    metadata = {
        str(key): _copy_payload_value(value)
        for key, value in runtime_options.items()
        if str(key) in metadata_keys or str(key) in _NATIVE_RUNTIME_PASSTHROUGH_KEYS
    }
    option_payload = {
        str(key): value
        for key, value in runtime_options.items()
        if str(key) not in metadata_keys and str(key) not in _NATIVE_RUNTIME_PASSTHROUGH_KEYS
    }
    resolved = _resolve_runtime_options(option_payload)
    normalized = {
        "elec_model": resolved["model"],
        "solvated_ion_diameter_mixing_rule": bool(resolved["runtime"]["solvated_ion_diameter_mixing_rule"]),
        "ion_dispersion_mixing_rule": bool(resolved["runtime"]["ion_dispersion_mixing_rule"]),
    }
    normalized.update(metadata)
    return normalized


def _runtime_parameter_provenance_payload(metadata: Mapping[str, Any], has_binary_records: bool) -> dict[str, Any]:
    fields = _provenance_metadata_fields(metadata)
    source_label = next((str(metadata[key]) for key in fields if key in {"source", "dataset", "paper"}), "ParameterSet")
    source_backed = bool(metadata.get("source_backed", False))
    if fields and source_backed:
        status = "source_backed_parameter_metadata"
    elif fields:
        status = "declared_parameter_metadata"
    else:
        status = "parameter_metadata_missing_source"
    return {
        "_parameter_source_label": source_label,
        "_parameter_provenance_status": status,
        "_parameter_provenance_fields": fields,
        "_binary_interaction_provenance_status": (
            "explicit_binary_records" if has_binary_records else "missing_binary_records"
        ),
    }


def _provenance_metadata_fields(metadata: Mapping[str, Any]) -> list[str]:
    return [
        key
        for key in _PROVENANCE_METADATA_KEYS
        if isinstance(metadata.get(key), str) and bool(str(metadata[key]).strip())
    ]


def _json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _json_ready(value.tolist())
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return value


def _pure_record_json(record: PureRecord) -> dict[str, Any]:
    payload = asdict(record)
    payload["molar_mass_units"] = "kg/mol"
    return payload


def _canonical_array(payload: Mapping[str, Any], key: str) -> list[Any]:
    if key not in payload:
        raise InputError(f"canonical parameter payload requires {key} as a JSON array.")
    value = payload[key]
    if not isinstance(value, list):
        raise InputError(f"canonical parameter payload {key} must be a JSON array.")
    return value


def _nonblank_identity(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise InputError(f"{field_name} must be a nonblank string.")
    text = value.strip()
    if not text:
        raise InputError(f"{field_name} must be a nonblank string.")
    if text != value:
        raise InputError(f"{field_name} must not contain surrounding whitespace.")
    return text
