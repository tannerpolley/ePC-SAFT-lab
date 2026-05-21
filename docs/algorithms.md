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
Ipopt-backed equilibrium and speciation routes.

**LaTeX source**

```tex
The \texttt{NlpProblem} contract is the common native interface for objective,
constraint, Jacobian, bounds, scaling, and diagnostics payloads used by
Ipopt-backed equilibrium and speciation routes.
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
- Code owners: `src/epcsaft/native/bindings/module.cpp:3650` (m.def("_fit_generic_native_ceres", &fit_generic_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:565` (ceres::Solver::Options ceres_regression_options_cpp(int max_num_iterations) {)

The Ceres adapter family owns native least-squares solve setup for supported
regression routes. It is separate from Ipopt and does not call Ipopt routes.

**LaTeX source**

```tex
The Ceres adapter family owns native least-squares solve setup for supported
regression routes. It is separate from Ipopt and does not call Ipopt routes.
```


## Equilibrium Algorithms

### `neutral_tp_flash_ipopt`
- Family: Phase equilibrium
- Status: Implemented
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient and constraint Jacobian
- Solver role: Native neutral TP flash two-phase EOS constrained NLP
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/routes/route_builders.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/equilibrium/routes/neutral/test_flash.py
- Capability key: neutral_tp_flash
- Description: Solves neutral two-phase TP flash through the native Ipopt EOS route.
- Change note: Initial algorithm-registry entry for neutral TP flash.
- LaTeX: `docs/latex/algorithms.tex:72`
- Code owners: `src/epcsaft/equilibrium/workflows.py:304` (@dataclass(frozen=True, slots=True)), `src/epcsaft/native/bindings/module.cpp:2130` (m.def("_native_neutral_tp_flash_eos_nlp_contract", [](), `src/epcsaft/native/bindings/module.cpp:2853` (m.def("_native_neutral_tp_flash_eos_route_result", [](), `src/epcsaft/native/equilibrium/routes/route_builders.cpp:1779` (NeutralTwoPhaseEosNlpContract evaluate_neutral_two_phase_eos_tp_flash_nlp_contract(), `src/epcsaft/native/equilibrium/routes/route_builders.cpp:2660` (NeutralTwoPhaseEosRouteResult solve_neutral_two_phase_eos_tp_flash_route()

This entry covers the internal neutral TP flash route. The hard public API reset
does not expose typed problem objects or string route facades.

**LaTeX source**

```tex
This entry covers the internal neutral TP flash route. The hard public API reset
does not expose typed problem objects or string route facades.
```


### `neutral_lle_ipopt`
- Family: Phase equilibrium
- Status: Implemented
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient and constraint Jacobian
- Solver role: Native neutral liquid-liquid two-phase EOS constrained NLP
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/routes/route_builders.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/equilibrium/routes/neutral/test_lle.py
- Capability key: neutral_lle_flash
- Description: Solves neutral LLE through the native Ipopt EOS route.
- Change note: Initial algorithm-registry entry for neutral LLE.
- LaTeX: `docs/latex/algorithms.tex:89`
- Code owners: `src/epcsaft/equilibrium/workflows.py:417` (@dataclass(frozen=True, slots=True)), `src/epcsaft/native/bindings/module.cpp:2149` (m.def("_native_neutral_lle_eos_nlp_contract", [](), `src/epcsaft/native/bindings/module.cpp:2898` (m.def("_native_neutral_lle_eos_route_result", [](), `src/epcsaft/native/equilibrium/routes/route_builders.cpp:1808` (NeutralTwoPhaseEosNlpContract evaluate_neutral_two_phase_eos_lle_nlp_contract(), `src/epcsaft/native/equilibrium/routes/route_builders.cpp:2689` (NeutralTwoPhaseEosRouteResult solve_neutral_two_phase_eos_lle_route()

This entry covers the internal neutral liquid-liquid split route.

**LaTeX source**

```tex
This entry covers the internal neutral liquid-liquid split route.
```


### `electrolyte_lle_ipopt`
- Family: Electrolyte phase equilibrium
- Status: Implemented
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient and constraint Jacobian
- Solver role: Native charge-constrained electrolyte LLE EOS constrained NLP
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/routes/route_builders.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/equilibrium/routes/electrolyte/test_route_builders.py
- Capability key: electrolyte_lle
- Description: Solves electrolyte liquid-liquid split routes with charge-constrained phase amounts.
- Change note: Initial algorithm-registry entry for electrolyte LLE.
- LaTeX: `docs/latex/algorithms.tex:105`
- Code owners: `src/epcsaft/equilibrium/workflows.py:440` (@dataclass(frozen=True, slots=True)), `src/epcsaft/native/bindings/module.cpp:2168` (m.def("_native_electrolyte_lle_eos_nlp_contract", [](), `src/epcsaft/native/bindings/module.cpp:2943` (m.def("_native_electrolyte_lle_eos_route_result", [](), `src/epcsaft/native/equilibrium/routes/route_builders.cpp:1837` (NeutralTwoPhaseEosNlpContract evaluate_electrolyte_lle_eos_nlp_contract(), `src/epcsaft/native/equilibrium/routes/route_builders.cpp:2718` (NeutralTwoPhaseEosRouteResult solve_electrolyte_lle_eos_route()

This entry covers the generic electrolyte LLE route. Downstream extraction or
selectivity metrics remain outside the package algorithm.

**LaTeX source**

```tex
This entry covers the generic electrolyte LLE route. Downstream extraction or
selectivity metrics remain outside the package algorithm.
```


### `bubble_dew_ipopt`
- Family: Phase equilibrium
- Status: Implemented
- Public API: Equilibrium(mixture, ...).bubble_pressure(...)
- Backend: Native C++ Ipopt equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient and constraint Jacobian
- Solver role: Native fixed-composition bubble/dew constrained NLP routes
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/api/frontend/test_equilibrium.py::test_equilibrium_bubble_pressure_uses_trusted_cppad_ipopt_route
- Capability key: neutral_bubble_dew
- Description: Solves neutral bubble and dew route variants through native Ipopt.
- Change note: Initial algorithm-registry entry for neutral bubble/dew routes.
- LaTeX: `docs/latex/algorithms.tex:122`
- Code owners: `src/epcsaft/equilibrium/workflows.py:365` (@dataclass(frozen=True, slots=True)), `src/epcsaft/equilibrium/workflows.py:391` (@dataclass(frozen=True, slots=True)), `src/epcsaft/native/bindings/module.cpp:2397` (m.def("_native_neutral_bubble_p_eos_nlp_contract", [](), `src/epcsaft/native/bindings/module.cpp:2993` (m.def("_native_neutral_bubble_p_eos_route_result", [](), `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp:1863` (NeutralTwoPhaseEosRouteResult solve_pressure_route(), `src/epcsaft/native/equilibrium/routes/derived/bubble_dew.cpp:1999` (NeutralTwoPhaseEosRouteResult solve_temperature_route()

This entry exposes the trusted neutral bubble-pressure proof through the reset
frontend. Other bubble/dew variants remain internal until they receive reset
frontend coverage.

**LaTeX source**

```tex
This entry exposes the trusted neutral bubble-pressure proof through the reset
frontend. Other bubble/dew variants remain internal until they receive reset
frontend coverage.
```


### `stability_tpd_ipopt`
- Family: Stability analysis
- Status: Implemented
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ipopt stability NLP
- Dependency: Ipopt
- Derivative backend: Exact native objective gradient and constraint Jacobian
- Solver role: Native tangent-plane-distance stability route
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/routes/stability/stability_route_builders.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/equilibrium/routes/stability/test_route_builders.py
- Capability key: neutral_stability; electrolyte_stability
- Description: Solves neutral and electrolyte TPD trial routes through native Ipopt.
- Change note: Initial algorithm-registry entry for stability routes.
- LaTeX: `docs/latex/algorithms.tex:140`
- Code owners: `src/epcsaft/equilibrium/workflows.py:322` (@dataclass(frozen=True, slots=True)), `src/epcsaft/native/bindings/module.cpp:2478` (m.def("_native_neutral_stability_tpd_nlp_contract", [](), `src/epcsaft/native/bindings/module.cpp:3199` (m.def("_native_neutral_stability_tpd_route_result", [](), `src/epcsaft/native/equilibrium/routes/stability/stability_route_builders.cpp:1251` (StabilityRouteResult solve_neutral_stability_tpd_route(), `src/epcsaft/native/equilibrium/routes/stability/stability_route_builders.cpp:1331` (StabilityRouteResult solve_electrolyte_stability_tpd_route(), `src/epcsaft/native/equilibrium/routes/stability/stability_route_builders.cpp:1409` (StabilityRouteResult solve_reactive_stability_tpd_route()

This entry covers neutral and electrolyte tangent-plane-distance trial routes.
It does not describe downstream phase-selection policy beyond the returned
generic stability payload.

**LaTeX source**

```tex
This entry covers neutral and electrolyte tangent-plane-distance trial routes.
It does not describe downstream phase-selection policy beyond the returned
generic stability payload.
```


## Reactive and Speciation Algorithms

### `ideal_speciation_ipopt`
- Family: Chemical equilibrium
- Status: Implemented
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ipopt ideal Gibbs speciation NLP
- Dependency: Ipopt
- Derivative backend: Analytic or CppAD ideal log-amount residual Jacobian
- Solver role: Native homogeneous ideal reactive speciation route
- Implementation owner: src/epcsaft/equilibrium/reactive_speciation.py; src/epcsaft/native/equilibrium/routes/reactive/ideal_speciation_problem.cpp; src/epcsaft/native/equilibrium/routes/reactive/chemical_equilibrium.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/equilibrium/routes/reactive/test_chemical_equilibrium_native_api.py
- Capability key: reactive_speciation
- Description: Solves ideal homogeneous reactive speciation through native Ipopt.
- Change note: Initial algorithm-registry entry for ideal speciation.
- LaTeX: `docs/latex/algorithms.tex:160`
- Code owners: `src/epcsaft/equilibrium/reactive_speciation.py:625` (def _solve_reactive_speciation_native(), `src/epcsaft/equilibrium/workflows.py:496` (@dataclass(frozen=True, slots=True)), `src/epcsaft/native/bindings/module.cpp:3656` (m.def("_solve_chemical_equilibrium_native", &solve_chemical_equilibrium_native_binding);), `src/epcsaft/native/equilibrium/routes/reactive/ideal_speciation_problem.cpp:699` (IdealSpeciationIpoptResult solve_ideal_speciation_ipopt(), `src/epcsaft/native/equilibrium/routes/reactive/ideal_speciation_problem.cpp:735` (ChemicalEquilibriumResultNative solve_ideal_speciation_chemical_equilibrium_ipopt()

This entry covers the ideal-standard-state speciation route. It is a chemical
equilibrium algorithm, not a phase-equilibrium split.

**LaTeX source**

```tex
This entry covers the ideal-standard-state speciation route. It is a chemical
equilibrium algorithm, not a phase-equilibrium split.
```


### `nonideal_speciation_ipopt`
- Family: Chemical equilibrium
- Status: Implemented
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ipopt nonideal residual speciation NLP
- Dependency: Ipopt
- Derivative backend: CppAD implicit phase-state sensitivity path where required
- Solver role: Native homogeneous nonideal reactive speciation route
- Implementation owner: src/epcsaft/equilibrium/reactive_speciation.py; src/epcsaft/native/equilibrium/routes/reactive/chemical_equilibrium.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/equilibrium/routes/reactive/test_chemical_equilibrium_native_api.py
- Capability key: reactive_speciation
- Description: Solves nonideal homogeneous reactive speciation through native Ipopt.
- Change note: Initial algorithm-registry entry for nonideal speciation.
- LaTeX: `docs/latex/algorithms.tex:177`
- Code owners: `src/epcsaft/equilibrium/reactive_speciation.py:625` (def _solve_reactive_speciation_native(), `src/epcsaft/equilibrium/workflows.py:496` (@dataclass(frozen=True, slots=True)), `src/epcsaft/native/bindings/module.cpp:3656` (m.def("_solve_chemical_equilibrium_native", &solve_chemical_equilibrium_native_binding);), `src/epcsaft/native/equilibrium/routes/reactive/chemical_equilibrium.cpp:2419` (ChemicalEquilibriumResultNative solve_nonideal_speciation_chemical_equilibrium_ipopt()

This entry covers nonideal standard-state routes whose residuals require
package thermodynamic activity/fugacity calculations.

**LaTeX source**

```tex
This entry covers nonideal standard-state routes whose residuals require
package thermodynamic activity/fugacity calculations.
```


### `reactive_lle_liquid_root_ipopt`
- Family: Reactive phase equilibrium
- Status: Implemented
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ipopt reactive liquid-root phase-equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Native route residual Jacobian
- Solver role: Coupled reactive LLE liquid-root constrained route
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/routes/reactive/phase_equilibrium_problem.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/equilibrium/routes/reactive/test_lle.py
- Capability key: reactive_lle_liquid_root
- Description: Solves coupled neutral reactive LLE through the native liquid-root Ipopt route.
- Change note: Initial algorithm-registry entry for reactive LLE.
- LaTeX: `docs/latex/algorithms.tex:194`
- Code owners: `src/epcsaft/equilibrium/workflows.py:634` (@dataclass(frozen=True, slots=True)), `src/epcsaft/native/bindings/module.cpp:2223` (m.def("_native_reactive_lle_eos_nlp_contract", [](), `src/epcsaft/native/equilibrium/routes/reactive/phase_equilibrium_problem.cpp:3011` (epcsaft::native::equilibrium_nlp::ReactiveTwoPhaseEosRouteResult solve_reactive_phase_liquid_root_route_native(), `src/epcsaft/native/equilibrium/routes/route_builders.cpp:2178` (ReactiveTwoPhaseEosRouteResult solve_reactive_lle_eos_route()

This entry is a coupled reactive phase-equilibrium route, not a staged
speciation-then-split workflow.

**LaTeX source**

```tex
This entry is a coupled reactive phase-equilibrium route, not a staged
speciation-then-split workflow.
```


### `reactive_electrolyte_lle_liquid_root_ipopt`
- Family: Reactive electrolyte phase equilibrium
- Status: Implemented
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ipopt reactive electrolyte liquid-root phase-equilibrium NLP
- Dependency: Ipopt
- Derivative backend: Native route residual Jacobian
- Solver role: Coupled reactive electrolyte LLE liquid-root constrained route
- Implementation owner: src/epcsaft/equilibrium/workflows.py; src/epcsaft/native/equilibrium/routes/reactive/phase_equilibrium_problem.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/equilibrium/routes/reactive_electrolyte/test_route_builders.py
- Capability key: reactive_electrolyte_lle_liquid_root
- Description: Solves coupled reactive electrolyte LLE through the native liquid-root Ipopt route.
- Change note: Initial algorithm-registry entry for reactive electrolyte LLE.
- LaTeX: `docs/latex/algorithms.tex:211`
- Code owners: `src/epcsaft/equilibrium/workflows.py:634` (@dataclass(frozen=True, slots=True)), `src/epcsaft/native/bindings/module.cpp:2278` (m.def("_native_reactive_electrolyte_lle_eos_nlp_contract", [](), `src/epcsaft/native/equilibrium/routes/reactive/phase_equilibrium_problem.cpp:3011` (epcsaft::native::equilibrium_nlp::ReactiveTwoPhaseEosRouteResult solve_reactive_phase_liquid_root_route_native(), `src/epcsaft/native/equilibrium/routes/route_builders.cpp:2225` (ReactiveTwoPhaseEosRouteResult solve_reactive_electrolyte_lle_eos_route()

This entry preserves the boundary that the package returns generic reactive
phase outputs; downstream projects compute application metrics from those
outputs.

**LaTeX source**

```tex
This entry preserves the boundary that the package returns generic reactive
phase outputs; downstream projects compute application metrics from those
outputs.
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
- LaTeX: `docs/latex/algorithms.tex:231`
- Code owners: `src/epcsaft/native/bindings/module.cpp:3645` (m.def("_fit_pure_neutral_native_ceres", &fit_pure_neutral_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:578` (class PureNeutralCeresCostFunction final : public ceres::CostFunction {), `src/epcsaft/regression/core.py:2409` (def fit_pure_neutral(), `src/epcsaft/regression/core.py:2744` (def fit_pure_parameters()

This entry covers the implemented pure-neutral native Ceres route and does not
broaden support to every possible pure-component parameter family.

**LaTeX source**

```tex
This entry covers the implemented pure-neutral native Ceres route and does not
broaden support to every possible pure-component parameter family.
```


### `pure_ion_ceres_regression`
- Family: Regression
- Status: Implemented
- Public API: Internal native route only; no reset public frontend method yet
- Backend: Native C++ Ceres regression
- Dependency: Ceres
- Derivative backend: CppAD implicit residual Jacobian for supported pure-ion targets
- Solver role: Native least-squares pure-ion parameter regression
- Implementation owner: src/epcsaft/regression/core.py; src/epcsaft/native/regression/ceres_regression.cpp; src/epcsaft/native/bindings/module.cpp
- Validation: tests/native/regression/test_liquid_electrolyte.py
- Capability key: regression:pure_ion
- Description: Fits currently supported pure-ion and Born-related target sets through native Ceres.
- Change note: Initial algorithm-registry entry for pure-ion regression.
- LaTeX: `docs/latex/algorithms.tex:248`
- Code owners: `src/epcsaft/native/bindings/module.cpp:3650` (m.def("_fit_generic_native_ceres", &fit_generic_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:1537` (class PureIonCeresCostFunction final : public ceres::CostFunction {), `src/epcsaft/regression/core.py:2792` (def fit_pure_ion(), `src/epcsaft/regression/core.py:2995` (def fit_liquid_electrolyte_parameters()

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
- LaTeX: `docs/latex/algorithms.tex:264`
- Code owners: `src/epcsaft/native/bindings/module.cpp:3650` (m.def("_fit_generic_native_ceres", &fit_generic_native_ceres_binding);), `src/epcsaft/native/regression/ceres_regression.cpp:1660` (class BinaryKijCeresCostFunction final : public ceres::CostFunction {), `src/epcsaft/regression/core.py:2821` (def fit_binary_parameters()

This entry intentionally does not claim native optimizer support for every
binary parameter family, including `l_{ij}` or `k^{hb}_{ij}`.

**LaTeX source**

```tex
This entry intentionally does not claim native optimizer support for every
binary parameter family, including \(l_{ij}\) or \(k^{hb}_{ij}\).
```

**Rendered formulae**

$$
l_{ij}
$$

$$
k^{hb}_{ij}
$$


### `reactive_electrolyte_batch_residual_context`
- Family: Reactive regression context
- Status: Implemented residual evaluator
- Public API: Internal residual context only; no reset public frontend method yet
- Backend: Python orchestration over package thermodynamic calls
- Dependency: None for the context itself
- Derivative backend: Not a registered native optimizer derivative path
- Solver role: Structured residual/context evaluator, not a production Ceres optimizer
- Implementation owner: src/epcsaft/regression/reactive.py; src/epcsaft/runtime/__init__.py
- Validation: tests/native/equilibrium/routes/reactive/test_phase_equilibrium_residual_surface.py
- Capability key: reactive_electrolyte_batch_context
- Description: Evaluates mixed reactive-electrolyte residual contexts without claiming production optimizer support.
- Change note: Initial algorithm-registry entry preserves the current residual-evaluator claim boundary.
- LaTeX: `docs/latex/algorithms.tex:281`
- Code owners: `src/epcsaft/regression/reactive.py:759` (def build_reactive_regression_objective(), `src/epcsaft/regression/reactive.py:790` (def evaluate_reactive_regression_objective()

This entry records the implemented residual/context evaluator and explicitly
does not claim native Ceres production optimization for reactive electrolyte
batch fitting.

**LaTeX source**

```tex
This entry records the implemented residual/context evaluator and explicitly
does not claim native Ceres production optimization for reactive electrolyte
batch fitting.
```
