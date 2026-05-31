# Score and Harden Provider EOS Properties Structure

- Issue title: Score and harden provider EOS properties source structure
- Milestone: `M3 - EOS`
- Package scope: `epcsaft` provider/core only

## Problem

The provider EOS properties folder is cleaner after the Born and source-structure
cleanup work, but several source files still concentrate multiple ownership
concepts. This makes the EOS harness harder to navigate and increases the risk
that future derivative or property work adds one-off helper logic instead of
deepening the relevant provider module.

This issue records a complete file/function scorecard for
`packages/epcsaft/src/epcsaft/native/eos/properties` and uses the scorecard to
prioritize keep/move/split/merge/delete recommendations. It is an M3 provider
structure task only; it must not change public EOS behavior.

## Intended Outcome

The provider EOS properties folder has a durable scorecard for every file and
top-level function/declaration, plus prioritized cleanup recommendations that
future implementation agents can execute without re-litigating scope.

## Scoring Model

Scores are 1-5 health scores.

| Score | Meaning |
| --- | --- |
| `5` | Canonical, focused, and should stay as-is. |
| `4` | Relevant and needed; only minor locality or naming cleanup may be useful. |
| `3` | Needed, but placement or scope should be revisited. |
| `2` | Relevant but overloaded, too specific, or poorly localized; split/move recommended. |
| `1` | Likely redundant, dead, or badly placed enough that deletion or replacement should be considered. |

Each score considers provider-EOS relevance, whether the code is still needed,
placement under `eos/properties`, generality versus one-off logic, and
organization/readability.

Action values:

- `keep`: retain the file/function where it is.
- `move`: relocate to a better owning file/header without behavior change.
- `split`: divide the current function/file by ownership.
- `merge`: fold shallow helpers into the owning implementation.
- `delete`: remove only if implementation proves it is dead or redundant.

## File Scorecard

| File | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `activity.cpp` | 2 | split | Needed for provider activity coefficients, but it mixes MIAC gamma construction, solvation free energy, solvent selection, osmotic coefficient, metadata shaping, and public dispatch in one source. |
| `chemical_potential.cpp` | 4 | keep | Focused conversion from residual Helmholtz composition derivatives into residual chemical potentials. Small contribution helpers are acceptable. |
| `compressibility.cpp` | 4 | keep | Focused compressibility/pressure ownership with CppAD density derivative entrypoint. Some helper declarations may not need the shared hub. |
| `density.cpp` | 2 | split | Needed density closure path, but root scanning, bracket refinement, candidate diagnostics, seed solving, Brent fallback, and public solve reporting are all concentrated together. |
| `fugacity.cpp` | 4 | keep | Focused fugacity coefficient assembly from residual chemical potentials and compressibility corrections. |
| `pure_neutral_parameter_derivatives.cpp` | 3 | keep | Needed provider CppAD pure-neutral parameter path, but hyper-specific enough that future pure-parameter derivative families should share a clearer parameter-derivative owner. |
| `residual_association_sensitivities.cpp` | 4 | keep | Focused CppAD association implicit sensitivity implementation used by residual derivative routes. |
| `residual_association_sensitivities.h` | 4 | keep | Small internal declaration header with clear association sensitivity ownership. |
| `residual_backend_helpers.h` | 3 | move | Needed backend-label helpers, but not all helpers are residual-specific and the header may be better owned by derivative metadata or capability evidence support. |
| `residual_helmholtz.cpp` | 4 | keep | Focused public residual Helmholtz contribution entrypoints after #202. |
| `residual_helmholtz_internal.h` | 2 | split | Needed scalar/CpAD residual substrate, but mixes scalar state structs, CppAD tensor helpers, pure contribution kernels, ion/Born parameter routing, and association implicit terms in one large internal header. |
| `residual_parameter_phase_derivatives.cpp` | 2 | split | Needed CppAD parameter phase derivatives, but neutral binary, association, generic component, Born, dielectric, and pure-parameter routing are concentrated in long functions. |
| `residual_phase_derivatives.cpp` | 2 | split | Needed phase-state and phase-objective derivative path, but objective derivatives, temperature-variable derivatives, ln fugacity sensitivity, pressure derivatives, and association corrections are mixed in one large source. |
| `residual_properties.cpp` | 5 | keep | Minimal residual property wrappers for `hres`, `gres`, and `sres`; focused and easy to audit. |
| `residual_property_derivatives.cpp` | 4 | keep | Focused residual density, temperature, and composition derivative entrypoints. |

