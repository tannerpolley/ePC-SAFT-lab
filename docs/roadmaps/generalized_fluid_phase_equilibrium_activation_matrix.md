# Generalized Fluid-Phase Equilibrium Activation Matrix

## Purpose

This document is the row-by-row activation companion to
`docs/roadmaps/generalized_fluid_phase_equilibrium_algorithm.md`. The
algorithm doctrine defines the mathematical form. This matrix defines the
admission rows, proof examples, sequencing gates, and documentation checks that
keep implementation from silently broadening into unsupported phase, chemical,
associating, electrolyte, or reactive routes.

The generalized matrices are not route menus. They are activation records for
three problem families:

- phase-only equilibrium (`PE-*`);
- chemical-only equilibrium (`CE-*`);
- combined phase-chemical equilibrium (`CPE-*`).

Bubble and dew pressure/temperature routes are derived utility routes. They
remain implemented and tested through the existing selector/core route surface,
but the generic `bubble_dew_derived_routes` key is deliberately excluded from
the generalized PE/CE/CPE matrices. Do not delete existing bubble/dew code or
tests; demote them only in the generalized roadmap. A future row may use a
fixed-composition VLE proof case, but the matrix row must name the underlying
equilibrium family rather than admitting a generic bubble/dew route key.

The executable registry for this document is
`docs/roadmaps/equilibrium_benchmark_registry.yaml`.

## Current Baseline

The current production-exposed public selector routes remain:

- neutral, nonreactive, nonelectrolyte `bubble_pressure`,
  `bubble_temperature`, `dew_pressure`, and `dew_temperature`;
- neutral, nonreactive, nonelectrolyte `flash` through `neutral_tp_flash`;
- neutral, nonreactive, nonelectrolyte, nonassociating `lle` through
  `neutral_lle`.

The current Stage 1 generalized-matrix baseline is narrower:

- PE-01 `neutral_tp_flash`;
- PE-03 `neutral_lle`;
- internal PE support rows used by those routes.

Those routes must report:

```text
phase_discovery_backend = "held_tpd_volume_composition"
stability_certificate = "tpd_postsolve"
```

This does not expose associating LLE, electrolyte LLE, reactive LLE, reactive
electrolyte LLE, or generalized multiphase flash.

## Activation Status Vocabulary

| Status | Meaning |
| --- | --- |
| `production_exposed` | Public route selection is allowed and backed by exact derivative, postsolve certification, and executable proof evidence. |
| `diagnostic_only` | The row records internal infrastructure, diagnostics, or helper capability; it must not return `production_accepted` by itself. |
| `planned_not_public` | The row is part of the roadmap but is not reachable through public route selection. |
| `blocked_not_implemented` | The row is explicitly blocked until named proof, derivative, fixture, and capability gates pass. |
| `source_data_needed` | The row or benchmark has a source-backed target but no executable local fixture yet. |

## Benchmark Evidence Tiers

| Tier | Meaning |
| --- | --- |
| `T0` | Documented design or source inventory only; not executable production evidence. |
| `T1` | Executable package fixture or contract test with deterministic acceptance checks. |
| `T2` | Source-backed digitized or tabulated reference data with tolerances. |
| `T3` | Reproducible literature curve/table workflow with recorded artifacts and tolerances. |

No row may be `production_exposed` unless at least one proof case is `T1` or
higher, the proof fixture is available, exact derivatives are declared, and
postsolve certification checks are named.

## Canonical Activation-Record Schema

The registry records the staged version of the richer activation record that a
future native metadata surface can mirror:

```text
key
category
route_family
exposure
activation_status
production_exposed
phase_kinds
phase_count_policy
species_basis_policy
knowns
primary_variables
optional_variables
variable_model
objective_family
hard_constraints
optional_constraints
residual_blocks
phase_discovery_backend
seed_generators
stability_checks
certification_families
thermo_provider_contract
derivative_contract
internal_state_policy
proof_cases
required_evidence
forbidden_shortcuts
```

This stage keeps the native `ProblemFamilyActivation` struct intact and adds
the richer documentation/registry records first. That preserves the existing
native selector behavior while making the generalized matrix testable.

## Phase-Equilibrium Matrix

Each phase-equilibrium row carries at least one proof example and evidence
tier in `equilibrium_benchmark_registry.yaml`.

