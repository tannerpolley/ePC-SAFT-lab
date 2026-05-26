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
- Implementation owner: src/epcsaft/native/equilibrium/core/nlp_problem.h
- Validation: tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py
- Capability key: native_nlp_problem_contract
- Description: Defines the common native NLP shape consumed by the Ipopt adapter.
- Change note: Initial algorithm-registry entry for the shared native NLP contract.
- LaTeX: `docs/latex/algorithms.tex:17`
- Code owners: `src/epcsaft/native/equilibrium/core/nlp_problem.h:33` (class NlpProblem {)

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
- Implementation owner: src/epcsaft/native/equilibrium/solvers/ipopt_adapter.cpp
- Validation: tests/native/equilibrium/blocks/test_ipopt_adapter_contract.py
- Capability key: native_ipopt_equilibrium_nlp
- Description: Bridges the package NLP contract to Ipopt without owning route equations.
- Change note: Initial algorithm-registry entry for native Ipopt dispatch.
- LaTeX: `docs/latex/algorithms.tex:35`
- Code owners: `src/epcsaft/native/equilibrium/solvers/ipopt_adapter.cpp:325` (class IpoptTnlpAdapter final : public Ipopt::TNLP {)

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
- Implementation owner: src/epcsaft/native/regression/ceres_regression.cpp
- Validation: tests/native/regression/test_binary.py
- Capability key: native_ceres_regression
- Description: Shared adapter pattern for currently supported native Ceres regression routes.
- Change note: Initial algorithm-registry entry for native Ceres regression dispatch.
- LaTeX: `docs/latex/algorithms.tex:53`
- Code owners: `src/epcsaft/native/bindings/module.cpp:1040` (m.def("_fit_generic_native_ceres", &fit_generic_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:565` (ceres::Solver::Options ceres_regression_options_cpp(int max_num_iterations) {)

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
- Public API: Equilibrium(mixture, route='bubble_pressure'|'bubble_temperature'|'dew_pressure'|'dew_temperature', ...).solve()
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient, constraint Jacobian, and Hessian callbacks
- Solver role: Production selector-dispatched neutral bubble/dew constrained NLP route specs
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/core/selector_core.cpp; src/epcsaft/native/equilibrium/core/activation_matrix.h; src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp; src/epcsaft/native/equilibrium/register_bindings.cpp
- Validation: tests/api/frontend/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route; tests/native/equilibrium/diagnostics/test_selector_core_contracts.py; tests/native/contracts/test_equilibrium_activation_capabilities.py
- Capability key: bubble_dew_derived_routes
- Description: Solves production neutral bubble/dew pressure and temperature route specs through the native selector core.
- Change note: Neutral VLE selector expansion promotes bubble/dew pressure and temperature routes through the shared thermodynamic constrained core.
- LaTeX: `docs/latex/algorithms.tex:72`
- Code owners: `src/epcsaft/equilibrium/workflows.py:522` (def _solve_selector_route(), `src/epcsaft/native/equilibrium/core/selector_core.cpp:349` (SelectorContract evaluate_selector_contract(), `src/epcsaft/native/equilibrium/core/selector_core.cpp:403` (epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult solve_selector_route(), `src/epcsaft/native/equilibrium/register_bindings.cpp:827` (m.def("_native_equilibrium_selector_contract", [](), `src/epcsaft/native/equilibrium/register_bindings.cpp:877` (m.def("_native_equilibrium_selector_route_result", [](), `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp:2701` (NeutralTwoPhaseEosRouteResult solve_pressure_route(), `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp:2838` (NeutralTwoPhaseEosRouteResult solve_temperature_route()

This entry exposes the trusted neutral bubble/dew proof set through route specs
configured by `Equilibrium(mixture, route=..., ...)` and executed by
`solve()`. The selector core reads the
native activation matrix, admits only neutral non-reactive non-electrolyte
non-associating mixtures for the production contract, and requires exact
derivatives plus postsolve certification.

**LaTeX source**

```tex
This entry exposes the trusted neutral bubble/dew proof set through route specs
configured by \texttt{Equilibrium(mixture, route=..., ...)} and executed by
\texttt{solve()}. The selector core reads the
native activation matrix, admits only neutral non-reactive non-electrolyte
non-associating mixtures for the production contract, and requires exact
derivatives plus postsolve certification.
```


### `neutral_tp_flash_ipopt`
- Family: Phase equilibrium
- Status: Implemented
- Public API: Equilibrium(mixture, route='flash', ...).solve()
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient, constraint Jacobian, and Hessian callbacks
- Solver role: Production selector-dispatched neutral two-phase TP flash route spec
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/core/selector_core.cpp; src/epcsaft/native/equilibrium/core/activation_matrix.h; src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp; src/epcsaft/native/equilibrium/register_bindings.cpp
- Validation: tests/api/frontend/test_equilibrium.py::test_equilibrium_flash_recovers_shared_two_phase_hydrocarbon_point; tests/native/equilibrium/diagnostics/test_selector_core_contracts.py; tests/native/contracts/test_equilibrium_activation_capabilities.py
- Capability key: neutral_tp_flash
- Description: Solves certified neutral two-phase TP flash through the native selector core.
- Change note: Neutral VLE selector expansion exposes TP flash only after selector-owned seed generation, residual closure, and postsolve certification.
- LaTeX: `docs/latex/algorithms.tex:93`
- Code owners: `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp:2971` (NeutralTwoPhaseEosRouteResult solve_flash_route()

This entry exposes the trusted neutral two-phase TP flash proof through the
`flash` route spec configured by
`Equilibrium(mixture, route="flash", ...)` and executed by
`solve()`. Flash is a route spec over the same native
two-phase EOS constrained core as bubble and dew routes. The native
selector owns deterministic seed generation, activation checks, exact
derivative requirements, and postsolve certification. Gibbs/free-energy terms
may shape the NLP or seed ranking, but solver success alone is not the
acceptance criterion.

**LaTeX source**

```tex
This entry exposes the trusted neutral two-phase TP flash proof through the
\texttt{flash} route spec configured by
\texttt{Equilibrium(mixture, route="flash", ...)} and executed by
\texttt{solve()}. Flash is a route spec over the same native
two-phase EOS constrained core as bubble and dew routes. The native
selector owns deterministic seed generation, activation checks, exact
derivative requirements, and postsolve certification. Gibbs/free-energy terms
may shape the NLP or seed ranking, but solver success alone is not the
acceptance criterion.
```


### `neutral_lle_ipopt`
- Family: Phase equilibrium
- Status: Implemented
- Public API: Equilibrium(mixture, route='lle', ...).solve()
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient, constraint Jacobian, and Hessian callbacks
- Solver role: Production selector-dispatched neutral nonassociating LLE route spec
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/core/selector_core.cpp; src/epcsaft/native/equilibrium/core/activation_matrix.h; src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp; src/epcsaft/native/equilibrium/register_bindings.cpp
- Validation: tests/api/frontend/test_equilibrium.py::test_equilibrium_lle_route_returns_named_liquid_phase_helpers; tests/native/equilibrium/results/test_neutral_lle_reference_values.py; tests/native/contracts/test_equilibrium_activation_capabilities.py
- Capability key: neutral_lle
- Description: Solves certified neutral nonassociating LLE through the native selector core.
- Change note: Neutral LLE is production-exposed only for the current neutral nonassociating activation-row proof.
- LaTeX: `docs/latex/algorithms.tex:117`
- Code owners: `src/epcsaft/equilibrium/workflows.py:444` ("lle": _EquilibriumRouteSpec(), `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp:2151` (NeutralTwoPhaseEosRouteResult solve_activated_neutral_lle_eos_route()

This entry exposes the trusted neutral nonassociating LLE proof through the
`lle` route spec configured by
`Equilibrium(mixture, route="lle", ...)` and executed by
`solve()`. The route uses the activation-plan compiler and generic
two-phase EOS NLP with liquid-liquid phase keys, exact derivative callbacks,
postsolve certification, and a phase-distance anti-collapse gate. The
phase-distance row is not a thermodynamic equilibrium equation. Associating
LLE, electrolyte LLE, and reactive LLE remain out of scope for this entry.

**LaTeX source**

```tex
This entry exposes the trusted neutral nonassociating LLE proof through the
\texttt{lle} route spec configured by
\texttt{Equilibrium(mixture, route="lle", ...)} and executed by
\texttt{solve()}. The route uses the activation-plan compiler and generic
two-phase EOS NLP with liquid-liquid phase keys, exact derivative callbacks,
postsolve certification, and a phase-distance anti-collapse gate. The
phase-distance row is not a thermodynamic equilibrium equation. Associating
LLE, electrolyte LLE, and reactive LLE remain out of scope for this entry.
```


### `neutral_tpd_stability`
- Family: Phase discovery and certification
- Status: Implemented for PE-01 neutral TP flash and PE-03 neutral nonassociating LLE; planned for broader neutral multiphase rows
- Public API: Internal route-discovery and certification infrastructure only
- Backend: Native C++ equilibrium core
- Dependency: None
- Derivative backend: EOS/provider chemical-potential and free-energy derivatives as required by the selected trial problem
- Solver role: Neutral tangent-plane stability evaluator for phase discovery and postsolve certification
- Implementation owner: src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp; src/epcsaft/native/equilibrium/core/two_phase_eos_route.h; docs/roadmaps/generalized_fluid_phase_equilibrium.md
- Validation: tests/native/equilibrium/results/test_neutral_vle_reference_values.py; tests/native/equilibrium/results/test_neutral_lle_reference_values.py; tests/native/equilibrium/diagnostics/test_selector_core_contracts.py
- Capability key: internal:neutral_tpd_stability
- Description: Defines neutral TPD stability checks for current neutral TP flash and neutral nonassociating LLE acceptance.
- Change note: Current Stage 1 baseline for PE-01 and PE-03; broader neutral multiphase, associating, electrolyte, and reactive rows still require separate admission.
- LaTeX: `docs/latex/algorithms.tex:140`
- Code owners: `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp:422` (void append_tpd_candidates_for_reference_block()

This algorithm evaluates neutral tangent-plane distance candidates for route
discovery and certification in the current neutral two-phase TP flash and
neutral nonassociating LLE routes. It is not a public route and must not change
capability exposure by itself. Accepted multiphase results require more than a
per-phase local check: the phase set must be certified against missing
lower-free-energy candidates and mass-balance incompleteness.

**LaTeX source**

```tex
This algorithm evaluates neutral tangent-plane distance candidates for route
discovery and certification in the current neutral two-phase TP flash and
neutral nonassociating LLE routes. It is not a public route and must not change
capability exposure by itself. Accepted multiphase results require more than a
per-phase local check: the phase set must be certified against missing
lower-free-energy candidates and mass-balance incompleteness.
```


### `neutral_held_phase_discovery`
- Family: Phase discovery and certification
- Status: Implemented for PE-01 neutral TP flash and PE-03 neutral nonassociating LLE; planned for PE-04 neutral multiphase discovery
- Public API: Internal route-discovery infrastructure only
- Backend: Native C++ equilibrium core
- Dependency: None
- Derivative backend: EOS/provider derivatives for volume-composition trial phases
- Solver role: HELD-style neutral candidate generation, de-duplication, and seed construction
- Implementation owner: src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp; src/epcsaft/native/equilibrium/core/activation_matrix.h; docs/roadmaps/generalized_fluid_phase_equilibrium.md
- Validation: tests/native/equilibrium/results/test_neutral_vle_reference_values.py; tests/native/equilibrium/results/test_neutral_lle_reference_values.py; tests/native/equilibrium/diagnostics/test_selector_core_contracts.py
- Capability key: internal:neutral_held_phase_discovery
- Description: Adds HELD-style neutral volume-composition phase discovery for the current neutral TP flash and neutral nonassociating LLE activation rows.
- Change note: Current Stage 1 baseline for PE-01 and PE-03; PE-04 neutral multiphase discovery remains a future row.
- LaTeX: `docs/latex/algorithms.tex:161`
- Code owners: `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp:1760` (NeutralPhaseDiscoveryResult evaluate_neutral_tpd_phase_discovery()

This algorithm reduces dependence on user-supplied phase guesses by using
neutral TPD or volume-composition trial problems to generate deterministic
candidate phases. It still requires bounded seed policies, candidate ranking,
continuation, and postsolve certification; it is not a magic guess-free solver.

**LaTeX source**

```tex
This algorithm reduces dependence on user-supplied phase guesses by using
neutral TPD or volume-composition trial problems to generate deterministic
candidate phases. It still requires bounded seed policies, candidate ranking,
continuation, and postsolve certification; it is not a magic guess-free solver.
```


### `phase_candidate_mass_balance_selection`
- Family: Phase discovery and certification
- Status: Implemented for PE-01 neutral TP flash and PE-03 neutral nonassociating LLE; planned for PE-04 neutral multiphase discovery
- Public API: Internal route-discovery infrastructure only
- Backend: Native C++ equilibrium core
- Dependency: None
- Derivative backend: Not applicable for the first LP/active-set feasibility selector
- Solver role: Selects candidate phase sets whose phase fractions satisfy feed material balance
- Implementation owner: src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp; docs/roadmaps/generalized_fluid_phase_equilibrium.md
- Validation: tests/native/equilibrium/results/test_neutral_vle_reference_values.py; tests/native/equilibrium/results/test_neutral_lle_reference_values.py
- Capability key: internal:phase_candidate_mass_balance_selection
- Description: Filters HELD/TPD phase candidates by mass-balance feasibility before Ipopt route assembly.
- Change note: Current Stage 1 baseline prevents accepting locally stable but mass-balance-incomplete phase sets for PE-01 and PE-03.
- LaTeX: `docs/latex/algorithms.tex:180`
- Code owners: `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp:490` (void select_two_phase_candidate_set()

This algorithm solves the small candidate phase-fraction feasibility problem
before final route assembly. A candidate set that cannot reconstruct the feed
composition is incomplete even if individual candidate phases look locally
stable.

**LaTeX source**

```tex
This algorithm solves the small candidate phase-fraction feasibility problem
before final route assembly. A candidate set that cannot reconstruct the feed
composition is incomplete even if individual candidate phases look locally
stable.
```


### `postsolve_tpd_certification`
- Family: Phase discovery and certification
- Status: Implemented for PE-01 neutral TP flash and PE-03 neutral nonassociating LLE; planned for broader neutral multiphase rows
- Public API: Internal postsolve certification infrastructure only
- Backend: Native C++ equilibrium core
- Dependency: None
- Derivative backend: EOS/provider derivatives required by the selected TPD backend
- Solver role: Converts finite optimizer outputs into production_accepted, unstable, metastable, or uncertified statuses
- Implementation owner: src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp; src/epcsaft/native/equilibrium/register_bindings.cpp; docs/roadmaps/generalized_fluid_phase_equilibrium.md
- Validation: tests/native/equilibrium/results/test_neutral_vle_reference_values.py; tests/native/equilibrium/results/test_neutral_lle_reference_values.py; tests/native/equilibrium/diagnostics/test_selector_core_contracts.py
- Capability key: internal:postsolve_tpd_certification
- Description: Adds full phase-set stability certification after neutral Ipopt solves for PE-01 and PE-03.
- Change note: Establishes optimizer success as insufficient for generalized phase-equilibrium acceptance; current implementation is limited to neutral TP flash and neutral nonassociating LLE.
- LaTeX: `docs/latex/algorithms.tex:199`
- Code owners: `src/epcsaft/native/equilibrium/core/two_phase_eos_route.cpp:1913` (NeutralTwoPhaseEosPostsolve evaluate_neutral_two_phase_eos_postsolve()

This algorithm runs after an Ipopt route returns finite variables. It checks
stability, phase distinctness, candidate completeness, and route certification
blocks before assigning a production-accepted status.

**LaTeX source**

```tex
This algorithm runs after an Ipopt route returns finite variables. It checks
stability, phase distinctness, candidate completeness, and route certification
blocks before assigning a production-accepted status.
```


### `generalized_equilibrium_activation_registry`
- Family: Equilibrium activation policy
- Status: Documentation-only
- Public API: No public route exposure; registry controls future generalized admission
- Backend: Markdown and YAML registry
- Dependency: None
- Derivative backend: Exact derivatives required before production row exposure
- Solver role: Records PE/CE/CPE activation rows, proof cases, evidence tiers, and benchmark status
- Implementation owner: docs/roadmaps/generalized_fluid_phase_equilibrium.md; docs/roadmaps/equilibrium_benchmark_registry.yaml
- Validation: tests/native/contracts/test_generalized_activation_matrix_registry.py; tests/native/contracts/test_equilibrium_benchmark_registry.py
- Capability key: docs:generalized_equilibrium_activation_registry
- Description: Defines generalized phase-only, chemical-only, and combined phase-chemical activation matrices.
- Change note: Bubble/dew routes remain derived utilities outside the generalized matrices; every generalized row carries proof evidence.
- LaTeX: `docs/latex/algorithms.tex:217`
- Code owners: Documentation-only or planned entry; no current owner expected.

The generalized equilibrium activation registry records three admission
matrices: phase-only rows, chemical-only rows, and combined phase-chemical
rows. Bubble and dew pressure/temperature routes remain implemented and tested
as derived utility routes through the existing selector surface, but their
generic route keys are excluded from the generalized matrices. Every generalized
activation row must carry at least one proof case and evidence tier before it
can be used for future route admission.

**LaTeX source**

```tex
The generalized equilibrium activation registry records three admission
matrices: phase-only rows, chemical-only rows, and combined phase-chemical
rows. Bubble and dew pressure/temperature routes remain implemented and tested
as derived utility routes through the existing selector surface, but their
generic route keys are excluded from the generalized matrices. Every generalized
activation row must carry at least one proof case and evidence tier before it
can be used for future route admission.
```


### `explicit_association_closure_diagnostics`
- Family: Association diagnostics
- Status: Planned
- Public API: Internal diagnostics or explicitly approximate experimental route only
- Backend: Native C++ EOS/state diagnostics
- Dependency: CppAD for exact derivatives of the approximate closure
- Derivative backend: CppAD explicit derivatives of approximate association closures
- Solver role: Seeds, diagnoses, or continues associating routes without claiming exact PC-SAFT association
- Implementation owner: docs/roadmaps/explicit_association_closure_for_pcsaft.md; docs/derivation/explicit_association_closure_for_pcsaft.tex
- Validation: Planned explicit-vs-implicit association diagnostics against Gross/Sadowski 2002 EOS cases
- Capability key: planned:explicit_association_closure_diagnostics
- Description: Records explicit association closures as approximate Helmholtz diagnostics, not production exact association.
- Change note: Keeps explicit association closures out of production acceptance unless a route is deliberately exposed as approximate.
- LaTeX: `docs/latex/algorithms.tex:239`
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
- Implementation owner: src/epcsaft/regression/core.py; src/epcsaft/native/regression/ceres_regression.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/api/frontend/test_regression.py::test_regression_hydrocarbon_anchor_routes_through_new_object_api
- Capability key: regression:pure_neutral
- Description: Fits currently supported pure-neutral parameter targets through native Ceres.
- Change note: Initial algorithm-registry entry for pure-neutral regression.
- LaTeX: `docs/latex/algorithms.tex:262`
- Code owners: `src/epcsaft/native/bindings/module.cpp:1035` (m.def("_fit_pure_neutral_native_ceres", &fit_pure_neutral_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:578` (class PureNeutralCeresCostFunction final : public ceres::CostFunction {), `src/epcsaft/regression/core.py:2402` (def fit_pure_neutral(), `src/epcsaft/regression/core.py:2737` (def fit_pure_parameters()

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
- Implementation owner: src/epcsaft/regression/core.py; src/epcsaft/native/regression/ceres_regression.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/regression/test_liquid_electrolyte.py
- Capability key: regression:pure_ion
- Description: Fits currently supported pure-ion and Born-related target sets through native Ceres.
- Change note: Initial algorithm-registry entry for pure-ion regression; caveat preserves current target-family limits.
- LaTeX: `docs/latex/algorithms.tex:281`
- Code owners: `src/epcsaft/native/bindings/module.cpp:1040` (m.def("_fit_generic_native_ceres", &fit_generic_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:1537` (class PureIonCeresCostFunction final : public ceres::CostFunction {), `src/epcsaft/regression/core.py:2785` (def fit_pure_ion(), `src/epcsaft/regression/core.py:2988` (def fit_liquid_electrolyte_parameters()

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
- Implementation owner: src/epcsaft/regression/core.py; src/epcsaft/native/regression/ceres_regression.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/regression/test_binary.py
- Capability key: regression:binary_pair
- Description: Fits the currently implemented constant-k_ij binary parameter route through native Ceres.
- Change note: Initial algorithm-registry entry keeps l_ij and k_hb_ij out of the claim until implementation evidence exists.
- LaTeX: `docs/latex/algorithms.tex:299`
- Code owners: `src/epcsaft/native/bindings/module.cpp:1040` (m.def("_fit_generic_native_ceres", &fit_generic_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:1660` (class BinaryKijCeresCostFunction final : public ceres::CostFunction {), `src/epcsaft/regression/core.py:2814` (def fit_binary_parameters()

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
