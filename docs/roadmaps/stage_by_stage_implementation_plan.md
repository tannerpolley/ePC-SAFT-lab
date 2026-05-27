# GFPE Stage-by-Stage Implementation Plan

This is the GFPE-first execution plan for
`docs/roadmaps/generalized_fluid_phase_equilibrium.md`.
`docs/roadmaps/FULL_ROADMAP.md` remains package context and a completion
standard, but it is not the organizing spine for this file.

The purpose of this plan is to turn generalized fluid-phase equilibrium
doctrine into implementable stages. The center of gravity is:

```text
user request
  -> pretreated thermodynamic problem
  -> family admission and route contract
  -> source-backed phase-equilibrium NLP
  -> stability and phase-discovery certification
  -> benchmark-backed capability claim
```

Stage labels in this file are planning labels only. They are not runtime route
keys, selector keys, registry keys, capability keys, or public API names.

## Scope And Source Map

This plan covers generalized fluid-phase equilibrium and only the adjacent work
needed to make GFPE reliable. Regression, downstream integration, chemical
equilibrium, and combined phase-chemical equilibrium appear only where they
constrain GFPE pretreatment, route admission, validation, or future extension.

Authoritative local references:

- GFPE doctrine: `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- GFPE executable registry: `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- package context: `docs/roadmaps/FULL_ROADMAP.md`
- equation source of truth: `docs/latex/equations.tex`
- algorithm source of truth: `docs/latex/algorithms.tex`
- generated algorithm view: `docs/algorithms.md`
- public equilibrium seam: `src/epcsaft/equilibrium/workflows.py`
- current route admission seam:
  `src/epcsaft/native/equilibrium/core/activation_matrix.h`
- selector owner:
  `src/epcsaft/native/equilibrium/core/selector_core.cpp`
- shared NLP seam:
  `src/epcsaft/native/equilibrium/core/nlp_problem.h`
- Ipopt adapter:
  `src/epcsaft/native/equilibrium/solvers/ipopt_adapter.cpp`
- current neutral amount-volume route:
  `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- current derived bubble/dew route:
  `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp`
- pybind equilibrium registration:
  `src/epcsaft/native/equilibrium/register_bindings.cpp`
- selector and route diagnostics tests:
  `tests/native/equilibrium/diagnostics/`
- GFPE registry tests:
  `tests/native/contracts/test_generalized_activation_matrix_registry.py`
  and `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- public API route tests:
  `tests/api/frontend/test_equilibrium.py`

Non-authoritative raw response notes must stay uncited unless they are
converted into source-backed roadmap text, tests, or registry entries.

## Common GFPE Definitions

Pretreatment means every deterministic step that turns user-facing request data
into a solver-ready thermodynamic problem before Ipopt or a phase-discovery
optimizer runs. Pretreatment owns:

- route request validation;
- unit and basis normalization;
- species ordering;
- family classification;
- parameter provenance checks;
- active EOS contribution selection;
- phase eligibility;
- physical variable layout;
- coordinate transforms;
- bounds and scaling;
- seed generation;
- candidate phase screening;
- diagnostics that explain why a problem is or is not selector-eligible.

The canonical phase variables are true species amounts by phase and phase
volumes:

```text
n_{i,a}  species i amount in phase a
V_a      phase a volume
N_a      = sum_i n_{i,a}
x_{i,a}  = n_{i,a} / N_a
rho_a    = N_a / V_a
```

For fixed `T` and `P`, the physical objective is the pressure-transformed
Helmholtz objective:

```text
Phi(T, P, n, V) = sum_a A_a(T, V_a, n_a) + P * sum_a V_a
```

The neutral nonreactive TP flash constraints are:

```text
sum_a n_{i,a} = z_i F
P_eos(T, V_a, n_a) - P = 0
mu_i(T, V_a, n_a) - mu_i(T, V_b, n_b) = 0
```

Electrolyte extensions add per-phase charge balance and projected
electrochemical-potential equality:

```text
sum_i charge_i * n_{i,a} = 0
Pi_perp(mu_i + charge_i * psi_a) equal across transferable phases
```

Reactive extensions add reaction-affinity constraints:

```text
sum_i nu_{r,i} * mu_i = 0
```

The current deterministic neutral TPD and candidate screening code is useful
pretreatment and postsolve support. It is not full HELD.

## Stage 0 - GFPE Doctrine And Registry Lock

Purpose: make the GFPE roadmap, registry, algorithm index, and public route
language agree before any new route behavior is added.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `docs/latex/algorithms.tex`
- `docs/algorithms.md`
- `docs/algorithms_registry.yaml`
- `docs/adr/0003-selector-core-activation-capabilities.md`
- `docs/adr/0004-associating-equilibrium-architecture.md`

Steps:

1. Keep GFPE as the canonical generalized equilibrium doctrine.
2. Keep `FULL_ROADMAP.md` as package context only for this work.
3. Keep `equilibrium_benchmark_registry.yaml` on schema version 2 with:
   `family_rows`, `derived_subworkflows`, and PE-focused `benchmark_cases`.