## Function Scorecard

### `activity.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `build_infinite_dilution_reference_cpp` | 3 | move | Needed for MIAC reference-state setup, but belongs with reference-state helpers rather than the full activity dispatch file. |
| `reference_state_from_cache_or_build_cpp` | 3 | move | Needed cache adapter, but reference-state cache ownership should be separated from coefficient assembly. |
| `miac_gamma_vector_cpp` | 3 | split | Needed MIAC gamma path; should sit in an MIAC-focused module with its reference-state helpers. |
| `gsolv_values_cpp` | 3 | move | Needed auxiliary solvation values, but it is not the same responsibility as pair activity/osmotic assembly. |
| `resolve_solvent_index_cpp` | 3 | move | Needed input-resolution helper; should live near solvent/charge-group input normalization. |
| `normalize_mw_cpp` | 3 | merge | Small helper; keep only if reused after activity split, otherwise fold into solvent mass-basis logic. |
| `solvent_pool_mix_mw_cpp` | 3 | move | Needed solvent-pool molecular-weight helper; belongs with solvent basis logic. |
| `validate_activity_inputs_cpp` | 4 | keep | Useful validation guard for activity coefficient input topology. |
| `assign_activity_metadata_cpp` | 3 | split | Needed payload shaping, but metadata assignment should be separate from thermodynamic coefficient calculation. |
| `assign_activity_aux_cpp` | 3 | split | Needed optional auxiliary payload, but auxiliary shaping should not make the core activity source hard to scan. |
| `assign_pair_activity_cpp` | 3 | split | Needed mean ionic/pair coefficient assembly; belongs in a pair-activity focused section or source. |
| `osmotic_coefficient_cpp` | 3 | move | Needed electrolyte activity output, but osmotic coefficient logic is distinct from MIAC and metadata assignment. |
| `activity_coefficient_values_impl_cpp` | 2 | split | Central dispatcher is needed, but it currently coordinates too many distinct responsibilities. |
| `activity_coefficient_values_cpp` | 4 | keep | Public provider entrypoint should remain stable and delegate to focused internal modules. |

### `chemical_potential.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `mu_contribution_cpp` | 4 | keep | Canonical contribution-to-chemical-potential transformation. |
| `mu_hc_cpp` | 4 | merge | Thin named helper is readable; can stay or be merged if contribution mapping is table-driven later. |
| `mu_disp_cpp` | 4 | merge | Thin named helper is readable; can stay or be merged if contribution mapping is table-driven later. |
| `mu_assoc_cpp` | 4 | merge | Thin named helper is readable; can stay or be merged if contribution mapping is table-driven later. |
| `mu_ion_cpp` | 4 | merge | Thin named helper is readable; can stay or be merged if contribution mapping is table-driven later. |
| `mu_born_cpp` | 4 | merge | Thin named helper is readable; can stay or be merged if contribution mapping is table-driven later. |
| `mu_total_cpp` | 4 | keep | Focused vector summation for residual chemical potential payloads. |
| `residual_chemical_potential_result_cpp` | 5 | keep | Main result entrypoint; needed by state, fugacity, and derivative routes. |
| `mures_cpp` | 5 | keep | Public native scalar-vector convenience entrypoint. |

