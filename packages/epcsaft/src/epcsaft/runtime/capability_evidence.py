"""Registered capability evidence and cheap validation lanes.

This module is intentionally side-effect free so command-line wrappers can
import the registry without importing the native extension.
"""

from __future__ import annotations

from typing import Final

_EQUILIBRIUM_PRODUCTION_ROUTES_BY_FAMILY: Final[dict[str, tuple[str, ...]]] = {
    "neutral_tp_flash": ("flash",),
    "neutral_lle": ("lle",),
    "bubble_dew_derived_routes": (
        "bubble_pressure",
        "bubble_temperature",
        "dew_pressure",
        "dew_temperature",
    ),
}

EQUILIBRIUM_API_TEST_FILE: Final[str] = "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py"
EQUILIBRIUM_BUBBLE_DERIVATIVE_TEST_FILE: Final[str] = (
    "packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py"
)
EQUILIBRIUM_CAPABILITY_TEST_FILE: Final[str] = (
    "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py"
)


def production_equilibrium_activation_rows() -> tuple[dict[str, object], ...]:
    """Return production-exposed equilibrium activation rows from the generated mirror."""

    return tuple(
        {
            "key": family,
            "production_exposed": True,
            "public_routes": routes,
        }
        for family, routes in _EQUILIBRIUM_PRODUCTION_ROUTES_BY_FAMILY.items()
    )


def public_ipopt_routes_by_family() -> dict[str, tuple[str, ...]]:
    """Return selector-admitted public route labels keyed by production family."""

    return dict(_EQUILIBRIUM_PRODUCTION_ROUTES_BY_FAMILY)


def public_ipopt_route_family_map() -> dict[str, str]:
    """Return each selector-admitted public route label mapped to its activation family."""

    route_to_family: dict[str, str] = {}
    for family_key, routes in public_ipopt_routes_by_family().items():
        for route in routes:
            if route in route_to_family:
                raise RuntimeError(
                    f"Public equilibrium route '{route}' is admitted by both "
                    f"'{route_to_family[route]}' and '{family_key}'."
                )
            route_to_family[route] = family_key
    return route_to_family

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
        "tests": ("packages/epcsaft-regression/tests/native/test_pure.py",),
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
        "tests": ("packages/epcsaft-regression/tests/native/test_binary.py",),
    },
    {
        "row_family": "electrolyte_property",
        "subsystem": "electrolyte",
        "quantity": "born_parameter_liquid",
        "derivative": "parameter_sensitivity",
        "backend": "cppad",
        "supported": True,
        "classification": "production_supported",
        "reason": "public Born parameter derivative reporting is CppAD-backed for d_born and f_solv",
        "tests": ("packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py",),
    },
)

EQUILIBRIUM_VALIDATION_TARGETS_BY_FAMILY: Final[dict[str, str]] = {
    "bubble_dew_derived_routes": (
        f"{EQUILIBRIUM_API_TEST_FILE}::"
        "test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route"
    ),
    "neutral_tp_flash": (
        f"{EQUILIBRIUM_API_TEST_FILE}::"
        "test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point"
    ),
    "neutral_lle": (
        f"{EQUILIBRIUM_API_TEST_FILE}::"
        "test_equilibrium_lle_route_returns_named_liquid_phase_helpers"
    ),
}

REGRESSION_CAPABILITY_KEYS: Final[tuple[str, ...]] = (
    "pure_neutral",
    "binary_pair_constant_kij",
    "liquid_electrolyte_born",
)

REGRESSION_CAPABILITY_DIMENSIONS: Final[tuple[str, ...]] = (
    "registry_known_target_kind",
    "derivative_supported_target_kind",
    "optimizer_supported_target_kind",
    "public_production_supported_target_kind",
)

REGRESSION_CAPABILITY_REVISIT_AFTER: Final[tuple[str, ...]] = ("#136", "#137")