4. Keep roadmap `family_label` values descriptive:
   `PE-Neutral TP Flash`, `PE-Associating TP Flash`,
   `PE-Electrolyte LLE/TP Flash`, `PE-Generalized Multiphase`,
   `CE Chemical Equilibrium Placeholder`, and
   `CPE Combined Phase-Chemical Placeholder`.
5. State in every relevant doc that family labels are roadmap labels only.
6. Keep current public route strings separate from roadmap family labels.
7. Keep bubble, dew, cloud, and shadow outside the main family rows.
8. State that current deterministic TPD/candidate screening is not full HELD.
9. Keep generalized family rows `planned_not_public` and
   `production_exposed: false` until staged HELD, exact derivatives, and
   postsolve certification pass.
10. Keep raw AI-response notes uncited and outside the authoritative source
    hierarchy.
11. Regenerate `docs/algorithms.md` and `docs/algorithms_registry.yaml` only
    through `scripts/docs/sync_algorithm_registry.py` after changing
    `docs/latex/algorithms.tex`.

Exit evidence:

- GFPE and registry tests pass.
- Generated algorithm docs are synchronized when algorithm source changes.
- No visible PE/CE/CPE numeric row IDs remain in GFPE or the registry.
- Public route strings are not presented as roadmap family labels.
- Existing public route behavior is not removed by roadmap cleanup.

Do not proceed if:

- a generalized family is marked production-exposed without HELD and exact
  derivative evidence;
- deterministic screening is named as full HELD;
- the plan uses `FULL_ROADMAP.md` milestones as the GFPE stage spine.

## Stage 1 - Public Request Pretreatment

Purpose: define how a user-facing equilibrium request becomes a validated
route request before native dispatch.

References:

- `src/epcsaft/equilibrium/workflows.py`
- `src/epcsaft/native/equilibrium/core/selector_core.cpp`
- `tests/api/frontend/test_equilibrium.py`
- `tests/native/equilibrium/diagnostics/test_selector_core_contracts.py`
- ADR 0003 selector-core decision

Steps:

1. Enumerate the current public equilibrium request forms:
   `bubble_pressure`, `bubble_temperature`, `dew_pressure`,
   `dew_temperature`, `flash`, and neutral nonassociating `lle`.
2. Document which public inputs are required, forbidden, or role-specific for
   each route:
   `T`, `P`, `x`, `y`, `z`, feed amount basis, composition role, and route
   option payloads.
3. Define the canonical input unit expectation at the public seam:
   temperature in kelvin, pressure in pascal, compositions as mole fractions
   unless a documented route says otherwise, and feed amounts in a declared
   extensive basis.
4. Add request-level validation for finite numeric inputs before any EOS call.
5. Normalize composition vectors once, with diagnostics reporting the original
   sum, normalized sum, and species ordering.
6. Reject mismatched composition length before native solver dispatch.
7. Reject route requests that mix incompatible fixed variables, such as
   specifying both fixed `T` and a temperature-solve boundary route.
8. Keep public request validation separate from GFPE roadmap family admission.
9. Preserve existing public route names while planning generalized internals.
10. Make the selector error messages explain whether the failure came from
    route shape, mixture family, parameter data, derivative coverage, or
    production exposure.

Exit evidence:

- API tests cover required and forbidden request fields for each public route.
- Selector diagnostics distinguish invalid request shape from unsupported
  family admission.
- No code consumes roadmap `family_label` strings as route keys.

Do not proceed if:

- invalid public inputs can reach EOS state construction;
- route validation silently rewrites the user request without diagnostics;
- generalized roadmap labels are passed through the public API as route names.

## Stage 2 - Species And Family Classification Pretreatment

Purpose: classify the thermodynamic problem before choosing a route, while
making clear that family labels are planning labels, not code keys.

References:

- `src/epcsaft/native/equilibrium/core/activation_matrix.h`
- `src/epcsaft/native/equilibrium/core/selector_core.cpp`
- `src/epcsaft/native/equilibrium/core/activation_plan.h`
- `src/epcsaft/native/equilibrium/core/activated_equilibrium_nlp.cpp`
- `tests/native/contracts/test_equilibrium_activation_capabilities.py`
- `tests/native/equilibrium/diagnostics/test_route_metadata_contracts.py`

Steps:

1. Define a pretreated classification record with fields for:
   neutral species, ionic species, associating species, reactive species,
   phase-eligible species, transferable species, and fixed species.
2. Separate code-owned route admission keys from roadmap labels. Existing
   native keys such as current selector families may remain implementation
   details, but they must not leak into the roadmap as the organizing model.
3. Classify a mixture as neutral only when no ionic charge balance,
   electrochemical-potential projection, reaction basis, or association
   mass-action variables are needed.
4. Classify a mixture as associating when active parameters require association
   site fractions or association mass-action consistency.
