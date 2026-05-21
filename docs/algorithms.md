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
- Code owners: `src/epcsaft/native/bindings/module.cpp:874` (m.def("_fit_generic_native_ceres", &fit_generic_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:565` (ceres::Solver::Options ceres_regression_options_cpp(int max_num_iterations) {)

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
- Public API: Equilibrium(mixture, ...).bubble_pressure(...)
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient, constraint Jacobian, and Hessian callbacks
- Solver role: Production selector-dispatched neutral bubble-pressure constrained NLP
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/core/selector_core.cpp; src/epcsaft/native/equilibrium/core/activation_matrix.h; src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp; src/epcsaft/native/equilibrium/register_bindings.cpp
- Validation: tests/api/frontend/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route; tests/native/equilibrium/diagnostics/test_selector_core_contracts.py; tests/native/contracts/test_equilibrium_activation_capabilities.py
- Capability key: bubble_dew_derived_routes
- Description: Solves the production neutral bubble-pressure route through the native selector core.
- Change note: Selector-core completion makes the activation matrix authoritative and removes non-production route AlgIDs.
- LaTeX: `docs/latex/algorithms.tex:72`
- Code owners: `src/epcsaft/equilibrium/workflows.py:156` (def bubble_p(mixture: Any, *, T: float, x: Any, options: EquilibriumOptions | None = None) -> EquilibriumResult:), `src/epcsaft/native/equilibrium/core/selector_core.cpp:112` (SelectorContract evaluate_selector_contract(), `src/epcsaft/native/equilibrium/core/selector_core.cpp:139` (epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult solve_selector_route(), `src/epcsaft/native/equilibrium/register_bindings.cpp:600` (m.def("_native_equilibrium_selector_contract", [](), `src/epcsaft/native/equilibrium/register_bindings.cpp:617` (m.def("_native_equilibrium_selector_route_result", [](), `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp:1863` (NeutralTwoPhaseEosRouteResult solve_pressure_route(), `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp:1999` (NeutralTwoPhaseEosRouteResult solve_temperature_route()

This entry exposes the trusted neutral bubble-pressure proof through
`Equilibrium(mixture).bubble_pressure`. The selector core reads the native
activation matrix, admits only neutral non-reactive non-electrolyte
non-associating mixtures for the production contract, and requires exact
derivatives plus postsolve certification. TP flash, LLE, stability, electrolyte,
reactive, and speciation families are declared-not-exposed future families in
the activation matrix; they are not active algorithm-registry entries and they
do not imply public route availability.

**LaTeX source**

```tex
This entry exposes the trusted neutral bubble-pressure proof through
\texttt{Equilibrium(mixture).bubble_pressure}. The selector core reads the native
activation matrix, admits only neutral non-reactive non-electrolyte
non-associating mixtures for the production contract, and requires exact
derivatives plus postsolve certification. TP flash, LLE, stability, electrolyte,
reactive, and speciation families are declared-not-exposed future families in
the activation matrix; they are not active algorithm-registry entries and they
do not imply public route availability.
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
- LaTeX: `docs/latex/algorithms.tex:97`
- Code owners: `src/epcsaft/native/bindings/module.cpp:869` (m.def("_fit_pure_neutral_native_ceres", &fit_pure_neutral_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:578` (class PureNeutralCeresCostFunction final : public ceres::CostFunction {), `src/epcsaft/regression/core.py:2409` (def fit_pure_neutral(), `src/epcsaft/regression/core.py:2744` (def fit_pure_parameters()

This entry covers the implemented pure-neutral native Ceres route and does not
broaden support to every possible pure-component parameter family.

**LaTeX source**

```tex
This entry covers the implemented pure-neutral native Ceres route and does not
broaden support to every possible pure-component parameter family.
```


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
- LaTeX: `docs/latex/algorithms.tex:114`
- Code owners: `src/epcsaft/native/bindings/module.cpp:874` (m.def("_fit_generic_native_ceres", &fit_generic_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:1537` (class PureIonCeresCostFunction final : public ceres::CostFunction {), `src/epcsaft/regression/core.py:2792` (def fit_pure_ion(), `src/epcsaft/regression/core.py:2995` (def fit_liquid_electrolyte_parameters()

This entry is limited to the currently implemented pure-ion target surface.

**LaTeX source**

```tex
This entry is limited to the currently implemented pure-ion target surface.
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
- LaTeX: `docs/latex/algorithms.tex:130`
- Code owners: `src/epcsaft/native/bindings/module.cpp:874` (m.def("_fit_generic_native_ceres", &fit_generic_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:1660` (class BinaryKijCeresCostFunction final : public ceres::CostFunction {), `src/epcsaft/regression/core.py:2821` (def fit_binary_parameters()

This entry intentionally does not claim native optimizer support for every
binary parameter family. It is not a production Ceres optimizer for `l_{ij}`
or `k^{hb}_{ij}`.

**LaTeX source**

```tex
This entry intentionally does not claim native optimizer support for every
binary parameter family. It is not a production Ceres optimizer for \(l_{ij}\)
or \(k^{hb}_{ij}\).
```

**Rendered formulae**

$$
l_{ij}
$$

$$
k^{hb}_{ij}
$$
