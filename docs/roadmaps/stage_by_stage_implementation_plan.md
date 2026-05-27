# GFPE Stage-by-Stage Implementation Plan

This is the GFPE-first execution plan for
`docs/roadmaps/generalized_fluid_phase_equilibrium.md`.

GFPE is the organizing spine for this file. `FULL_ROADMAP.md` is a boundary
document: it explains package identity, derivative policy, benchmark
standards, and downstream consequences, but it does not define the stage order
here. Package-wide milestones are intentionally not used as stage names.

The plan covers generalized fluid-phase equilibrium and only the pretreatment,
NLP, derivative, phase-discovery, and registry work needed to make GFPE
reliable. Regression, downstream application metrics, homogeneous chemical
equilibrium, and combined phase-chemical equilibrium appear only where they
constrain GFPE admission or future extension.

Stage labels in this file are planning labels only. They are not Python route
strings, C++ selector keys, registry keys, capability keys, or public API
names.

## Source Hierarchy

Use this order when two documents disagree:

1. `docs/latex/equations.tex` for EOS contribution equations.
2. `docs/roadmaps/generalized_fluid_phase_equilibrium.md` for GFPE doctrine,
   mathematical form, family order, and admission policy.
3. `docs/roadmaps/equilibrium_benchmark_registry.yaml` for executable family
   rows, derived subworkflows, proof cases, and production flags.
4. This file for implementation sequencing and stage exit evidence.
5. `docs/roadmaps/FULL_ROADMAP.md` for package-wide boundaries and completion
   standards.
6. Generated views such as `docs/equations.md`, `docs/equations_registry.yaml`,
   `docs/algorithms.md`, and `docs/algorithms_registry.yaml` for navigation
   and consistency checks only.

Raw response notes under `docs/ChatGPT_Gemini_Responses/` are not
authoritative sources and must not be cited in GFPE doctrine or registry rows
unless their claims have been converted into source-backed equations, tests, or
benchmark fixture records.

## Implementation Reference Map

GFPE doctrine and registry:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `tests/native/contracts/test_generalized_activation_matrix_registry.py`
- `tests/native/contracts/test_equilibrium_benchmark_registry.py`

Equation and algorithm sources:

- `docs/latex/equations.tex`
- `docs/latex/algorithms.tex`
- `scripts/docs/sync_equation_registry.py`
- `scripts/docs/sync_algorithm_registry.py`
- `tests/native/contracts/test_equation_registry.py`
- `tests/native/contracts/test_algorithm_registry.py`

Public request seam:

- `src/epcsaft/equilibrium/workflows.py`
- `tests/api/frontend/test_equilibrium.py`

Selector and family-admission seam:

- `src/epcsaft/native/equilibrium/core/activation_matrix.h`
- `src/epcsaft/native/equilibrium/core/activation_plan.h`
- `src/epcsaft/native/equilibrium/core/selector_core.h`
- `src/epcsaft/native/equilibrium/core/selector_core.cpp`
- `src/epcsaft/native/equilibrium/register_bindings.cpp`
- `tests/native/equilibrium/diagnostics/test_selector_core_contracts.py`
- `tests/native/contracts/test_equilibrium_activation_capabilities.py`

Shared phase-NLP seam:

- `src/epcsaft/native/equilibrium/core/nlp_problem.h`
- `src/epcsaft/native/equilibrium/core/nlp_problem.cpp`
- `src/epcsaft/native/equilibrium/core/variable_layout.h`
- `src/epcsaft/native/equilibrium/core/variable_layout.cpp`
- `src/epcsaft/native/equilibrium/core/second_order.h`
- `src/epcsaft/native/equilibrium/core/variable_transform.h`
- `src/epcsaft/native/equilibrium/core/variable_transform.cpp`
- `src/epcsaft/native/equilibrium/solvers/ipopt_adapter.h`
- `src/epcsaft/native/equilibrium/solvers/ipopt_adapter.cpp`
- `tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py`

Current neutral utility-route anchors:

- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.h`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp`
- `tests/native/equilibrium/results/test_neutral_vle_reference_values.py`
- `tests/native/equilibrium/results/test_neutral_lle_reference_values.py`
- `tests/native/equilibrium/diagnostics/test_native_route_diagnostics_contract.py`

Parameter, mixture, and capability seams:

- `src/epcsaft/model/parameters.py`
- `src/epcsaft/model/options.py`
- `src/epcsaft/frontend/mixture.py`
- `src/epcsaft/runtime/capability_evidence.py`
- `tests/support/equilibrium_cases.py`

Association and electrolyte constraints:

- `docs/roadmaps/explicit_association_closure_for_pcsaft.md`
- `docs/adr/0004-associating-equilibrium-architecture.md`
- `analyses/paper_validation/2026_khudaida/`
- `scripts/dev/run_ipopt_exact_hessian_proofs.py`

## GFPE Pretreatment Pipeline

Pretreatment is the deterministic front half of GFPE. It turns a user-facing
request into a solver-ready thermodynamic problem before Ipopt or a
phase-discovery optimizer runs.

The intended pipeline is:

```text
public request
  -> request-shape record
  -> normalized thermodynamic input record
  -> species and phase-eligibility record
  -> parameter and EOS-contribution readiness record
  -> physical-basis and variable-layout record
  -> bounds, scaling, and transform record
  -> seed and candidate record
  -> NlpProblem contract
  -> Ipopt solve or phase-discovery stage
  -> postsolve certification
  -> registry and capability evidence
```

Each stage below either creates one of those records, deepens the shared NLP
contract, or supplies the source-backed proof needed to promote registry
evidence.

## GFPE Non-Negotiables

These rules apply to every stage:

- Family labels are roadmap labels only.
- Public route strings remain separate from roadmap labels.
- Current `bubble_*`, `dew_*`, `flash`, and neutral `lle` utility behavior is
  preserved unless a later implementation explicitly migrates it with tests.
- Current deterministic TPD/candidate screening is seed and certification
  support, not full HELD.
- Generalized production exposure requires exact objective gradients, exact
  constraint Jacobians, exact Lagrangian Hessian support, route-owned bounds,
  route-owned scaling, transform chain-rule coverage, HELD-stage phase
  discovery, and postsolve phase-set certification.
- Domain safety uses explicit route bounds, a smooth `VariableTransform`
  wrapper, and Ipopt internal barrier handling of declared bounds and
  constraints.
- Do not add permanent custom barrier terms to the thermodynamic objective.
- Benchmark proof cases must be source-backed. A synthetic unit fixture can
  test mechanics, but it cannot prove a GFPE family.
- Pereira 2012 System III remains HELD/SAFT-VR literature context only until
  model parity or a source-backed ePC-SAFT reparameterization exists.
- The first neutral proof target must be a source-backed ePC-SAFT-compatible
  TP flash fixture.
- Gross/Sadowski 2002 methanol/cyclohexane is the first associating proof
  target after association derivative gates pass.
- Khudaida 2026 electrolyte LLE is the first electrolyte proof target after
  Born SSM+DS exact-Hessian and HELD2.0 gates pass.