5. Classify a mixture as electrolyte when any charged true species, salt basis,
   Debye-Huckel term, Born term, charge-neutral reduced variables, or
   electrochemical transfer condition is active.
6. Classify a mixture as reactive when chemical stoichiometry, reaction
   extents, standard-state convention, or reaction affinity constraints are
   active.
7. Define phase eligibility per species and per phase before building the NLP.
8. Define transfer eligibility separately from species existence. A phase may
   contain a species that is not transferable across every phase boundary.
9. Report selector-ineligible mixtures before Ipopt dispatch when the active
   family has not passed GFPE admission gates.
10. Add negative tests for associating, electrolyte, and reactive inputs
    reaching current neutral-only production routes.

Exit evidence:

- Classification diagnostics are present in route metadata.
- Selector tests prove unsupported families fail before solver dispatch.
- Capability output distinguishes current public utilities from future GFPE
  family rows.

Do not proceed if:

- association, electrolyte, or reactive markers can be ignored to force a
  neutral route;
- a runtime key is renamed just to match a roadmap label;
- selector-ineligible failures are only discovered after an optimizer run.

## Stage 3 - Parameter And EOS Contribution Pretreatment

Purpose: prove the route has the parameter data and EOS contribution set needed
for the requested family before variables or seeds are assembled.

References:

- `docs/latex/equations.tex`
- `src/epcsaft/model/parameters.py`
- `src/epcsaft/model/options.py`
- `src/epcsaft/frontend/mixture.py`
- `src/epcsaft/native/` EOS contribution owners
- `docs/adr/0002-hard-public-api-reset-cppad-only-frontend.md`
- `docs/roadmaps/explicit_association_closure_for_pcsaft.md`
- `tests/native/contracts/test_equation_registry.py`

Steps:

1. Treat `ParameterSet` and `ParameterSet.to_runtime_dict()` as the canonical
   public-to-native parameter boundary.
2. Check pure neutral PC-SAFT parameters before admitting a neutral PE route:
   segment number, segment diameter, dispersion energy, molecular weight when
   required by density or reporting, and binary interaction parameters.
3. Check association parameters before admitting associating PE:
   association scheme, site list, association energy, association volume, and
   cross-association rules.
4. Check electrolyte parameters before admitting electrolyte PE:
   charges, ion sizes or solvated diameters, ion-solvent dispersion data,
   Debye-Huckel settings, Born settings, relative-permittivity model, SSM
   model, and DS model where active.
5. Record active residual contribution families in route metadata:
   hard-chain, dispersion, association, Debye-Huckel, Born, SSM, DS, and any
   selected dielectric contribution.
6. Reject missing parameter families loudly at pretreatment time.
7. Record parameter provenance in proof fixtures, including source file,
   paper/table/figure when available, units, converted units, and fitted
   domain.
8. Do not treat a direct dictionary as a full literature benchmark source
   unless the test is explicitly synthetic or a small unit test.
9. Route every durable equation claim through `docs/latex/equations.tex` or a
   generated registry view.
10. Keep association explicit-closure diagnostics separate from exact
    association production admission.
11. For electrolyte validation, require the Born SSM+DS master path with exact
    Hessian support before declaring the electrolyte PE proof eligible.

Exit evidence:

- Route diagnostics list active residual families and parameter provenance.
- Missing parameter-family tests fail before native solver dispatch.
- Benchmark fixtures point to source-backed parameter records.
- Equation registry tests catch stale equation documentation.

Do not proceed if:

- a route can run with placeholder parameters;
- a proof case lacks source-backed parameter provenance;
- electrolyte PE validation bypasses the Born SSM+DS exact-Hessian gate.

## Stage 4 - Canonical Basis And Variable Layout Pretreatment

Purpose: define the physical variables and lifted true-species state before the
route creates an `NlpProblem`.

References:

- `src/epcsaft/native/equilibrium/core/variable_layout.h`
- `src/epcsaft/native/equilibrium/core/variable_layout.cpp`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.h`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- `src/epcsaft/native/equilibrium/core/nlp_problem.h`
- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`

Steps:

1. Define the physical variable vector in true species amounts and phase
   volumes for every PE route:

   ```text
   x_phys = [n_{1,1}, ..., n_{Nc,1}, V_1, ..., n_{1,Np}, ..., V_Np]
   ```

2. Store species order, phase order, and variable block boundaries in route
   metadata.
3. Build helper accessors for amount blocks, volume blocks, composition blocks,
   total phase amount, density, and phase fraction.
4. Ensure route constraints are written in the same physical basis used by the
   objective.
5. Define the material-balance map once:

   ```text
   b_i(n) = sum_a n_{i,a} - z_i F
   ```

6. Define the pressure-consistency map once:

   ```text
   p_a(n_a, V_a) = P_eos(T, V_a, n_a) - P_spec
   ```

7. Define transferable-potential residuals only for species that are both
   present and transferable across the selected phase pair.