| Row | Family key | Scope | Required discovery/certification | First proof case | Current status |
| --- | --- | --- | --- | --- | --- |
| PE-01 | `neutral_tp_flash` | Neutral, nonreactive, nonelectrolyte two-phase TP flash | `held_tpd_volume_composition` plus `tpd_postsolve`; material balance, common pressure, common fugacity, noncollapse, full phase-set stability | Hydrocarbon methane/ethane/propane case in `tests/support/hydrocarbon_cases.py` | `production_exposed` |
| PE-02 | `neutral_two_phase_vle_tp` | Neutral, nonreactive, nonelectrolyte two-phase VLE at fixed `T,P` | Same PE-01 discovery/certification without fixed-composition route reduction | Hydrocarbon VLE fixture after PE-01 remains green | `planned_not_public` |
| PE-03 | `neutral_lle` | Neutral, nonreactive, nonelectrolyte, nonassociating two-liquid split | `held_tpd_volume_composition` plus `tpd_postsolve`; material balance, common pressure, common fugacity, phase-distance anti-collapse, full phase-set stability | Synthetic nonideal binary in `tests/support/equilibrium_cases.py` | `production_exposed` |
| PE-04 | `neutral_multiphase_nonassoc` | Neutral nonassociating LLLE/VLLE or more-than-two-phase discovery | HELD/TPD candidate generation generalized beyond two selected phases; mass-balance-complete phase-set certification | Internal ternary or source-backed literature case after PE-01/PE-03 remain green | `planned_not_public` |
| PE-05 | `neutral_vle_multicomponent` | Neutral multicomponent VLE beyond current hydrocarbon proof envelope | PE-01 discovery/certification retained; broader benchmark coverage | Additional hydrocarbon or PC-SAFT paper fixture | `planned_not_public` |
| PE-06 | `neutral_single_phase_stability` | Single feed stability check without route solve | Neutral TPD over simplex; no raw route acceptance from optimizer status | Hydrocarbon feed stable/unstable pair | `planned_not_public` |
| PE-07 | `neutral_split_seed_generation` | Deterministic seed and candidate ranking layer | Seed inventory, de-duplication, rank diagnostics, phase-set completeness metrics | Shared with PE-01/PE-03/PE-04 | `diagnostic_only` |
| PE-08 | `neutral_density_closure` | EOS density/volume solve for phase candidates | Exact density closure diagnostics and domain failure reporting | Existing native EOS density checks | `diagnostic_only` |
| PE-09 | `neutral_property_certification` | Residual-property consistency at accepted phase states | Exact state/property diagnostics; no separate route admission | Existing state/property checks | `diagnostic_only` |
| PE-10 | `associating_vle_one_assoc_fixed_liquid_pressure` | Neutral, nonelectrolyte, nonreactive VLE proof with at most one associating component | Exact associating EOS derivatives, association mass-action diagnostics, route-local postsolve certification; no global associating LLE claim | Gross/Sadowski 2002 Figure 2 methanol/isobutane, `T = 373.15 K`, `k_ij = 0.05` | `blocked_not_implemented` |
| PE-11 | `associating_isothermal_vle_one_assoc` | Additional isothermal associating VLE proof | Same as PE-10, plus a second source-backed Gross/Sadowski case | Gross/Sadowski 2002 1-pentanol/benzene or 1-propanol/benzene | `blocked_not_implemented` |
| PE-12 | `associating_lle` | Neutral associating liquid-liquid split | PE-04-style full phase discovery plus exact associating EOS derivatives plus PE-10/PE-11 VLE evidence | Methanol/cyclohexane only after VLE gates; water/alcohol later | `blocked_not_implemented` |
| PE-13 | `associating_temperature_condition_vle` | Associating VLE with solved temperature condition | Temperature-variable route proof with exact derivative and association diagnostics | Gross/Sadowski isobaric VLE after PE-10/PE-11 | `blocked_not_implemented` |
| PE-14 | `cross_associating_vle` | More than one associating component or cross-association route | Full association-matrix diagnostics and exact derivative proof | Source-backed alcohol/alcohol or water/alcohol case | `planned_not_public` |
| PE-15 | `electrolyte_lle_salt_solvent` | Strong-electrolyte LLE with salt/solvent lift | Phase electroneutrality, reduced variables, electrolyte TPD, distributed-ion policy | Ascani/Sadowski/Held 2022 mixed-solvent electrolyte case | `source_data_needed` |
| PE-16 | `electrolyte_lle_trace_ion` | Electrolyte LLE with trace-ion handling | Reduced-coordinate bounds, charge-neutral perturbations, reported floors and tolerances | Ascani 2022 trace-ion variant | `source_data_needed` |
| PE-17 | `electrolyte_vlle` | Strong-electrolyte vapor-liquid-liquid equilibrium | Electrolyte HELD/TPD with all eligible phases considered | Ascani 2022 or Held electrolyte benchmark | `source_data_needed` |
| PE-18 | `electrolyte_tpd_reduced_composition` | Formal electrolyte TPD in reduced composition coordinates | Composition domain has `C-2` independent coordinates after sum and electroneutrality constraints | Perdomo/HELD2.0-style reduced TPD case | `planned_not_public` |
| PE-19 | `electrolyte_tpd_reduced_moles` | Formal electrolyte TPD in reduced mole-number coordinates | Reduced mole-number space has `C-1` degrees of freedom after electroneutrality; dual counts depend on primal form | Perdomo-style reduced mole-number case | `planned_not_public` |
| PE-20 | `phase_distance_anti_collapse` | Nontriviality gate for candidate distinctness | Used only to prevent duplicate phases; never treated as thermodynamic equilibrium proof | Existing neutral LLE/flash noncollapse diagnostics | `diagnostic_only` |
| PE-21 | `supporting_plane_phase_set` | Common-tangent/supporting-plane certification | Full phase-set stability, not just per-phase TPD | Shared postsolve certificate | `diagnostic_only` |
| PE-22 | `phase_candidate_mass_balance` | Candidate-set completeness | Candidate phase set must be able to reconstruct the feed within tolerance | Shared HELD/TPD diagnostics | `diagnostic_only` |
| PE-23 | `generalized_multiphase_flash` | General neutral/electrolyte/reactive multiphase flash | All active constraints, reduced variables, reactions, and phase-set certification | Deferred until PE/CE/CPE rows mature | `planned_not_public` |