## Common Physical Form

For phases `a = 1..Np` and true species `i = 1..Nc`, the canonical physical
variables are phase species amounts and phase volumes:

```text
n_{i,a}  species i amount in phase a
V_a      phase a volume
N_a      = sum_i n_{i,a}
x_{i,a}  = n_{i,a} / N_a
rho_a    = N_a / V_a
```

For fixed `T` and `P`, the GFPE objective is:

```text
Phi(T, P, n, V) = sum_a A_a(T, V_a, n_a) + P * sum_a V_a
```

The neutral nonreactive TP flash constraints are:

```text
sum_a n_{i,a} = z_i F
P_eos(T, V_a, n_a) - P = 0
mu_i(T, V_a, n_a) - mu_i(T, V_b, n_b) = 0
```

Electrolyte GFPE adds phase charge balance and reduced-basis electrochemical
potential equality:

```text
sum_i charge_i * n_{i,a} = 0
Pi_perp(mu_i + charge_i * psi_a) equal across transferable phases
```

Future combined phase-chemical work adds reaction-affinity constraints:

```text
sum_i nu_{r,i} * mu_i = 0
```

These equations define the direction of the stage plan. The implementation can
use reduced coordinates, transformed coordinates, or route-specific degrees of
freedom only if it provides a deterministic lift back into this physical basis.

## Stage 0 - GFPE Doctrine, Registry, And Scope Lock

Purpose: keep the GFPE source hierarchy, registry rows, algorithm language, and
public-route language aligned before solver work expands.

Primary output:

- A stable source hierarchy and registry doctrine that future stages can test
  against.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `docs/roadmaps/FULL_ROADMAP.md`
- `docs/latex/algorithms.tex`
- `docs/algorithms.md`
- `docs/algorithms_registry.yaml`
- `docs/adr/0003-selector-core-activation-capabilities.md`
- `docs/adr/0004-associating-equilibrium-architecture.md`

Substeps:

1. State that GFPE, not the package-wide roadmap, controls this stage order.
2. Keep `FULL_ROADMAP.md` as a boundary for package identity, derivative
   policy, benchmark expectations, and downstream consequences.
3. Keep `equilibrium_benchmark_registry.yaml` on schema version 2.
4. Keep registry top-level sections as `family_rows`,
   `derived_subworkflows`, and PE-focused `benchmark_cases`.
5. Keep the six visible family labels descriptive:
   `PE-Neutral TP Flash`, `PE-Associating TP Flash`,
   `PE-Electrolyte LLE/TP Flash`, `PE-Generalized Multiphase`,
   `CE Chemical Equilibrium Placeholder`, and
   `CPE Combined Phase-Chemical Placeholder`.
6. State that those labels are roadmap labels only in GFPE, the registry, and
   this plan.
7. Keep public route strings out of the registry family-label namespace.
8. Keep bubble, dew, cloud, and shadow under `derived_subworkflows`.
9. Keep generalized family rows `planned_not_public` with
   `production_exposed: false` until HELD and derivative gates pass.
10. Remove stale narrow-roadmap references when they appear in registry-facing
    docs or tests.
11. Keep raw AI-response notes uncited.
12. Update `docs/latex/algorithms.tex` before regenerating algorithm views.
13. Regenerate `docs/algorithms.md` and `docs/algorithms_registry.yaml` only
    with `scripts/docs/sync_algorithm_registry.py`.

Acceptance checks:

- Registry schema is version 2.
- No visible numeric PE/CE/CPE row IDs remain in GFPE or the registry.
- Derived workflows are not family rows.
- Deterministic screening is not named as full HELD.
- Algorithm generated views are synchronized when algorithm source changes.

Stop conditions:

- A generalized family row is production-exposed before HELD and exact
  derivative evidence exists.
- Public route strings are presented as GFPE family labels.
- This file starts using package-wide roadmap milestones as the stage spine.

## Stage 1 - Public Request Pretreatment

Purpose: turn a user-facing equilibrium call into a validated request-shape
record before native dispatch.

Primary output:

- `request_pretreatment` diagnostics covering route shape, fixed variables,
  composition role, unit basis, and validation status.

References:

- `src/epcsaft/equilibrium/workflows.py`
- `src/epcsaft/native/equilibrium/core/selector_core.cpp`
- `src/epcsaft/native/equilibrium/register_bindings.cpp`
- `tests/api/frontend/test_equilibrium.py`
- `tests/native/equilibrium/diagnostics/test_selector_core_contracts.py`

Substeps:

1. Enumerate the current public route names:
   `bubble_pressure`, `bubble_temperature`, `dew_pressure`,
   `dew_temperature`, `flash`, and neutral nonassociating `lle`.
2. For each route, declare required inputs, forbidden inputs, and
   role-specific composition inputs:
   `T`, `P`, `x`, `y`, `z`, feed amount, and route options.
3. Declare public unit expectations:
   `T` in kelvin, `P` in pascal, composition as mole fractions, and feed as a
   declared extensive basis.
4. Validate finite numeric values before native dispatch.
5. Validate composition vector length against species count before EOS state
   construction.
6. Normalize composition vectors exactly once.
7. Report original composition sum, normalized sum, normalization tolerance,
   and species ordering in diagnostics.
8. Reject route requests that mix incompatible fixed variables, such as a
   boundary-temperature route with a fixed boundary temperature.
9. Separate public request shape from GFPE family admission. A valid public
   request may still be selector-ineligible.
10. Make errors identify the failed pretreatment layer:
    route shape, composition basis, mixture family, parameter readiness,
    derivative coverage, or production exposure.
11. Preserve current public route names. Do not introduce roadmap
    `family_label` values as public route names.

Acceptance checks:

- API tests cover required and forbidden public inputs.
- Selector diagnostics distinguish route-shape rejection from family-admission
  rejection.
- No code path consumes `family_label` strings as public routes.

Stop conditions:

- Invalid public inputs reach native EOS state construction.
- Request normalization silently changes user input without diagnostics.
- Route validation and GFPE admission are collapsed into one opaque failure.

## Stage 2 - Thermodynamic Input Basis Pretreatment

Purpose: make temperature, pressure, feed, species order, and amount basis
explicit before species-family classification.

Primary output:

- `thermodynamic_input` diagnostics covering resolved `T`, `P`, feed basis,
  total feed amount, species order, and composition basis.

References:

- `src/epcsaft/equilibrium/workflows.py`
- `src/epcsaft/frontend/mixture.py`
- `src/epcsaft/model/options.py`
- `tests/support/equilibrium_cases.py`
- `tests/api/frontend/test_equilibrium.py`

Substeps:

1. Resolve the public mixture species order before building any native payload.
2. Store the composition vector in that same species order.
3. Define the default feed total `F` for mole-fraction inputs.
4. Preserve enough diagnostics to reconstruct `z_i F`.
5. Declare whether a route uses mole fractions, phase compositions, or
   extensive feed amounts at the public seam.
6. Declare whether pressure is fixed, solved, or only used as a boundary
   continuation parameter.
