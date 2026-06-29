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
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "associating_neutral_lle_gross_2002_public_exact_hessian",
        "derivative": "association_lagrangian_hessian",
        "backend": "cppad_implicit_association",
        "supported": True,
        "classification": "production_supported",
        "public_admission_state": "public_route_open",
        "public_route": "lle",
        "selector_family": "neutral_lle",
        "source_configuration": "Gross2002 Figure8 methanol-cyclohexane",
        "component_pair": ("methanol", "cyclohexane"),
        "assoc_scheme": "2B",
        "k_ij": 0.051,
        "phase_count": 2,
        "source_fixture": (
            "data/reference/equilibrium_benchmarks/associating_lle/"
            "methanol_cyclohexane"
        ),
        "reason": "issue #190 admits only the source-backed Gross/Sadowski 2002 methanol/cyclohexane neutral two-phase LLE proof from #145 through exact implicit-association Hessian evidence",
        "tests": (
            "scripts/validation/check_associating_gfpe_gate.py",
            "scripts/validation/check_associating_lle_gross_2002.py",
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py",
            "packages/epcsaft-equilibrium/tests/native/results/test_associating_lle_reference_values.py",
            "tests/native/contracts/test_associating_gfpe_gate_checker.py",
            "tests/native/contracts/test_associating_lle_gross_2002_checker.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "associating_neutral_lle_gross_2002_figure_10_public_exact_hessian",
        "derivative": "association_lagrangian_hessian",
        "backend": "cppad_implicit_association",
        "supported": True,
        "classification": "production_supported",
        "public_admission_state": "public_route_open",
        "public_route": "lle",
        "selector_family": "neutral_lle",
        "source_configuration": "Gross2002 Figure10 water-1-pentanol",
        "component_pair": ("water", "1-pentanol"),
        "assoc_scheme": "2B",
        "k_ij": 0.016,
        "phase_count": 2,
        "source_fixture": "analyses/paper_validation/2002_gross/figures/figure_10",
        "reason": "Figure 10 full replication admits only the source-backed Gross/Sadowski 2002 water/1-pentanol lower LLE boundary through exact implicit-association Hessian evidence.",
        "tests": (
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py",
            "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "associating_neutral_vle_gross_2002_figure_10_public_exact_hessian",
        "derivative": "association_lagrangian_hessian",
        "backend": "cppad_implicit_association",
        "supported": True,
        "classification": "production_supported",
        "public_admission_state": "public_route_open",
        "public_route": "bubble_pressure/dew_pressure",
        "selector_family": "bubble_dew_derived_routes",
        "source_configuration": "Gross2002 Figure10 water-1-pentanol",
        "component_pair": ("water", "1-pentanol"),
        "assoc_scheme": "2B",
        "k_ij": 0.016,
        "phase_count": 2,
        "source_fixture": "analyses/paper_validation/2002_gross/figures/figure_10",
        "reason": "Figure 10 full replication admits only the source-backed Gross/Sadowski 2002 water/1-pentanol upper VLLE/VLE boundary through pressure-route exact implicit-association Hessian evidence.",
        "tests": (
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py",
            "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "neutral_multiphase_nonassoc",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_explicit_density",
        "supported": True,
        "classification": "production_supported",
        "reason": "production selector exposes explicit neutral nonassociating multiphase sets through the strict reduced-fugacity residual route",
        "tests": (
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "single_component_vle",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_phase_blocks_with_cppad_implicit_association_for_pure_2b_associating_inputs",
        "supported": True,
        "classification": "production_supported",
        "reason": "production selector exposes single-component VLE saturation through a fixed-temperature pressure route with exact Ipopt callbacks, including the narrow pure neutral 2B associating admission used for Gross/Sadowski 2002 Figure 1",
        "tests": (
            "packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py",
            "packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py",
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "electrolyte_gfpe_readiness",
        "quantity": "electrolyte_held2_readiness_born_ssm_ds_exactness",
        "derivative": "born_ssm_ds_composition_fugacity_activity_and_parameter_receipts",
        "backend": "cppad_born_ssm_ds",
        "supported": True,
        "classification": "prerequisite_evidence",
        "public_admission_state": "prerequisite_evidence_only",
        "selector_family": "electrolyte_lle",
        "source_configuration": "Khudaida 2026 electrolyte LLE readiness",
        "component_set": ("water", "ethanol", "isobutanol", "NaCl"),
        "reduced_basis": "charge_neutral_NaCl_amount_lift",
        "phase_count": 2,
        "source_fixture": (
            "data/reference/equilibrium_benchmarks/electrolyte_lle/"
            "water_ethanol_isobutanol_nacl"
        ),
        "reason": (
            "issue #300 records the electrolyte HELD2 prerequisite gate: source-backed "
            "Khudaida inputs, exact charge-neutral NaCl amount lifting, CppAD Born "
            "SSM/DS derivative receipts, and downstream public-admission prerequisites."
        ),
        "tests": (
            "scripts/validation/check_electrolyte_held2_readiness.py",
            "tests/native/contracts/test_electrolyte_held2_readiness_checker.py",
            "packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py",
            "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py",
            "tests/native/contracts/test_generalized_equilibrium_registry.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "electrolyte_phase_discovery",
        "quantity": "electrolyte_held2_counterion_pair_phase_discovery",
        "derivative": "counterion_pair_reduced_tpd_bookkeeping",
        "backend": "native_counterion_pair_phase_discovery",
        "supported": True,
        "classification": "phase_discovery_evidence",
        "public_admission_state": "prerequisite_evidence_only",
        "selector_family": "electrolyte_lle",
        "source_configuration": "Khudaida 2026 NaCl plus Ascani 2022 mixed-electrolyte counterion fixtures",
        "component_set": ("water", "ethanol", "isobutanol", "NaCl"),
        "source_fixture": (
            "data/reference/equilibrium_benchmarks/electrolyte_lle/"
            "water_ethanol_isobutanol_nacl"
        ),
        "preprocessor_fixtures": (
            "analyses/paper_validation/2022_ascani/tables/table_005/table_005.md",
            "docs/papers/md/Equilibrium/Ascani, Sadowski, Held - 2022 - Calculation of Multiphase Equilibria Containing Mixed Solvents and M.md",
        ),
        "reduced_basis": "independent_counterion_pair_matrix",
        "stage_status": "phase_discovery_complete_stage_iii_pending",
        "reason": (
            "issue #306 records the electrolyte HELD2 phase-discovery gate: "
            "native counterion-pair matrix construction, charge-neutral candidate "
            "diagnostics, pair-based mean-ionic bookkeeping, source-backed multi-ion "
            "preprocessor fixtures, and downstream Stage III/postsolve prerequisites."
        ),
        "tests": (
            "scripts/validation/check_electrolyte_held2_phase_discovery.py",
            "tests/native/contracts/test_electrolyte_held2_phase_discovery.py",
            "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py",
            "tests/native/contracts/test_generalized_equilibrium_registry.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "electrolyte_stage_iii_refinement",
        "quantity": "electrolyte_held2_stage_iii_reduced_variable_refinement",
        "derivative": "counterion_pair_reduced_residual_jacobian_hessian_receipts",
        "backend": "native_electrolyte_stage_iii_refinement",
        "supported": True,
        "classification": "stage_iii_refinement_evidence",
        "public_admission_state": "prerequisite_evidence_only",
        "selector_family": "electrolyte_lle",
        "source_configuration": "Khudaida 2026 NaCl local Stage III refinement",
        "component_set": ("water", "ethanol", "isobutanol", "NaCl"),
        "source_fixture": (
            "data/reference/equilibrium_benchmarks/electrolyte_lle/"
            "water_ethanol_isobutanol_nacl"
        ),
        "reduced_basis": "independent_counterion_pair_matrix",
        "stage_status": "stage_iii_refinement_complete_postsolve_pending",
        "route_hessian_mode": "limited_memory_charged_born_route",
        "reason": (
            "issue #312 records the electrolyte HELD2 Stage III refinement gate: "
            "the checker consumes #269/#300/#302/#306, calls native "
            "`_native_electrolyte_stage_iii_refinement`, retains exact reduced "
            "counterion-pair residual Jacobian/Hessian receipts, records strict "
            "Ipopt solver diagnostics, and feeds postsolve certification plus "
            "public electrolyte route admission."
        ),
        "tests": (
            "scripts/validation/check_electrolyte_stage_iii_refinement.py",
            "tests/native/contracts/test_electrolyte_stage_iii_refinement.py",
            "tests/native/contracts/test_electrolyte_held2_phase_discovery.py",
            "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py",
            "tests/native/contracts/test_generalized_equilibrium_registry.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "electrolyte_postsolve_certification",
        "quantity": "electrolyte_held2_postsolve_phase_set_certification",
        "derivative": "postsolve_physical_residual_certification",
        "backend": "native_electrolyte_postsolve_certification",
        "supported": True,
        "classification": "postsolve_certification_evidence",
        "public_admission_state": "prerequisite_evidence_only",
        "selector_family": "electrolyte_lle",
        "source_configuration": "Khudaida 2026 NaCl local postsolve certification",
        "component_set": ("water", "ethanol", "isobutanol", "NaCl"),
        "source_fixture": (
            "data/reference/equilibrium_benchmarks/electrolyte_lle/"
            "water_ethanol_isobutanol_nacl"
        ),
        "reduced_basis": "independent_counterion_pair_matrix",
        "stage_status": "postsolve_certified_public_admission_pending",
        "route_hessian_mode": "limited_memory_charged_born_route",
        "reason": (
            "issue #313 records the electrolyte postsolve certification gate: "
            "the checker consumes #312, calls native "
            "`_native_electrolyte_postsolve_certification`, retains explicit-ion "
            "reconstruction, per-phase and total charge residuals, neutral and "
            "mean-ionic transfer residuals, pressure consistency, phase amount, "
            "composition normalization, and domain-margin diagnostics consumed by "
            "#314 public electrolyte route admission."
        ),
        "tests": (
            "scripts/validation/check_electrolyte_postsolve_certification.py",
            "tests/native/contracts/test_electrolyte_postsolve_certification.py",
            "tests/native/contracts/test_electrolyte_stage_iii_refinement.py",
            "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py",
            "tests/native/contracts/test_generalized_equilibrium_registry.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "electrolyte_public_admission",
        "quantity": "electrolyte_lle_khudaida_public_admission",
        "derivative": "exact_reduced_counterion_pair_jacobian_hessian_receipts",
        "backend": "native_electrolyte_postsolve_certification",
        "supported": True,
        "classification": "production_supported",
        "public_admission_state": "public_route_open",
        "public_route": "electrolyte_lle",
        "selector_family": "electrolyte_lle",
        "source_configuration": "Khudaida 2026 NaCl mixed-solvent electrolyte LLE",
        "component_set": ("water", "ethanol", "isobutanol", "NaCl"),
        "native_component_set": ("H2O", "Ethanol", "Butanol", "Na+", "Cl-"),
        "source_fixture": (
            "data/reference/equilibrium_benchmarks/electrolyte_lle/"
            "water_ethanol_isobutanol_nacl"
        ),
        "parameter_bundle": "analyses/paper_validation/2026_khudaida/parameters",
        "reduced_basis": "independent_counterion_pair_matrix",
        "stage_status": "public_admission_complete",
        "phase_discovery_status": "held2_public_route_phase_discovery_and_scenario_validation_admitted",
        "route_hessian_mode": "limited_memory_charged_born_route_with_exact_reduced_derivative_receipts",
        "reason": (
            "issue #350 admits only the source-backed Khudaida 2026 NaCl mixed-solvent "
            "electrolyte LLE route after #269/#300/#302/#306/#312/#313/#314 and #344-#349 "
            "evidence proves source fixture parsing, reduced charge-neutral variables, "
            "continuous charge-neutral TPD, HELD2 Stage I/II discovery, Stage III replay "
            "consumption, postsolve phase-set certification, and the retained scenario ladder."
        ),
        "tests": (
            "scripts/validation/check_electrolyte_public_admission.py",
            "scripts/validation/check_electrolyte_held2_public_route_scenarios.py",
            "tests/native/contracts/test_electrolyte_public_admission.py",
            "tests/native/contracts/test_electrolyte_postsolve_certification.py",
            "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py",
            "tests/native/contracts/test_generalized_equilibrium_registry.py",
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
            "input_scope": (
                "neutral non-reactive non-electrolyte liquid/liquid mixtures: non-associating mixtures plus "
                "the source-backed Gross/Sadowski 2002 methanol/cyclohexane and water/1-pentanol associating proof fixtures"
            ),
            "requires": ["cppad", "ipopt"],
        },
        "neutral_multiphase_nonassoc": {
            "available": bool(activation["ipopt_available"]),
            "production": True,
            "entrypoint": "Equilibrium(mixture, route='multiphase', T=..., P=..., z=..., phase_kinds=[...]).solve()",
            "public_routes": public_routes_by_family["neutral_multiphase_nonassoc"],
            "selector_core": True,
            "input_scope": "neutral non-reactive non-electrolyte non-associating explicit phase-kind sets",
            "requires": ["cppad", "ipopt"],
        },
        "single_component_vle": {
            "available": bool(activation["ipopt_available"]),
            "production": True,
            "entrypoint": "Equilibrium(mixture, route='single_component_vle', T=...).solve()",
            "public_routes": public_routes_by_family["single_component_vle"],
            "selector_core": True,
            "input_scope": "single neutral non-reactive non-electrolyte component, including pure 2B associating components for the retained Gross/Sadowski 2002 Figure 1 saturation proof",
            "requires": ["cppad", "ipopt"],
        },
        "electrolyte_lle": {
            "available": bool(activation["ipopt_available"]),
            "production": True,
            "entrypoint": "Equilibrium(mixture, route='electrolyte_lle', T=..., P=..., z=...).solve()",
            "public_routes": public_routes_by_family["electrolyte_lle"],
            "selector_core": False,
            "input_scope": (
                "source-backed Khudaida 2026 NaCl mixed-solvent LLE for explicit-ion "
                "H2O/Ethanol/Butanol/Na+/Cl- feeds built from the retained parameter bundle"
            ),
            "phase_discovery_status": "held2_public_route_phase_discovery_and_scenario_validation_admitted",
            "validation_scope": (
                "retained HELD2 Stage I/II public-route discovery, Stage III replay consumption, "
                "postsolve certification, and stable/unstable/boundary/phase-label/neutral-limit/"
                "common-ion/mixed-salt scenario ladder for the admitted electrolyte_lle fixture only"
            ),
            "requires": ["cppad", "ipopt"],
            "unsupported_surfaces": [
                "reactive_electrolyte_lle",
                "reactive_lle",
                "reactive_speciation",
                "ce",
                "cpe",
                "regression",
            ],
        },
        "problem_objects": {
            "available": True,
            "backend": "constructor_configured_frontend",
            "classes": list(EQUILIBRIUM_PROBLEM_OBJECT_CLASSES),
            "entrypoint": "Equilibrium(mixture, route=..., ...)",
        },
    }