## Chemical-Equilibrium Matrix

Chemical-equilibrium rows do not imply phase splitting. They own reaction
sets, conservation bases, reaction-constant conventions, and homogeneous
stability checks.

| Row | Family key | Scope | Required proof | Current status |
| --- | --- | --- | --- | --- |
| CE-01 | `ideal_homogeneous_reaction` | Ideal homogeneous reaction at fixed `T,P` | Closed-form or high-precision synthetic equilibrium | `planned_not_public` |
| CE-02 | `stoichiometric_extent_ce` | Extent-variable homogeneous CE | Element/moiety balance and reaction affinity residuals | `planned_not_public` |
| CE-03 | `true_species_ce` | True-species mole variables without phase split | Element matrix rank, positivity, affinity stationarity | `planned_not_public` |
| CE-04 | `nonstoichiometric_element_ce` | Gibbs minimization with elemental conservation | Element basis, rank handling, no dependent reaction requirement | `planned_not_public` |
| CE-05 | `activity_based_speciation` | Nonideal liquid speciation with activity coefficients | Activity/standard-state convention test | `planned_not_public` |
| CE-06 | `acid_base_speciation` | Acid/base reactions and charged species | Charge balance, element balance, pH convention proof | `planned_not_public` |
| CE-07 | `electrolyte_speciation` | Electrolyte true-species speciation | Reduced electrochemical potential and charge-neutral basis | `planned_not_public` |
| CE-08 | `ion_pairing` | Ion-pair formation/dissociation | Element/charge conservation and association with electrolyte variables | `planned_not_public` |
| CE-09 | `solvation_complexation` | Complex formation with neutral and ionic species | Moiety conservation and activity convention proof | `planned_not_public` |
| CE-10 | `salt_dissociation` | Salt split into cation/anion true species | Salt-to-ion lift, electroneutrality, mean ionic convention | `planned_not_public` |
| CE-11 | `temperature_dependent_k` | Temperature-dependent equilibrium constants | Standard-state and derivative convention check | `planned_not_public` |
| CE-12 | `pressure_dependent_k` | Pressure-dependent reaction equilibrium | Volume correction and derivative convention check | `planned_not_public` |
| CE-13 | `reaction_constant_conversion` | Conversion among `K_x`, `K_gamma`, `K_m`, and standard-state forms | Round-trip convention tests | `planned_not_public` |
| CE-14 | `rank_deficient_reaction_sets` | Dependent reactions | Rank reduction and invariant equilibrium proof | `planned_not_public` |
| CE-15 | `moiety_conserved_speciation` | Biochemical or grouped species style balances | Moiety matrix proof | `planned_not_public` |
| CE-16 | `precipitation_candidate` | Solid-forming chemistry | Not admitted by this fluid-phase doctrine; requires a solid-phase ADR | `blocked_not_implemented` |
| CE-17 | `homogeneous_reactive_derivatives` | CE derivative backend | Exact Jacobian/Hessian contracts for CE NLP | `planned_not_public` |
| CE-18 | `standard_state_registry` | Standard-state metadata | Explicit conversion and capability language | `planned_not_public` |
| CE-19 | `ce_certification` | Homogeneous CE postsolve certification | Element residual, charge residual when ionic, affinity residual, positivity | `planned_not_public` |