8. For associating routes, choose one production architecture before proof:
   lifted association-site variables with mass-action constraints, or complete
   implicit association sensitivities.
9. For electrolyte routes, define reduced charge-neutral coordinates and a
   deterministic lift into true species by phase.
10. For reactive routes, define reaction coordinates or an element/moiety basis
    and a lift into true species by phase.
11. Record the lift/back-lift equations in documentation before coding the
    route.
12. Add variable-layout tests for species count, phase count, phase volume
    positions, and lifted basis consistency.

Exit evidence:

- Variable-layout tests prove consistent index ownership.
- Route metadata can reconstruct every physical block from a solver result.
- Constraint residual tests use the same basis as the objective.

Do not proceed if:

- composition variables and amount variables are mixed without a declared lift;
- charge-neutral reduced variables lack a true-species lift;
- association site variables are hidden from derivative and diagnostics
  contracts.

## Stage 5 - Bounds, Scaling, And Transform Pretreatment

Purpose: make domain safety a declared route contract before expanding GFPE
families.

References:

- `src/epcsaft/native/equilibrium/core/nlp_problem.h`
- `src/epcsaft/native/equilibrium/solvers/ipopt_adapter.cpp`
- `tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py`
- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`

Steps:

1. Require every route to own variable lower and upper bounds.
2. Require every route to own constraint lower and upper bounds.
3. Define amount floors, phase-volume bounds, density bounds, composition
   floors, packing-fraction margins, and phase-fraction noncollapse limits.
4. For electrolyte routes, add charge-neutrality constraints and reduced-basis
   bounds before electrochemical residuals are evaluated.
5. For associating routes, add site-fraction or association-state bounds before
   association residuals are evaluated.
6. Define a reusable `VariableTransform` concept:

   ```text
   solver_to_physical(u) -> x
   dx_du(u)
   d2x_du2(u)
   ```

7. Keep route equations in physical variables. The transform owns coordinate
   maps and chain-rule derivative assembly.
8. Use smooth maps for positivity, trace components, simplex-like
   compositions, phase volumes, and reduced electrolyte coordinates.
9. Require scaling for amounts, volumes, pressure residuals, material-balance
   residuals, potential-equality residuals, objective values, and transform
   coordinates.
10. Use Ipopt's internal barrier for declared bounds and constraints.
11. Do not add permanent custom barrier terms to the thermodynamic objective.
12. Report domain margins in result diagnostics:
    amount floor margin, volume margin, density margin, packing margin,
    composition floor margin, charge-balance margin, and transform saturation
    margin.
13. Add contract tests that assert scaling metadata and domain-margin metadata
    are present for admitted generalized routes.

Exit evidence:

- `NlpProblem` exposes bounds and scaling for every route.
- Ipopt adapter tests prove declared bounds and constraints are transferred.
- Diagnostics report domain margins without silent clipping.

Do not proceed if:

- a route relies on ad hoc clipping to remain inside the EOS domain;
- the thermodynamic objective is permanently modified for domain safety;
- a transform changes variables without exact chain-rule derivative coverage.

## Stage 6 - Seed And Stability Pretreatment

Purpose: separate initialization support from generalized phase-discovery
evidence.

References:

- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- `docs/algorithms.md` entries:
  `neutral_tpd_stability`,
  `neutral_deterministic_phase_candidate_screening`,
  `phase_candidate_mass_balance_selection`,
  and `postsolve_tpd_certification`
- `tests/native/equilibrium/results/test_neutral_vle_reference_values.py`
- `tests/native/equilibrium/results/test_neutral_lle_reference_values.py`
- `tests/native/equilibrium/diagnostics/test_selector_core_contracts.py`

Steps:

1. Keep density roots and single-phase state solves as state evaluation and seed
   generation tools.
2. Keep deterministic neutral TPD/candidate screening as seed and certification
   support.
3. Name deterministic candidate screening exactly as deterministic screening,
   not HELD.
4. Store every generated candidate with:
   composition, phase kind, volume or density, seed source, TPD estimate,
   pressure residual estimate, and feasibility status.
5. Run candidate de-duplication with declared composition and density
   tolerances.
6. Run candidate mass-balance feasibility before assembling a final phase set.
7. Preserve lower-free-energy or instability diagnostics even when a candidate
   is rejected for mass-balance infeasibility.
8. Add seed ranking that is deterministic for a fixed input problem.
9. Record whether the final Ipopt start came from user input, deterministic
   screening, continuation, a boundary workflow, or a stored benchmark fixture.
10. Add postsolve stability diagnostics after final Ipopt solves.
11. Keep seed-generation success distinct from route acceptance.

Exit evidence:

- Diagnostics identify seed source and candidate-selection decisions.
- Tests reject any doc or registry language that calls deterministic screening
  full HELD.
- Current utility routes retain their existing deterministic support without
  creating generalized production claims.

Do not proceed if:

- optimizer success is accepted without postsolve stability checks;
- candidate generation is treated as proof of phase-set completeness;
- seed failure is hidden behind a generic solver failure.

## Stage 7 - Shared NLP And Ipopt Infrastructure Gate

Purpose: make the shared optimizer seam strong enough for generalized GFPE
before adding new families.

References:

- `src/epcsaft/native/equilibrium/core/nlp_problem.h`
- `src/epcsaft/native/equilibrium/core/nlp_problem.cpp`
- `src/epcsaft/native/equilibrium/solvers/ipopt_adapter.h`
- `src/epcsaft/native/equilibrium/solvers/ipopt_adapter.cpp`
- `tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py`
- `scripts/dev/run_ipopt_exact_hessian_proofs.py`

Steps:

1. Treat `NlpProblem` as the route-owned contract for objective, gradient,
   constraints, sparse Jacobian structure, sparse Jacobian values, Lagrangian
   Hessian values, bounds, scaling, and diagnostics.
2. Require fixed sparse Jacobian ordering:

   ```text
   rows[k], cols[k], values[k]
   ```

   must describe the same nonzero in the same order for every evaluation.

3. Require exact objective gradients for admitted generalized routes.
4. Require exact constraint Jacobians for admitted generalized routes.
5. Require exact Lagrangian Hessian values before production exposure unless a
   route is explicitly marked internal diagnostic.
6. Require derivative metadata that records the active backend and any missing
   exact block.
7. Keep Ipopt option transfer in the adapter, not in route equations.
8. Keep route equation ownership in the route problem, not in the adapter.
9. Add tests for:
   objective value;
   gradient size;
   constraint size;
   Jacobian nonzero count;
   fixed Jacobian ordering;
   Hessian nonzero count;
   bounds size;
   scaling size;
   and diagnostic payload shape.
10. Add failure tests for mismatched sparse structure and value vector length.
11. Add exact-Hessian proof scripts for active route families before production
    admission.

Exit evidence:

- Focused native Ipopt adapter tests pass.
- A route cannot be admitted if its sparse structure and value vectors diverge.
- Exact derivative metadata is visible in route diagnostics and capability
  evidence.

Do not proceed if:

- a generalized route bypasses `NlpProblem`;
- Ipopt adapter code owns thermodynamic residual equations;
- missing exact Hessian coverage is treated as production-ready.

## Stage 8 - Neutral TP Flash Proof

Purpose: prove the first generalized PE family on neutral TP flash before
deriving boundary workflows or widening to association/electrolytes.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- `src/epcsaft/native/equilibrium/core/selector_core.cpp`
- `tests/native/equilibrium/results/test_neutral_vle_reference_values.py`
- `tests/native/equilibrium/diagnostics/test_native_route_diagnostics_contract.py`

Steps:

1. Use `PE-Neutral TP Flash` as the first GFPE proof family.
2. Use the amount-volume physical variable model from Stage 4.
3. Use the bounds, scaling, and transform rules from Stage 5.
4. Use deterministic screening only as seed and postsolve support from Stage 6.
5. Build the proof around Pereira 2012 System III unless a source-backed audit
   proves the fixture physically unsuitable.
6. Record the proof fixture inputs:
   species, parameters, binary interaction parameters, `T`, `P`, feed
   composition, expected phases, expected composition window, and source
   provenance.
7. Evaluate the thermodynamic objective:

   ```text
   Phi = sum_a A_a + P * sum_a V_a
   ```

8. Enforce material balance, pressure consistency, and chemical-potential
   equality as hard route constraints or certified KKT residuals.
9. Certify noncollapse through phase amount, phase fraction, composition
   distance, and density/volume margins.
10. Certify postsolve stability with TPD diagnostics.
11. Certify exact derivative coverage for the active objective and constraints.
12. Keep the registry row `planned_not_public` until continuous TPD and HELD
    stages pass.
13. Keep existing public `flash` behavior unchanged unless the implementation
    explicitly migrates it through the same verified route with tests.

Exit evidence:

- Pereira neutral proof fixture exists and is source-backed.
- Neutral TP flash diagnostics include material, pressure, potential,
  stability, derivative, and domain margins.
- Registry tests still show generalized neutral TP flash as not production
  exposed until HELD completion.

Do not proceed if:

- the first neutral proof is a synthetic fixture;
- production admission rests only on Ipopt convergence;
- public utility-route success is used as generalized GFPE proof without the
  GFPE gates.

## Stage 9 - Derived Boundary Workflows And Diagrams

Purpose: derive bubble, dew, cloud, and shadow workflows from the neutral TP
flash core after the main proof is reliable.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp`
- `src/epcsaft/equilibrium/workflows.py`
- `tests/api/frontend/test_equilibrium.py`
- `tests/native/contracts/test_equilibrium_benchmark_registry.py`

