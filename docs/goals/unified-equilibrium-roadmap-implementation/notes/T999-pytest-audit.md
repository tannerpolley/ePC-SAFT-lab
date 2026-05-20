# Pytest Audit For Unified Equilibrium Cleanup

Date: 2026-05-20

Scope: static audit only. No broad pytest run was used for this inventory.

Update: `tests/helpers/*.py` have been restored as active test support modules.
`tests/helpers/__init__.py` remains deleted with the rest of the pytest package
sentinels. Public/Python equilibrium tests have been moved from
`tests/equilibrium` into `tests/api/equilibrium`; `tests/native/equilibrium`
is now the native C++/pybind equilibrium contract boundary.

## Rubric

Scores are 1-5, where 5 is strongest.

- Relevance: proves a generic package API, native contract, solver contract, or workflow guard that belongs in pytest.
- Scope: tight and diagnostic, with small inputs and clear failure cause. Low scope means broad, paper-scale, slow, or overly specific.
- Need: should remain in pytest rather than moving to an explicit benchmark, analysis, profile, or downstream validation workflow.

Recommended actions:

- Keep: current pytest ownership is right.
- Split: keep behavior, but divide by route/API concern.
- Merge: combine with a nearby smaller contract file.
- Move: remove from pytest and put under benchmark/profile/analysis self-checks.
- Delete: keep deleted or remove because it is paper-scale, obsolete, or redundant.
- Restore: deletion is wrong for active pytest imports.

## Folder Scores

| Path | Relevance | Scope | Need | Recommendation | Reason |
| --- | ---: | ---: | ---: | --- | --- |
| `tests/api` | 5 | 3 | 5 | Keep, split bulky files | Public API contracts are right for pytest, but reactive/regression/runtime files are too option-combinatorial. |
| `tests/api/equilibrium` | 5 | 3 | 5 | Keep as public equilibrium API boundary | Generic Python equilibrium API tests belong here; the duplicate root `tests/equilibrium` folder has been removed. |
| `tests/api/package` | 4 | 3 | 4 | Keep, trim downstream names | Useful public package smoke contracts, but should stay generic and not become downstream case-study validation. |
| `tests/api/parameters` | 5 | 4 | 5 | Keep | Parameter schema/template contracts belong in pytest. |
| `tests/api/reactive` | 5 | 2 | 5 | Split and merge | Important generic reactive API coverage, but several files encode too many options and staged/production distinctions. |
| `tests/api/regression` | 5 | 2 | 5 | Split | Required public regression API contracts, but native backend file is too large and should be grouped by target family. |
| `tests/api/runtime` | 5 | 3 | 5 | Split one large file | Runtime public methods belong in pytest; neutral method file is too broad. |
| `tests/api/equilibrium/core` | 5 | 3 | 5 | Keep, split broad files | Good public/core route coverage, but bubble/dew/LLE/native result files should be smaller. |
| `tests/api/equilibrium/electrolyte` | 5 | 3 | 5 | Keep, genericize dataset fixtures | Tests should prove electrolyte LLE/bubble contracts, not Ascani/Khudaida paper reproduction. |
| `tests/api/equilibrium/reactive` | 5 | 3 | 5 | Keep, split coupled route proof from result formatting | Good new-roadmap surface; keep exact route contract diagnostic. |
| `tests/helpers` | 5 | 5 | 5 | Keep restored helper modules; delete only `__init__.py` | Active tests import these modules. The helper `.py` files are support fixtures, not collected tests. |
| `tests/native` | 5 | 3 | 5 | Keep split route-builder files | Native C++/pybind contracts are critical; route-builder proof is now split by route family. |
| `tests/native/ceres` | 5 | 4 | 5 | Keep | Native regression backend smoke contracts belong in pytest. |
| `tests/native/contracts` | 5 | 5 | 5 | Keep | Tight build/equation/derivative/native contract gates. |
| `tests/native/cppad` | 5 | 4 | 5 | Keep, move Figiel analysis dependency out | Exact derivative substrate contracts belong in pytest; one file still depends on analysis data. |
| `tests/native/equilibrium` | 5 | 2 | 5 | Split aggressively | Native equilibrium route tests are necessary, but the monolith and paper-named fixtures make diagnosis hard. |
| `tests/native/runtime` | 5 | 3 | 5 | Keep, move MIAC analysis dependency out | Runtime cache/density/contribution contracts belong in pytest; analysis-owned Figiel MIAC coverage does not. |
| `tests/regression/core` | 4 | 4 | 4 | Keep hydrocarbon anchor; merge fixed reaction constant | The hydrocarbon anchor is trusted exact-Hessian/Ceres proof. Fixed reaction constant belongs near reactive API conventions. |
| `tests/regression/electrolyte` | 2 | 1 | 1 | Delete or move to benchmarks | Current deletion matches policy; MIAC parity/regression paper checks should not be pytest. |
| `tests/regression/literature` | 1 | 1 | 1 | Delete | Current deletion matches policy; paper reproduction belongs in explicit benchmark/analysis workflows. |
| `tests/fixtures/literature` | 1 | 1 | 1 | Delete or move to analysis data | Literature fixtures should not be package pytest fixtures. |
| `tests/profile` | 3 | 2 | 2 | Move out of pytest | Profiling should be an explicit profile/benchmark command, not normal pytest collection. |
| `tests/workflows` | 4 | 3 | 4 | Keep workflow guards, remove paper/profile gates | Repo/build wrapper tests belong in pytest; paper validation does not. |
| `tests/workflows/benchmarks` | 3 | 3 | 3 | Keep only script schema smoke tests | Benchmark harness schema can be tested; benchmark acceptance belongs to benchmark commands. |
| `tests/workflows/build` | 5 | 4 | 4 | Keep | Build workflow command guards are useful, usually cheap, and diagnostic. |
| `tests/workflows/data_validation` | 1 | 1 | 1 | Delete | Data-validation papers belong under `analyses/`, not pytest. |
| `tests/workflows/paper_validation` | 1 | 1 | 1 | Delete | Current deletion matches policy. |
| `tests/workflows/repo` | 4 | 3 | 4 | Keep, split policy files | Good guardrail tests, but structure/run_pytest files are becoming policy bundles. |
| `tests/workflows/validation` | 2 | 1 | 1 | Delete or move | Equilibrium confidence validation should be trusted route ladder plus explicit analysis, not broad feed-line pytest. |