7. Declare whether temperature is fixed, solved, or only used as a boundary
   continuation parameter.
8. Ensure all unit conversions happen before native dispatch and are reported
   when a conversion is supported.
9. Reject unknown unit bases loudly. Do not infer hidden units.
10. Record the thermodynamic input payload in route diagnostics so a failed run
    can be reproduced without reading UI-level objects.

Acceptance checks:

- A native diagnostic payload can identify the species order, feed basis, `T`,
  `P`, and composition role used for the solve.
- Public tests prove mismatched lengths and nonfinite values stop before
  native dispatch.

Stop conditions:

- A route can build a native request without a declared species order.
- Feed amount basis is implicit in solver code.
- Temperature or pressure meaning changes between public and native layers.

## Stage 3 - Species, Phase Eligibility, And Family Classification

Purpose: classify the pretreated thermodynamic problem without leaking
roadmap labels into runtime keys.

Primary output:

- `input_classification` diagnostics covering neutral, ionic, associating,
  reactive, phase-eligible, transferable, and fixed species.

References:

- `src/epcsaft/native/equilibrium/core/activation_matrix.h`
- `src/epcsaft/native/equilibrium/core/activation_plan.h`
- `src/epcsaft/native/equilibrium/core/selector_core.h`
- `src/epcsaft/native/equilibrium/core/selector_core.cpp`
- `src/epcsaft/native/equilibrium/core/activated_equilibrium_nlp.cpp`
- `tests/native/contracts/test_equilibrium_activation_capabilities.py`
- `tests/native/equilibrium/diagnostics/test_route_metadata_contracts.py`

Substeps:

1. Define classification fields for neutral species indices.
2. Define classification fields for ionic species indices and charges.
3. Define classification fields for associating species and active site
   schemes.
4. Define classification fields for reactive species and active reaction
   basis when present.
5. Define phase eligibility per species and per possible phase.
6. Define transfer eligibility separately from phase eligibility.
7. Define fixed or constrained species separately from transferable species.
8. Classify a problem as neutral only when no charge-balance, electrochemical,
   association mass-action, or reaction-affinity equations are active.
9. Classify a problem as associating when active parameter data requires
   association site fractions or association mass-action consistency.
10. Classify a problem as electrolyte when charged true species, salt basis,
    Debye-Huckel, Born, charge-neutral reduced variables, or electrochemical
    transfer conditions are active.
11. Classify a problem as reactive when reaction stoichiometry, reaction
    extents, standard-state convention, or reaction-affinity constraints are
    active.
12. Keep current native admission keys as implementation details.
13. Report selector-ineligible mixtures before any Ipopt dispatch.
14. Add negative tests for associating, electrolyte, and reactive inputs that
    try to enter current neutral-only generalized paths.

Acceptance checks:

- Route metadata exposes classification fields.
- Unsupported families fail before optimizer construction.
- Capability evidence separates current public utilities from GFPE family
  rows.

Stop conditions:

- Association, electrolyte, or reactive markers are ignored to force a neutral
  route.
- Runtime keys are renamed only to match roadmap labels.
- Selector-ineligible failures are discovered only after optimizer execution.

## Stage 4 - Parameter And EOS Contribution Pretreatment

Purpose: prove that the active route has the parameter families and EOS
contributions required by its classified family.

Primary output:

- `parameter_readiness` diagnostics covering required parameter families,
  active residual contributions, provenance, and exact-derivative readiness.

References:

- `docs/latex/equations.tex`
- `docs/equations_registry.yaml`
- `src/epcsaft/model/parameters.py`
- `src/epcsaft/model/options.py`
- `src/epcsaft/frontend/mixture.py`
- `src/epcsaft/native/`
- `docs/roadmaps/explicit_association_closure_for_pcsaft.md`
- `tests/native/contracts/test_equation_registry.py`

Substeps:

1. Treat `ParameterSet` and `ParameterSet.to_runtime_dict()` as the public to
   native parameter boundary.
2. For neutral PE, require pure component PC-SAFT parameters:
   segment number, segment diameter, dispersion energy, and any molecular data
   needed by density or reporting.
3. For neutral binary or multicomponent PE, require binary interaction data or
   an explicitly source-backed zero-interaction convention.
4. For associating PE, require association scheme, site list, association
   energy, association volume, and cross-association rule.
5. For electrolyte PE, require species charges, ion sizes or solvated
   diameters, ion-solvent dispersion data, Debye-Huckel settings, Born
   settings, relative-permittivity model, SSM model, and DS model when active.
6. Record active residual contribution families:
   hard-chain, dispersion, association, Debye-Huckel, Born, SSM, DS, and any
   dielectric contribution.
7. Record parameter provenance by source file, paper, table, figure, units,
   converted units, and fitted domain when available.
8. Reject missing required parameter families in pretreatment.
9. Keep direct dictionaries acceptable only for small synthetic tests, not
   source-backed GFPE proof cases.
10. Route durable equation claims through `docs/latex/equations.tex` or a
    generated registry view.
11. Keep reduced explicit association closures diagnostic unless a route is
    explicitly approximate.
12. Block electrolyte PE validation until the Born SSM+DS master path has exact
    Hessian support.

Acceptance checks:

- Route diagnostics list active residual families and parameter readiness.
- Missing required parameter families fail before solver dispatch.
- Source-backed benchmark fixtures record parameter provenance.
- Equation registry tests stay synchronized.

Stop conditions:

- A GFPE proof case uses placeholder parameter data.
- A benchmark fixture lacks source-backed parameter provenance.
- Electrolyte validation bypasses the Born SSM+DS exact-Hessian gate.

## Stage 5 - Physical Basis, Lifts, And Variable Layout

Purpose: define the true-species physical state that every route must evaluate
even if the solver uses reduced coordinates.

Primary output:

- `variable_layout` diagnostics covering physical variable order, phase block
  boundaries, lifts from reduced coordinates, and result back-lifts.

References:

- `src/epcsaft/native/equilibrium/core/variable_layout.h`
- `src/epcsaft/native/equilibrium/core/variable_layout.cpp`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.h`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- `src/epcsaft/native/equilibrium/core/nlp_problem.h`
- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`

Substeps:

1. Define the physical PE variable vector:

   ```text
   x_phys = [n_{1,1}, ..., n_{Nc,1}, V_1, ..., n_{1,Np}, ..., V_Np]
   ```

2. Store species order, phase order, and variable block boundaries in route
   metadata.
3. Provide accessors for phase amount blocks.
4. Provide accessors for phase volume entries.
5. Provide accessors for phase composition, total phase amount, density, and
   phase fraction.
6. Define the material-balance map once:

   ```text
   b_i(n) = sum_a n_{i,a} - z_i F
   ```

7. Define the phase-pressure map once:

   ```text
   p_a(n_a, V_a) = P_eos(T, V_a, n_a) - P_spec
   ```

8. Define transferable-potential residuals only for species eligible to
   transfer across the selected phase pair.
9. For associating routes, choose one production architecture before proof:
   lifted association-site variables with mass-action constraints, or complete
   implicit association sensitivities.
