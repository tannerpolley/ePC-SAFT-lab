# Algorithm Index

This file is generated from `docs/latex/algorithms.tex` by `scripts/docs/sync_algorithm_registry.py`.
The LaTeX document remains the current source of truth; this Markdown view and `docs/algorithms_registry.yaml` stay aligned with it.

## Core Optimizer and Adapter Algorithms

### `native_nlp_problem_contract`
- Family: Core optimizer adapter
- Status: Implemented
- Public API: Private native contract used by package equilibrium routes
- Backend: Native C++
- Dependency: None
- Derivative backend: Route-provided exact gradient and Jacobian callbacks
- Solver role: Shared interface for Ipopt-owned constrained NLP routes
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/nlp_problem.h
- Validation: packages/epcsaft-equilibrium/tests/native/blocks/test_ipopt_adapter_contract.py
- Capability key: native_nlp_problem_contract
- Description: Defines the common native NLP shape consumed by the Ipopt adapter.
- Change note: Initial algorithm-registry entry for the shared native NLP contract.
- LaTeX: `docs/latex/algorithms.tex:17`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/nlp_problem.h:33` (class NlpProblem {)

The `NlpProblem` contract is the common native interface for objective,
constraint, Jacobian, bounds, scaling, and diagnostics payloads used by
Ipopt-backed production routes.

**LaTeX source**

```tex
The \texttt{NlpProblem} contract is the common native interface for objective,
constraint, Jacobian, bounds, scaling, and diagnostics payloads used by
Ipopt-backed production routes.
```


### `ipopt_tnlp_adapter`
- Family: Core optimizer adapter
- Status: Implemented
- Public API: Private native adapter reached through package equilibrium routes
- Backend: Native C++ Ipopt TNLP adapter
- Dependency: Ipopt
- Derivative backend: Route-provided exact gradient and Jacobian callbacks
- Solver role: Maps NlpProblem into Ipopt::TNLP and returns IpoptSolveResult
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/solvers/ipopt_adapter.cpp
- Validation: packages/epcsaft-equilibrium/tests/native/blocks/test_ipopt_adapter_contract.py
- Capability key: native_ipopt_equilibrium_nlp
- Description: Bridges the package NLP contract to Ipopt without owning route equations.
- Change note: Initial algorithm-registry entry for native Ipopt dispatch.
- LaTeX: `docs/latex/algorithms.tex:35`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/solvers/ipopt_adapter.cpp:517` (class IpoptTnlpAdapter final : public Ipopt::TNLP {)

The Ipopt adapter owns solver invocation, option transfer, status mapping, and
diagnostic capture for constrained NLP routes. Route-specific residuals and
Jacobians remain in their route problem owners.

**LaTeX source**

```tex
The Ipopt adapter owns solver invocation, option transfer, status mapping, and
diagnostic capture for constrained NLP routes. Route-specific residuals and
Jacobians remain in their route problem owners.
```


### `native_ceres_regression_adapter`
- Family: Core optimizer adapter
- Status: Implemented
- Public API: Private native adapter reached through regression helpers
- Backend: Native C++ Ceres least-squares adapter
- Dependency: Ceres
- Derivative backend: Native analytic or CppAD-backed residual Jacobians, route dependent
- Solver role: Maps regression residual/Jacobian evaluators into ceres::CostFunction and ceres::Problem
- Implementation owner: packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp
- Validation: packages/epcsaft-regression/tests/native/test_binary.py
- Capability key: native_ceres_regression
- Description: Shared adapter pattern for currently supported native Ceres regression routes.
- Change note: Initial algorithm-registry entry for native Ceres regression dispatch.
- LaTeX: `docs/latex/algorithms.tex:53`
- Code owners: `packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp:511` (ceres::Solver::Options ceres_regression_options_cpp(int max_num_iterations) {)

The Ceres adapter family owns native least-squares solve setup for supported
regression routes. It is separate from Ipopt and does not call Ipopt routes.

**LaTeX source**

```tex
The Ceres adapter family owns native least-squares solve setup for supported
regression routes. It is separate from Ipopt and does not call Ipopt routes.
```


## Equilibrium Algorithms

### `bubble_dew_ipopt`
- Family: Phase equilibrium
- Status: Implemented
- Public API: Equilibrium(mixture, route='bubble_pressure'|'dew_pressure', ...).solve()
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient, constraint Jacobian, and Hessian callbacks
- Solver role: Production selector-dispatched neutral bubble/dew constrained NLP route specs
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp
- Validation: packages/epcsaft-equilibrium/tests/api/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route; packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py; packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py
- Capability key: bubble_dew_derived_routes
- Description: Solves production neutral bubble/dew pressure route specs through the native selector core.
- Change note: Bubble/dew temperature contracts remain closed because retained inverse-workbook points are not live literature-backed production proof.
- LaTeX: `docs/latex/algorithms.tex:72`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp:907` (SelectorContract evaluate_selector_contract(), `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp:980` (epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult solve_selector_route(), `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp:3024` (m.def("_native_equilibrium_selector_contract", [](), `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp:3070` (m.def("_native_equilibrium_selector_route_result", [](), `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp:3969` (NeutralTwoPhaseEosRouteResult solve_pressure_route(), `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp:4123` (NeutralTwoPhaseEosRouteResult solve_temperature_route(), `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py:984` (def _solve_selector_route()

This entry exposes the trusted neutral bubble/dew pressure proof set through route specs
configured by `Equilibrium(mixture, route=..., ...)` and executed by
`solve()`. The selector core reads the
native activation matrix, admits neutral non-reactive non-electrolyte inputs,
and requires exact derivatives plus postsolve certification. Associating inputs
are restricted to the source-backed Gross/Sadowski 2002 Figures 2--9 proof
fixtures; this is not generalized associating phase-equilibrium admission.

**LaTeX source**

```tex
This entry exposes the trusted neutral bubble/dew pressure proof set through route specs
configured by \texttt{Equilibrium(mixture, route=..., ...)} and executed by
\texttt{solve()}. The selector core reads the
native activation matrix, admits neutral non-reactive non-electrolyte inputs,
and requires exact derivatives plus postsolve certification. Associating inputs
are restricted to the source-backed Gross/Sadowski 2002 Figures 2--9 proof
fixtures; this is not generalized associating phase-equilibrium admission.
```


### `neutral_tp_flash_ipopt`
- Family: Phase equilibrium
- Status: Internal component diagnostic; declared not exposed
- Public API: None; Equilibrium(mixture, route='flash', ...) is rejected before native dispatch
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient, constraint Jacobian, and Hessian callbacks
- Solver role: Internal neutral two-phase TP flash component diagnostics
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp
- Validation: scripts/validation/check_neutral_tp_flash_fixture.py; packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py
- Capability key: neutral_tp_flash
- Description: Retains neutral two-phase TP flash component diagnostics without public route admission.
- Change note: TP flash remains closed because the retained workbook fixture is not live literature-backed production proof.
- LaTeX: `docs/latex/algorithms.tex:94`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/routes/derived/bubble_dew.cpp:4282` (NeutralTwoPhaseEosRouteResult solve_flash_route()

This entry retains internal neutral two-phase TP flash component diagnostics
over the shared two-phase EOS constrained core. The public `flash`
route is rejected before native dispatch. Selector-owned seed generation,
residual closure, and postsolve certification remain implementation evidence,
but they do not replace a live literature-backed production proof.

**LaTeX source**

```tex
This entry retains internal neutral two-phase TP flash component diagnostics
over the shared two-phase EOS constrained core. The public \texttt{flash}
route is rejected before native dispatch. Selector-owned seed generation,
residual closure, and postsolve certification remain implementation evidence,
but they do not replace a live literature-backed production proof.
```


### `neutral_lle_ipopt`
- Family: Phase equilibrium
- Status: Internal validation; declared not exposed
- Public API: None; Equilibrium(mixture, route='lle', ...) is rejected before native dispatch
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient, constraint Jacobian, and Hessian callbacks
- Solver role: Internal neutral LLE route refinement and certification diagnostics
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/workflows.py; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/selector_core.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp
- Validation: scripts/validation/check_neutral_lle_showcase.py; packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py; packages/epcsaft-equilibrium/tests/contracts/test_activation_capabilities.py
- Capability key: neutral_lle
- Description: Retains source-backed neutral LLE refinement diagnostics without public route admission.
- Change note: Neutral LLE is closed because the sampled-candidate Stage II audit is not a global HELD proof.
- LaTeX: `docs/latex/algorithms.tex:114`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp:6454` (NeutralTwoPhaseEosRouteResult solve_activated_neutral_lle_eos_route()

This entry retains the source-backed neutral LLE refinement path as internal
validation. The generic two-phase EOS NLP uses liquid-liquid phase keys, exact
derivative callbacks, postsolve checks, and a phase-distance anti-collapse
gate. Those checks do not turn a finite sampled-candidate Stage II bound audit
into the global HELD proof required for production admission, so the public
`lle` route remains closed. Electrolyte and reactive LLE remain outside
this entry.

**LaTeX source**

```tex
This entry retains the source-backed neutral LLE refinement path as internal
validation. The generic two-phase EOS NLP uses liquid-liquid phase keys, exact
derivative callbacks, postsolve checks, and a phase-distance anti-collapse
gate. Those checks do not turn a finite sampled-candidate Stage II bound audit
into the global HELD proof required for production admission, so the public
\texttt{lle} route remains closed. Electrolyte and reactive LLE remain outside
this entry.
```


### `neutral_tpd_stability`
- Family: Phase discovery and certification
- Status: Internal utility support for neutral TP flash and neutral LLE; generalized admission requires global HELD proof
- Public API: Internal route-discovery and certification infrastructure only
- Backend: Native C++ equilibrium core
- Dependency: None
- Derivative backend: EOS/provider chemical-potential and free-energy derivatives as required by the selected trial problem
- Solver role: Neutral tangent-plane stability evaluator for phase discovery and postsolve certification
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h; docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md
- Validation: packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py; packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py; packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py
- Capability key: internal:neutral_tpd_stability
- Description: Defines neutral TPD stability diagnostics for internal TP-flash and LLE validation.
- Change note: Deterministic and sampled-candidate screening is not a global HELD proof and authorizes no public route by itself.
- LaTeX: `docs/latex/algorithms.tex:136`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp:1680` (void append_tpd_candidates_for_reference_block()

This algorithm evaluates neutral tangent-plane distance candidates for route
discovery and certification in the current neutral two-phase TP flash and
neutral LLE validation paths. It is not a public route and must not change
capability exposure by itself. Accepted multiphase results require more than a
per-phase local check: the phase set must be certified against missing
lower-free-energy candidates and mass-balance incompleteness.

**LaTeX source**

```tex
This algorithm evaluates neutral tangent-plane distance candidates for route
discovery and certification in the current neutral two-phase TP flash and
neutral LLE validation paths. It is not a public route and must not change
capability exposure by itself. Accepted multiphase results require more than a
per-phase local check: the phase set must be certified against missing
lower-free-energy candidates and mass-balance incompleteness.
```


### `neutral_continuous_tpd_minimization`
- Family: Phase discovery and certification
- Status: Implemented for neutral volume-composition TPD refinement; generalized admission still requires the HELD Stage II dual loop
- Public API: Internal route-discovery and certification infrastructure only
- Backend: Native C++ equilibrium core
- Dependency: None
- Derivative backend: EOS/provider chemical-potential and free-energy derivatives through pressure-root phase-block evaluation
- Solver role: Refines deterministic TPD starts through continuous composition-space minimization with trial density/volume from the EOS pressure root
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.h
- Validation: packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py
- Capability key: internal:neutral_continuous_tpd_minimization
- Description: Adds continuous neutral TPD refinement diagnostics distinct from deterministic candidate screening.
- Change note: This is the Stage 9 continuous-TPD layer. It does not satisfy the HELD Stage II dual cutting-plane requirement by itself.
- LaTeX: `docs/latex/algorithms.tex:157`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp:1409` (NeutralTpdCandidate refine_neutral_tpd_candidate()

This algorithm starts from deterministic neutral TPD trial compositions and
performs a bounded coordinate search on the composition simplex. Each trial
composition is evaluated through the pressure-root phase-block path so the
diagnostics include trial composition, phase kind, density, molar volume,
TPD value, start source, iteration count, and convergence status.

**LaTeX source**

```tex
This algorithm starts from deterministic neutral TPD trial compositions and
performs a bounded coordinate search on the composition simplex. Each trial
composition is evaluated through the pressure-root phase-block path so the
diagnostics include trial composition, phase kind, density, molar volume,
TPD value, start source, iteration count, and convergence status.
```


### `neutral_held_stage_ladder_diagnostics`
- Family: Phase discovery and certification
- Status: Implemented as diagnostics for deterministic screening, continuous TPD, HELD Stage I, Stage II candidate bound-gap audit, and current-route Stage III refinement with an Ipopt solver-convergence gate
- Public API: Internal route-discovery and certification infrastructure only
- Backend: Native C++ equilibrium core
- Dependency: Neutral TPD stability, continuous TPD minimization, and Ipopt phase-amount/phase-volume routes
- Derivative backend: EOS/provider derivatives for TPD and exact route derivatives for Ipopt refinement
- Solver role: Reports which phase-discovery stages supplied evidence and prevents deterministic screening from being reported as full HELD
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp
- Validation: packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py
- Capability key: internal:neutral_held_stage_ladder_diagnostics
- Description: Exposes Stage 9 phase-discovery status fields for deterministic screening, continuous TPD, HELD Stage I, HELD Stage II, and HELD Stage III.
- Change note: Stage II now reports an executable candidate bound-gap audit; an open gap remains incomplete HELD evidence until the outer/inner dual loop converges. Stage III diagnostics require the current Ipopt route to report Ipopt success and solve_succeeded before postsolve certification can be counted.
- LaTeX: `docs/latex/algorithms.tex:177`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp:2332` (void finalize_stage9_phase_discovery()

This diagnostic layer makes the phase-discovery ladder auditable. Current
deterministic screening remains seed and certification support. Continuous TPD
and HELD Stage I can run from multiple starts, while Stage II reports a
candidate lower/upper bound audit and remains incomplete when the finite
sampled-candidate gap closes without a global outer/inner HELD proof. Current
Ipopt phase-amount/phase-volume solves are reported as
current-route Stage III refinement only when the Ipopt solve itself reports
success and solve_succeeded; acceptable-level status, finite variables, and
postsolve acceptance are diagnostics, not proof that Stage II or Stage III has
converged.
The internal neutral LLE refinement uses the `held_refinement` Ipopt profile so the
Stage III diagnostic records an actual converged route solve before postsolve
certification is evaluated.

**LaTeX source**

```tex
This diagnostic layer makes the phase-discovery ladder auditable. Current
deterministic screening remains seed and certification support. Continuous TPD
and HELD Stage I can run from multiple starts, while Stage II reports a
candidate lower/upper bound audit and remains incomplete when the finite
sampled-candidate gap closes without a global outer/inner HELD proof. Current
Ipopt phase-amount/phase-volume solves are reported as
current-route Stage III refinement only when the Ipopt solve itself reports
success and solve_succeeded; acceptable-level status, finite variables, and
postsolve acceptance are diagnostics, not proof that Stage II or Stage III has
converged.
The internal neutral LLE refinement uses the `held_refinement` Ipopt profile so the
Stage III diagnostic records an actual converged route solve before postsolve
certification is evaluated.
```


### `neutral_deterministic_phase_candidate_screening`
- Family: Phase discovery and certification
- Status: Internal utility support for neutral TP flash and neutral LLE; supplemented by continuous TPD and HELD-stage diagnostics
- Public API: Internal route-discovery infrastructure only
- Backend: Native C++ equilibrium core
- Dependency: None
- Derivative backend: EOS/provider derivatives for volume-composition trial phases
- Solver role: Deterministic neutral candidate generation, de-duplication, and seed construction
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h; docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md
- Validation: packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py; packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py; packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py
- Capability key: internal:neutral_deterministic_phase_candidate_screening
- Description: Adds deterministic neutral volume-composition candidate screening for internal TP-flash and LLE validation.
- Change note: Deterministic screening remains distinct from continuous TPD and must not be promoted as full HELD evidence.
- LaTeX: `docs/latex/algorithms.tex:205`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp:4947` (NeutralPhaseDiscoveryResult evaluate_neutral_tpd_phase_discovery()

This algorithm reduces dependence on user-supplied phase guesses by using
neutral TPD or volume-composition trial problems to generate deterministic
candidate phases. It still requires bounded seed policies, candidate ranking,
continuation, and postsolve certification. It is not full HELD and must not be
used as generalized production evidence by itself.

**LaTeX source**

```tex
This algorithm reduces dependence on user-supplied phase guesses by using
neutral TPD or volume-composition trial problems to generate deterministic
candidate phases. It still requires bounded seed policies, candidate ranking,
continuation, and postsolve certification. It is not full HELD and must not be
used as generalized production evidence by itself.
```


### `phase_candidate_mass_balance_selection`
- Family: Phase discovery and certification
- Status: Internal candidate-selection support for neutral TP flash and neutral LLE
- Public API: Internal route-discovery infrastructure only
- Backend: Native C++ equilibrium core
- Dependency: None
- Derivative backend: Not applicable for the first LP/active-set feasibility selector
- Solver role: Selects candidate phase sets whose phase fractions satisfy feed material balance
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp; docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md
- Validation: packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py; packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py
- Capability key: internal:phase_candidate_mass_balance_selection
- Description: Filters deterministic or TPD phase candidates by mass-balance feasibility before Ipopt route assembly.
- Change note: Mass-balance feasibility and a closed finite sampled-candidate bound are necessary diagnostics, not a global HELD proof or public admission.
- LaTeX: `docs/latex/algorithms.tex:225`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp:1875` (void select_two_phase_candidate_set()

This algorithm solves the small candidate phase-fraction feasibility problem
before final route assembly. A candidate set that cannot reconstruct the feed
composition is incomplete even if individual candidate phases look locally
stable. When several candidate pairs satisfy the feed within tolerance, the
selector keeps mass balance as the primary gate and uses the selected-pair TPD
bound as the tie-breaker so an arbitrary enumeration order cannot leave a
finite candidate bound gap open.

**LaTeX source**

```tex
This algorithm solves the small candidate phase-fraction feasibility problem
before final route assembly. A candidate set that cannot reconstruct the feed
composition is incomplete even if individual candidate phases look locally
stable. When several candidate pairs satisfy the feed within tolerance, the
selector keeps mass balance as the primary gate and uses the selected-pair TPD
bound as the tie-breaker so an arbitrary enumeration order cannot leave a
finite candidate bound gap open.
```


### `postsolve_tpd_certification`
- Family: Phase discovery and certification
- Status: Internal postsolve support for neutral TP flash and neutral LLE; generalized admission requires global HELD proof
- Public API: Internal postsolve certification infrastructure only
- Backend: Native C++ equilibrium core
- Dependency: None
- Derivative backend: EOS/provider derivatives required by the selected TPD backend
- Solver role: Converts finite optimizer outputs into production_accepted, unstable, metastable, or uncertified statuses
- Implementation owner: packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/register_bindings.cpp; docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md
- Validation: packages/epcsaft-equilibrium/tests/native/results/test_neutral_vle_reference_values.py; packages/epcsaft-equilibrium/tests/native/results/test_neutral_lle_reference_values.py; packages/epcsaft-equilibrium/tests/native/diagnostics/test_selector_core_contracts.py
- Capability key: internal:postsolve_tpd_certification
- Description: Adds phase-set stability certification after current neutral Ipopt solves.
- Change note: Establishes optimizer success as insufficient for public phase-equilibrium admission; current implementation remains internal TP-flash and LLE evidence.
- LaTeX: `docs/latex/algorithms.tex:247`
- Code owners: `packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/two_phase_eos_route.cpp:6067` (NeutralTwoPhaseEosPostsolve evaluate_neutral_two_phase_eos_postsolve()

This algorithm runs after an Ipopt route returns finite variables. It checks
stability, phase distinctness, candidate completeness, and route certification
blocks before assigning a production-accepted status.
That internal status label does not expose a public selector route.

**LaTeX source**

```tex
This algorithm runs after an Ipopt route returns finite variables. It checks
stability, phase distinctness, candidate completeness, and route certification
blocks before assigning a production-accepted status.
That internal status label does not expose a public selector route.
```


### `generalized_equilibrium_activation_registry`
- Family: Equilibrium registry ownership
- Status: Documentation-only
- Public API: Runtime exposure is owned only by the native activation descriptor
- Backend: Native activation descriptor plus separate M4 and M6 YAML registries
- Dependency: None
- Derivative backend: Exact derivatives are M4 admission gates, not M6 evidence activation
- Solver role: M4 records algorithm and local-proof gates; M6 records evidence; neither duplicates runtime exposure
- Implementation owner: docs/superpowers/milestones/M4-equilibrium/generalized-fluid-phase-equilibrium.md; docs/superpowers/milestones/M4-equilibrium/registries/equilibrium-algorithm-admission-registry.yaml; docs/superpowers/milestones/M6-validation/registries/equilibrium-evidence-registry.yaml; packages/epcsaft-equilibrium/src/epcsaft_equilibrium/native/equilibrium/core/activation_matrix.h
- Validation: tests/native/contracts/test_generalized_equilibrium_registry.py; tests/native/contracts/test_equilibrium_benchmark_registry.py
- Capability key: docs:generalized_equilibrium_activation_registry
- Description: Separates algorithm admission, validation evidence, and runtime activation ownership.
- Change note: M4 and M6 registries are non-activating; the native activation descriptor is the sole runtime route authority.
- LaTeX: `docs/latex/algorithms.tex:266`
- Code owners: Documentation-only or planned entry; no current owner expected.

The M4 equilibrium algorithm registry records descriptive family contracts,
local-proof readiness, and admission gates. The separate M6 evidence registry
records literature cases, commands, tolerances, fixtures, and evidence
maturity. Neither registry declares runtime exposure; the native activation
descriptor is the sole route authority. Current deterministic screening is not
full HELD, so generalized families remain incomplete until their source-faithful
algorithm and derivative gates pass.

**LaTeX source**

```tex
The M4 equilibrium algorithm registry records descriptive family contracts,
local-proof readiness, and admission gates. The separate M6 evidence registry
records literature cases, commands, tolerances, fixtures, and evidence
maturity. Neither registry declares runtime exposure; the native activation
descriptor is the sole route authority. Current deterministic screening is not
full HELD, so generalized families remain incomplete until their source-faithful
algorithm and derivative gates pass.
```


### `explicit_association_closure_diagnostics`
- Family: Association diagnostics
- Status: Planned
- Public API: Internal diagnostics or explicitly approximate experimental route only
- Backend: Native C++ EOS/state diagnostics
- Dependency: CppAD for exact derivatives of the approximate closure
- Derivative backend: CppAD explicit derivatives of approximate association closures
- Solver role: Seeds, diagnoses, or continues associating routes without claiming exact PC-SAFT association
- Implementation owner: docs/superpowers/specs/2026-05-23-m3-eos-explicit-association-closure-for-pcsaft.md; docs/latex/explicit_assocation.tex
- Validation: Planned explicit-vs-implicit association diagnostics against Gross/Sadowski 2002 EOS cases
- Capability key: planned:explicit_association_closure_diagnostics
- Description: Records explicit association closures as approximate Helmholtz diagnostics, not production exact association.
- Change note: Keeps explicit association closures out of production acceptance unless a route is deliberately exposed as approximate.
- LaTeX: `docs/latex/algorithms.tex:288`
- Code owners: Documentation-only or planned entry; no current owner expected.

This planned diagnostic family may use explicit algebraic association closures
for seed generation, continuation, and comparison against
`implicit_exact`. CppAD derivatives are exact for the approximate
closure only. They are not exact derivatives of the PC-SAFT mass-action
association model unless the closure satisfies the mass-action equations at the
same tolerance as the exact solve.

**LaTeX source**

```tex
This planned diagnostic family may use explicit algebraic association closures
for seed generation, continuation, and comparison against
\texttt{implicit_exact}. CppAD derivatives are exact for the approximate
closure only. They are not exact derivatives of the PC-SAFT mass-action
association model unless the closure satisfies the mass-action equations at the
same tolerance as the exact solve.
```


## Regression Algorithms

### `pure_neutral_ceres_regression`
- Family: Regression
- Status: Implemented
- Public API: Regression(mixture, ...).fit_pure_neutral(...)
- Backend: Native C++ Ceres regression
- Dependency: Ceres
- Derivative backend: Native residual Jacobian for supported target families
- Solver role: Native least-squares pure-neutral parameter regression
- Implementation owner: packages/epcsaft-regression/src/epcsaft_regression/core.py; packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp; packages/epcsaft-regression/src/epcsaft_regression/native/regression/module.cpp
- Validation: packages/epcsaft-regression/tests/api/test_regression.py::test_regression_hydrocarbon_anchor_routes_through_new_object_api
- Capability key: regression:pure_neutral
- Description: Fits currently supported pure-neutral parameter targets through native Ceres.
- Change note: Initial algorithm-registry entry for pure-neutral regression.
- LaTeX: `docs/latex/algorithms.tex:311`
- Code owners: `packages/epcsaft-regression/src/epcsaft_regression/core.py:2437` (def fit_pure_neutral(), `packages/epcsaft-regression/src/epcsaft_regression/core.py:2771` (def fit_pure_parameters(), `packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp:524` (class PureNeutralCeresCostFunction final : public ceres::CostFunction {)

This entry covers the implemented nonassociating pure-neutral native Ceres route
for `m`, `\sigma`, and `\epsilon/k_B`. It is not a production Ceres
optimizer for association-energy \verb|e_assoc| or association-volume
\verb|vol_a| targets until the association parameter-sensitivity work lands.

**LaTeX source**

```tex
This entry covers the implemented nonassociating pure-neutral native Ceres route
for \(m\), \(\sigma\), and \(\epsilon/k_B\). It is not a production Ceres
optimizer for association-energy \verb|e_assoc| or association-volume
\verb|vol_a| targets until the association parameter-sensitivity work lands.
```

**Rendered formulae**

$$
m
$$

$$
\sigma
$$

$$
\epsilon/k_B
$$


### `pure_ion_ceres_regression`
- Family: Regression
- Status: Implemented with caveat
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ceres regression
- Dependency: Ceres
- Derivative backend: CppAD implicit residual Jacobian for supported pure-ion targets
- Solver role: Native least-squares pure-ion parameter regression
- Implementation owner: packages/epcsaft-regression/src/epcsaft_regression/core.py; packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp; packages/epcsaft-regression/src/epcsaft_regression/native/regression/module.cpp
- Validation: packages/epcsaft-regression/tests/native/test_liquid_electrolyte.py
- Capability key: regression:pure_ion
- Description: Fits currently supported pure-ion and Born-related target sets through native Ceres.
- Change note: Initial algorithm-registry entry for pure-ion regression; caveat preserves current target-family limits.
- LaTeX: `docs/latex/algorithms.tex:330`
- Code owners: `packages/epcsaft-regression/src/epcsaft_regression/core.py:2819` (def fit_pure_ion(), `packages/epcsaft-regression/src/epcsaft_regression/core.py:3022` (def fit_liquid_electrolyte_parameters(), `packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp:1464` (class PureIonCeresCostFunction final : public ceres::CostFunction {)

This entry is limited to the currently implemented pure-ion target surface. It
does not claim support for association-affecting target kinds merely because the
native target-kind registry knows their labels.

**LaTeX source**

```tex
This entry is limited to the currently implemented pure-ion target surface. It
does not claim support for association-affecting target kinds merely because the
native target-kind registry knows their labels.
```


### `binary_kij_ceres_regression`
- Family: Regression
- Status: Implemented with caveat
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ceres regression
- Dependency: Ceres
- Derivative backend: CppAD-backed binary k_ij residual Jacobian
- Solver role: Native least-squares constant-k_ij binary regression
- Implementation owner: packages/epcsaft-regression/src/epcsaft_regression/core.py; packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp; packages/epcsaft-regression/src/epcsaft_regression/native/regression/module.cpp
- Validation: packages/epcsaft-regression/tests/native/test_binary.py
- Capability key: regression:binary_pair
- Description: Fits the currently implemented constant-k_ij binary parameter route through native Ceres.
- Change note: Initial algorithm-registry entry keeps l_ij and k_hb_ij out of the claim until implementation evidence exists.
- LaTeX: `docs/latex/algorithms.tex:348`
- Code owners: `packages/epcsaft-regression/src/epcsaft_regression/core.py:2848` (def fit_binary_parameters(), `packages/epcsaft-regression/src/epcsaft_regression/native/regression/ceres_regression.cpp:1601` (class BinaryKijCeresCostFunction final : public ceres::CostFunction {)

This entry intentionally does not claim native optimizer support for every
binary parameter family. It is not a production Ceres optimizer for `l_{ij}`
or `k^{hb}_{ij}`, and active-association `l_{ij}` remains pending until
derivative and optimizer evidence both exist.

**LaTeX source**

```tex
This entry intentionally does not claim native optimizer support for every
binary parameter family. It is not a production Ceres optimizer for \(l_{ij}\)
or \(k^{hb}_{ij}\), and active-association \(l_{ij}\) remains pending until
derivative and optimizer evidence both exist.
```

**Rendered formulae**

$$
l_{ij}
$$

$$
k^{hb}_{ij}
$$

$$
l_{ij}
$$