### `compressibility.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `z_term_scale_cpp` | 4 | keep | Needed correction scale shared with fugacity; placement is acceptable but shared declaration should be intentional. |
| `normalized_dadrho_scale_cpp` | 4 | keep | Focused helper for contribution-normalized density derivative terms. |
| `normalized_dadrho_term_cpp` | 4 | keep | Small focused helper. |
| `z_total_cpp` | 4 | keep | Small focused compressibility formula helper. |
| `normalized_dadrho_terms_cpp` | 4 | keep | Needed by residual derivative and compressibility assembly. |
| `compressibility_terms_from_dadrho_cpp` | 4 | keep | Focused conversion from derivative result to compressibility contribution terms. |
| `compressibility_factor_result_cpp` | 5 | keep | Main result entrypoint for contribution-aware compressibility factor. |
| `Z_cpp` | 5 | keep | Public native compressibility convenience entrypoint. |
| `p_cpp` | 5 | keep | Public native pressure entrypoint used by density and activity paths. |
| `cppad_pressure_density_derivative_cpp` | 4 | keep | Needed CppAD-backed pressure-density derivative entrypoint. |

### `density.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `density_scan_grid_cpp` | 3 | move | Needed scan policy, but should be private to density scanning instead of shared declaration hub unless reused externally. |
| `density_scan_point_cpp` | 3 | move | Needed scan helper; should be local to density scanning/reporting. |
| `density_failure_message_cpp` | 3 | move | Needed diagnostics helper, but diagnostic formatting should be separate from root solving. |
| `density_brackets_cpp` | 3 | move | Needed bracketing helper; belongs in density scan/bracket owner. |
| `refine_density_brackets_cpp` | 3 | move | Needed refinement helper; belongs with bracketing and should not be globally declared unless reused. |
| `density_root_valid_cpp` | 3 | move | Needed candidate validator; belongs with candidate diagnostics/selection. |
| `density_root_from_seed_cpp` | 2 | split | Needed seed solve path, but long and mixes iteration, validation, and output selection. |
| `density_near_root_candidate_cpp` | 3 | move | Needed near-root candidate builder; should be private density implementation detail. |
| `density_candidate_diagnostics_cpp` | 3 | move | Needed diagnostics adapter; should live near reporting. |
| `density_solve_report_cpp` | 2 | split | Needed public solve report, but long orchestration function should delegate to scan, seed, candidate, and diagnostics modules. |
| `den_cpp` | 2 | split | Needed public density entrypoint, but currently duplicates/coordinates solve reporting responsibilities. |
| `reduced_density_to_molar` | 4 | keep | Clear conversion helper and provider-owned EOS utility. |
| `density_brent_cpp` | 2 | move | Needed scalar root algorithm today, but generic algorithmic code should be isolated from density policy. |
| `density_root_residual_cpp` | 4 | keep | Clear pressure residual helper for density solving. |

### `fugacity.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `exp_vector` | 4 | keep | Small local conversion helper. |
| `stable_logz_over_zminus1` | 4 | keep | Focused numerical helper for stable fugacity correction. |
| `lnfug_correction_scale_cpp` | 4 | keep | Focused compressibility correction helper. |
| `lnfug_contribution_cpp` | 4 | keep | Canonical contribution-level fugacity transformation. |
| `lnfug_hc_cpp` | 4 | merge | Thin contribution helper; acceptable, could merge into table-driven assembly later. |
| `lnfug_disp_cpp` | 4 | merge | Thin contribution helper; acceptable, could merge into table-driven assembly later. |
| `lnfug_assoc_cpp` | 4 | merge | Thin contribution helper; acceptable, could merge into table-driven assembly later. |
| `lnfug_ion_cpp` | 4 | merge | Thin contribution helper; acceptable, could merge into table-driven assembly later. |
| `lnfug_born_cpp` | 4 | merge | Thin contribution helper; acceptable, could merge into table-driven assembly later. |
| `lnfug_total_cpp` | 4 | keep | Focused vector summation for fugacity payload. |
| `fugacity_coefficient_result_cpp` | 5 | keep | Main contribution-aware fugacity coefficient result entrypoint. |
| `lnfug_cpp` | 5 | keep | Public native log-fugacity convenience entrypoint. |
| `fugcoef_cpp` | 5 | keep | Public native fugacity coefficient convenience entrypoint. |