## Combined Phase-Chemical Matrix

Combined rows activate phase transfer and reaction equilibrium together. They
must never compare raw ionic chemical potentials across phases. Ionic and
electrolyte rows use reduced/projected electrochemical potentials and explicit
charge constraints.

| Row | Family key | Scope | Required proof | Current status |
| --- | --- | --- | --- | --- |
| CPE-01 | `neutral_reactive_vle_flash` | Neutral reactive VLE or TP flash | Transfer equilibrium plus reaction affinity with exact derivatives | `planned_not_public` |
| CPE-02 | `neutral_reactive_fixed_composition_vle` | Neutral reactive fixed-composition VLE utility proof | Route-specific reactive proof before public exposure | `planned_not_public` |
| CPE-03 | `neutral_reactive_lle` | Neutral reactive LLE | Full phase-set discovery plus reaction certification | `planned_not_public` |
| CPE-04 | `neutral_reactive_multiphase` | Neutral reactive LLLE/VLLE | Multiphase candidate completeness and reaction proof | `planned_not_public` |
| CPE-05 | `activity_reactive_lle` | Activity-model reactive LLE analogue | Ascani 2023-style neutral CPE/LLE reference; not an electrolyte proof | `source_data_needed` |
| CPE-06 | `transfer_reaction_split` | Shared species transfer plus in-phase reactions | Clear ownership of transfer and reaction residuals | `planned_not_public` |
| CPE-07 | `nonstoichiometric_reactive_phase` | Element-based reactive phase split | Element conservation across phases and reactions | `planned_not_public` |
| CPE-08 | `reactive_phase_stability` | Reactive TPD or equivalent stability | Phase-set certification with reaction degrees of freedom | `planned_not_public` |
| CPE-09 | `electrolyte_reactive_lle` | Reactive electrolyte LLE | Reduced variables, charge constraints, reaction affinity, electrolyte TPD | `source_data_needed` |
| CPE-10 | `reactive_electrolyte_vle` | Reactive electrolyte VLE | Distributed-ion policy and vapor eligibility proof | `planned_not_public` |
| CPE-11 | `reactive_electrolyte_vlle` | Reactive electrolyte VLLE | Multiphase reduced-coordinate discovery and certification | `source_data_needed` |
| CPE-12 | `cross_phase_reaction` | Reactions spanning phases | Explicit cross-phase stoichiometry and transfer coupling | `planned_not_public` |
| CPE-13 | `extractive_reactive_lle` | Solvent extraction style reactive LLE | Upstream generic proof reduced from downstream examples | `source_data_needed` |
| CPE-14 | `true_species_reactive_electrolyte` | True-species reactive electrolyte formulation | Reduced electrochemical potential and element/charge rank proof | `planned_not_public` |
| CPE-15 | `salt_lift_reactive_phase` | Salt/solvent lifted formulation with reactions | Exact back-lift and convention proof | `planned_not_public` |
| CPE-16 | `combined_derivative_backend` | Exact derivatives for combined CPE NLPs | Jacobian/Hessian contracts across transfer, reaction, charge | `planned_not_public` |
| CPE-17 | `combined_result_schema` | Result payload for combined routes | Phase, reaction, charge, and stability diagnostics | `planned_not_public` |
| CPE-18 | `combined_capability_evidence` | Capability claims for CPE | Evidence records and negative tests | `planned_not_public` |
| CPE-19 | `temperature_route_cpe` | Reactive/electrolyte temperature-condition route | Temperature derivative and route-specific proof | `planned_not_public` |
| CPE-20 | `pressure_route_cpe` | Reactive/electrolyte pressure-condition route | Pressure derivative and route-specific proof | `planned_not_public` |
| CPE-21 | `continuation_cpe` | Continuation across composition or condition | Deterministic continuation diagnostics and certification at each point | `planned_not_public` |
| CPE-22 | `benchmark_cpe` | Source-backed benchmark runs | Fixture, command, expected result, and tolerance | `planned_not_public` |
| CPE-23 | `downstream_smoke_cpe` | Reduced downstream contract reproductions | Compact public API proof, no downstream-specific package API | `source_data_needed` |
| CPE-24 | `generalized_fluid_equilibrium` | Unified multiphase, reactive, electrolyte, associating flash | Final integration after all prerequisite PE, CE, and CPE rows mature | `planned_not_public` |

