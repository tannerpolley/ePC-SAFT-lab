"""Capability reporting for the equilibrium extension package."""

from __future__ import annotations

from ._native import native_ipopt_backend_info, provider_contract
from .capability_evidence import (
    DEVELOPMENT_COMPONENT_EVIDENCE,
    production_capability_evidence,
)
from .equilibrium_activation import (
    EQUILIBRIUM_ACTIVATION_MATRIX,
    EQUILIBRIUM_SELECTOR_ROUTE_CONTRACTS,
)
from .phase_equilibrium_certification import (
    phase_equilibrium_certification_contracts,
    validate_phase_equilibrium_certification_contracts,
)

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
        "reason": "production selector exposes neutral bubble/dew pressure routes through exact Ipopt callbacks and retained source-backed evidence",
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
        "classification": "component_evidence",
        "reason": "neutral two-phase TP flash retains component-level solver evidence, but its workbook explicitly does not establish a literature benchmark or public admission",
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
        "classification": "internal_validation_evidence",
        "reason": "neutral nonassociating LLE retains an internal exact-derivative formulation and sampled-candidate validation, but it has no global phase-set proof or public selector admission",
        "tests": (
            "packages/epcsaft-equilibrium/tests/api/test_equilibrium.py",
            "packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "associating_neutral_lle_gross_2002_internal_exact_hessian",
        "derivative": "association_lagrangian_hessian",
        "backend": "cppad_implicit_association",
        "supported": True,
        "classification": "internal_validation_evidence",
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
        "reason": "the source-backed Gross/Sadowski 2002 methanol/cyclohexane case retains internal exact implicit-association Hessian evidence, but the sampled-candidate audit does not prove global phase-set completeness",
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
        "quantity": "associating_neutral_lle_gross_2002_figure_10_internal_exact_hessian",
        "derivative": "association_lagrangian_hessian",
        "backend": "cppad_implicit_association",
        "supported": True,
        "classification": "internal_validation_evidence",
        "selector_family": "neutral_lle",
        "source_configuration": "Gross2002 Figure10 water-1-pentanol",
        "component_pair": ("water", "1-pentanol"),
        "assoc_scheme": "2B",
        "k_ij": 0.016,
        "phase_count": 2,
        "source_fixture": "analyses/paper_validation/2002_gross/figures/figure_10",
        "reason": "Figure 10 retains source-backed internal exact implicit-association Hessian evidence for the lower LLE boundary; it is not a global phase-set proof or public-route admission.",
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
        "classification": "component_evidence",
        "selector_family": "bubble_dew_derived_routes",
        "source_configuration": "Gross2002 Figure10 water-1-pentanol",
        "component_pair": ("water", "1-pentanol"),
        "assoc_scheme": "2B",
        "k_ij": 0.016,
        "phase_count": 2,
        "source_fixture": "analyses/paper_validation/2002_gross/figures/figure_10",
        "reason": "Figure 10 retains source-backed upper VLLE/VLE component evidence, but it is not an activation proof for the public pressure routes.",
        "tests": (
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py",
            "packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "internal_multiphase_diagnostic",
        "quantity": "neutral_multiphase_nonassoc",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_explicit_density",
        "supported": True,
        "classification": "internal_diagnostic_evidence",
        "selector_family": "neutral_multiphase_nonassoc",
        "reason": "retained internal reduced-fugacity diagnostics do not establish native-selector ownership or public admission",
        "tests": (
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_internal_multiphase_activation_contracts.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "single_component_vle",
        "derivative": "lagrangian_hessian",
        "backend": "cppad_phase_blocks",
        "supported": True,
        "classification": "production_supported",
        "reason": "production selector exposes nonassociating methane, ethane, and propane saturation through a fixed-temperature pressure route with exact Ipopt callbacks and retained NIST joins",
        "tests": (
            "packages/epcsaft-equilibrium/tests/api/test_single_component_vle.py",
            "packages/epcsaft-equilibrium/tests/native/blocks/test_single_component_vle_block.py",
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py",
        ),
    },
    {
        "row_family": "equilibrium",
        "subsystem": "native_ipopt",
        "quantity": "reactive_speciation_standalone_ce_validation",
        "derivative": "standalone_ce_lagrangian_hessian_and_final_proof_diagnostics",
        "backend": "analytic_ce_objective_with_cppad_eos_activity_extensions",
        "supported": True,
        "classification": "internal_validation_evidence",
        "selector_family": "reactive_speciation",
        "reason": (
            "standalone homogeneous CE remains an internal validation target; the live MEA continuation "
            "fails final balance and stationarity proof and therefore authorizes no public route"
        ),
        "tests": (
            "packages/epcsaft-equilibrium/tests/native/diagnostics/test_chemical_equilibrium_eos_activity.py",
            "tests/native/contracts/test_standalone_ce_gate.py",
            "tests/native/contracts/test_ce_robustness_followup_gate.py",
            "scripts/validation/check_standalone_ce_gate.py",
            "scripts/validation/check_ce_robustness_followup.py",
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
            "SSM/DS derivative receipts retained for selector-integration repair."
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
            "Ipopt solver diagnostics and feeds internal postsolve validation."
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
        "selector_family": "electrolyte_lle",
        "source_configuration": "Khudaida 2026 NaCl local postsolve certification",
        "component_set": ("water", "ethanol", "isobutanol", "NaCl"),
        "source_fixture": (
            "data/reference/equilibrium_benchmarks/electrolyte_lle/"
            "water_ethanol_isobutanol_nacl"
        ),
        "reduced_basis": "independent_counterion_pair_matrix",
        "stage_status": "postsolve_component_diagnostic_complete_selector_integration_pending",
        "route_hessian_mode": "limited_memory_charged_born_route",
        "reason": (
            "issue #313 records the electrolyte postsolve certification gate: "
            "the checker consumes #312, calls native "
            "`_native_electrolyte_postsolve_certification`, retains explicit-ion "
            "reconstruction, per-phase and total charge residuals, neutral and "
            "mean-ionic transfer residuals, pressure consistency, phase amount, "
            "composition normalization, and domain-margin diagnostics retained for repair."
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
        "subsystem": "electrolyte_validation_repair",
        "quantity": "electrolyte_lle_khudaida_repair_evidence",
        "derivative": "exact_reduced_counterion_pair_jacobian_hessian_receipts",
        "backend": "native_electrolyte_postsolve_certification",
        "supported": True,
        "classification": "internal_validation_evidence",
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
        "stage_status": "retained_diagnostic_evidence",
        "phase_discovery_status": "held2_component_diagnostics_retained_selector_integration_required",
        "route_hessian_mode": "limited_memory_charged_born_route_with_exact_reduced_derivative_receipts",
        "reason": (
            "source-backed Khudaida component diagnostics are retained for repair, but direct postsolve "
            "dispatch does not establish native-selector ownership or public electrolyte-LLE admission"
        ),
        "tests": (
            "scripts/validation/check_electrolyte_public_admission.py",
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
    grouped: dict[str, list[str]] = {}
    proofs_by_family: dict[str, list[str]] = {}
    selector_families: set[str] = set()
    for contract in EQUILIBRIUM_SELECTOR_ROUTE_CONTRACTS:
        family = str(contract["selector_family"])
        selector_families.add(family)
        proof_routes = [str(route) for route in contract.get("proof_routes", ())]
        if not bool(contract["production_exposed"]):
            if proof_routes:
                raise RuntimeError(
                    f"Closed equilibrium selector route '{contract['public_route']}' publishes proofs."
                )
            continue
        grouped.setdefault(family, []).append(str(contract["public_route"]))
        proofs_by_family.setdefault(family, []).extend(proof_routes)

    activation_by_family = {
        str(row["key"]): row for row in EQUILIBRIUM_ACTIVATION_MATRIX
    }
    unknown_families = selector_families - set(activation_by_family)
    if unknown_families:
        raise RuntimeError(
            "Selector routes reference unknown activation families: "
            + ", ".join(sorted(unknown_families))
            + "."
        )
    for family in selector_families:
        activation = activation_by_family[family]
        public_routes = grouped.get(family, [])
        if bool(activation["production_exposed"]) != bool(public_routes):
            raise RuntimeError(
                f"Selector route exposure does not match activation family '{family}'."
            )
        if list(activation.get("public_routes", ())) != public_routes:
            raise RuntimeError(
                f"Selector public routes do not match activation family '{family}'."
            )
        if list(activation.get("proof_routes", ())) != proofs_by_family.get(family, []):
            raise RuntimeError(
                f"Selector proof routes do not match activation family '{family}'."
            )
    return {family: tuple(routes) for family, routes in grouped.items()}


def public_route_family_map() -> dict[str, str]:
    route_to_family: dict[str, str] = {}
    public_routes_by_family()
    for contract in EQUILIBRIUM_SELECTOR_ROUTE_CONTRACTS:
        if not bool(contract["production_exposed"]):
            continue
        route = str(contract["public_route"])
        family = str(contract["selector_family"])
        if route in route_to_family:
            raise RuntimeError(
                f"Public equilibrium route '{route}' is admitted by both "
                f"'{route_to_family[route]}' and '{family}'."
            )
        route_to_family[route] = family
    return route_to_family


def registered_public_routes() -> list[str]:
    return sorted(public_route_family_map())


def _activation_capabilities(*, ipopt_route_available: bool) -> dict[str, object]:
    rows = [_capability_value(row) for row in EQUILIBRIUM_ACTIVATION_MATRIX]
    selector_route_contracts = [
        _capability_value(row) for row in EQUILIBRIUM_SELECTOR_ROUTE_CONTRACTS
    ]
    evidence = production_capability_evidence(EQUILIBRIUM_ACTIVATION_MATRIX)
    production_families = [str(row["key"]) for row in rows if bool(row["production_exposed"])]
    declared_not_exposed = [str(row["key"]) for row in rows if str(row["exposure_status"]) == "declared_not_exposed"]
    routes_by_family = {family: list(routes) for family, routes in public_routes_by_family().items()}
    return {
        "source": "native_cpp",
        "rows": rows,
        "selector_route_contracts": selector_route_contracts,
        "production_families": production_families,
        "declared_not_exposed_families": declared_not_exposed,
        "public_routes": registered_public_routes(),
        "public_routes_by_family": routes_by_family,
        "public_route_family_map": dict(sorted(public_route_family_map().items())),
        "evidence_complete_families": list(evidence),
        "ipopt_available": ipopt_route_available,
    }


def capabilities() -> dict[str, object]:
    from epcsaft import runtime_build_info

    native_dependencies = runtime_build_info()["native_dependencies"]  # type: ignore[index]
    cppad = dict(native_dependencies["cppad"])  # type: ignore[index]
    ipopt = native_ipopt_backend_info()
    ipopt_route_available = bool(ipopt.get("available", False))
    activation = _activation_capabilities(ipopt_route_available=ipopt_route_available)
    production_evidence = {
        family: _capability_value(record)
        for family, record in production_capability_evidence(
            EQUILIBRIUM_ACTIVATION_MATRIX
        ).items()
    }
    family_capabilities = {
        family: {
            "available": bool(activation["ipopt_available"]),
            "production": True,
            "entrypoint": record["public_entrypoint"],
            "public_routes": record["public_routes"],
            "selector_core": True,
            "input_scope": record["input_scope"],
            "requires": ["cppad", "ipopt"],
            "evidence": record,
        }
        for family, record in production_evidence.items()
    }
    route_derivative_rows = [_capability_value(row) for row in EQUILIBRIUM_ROUTE_DERIVATIVE_EVIDENCE]
    route_derivative_evidence = {
        "source": "epcsaft_equilibrium",
        "implemented_capability_claims_only": False,
        "production_rows_are_capability_safe": True,
        "rows": route_derivative_rows,
    }
    phase_equilibrium_certification = phase_equilibrium_certification_contracts(
        activation=activation,
        route_derivative_evidence=route_derivative_evidence,
    )
    certification_blockers = validate_phase_equilibrium_certification_contracts(
        phase_equilibrium_certification,
    )
    if certification_blockers:
        raise RuntimeError(
            "phase equilibrium certification contract failed: "
            + ", ".join(certification_blockers)
        )
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
        "route_derivative_evidence": route_derivative_evidence,
        "phase_equilibrium_certification": phase_equilibrium_certification,
        "capability_evidence": {
            "source": "epcsaft_equilibrium.capability_evidence",
            "complete_families": list(production_evidence),
            "production_records": production_evidence,
            "development_component_evidence": [
                _capability_value(record) for record in DEVELOPMENT_COMPONENT_EVIDENCE
            ],
        },
        **family_capabilities,
        "problem_objects": {
            "available": True,
            "backend": "constructor_configured_frontend",
            "classes": list(EQUILIBRIUM_PROBLEM_OBJECT_CLASSES),
            "entrypoint": "Equilibrium(mixture, route=..., ...)",
        },
    }