### `pure_neutral_parameter_derivatives.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `validate_pure_neutral_parameter_args` | 4 | keep | Needed loud validation for pure neutral derivative route. |
| `pure_neutral_state_scalar_cpp` | 3 | move | Needed scalar tape model, but should be considered for a broader pure-parameter derivative kernel if more pure families are added. |
| `cppad_pure_neutral_parameter_derivatives_cpp` | 4 | keep | Public native CppAD provider derivative entrypoint for pure neutral parameters. |

### `residual_association_sensitivities.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `association_density_response_cppad_cpp` | 4 | keep | Focused association implicit density sensitivity path. |
| `association_phase_state_response_cppad_cpp` | 4 | keep | Focused association implicit phase-state sensitivity path. |

### `residual_association_sensitivities.h`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `association_density_response_cppad_cpp` | 4 | keep | Internal declaration needed by parameter derivative route. |
| `association_phase_state_response_cppad_cpp` | 4 | keep | Internal declaration needed by phase derivative route. |

### `residual_backend_helpers.h`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `contribution_backend_name` | 3 | move | Needed label mapping, but backend naming could be centralized with derivative metadata. |
| `has_association_sites` | 4 | keep | Small topology helper with real reuse across derivative routes. |
| `association_backend_name` | 3 | move | Needed label helper, but capability/backend metadata ownership should be explicit. |
| `born_backend_name` | 3 | move | Needed label helper, but capability/backend metadata ownership should be explicit. |
| `composition_derivative_backend_map` | 3 | move | Needed public evidence mapping, but likely belongs with derivative result metadata. |

### `residual_helmholtz.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `ares_contribution_value_cpp` | 4 | keep | Small contribution selector used by shared interfaces. |
| `ares_contributions_cpp` | 5 | keep | Canonical residual Helmholtz contribution-family assembly entrypoint. |
| `residual_helmholtz_result_cpp` | 5 | keep | Main scalar contribution result entrypoint. |
| `ares_cpp` | 5 | keep | Public native residual Helmholtz convenience entrypoint. |
| `cppad_eos_contribution_derivatives_cpp` | 4 | keep | Needed CppAD contribution derivative entrypoint; placement is acceptable because it tapes contribution-family outputs. |