Steps:

1. Keep bubble, dew, cloud, and shadow as derived subworkflows, not main
   activation-family rows.
2. Implement each boundary workflow as a degree-of-freedom swap over the
   shared phase NLP:
   fixed `T` solve for boundary `P`, or fixed `P` solve for boundary `T`.
3. Bubble point:
   fixed liquid/feed composition, incipient vapor composition free, boundary
   `P` or `T` free.
4. Dew point:
   fixed vapor composition, incipient liquid composition free, boundary `P` or
   `T` free.
5. Cloud point:
   fixed parent liquid composition, incipient second-liquid composition free,
   boundary `P` or `T` free.
6. Shadow point:
   matched cloud-point state with shadow-phase composition and volume reported.
7. Use the Pereira neutral proof mixture for shared boundary workflow testing
   unless implementation proves it physically unsuitable.
8. If Pereira is unsuitable for a specific boundary diagram, stop and select a
   source-backed neutral binary. Do not invent a fixture.
9. Generate `T-x` and `P-x` traces from boundary solves with continuation
   metadata and failure diagnostics per trace point.
10. Keep VLLE-specific tests out of this stage.
11. Keep current public bubble/dew route behavior intact while generalized
    derived-workflow tests are added.

Exit evidence:

- Registry tests prove bubble/dew/cloud/shadow are derived subworkflows.
- Boundary workflow tests prove fixed/free variable contracts.
- Diagram tests prove trace generation and diagnostic reporting.

