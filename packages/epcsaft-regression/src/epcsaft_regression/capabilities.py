"""Capability reporting for the future ePC-SAFT regression extension."""

from __future__ import annotations

from typing import Any

import epcsaft

from .native_adapter import native_ceres_backend_info

REGRESSION_CAPABILITY_KEYS = (
    "pure_neutral",
    "binary_pair_constant_kij",
    "liquid_electrolyte_born",
)

REGRESSION_CAPABILITY_DIMENSIONS = (
    "registry_known_target_kind",
    "derivative_supported_target_kind",
    "optimizer_supported_target_kind",
    "public_production_supported_target_kind",
)

REGRESSION_CAPABILITY_REVISIT_AFTER = ("#136", "#137")

REGRESSION_TARGET_KIND_ROWS = (
    {
        "target_kind": "m",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": True,
        "public_production_supported_target_kind": False,
        "production_scope": "nonassociating pure-neutral Ceres regression",
        "route_key": "pure_neutral",
        "derivative_backend": "cppad_implicit",
        "optimizer_backend": "native_ceres",
        "tests": (
            "packages/epcsaft-regression/tests/native/test_pure.py::test_ceres_pure_neutral_regression_owns_optimizer_loop",
            "packages/epcsaft-regression/tests/api/test_regression.py::test_regression_hydrocarbon_anchor_routes_through_new_object_api",
        ),
    },
    {
        "target_kind": "s",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": True,
        "public_production_supported_target_kind": False,
        "production_scope": "tested pure-neutral and pure-ion Ceres regression routes",
        "route_key": "pure_neutral; pure_ion",
        "derivative_backend": "cppad_implicit",
        "optimizer_backend": "native_ceres",
        "tests": (
            "packages/epcsaft-regression/tests/native/test_pure.py::test_ceres_pure_neutral_regression_owns_optimizer_loop",
            "packages/epcsaft-regression/tests/native/test_pure.py::test_ceres_pure_ion_regression_uses_cppad_implicit_for_density_osmotic_miac",
        ),
    },
    {
        "target_kind": "e",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": True,
        "public_production_supported_target_kind": False,
        "production_scope": "tested pure-neutral and pure-ion Ceres regression routes",
        "route_key": "pure_neutral; pure_ion",
        "derivative_backend": "cppad_implicit",
        "optimizer_backend": "native_ceres",
        "tests": (
            "packages/epcsaft-regression/tests/native/test_pure.py::test_ceres_pure_neutral_regression_owns_optimizer_loop",
            "packages/epcsaft-regression/tests/native/test_pure.py::test_ceres_pure_ion_regression_uses_cppad_implicit_for_density_osmotic_miac",
        ),
    },
    {
        "target_kind": "e_assoc",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": False,
        "public_production_supported_target_kind": False,
        "production_scope": "pure associating component property derivatives only; optimizer support remains unclaimed",
        "route_key": "pure_association_parameter_property_derivatives",
        "derivative_backend": "cppad_implicit",
        "optimizer_backend": "not_claimed",
        "tests": (
            "packages/epcsaft/tests/native/state/test_fugacity_derivatives.py::test_associating_pure_parameter_derivative_results_support_e_assoc_and_vol_a",
        ),
        "revisit_after_issue": "#136",
    },
    {
        "target_kind": "vol_a",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": False,
        "public_production_supported_target_kind": False,
        "production_scope": "pure associating component property derivatives only; optimizer support remains unclaimed",
        "route_key": "pure_association_parameter_property_derivatives",
        "derivative_backend": "cppad_implicit",
        "optimizer_backend": "not_claimed",
        "tests": (
            "packages/epcsaft/tests/native/state/test_fugacity_derivatives.py::test_associating_pure_parameter_derivative_results_support_e_assoc_and_vol_a",
        ),
        "revisit_after_issue": "#136",
    },
    {
        "target_kind": "d_born",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": True,
        "public_production_supported_target_kind": False,
        "production_scope": "tested liquid-electrolyte Born/SSM/DS Ceres regression route",
        "route_key": "liquid_electrolyte_born",
        "derivative_backend": "cppad_implicit",
        "optimizer_backend": "native_ceres",
        "tests": (
            "packages/epcsaft-regression/tests/native/test_pure.py::test_ceres_pure_ion_regression_uses_cppad_implicit_for_density_osmotic_miac",
            "packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py::test_ceres_liquid_electrolyte_regression_uses_native_ssmds_derivatives",
        ),
    },
    {
        "target_kind": "k_ij",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": True,
        "public_production_supported_target_kind": False,
        "production_scope": "tested constant binary k_ij Ceres regression route",
        "route_key": "binary_pair_constant_kij",
        "derivative_backend": "cppad_implicit",
        "optimizer_backend": "native_ceres",
        "tests": (
            "packages/epcsaft-regression/tests/native/test_binary.py::test_ceres_binary_kij_regression_uses_native_cppad_implicit_jacobian",
            "packages/epcsaft-regression/tests/native/test_binary.py::test_ceres_binary_kij_regression_accepts_associating_neutral_rows",
        ),
    },
    {
        "target_kind": "l_ij",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": False,
        "public_production_supported_target_kind": False,
        "production_scope": "binary pair property derivatives, including active-association implicit sensitivity; optimizer support remains unclaimed",
        "route_key": "binary_association_parameter_property_derivatives",
        "derivative_backend": "cppad_implicit",
        "optimizer_backend": "not_claimed",
        "tests": (
            "packages/epcsaft/tests/native/state/test_fugacity_derivatives.py::test_associating_binary_parameter_derivative_results_support_lij_and_khb",
        ),
        "revisit_after_issue": "#137",
    },
    {
        "target_kind": "k_hb_ij",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": False,
        "public_production_supported_target_kind": False,
        "production_scope": "active-association binary pair property derivatives only; optimizer support remains unclaimed",
        "route_key": "binary_association_parameter_property_derivatives",
        "derivative_backend": "cppad_implicit",
        "optimizer_backend": "not_claimed",
        "tests": (
            "packages/epcsaft/tests/native/state/test_fugacity_derivatives.py::test_associating_binary_parameter_derivative_results_support_lij_and_khb",
        ),
        "revisit_after_issue": "#137",
    },
    {
        "target_kind": "f_solv",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": True,
        "public_production_supported_target_kind": False,
        "production_scope": "tested liquid-electrolyte Born/SSM/DS Ceres regression route",
        "route_key": "liquid_electrolyte_born",
        "derivative_backend": "cppad_implicit",
        "optimizer_backend": "native_ceres",
        "tests": (
            "packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py::test_ceres_liquid_electrolyte_regression_uses_native_ssmds_derivatives",
        ),
    },
    {
        "target_kind": "dielc",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": False,
        "optimizer_supported_target_kind": False,
        "public_production_supported_target_kind": False,
        "production_scope": "registry only until relative-permittivity parameter optimizer evidence exists",
        "route_key": "liquid_electrolyte_relative_permittivity_pending",
        "derivative_backend": "not_claimed",
        "optimizer_backend": "not_claimed",
        "tests": (),
        "revisit_after_issue": "#135-follow-up",
    },
)


