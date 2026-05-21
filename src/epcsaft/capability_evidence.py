"""Registered capability evidence and cheap validation lanes.

This module is intentionally side-effect free so command-line wrappers can
import the registry without importing the native extension.
"""

from __future__ import annotations

from typing import Final

REACTIVE_SPECIATION_STANDARD_STATES: Final[tuple[str, ...]] = (
    "ideal_mole_fraction",
    "mole_fraction_activity",
    "concentration",
)

IPOPT_EQUILIBRIUM_ROUTE_EVIDENCE: Final[tuple[dict[str, object], ...]] = (
    {
        "key": "reactive_speciation",
        "public_routes": tuple(
            f"reactive_speciation:{state}" for state in REACTIVE_SPECIATION_STANDARD_STATES
        ),
        "payload": {
            "backend": "native_ipopt_equilibrium_nlp",
            "sweep_available_from_ipopt": True,
            "activity_output_modes": ("auto", "always", "never"),
            "jacobian_auto_policy": "cppad_only_else_raise",
            "jacobian_auto_supported_standard_states": REACTIVE_SPECIATION_STANDARD_STATES,
            "implemented_standard_states": REACTIVE_SPECIATION_STANDARD_STATES,
            "auto_request": "implemented_standard_states_route_to_native_ipopt",
            "solver_backends": ("ipopt",),
            "explicit_ipopt_request": "implemented_standard_states_route_to_native_ipopt_when_compiled",
            "ipopt_formulation": "thermodynamic_constrained_nlp",
            "ideal_speciation_nlp_available_from_ipopt": True,
            "nonideal_speciation_nlp_available_from_ipopt": True,
            "nonideal_derivative_backend": "cppad_explicit_density",
            "mixed_standard_state_policy": "raise_until_single_objective_is_specified",
        },
    },
    {
        "key": "neutral_tp_flash",
        "public_routes": (),
        "payload": {
            "backend": "native_ipopt_equilibrium_nlp",
            "internal_methods": ("tp_flash", "flash_tp"),
            "ipopt_formulation": "thermodynamic_constrained_nlp",
        },
    },
    {
        "key": "neutral_stability",
        "public_routes": (),
        "payload": {
            "backend": "native_ipopt_equilibrium_nlp",
            "internal_methods": ("stability_tp",),
            "ipopt_formulation": "thermodynamic_constrained_nlp",
            "route": "tangent_plane_distance",
        },
    },
    {
        "key": "electrolyte_stability",
        "public_routes": (),
        "payload": {
            "backend": "native_ipopt_equilibrium_nlp",
            "internal_methods": ("electrolyte_stability_tp",),
            "ipopt_formulation": "thermodynamic_constrained_nlp",
            "route": "charge_constrained_tangent_plane_distance",
        },
    },
    {
        "key": "reactive_stability",
        "public_routes": (),
        "payload": {
            "backend": "native_ipopt_equilibrium_nlp",
            "internal_methods": ("reactive_stability_tp",),
            "ipopt_formulation": "thermodynamic_constrained_nlp",
            "route": "coupled_reactive_tangent_plane_distance",
        },
    },
    {
        "key": "neutral_lle_flash",
        "public_routes": (),
        "payload": {
            "backend": "native_ipopt_equilibrium_nlp",
            "internal_methods": ("lle_flash", "lle_tp"),
            "ipopt_formulation": "thermodynamic_constrained_nlp",
        },
    },
    {
        "key": "neutral_bubble_dew",
        "public_routes": ("Equilibrium.bubble_pressure",),
        "payload": {
            "backend": "native_ipopt_equilibrium_nlp",
            "methods": ("bubble_pressure",),
            "internal_methods": ("bubble_p", "bubble_t", "dew_p", "dew_t"),
        },
    },
    {
        "key": "electrolyte_lle",
        "public_routes": (),
        "payload": {
            "backend": "native_ipopt_equilibrium_nlp",
            "internal_methods": ("electrolyte_lle", "electrolyte_lle_tp"),
            "solver_backends": ("ipopt",),
            "explicit_ipopt_request": "routes_to_native_ipopt_when_compiled",
            "ipopt_formulation": "thermodynamic_constrained_nlp",
        },
    },
    {
        "key": "electrolyte_bubble_pressure",
        "public_routes": (),
        "payload": {
            "backend": "native_ipopt_equilibrium_nlp",
            "scope": "fixed liquid composition with neutral vapor species; ions remain liquid-only",
        },
    },
)

EQUILIBRIUM_PROBLEM_OBJECT_CLASSES: Final[tuple[str, ...]] = (
)