## Staged Roadmap

| Stage | Scope | Rows | Admission rule |
| --- | --- | --- | --- |
| 0 | Documentation, matrix, schema, registry, and stale-plan reconciliation | All rows | No new public route exposure. |
| 1 | Neutral HELD/TPD phase discovery and postsolve certification | PE-01, PE-03, then PE-04 | Keep associating, electrolyte, and reactive routes blocked. |
| 2 | Standalone chemical-equilibrium infrastructure | CE-01, CE-04, CE-05, CE-13 | Prove balances, reaction affinity, convention metadata, and exact derivatives. |
| 3 | Neutral combined phase-chemical equilibrium | CPE-01, CPE-03, CPE-05 | Require phase and CE proof together. |
| 4 | Narrow associating VLE | PE-10, PE-11 | Start from EOS association checks and one Gross/Sadowski 2002 fixed-composition pressure proof. |
| 5 | Strong-electrolyte LLE | PE-15, PE-16, PE-17 | Require reduced-coordinate charge balance and electrolyte TPD proof. |
| 6 | Electrolyte chemical equilibrium | CE-07, CE-10, CE-13 | Keep standard-state and mean-ionic conventions explicit. |
| 7 | Reactive electrolyte combined equilibrium | CPE-09, CPE-10, CPE-12, CPE-14 | Require charge, reaction, transfer, and phase stability certification together. |
| 8 | Generalized multiphase integration | PE-23, CPE-24 | Not a shortcut around earlier rows. |

The next implementation issue after this matrix/registry stage is:

```text
Implement HELD-style neutral phase discovery and TPD postsolve certification for PE-01/PE-03/PE-04.
```

It must not implement associating, electrolyte, or reactive routes.

## Benchmark Registry

`docs/roadmaps/equilibrium_benchmark_registry.yaml` is the executable manifest
for the matrix. It records:

- evidence-tier definitions;
- excluded derived utility route keys;
- activation rows and required row metadata;
- proof cases with evidence tier, source, fixture status, row references, and
  acceptance checks;
- benchmark cases, including missing-source entries marked
  `source_data_needed`.

If source data are missing, create the manifest entry with
`status: source_data_needed`, add a clear `todo`, and keep the row nonpublic.
Do not invent fixture data or mark literature benchmarks complete without an
executable source-backed data fixture and tolerance checks.

## Evidence Requirements

Phase-equilibrium proof requires all of:

- exact derivative route evidence or an explicit nonproduction label;
- active route metadata matching implementation diagnostics;
- optimizer convergence;
- material-balance residuals;
- phase pressure residuals where pressure is shared;
- transfer equilibrium residuals using the correct potential basis;
- noncollapse/candidate-distinctness checks;
- full phase-set stability, including per-phase stability,
  common-tangent/supporting-plane evidence, and candidate mass-balance
  completeness.

Chemical-equilibrium proof requires all of:

- element or moiety balance residuals;
- charge balance when ionic species are active;
- reaction-affinity residuals in the declared standard-state convention;
- exact derivative evidence for the active CE NLP;
- convention metadata for every equilibrium constant.

Combined phase-chemical proof requires all phase and chemical evidence plus:

- transfer equilibrium and reaction equilibrium satisfied together;
- reduced/projected electrochemical potential equations for ionic transfer;
- deterministic candidate generation and ranking;
- certification of the full accepted phase set, not just the phases returned
  by the local optimizer.