### `residual_helmholtz_internal.h`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `vector_output_component_hessian_cppad` | 3 | move | Useful CppAD tensor helper; should be in a derivative utility header if reused outside residual kernels. |
| `scalar_function_third_derivative_tensor_cppad` | 3 | move | Useful high-order CppAD helper; should be in a derivative utility header or phase derivative owner. |
| `scalar_component_parameter_cpp` | 3 | move | Needed parameter override helper; belongs with component-parameter derivative routing. |
| `scalar_dielc_parameter_cpp` | 3 | move | Needed dielectric parameter override helper; belongs with dielectric/parameter routing. |
| `ion_diameter_scalar_cpp` | 3 | move | Needed scalar ion diameter route; should sit with ion contribution scalar kernel. |
| `ion_born_radius_scalar_cpp` | 3 | move | Needed scalar Born radius route; should sit with Born contribution scalar kernel. |
| `mixture_state_scalar_cpp` | 3 | split | Needed scalar mixture-state builder, but as a central dependency it should be in a focused scalar-state header. |
| `hs_contact_value_scalar_cpp` | 4 | keep | Small hard-chain contact helper; current use is acceptable but a hard-chain scalar header may be cleaner. |
| `hard_chain_state_scalar_cpp` | 3 | move | Needed scalar hard-chain state builder; should sit with hard-chain scalar contribution ownership. |
| `dispersion_polynomials_scalar_cpp` | 3 | move | Needed scalar dispersion state builder; should sit with dispersion scalar contribution ownership. |
| `ares_hs_scalar_cpp` | 3 | move | Needed hard-sphere scalar contribution; should sit with hard-chain scalar contribution ownership. |
| `ares_hc_scalar_cpp` | 3 | move | Needed hard-chain scalar contribution; should sit with hard-chain scalar contribution ownership. |
| `ares_disp_scalar_cpp` | 3 | move | Needed dispersion scalar contribution; should sit with dispersion scalar contribution ownership. |
| `ares_hc_cpp` | 4 | keep | Lightweight double wrapper for hard-chain contribution assembly. |
| `ares_disp_cpp` | 4 | keep | Lightweight double wrapper for dispersion contribution assembly. |
| `ares_assoc_scalar_cpp` | 3 | move | Needed association scalar contribution; should sit with association scalar contribution ownership. |
| `ares_assoc_cpp` | 4 | keep | Lightweight double wrapper for association contribution assembly. |
| `hs_contact_density_derivative_scalar_cpp` | 3 | move | Needed association derivative helper; should sit with association implicit sensitivity helpers. |
| `hs_contact_composition_derivative_scalar_cpp` | 3 | move | Needed association derivative helper; should sit with association implicit sensitivity helpers. |
| `association_volume_scalar_cpp` | 3 | move | Needed association parameter helper; should sit with association scalar kernel and parameter routing. |
| `solve_linear_system_scalar_cpp` | 3 | move | Needed scalar linear solve helper; should be isolated as numerical substrate instead of residual contribution logic. |
| `association_site_fraction_density_terms_scalar_cpp` | 3 | move | Needed association implicit density terms; should sit with association sensitivities. |
| `association_site_fraction_composition_terms_scalar_cpp` | 3 | move | Needed association implicit composition terms; should sit with association sensitivities. |
| `association_implicit_terms_scalar_cpp` | 2 | split | Needed, but long and central; should be split into association delta construction, density terms, and composition terms. |
| `ares_ion_scalar_cpp` | 3 | move | Needed ionic scalar contribution; should sit in an ionic scalar contribution owner. |
| `ares_ion_cpp` | 4 | keep | Lightweight double wrapper for ionic contribution assembly. |
| `ares_born_scalar_cpp` | 2 | split | Needed Born scalar contribution, but long and mixes Born model selection, SSM/DS geometry, dielectric routing, and parameter override behavior. |
| `ares_born_cpp` | 4 | keep | Lightweight double wrapper for Born contribution assembly. |
| `ares_contributions_scalar_cpp` | 3 | split | Needed aggregate scalar contribution assembly, but should depend on focused scalar contribution modules rather than owning every family. |

### `residual_parameter_phase_derivatives.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `association_parameter_phase_derivatives_cpp` | 2 | split | Needed association parameter phase derivative path, but too long and mixes explicit CppAD tape setup, implicit association corrections, pressure chain rule, fugacity, and derivative payload assembly. |
| `neutral_binary_kij_phase_derivatives_cpp` | 4 | keep | Thin compatibility/native convenience route for `k_ij`; acceptable if it delegates to the pair-parameter route. |
| `neutral_binary_pair_parameter_phase_derivatives_cpp` | 2 | split | Needed binary parameter phase derivative path, but it combines binary validation, association special-casing, CppAD tape construction, and payload assembly. |
| `generic_component_parameter_phase_derivatives_cpp` | 2 | split | Needed generic component-parameter path for Born/dielectric/pure component parameters, but it combines target validation, CppAD tape construction, association corrections, and phase payload assembly. |