DERIVATIVE_COVERAGE_ROWS: Final[tuple[dict[str, object], ...]] = (
    {
        "row_family": "regression",
        "subsystem": "regression",
        "quantity": "pure_neutral_parameters",
        "derivative": "objective_jacobian",
        "backend": "cppad_implicit",
        "supported": True,
        "classification": "production_supported",
        "reason": "validated CppAD plus implicit density-sensitivity regression slice",
        "tests": ("tests/native/regression/test_pure.py",),
    },
    {
        "row_family": "regression",
        "subsystem": "regression",
        "quantity": "binary_kij",
        "derivative": "objective_jacobian",
        "backend": "cppad_implicit",
        "supported": True,
        "classification": "production_supported",
        "reason": "validated Ceres route with CppAD and implicit density/association sensitivities",
        "tests": (
            "tests/native/regression/test_binary.py",
        ),
    },
    {
        "row_family": "electrolyte_property",
        "subsystem": "electrolyte",
        "quantity": "ssmds_born_liquid",
        "derivative": "parameter_sensitivity",
        "backend": "cppad",
        "supported": True,
        "classification": "production_supported",
        "reason": "public derivative reporting is CppAD-only; native analytic kernels may remain internal transition details",
        "tests": ("tests/native/state/test_born_ssmds_liquid_derivatives.py",),
    },
)

EQUILIBRIUM_ROUTE_DERIVATIVE_EVIDENCE: Final[tuple[dict[str, object], ...]] = (
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "neutral_two_phase_routes",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_phase_blocks",
        "supported": True,
        "classification": "production_supported",
        "reason": "neutral TP flash, LLE, stability, bubble, and dew routes require exact gradients/Jacobians and default to exact Hessians",
        "tests": (
            "tests/api/frontend/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route",
            "tests/native/equilibrium/routes/neutral/test_flash.py",
            "tests/native/equilibrium/routes/neutral/test_lle.py",
            "tests/native/equilibrium/routes/neutral/test_bubble_dew.py",
            "tests/native/equilibrium/routes/stability/test_route_builders.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "electrolyte_lle_and_stability",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_explicit_density",
        "supported": True,
        "classification": "production_supported",
        "reason": "electrolyte LLE and charge-constrained stability routes report exact Hessian metadata and reject non-certified postsolves",
        "tests": (
            "tests/native/equilibrium/routes/electrolyte/test_lle_residual_surface.py",
            "tests/native/equilibrium/routes/electrolyte/test_lle_residual_jacobian.py",
            "tests/native/equilibrium/routes/electrolyte/test_route_builders.py",
            "tests/native/equilibrium/routes/stability/test_route_builders.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "electrolyte_bubble_pressure",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_explicit_density",
        "supported": True,
        "classification": "production_supported",
        "reason": "electrolyte bubble pressure is a registered production Ipopt route with exact-Hessian route-builder evidence and public phase-eligibility diagnostics",
        "tests": (
            "tests/native/equilibrium/routes/electrolyte/test_route_builders.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "reactive_stability",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_explicit_density",
        "supported": True,
        "classification": "production_supported",
        "reason": "reactive stability routes through the native coupled reactive TPD Ipopt route with exact Hessian evidence and shared certification diagnostics",
        "tests": (
            "tests/native/equilibrium/routes/reactive/test_chemical_equilibrium_native_api.py",
            "tests/native/equilibrium/routes/stability/test_route_builders.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "reactive_lle_and_reactive_electrolyte_lle",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_explicit_density",
        "supported": True,
        "classification": "route_builder_supported_capability_pending",
        "reason": "native reactive LLE route builders expose exact Hessian paths, while production capability registration still waits for benchmark and acceptance evidence",
        "tests": (
            "tests/native/equilibrium/routes/reactive/test_phase_equilibrium_residual_jacobian.py",
            "tests/native/equilibrium/routes/reactive/test_lle.py",
            "tests/native/equilibrium/routes/reactive_electrolyte/test_route_builders.py",
        ),
    },
)

REGRESSION_CAPABILITY_KEYS: Final[tuple[str, ...]] = (
    "pure_neutral",
)

NATIVE_CONTRACT_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/native/equilibrium/diagnostics/test_route_metadata_contracts.py",
    "tests/native/equilibrium/diagnostics/test_native_route_diagnostics_contract.py",
)

GENERIC_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/api/package/test_package_main.py::test_python_m_epcsaft_reports_package_and_core_status",
    "tests/api/frontend",
    "tests/native/state/test_pressure_density.py",
    "tests/native/state/test_phase_state_sensitivities.py",
    "tests/native/contracts/test_equation_registry.py::test_equation_registry_outputs_are_synced",
    *NATIVE_CONTRACT_TEST_TARGETS,
    "tests/workflows/repo/test_project_structure.py",
    "tests/workflows/repo/test_run_pytest.py::test_list_slices_exits_without_running_pytest",
    "tests/workflows/repo/test_workflow_entrypoints.py::test_docs_make_confidence_suite_the_default_runtime_check",
)
CONFIDENCE_TEST_TARGETS: Final[tuple[str, ...]] = (
    *GENERIC_TEST_TARGETS,
    "tests/native/state/test_contributions.py::test_native_residual_helmholtz_and_compressibility_contributions_match_neutral_contract",
)
EQUILIBRIUM_CONFIDENCE_TEST_TARGETS: Final[tuple[str, ...]] = (
    (
        "tests/native/equilibrium/routes/neutral/test_bubble_dew.py::"
        "test_neutral_bubble_pressure_workbook_accepted_point_runs_postsolve"
    ),
    (
        "tests/native/equilibrium/routes/neutral/test_bubble_dew.py::"
        "test_neutral_fixed_temperature_pressure_route_uses_exact_hessian_when_requested"
    ),
    "tests/native/equilibrium/diagnostics/test_native_route_diagnostics_contract.py",
)
EQUILIBRIUM_API_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/api/frontend/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route",
)
RUNTIME_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/api/frontend/test_state_properties.py::test_cppad_state_proves_hydrocarbon_values_and_derivatives",
    "tests/native/state/test_pressure_density.py",
    "tests/native/state/test_phase_state_sensitivities.py",
)
API_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/api/frontend",
)
NATIVE_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/native/state/test_pressure_density.py",
    "tests/native/state/test_phase_state_sensitivities.py",
    "tests/native/state/test_contributions.py",
    "tests/native/state/test_runtime_cache.py",
)
TEST_SLICES: Final[dict[str, dict[str, object]]] = {
    "generic": {"targets": GENERIC_TEST_TARGETS, "cheap_by_default": True},
    "all": {"targets": ("tests",), "cheap_by_default": False},
    "confidence": {"targets": CONFIDENCE_TEST_TARGETS, "cheap_by_default": False},
    "equilibrium-confidence": {"targets": EQUILIBRIUM_CONFIDENCE_TEST_TARGETS, "cheap_by_default": False},
    "equilibrium-api": {"targets": EQUILIBRIUM_API_TEST_TARGETS, "cheap_by_default": True},
    "runtime": {"targets": RUNTIME_TEST_TARGETS, "cheap_by_default": True},
    "api": {"targets": API_TEST_TARGETS, "cheap_by_default": True},
    "native": {"targets": NATIVE_TEST_TARGETS, "cheap_by_default": True},
    "native-contracts": {"targets": NATIVE_CONTRACT_TEST_TARGETS, "cheap_by_default": True},
}