10. For electrolyte routes, define charge-neutral reduced coordinates and a
    deterministic lift into true species by phase.
11. For reactive extensions, define reaction coordinates or element/moiety
    coordinates and a deterministic lift into true species.
12. Record every lift and back-lift equation before coding a route that uses
    reduced coordinates.
13. Add variable-layout tests for species count, phase count, volume positions,
    phase block slicing, and lift consistency.

Acceptance checks:

- Route metadata can reconstruct every physical block from a solver vector.
- Constraint residual tests use the same physical basis as the objective.
- Reduced-coordinate routes expose their true-species lift.

Stop conditions:

- Composition variables and amount variables are mixed without a declared
  lift.
- Charge-neutral reduced variables lack a true-species lift.
- Association state variables are hidden from derivative or diagnostic
  contracts.

## Stage 6 - Bounds, Scaling, Variable Transform, And Domain Diagnostics

Purpose: make domain safety a declared route contract before any family is
expanded.

Primary output:

- `domain_contract` diagnostics covering bounds, scaling, smooth transforms,
  Ipopt barrier ownership, and domain margins.

References:

- `src/epcsaft/native/equilibrium/core/nlp_problem.h`
- `src/epcsaft/native/equilibrium/core/second_order.h`
- `src/epcsaft/native/equilibrium/core/variable_transform.h`
- `src/epcsaft/native/equilibrium/solvers/ipopt_adapter.cpp`
- `tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py`
- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`

Substeps:

1. Require variable lower and upper bounds for every route.
2. Require constraint lower and upper bounds for every route.
3. Define amount floors.
4. Define phase-volume lower and upper bounds.
5. Define density or packing-fraction margins where the EOS requires them.
6. Define composition floors for trace components.
7. Define phase-fraction noncollapse limits.
8. For associating routes, define site-fraction or association-state bounds.
9. For electrolyte routes, define charge-neutrality constraints and
   reduced-basis bounds before electrochemical residuals are evaluated.
10. Define a reusable `VariableTransform` concept:

    ```text
    solver_to_physical(u) -> x
    dx_du(u)
    d2x_du2(u)
    ```

11. Keep route equations in physical variables.
12. Put coordinate maps and chain-rule derivative assembly in the transform
    wrapper.
13. Use smooth maps for positivity, trace components, simplex-like
    compositions, phase volumes, and reduced electrolyte variables.
14. Define objective scaling.
15. Define amount scaling.
16. Define volume scaling.
17. Define pressure-residual scaling.
18. Define material-balance residual scaling.
19. Define chemical-potential, fugacity, or electrochemical residual scaling.
20. Define transform-coordinate scaling.
21. Use Ipopt internal barrier handling for declared bounds and constraints.
22. Do not modify `Phi` with permanent custom barrier terms.
23. Report margins to amount floors, volume bounds, density bounds,
    packing-fraction limits, composition floors, charge-balance constraints,
    and transform saturation thresholds.
24. Add tests that assert scaling and domain-margin metadata exist for admitted
    GFPE routes.

Acceptance checks:

- `NlpProblem` exposes bounds and scaling for every admitted route.
- Ipopt adapter tests prove declared bounds and constraints are transferred.
- The native `VariableTransform` smoke proves `solver_to_physical`,
  `dx_du`, `d2x_du2`, and second-order chain-rule assembly for identity and
  positive-log maps.
- Diagnostics expose domain margins without silent clipping.

Stop conditions:

- A route relies on hidden clipping to stay inside the EOS domain.
- The thermodynamic objective is permanently changed for domain safety.
- A transform changes variables without exact chain-rule derivative coverage.

## Stage 7 - Seed, Candidate, And Stability Pretreatment

Purpose: keep initialization support separate from generalized
phase-discovery evidence.

Primary output:

- `seed_and_stability` diagnostics covering density roots, deterministic
  candidates, TPD estimates, candidate ranking, mass-balance feasibility, and
  postsolve stability checks.

References:

- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- `docs/algorithms.md`
- `docs/latex/algorithms.tex`
- `tests/native/equilibrium/results/test_neutral_vle_reference_values.py`
- `tests/native/equilibrium/results/test_neutral_lle_reference_values.py`
- `tests/native/equilibrium/diagnostics/test_selector_core_contracts.py`

Substeps:

1. Keep density roots and single-phase state solves as state evaluation and
   seed-generation tools.
2. Keep deterministic neutral TPD/candidate screening as seed and
   certification support.
3. Name deterministic candidate screening exactly as deterministic screening,
   not HELD.
4. Store every generated candidate with composition, phase kind, density,
   volume, seed source, TPD estimate, pressure residual estimate, and
   feasibility status.
5. Deduplicate candidates with declared composition and density tolerances.
6. Rank candidates deterministically for a fixed input problem.
7. Run candidate mass-balance feasibility before final phase-set assembly.
8. Preserve instability diagnostics even when a candidate is rejected for
   mass-balance infeasibility.
9. Record final Ipopt start source:
   user input, deterministic screening, continuation, boundary workflow, or
   benchmark fixture.
10. Add postsolve stability diagnostics after final Ipopt solves.
11. Keep seed-generation success distinct from route acceptance.
12. Keep all HELD status fields empty or planned until Stage 9 supplies
    executable HELD evidence.

Acceptance checks:

- Diagnostics identify candidate source, rank, feasibility, and selection.
- Tests reject any doc or registry language that calls deterministic screening
  full HELD.
- Current utility routes retain deterministic support without generalized
  production claims.

Stop conditions:

- Optimizer success is accepted without postsolve stability checks.
- Candidate generation is treated as phase-set completeness.
- Seed failure is hidden behind a generic solver failure.

## Stage 8 - Shared NLP And Ipopt Infrastructure Gate

Purpose: make the optimizer seam strong enough for all GFPE families before
new family behavior expands.

Primary output:

- A route-owned `NlpProblem` contract with exact derivatives, sparse
  structures, bounds, scaling, transform policy, and diagnostics.
- A complete Ipopt numerics gate that is finished before Stage 9 starts any
  real-mixture HELD proof case.

References:

- `src/epcsaft/native/equilibrium/core/nlp_problem.h`
- `src/epcsaft/native/equilibrium/core/nlp_problem.cpp`
- `src/epcsaft/native/equilibrium/core/second_order.h`
- `src/epcsaft/native/equilibrium/solvers/ipopt_adapter.h`
- `src/epcsaft/native/equilibrium/solvers/ipopt_adapter.cpp`
- `tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py`
- `scripts/dev/run_ipopt_exact_hessian_proofs.py`

Substeps:

1. Treat `NlpProblem` as the route-owned contract for objective, gradient,
   constraints, Jacobian, Hessian, bounds, scaling, and diagnostics.
2. Require fixed sparse Jacobian ordering:

   ```text
   rows[k], cols[k], values[k]
   ```

   The same index `k` must describe the same nonzero for every evaluation.

3. Require sparse Hessian ordering and values for the Lagrangian Hessian.
4. Require exact objective gradients for admitted GFPE routes.
5. Require exact constraint Jacobians for admitted GFPE routes.
6. Require exact Lagrangian Hessians before production exposure unless the
   route is internal diagnostic only.
7. Record derivative backend metadata for every active objective and
   constraint block.
8. Record any missing exact derivative block as a hard admission blocker.
9. Keep Ipopt option transfer in the adapter.
10. Keep thermodynamic residual equations in route problems.
11. Pass route-owned bounds and constraints to Ipopt.
12. Pass route-owned scaling to Ipopt or to the route-owned scaling adapter.
13. Keep Ipopt on user scaling for GFPE routes; do not depend on automatic
    scaling as the production contract.
14. Define nondimensional or reference-scale residual conventions for every
    material, pressure, phase-equilibrium, charge, and reaction residual row.
15. Report scaling-quality diagnostics:
    objective scale, min/max variable scale, min/max constraint scale,
    variable-scale ratio, constraint-scale ratio, scaled constraint violation,
    scaled stationarity, and bound-complementarity norms.
16. Report active-bound and barrier diagnostics:
    lower-bound count, upper-bound count, total active variable-bound count,
    final barrier parameter, restoration-phase observation, final and maximum
    regularization size, and maximum step trial count.
17. Treat scaled numerical acceptance as a separate gate from physical
    postsolve acceptance.
18. Add Ipopt option profiles before Stage 9 real-mixture work:
    `proof`, `continuation_trace`, `held_refinement`, and `diagnostic`.
19. Require exact Hessian mode for all production profiles; keep limited-memory
    Hessian use diagnostic-only through the `profile_exact_hessian_gate`
    diagnostic.
20. Record the requested and selected linear solver for every route solve.
21. Record bound-push and bound-fraction values used by the profile or caller.
22. Preserve continuation starts with primal variables, bound multipliers, and
    constraint multipliers.
23. Add tests for objective value, gradient size, constraint size, Jacobian
    structure size, Jacobian value size, fixed sparse ordering, Hessian
    nonzero count, bounds size, scaling size, and diagnostic payload shape.
24. Add failure tests for mismatched sparse structure and values.
25. Add scaling-quality tests that assert actual scale magnitudes and scaled
    residual norms, not only vector sizes.
26. Add exact-Hessian proof scripts for active route families before registry
    promotion.

Acceptance checks:

- Focused Ipopt adapter contract tests pass.
- A route cannot be admitted when sparse structure and value vectors diverge.
- Exact derivative metadata appears in route diagnostics and capability
  evidence.
- Ipopt diagnostics report user-scaling, option profile, scaled numerical
  acceptance, active-bound pattern, barrier behavior, regularization, and
  linear-solver selection.
- Stage 9 cannot use real-mixture HELD proof cases until the Stage 8 Ipopt
  scaling and numerics contract is present in tests.

Stop conditions:

- A GFPE route bypasses `NlpProblem`.
- Ipopt adapter code owns thermodynamic equations.
- Missing exact Hessian coverage is treated as production-ready.
- A real-mixture Stage 9 proof starts while scaling quality, scaled numerical
  acceptance, barrier diagnostics, or option-profile behavior are untested.

## Stage 9 - Continuous TPD And HELD Stage Ladder

Purpose: replace seed-only deterministic screening with the staged
phase-discovery evidence required before source-backed neutral proof,
boundary workflows, or generalized GFPE admission.

Primary output:

- HELD-stage diagnostics that distinguish continuous TPD, Stage I stability,
  Stage II dual discovery, and Stage III primal refinement.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/algorithms.md`
