# Generalized Fluid-Phase Equilibrium Activation Matrix

## Purpose

This document is the row-by-row activation companion to
`docs/roadmaps/generalized_fluid_phase_equilibrium_algorithm.md`. The
algorithm doctrine defines the mathematical form. This matrix defines the
admission rows, proof examples, sequencing gates, and documentation checks that
keep the implementation from silently broadening into unsupported phase,
chemical, associating, electrolyte, or reactive routes.

The matrix is not a wish list. A row may become production-exposed only when
the route implementation, derivative backend, activation metadata, postsolve
certification, proof case, negative broadening tests, and public capability
language all agree.

## Current Baseline

The current production-exposed equilibrium baseline is:

- neutral, nonreactive, nonelectrolyte `bubble_pressure`,
  `bubble_temperature`, `dew_pressure`, and `dew_temperature`;
- neutral, nonreactive, nonelectrolyte `flash` through `neutral_tp_flash`;
- neutral, nonreactive, nonelectrolyte, nonassociating `lle` through
  `neutral_lle`.

The current Stage 1 phase-discovery baseline is implemented only for the
neutral fixed-`T`, fixed-`P` two-phase EOS routes:

- `neutral_tp_flash`;
- `neutral_lle`.

Those routes must report:

```text
phase_discovery_backend = "held_tpd_volume_composition"
stability_certificate = "tpd_postsolve"
```

This does not expose associating LLE, electrolyte LLE, reactive LLE, reactive
electrolyte LLE, or generalized multiphase flash. It only means the neutral
TP flash and neutral nonassociating LLE baseline now has deterministic
HELD/TPD-style candidate generation and full phase-set postsolve
certification.

## Row Schema

Each activation row should define:

- row id and family key;
- public route names, if any;
- current exposure status;
- phase kinds and phase-count policy;
- admissible species classes;
- fixed knowns and solved unknowns;
- variable representation;
- thermodynamic objective family;
- transfer, reaction, charge, and conservation constraints;
- internal-state strategy;
- discovery backend and seed generators;
- postsolve certification family;
- derivative and Hessian requirement;
- first proof case and negative broadening checks;
- capability wording that the public API is allowed to claim.

Accepted exposure statuses:

| Status | Meaning |
| --- | --- |
| `production_current` | Public route is exposed and backed by exact derivative and certification evidence. |
| `declared_not_exposed` | Row is represented in the activation policy but blocked from production selection. |
| `planned` | Row is part of the roadmap but should not be reachable through public route selection. |
| `experimental_internal` | Internal diagnostic route only; public capabilities must not claim support. |
| `blocked_until` | Row has explicit proof gates that must pass before route admission. |

## Phase-Equilibrium Rows