## Explicit Non-Admission Rules

- Do not treat HELD/TPD as eliminating initial guesses. It reduces dependence
  on user phase guesses by using deterministic seeds, candidate generation,
  ranking, continuation, and certification.
- Do not treat a phase-distance constraint as thermodynamic equilibrium. It is
  an anti-collapse and candidate-distinctness gate.
- Do not treat per-phase TPD as enough for multiphase acceptance. The accepted
  phase set must also satisfy common-tangent/supporting-plane and mass-balance
  completeness evidence.
- Do not compare raw ionic chemical potentials across phases. Use the reduced
  or projected electrochemical potential basis declared by the electrolyte
  formulation.
- Do not describe explicit association closures as exact PC-SAFT association
  unless the closure is proven to reproduce the mass-action solution. CppAD
  derivatives of an explicit closure are exact derivatives of that approximate
  Helmholtz model.
- Do not expose associating LLE before PE-04, PE-10, and PE-11 pass.
- Do not broaden `capabilities()` before the corresponding matrix row is
  backed by implementation, proof tests, and negative broadening tests.

## F. Codex Implementation Instructions

Paste the following into the Codex task prompt.

### F1. Task Title

Add generalized equilibrium activation matrices, proof examples, and benchmark
registry

### F2. Non-Interaction Rule

Do not ask the user to choose options. Use the defaults in this document. If
source data are missing, create the manifest entry with
`status: source_data_needed`, add a clear TODO, and write a test that verifies
the benchmark is not marked production until data exist.

### F3. Files To Read First

Read these files before editing:

```text
docs/roadmaps/FULL_ROADMAP.md
docs/roadmaps/unified_equilibrium_core_algorithm.md
docs/roadmaps/generalized_fluid_phase_equilibrium_algorithm.md
docs/roadmaps/gross2002_associating_vle_redo_plan.md
docs/roadmaps/explicit_association_closure_for_pcsaft.md
docs/algorithms.md
docs/latex/algorithms.tex
docs/algorithms_registry.yaml
src/epcsaft/native/equilibrium/core/activation_matrix.h
tests/support/hydrocarbon_cases.py
tests/native/equilibrium/results/test_neutral_vle_reference_values.py
```

Also inspect whether these local analysis paths exist before creating new
fixture duplicates:

```text
analyses/paper_validation/2002_gross/
analyses/paper_validation/2022_ascani_electrolyte_lle/
analyses/paper_validation/2023_ascani_reactive_lle/
analyses/paper_validation/2020_koulocheris_cpe/
analyses/paper_validation/2019_tsanas_electrolyte_cpe/
analyses/paper_validation/2022_tsanas_reactive_electrolyte_lle/
analyses/paper_validation/2022_coatleven_xrr/
analyses/paper_validation/2023_belov_ipopt_ce/
analyses/paper_validation/2026_rezaee_lithium_des/
```

If these exact folders do not exist, do not invent data. Create documentation
and manifest entries with `source_data_needed`.

### F4. Documentation Changes To Make

Create:

```text
docs/roadmaps/generalized_fluid_phase_equilibrium_activation_matrix.md
docs/roadmaps/equilibrium_benchmark_registry.yaml
```

The markdown document must include:

1. Activation status vocabulary.
2. Benchmark evidence tiers.
3. Canonical activation-record schema.
4. Phase-equilibrium matrix PE-01 through PE-23.
5. Chemical-equilibrium matrix CE-01 through CE-19.
6. Combined CPE matrix CPE-01 through CPE-24.
7. Staged roadmap table.
8. Benchmark registry explanation.
9. Codex implementation instructions or a pointer to them.

Update:

```text
docs/roadmaps/unified_equilibrium_core_algorithm.md
docs/roadmaps/FULL_ROADMAP.md
docs/algorithms.md
docs/latex/algorithms.tex
docs/algorithms_registry.yaml
```

The updates must say:

- Bubble/dew routes are derived utility routes and are excluded from the
  generalized activation matrices.
- The generalized matrices are phase-only, chemical-only, and combined CPE.
- Each activation row must carry at least one proof example and evidence tier.
- Do not delete existing bubble/dew code or tests. Only demote them in the
  generalized roadmap.

### F5. Code Changes To Make

Extend or prepare `ProblemFamilyActivation` in:

```text
src/epcsaft/native/equilibrium/core/activation_matrix.h
```