### `residual_phase_derivatives.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `eos_phase_objective_derivatives_cpp` | 3 | split | Needed phase objective derivative entrypoint; should delegate high-order CppAD tape mechanics to a focused objective derivative helper. |
| `eos_phase_temperature_variable_derivatives_cpp` | 3 | split | Needed temperature-variable objective derivative entrypoint; should share more structure with the fixed-temperature objective route. |
| `phase_state_ln_fugacity_density_sensitivity_cpp` | 2 | split | Needed core sensitivity path, but very long and mixes CppAD setup, residual derivative math, fugacity chain rule, pressure-root chain rule, and association correction logic. |
| `phase_state_ln_fugacity_explicit_density_composition_sensitivity_cpp` | 4 | keep | Thin explicit-density wrapper; acceptable if the core sensitivity path is split. |
| `phase_state_ln_fugacity_composition_sensitivity_cpp` | 4 | keep | Thin pressure-closed wrapper; acceptable if the core sensitivity path is split. |
| `eos_phase_pressure_derivatives_cpp` | 3 | split | Needed pressure derivative result, but should delegate tape setup and result validation to focused helpers. |
| `eos_phase_association_derivative_corrections_cpp` | 3 | move | Needed association correction path; belongs with association sensitivity ownership rather than general phase derivatives. |

### `residual_properties.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `hres_cpp` | 5 | keep | Minimal residual enthalpy wrapper; focused and needed. |
| `gres_cpp` | 5 | keep | Minimal residual Gibbs wrapper; focused and needed. |
| `sres_cpp` | 5 | keep | Minimal residual entropy wrapper; focused and needed. |

### `residual_property_derivatives.cpp`

| Function | Score | Action | Rationale |
| --- | ---: | --- | --- |
| `dadrho_result_cpp` | 4 | keep | Focused density derivative entrypoint. |
| `temperature_derivative_residual_helmholtz_result_cpp` | 4 | keep | Focused temperature derivative entrypoint. |
| `dadt_cpp` | 5 | keep | Public native residual temperature derivative convenience entrypoint. |
| `composition_derivative_residual_helmholtz_result_cpp` | 4 | keep | Focused composition derivative entrypoint used by chemical potential and state paths. |

## Recommended Cleanup Order

1. Keep stable files as-is unless a nearby implementation change needs them:
   `residual_properties.cpp`, `chemical_potential.cpp`, `compressibility.cpp`,
   `fugacity.cpp`, `residual_helmholtz.cpp`, and
   `residual_property_derivatives.cpp`.
2. Split `residual_helmholtz_internal.h` into named scalar kernel owners:
   scalar state, CppAD tensor helpers, hard-chain/dispersion, association,
   ionic, Born, and aggregate contribution assembly.
3. Split `residual_phase_derivatives.cpp` by objective derivatives,
   phase-state fugacity sensitivity, pressure derivatives, and association
   correction ownership.
4. Split `residual_parameter_phase_derivatives.cpp` by association parameter,
   binary pair parameter, and generic component parameter derivative ownership.
5. Split `density.cpp` into scan/bracket, root solve, diagnostics/reporting,
   and public density entrypoint ownership. Remove shared declarations for
   helpers that become private.
6. Split `activity.cpp` only where it improves locality: MIAC/reference-state,
   gsolv auxiliary values, pair activity/osmotic coefficient, metadata shaping,
   and public dispatch.
7. Revisit `residual_backend_helpers.h` once derivative metadata ownership is
   clearer; move backend label helpers to that owner if it exists.

## Acceptance Criteria

- [x] The durable plan scores every file and top-level function/declaration
  under `packages/epcsaft/src/epcsaft/native/eos/properties`.
- [x] Each score includes relevance, need, placement, generality, and
  organization rationale.
- [x] Each low-scoring item has an explicit `keep`, `move`, `split`, `merge`,
  or `delete` recommendation.
- [x] The plan identifies safe M3 provider cleanup recommendations and
  follow-up candidates.
- [x] No public API names, derivative payloads, capability contracts, or
  equation semantics change.

## Non-Goals

- No equilibrium or regression package work.
- No public API redesign.
- No equation theory changes.
- No new tests beyond existing focused proof commands unless implementation
  changes demand them.

## Proof Oracle