REGRESSION_TARGET_KIND_EVIDENCE: Final[tuple[dict[str, object], ...]] = (
    {
        "target_kind": "m",
        "registry_known_target_kind": True,
        "derivative_supported_target_kind": True,
        "optimizer_supported_target_kind": True,
        "public_production_supported_target_kind": True,
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
        "public_production_supported_target_kind": True,
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
        "public_production_supported_target_kind": True,
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
        "public_production_supported_target_kind": True,
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
        "public_production_supported_target_kind": True,
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
        "public_production_supported_target_kind": True,
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

NATIVE_CONTRACT_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/native/contracts/test_generalized_equilibrium_registry.py",
    "tests/native/contracts/test_equilibrium_benchmark_registry.py",
    "packages/epcsaft/tests/native/contracts/test_provider_only_core_symbols.py",
    "packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py",
    "packages/epcsaft-equilibrium/tests/native/diagnostics/test_native_route_diagnostics_contract.py",
)

PROVIDER_API_TEST_TARGETS: Final[tuple[str, ...]] = (
    "packages/epcsaft/tests/api/package/test_root_exports.py",
    "packages/epcsaft/tests/api/package/test_package_main.py",
    "packages/epcsaft/tests/api/frontend/test_imports.py",
    "packages/epcsaft/tests/api/frontend/test_mixture.py",
    "packages/epcsaft/tests/api/frontend/test_templates.py",
    "packages/epcsaft/tests/api/frontend/test_state_properties.py",
)

REGRESSION_API_TEST_TARGETS: Final[tuple[str, ...]] = (
    "packages/epcsaft-regression/tests/api/test_regression.py",
)

REGRESSION_TEST_TARGETS: Final[tuple[str, ...]] = (
    *REGRESSION_API_TEST_TARGETS,
    "packages/epcsaft-regression/tests/native/test_pure.py",
    "packages/epcsaft-regression/tests/native/test_binary.py",
    "packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py",
    "packages/epcsaft-regression/tests/contracts/test_ceres_cppad_build_contract.py",
)

EQUILIBRIUM_PACKAGE_CONTRACT_TARGETS: Final[tuple[str, ...]] = (
    EQUILIBRIUM_CAPABILITY_TEST_FILE,
)

INTEGRATION_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/workflows/repo/test_internal_package_workspace.py",
    "tests/workflows/repo/test_package_extension_boundary.py",
)

FRONTEND_API_TEST_TARGETS: Final[tuple[str, ...]] = (
    *PROVIDER_API_TEST_TARGETS,
)