def provider_contract() -> dict[str, object]:
    return {
        "provider_package": "epcsaft",
        "provider_api_contract_id": "provider_api_v1",
        "provider_native_sdk_contract_id": "provider_native_sdk_v1",
    }


def _provider_cppad_capability() -> dict[str, object]:
    return dict(epcsaft.capabilities()["derivatives"]["cppad"])


def _ceres_capability() -> dict[str, object]:
    ceres = native_ceres_backend_info()
    ceres_available = bool(ceres.get("available", False))
    out: dict[str, object] = {
        **ceres,
        "production": False,
        "scope": "native optimizer backend owned by the regression extension",
        "native_hot_loop": ceres_available,
        "production_routes": [],
    }
    if ceres_available:
        out["reason"] = "resolved_input_overlay_pending"
    else:
        out["reason"] = "extension_dependency_missing"
    return out


def _capability_value(value: object) -> object:
    if isinstance(value, tuple):
        return [_capability_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _capability_value(item) for key, item in value.items()}
    return value


def _regression_target_kind_evidence() -> dict[str, object]:
    rows = [_capability_value(row) for row in REGRESSION_TARGET_KIND_ROWS]
    production_targets = [
        str(row["target_kind"]) for row in rows if bool(row["public_production_supported_target_kind"])
    ]
    registry_only_targets = [
        str(row["target_kind"])
        for row in rows
        if bool(row["registry_known_target_kind"]) and not bool(row["public_production_supported_target_kind"])
    ]
    return {
        "source": "registered_regression_extension_evidence",
        "dimensions": list(REGRESSION_CAPABILITY_DIMENSIONS),
        "revisit_after": list(REGRESSION_CAPABILITY_REVISIT_AFTER),
        "production_supported_target_kinds": production_targets,
        "registry_only_or_pending_target_kinds": registry_only_targets,
        "rows": rows,
    }


def capabilities() -> dict[str, object]:
    cppad = _provider_cppad_capability()
    ceres = _ceres_capability()
    regression_target_evidence = _regression_target_kind_evidence()
    native_regression_evidence_available = bool(
        bool(ceres.get("available", False)) and bool(cppad.get("available", False))
    )
    return {
        "package": "epcsaft-regression",
        "owner": "regression_extension",
        "status": "configured_workflow_overlay_pending",
        "provider_contract": provider_contract(),
        "native_dependencies": {
            "cppad": cppad,
            "ceres": ceres,
        },
        "requires": ["epcsaft", "cppad", "ceres"],
        "forbidden_default_dependencies": ["ipopt"],
        "optimizers": {
            "ceres": ceres,
        },
        "derivatives": {
            "cppad": cppad,
            "regression_ceres_jacobians": {
                "available": native_regression_evidence_available,
                "production": False,
                "routes": list(REGRESSION_CAPABILITY_KEYS),
                "backends": ["cppad_implicit"],
                "requires": ["ceres", "cppad"],
            },
        },
        "regression": {
            "target_kind_evidence": regression_target_evidence,
            "production_supported_target_kinds": list(regression_target_evidence["production_supported_target_kinds"]),
            "pure_neutral": {
                "available": False,
                "production": False,
                "backend": "native_ceres",
                "entrypoint": "Regression(mixture, controls=...).fit(dataset, parameters=...)",
                "jacobian_backend": "cppad_implicit",
                "target_kinds": ["m", "s", "e"],
                "reason": "resolved_input_overlay_pending",
            },
            "binary_pair_constant_kij": {
                "available": False,
                "production": False,
                "backend": "native_ceres",
                "entrypoint": "Regression(mixture, controls=...).fit(dataset, parameters=...)",
                "jacobian_backend": "cppad_implicit",
                "target_kinds": ["k_ij"],
                "reason": "resolved_input_overlay_pending",
            },
            "liquid_electrolyte_born": {
                "available": False,
                "production": False,
                "backend": "native_ceres",
                "entrypoint": "Regression(mixture, controls=...).fit(dataset, parameters=...)",
                "jacobian_backend": "cppad_implicit",
                "target_kinds": ["d_born", "f_solv"],
                "reason": "resolved_input_overlay_pending",
            },
        },
    }


__all__ = ["capabilities", "provider_contract"]