```powershell
uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10
uv run python run_pytest.py packages/epcsaft/tests/native/state/test_contributions.py packages/epcsaft/tests/native/state/test_eos_contributions.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py -q
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/build/test_build_epcsaft.py -q
uv run python scripts/dev/validate_project.py quick
```

If EqID/source trace comments move, also run:

```powershell
uv run python scripts/docs/sync_equation_registry.py --check --strict-traceability
uv run python run_pytest.py tests/native/contracts/test_equation_registry.py -q
```

Use the full native build command instead of `--build-only` when `build/dev` is
not already configured.

## Issue Handoff

```json grill_plan_to_issue_handoff
{
  "slug": "score-provider-eos-properties-structure",
  "target_repo": "ePC-SAFT/ePC-SAFT",
  "target_repo_root": "C:\\Users\\Tanner\\Documents\\Workspaces\\Engineering\\ePC-SAFT",
  "source_repo": "ePC-SAFT/ePC-SAFT",
  "issue_source_policy": "local-main-sync",
  "title": "Score and harden provider EOS properties source structure",
  "outcome": "The provider EOS properties folder has a complete file/function scorecard and prioritized keep/move/split/delete recommendations for structure cleanup, with public EOS behavior unchanged.",
  "issue_policy": "create",
  "milestone_policy": "hard",
  "milestone_title": "M3 - EOS",
  "full_roadmap": "docs/milestones/PROJECT_CONTEXT.md",
  "full_roadmap_milestone_section": "Required milestones",
  "project_policy": "dashboard-only",
  "plan_file": "docs/milestones/M3-eos/plans/score-provider-eos-properties-structure.md",
  "required_checks_policy": "allow-none-with-local-proof",
  "labels": ["type:task", "status:ready", "agent-ready", "area:core", "area:derivatives", "native", "validation"],
  "acceptance_criteria": [
    "The durable plan scores every file and top-level function/declaration under packages/epcsaft/src/epcsaft/native/eos/properties.",
    "Each score includes relevance, need, placement, generality, and organization rationale.",
    "Each low-scoring item has an explicit keep/move/split/merge/delete recommendation.",
    "The plan identifies which recommendations are safe M3 provider cleanup and which require follow-up issues.",
    "No public API names, derivative payloads, capability contracts, or equation semantics change."
  ],
  "non_goals": [
    "No equilibrium or regression package work.",
    "No public API redesign.",
    "No equation theory changes.",
    "No new tests beyond existing focused proof commands unless implementation changes demand them."
  ],
  "proof_oracle": [
    "uv run python scripts/dev/build_epcsaft.py --build-only --parallel 10",
    "uv run python run_pytest.py packages/epcsaft/tests/native/state/test_contributions.py packages/epcsaft/tests/native/state/test_eos_contributions.py packages/epcsaft/tests/native/state/test_phase_state_sensitivities.py packages/epcsaft/tests/native/state/test_born_parameter_derivatives.py -q",
    "uv run python run_pytest.py tests/workflows/repo/test_project_structure.py tests/workflows/repo/test_package_extension_boundary.py tests/workflows/build/test_build_epcsaft.py -q",
    "uv run python scripts/dev/validate_project.py quick"
  ],
  "candidate_allowed_files": [
    "packages/epcsaft/src/epcsaft/native/eos/properties/**",
    "packages/epcsaft/src/epcsaft/native/eos/core_internal.h",
    "CMakeLists.txt",
    "packages/epcsaft/CMakeLists.txt",
    "packages/epcsaft/src/epcsaft/native_sdk/provider_native_sdk_v1/**",
    "tests/workflows/repo/test_project_structure.py",
    "tests/workflows/repo/test_package_extension_boundary.py",
    "tests/workflows/build/test_build_epcsaft.py"
  ],
  "issue_count_policy": "single-issue",
  "decomposition_policy": "single-issue",
  "issue_set": [],
  "execution_boundary": {
    "skill_scope": "issue-and-plan-publication-only",
    "approval_meaning": "publish-issue-and-plan-only",
    "implementation_skill": "issue-goal-execute-merge",
    "allowed_after_approval": ["repo-qualified GitHub issue create/update", "durable plan file writes", "default-branch commit/push for plan docs only"],
    "forbidden_after_approval": ["implementation branch creation", "implementation edits", "implementation commits", "implementation pushes", "PR creation", "merge", "GoalBuddy board", "native goal activation"]
  },
  "doc_grill_evidence": {
    "docs_read": ["CONTEXT.md", "docs/agents/issue-tracker.md", "docs/milestones/PROJECT_CONTEXT.md", "docs/milestones/M3-eos/README.md", "docs/adr/0002-hard-public-api-reset-cppad-only-frontend.md", "docs/adr/0005-package-extension-split.md"],
    "constraints_found": ["M3 owns provider EOS/state/parameters, native SDK contract, exact derivatives, CppAD/implicit sensitivities, and provider-only capability claims.", "ADR 0005 keeps provider EOS and CppAD derivative support in packages/epcsaft.", "ADR 0002 requires public derivative workflows to remain CppAD-backed without fallback/backend-mode surfaces."],
    "contradictions_found": ["The properties folder is structurally cleaner after #202, but residual_helmholtz_internal.h and derivative-heavy sources still concentrate several ownership concepts."],
    "questions_derived": ["Whether to create one issue or an issue set.", "How exhaustive the scoring should be.", "Whether low scores should force cleanup or produce recommendations."]
  },
  "decision_log": [
    {"decision": "Issue count", "status": "locked", "source": "user", "question_id": "issue_count_policy"},
    {"decision": "Scoring granularity", "status": "locked", "source": "user", "question_id": "scoring_granularity"},
    {"decision": "Action policy", "status": "locked", "source": "user", "question_id": "action_policy"},
    {"decision": "Milestone", "status": "discoverable", "source": "docs", "no_question_needed_reason": "The requested folder is provider EOS code and PROJECT_CONTEXT assigns this to M3 - EOS."},
    {"decision": "Package boundary", "status": "discoverable", "source": "docs", "no_question_needed_reason": "Issue tracker docs and ADR 0005 keep this provider-only under packages/epcsaft."}
  ],
  "question_log": [
    {"id": "issue_count_policy", "decision": "Issue count", "tool": "request_user_input", "question": "Should this become one M3 issue or a split issue set?", "answer": "One M3 Issue (Recommended)", "source": "user"},
    {"id": "scoring_granularity", "decision": "Scoring granularity", "tool": "request_user_input", "question": "How exhaustive should the scoring be?", "answer": "Top-Level Functions (Recommended)", "source": "user"},
    {"id": "action_policy", "decision": "Action policy", "tool": "request_user_input", "question": "What should low scores require in the issue?", "answer": "Recommend Actions (Recommended)", "source": "user"}
  ],
  "unresolved_decisions": [],
  "skills_used": [
    {"skill": "grill-plan-to-issue", "why": "User explicitly requested GitHub-backed issue planning.", "evidence": "Repo gate passed and the handoff includes issue policy, milestone, plan file, acceptance criteria, proof oracle, and execution boundary."},
    {"skill": "grill-with-docs", "why": "Required for repo-backed planning against glossary, roadmap, tracker, and ADRs.", "evidence": "CONTEXT, PROJECT_CONTEXT, issue tracker docs, ADR 0002, and ADR 0005 shaped scope."},
    {"skill": "improve-codebase-architecture", "why": "The request scores module depth, placement, and organization.", "evidence": "The plan uses module depth/locality and keep/move/split/delete recommendations."},
    {"skill": "chemical-engineer", "why": "The scoring touches EOS contribution and derivative ownership.", "evidence": "The plan protects residual Helmholtz, CppAD derivative, and provider capability semantics."},
    {"skill": "superpowers:brainstorming", "why": "The cleanup policy needed user choices before issue publication.", "evidence": "Questions locked issue count, scoring granularity, and action policy."}
  ]
}
```