Do not proceed if:

- a boundary workflow is promoted to a main family row;
- cloud/shadow tests silently become VLLE tests;
- boundary workflows duplicate a separate thermodynamic core instead of using
  the shared GFPE route.

## Stage 10 - Continuous TPD And HELD Stage Ladder

Purpose: replace seed-only deterministic screening with the staged
phase-discovery evidence required for generalized admission.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/algorithms.md`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- `tests/native/contracts/test_generalized_activation_matrix_registry.py`
- `tests/native/equilibrium/diagnostics/test_selector_core_contracts.py`

Steps:

1. Add continuous TPD minimization in volume-composition space.
2. Report the TPD objective, trial-phase composition, trial volume or density,
   local status, and source seed for every TPD minimization.
3. Add HELD Stage I stability testing with multiple starts and declared
   failure modes.
4. Add HELD Stage II dual cutting-plane phase discovery with explicit upper and
   lower bounds.
5. Store candidate phases generated by Stage II with enough metadata to replay
   route assembly.
6. Use the Ipopt amount-volume NLP as HELD Stage III primal refinement.
7. Record the relation between Stage II bounds and Stage III refined objective.
8. Add phase-set completeness checks:
   no missing lower-free-energy candidate, material-balance feasibility, no
   duplicate phase, and no collapsed phase.
9. Keep deterministic screening results available as seeds, but do not mix
   them with HELD status fields.
10. Expose HELD stage status in registry evidence only after executable tests
    exist.

Exit evidence:

- Tests distinguish deterministic screening, continuous TPD, HELD Stage I,
  HELD Stage II, and HELD Stage III.
- Registry rows can name which HELD gates are passed for each family.
- Generalized production exposure remains false until the relevant HELD ladder
  is complete.

Do not proceed if:

- local TPD success is treated as global phase-discovery proof;
- HELD status fields can be filled by deterministic screening;
- phase-set completeness lacks a mass-balance feasibility check.

## Stage 11 - Generalized Multiphase PE

Purpose: extend GFPE from selected two-phase solves to unknown phase count and
phase-set certification.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- future generalized phase-set route owner to be added only after Stage 10

Steps:

1. Define a generalized phase-set data structure with phase count, phase kinds,
   candidate source, amounts, volumes, compositions, and objective value.
2. Allow more than two candidate phases after HELD Stage II phase discovery.
3. Assemble material-balance feasibility for arbitrary candidate phase sets.
4. Select candidate phase sets by feasibility, thermodynamic objective, and
   phase-set completeness diagnostics.
5. Refine candidate phase sets with the shared amount-volume NLP.
6. Reject duplicate or collapsed phases after refinement.
7. Certify every accepted phase against continuous TPD or HELD-discovered
   missing phases.
8. Add benchmark replay for representative neutral, associating, and
   electrolyte cases only after each base family is validated.
9. Keep `PE-Generalized Multiphase` not production-exposed until it proves
   phase-count independence.

Exit evidence:

- Generalized phase-set tests fail if a lower-free-energy feasible phase set is
  omitted.
- Result diagnostics report phase count, phase kinds, phase-set feasibility,
  and completeness status.
- No route assumes exactly two phases after entering the generalized
  multiphase path.

Do not proceed if:

- multiphase support is only a loop around two-phase route calls;
- phase-count assumptions remain hidden in variable layout or diagnostics;
- representative cases are replayed before their base family proof is stable.

## Stage 12 - Associating PE Admission

Purpose: admit associating phase equilibrium through the GFPE amount-volume
route, not through a narrow bubble-only path.

References:

- `docs/roadmaps/explicit_association_closure_for_pcsaft.md`
- `docs/adr/0004-associating-equilibrium-architecture.md`
- `docs/latex/equations.tex`
- `docs/algorithms.md` entry `explicit_association_closure_diagnostics`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`