- `docs/latex/algorithms.tex`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- `tests/native/contracts/test_generalized_activation_matrix_registry.py`
- `tests/native/equilibrium/diagnostics/test_selector_core_contracts.py`

Substeps:

1. Add continuous TPD minimization in volume-composition space.
2. Report TPD objective, trial composition, trial volume or density, local
   status, start source, and final residuals.
3. Add HELD Stage I stability testing with multiple starts.
4. Report Stage I failure modes separately from instability proof.
5. Treat any continuous TPD iteration-limit result as incomplete Stage I
   evidence, regardless of whether another start found a negative TPD value.
6. Add HELD Stage II dual cutting-plane phase discovery.
7. Report Stage II upper bounds, lower bounds, candidate phases, and stopping
   criteria.
8. Store Stage II candidate phases with replayable route-assembly metadata.
9. Use the amount-volume Ipopt NLP as HELD Stage III primal refinement.
10. Record the relation between Stage II bounds and Stage III refined objective.
    Stage III evidence requires Ipopt `success` and `solve_succeeded`.
    Acceptable-level status, a finite-variable postsolve with
    `tiny_step_detected`, iteration-limit, or another nonconverged Ipopt status
    remains diagnostic evidence only. The current neutral LLE proof fixture uses
    the route-owned `held_refinement` Ipopt profile; postsolve certification is
    not allowed to promote a nonconverged Ipopt attempt.
11. Check phase-set completeness:
    no missing lower-free-energy candidate, mass-balance feasibility, no
    duplicate phase, no collapsed phase, and no unexamined transferable species.
12. Keep deterministic screening available as a seed source.
13. Do not fill HELD status fields from deterministic screening.
14. Promote HELD stage status in the registry only after executable tests
    exist.
15. Keep live diagnosis narrow: use
    `uv run python run_pytest.py --equilibrium-debug -q -s <one equilibrium
    test node>`, not whole equilibrium result files. The debug lane must enable
    Ipopt iteration output, stored Ipopt iteration history, seed-attempt
    summaries, and continuous-TPD iteration traces. It cannot run pytest slices.
16. Use
    `uv run python scripts/validation/check_stage9_phase_discovery_evidence.py --json`
    as the cheap Stage 9 phase-discovery evidence snapshot. Add
    `--include-route-refinement` only when the current Stage III Ipopt
    route-refinement evidence is needed. Use
    `--debug --include-route-refinement --require-complete` when the question
    is "what is the TPD/Ipopt solver doing?", because that turns on
    continuous-TPD trace rows, route seed-attempt markers, Ipopt
    `print_level=5`, bounded Ipopt iteration-history diagnostics, and a
    nonzero exit if current Stage III convergence evidence is incomplete.

Acceptance checks:

- Tests distinguish deterministic screening, continuous TPD, HELD Stage I,
  HELD Stage II, and HELD Stage III.
- Registry rows can name which HELD gates are passed for each family.
- Production exposure remains false until the relevant HELD ladder is
  complete.
- Current neutral evidence reports deterministic screening as seed support,
  continuous TPD and HELD Stage I only when all continuous TPD starts converge,
  HELD Stage II as an executable candidate bound audit, and current Ipopt
  solves as Stage III refinement only after the route solve itself converges. A
  Stage II open candidate bound gap remains incomplete HELD evidence; the
  current neutral fixture closes only the finite candidate bound audit, not the
  full generalized dual-loop HELD admission gate.
- The executable Stage 9 checker reports any iteration-limit continuous TPD
  result as incomplete evidence, not as convergence.
- Public utility `flash` may keep deterministic TPD postsolve certification
  without requesting continuous TPD; that path is not Stage I evidence.