| Row | Family key | Scope | Required discovery/certification | First proof case | Current status |
| --- | --- | --- | --- | --- | --- |
| PE-01 | `neutral_tp_flash` | Neutral, nonreactive, nonelectrolyte two-phase TP flash | `held_tpd_volume_composition` plus `tpd_postsolve`; material balance, common pressure, common fugacity, noncollapse, full phase-set stability | Hydrocarbon methane/ethane/propane case in `tests/support/hydrocarbon_cases.py`; proof through `Run Ipopt Exact Hessian Proofs` | `production_current` |
| PE-02 | `bubble_dew_derived_routes` | Neutral, nonreactive, nonelectrolyte bubble/dew pressure and temperature | Route-seeded incipient-phase solve; fixed-composition, pressure/temperature, fugacity, and noncollapse checks | Existing hydrocarbon bubble/dew cases | `production_current` for nonassociating neutral routes |
| PE-03 | `neutral_lle` | Neutral, nonreactive, nonelectrolyte, nonassociating two-liquid split | `held_tpd_volume_composition` plus `tpd_postsolve`; material balance, common pressure, common fugacity, phase-distance anti-collapse, full phase-set stability | Synthetic nonideal binary in `tests/support/equilibrium_cases.py` | `production_current` with nonassociating restriction |
| PE-04 | `neutral_multiphase_nonassoc` | Neutral nonassociating LLLE/VLLE or more-than-two-phase discovery | HELD/TPD candidate generation generalized beyond two selected phases; mass-balance-complete phase-set certification | Internal ternary or source-backed literature case after PE-01/PE-03 remain green | `planned` |
| PE-05 | `neutral_vle_multicomponent` | Neutral multicomponent VLE beyond current hydrocarbon proof envelope | PE-01 discovery/certification retained; broader benchmark coverage | Additional hydrocarbon or PC-SAFT paper fixture | `planned` |
| PE-06 | `neutral_single_phase_stability` | Single feed stability check without route solve | Neutral TPD over simplex; no raw route acceptance from optimizer status | Hydrocarbon feed stable/unstable pair | `planned` |
| PE-07 | `neutral_split_seed_generation` | Deterministic seed and candidate ranking layer | Seed inventory, de-duplication, rank diagnostics, phase-set completeness metrics | Shared with PE-01/PE-03/PE-04 | `production_current` only where called by PE-01/PE-03 |
| PE-08 | `neutral_density_closure` | EOS density/volume solve for phase candidates | Exact density closure diagnostics and domain failure reporting | Existing native EOS density checks | `production_current` as a provider dependency |
| PE-09 | `neutral_property_certification` | Residual-property consistency at accepted phase states | Exact state/property diagnostics; no separate route admission | Existing state/property checks | `production_current` as a provider dependency |
| PE-10 | `associating_bubble_pressure_one_assoc` | Neutral, nonelectrolyte, nonreactive `bubble_pressure` with at most one associating component | Exact associating EOS derivatives, association diagnostics, route-local postsolve certification; no global associating LLE claim | Gross/Sadowski 2002 Figure 2 methanol/isobutane, `T = 373.15 K`, `k_ij = 0.05` | `blocked_until` association EOS proof and narrow route proof pass |
| PE-11 | `associating_isothermal_vle_one_assoc` | Additional isothermal associating VLE proof | Same as PE-10, plus a second source-backed Gross/Sadowski case | Gross/Sadowski 2002 1-pentanol/benzene or 1-propanol/benzene | `blocked_until` PE-10 passes |
| PE-12 | `associating_lle` | Neutral associating liquid-liquid split | PE-04-style full phase discovery plus exact associating EOS derivatives plus PE-10/PE-11 VLE evidence | Methanol/cyclohexane only after the VLE gates; water/alcohol later | `blocked_until` PE-04, PE-10, and PE-11 pass |
| PE-13 | `associating_temperature_routes` | Associating bubble/dew temperature routes | Temperature-variable route proof with exact derivative and association diagnostics | Gross/Sadowski isobaric VLE after PE-10/PE-11 | `blocked_until` isothermal associating VLE is stable |
| PE-14 | `cross_associating_vle` | More than one associating component or cross-association route | Full association-matrix diagnostics and exact derivative proof | Source-backed alcohol/alcohol or water/alcohol case | `planned` |
| PE-15 | `electrolyte_lle_salt_solvent` | Strong-electrolyte LLE with salt/solvent lift | Phase electroneutrality, reduced variables, electrolyte TPD, distributed-ion policy | Ascani/Sadowski/Held 2022 mixed-solvent electrolyte case | `blocked_until` neutral phase-discovery baseline and electrolyte TPD proof pass |
| PE-16 | `electrolyte_lle_trace_ion` | Electrolyte LLE with trace-ion handling | Reduced-coordinate bounds, charge-neutral perturbations, reported floors and tolerances | Ascani 2022 trace-ion variant | `planned` |
| PE-17 | `electrolyte_vlle` | Strong-electrolyte vapor-liquid-liquid equilibrium | Electrolyte HELD/TPD with all eligible phases considered | Ascani 2022 or Held electrolyte benchmark | `planned` |
| PE-18 | `electrolyte_tpd_reduced_composition` | Formal electrolyte TPD in reduced composition coordinates | Composition domain has `C-2` independent coordinates after sum and electroneutrality constraints | Perdomo/HELD2.0-style reduced TPD case | `planned` |
| PE-19 | `electrolyte_tpd_reduced_moles` | Formal electrolyte TPD in reduced mole-number coordinates | Reduced mole-number space has `C-1` degrees of freedom after electroneutrality; dual counts depend on primal form | Perdomo-style reduced mole-number case | `planned` |
| PE-20 | `phase_distance_anti_collapse` | Nontriviality gate for candidate distinctness | Used only to prevent duplicate phases; never treated as thermodynamic equilibrium proof | Existing neutral LLE/flash noncollapse diagnostics | `production_current` as a certification subcheck |
| PE-21 | `supporting_plane_phase_set` | Common-tangent/supporting-plane certification | Full phase-set stability, not just per-phase TPD | Shared postsolve certificate | `production_current` for PE-01/PE-03 |
| PE-22 | `phase_candidate_mass_balance` | Candidate-set completeness | Candidate phase set must be able to reconstruct the feed within tolerance | Shared HELD/TPD diagnostics | `production_current` for PE-01/PE-03 |
| PE-23 | `generalized_multiphase_flash` | General neutral/electrolyte/reactive multiphase flash | All active constraints, reduced variables, reactions, and phase-set certification | Deferred until PE/CE/CPE rows mature | `planned` |