## Active File Scores

| File | R | S | N | Recommendation |
| --- | ---: | ---: | ---: | --- |
| `tests/api/equilibrium/electrolyte/test_electrolyte_lle_problem_native_ipopt.py` | 5 | 5 | 5 | Keep. Tiny public API to native Ipopt route check. |
| `tests/api/package/test_downstream_integration_smokes.py` | 4 | 3 | 4 | Keep but genericize names if it grows; do not validate downstream case studies here. |
| `tests/api/package/test_package_main.py` | 5 | 5 | 5 | Keep. Cheap package CLI/module contract. |
| `tests/api/parameters/test_parameter_dataset_contracts.py` | 5 | 5 | 5 | Keep. Dataset contract is small and generic. |
| `tests/api/parameters/test_parameter_schema.py` | 5 | 4 | 5 | Keep. |
| `tests/api/parameters/test_parameter_templates.py` | 5 | 4 | 5 | Keep; isolate built-in dataset smoke from template mechanics if it grows. |
| `tests/api/reactive/test_implicit_sensitivity.py` | 5 | 5 | 5 | Keep. |
| `tests/api/reactive/test_reaction_constant_conventions.py` | 5 | 4 | 5 | Keep; merge fixed-reaction regression test here. |
| `tests/api/reactive/test_reactive_electrolyte_bubble_results.py` | 5 | 3 | 5 | Keep; genericize Khudaida dataset fixture naming. |
| `tests/api/reactive/test_reactive_electrolyte_bubble_setup.py` | 5 | 3 | 5 | Keep; split setup validation from native request forwarding if it grows. |
| `tests/api/reactive/test_reactive_phase_equilibrium_problem_routes_native.py` | 5 | 4 | 5 | Keep. New coupled route public contract. |
| `tests/api/reactive/test_reactive_regression_diagnostics.py` | 5 | 4 | 5 | Keep. |
| `tests/api/reactive/test_reactive_regression_execution.py` | 5 | 5 | 5 | Keep. |
| `tests/api/reactive/test_reactive_regression_setup.py` | 5 | 2 | 5 | Split into objective construction, target-family mapping, and validation errors. |
| `tests/api/reactive/test_reactive_speciation_errors.py` | 5 | 4 | 5 | Keep. |
| `tests/api/reactive/test_reactive_speciation_options.py` | 5 | 2 | 5 | Split option validation, native request payload, and Ipopt dependency behavior. |
| `tests/api/reactive/test_reactive_speciation_results.py` | 5 | 3 | 5 | Keep, but split result formatting from diagnostics if more cases are added. |
| `tests/api/reactive/test_reactive_staged_workflow_contract.py` | 4 | 3 | 4 | Merge with staged route not-production contract; keep only while staged workflow is public. |
| `tests/api/reactive/test_staged_reactive_route_not_production.py` | 4 | 4 | 4 | Merge with staged workflow contract. |
| `tests/api/regression/test_regression_api_native_backends.py` | 5 | 2 | 5 | Split by target family: pure neutral, pure ion, binary, electrolyte, metadata. |
| `tests/api/regression/test_regression_api_public_contracts.py` | 5 | 4 | 5 | Keep. |
| `tests/api/regression/test_regression_api_results_and_errors.py` | 5 | 4 | 5 | Keep. |
| `tests/api/regression/test_regression_problem_schema.py` | 5 | 3 | 5 | Keep; split dataset schema from native runner payload if it grows. |
| `tests/api/runtime/test_runtime_capabilities_dependency_gates.py` | 5 | 5 | 5 | Keep. |
| `tests/api/runtime/test_runtime_exports_and_metadata.py` | 5 | 3 | 5 | Keep; split exports from metadata maps if it grows. |
| `tests/api/runtime/test_runtime_ionic_methods.py` | 5 | 4 | 5 | Keep. |
| `tests/api/runtime/test_runtime_neutral_methods.py` | 5 | 2 | 5 | Split scalar properties, contribution maps, density closure, and error behavior. |
| `tests/api/test_equilibrium_capabilities.py` | 4 | 5 | 3 | Merge into runtime capability dependency gates. |
| `tests/api/equilibrium/core/test_api.py` | 5 | 4 | 5 | Keep. |
| `tests/api/equilibrium/core/test_bubble_dew.py` | 5 | 2 | 5 | Split bubble request/result, dew request/result, and derivative policy. |
| `tests/api/equilibrium/core/test_derivative_policy.py` | 5 | 5 | 5 | Keep. |
| `tests/api/equilibrium/core/test_lle.py` | 5 | 2 | 5 | Split neutral LLE API, route request, and acceptance diagnostics. |
| `tests/api/equilibrium/core/test_native_requests.py` | 4 | 5 | 3 | Merge into route request/result files. |
| `tests/api/equilibrium/core/test_native_results.py` | 5 | 3 | 5 | Keep; split postsolve certificates from result normalization if it grows. |
| `tests/api/equilibrium/core/test_stability.py` | 5 | 3 | 5 | Keep; split neutral stability from route certificate payloads. |
| `tests/api/equilibrium/core/test_vle.py` | 5 | 3 | 5 | Keep; split flash convenience from typed problem contracts if it grows. |
| `tests/api/equilibrium/electrolyte/test_electrolyte_bubble.py` | 5 | 3 | 5 | Keep but genericize dataset fixture naming. |
| `tests/api/equilibrium/electrolyte/test_electrolyte_lle_results.py` | 5 | 3 | 5 | Keep but avoid paper-scale expected values. |
| `tests/api/equilibrium/electrolyte/test_electrolyte_lle_smokes.py` | 5 | 4 | 5 | Keep. |
| `tests/api/equilibrium/electrolyte/test_electrolyte_lle_solver_contracts.py` | 5 | 4 | 5 | Keep. |
| `tests/api/equilibrium/reactive/test_reactive_electrolyte_lle_coupled_solver.py` | 5 | 3 | 5 | Keep; split certificate contract from public result mapping if it grows. |
| `tests/api/equilibrium/reactive/test_reactive_lle.py` | 5 | 4 | 5 | Keep. |
| `tests/helpers/binary_regression_cases.py` | 5 | 5 | 5 | Keep restored. Helper fixture, not a collected test. |
| `tests/helpers/native_cases.py` | 5 | 5 | 5 | Keep restored. Active native tests import it. |
| `tests/helpers/numeric.py` | 5 | 5 | 5 | Keep restored. Active assertion helper. |
| `tests/helpers/regression_cases.py` | 5 | 5 | 5 | Keep restored. Active regression tests import it. |
| `tests/helpers/runtime_cases.py` | 5 | 5 | 5 | Keep restored. Active runtime/native tests import it. |
| `tests/native/ceres/test_ceres_binary_regression.py` | 5 | 4 | 5 | Keep. |
| `tests/native/ceres/test_ceres_liquid_electrolyte_regression.py` | 5 | 4 | 5 | Keep; ensure it stays a backend smoke, not MIAC paper validation. |
| `tests/native/ceres/test_ceres_pure_regression.py` | 5 | 4 | 5 | Keep. |
| `tests/native/contracts/test_algorithm_registry.py` | 5 | 5 | 5 | Keep. |
| `tests/native/contracts/test_association_implicit_derivative_contract.py` | 5 | 5 | 5 | Keep. |
| `tests/native/contracts/test_ceres_cppad_build_contract.py` | 5 | 5 | 5 | Keep. |
| `tests/native/contracts/test_derivative_coverage_matrix.py` | 5 | 5 | 5 | Keep. |
| `tests/native/contracts/test_equation_registry.py` | 5 | 4 | 5 | Keep. |
| `tests/native/contracts/test_equilibrium_native_contracts.py` | 5 | 5 | 5 | Keep. |
| `tests/native/contracts/test_property_derivative_backend_contract.py` | 5 | 5 | 5 | Keep. |
| `tests/native/cppad/test_cppad_activity_derivatives.py` | 5 | 5 | 5 | Keep. |
| `tests/native/cppad/test_cppad_born_ssmds_liquid_derivatives.py` | 5 | 2 | 5 | Keep derivative intent but replace `analyses.data_validation.miac_fits` dependency with a compact package fixture. |
| `tests/native/cppad/test_cppad_bubble_derivatives.py` | 5 | 5 | 5 | Keep. |
| `tests/native/cppad/test_cppad_eos_contributions.py` | 5 | 5 | 5 | Keep. |
| `tests/native/cppad/test_cppad_fugacity_derivatives.py` | 5 | 4 | 5 | Keep. |
| `tests/native/cppad/test_cppad_lle_derivatives.py` | 5 | 5 | 5 | Keep. |
| `tests/native/cppad/test_cppad_pressure_density.py` | 5 | 5 | 5 | Keep. |
| `tests/native/cppad/test_cppad_pressure_derivatives.py` | 5 | 4 | 5 | Keep. |
| `tests/native/cppad/test_cppad_relative_permittivity_derivatives.py` | 5 | 5 | 5 | Keep. |
| `tests/native/cppad/test_cppad_runtime_contract.py` | 5 | 5 | 5 | Keep. |
| `tests/native/cppad/test_cppad_scalar_smoke.py` | 5 | 5 | 5 | Keep. |
| `tests/native/cppad/test_phase_state_sensitivities.py` | 5 | 4 | 5 | Keep. |
| `tests/native/equilibrium/test_association_block.py` | 5 | 5 | 5 | Keep. |
| `tests/native/equilibrium/test_chemical_equilibrium_native_api.py` | 5 | 3 | 5 | Keep; split API success, diagnostics, and warm-start behavior if it grows. |
| `tests/native/equilibrium/test_chemical_equilibrium_native_errors.py` | 5 | 3 | 5 | Keep; split validation error families if it grows. |
| `tests/native/equilibrium/test_electrolyte_lle_residual_jacobian.py` | 5 | 5 | 5 | Keep. |
| `tests/native/equilibrium/test_electrolyte_lle_residual_surface.py` | 5 | 4 | 5 | Keep. |
| `tests/native/equilibrium/test_eos_phase_block.py` | 5 | 2 | 5 | Split EOS phase state, transfer residuals, and derivative payload. |
| `tests/native/equilibrium/test_ideal_gibbs_reaction_blocks.py` | 5 | 5 | 5 | Keep. |
| `tests/native/equilibrium/test_ipopt_adapter_contract.py` | 5 | 4 | 5 | Keep. |
| `tests/native/equilibrium/test_native_route_diagnostics_contract.py` | 5 | 5 | 5 | Keep. |
| `tests/native/equilibrium/test_reactive_phase_equilibrium_residual_jacobian.py` | 5 | 5 | 5 | Keep. |
| `tests/native/equilibrium/test_reactive_phase_equilibrium_residual_surface.py` | 5 | 4 | 5 | Keep. |
| `tests/native/equilibrium/test_result_builder.py` | 5 | 4 | 5 | Keep. |
| `tests/native/equilibrium/route_builder_cases.py` and `test_route_builders_*.py` | 5 | 4 | 5 | Keep split route-family files: neutral flash, neutral LLE, bubble/dew, stability, electrolyte, reactive two-phase, reactive LLE, and reactive electrolyte. |
| `tests/native/equilibrium/test_route_metadata_contracts.py` | 5 | 4 | 5 | Keep. |
| `tests/native/runtime/test_runtime_cache_contracts.py` | 5 | 2 | 5 | Split cache contracts from MIAC variant coverage; move MIAC analysis dependency out. |
| `tests/native/runtime/test_runtime_contribution_contracts.py` | 5 | 4 | 5 | Keep. |
| `tests/native/runtime/test_runtime_density_closure.py` | 5 | 4 | 5 | Keep. |
| `tests/regression/core/test_fixed_reaction_constant_parameter_fit.py` | 4 | 4 | 3 | Merge into `tests/api/reactive/test_reaction_constant_conventions.py`. |
| `tests/regression/core/test_hydrocarbon.py` | 5 | 5 | 5 | Keep. This is the trusted hydrocarbon regression anchor. |
| `tests/workflows/benchmarks/test_benchmark_neutral_equilibrium.py` | 4 | 4 | 4 | Keep as benchmark harness schema smoke. Do not add acceptance timing claims here. |
| `tests/workflows/benchmarks/test_benchmark_reactive_regression.py` | 4 | 3 | 4 | Keep if it stays schema/CLI focused; move semantic benchmark claims to benchmark command output. |
| `tests/workflows/build/test_build_backend.py` | 5 | 4 | 4 | Keep. |
| `tests/workflows/build/test_build_dist.py` | 5 | 5 | 4 | Keep. |
| `tests/workflows/build/test_build_epcsaft_script.py` | 5 | 5 | 4 | Keep. |
| `tests/workflows/build/test_build_epcsaft.py` | 5 | 4 | 4 | Keep. |
| `tests/workflows/build/test_build_system_ceres.py` | 5 | 5 | 4 | Keep. |
| `tests/workflows/build/test_native_runtime_env.py` | 5 | 4 | 4 | Keep. |
| `tests/workflows/repo/test_dependency_issue_triage.py` | 4 | 4 | 4 | Keep. |
| `tests/workflows/repo/test_project_structure.py` | 4 | 2 | 4 | Split into test tree policy, analysis layout policy, lexical gates, and docs/registry policy. |
| `tests/workflows/repo/test_run_pytest.py` | 5 | 3 | 5 | Keep; split slice registry behavior from broad-target guards if it grows. |
| `tests/workflows/repo/test_workflow_entrypoints.py` | 4 | 4 | 4 | Keep. |