Steps:

1. Choose the production association architecture before implementation:
   lifted association-site variables with mass-action constraints, or complete
   implicit association sensitivities.
2. If lifted variables are chosen, add site-fraction variables to the physical
   route layout and association mass-action equations to the constraint set.
3. If implicit sensitivities are chosen, prove complete first and second
   derivative propagation through the association solve.
4. Keep reduced explicit association closures as diagnostics unless a route is
   deliberately exposed as approximate.
5. Require exact gradient, Jacobian, and Lagrangian Hessian coverage for active
   association terms before production exposure.
6. Use Gross/Sadowski 2002 methanol/cyclohexane as the first associating proof.
7. Add a two-associating-component follow-on such as water/1-pentanol only
   after the first proof is stable and source-backed.
8. Reuse neutral GFPE bounds, scaling, transforms, stability, and HELD gates.
9. Add association-specific postsolve checks:
   site-fraction bounds, association mass-action residuals, contribution
   activation, and derivative block coverage.
10. Keep selector-ineligible associating mixtures out of current neutral public
    utility routes until the proof gates pass.

Exit evidence:

- Associating proof fixture is source-backed and executable.
- Association derivative tests prove exact first and second derivative coverage
  for the chosen architecture.
- Registry still rejects a narrow associating bubble route as general
  associating PE proof.

Do not proceed if:

- a single bubble-pressure proof is treated as associating TP flash validation;
- explicit association diagnostics are silently used as exact production
  equations;
- association variables are omitted from route metadata.

## Stage 13 - Electrolyte Pretreatment And Born SSM+DS Gate

Purpose: make electrolyte thermodynamics solver-ready before electrolyte PE is
validated.

References:

- `docs/latex/equations.tex`
- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `analyses/paper_validation/2026_khudaida/`
- `scripts/dev/run_ipopt_exact_hessian_proofs.py`

Steps:

1. Define true species for salts, ions, neutral solvents, complexes, and any
   phase-restricted species.
2. Define charges and charge-balance constraints before building the route NLP.
3. Define reduced electroneutral coordinates per phase.
4. Define a deterministic lift from reduced coordinates into true species
   amounts.
5. Define a back-lift for diagnostics and result reporting.
6. Project electrochemical potentials into the reduced electroneutral basis
   before comparing transfer equilibrium.
7. Record the active dielectric, Debye-Huckel, Born, SSM, and DS contribution
   settings in route metadata.
8. Make the Born SSM+DS path the master Born path.
9. Make simpler Born modes reduce from the master path rather than owning a
   separate production route.
10. Prove exact Hessian support for active Born SSM+DS phase blocks before
    electrolyte PE validation.
11. Add electrolyte domain diagnostics:
    charge-balance residuals, ionic-strength margins, concentration bounds,
    dielectric model domain, Born radius/model domain, and projected-potential
    residuals.
12. Keep electrolyte PE blocked until reduced variables and Born exact Hessian
    evidence are in place.

Exit evidence:

- Reduced electroneutral variable tests prove lift/back-lift consistency.
- Born SSM+DS exact-Hessian proof tests pass for active electrolyte blocks.
- Electrolyte route diagnostics distinguish charge balance from transfer
  equilibrium.

Do not proceed if:

- raw ionic chemical potentials are compared without projection;
- electrolyte validation runs before the Born SSM+DS exact-Hessian gate;
- charge neutrality is enforced by hidden clipping instead of declared
  constraints or reduced variables.

## Stage 14 - Electrolyte PE And HELD2.0 Validation

Purpose: prove strong-electrolyte LLE/TP flash through electrolyte-specific
phase discovery and certification.

References:

- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `analyses/paper_validation/2026_khudaida/`
- `docs/papers/` source material when a fixture is promoted into validation
- `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- future electrolyte route tests

Steps:

1. Add electrolyte TPD in the reduced electroneutral variable basis.
2. Add HELD2.0 phase discovery before claiming electrolyte generalized
   production readiness.
3. Use Khudaida 2026 electrolyte LLE as the first electrolyte validation
   target.
4. Treat Held 2014 Figure 6 as a follow-on after its data, units, and
   conventions are source-backed locally.
5. Treat Ascani/Sadowski/Held 2022 as a lower-confidence follow-on until its
   data and convention audit is complete.
6. Certify per-phase charge balance.
7. Certify total material balance.
8. Certify pressure consistency where the route is TP.
9. Certify projected electrochemical-potential equality for transferable
   charged species.
10. Certify neutral species chemical-potential or fugacity equality as
    appropriate.
11. Certify phase-set completeness through HELD2.0.
12. Report solvent, ion, salt, and phase-basis outputs in a result shape that
    downstream projects can consume without private EOS code.

Exit evidence:

- Khudaida electrolyte fixture is executable with declared tolerances.
- Electrolyte validation reports charge, material, pressure, potential,
  stability, derivative, and domain diagnostics.
- Registry rows remain nonproduction until HELD2.0 and Born SSM+DS exact
  Hessian gates pass.

Do not proceed if:

- electrolyte LLE acceptance is based only on composition error;
- a downstream case-study metric is used as the upstream package validation
  target;
- Held or Ascani follow-ons are promoted without source-backed fixture data.

## Stage 15 - CE And CPE Interface Gates For GFPE

Purpose: define the minimum chemical-equilibrium and combined-equilibrium
contracts needed so GFPE is not boxed into a nonreactive design.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/FULL_ROADMAP.md`
- `docs/latex/equations.tex`
- future CE/CPE roadmap files when created