Add fields or a second richer record type. Preferred staged implementation:

```cpp
struct ProofCase {
    std::string key;
    std::string evidence_tier;
    std::string source;
    std::vector<std::string> rows;
    std::vector<std::string> acceptance_checks;
    std::string fixture_status;
};

struct EquilibriumActivationRecord {
    std::string key;
    std::string category;
    std::string route_family;
    std::string exposure;
    std::string activation_status;
    std::vector<std::string> phase_kinds;
    std::string phase_count_policy;
    std::string species_basis_policy;
    std::vector<std::string> knowns;
    std::vector<std::string> primary_variables;
    std::vector<std::string> optional_variables;
    std::string variable_model;
    std::string objective_family;
    std::vector<std::string> hard_constraints;
    std::vector<std::string> optional_constraints;
    std::vector<std::string> residual_blocks;
    std::string phase_discovery_backend;
    std::vector<std::string> seed_generators;
    std::vector<std::string> stability_checks;
    std::vector<std::string> certification_families;
    std::string thermo_provider_contract;
    std::string derivative_contract;
    std::string internal_state_policy;
    std::vector<ProofCase> proof_cases;
    std::vector<std::string> required_evidence;
    std::vector<std::string> forbidden_shortcuts;
};
```

If adding the full struct causes excessive code churn, add documentation-only
records first and keep the old `ProblemFamilyActivation` intact. The first PR
may be docs + registry only.

### F6. Tests To Add

Add tests that do not require implementing all solvers yet:

```text
tests/native/contracts/test_generalized_activation_matrix_registry.py
tests/native/contracts/test_equilibrium_benchmark_registry.py
```

Required assertions:

1. Every activation row has:
   - key
   - category
   - objective_family
   - variable_model
   - derivative_contract
   - certification_families
   - at least one proof_case
2. Every proof case has:
   - evidence_tier
   - source
   - acceptance_checks
   - rows
3. No row is `production_exposed` unless:
   - evidence tier is `T1` or higher,
   - proof case fixture is available,
   - exact derivative contract is declared,
   - certification families include postsolve checks.
4. Bubble/dew route keys do not appear in the generalized matrices.
5. Existing hydrocarbon flash remains mapped to PE-01.
6. Rows marked `blocked_not_implemented` cannot be selected as public routes.
7. Rows marked `diagnostic_only` cannot return `production_accepted`.
8. Rows that involve charged species include `charge_balance` and
   electrochemical or mean ionic certification.
9. Rows that involve reactions include `reaction_affinity` and
   `reaction_constant_convention` certification.
10. Associating rows include `association_mass_action` and must not allow
    `explicit_approx` as final production.

### F7. Implementation Boundaries

Do not implement all solvers in this task. This task is
matrix/registry/schema/test scaffolding.

Do not expose any new public route.

Do not change existing passing hydrocarbon flash behavior.

Do not mark any literature benchmark complete unless executable data and
tolerance checks exist.

Do not add application-specific public APIs such as:

```python
fit_lithium_extraction_parameters(...)
calculate_extraction_efficiency(...)
fit_mea_absorption(...)
screen_lithium_extractants(...)
```

For Rezaee/lithium and MEA examples, only define generic equilibrium
benchmarks that return phase compositions, phase amounts,
activities/fugacities, reaction extents, and residual diagnostics.

### F8. After This Task, The Next Implementation Task

After this matrix/registry PR, open the next implementation issue:

```text
Implement HELD-style neutral phase discovery and TPD postsolve certification for PE-01/PE-03/PE-04.
```

That next issue should implement:

- neutral TPD evaluator;
- volume-composition trial phase problem;
- candidate phase generator;
- candidate de-duplication;
- candidate mass-balance selection;
- postsolve TPD certification;
- activation metadata for `phase_discovery_backend` and
  `stability_certificate`.

It must not implement associating, electrolyte, or reactive routes.

### F9. Final PR Checklist

The PR is complete only if:

- The new markdown activation document exists.
- The benchmark registry exists.
- The old roadmap points to the new activation document.
- The algorithm docs mention the three-matrix split.
- Tests prove every row has a proof example.
- Tests prove blocked rows are not public.
- Tests prove bubble/dew routes are excluded from these generalized matrices.
- The existing hydrocarbon flash test still passes.
- No row claims production support without executable proof.