## Chemical-Equilibrium Rows

Chemical-equilibrium rows do not imply phase splitting. They own reaction
sets, conservation bases, reaction-constant conventions, and homogeneous
stability checks.

| Row | Family key | Scope | Required proof | Current status |
| --- | --- | --- | --- | --- |
| CE-01 | `ideal_homogeneous_reaction` | Ideal homogeneous reaction at fixed `T,P` | Closed-form or high-precision synthetic equilibrium | `planned` |
| CE-02 | `stoichiometric_extent_ce` | Extent-variable homogeneous CE | Element/moiety balance and reaction affinity residuals | `planned` |
| CE-03 | `true_species_ce` | True-species mole variables without phase split | Element matrix rank, positivity, affinity stationarity | `planned` |
| CE-04 | `nonstoichiometric_element_ce` | Gibbs minimization with elemental conservation | Element basis, rank handling, no dependent reaction requirement | `planned` |
| CE-05 | `activity_based_speciation` | Nonideal liquid speciation with activity coefficients | Activity/standard-state convention test | `planned` |
| CE-06 | `acid_base_speciation` | Acid/base reactions and charged species | Charge balance, element balance, pH convention proof | `planned` |
| CE-07 | `electrolyte_speciation` | Electrolyte true-species speciation | Reduced electrochemical potential and charge-neutral basis | `planned` |
| CE-08 | `ion_pairing` | Ion-pair formation/dissociation | Element/charge conservation and association with electrolyte variables | `planned` |
| CE-09 | `solvation_complexation` | Complex formation with neutral and ionic species | Moiety conservation and activity convention proof | `planned` |
| CE-10 | `salt_dissociation` | Salt split into cation/anion true species | Salt-to-ion lift, electroneutrality, mean ionic convention | `planned` |
| CE-11 | `temperature_dependent_k` | Temperature-dependent equilibrium constants | Standard-state and derivative convention check | `planned` |
| CE-12 | `pressure_dependent_k` | Pressure-dependent reaction equilibrium | Volume correction and derivative convention check | `planned` |
| CE-13 | `reaction_constant_conversion` | Conversion among `K_x`, `K_gamma`, `K_m`, and standard-state forms | Round-trip convention tests | `planned` |
| CE-14 | `rank_deficient_reaction_sets` | Dependent reactions | Rank reduction and invariant equilibrium proof | `planned` |
| CE-15 | `moiety_conserved_speciation` | Biochemical or grouped species style balances | Moiety matrix proof | `planned` |
| CE-16 | `precipitation_candidate` | Solid-forming chemistry | Not admitted by this fluid-phase doctrine; requires a solid-phase ADR | `declared_not_exposed` |
| CE-17 | `homogeneous_reactive_derivatives` | CE derivative backend | Exact Jacobian/Hessian contracts for CE NLP | `planned` |
| CE-18 | `standard_state_registry` | Standard-state metadata | Explicit conversion and capability language | `planned` |
| CE-19 | `ce_certification` | Homogeneous CE postsolve certification | Element residual, charge residual when ionic, affinity residual, positivity | `planned` |

## Combined Phase-Chemical Rows

Combined rows activate phase transfer and reaction equilibrium together. They
must never compare raw ionic chemical potentials across phases. Ionic and
electrolyte rows use reduced/projected electrochemical potentials and explicit
charge constraints.