Steps:

1. Keep CE and CPE as placeholders in the GFPE registry until their equations,
   standard states, and tests exist.
2. Define the species-basis interface between GFPE and future CE:
   true species, element or moiety balances, reaction stoichiometry, and
   reaction extents.
3. Define the reaction-affinity residual:

   ```text
   A_r = sum_i nu_{r,i} * mu_i
   ```

4. Define the standard-state and reaction-constant convention before any
   reaction proof.
5. Ensure GFPE variable layouts can later carry reaction variables or lifted
   true-species amounts without redesigning the phase route.
6. Ensure electrolyte reduced variables can coexist with reaction coordinates
   for future reactive electrolyte LLE.
7. Define CPE as one simultaneous thermodynamic problem, not a staged phase
   solve plus a staged reaction solve accepted as final proof.
8. Keep homogeneous CE proof separate from CPE proof.
9. Keep CPE production blocked until PE and CE proof gates both exist.

Exit evidence:

- GFPE docs state the CE/CPE boundary without claiming implementation.
- Variable-layout and route metadata design can represent future reaction
  variables.
- Registry tests keep CE and CPE placeholders not production-exposed.

Do not proceed if:

- CE or CPE placeholders are used to claim reactive package capability;
- reaction standard-state conventions are implicit;
- staged PE plus staged CE is treated as simultaneous CPE proof.

## Stage 16 - Registry, Capability, And Benchmark Closure

Purpose: turn GFPE implementation evidence into public capability claims only
after the relevant proof gates pass.

References:

- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `src/epcsaft/runtime/capability_evidence.py`
- `tests/native/contracts/test_generalized_activation_matrix_registry.py`
- `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- `tests/native/contracts/test_equilibrium_activation_capabilities.py`
- `tests/workflows/repo/test_workflow_entrypoints.py`

Steps:

1. Promote a family row only when its stage-specific gates are executable and
   tested.
2. Keep benchmark cases PE-focused:
   Pereira first for neutral, Gross/Sadowski first for associating, Khudaida
   first for electrolyte, then Held and Ascani as lower-confidence follow-ons.
3. Record evidence tier, fixture status, source path, active equations,
   derivative coverage, stability coverage, and postsolve certification status
   for each benchmark.
4. Keep `epcsaft.capabilities()` honest:
   current public utility routes are separate from generalized GFPE rows.
5. Do not remove existing public route behavior when a GFPE family remains
   planned.
6. Add negative tests for stale source references, deleted narrow roadmap file
   references, and raw-response note citations.
7. Add positive tests for derived subworkflow placement after neutral TP flash.
8. Add positive tests for deterministic screening being named as deterministic
   screening, not HELD.
9. Add benchmark fixture tests only when source data and acceptance tolerances
   are present.
10. Before handoff, run focused registry and route contract tests in proportion
    to the edited surface.

Exit evidence:

- Registry contract tests pass.
- Capability tests pass.
- Benchmark tests pass for admitted fixtures.
- Public docs and capability output make the same claims.
- No downstream-specific application metric is exposed as a package API.

Do not proceed if:

- a registry row is promoted before proof gates pass;
- a capability claim cannot point to executable evidence;
- a downstream repository becomes the source of package route semantics.

## Stage Dependency Summary

The GFPE dependency chain is:

```text
0 doctrine and registry lock
1 public request pretreatment
2 species and family classification
3 parameter and EOS contribution pretreatment
4 canonical basis and variable layout
5 bounds, scaling, and transforms
6 seed and stability pretreatment
7 shared NLP and Ipopt infrastructure
8 neutral TP flash proof
9 derived boundary workflows
10 continuous TPD and HELD
11 generalized multiphase PE
12 associating PE
13 electrolyte pretreatment and Born SSM+DS
14 electrolyte PE and HELD2.0
15 CE/CPE interface gates
16 registry, capability, and benchmark closure
```

The earliest useful implementation slices are therefore not new phase families.
They are pretreatment contracts, diagnostics, bounds/scaling/transform
contracts, and sparse NLP derivative contracts. New families should wait until
the neutral GFPE proof and phase-discovery gates make the acceptance path
auditable.
