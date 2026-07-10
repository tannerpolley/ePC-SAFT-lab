"""Repository-owned pytest slices and validation lanes.

This module uses only the Python standard library and contains no scientific
capability metadata.  Package runtime reports describe package behavior;
repository validation orchestration belongs here.
"""

from __future__ import annotations

from typing import Final

EQUILIBRIUM_API_TEST_FILE: Final = "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py"
EQUILIBRIUM_SINGLE_COMPONENT_VLE_TEST_FILE: Final = (
    "packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py"
)
EQUILIBRIUM_GROSS_INTERNAL_CERTIFICATION_TEST_FILE: Final = (
    "packages/epcsaft-equilibrium/tests/api/test_associating_lle_gross_2002_certification.py"
)
EQUILIBRIUM_BUBBLE_DERIVATIVE_TEST_FILE: Final = "packages/epcsaft-equilibrium/tests/api/test_bubble_derivatives.py"
EQUILIBRIUM_CAPABILITY_TEST_FILE: Final = "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py"

NATIVE_CONTRACT_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/native/contracts/test_generalized_equilibrium_registry.py",
    "tests/native/contracts/test_equilibrium_benchmark_registry.py",
    "tests/native/contracts/test_neutral_tp_flash_fixture_checker.py",
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

REGRESSION_TEST_TARGETS: Final[tuple[str, ...]] = (
    "packages/epcsaft-regression/tests/api/test_regression.py",
    "packages/epcsaft-regression/tests/native/test_pure.py",
    "packages/epcsaft-regression/tests/native/test_binary.py",
    "packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py",
    "packages/epcsaft-regression/tests/contracts/test_ceres_cppad_build_contract.py",
)

EQUILIBRIUM_PACKAGE_CONTRACT_TARGETS: Final[tuple[str, ...]] = (EQUILIBRIUM_CAPABILITY_TEST_FILE,)

INTEGRATION_TEST_TARGETS: Final[tuple[str, ...]] = (
    "tests/workflows/repo/test_internal_package_workspace.py",
    "tests/workflows/repo/test_package_extension_boundary.py",
)

GENERIC_TEST_TARGETS: Final[tuple[str, ...]] = (
    *PROVIDER_API_TEST_TARGETS,
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
    "packages/epcsaft/tests/native/state/test_contributions.py::"
    "test_native_residual_helmholtz_and_compressibility_contributions_match_neutral_contract",
)

EQUILIBRIUM_CONFIDENCE_TEST_TARGETS: Final[tuple[str, ...]] = (
    f"{EQUILIBRIUM_API_TEST_FILE}::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route",
    f"{EQUILIBRIUM_SINGLE_COMPONENT_VLE_TEST_FILE}::test_single_component_vle_route_returns_saturation_payload",
    f"{EQUILIBRIUM_GROSS_INTERNAL_CERTIFICATION_TEST_FILE}::"
    "test_associating_lle_gross_2002_certification_payload_reports_shared_contract",
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
    f"{EQUILIBRIUM_SINGLE_COMPONENT_VLE_TEST_FILE}::"
    "test_single_component_vle_route_configures_pure_temperature_problem",
    f"{EQUILIBRIUM_SINGLE_COMPONENT_VLE_TEST_FILE}::test_single_component_vle_route_rejects_binary_mixture",
    f"{EQUILIBRIUM_SINGLE_COMPONENT_VLE_TEST_FILE}::test_single_component_vle_route_rejects_public_composition_specs",
    EQUILIBRIUM_BUBBLE_DERIVATIVE_TEST_FILE,
    *EQUILIBRIUM_PACKAGE_CONTRACT_TARGETS,
)

RUNTIME_TEST_TARGETS: Final[tuple[str, ...]] = (
    "packages/epcsaft/tests/api/frontend/test_state_properties.py::"
    "test_cppad_state_proves_hydrocarbon_values_and_derivatives",
    "packages/epcsaft/tests/native/state/test_pressure_density.py",
    "packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py",
)

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
        "targets": (
            "tests",
            "packages/epcsaft/tests",
            "packages/epcsaft-equilibrium/tests",
            "packages/epcsaft-regression/tests",
        ),
        "cheap_by_default": False,
    },
    "confidence": {"targets": CONFIDENCE_TEST_TARGETS, "cheap_by_default": False},
    "provider-api": {"targets": PROVIDER_API_TEST_TARGETS, "cheap_by_default": True},
    "equilibrium-confidence": {
        "targets": EQUILIBRIUM_CONFIDENCE_TEST_TARGETS,
        "cheap_by_default": False,
    },
    "equilibrium-api": {"targets": EQUILIBRIUM_API_TEST_TARGETS, "cheap_by_default": True},
    "regression": {"targets": REGRESSION_TEST_TARGETS, "cheap_by_default": False},
    "integration": {"targets": INTEGRATION_TEST_TARGETS, "cheap_by_default": True},
    "runtime": {"targets": RUNTIME_TEST_TARGETS, "cheap_by_default": True},
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
    """Return the pytest targets for a named repository slice."""

    return tuple(str(target) for target in TEST_SLICES[name]["targets"])


def validation_lane_commands(name: str) -> tuple[tuple[str, ...], ...]:
    """Return executable commands for a named repository validation lane."""

    return tuple(tuple(str(part) for part in command) for command in VALIDATION_LANES[name]["commands"])


def registered_exact_test_nodes() -> tuple[str, ...]:
    """Return each unique exact pytest node referenced by any named slice."""

    return tuple(
        dict.fromkeys(target for slice_name in TEST_SLICES for target in registry_targets(slice_name) if "::" in target)
    )
