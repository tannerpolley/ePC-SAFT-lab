Diagnostics
===========

Runtime Capabilities
--------------------

``epcsaft.capabilities()`` reports provider runtime features. Equilibrium route
capabilities are reported by ``epcsaft_equilibrium.capabilities()``. The
important backend labels are:

* ``native``: production native runtime path.
* ``native_ipopt_equilibrium_nlp``: implemented production equilibrium route
  owned by the native Ipopt NLP layer.
* ``batch_residual_evaluation_context``: Python batches rows and formats
  diagnostics for a residual context; this is not a production optimizer.

The native activation matrix owns selector-admitted public route names, and
``epcsaft_equilibrium.capability_evidence`` joins each exposed family to exact
proof nodes, retained artifacts, and acceptance metrics. Repository test slices
and ``scripts/dev/validate_project.py`` modes are owned separately by
``scripts.dev.validation_registry``. Provider capability metadata contains only
provider-owned scientific evidence.

Use ``uv run python run_pytest.py --native-contracts -q`` for native route
metadata and result-diagnostics checks. That slice is intentionally separate
from the broad native route-builder solver suite, which is slow and should be
targeted only by a single test node or with explicit long-test opt-in.

Equilibrium route results keep diagnostics as JSON-like dictionaries for stable
serialization. For code that needs a typed interface over common route fields,
use ``result.route_diagnostics`` or ``exc.route_diagnostics`` on
``SolutionError``. The view exposes route status, solver backend, exact
derivative flags, residual families, constraint families, selected seed name,
and normalized seed-attempt counts without changing the underlying diagnostics
payload.

EOS state diagnostics keep the same JSON-like ``state.state_diagnostics()``
dictionary for serialization. Code that wants a typed view over the stable
payload can use ``state.state_diagnostics_view()`` or
``epcsaft.state.eos_views.StateDiagnosticsView``. The view exposes temperature, phase,
composition, pressure, molar density, compressibility factor, ionic-output
presence, and fugacity-contribution terms while leaving the serialized
``state_diagnostics()`` keys unchanged.

For reactive electrolyte regression, the
``mixed_pressure_speciation_residual_context`` capability advertises the
diagnostic residual context, its supported target families, and the fact that it
is not a production optimizer. Reactive electrolyte parameter fitting is not
public until native Ceres owns the optimizer route with exact derivatives.

Selector Neutral VLE Diagnostics
--------------------------------

The production equilibrium diagnostic paths are the native selector-backed
neutral VLE routes:

* ``Equilibrium(mixture, route="bubble_pressure", T=..., x=...).solve()``
* ``Equilibrium(mixture, route="dew_pressure", T=..., y=...).solve()``
* ``Equilibrium(mixture, route="single_component_vle", T=...).solve()``

Accepted results include enough route diagnostics to prove that the native
activation row, exact Ipopt derivative path, density closure, residual rows,
hard constraints, and postsolve certification were used:

* ``selector_family`` is ``bubble_dew_derived_routes`` for bubble/dew pressure
  specs or ``single_component_vle`` for the scoped hydrocarbon saturation route.
* ``route`` is the admitted selector route spec.
* ``activation`` is copied from the native activation matrix row.
* ``residual_families`` and ``constraint_families`` match that activation row.
* ``gradient_approximation`` and ``jacobian_approximation`` are exact.
* ``postsolve_certification`` is present and accepted.

Neutral LLE and TP flash retain internal activation, refinement, and
certification diagnostics. Neutral LLE remains closed because a finite
sampled-candidate Stage II audit is not a global HELD proof. Multiphase,
electrolyte, reactive, CE/CPE, and generalized stability families are internal
validation surfaces until matching activation-matrix proof exposes them
through the selector core. Retained electrolyte artifacts provide component,
replay, and postsolve diagnostics for repair; they do not admit a public route.

Contribution Maps
-----------------

State objects expose contribution-map helpers:

* ``state.helmholtz_contributions()``
* ``state.residual_helmholtz_contributions()``
* ``state.pressure_contributions()``
* ``state.chemical_potential_contributions()``
* ``state.ln_fugacity_coefficient_contributions()``

Public contribution family names are ``hard_chain``, ``dispersion``,
``association``, ``ionic``, and ``born``. Inactive terms are retained with zero
values when the native runtime evaluates them as inactive.

Activity coefficients are available through ``state.activity_coefficient(...)``.
Additive activity-coefficient term decomposition is not currently exposed by
the native activity API, so ``state.activity_coefficient_contributions()``
raises ``InputError`` instead of returning invented terms.