- Test wrappers reject broad native equilibrium result-file sweeps unless
  `--allow-long-equilibrium-tests` is explicitly set.

Stop conditions:

- Local TPD success is treated as global phase-discovery proof.
- Any iteration-limit continuous TPD solve is accepted as Stage I evidence.
- HELD status fields can be satisfied by deterministic screening.
- Phase-set completeness lacks mass-balance feasibility.

## Stage 10 - Neutral TP Flash Source-Backed Proof

Purpose: prove the first GFPE family on neutral TP flash before deriving
boundary workflows or widening to association/electrolytes.

Primary output:

- A source-backed `PE-Neutral TP Flash` proof case with full route diagnostics,
  exact derivative evidence, Stage 9 phase-discovery evidence, and registry
  evidence that still remains nonproduction until all GFPE promotion gates
  pass.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- `src/epcsaft/native/equilibrium/core/selector_core.cpp`
- `tests/native/equilibrium/results/test_neutral_vle_reference_values.py`
- `tests/native/equilibrium/diagnostics/test_native_route_diagnostics_contract.py`

Substeps:

1. Use `PE-Neutral TP Flash` as the first GFPE proof family.
2. Use the Stage 5 amount-volume physical variable model.
3. Use the Stage 6 bounds, scaling, and transform policy.
4. Use Stage 7 deterministic screening only as seed and certification support.
5. Use Stage 9 continuous TPD and HELD diagnostics as the phase-discovery
   evidence path for generalized proof.
6. Treat Pereira 2012 System III as a HELD/SAFT-VR reference, not the current
   executable ePC-SAFT proof fixture.
7. Use the hydrocarbon workbook-derived TP flash as the first executable
   Stage 10 fixture. The workbook supplies PC-SAFT component parameters,
   binary interactions, `T`, `P`, and liquid/vapor phase compositions at a
   bubble-point coexistence state. The Stage 10 fixture derives a TP-flash
   feed by equal-phase lever blending and expects 0.5 liquid / 0.5 vapor
   fractions.
   The Pereira source audit now lives under
   `data/reference/equilibrium_benchmarks/neutral_tp_flash/pereira_2012` as
   non-executable SAFT-VR evidence and records the published second-feed
   composition inconsistency. Its readiness files separate reported
   material-balance-feasible points from inferred feed-correction candidates.
   First produce the Stage 9 evidence payload with
   `uv run python scripts/validation/check_stage9_phase_discovery_evidence.py --json --include-route-refinement`,
   then pass it to the Stage 10 readiness gate with
   `uv run python scripts/validation/check_equilibrium_benchmark_readiness.py --json --stage9-evidence-json <payload>`.
   Use `--require-executable` only when promoting a case to proof evidence.
   The readiness gate reports every executable fixture field independently so
   missing PC/ePC parameters, binary interactions, normalized feed data,
   expected phase fractions, accepted model family, source path, tolerances, or
   Stage 9 evidence cannot be hidden behind a generic blocked status.
8. Record proof species, parameters, binary interactions, `T`, `P`, feed
   composition, expected phases, expected composition window, and source
   provenance.
   The registry source gate also requires expected phase count, expected phase
   compositions, expected phase fractions, accepted source model family, source
   path, and acceptance tolerances before any case can be marked as executable
   Stage 10 proof.
9. Evaluate the pressure-transformed Helmholtz objective:

   ```text
   Phi = sum_a A_a + P * sum_a V_a
   ```

10. Enforce or certify material balance for every species.
11. Enforce or certify phase pressure consistency.
12. Enforce or certify chemical-potential equality for transferable species.
13. Certify noncollapse through phase amount, phase fraction, composition
    distance, and density or volume margins.
14. Certify postsolve stability with Stage 9 phase-discovery diagnostics.
15. Certify exact derivatives for the active objective and constraints.
16. Store all proof evidence in tests and registry fields without marking
    generalized production exposure.
17. Run the Stage 10 proof with
    `uv run python scripts/validation/check_stage10_neutral_tp_flash_proof.py --stage9-evidence-json <payload> --require-proof`.
    Use `--debug --json` for convergence diagnosis so Ipopt `print_level=5`,
    any selected-path seed-attempt traces, and bounded iteration history are
    visible without corrupting the JSON proof payload. Tests must pass a Stage 9 evidence JSON
    fixture instead of generating Stage 9 evidence inside the Stage 10 test, so
    the test does not hide an extra continuous-TPD/Ipopt route solve.
18. Keep existing public `flash` behavior unchanged unless it is explicitly
    migrated through the same verified route and tests.

Acceptance checks:

- Neutral proof fixture exists, is source-backed, and is executable with the
  active ePC-SAFT model before being used as proof evidence.
- Stage 10 proof completion requires native Ipopt `success` and
  `solve_succeeded`; iteration-limit, acceptable-point, tiny-step, or other
  nonconverged statuses remain blockers.
- Pereira is not used as ePC-SAFT proof evidence unless SAFT-VR support or a
  source-backed ePC-SAFT reparameterization closes the model-family gap.
- Neutral TP flash diagnostics include material, pressure, potential,
  stability, derivative, and domain margins.
- Registry tests keep generalized neutral TP flash not production-exposed
  until HELD completion.

Stop conditions:

- The first neutral proof is synthetic.
- Pereira SAFT-VR parameters are treated as ePC-SAFT parameters.
- Production admission rests only on optimizer convergence.
- Current public utility success is used as generalized GFPE proof without
  GFPE gates.

## Stage 11 - Derived Boundary Workflows And Diagram Traces

Purpose: derive bubble, dew, cloud, and shadow workflows from the neutral GFPE
core after Stage 9 phase discovery and Stage 10 neutral proof are reliable.

Primary output:

