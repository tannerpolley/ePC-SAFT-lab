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
- Public API: Equilibrium(mixture, route='bubble_pressure'|'bubble_temperature'|'dew_pressure'|'dew_temperature', ...).solve()
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient, constraint Jacobian, and Hessian callbacks
- Solver role: Production selector-dispatched neutral bubble/dew constrained NLP route specs
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/core/selector_core.cpp; src/epcsaft/native/equilibrium/core/activation_matrix.h; src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp; src/epcsaft/native/equilibrium/register_bindings.cpp
- Validation: tests/api/frontend/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route; tests/native/equilibrium/diagnostics/test_selector_core_contracts.py; tests/native/contracts/test_equilibrium_activation_capabilities.py
- Capability key: bubble_dew_derived_routes
- Description: Solves production neutral bubble/dew pressure and temperature route specs through the native selector core.
- Change note: Neutral VLE selector expansion promotes bubble/dew pressure and temperature routes through the shared residual core.
- LaTeX: `docs/latex/algorithms.tex:72`
- Code owners: `src/epcsaft/equilibrium/workflows.py:475` (def _solve_selector_vle(), `src/epcsaft/native/equilibrium/core/selector_core.cpp:324` (SelectorContract evaluate_selector_contract(), `src/epcsaft/native/equilibrium/core/selector_core.cpp:357` (epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult solve_selector_route(), `src/epcsaft/native/equilibrium/register_bindings.cpp:634` (m.def("_native_equilibrium_selector_contract", [](), `src/epcsaft/native/equilibrium/register_bindings.cpp:648` (m.def("_native_equilibrium_selector_route_result", [](), `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp:2640` (NeutralTwoPhaseEosRouteResult solve_pressure_route(), `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp:2777` (NeutralTwoPhaseEosRouteResult solve_temperature_route()

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
- Code owners: `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp:2910` (NeutralTwoPhaseEosRouteResult solve_flash_route()

This entry exposes the trusted neutral two-phase TP flash proof through the
`flash` route spec configured by
`Equilibrium(mixture, route="flash", ...)` and executed by
`solve()`. Flash is a route spec over the same native
VLE residual and hard-constraint core as bubble and dew routes. The native
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
VLE residual and hard-constraint core as bubble and dew routes. The native
selector owns deterministic seed generation, activation checks, exact
derivative requirements, and postsolve certification. Gibbs/free-energy terms
may shape the NLP or seed ranking, but solver success alone is not the
acceptance criterion.
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
- LaTeX: `docs/latex/algorithms.tex:119`
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
- LaTeX: `docs/latex/algorithms.tex:136`
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
- LaTeX: `docs/latex/algorithms.tex:152`
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
