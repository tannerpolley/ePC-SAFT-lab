from __future__ import annotations

from typing import Any

class ActivityCoefficientNative: ...


class CompositionContributionResult: ...


class CompressibilityFactorResult: ...


class FugacityContributionResult: ...


class NativeArgs: ...


class NativeMixture: ...


class ResolvedNativeInput:
    contract_id: str
    schema: str
    schema_version: int
    definition_fingerprint_sha256: str
    component_order: list[str]


class ProviderResolvedInputHandleV1:
    contract_id: str
    schema: str
    schema_version: int
    definition_fingerprint_sha256: str
    snapshot_fingerprint_sha256: str
    component_order: list[str]
    temperature_K: float
    composition_basis: str
    canonical_composition: list[float]
    evaluated_records: list[dict[str, Any]]
    structural_zeros: list[dict[str, Any]]
    affected_record_ids: dict[str, list[str]]
    trial_phase_composition_invariant: bool
    active_residual_families: list[str]
    ionic_component_indices: list[int]
    association_topology_fingerprint_sha256: str
    scientific_source_classifications: list[str]
    native_mapping: dict[str, dict[str, str]]


class NativeSolutionError(RuntimeError): ...


class NativeState: ...


class NativeValueError(ValueError): ...


class ResidualChemicalPotentialResult: ...


class ScalarContributionTerms: ...


class VectorContributionTerms: ...


def _native_association_site_fraction_solve(*args: Any, **kwargs: Any) -> Any: ...
def _native_cppad_eos_contributions(*args: Any, **kwargs: Any) -> Any: ...
def _native_cppad_neutral_binary_kij_properties(*args: Any, **kwargs: Any) -> Any: ...
def _native_cppad_neutral_binary_pair_properties(*args: Any, **kwargs: Any) -> Any: ...
def _native_cppad_association_component_parameters(*args: Any, **kwargs: Any) -> Any: ...
def _native_cppad_pressure_density(*args: Any, **kwargs: Any) -> Any: ...
def _native_cppad_pure_neutral_parameters(*args: Any, **kwargs: Any) -> Any: ...
def _native_cppad_smoke(*args: Any, **kwargs: Any) -> dict[str, Any]: ...
def _native_phase_state_ln_fugacity_composition_sensitivity(*args: Any, **kwargs: Any) -> Any: ...
def _native_provider_sdk_contract(*args: Any, **kwargs: Any) -> dict[str, Any]: ...
def _native_resolved_input_field_accounting() -> dict[str, str]: ...
def _native_provider_parameter_access_parity(
    legacy: NativeArgs,
    handle: ProviderResolvedInputHandleV1,
) -> dict[str, Any]: ...
def _native_provider_parameter_kernel_parity(
    legacy: NativeArgs,
    handle: ProviderResolvedInputHandleV1,
    density: float,
) -> dict[str, Any]: ...
def __getattr__(name: str) -> Any: ...