- Derived boundary workflow contracts and `T-x` or `P-x` diagram trace
  diagnostics that reuse the shared GFPE core.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp`
- `src/epcsaft/equilibrium/workflows.py`
- `tests/api/frontend/test_equilibrium.py`
- `tests/native/contracts/test_equilibrium_benchmark_registry.py`

Substeps:

1. Keep bubble, dew, cloud, and shadow as derived subworkflows.
2. Do not add them as main family rows.
3. Implement each boundary workflow as a degree-of-freedom swap over the
   shared phase NLP.
4. For bubble point, fix liquid or feed composition and solve incipient vapor
   composition plus boundary `P` or `T`.
5. For dew point, fix vapor composition and solve incipient liquid composition
   plus boundary `P` or `T`.
6. For cloud point, fix parent liquid composition and solve incipient
   second-liquid composition plus boundary `P` or `T`.
7. For shadow point, report the incipient phase composition and volume matched
   to the cloud-point state.
8. Use the Stage 10 source-backed ePC-SAFT-compatible neutral mixture as the
   shared boundary mixture. The current executable fixture is the hydrocarbon
   workbook PC-SAFT phase split, not a Pereira-derived fixture.
9. Keep Pereira as HELD/SAFT-VR literature context unless model parity or a
   source-backed ePC-SAFT reparameterization exists.
10. Do not invent a boundary fixture.
11. Do not add VLLE-specific tests in this stage.
12. Keep routine validation contract-only unless an explicitly named single
    boundary route point is requested. A checker or test must not solve all
    bubble/dew `T-x` and `P-x` points by default.
13. Generate `T-x` and `P-x` traces through continuation only behind an
    explicit sweep opt-in. Per-point diagnostics must include route, fixed
    composition role, seed source, seed-attempt status, Ipopt status, Ipopt
    iteration history, final residuals, and skipped-point reason.
14. Require strict route convergence before Stage 11 completion:
    `solver_status == success`, `application_status == solve_succeeded`, and
    no selected seed attempt ending in `max_iterations_exceeded`. Acceptable
    points, tiny steps, feasible points, postsolve-accepted finite variables,
    or any iteration-limit seed path are diagnostic evidence only.
15. Preserve current public bubble/dew route behavior while generalized
    derived-workflow tests are added.

Acceptance checks:

- Registry tests prove bubble/dew/cloud/shadow are derived subworkflows.
- Boundary tests prove fixed/free variable contracts.
- The Stage 11 checker rejects implicit route sweeps and exposes Ipopt
  `print_level=5` output plus stored iteration history when a single debug
  route point is requested.
- Diagram tests prove trace generation and diagnostic reporting without
  treating nonconverged Ipopt paths as complete evidence.

Stop conditions:

- A boundary workflow is promoted to a main family row.
- Cloud/shadow work becomes a VLLE proof.
- Boundary workflows duplicate a separate thermodynamic core instead of using
  the shared GFPE route.
- A boundary point with `acceptable_point`, `tiny_step_detected`,
  `feasible_point_found`, or `max_iterations_exceeded` is called Stage 11
  complete.
- Routine validation solves a multi-point boundary route sweep without an
  explicit sweep opt-in.

## Stage 12 - Generalized Phase-Set And Multiphase PE

Purpose: extend GFPE from selected two-phase solves to unknown phase count and
phase-set certification.

Primary output:

- A generalized phase-set route contract that no longer assumes exactly two
  phases after phase discovery.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `src/epcsaft/native/equilibrium/core/variable_layout.h`
- `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp`
- future generalized phase-set route owner created after Stage 9

Substeps:

1. Define a phase-set data structure with phase count, phase kinds, candidate
   sources, amounts, volumes, compositions, objective value, and status.
2. Allow more than two candidate phases after HELD Stage II discovery.
3. Assemble material-balance feasibility for arbitrary candidate phase sets.
4. Select candidate phase sets by feasibility, thermodynamic objective, and
   phase-set completeness diagnostics.
5. Refine candidate phase sets with the shared amount-volume NLP.
6. Reject duplicate phases.
7. Reject collapsed phases.
8. Certify every accepted phase against continuous TPD or HELD-discovered
   missing phases.
9. Replay representative neutral, associating, and electrolyte cases only
   after each base family has source-backed proof.
10. Keep `PE-Generalized Multiphase` not production-exposed until phase-count
    independence is tested.

Acceptance checks:

- Tests fail if a lower-free-energy feasible phase set is omitted.
- Diagnostics report phase count, phase kinds, feasibility, and completeness.
- No generalized path assumes exactly two phases after discovery.

Stop conditions:

- Multiphase support is only repeated two-phase calls.
- Phase-count assumptions remain hidden in variable layout or diagnostics.
- Representative cases are replayed before their base family proof is stable.

## Stage 13 - Associating GFPE Pretreatment And Proof

Purpose: admit associating phase equilibrium through the GFPE amount-volume
route, not through a narrow boundary-only route.

Primary output:

- Associating GFPE route admission with exact association derivative evidence
  and source-backed Gross/Sadowski proof data.

References:

- `docs/roadmaps/explicit_association_closure_for_pcsaft.md`
- `docs/adr/0004-associating-equilibrium-architecture.md`
- `docs/latex/equations.tex`
- `docs/algorithms.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`

Substeps:

1. Choose the production association architecture before implementation.
2. Option A: add lifted association-site variables and mass-action constraints.
3. Option B: use complete implicit association sensitivities.
4. For lifted variables, add site-fraction variables to the physical route
   layout.
5. For lifted variables, add association mass-action equations to the
   constraint set.
6. For implicit sensitivities, prove first and second derivative propagation
   through the association solve.
7. Keep reduced explicit association closures diagnostic unless a route is
   deliberately exposed as approximate.
8. Require exact gradient, Jacobian, and Lagrangian Hessian coverage for active
   association terms before production exposure.
9. Use Gross/Sadowski 2002 methanol/cyclohexane as the first associating proof.
10. Add a two-associating-component follow-on only after the first proof is
    stable and source-backed.
11. Reuse neutral GFPE bounds, scaling, transforms, stability, and HELD gates.
12. Add association-specific postsolve checks:
    site-fraction bounds, mass-action residuals, contribution activation, and
    derivative block coverage.
13. Keep selector-ineligible associating mixtures out of current neutral public
    utility routes until proof gates pass.

Acceptance checks:

- Associating proof fixture is source-backed and executable.
- Association derivative tests prove exact first and second derivative
  coverage for the chosen architecture.
- Registry rejects narrow associating boundary work as general associating PE
  proof.

Stop conditions:

- A single bubble-pressure proof is treated as associating TP flash validation.
- Explicit association diagnostics are silently used as exact production
  equations.
- Association variables are omitted from route metadata.

## Stage 14 - Electrolyte Pretreatment And Born SSM+DS Gate

Purpose: make electrolyte thermodynamics solver-ready before electrolyte PE is
validated.

Primary output:

- Electrolyte pretreatment records for true species, reduced electroneutral
  variables, contribution activation, Born SSM+DS derivative readiness, and
  electrochemical residual projection.

References:

- `docs/latex/equations.tex`
- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `analyses/paper_validation/2026_khudaida/`
- `scripts/dev/run_ipopt_exact_hessian_proofs.py`

Substeps:

1. Define true species for salts, ions, neutral solvents, complexes, and any
   phase-restricted species.
2. Define charges for every charged true species.
3. Define per-phase charge-balance constraints before building the NLP.
4. Define reduced electroneutral coordinates per phase.
5. Define a deterministic lift from reduced coordinates into true species
   amounts.
6. Define a back-lift for diagnostics and result reporting.
7. Project electrochemical potentials into the reduced electroneutral basis.
8. Compare transfer equilibrium only after projection.
9. Record active dielectric, Debye-Huckel, Born, SSM, and DS settings.
10. Make the Born SSM+DS path the master Born path.
11. Make simpler Born modes reduce from the master path.
12. Prove exact Hessian support for active Born SSM+DS phase blocks before
    electrolyte PE validation.
13. Add electrolyte domain diagnostics:
    charge-balance residuals, ionic-strength margins, concentration bounds,
    dielectric model domain, Born model domain, and projected-potential
    residuals.
14. Keep electrolyte PE blocked until reduced variables and Born exact Hessian
    evidence are in place.

Acceptance checks:

- Reduced electroneutral variable tests prove lift and back-lift consistency.
- Born SSM+DS exact-Hessian proof tests pass for active electrolyte blocks.
- Electrolyte diagnostics distinguish charge balance from transfer
  equilibrium.

Stop conditions:

- Raw ionic chemical potentials are compared without projection.
- Electrolyte validation runs before the Born SSM+DS exact-Hessian gate.
- Charge neutrality is enforced by hidden clipping instead of declared
  constraints or reduced variables.

## Stage 15 - Electrolyte GFPE And HELD2.0 Validation

Purpose: prove strong-electrolyte LLE/TP flash through electrolyte-specific
phase discovery and certification.

Primary output:

- Source-backed electrolyte GFPE validation using Khudaida first, with HELD2.0
  and Born SSM+DS exact-Hessian evidence.

References:

- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `analyses/paper_validation/2026_khudaida/`
- `docs/papers/` source material when a fixture is promoted
- `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- future electrolyte GFPE route tests