GENERIC_TEST_TARGETS: Final[tuple[str, ...]] = (
    *FRONTEND_API_TEST_TARGETS,
    *EQUILIBRIUM_PACKAGE_CONTRACT_TARGETS,
    "packages/epcsaft/tests/native/state/test_pressure_density.py",
    "packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py",
    "tests/native/contracts/test_equation_registry.py::test_equation_registry_outputs_are_synced",
    *NATIVE_CONTRACT_TEST_TARGETS,
    *INTEGRATION_TEST_TARGETS,
    "tests/workflows/repo/test_project_structure.py",
    "tests/workflows/repo/test_run_pytest.py::test_list_slices_exits_without_running_pytest",
    "tests/workflows/repo/test_workflow_entrypoints.py::test_docs_make_confidence_suite_the_default_runtime_check",
)
CONFIDENCE_TEST_TARGETS: Final[tuple[str, ...]] = (
    *GENERIC_TEST_TARGETS,
    "packages/epcsaft/tests/native/state/test_contributions.py::test_native_residual_helmholtz_and_compressibility_contributions_match_neutral_contract",
)
EQUILIBRIUM_CONFIDENCE_TEST_TARGETS: Final[tuple[str, ...]] = tuple(
    EQUILIBRIUM_VALIDATION_TARGETS_BY_FAMILY[str(row["key"])] for row in production_equilibrium_activation_rows()
)
EQUILIBRIUM_API_TEST_TARGETS: Final[tuple[str, ...]] = (
    "packages/epcsaft-equilibrium/tests/api/test_imports.py",
    f"{EQUILIBRIUM_API_TEST_FILE}::test_workflow_object_is_constructed_with_problem_spec",
    f"{EQUILIBRIUM_API_TEST_FILE}::test_equilibrium_constructor_configures_route_before_solve",
    f"{EQUILIBRIUM_API_TEST_FILE}::test_equilibrium_requires_constructor_route",
    f"{EQUILIBRIUM_API_TEST_FILE}::test_constructor_enforces_route_required_and_forbidden_specs",
    f"{EQUILIBRIUM_API_TEST_FILE}::test_solve_signature_rejects_legacy_route_specs",
    f"{EQUILIBRIUM_API_TEST_FILE}::test_equilibrium_problem_and_structure_are_read_only_metadata",
    f"{EQUILIBRIUM_API_TEST_FILE}::test_equilibrium_problem_fixed_specs_are_deeply_read_only",
    f"{EQUILIBRIUM_API_TEST_FILE}::test_solver_options_reject_ignored_backend_selection_knobs",
    f"{EQUILIBRIUM_API_TEST_FILE}::test_equilibrium_lle_route_configures_neutral_liquid_pair_structure",
    f"{EQUILIBRIUM_API_TEST_FILE}::test_equilibrium_lle_constructor_rejects_associating_and_ionic_inputs",
    EQUILIBRIUM_BUBBLE_DERIVATIVE_TEST_FILE,
    *EQUILIBRIUM_PACKAGE_CONTRACT_TARGETS,
)
RUNTIME_TEST_TARGETS: Final[tuple[str, ...]] = (
    "packages/epcsaft/tests/api/frontend/test_state_properties.py::test_cppad_state_proves_hydrocarbon_values_and_derivatives",
    "packages/epcsaft/tests/native/state/test_pressure_density.py",
    "packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py",
)
API_TEST_TARGETS: Final[tuple[str, ...]] = PROVIDER_API_TEST_TARGETS
NATIVE_TEST_TARGETS: Final[tuple[str, ...]] = (
    "packages/epcsaft/tests/native/state/test_pressure_density.py",
    "packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py",
    "packages/epcsaft/tests/native/state/test_bubble_derivatives.py",
    "packages/epcsaft/tests/native/state/test_contributions.py",
    "packages/epcsaft/tests/native/state/test_runtime_cache.py",
)
TEST_SLICES: Final[dict[str, dict[str, object]]] = {
    "generic": {"targets": GENERIC_TEST_TARGETS, "cheap_by_default": True},
    "all": {
        "targets": ("tests", "packages/epcsaft/tests", "packages/epcsaft-equilibrium/tests", "packages/epcsaft-regression/tests"),
        "cheap_by_default": False,
    },
    "confidence": {"targets": CONFIDENCE_TEST_TARGETS, "cheap_by_default": False},
    "provider-api": {"targets": PROVIDER_API_TEST_TARGETS, "cheap_by_default": True},
    "equilibrium-confidence": {"targets": EQUILIBRIUM_CONFIDENCE_TEST_TARGETS, "cheap_by_default": False},
    "equilibrium-api": {"targets": EQUILIBRIUM_API_TEST_TARGETS, "cheap_by_default": True},
    "regression": {"targets": REGRESSION_TEST_TARGETS, "cheap_by_default": False},
    "integration": {"targets": INTEGRATION_TEST_TARGETS, "cheap_by_default": True},
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
    "provider": {
        "commands": (("scripts/dev/doctor.py",), ("run_pytest.py", "--provider-api", "-q")),
        "cheap_by_default": True,
        "evidence": "doctor plus provider-owned API pytest slice",
    },
    "equilibrium": {
        "commands": (("scripts/dev/doctor.py",), ("run_pytest.py", "--equilibrium-api", "-q")),
        "cheap_by_default": True,
        "evidence": "doctor plus equilibrium-extension API and capability pytest slice",
    },
    "regression": {
        "commands": (("scripts/dev/doctor.py",), ("run_pytest.py", "--regression", "-q")),
        "cheap_by_default": False,
        "evidence": "doctor plus regression-extension pytest slice",
    },
    "integration": {
        "commands": (("scripts/dev/doctor.py",), ("run_pytest.py", "--integration", "-q")),
        "cheap_by_default": True,
        "evidence": "doctor plus package-extension integration pytest slice",
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
                "packages/epcsaft-regression/tests/native/test_pure.py",
                "packages/epcsaft-regression/tests/native/test_binary.py",
                "-q",
            ),
        ),
        "cheap_by_default": False,
        "evidence": "Ceres and CppAD build profile plus focused native regression tests",
    },
    "equilibrium-confidence": {
        "commands": (("scripts/dev/doctor.py",), ("run_pytest.py", "--equilibrium-confidence", "-q", "-s")),
        "cheap_by_default": False,
        "evidence": "doctor plus one focused convergence target for each selector-admitted equilibrium family",
    },
    "equilibrium-debug": {
        "commands": (
            ("scripts/dev/doctor.py",),
            (
                "scripts/validation/check_phase_discovery.py",
                "--debug",
                "--include-route-refinement",
                "--require-complete",
            ),
        ),
        "cheap_by_default": False,
        "evidence": "doctor plus one phase-discovery route with verbose TPD and Ipopt diagnostics",
    },
}


def registry_targets(name: str) -> tuple[str, ...]:
    """Return the registered pytest targets for a named slice."""

    return tuple(str(target) for target in TEST_SLICES[name]["targets"])


def validation_lane_commands(name: str) -> tuple[tuple[str, ...], ...]:
    """Return executable commands for a named validation lane."""

    return tuple(tuple(str(part) for part in command) for command in VALIDATION_LANES[name]["commands"])


def registered_ipopt_public_routes() -> list[str]:
    """Return public Ipopt route labels registered by activation-driven capability evidence."""

    return sorted(public_ipopt_route_family_map())