| Row | Family key | Scope | Required proof | Current status |
| --- | --- | --- | --- | --- |
| CPE-01 | `neutral_reactive_vle_flash` | Neutral reactive VLE or TP flash | Transfer equilibrium plus reaction affinity with exact derivatives | `planned` |
| CPE-02 | `neutral_reactive_bubble_dew` | Neutral reactive bubble/dew routes | Route-specific reactive proof before public exposure | `planned` |
| CPE-03 | `neutral_reactive_lle` | Neutral reactive LLE | Full phase-set discovery plus reaction certification | `planned` |
| CPE-04 | `neutral_reactive_multiphase` | Neutral reactive LLLE/VLLE | Multiphase candidate completeness and reaction proof | `planned` |
| CPE-05 | `activity_reactive_lle` | Activity-model reactive LLE analogue | Ascani 2023-style neutral CPE/LLE reference; not an electrolyte proof | `planned` |
| CPE-06 | `transfer_reaction_split` | Shared species transfer plus in-phase reactions | Clear ownership of transfer and reaction residuals | `planned` |
| CPE-07 | `nonstoichiometric_reactive_phase` | Element-based reactive phase split | Element conservation across phases and reactions | `planned` |
| CPE-08 | `reactive_phase_stability` | Reactive TPD or equivalent stability | Phase-set certification with reaction degrees of freedom | `planned` |
| CPE-09 | `electrolyte_reactive_lle` | Reactive electrolyte LLE | Reduced variables, charge constraints, reaction affinity, electrolyte TPD | `planned` |
| CPE-10 | `reactive_electrolyte_vle` | Reactive electrolyte VLE | Distributed-ion policy and vapor eligibility proof | `planned` |
| CPE-11 | `reactive_electrolyte_vlle` | Reactive electrolyte VLLE | Multiphase reduced-coordinate discovery and certification | `planned` |
| CPE-12 | `cross_phase_reaction` | Reactions spanning phases | Explicit cross-phase stoichiometry and transfer coupling | `planned` |
| CPE-13 | `extractive_reactive_lle` | Solvent extraction style reactive LLE | Upstream generic proof reduced from downstream examples | `planned` |
| CPE-14 | `true_species_reactive_electrolyte` | True-species reactive electrolyte formulation | Reduced electrochemical potential and element/charge rank proof | `planned` |
| CPE-15 | `salt_lift_reactive_phase` | Salt/solvent lifted formulation with reactions | Exact back-lift and convention proof | `planned` |
| CPE-16 | `combined_derivative_backend` | Exact derivatives for combined CPE NLPs | Jacobian/Hessian contracts across transfer, reaction, charge | `planned` |
| CPE-17 | `combined_result_schema` | Result payload for combined routes | Phase, reaction, charge, and stability diagnostics | `planned` |
| CPE-18 | `combined_capability_evidence` | Capability claims for CPE | Evidence records and negative tests | `planned` |
| CPE-19 | `temperature_route_cpe` | Reactive/electrolyte temperature routes | Temperature derivative and route-specific proof | `planned` |
| CPE-20 | `pressure_route_cpe` | Reactive/electrolyte pressure routes | Pressure derivative and route-specific proof | `planned` |
| CPE-21 | `continuation_cpe` | Continuation across composition or condition | Deterministic continuation diagnostics and certification at each point | `planned` |
| CPE-22 | `benchmark_cpe` | Source-backed benchmark runs | Fixture, command, expected result, and tolerance | `planned` |
| CPE-23 | `downstream_smoke_cpe` | Reduced downstream contract reproductions | Compact public API proof, no downstream-specific package API | `planned` |
| CPE-24 | `generalized_fluid_equilibrium` | Unified multiphase, reactive, electrolyte, associating flash | Final integration after all prerequisite PE, CE, and CPE rows mature | `planned` |

## Stage Order

Stage 0 is documentation, matrix, and schema reconciliation. The source docs
for Stage 0 are this file,
`docs/roadmaps/generalized_fluid_phase_equilibrium_algorithm.md`,
`docs/roadmaps/unified_equilibrium_core_algorithm.md`, and
`docs/roadmaps/FULL_ROADMAP.md`.

Stage 1 is neutral HELD/TPD phase discovery and postsolve certification. The
current implementation has completed this only for PE-01 and PE-03. The next
neutral expansion is PE-04, not associating or electrolyte LLE.

Stage 2 is standalone chemical-equilibrium infrastructure:

- CE-01 ideal homogeneous CE;
- CE-04 nonstoichiometric element CE;
- CE-05 activity-based speciation;
- CE-13 reaction-constant conversion.

Stage 3 is neutral combined phase-chemical equilibrium:

- CPE-01 neutral reactive VLE flash;
- CPE-03 neutral reactive LLE;
- CPE-05 activity-model neutral reactive LLE references.

Stage 4 is narrow associating VLE:

