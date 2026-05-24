"""Registered capability evidence and cheap validation lanes.

This module is intentionally side-effect free so command-line wrappers can
import the registry without importing the native extension.
"""

from __future__ import annotations

from typing import Final

IPOPT_PUBLIC_ROUTES: Final[tuple[str, ...]] = (
    "bubble_pressure",
    "bubble_temperature",
    "dew_pressure",
    "dew_temperature",
    "flash",
    "lle",
)

EQUILIBRIUM_PROBLEM_OBJECT_CLASSES: Final[tuple[str, ...]] = (
    "EquilibriumProblem",
    "EquilibriumStructure",
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
        "tests": ("tests/native/regression/test_binary.py",),
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
        "quantity": "bubble_dew_derived_routes",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_phase_blocks",
        "supported": True,
        "classification": "production_supported",
        "reason": "the production selector exposes neutral bubble/dew pressure and temperature routes through exact gradient/Jacobian/Hessian Ipopt callbacks",
        "tests": (
            "tests/api/frontend/test_equilibrium.py",
            "tests/native/equilibrium/diagnostics/test_selector_core_contracts.py",
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
        "reason": "the production selector exposes neutral two-phase TP flash through the native activation-plan compiler, native-owned seed generation, and postsolve certification",
        "tests": (
            "tests/api/frontend/test_equilibrium.py",
            "tests/native/equilibrium/diagnostics/test_selector_core_contracts.py",
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
        "reason": "the production selector exposes neutral nonassociating LLE through the activation-plan compiler and generic two-phase EOS NLP with exact Ipopt callbacks",
        "tests": (
            "tests/api/frontend/test_equilibrium.py",
            "tests/native/equilibrium/results/test_neutral_lle_reference_values.py",
        ),
    },
)

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
            "tests/native/regression/test_pure.py::test_ceres_pure_neutral_regression_owns_optimizer_loop",
            "tests/api/frontend/test_regression.py::test_regression_hydrocarbon_anchor_routes_through_new_object_api",
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
            "tests/native/regression/test_pure.py::test_ceres_pure_neutral_regression_owns_optimizer_loop",
            "tests/native/regression/test_pure.py::test_ceres_pure_ion_regression_uses_cppad_implicit_for_density_osmotic_miac",
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
            "tests/native/regression/test_pure.py::test_ceres_pure_neutral_regression_owns_optimizer_loop",
            "tests/native/regression/test_pure.py::test_ceres_pure_ion_regression_uses_cppad_implicit_for_density_osmotic_miac",
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
            "tests/native/state/test_fugacity_derivatives.py::test_associating_pure_parameter_derivative_results_support_e_assoc_and_vol_a",
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
            "tests/native/state/test_fugacity_derivatives.py::test_associating_pure_parameter_derivative_results_support_e_assoc_and_vol_a",
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
            "tests/native/regression/test_pure.py::test_ceres_pure_ion_regression_uses_cppad_implicit_for_density_osmotic_miac",
            "tests/native/regression/test_liquid_electrolyte.py::test_ceres_liquid_electrolyte_regression_uses_native_ssmds_derivatives",
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
            "tests/native/regression/test_binary.py::test_ceres_binary_kij_regression_uses_native_cppad_implicit_jacobian",
            "tests/native/regression/test_binary.py::test_ceres_binary_kij_regression_accepts_associating_neutral_rows",
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
            "tests/native/state/test_fugacity_derivatives.py::test_associating_binary_parameter_derivative_results_support_lij_and_khb",
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
            "tests/native/state/test_fugacity_derivatives.py::test_associating_binary_parameter_derivative_results_support_lij_and_khb",
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
            "tests/native/regression/test_liquid_electrolyte.py::test_ceres_liquid_electrolyte_regression_uses_native_ssmds_derivatives",
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
    "tests/native/contracts/test_generalized_activation_matrix_registry.py",
    "tests/native/contracts/test_equilibrium_benchmark_registry.py",
    "tests/native/contracts/test_equilibrium_activation_capabilities.py",
    "tests/native/equilibrium/diagnostics/test_selector_core_contracts.py",
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
    "tests/native/equilibrium/diagnostics/test_selector_core_contracts.py",
    "tests/native/equilibrium/diagnostics/test_native_route_diagnostics_contract.py",
    "tests/api/frontend/test_equilibrium.py",
    "tests/native/equilibrium/results/test_neutral_vle_reference_values.py",
    "tests/native/state/test_bubble_derivatives.py",
)
EQUILIBRIUM_API_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/api/frontend/test_equilibrium.py",
    "tests/native/state/test_bubble_derivatives.py",
)
RUNTIME_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/api/frontend/test_state_properties.py::test_cppad_state_proves_hydrocarbon_values_and_derivatives",
    "tests/native/state/test_pressure_density.py",
    "tests/native/state/test_phase_state_sensitivities.py",
)
API_TEST_TARGETS: Final[tuple[str, ...]] = ("tests/api/frontend",)
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
    """Return public Ipopt route labels registered by activation-driven capability evidence."""

    return list(IPOPT_PUBLIC_ROUTES)