## Deleted Or Staged-Deleted File Scores

| File or group | R | S | N | Recommendation |
| --- | ---: | ---: | ---: | --- |
| `tests/**/__init__.py` | 1 | 5 | 1 | Delete. Test folders do not need package sentinels. |
| `tests/api/equilibrium/electrolyte/test_hubach_electrolyte_lle.py` | 2 | 1 | 1 | Delete or move to explicit paper/analysis validation. |
| `tests/fixtures/literature/**` | 1 | 1 | 1 | Delete from pytest; move only necessary source-backed data to `analyses/` or `data/reference/`. |
| `tests/profile/test_miac_profile.py` | 3 | 2 | 2 | Move to explicit profile command or benchmark self-check. |
| `tests/profile/test_regression_profile.py` | 3 | 2 | 2 | Move to explicit profile command or benchmark self-check. |
| `tests/profile/test_runtime_profile.py` | 3 | 2 | 2 | Move to explicit profile command or benchmark self-check. |
| `tests/regression/electrolyte/test_miac_liquid_electrolyte_parity.py` | 2 | 1 | 1 | Delete or move to explicit MIAC benchmark/analysis. |
| `tests/regression/electrolyte/test_miac_liquid_electrolyte_regression.py` | 2 | 1 | 1 | Delete or move to explicit MIAC benchmark/analysis. |
| `tests/regression/literature/**` | 1 | 1 | 1 | Delete. Paper reproduction is not pytest. |
| `tests/workflows/benchmarks/test_benchmark_literature_suite.py` | 2 | 2 | 2 | Move to benchmark script self-check or keep only a minimal registry schema test outside normal slices. |
| `tests/workflows/data_validation/test_mea_co2_pressure_speciation.py` | 1 | 1 | 1 | Delete from pytest; keep as explicit analysis/data-validation command. |
| `tests/workflows/paper_validation/**` | 1 | 1 | 1 | Delete. Current deletion matches policy. |
| `tests/workflows/validation/equilibrium_core/**` | 2 | 1 | 1 | Delete or move to explicit analysis; pytest should use the trusted route ladder. |