- PE-10 Gross/Sadowski 2002 methanol/isobutane `bubble_pressure`;
- PE-11 one additional isothermal Gross/Sadowski VLE proof;
- approximate explicit closures remain approximate Helmholtz models unless
  they are proven to match the exact association mass-action solution.

Stage 5 is strong-electrolyte LLE:

- PE-15 salt/solvent electrolyte LLE;
- PE-16 trace-ion handling;
- PE-17 electrolyte VLLE only after LLE is stable.

Stage 6 is electrolyte chemical equilibrium:

- CE-07 electrolyte speciation;
- CE-10 salt dissociation;
- CE-13 conversion conventions retained.

Stage 7 is reactive electrolyte combined equilibrium:

- CPE-09 reactive electrolyte LLE;
- CPE-10 reactive electrolyte VLE;
- CPE-12 cross-phase reactions;
- CPE-14 true-species reactive electrolyte formulation.

Stage 8 is generalized multiphase electrolyte/reactive/equilibrium
integration. It is not a shortcut around the earlier rows.

## Evidence Requirements

Phase-equilibrium proof requires all of:

- exact derivative route evidence or an explicit nonproduction label;
- active route metadata matching the implementation diagnostics;
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

## Codex Agent Instructions

Future Codex agents must treat this matrix as an implementation-control
document, not background reading. Before creating issues, editing code, or
changing capability claims for generalized equilibrium, read these files in
order:

1. `docs/roadmaps/FULL_ROADMAP.md`
2. `docs/roadmaps/unified_equilibrium_core_algorithm.md`
3. `docs/roadmaps/generalized_fluid_phase_equilibrium_algorithm.md`
4. `docs/roadmaps/generalized_fluid_phase_equilibrium_activation_matrix.md`
5. The row-specific roadmap or ADR for the requested tranche, for example
   `docs/roadmaps/gross2002_associating_vle_redo_plan.md` and ADR 0005 for
   associating `bubble_pressure`.

For Stage 1 work, preserve the current boundary:

- PE-01 `neutral_tp_flash` and PE-03 `neutral_lle` are the only rows with the
  current neutral `held_tpd_volume_composition` plus `tpd_postsolve` baseline.
- PE-03 remains neutral, nonreactive, nonelectrolyte, and nonassociating.
- PE-04 neutral multicomponent/multiphase phase discovery is the next neutral
  expansion; it is not permission to start associating LLE.
- New public routes require an explicit activation-row status change,
  capability-evidence update, tests, and negative broadening checks.

When turning this matrix into implementation issues, create vertical slices
that can be verified independently:

- one issue for row/schema or metadata changes;
- one issue for route or solver implementation;
- one issue for postsolve certification and result payloads;
- one issue for public API/capability claims only after route proof exists;
- one issue for source-backed benchmark or proof fixtures;
- one issue for documentation and stale-plan cleanup.

Every issue or implementation tranche must name:

- the row IDs it changes;
- the exact files expected to own the change;
- the route exposure status before and after;
- the proof case and validation command;
- the rows that remain blocked;
- the capability text that must not change.

Use repo-owned shared execution surfaces where they exist. Prefer the IntelliJ
run configurations for build, docs, registry sync, text gates, exact-Hessian
proofs, and named validation slices. Shell probes are fine for narrow reads,
git work, and one-off stale-text scans, but do not bypass existing dashboard
commands for durable validation.

Required validation for any matrix or Stage 1 documentation change:

```text
Sync Algorithm Registry
Check Text Gates
Build Docs
tests/native/contracts/test_algorithm_registry.py
```

If native route metadata, result diagnostics, activation rows, or AlgID owner
comments change, also run:

```text
Test Native Contracts
```

Before handoff, run the repo cleanup hook from the repo root:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Forbidden shortcuts:

- Do not update the matrix without updating stale roadmap, algorithm-registry,
  and capability language that contradicts it.
- Do not admit a route by removing a selector guard globally.
- Do not claim general associating VLE/LLE, electrolyte LLE, reactive LLE, or
  reactive electrolyte support from a single narrow proof.
- Do not treat explicit approximate association closures as exact PC-SAFT
  association.
- Do not treat optimizer success, a phase-distance constraint, or per-phase TPD
  alone as full phase-set certification.
- Do not compare raw ionic chemical potentials across phases.
- Do not add application-specific downstream APIs while implementing generic
  equilibrium rows.
