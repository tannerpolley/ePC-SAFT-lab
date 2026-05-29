"""Capability reporting for the equilibrium extension package."""

from __future__ import annotations

from ._native import native_ipopt_backend_info, provider_contract
from .equilibrium_activation import EQUILIBRIUM_ACTIVATION_MATRIX


EQUILIBRIUM_PROBLEM_OBJECT_CLASSES = (
    "EquilibriumProblem",
    "EquilibriumStructure",
)

EQUILIBRIUM_ROUTE_DERIVATIVE_EVIDENCE = (
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "bubble_dew_derived_routes",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_phase_blocks",
        "supported": True,
        "classification": "production_supported",
        "reason": "production selector exposes neutral bubble/dew pressure and temperature routes through exact Ipopt callbacks",
        "tests": (
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "neutral_tp_flash",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_phase_blocks",
        "supported": True,
        "classification": "production_supported",
        "reason": "production selector exposes neutral two-phase TP flash through activation-plan assembly and postsolve certification",
        "tests": (
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "neutral_lle",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_phase_blocks",
        "supported": True,
        "classification": "production_supported",
        "reason": "production selector exposes neutral nonassociating LLE through the generic two-phase EOS NLP with exact Ipopt callbacks",
        "tests": (
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
            "packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py",
        ),
    },
)


def _capability_value(value: object) -> object:
    if isinstance(value, tuple):
        return [_capability_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _capability_value(item) for key, item in value.items()}
    return value


def public_routes_by_family() -> dict[str, tuple[str, ...]]:
    routes_by_family: dict[str, tuple[str, ...]] = {}
    for row in EQUILIBRIUM_ACTIVATION_MATRIX:
        family_key = str(row["key"])
        routes = tuple(str(route) for route in row.get("public_routes", ()))
        if not bool(row["production_exposed"]):
            if routes:
                raise RuntimeError(f"Declared-not-exposed equilibrium family '{family_key}' publishes routes.")
            continue
        if not routes:
            raise RuntimeError(f"Production equilibrium family '{family_key}' publishes no public routes.")
        routes_by_family[family_key] = routes
    return routes_by_family


def public_route_family_map() -> dict[str, str]:
    route_to_family: dict[str, str] = {}
    for family_key, routes in public_routes_by_family().items():
        for route in routes:
            if route in route_to_family:
                raise RuntimeError(
                    f"Public equilibrium route '{route}' is admitted by both "
                    f"'{route_to_family[route]}' and '{family_key}'."
                )
            route_to_family[route] = family_key
    return route_to_family


def registered_public_routes() -> list[str]:
    return sorted(public_route_family_map())


def _activation_capabilities(*, ipopt_route_available: bool) -> dict[str, object]:
    rows = [_capability_value(row) for row in EQUILIBRIUM_ACTIVATION_MATRIX]
    production_families = [str(row["key"]) for row in rows if bool(row["production_exposed"])]
    declared_not_exposed = [str(row["key"]) for row in rows if str(row["exposure_status"]) == "declared_not_exposed"]
    routes_by_family = {family: list(routes) for family, routes in public_routes_by_family().items()}
    return {
        "source": "native_cpp",
        "rows": rows,
        "production_families": production_families,
        "declared_not_exposed_families": declared_not_exposed,
        "public_routes": registered_public_routes(),
        "public_routes_by_family": routes_by_family,
        "public_route_family_map": dict(sorted(public_route_family_map().items())),
        "ipopt_available": ipopt_route_available,
    }


def capabilities() -> dict[str, object]:
    from epcsaft import runtime_build_info

    native_dependencies = runtime_build_info()["native_dependencies"]  # type: ignore[index]
    cppad = dict(native_dependencies["cppad"])  # type: ignore[index]
    ipopt = native_ipopt_backend_info()
    ipopt_route_available = bool(ipopt.get("available", False))
    activation = _activation_capabilities(ipopt_route_available=ipopt_route_available)
    public_routes_by_family = dict(activation["public_routes_by_family"])
    return {
        "package": "epcsaft-equilibrium",
        "owner": "equilibrium_extension",
        "provider_contract": provider_contract(),
        "requires": ["epcsaft", "cppad", "ipopt"],
        "forbidden_default_dependencies": ["ceres"],
        "native_dependencies": {
            "cppad": cppad,
            "ipopt": ipopt,
        },
        "optimizer": {
            "ipopt": {
                **ipopt,
                "solver_backend": "ipopt",
                "production": ipopt_route_available,
                "scope": "native Ipopt dependency for production equilibrium NLP routes",
                "formulations": ["thermodynamic_constrained_nlp"],
                "adapter_available": bool(ipopt.get("adapter_available", False)),
                "adapter_source_available": bool(ipopt.get("adapter_source_available", False)),
                "adapter_kind": ipopt.get("adapter_kind", "native_tnlp_adapter"),
                "public_routes": list(activation["public_routes"]),
            },
        },
        "activation_matrix": activation,
        "production_families": list(activation["production_families"]),
        "declared_not_exposed_families": list(activation["declared_not_exposed_families"]),
        "public_routes": list(activation["public_routes"]),
        "derivative_policy": {
            "accepted_derivative_backends": [
                "cppad",
                "cppad_implicit",
                "cppad_explicit_density",
            ],
            "auto_policy": "public_frontend_forces_cppad_else_raise",
        },
        "route_derivative_evidence": {
            "source": "epcsaft_equilibrium",
            "implemented_capability_claims_only": False,
            "production_rows_are_capability_safe": True,
            "rows": [_capability_value(row) for row in EQUILIBRIUM_ROUTE_DERIVATIVE_EVIDENCE],
        },
        "bubble_dew_derived_routes": {
            "available": bool(activation["ipopt_available"]),
            "production": True,
            "entrypoint": "Equilibrium(mixture, route=..., ...).solve()",
            "public_routes": public_routes_by_family["bubble_dew_derived_routes"],
            "selector_core": True,
            "input_scope": "neutral non-reactive non-electrolyte non-associating mixtures",
            "requires": ["cppad", "ipopt"],
        },
        "neutral_tp_flash": {
            "available": bool(activation["ipopt_available"]),
            "production": True,
            "entrypoint": "Equilibrium(mixture, route='flash', T=..., P=..., z=...).solve()",
            "public_routes": public_routes_by_family["neutral_tp_flash"],
            "selector_core": True,
            "input_scope": "neutral non-reactive non-electrolyte non-associating two-phase mixtures",
            "requires": ["cppad", "ipopt"],
        },
        "neutral_lle": {
            "available": bool(activation["ipopt_available"]),
            "production": True,
            "entrypoint": "Equilibrium(mixture, route='lle', T=..., P=..., z=...).solve()",
            "public_routes": public_routes_by_family["neutral_lle"],
            "selector_core": True,
            "input_scope": "neutral non-reactive non-electrolyte non-associating liquid/liquid mixtures",
            "requires": ["cppad", "ipopt"],
        },
        "problem_objects": {
            "available": True,
            "backend": "constructor_configured_frontend",
            "classes": list(EQUILIBRIUM_PROBLEM_OBJECT_CLASSES),
            "entrypoint": "Equilibrium(mixture, route=..., ...)",
        },
    }