VALIDATION_LANES: Final[dict[str, dict[str, object]]] = {
    "quick": {
        "commands": (("scripts/dev/doctor.py",), ("run_pytest.py", "-q")),
        "cheap_by_default": True,
        "evidence": "doctor plus generic pytest slice",
    },
    "confidence": {
        "commands": (("scripts/dev/doctor.py",), ("run_pytest.py", "--confidence", "-q")),
        "cheap_by_default": False,
        "evidence": "doctor plus native runtime confidence pytest slice",
    },
    "docs": {
        "commands": (("-m", "sphinx", "-b", "html", "docs", "build/docs-html"),),
        "cheap_by_default": False,
        "evidence": "Sphinx documentation build",
    },
    "full": {
        "commands": (("scripts/dev/doctor.py",), ("run_pytest.py", "--all", "-q")),
        "cheap_by_default": False,
        "evidence": "doctor plus every retained pytest contract",
    },
    "ceres-cppad": {
        "commands": (
            ("scripts/dev/build_epcsaft.py", "--profile", "full"),
            (
                "run_pytest.py",
                "tests/native/regression/test_pure.py",
                "tests/native/regression/test_binary.py",
                "-q",
            ),
        ),
        "cheap_by_default": False,
        "evidence": "Ceres and CppAD build profile plus focused native regression tests",
    },
}


def registry_targets(name: str) -> tuple[str, ...]:
    """Return the registered pytest targets for a named slice."""

    return tuple(str(target) for target in TEST_SLICES[name]["targets"])


def validation_lane_commands(name: str) -> tuple[tuple[str, ...], ...]:
    """Return executable commands for a named validation lane."""

    return tuple(tuple(str(part) for part in command) for command in VALIDATION_LANES[name]["commands"])


def registered_ipopt_public_routes() -> list[str]:
    """Return public Ipopt route labels registered by executable route evidence."""

    return [
        str(route)
        for evidence in IPOPT_EQUILIBRIUM_ROUTE_EVIDENCE
        for route in evidence["public_routes"]  # type: ignore[index]
    ]