## Priority Cleanup Order

1. Keep restored `tests/helpers/*.py`, while keeping all `tests/**/__init__.py` deleted.
2. Done: split `tests/native/equilibrium/test_route_builders.py` into route-family files before adding more equilibrium route cases.
3. Done: removed pytest dependencies on `analyses.data_validation.miac_fits` and replaced them with compact package fixtures.
4. Done: split the largest API files: reactive speciation options, reactive regression setup, regression native backends, runtime neutral methods.
5. Deferred: split `tests/workflows/repo/test_project_structure.py` into smaller policy files in a later cleanup slice; current guards still pass.
6. Done: removed pytest profile slices and routed performance evidence through explicit benchmark commands/docs.
7. Kept broad `run_pytest.py --all` out of this cleanup loop; validation used targeted changed-file and single-node checks only.

## Validation Notes

- `uv run python run_pytest.py tests/workflows/repo/test_run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_workflow_entrypoints.py -q`
- `uv run python run_pytest.py tests/api/runtime/test_runtime_capabilities_dependency_gates.py tests/api/runtime/test_runtime_neutral_scalar_methods.py tests/api/runtime/test_runtime_neutral_contribution_methods.py tests/api/runtime/test_runtime_neutral_density_closure.py tests/api/regression/test_regression_api_pure_neutral_backend.py tests/api/regression/test_regression_api_pure_ion_backend.py tests/api/regression/test_regression_api_binary_backend.py -q`
- `uv run python run_pytest.py tests/api/reactive/test_reactive_speciation_reaction_definition.py tests/api/reactive/test_reactive_speciation_option_validation.py tests/api/reactive/test_reactive_speciation_native_requests.py tests/api/reactive/test_reactive_regression_surfaces.py tests/api/reactive/test_reactive_regression_context.py tests/api/reactive/test_reactive_regression_objective.py tests/api/reactive/test_reaction_constant_conventions.py -q`
- `uv run python run_pytest.py tests/api/equilibrium/core/test_vle.py::test_tp_flash_builds_one_native_route_request_before_ipopt_gate tests/api/equilibrium/core/test_lle.py::test_lle_flash_builds_one_native_route_request_before_ipopt_gate tests/api/equilibrium/core/test_stability.py::test_stability_uses_native_ipopt_route_after_validation tests/api/equilibrium/electrolyte/test_electrolyte_lle_smokes.py::test_electrolyte_lle_builds_native_route_before_ipopt_gate tests/api/equilibrium/electrolyte/test_electrolyte_lle_results.py::test_electrolyte_stability_builds_native_route_request_before_ipopt_gate tests/api/equilibrium/reactive/test_reactive_electrolyte_lle_coupled_solver.py::test_reactive_electrolyte_lle_public_route_certifies_accepted_native_split -q`
- `uv run python run_pytest.py tests/native/cppad/test_cppad_born_ssmds_liquid_derivatives.py tests/native/runtime/test_runtime_cache_contracts.py -q`
- `uv run python run_pytest.py tests/native/equilibrium/test_route_builders_neutral_bubble_dew.py::test_neutral_bubble_pressure_workbook_accepted_point_runs_postsolve tests/native/equilibrium/test_route_builders_neutral_bubble_dew.py::test_neutral_fixed_temperature_pressure_route_uses_exact_hessian_when_requested tests/native/equilibrium/test_route_builders_stability.py::test_reactive_stability_tpd_contract_uses_existing_stability_shape tests/native/equilibrium/test_route_builders_reactive_lle.py::test_reactive_lle_eos_route_builder_owns_canonical_initial_point tests/native/equilibrium/test_route_builders_reactive_electrolyte.py::test_reactive_electrolyte_lle_eos_route_builder_uses_liquid_root_residual_route -q`
- `uv run python run_pytest.py --list-slices`
- `uv run python scripts/docs/sync_algorithm_registry.py --check --strict-traceability`

The attempted whole `tests/api/equilibrium` folder run was stopped after timing out. It was intentionally replaced with the route-gate nodes above so pytest remains diagnostic instead of becoming a broad equilibrium sweep.

## Helper Resolution

`tests/helpers/*.py` are imported by active tests and have been restored. The active policy is:

- Delete `tests/helpers/__init__.py`.
- Keep `tests/helpers/binary_regression_cases.py`.
- Keep `tests/helpers/native_cases.py`.
- Keep `tests/helpers/numeric.py`.
- Keep `tests/helpers/regression_cases.py`.
- Keep `tests/helpers/runtime_cases.py`.