Substeps:

1. Add electrolyte TPD in the reduced electroneutral variable basis.
2. Add HELD2.0 phase discovery before electrolyte production readiness.
3. Use Khudaida 2026 electrolyte LLE as the first electrolyte validation
   target.
4. Treat Held 2014 Figure 6 as a follow-on after data, units, and conventions
   are source-backed locally.
5. Treat Ascani/Sadowski/Held 2022 as a lower-confidence follow-on until data
   and convention audit is complete.
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

Acceptance checks:

- Khudaida electrolyte fixture is executable with declared tolerances.
- Electrolyte validation reports charge, material, pressure, potential,
  stability, derivative, and domain diagnostics.
- Registry rows remain nonproduction until HELD2.0 and Born SSM+DS exact
  Hessian gates pass.

Stop conditions:

- Electrolyte LLE acceptance is based only on composition error.
- A downstream case-study metric is used as upstream package validation.
- Held or Ascani follow-ons are promoted without source-backed fixture data.

## Stage 16 - CE And CPE Interface Guards For GFPE

Purpose: keep GFPE from being boxed into a nonreactive design while avoiding
full CE/CPE implementation in this plan.

Primary output:

- Interface constraints showing how future CE/CPE can attach to GFPE without
  claiming reactive or combined equilibrium support now.

References:

- `docs/roadmaps/generalized_fluid_phase_equilibrium.md`
- `docs/latex/equations.tex`
- future CE/CPE roadmap files when created

Substeps:

1. Keep CE and CPE as placeholders in the GFPE registry.
2. Define the future species-basis interface:
   true species, elements or moieties, reaction stoichiometry, and reaction
   extents.
3. Define the future reaction-affinity residual:

   ```text
   A_r = sum_i nu_{r,i} * mu_i
   ```

4. Require a standard-state and reaction-constant convention before any CE
   proof.
5. Ensure GFPE variable layouts can later carry reaction variables or lifted
   true-species amounts.
6. Ensure electrolyte reduced variables can coexist with future reaction
   coordinates.
7. Define CPE as one simultaneous thermodynamic problem, not a staged phase
   solve plus a staged reaction solve accepted as final proof.
8. Keep homogeneous CE proof separate from CPE proof.
9. Keep CPE production blocked until PE and CE proof gates both exist.

Acceptance checks:

- GFPE docs state the CE/CPE boundary without claiming implementation.
- Variable-layout and route metadata design can represent future reaction
  variables.
- Registry tests keep CE and CPE placeholders not production-exposed.

Stop conditions:

- CE or CPE placeholders are used as capability claims.
- Reaction standard-state conventions are implicit.
- Staged PE plus staged CE is treated as simultaneous CPE proof.

## Stage 17 - Registry, Capability, And Benchmark Closure

Purpose: turn GFPE implementation evidence into public capability claims only
after the relevant proof gates pass.

Primary output:

- Registry rows, capability evidence, and benchmark fixtures that make exactly
  the claims proven by executable tests.

References:

- `docs/roadmaps/equilibrium_benchmark_registry.yaml`
- `src/epcsaft/runtime/capability_evidence.py`
- `tests/native/contracts/test_generalized_activation_matrix_registry.py`
- `tests/native/contracts/test_equilibrium_benchmark_registry.py`
- `tests/native/contracts/test_equilibrium_activation_capabilities.py`
- `tests/workflows/repo/test_workflow_entrypoints.py`

Substeps:

1. Promote a family row only when its stage-specific gates are executable and
   tested.
2. Keep benchmark cases PE-focused:
   source-backed ePC-SAFT-compatible neutral proof first for neutral, with
   Pereira retained as blocked SAFT-VR context; Gross/Sadowski first for
   associating; Khudaida first for electrolyte, then Held and Ascani as
   follow-ons.
3. Record evidence tier, fixture status, source path, active equations,
   derivative coverage, stability coverage, and postsolve certification status
   for each benchmark.
4. Keep `epcsaft.capabilities()` honest:
   current public utility routes are separate from generalized GFPE rows.
5. Preserve existing public route behavior when a GFPE family remains planned.
6. Add negative tests for stale source references, deleted narrow roadmap file
   references, and raw-response note citations.
7. Add positive tests for derived subworkflow placement after Stage 10 neutral
   TP flash proof.
8. Add positive tests for deterministic screening being named as deterministic
   screening, not HELD.
9. Add benchmark fixture tests only when source data and acceptance tolerances
   are present.
10. Before handoff, run focused registry and route contract tests in proportion
    to the edited surface.

Acceptance checks:

- Registry contract tests pass.
- Capability tests pass for edited capability evidence.
- Benchmark tests pass for admitted fixtures.
- Public docs and capability output make the same claims.
- No downstream-specific application metric is exposed as a package API.

Stop conditions:

- A registry row is promoted before proof gates pass.
- A capability claim cannot point to executable evidence.
- A downstream repository becomes the source of package route semantics.

## Dependency Chain

The GFPE dependency chain is:

```text
0 doctrine, registry, and scope lock
1 public request pretreatment
2 thermodynamic input basis pretreatment
3 species, phase eligibility, and family classification
4 parameter and EOS contribution pretreatment
5 physical basis, lifts, and variable layout
6 bounds, scaling, variable transform, and domain diagnostics
7 seed, candidate, and stability pretreatment
8 shared NLP and Ipopt infrastructure gate
9 continuous TPD and HELD stage ladder
10 neutral TP flash source-backed proof
11 derived boundary workflows and diagram traces
12 generalized phase-set and multiphase PE
13 associating GFPE pretreatment and proof
14 electrolyte pretreatment and Born SSM+DS gate
15 electrolyte GFPE and HELD2.0 validation
16 CE and CPE interface guards for GFPE
17 registry, capability, and benchmark closure
```

The earliest useful implementation slices are not new phase families. They are
pretreatment records, selector diagnostics, parameter readiness checks,
variable-layout contracts, bounds/scaling/transform contracts, seed and
candidate diagnostics, and sparse NLP derivative contracts. New family
admission should wait until those artifacts make the neutral GFPE proof
auditable.
