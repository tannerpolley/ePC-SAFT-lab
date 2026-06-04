# M8 - Python Toybox

Python-only exploratory toybox work for EOS, derivative, property, and
equilibrium-style analysis before provider or equilibrium implementation
admission.

## Scope

M8 is an analysis milestone, not a production package milestone. It can combine
EOS and equilibrium-style questions when the work is still a Python-only
toybox, diagnostic harness, or figure/data workflow. Production implementation
ownership stays with the package milestones:

- `M3 - EOS`: provider EOS behavior, native derivative contracts, public
  provider capability claims, and production EOS admission.
- `M4 - Equilibrium`: equilibrium package objectives, Jacobians, Hessians,
  Ipopt contracts, route behavior, and production equilibrium admission.
- `M6 - Validation`: executable literature benchmark evidence and
  release-quality validation gates.

M8 may produce evidence that later becomes M3, M4, or M6 work. It must not
claim provider, equilibrium, or benchmark capability by itself.

## Project Field Defaults

- Package: `analysis`
- Capability: `toybox`, `association`, `derivatives`, `property-validation`,
  or `equilibrium-probe`
- Backend: `python`, `jax`, `implicit`, or `none` when relevant
- Release target: `future`

## Current Specs

| Spec | Category | Summary |
| --- | --- | --- |
| [Picard autodiff and exact implicit sensitivity baseline hardening](../../specs/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening.md) | derivatives | Compare JAX autodiff through the explicit Picard model against exact implicit sensitivity baselines and parameter sensitivities. |
| [Associating-compound pressure density validation lane](../../specs/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane.md) | property validation | Build honest pressure-density and vapor-pressure/liquid-density style plots for associating compounds only. |
| [Pure-component saturation pressure solver](../../specs/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver.md) | property validation | Add a SciPy pure-component saturation solver so toybox pressure plots become true vapor-pressure predictions. |
| [Explicit closure admission decision](../../specs/2026-06-04-m8-python-toybox-explicit-closure-admission-decision.md) | admission | Use toybox evidence to decide whether Picard remains the only closure candidate and what gates block provider admission. |
| [Equilibrium relevance probe for Picard closure error](../../specs/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error.md) | equilibrium probe | Probe whether Picard closure error breaks objective, Jacobian, and Hessian quality before any M4 implementation work. |

## Current Plans

| Plan | Depends On | Summary |
| --- | --- | --- |
| [Picard autodiff and exact implicit sensitivity baseline hardening plan](../../plans/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening-plan.md) | none | Build exact implicit sensitivity, JAX Picard derivative, and Hessian agreement lanes. |
| [Associating-compound pressure density validation lane plan](../../plans/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane-plan.md) | none | Build associating-compound pressure-density and saturation-style validation plots. |
| [Pure-component saturation pressure solver plan](../../plans/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver-plan.md) | none | Build a SciPy pure-component saturation solver for true toybox vapor-pressure predictions. |
| [Explicit closure admission decision plan](../../plans/2026-06-04-m8-python-toybox-explicit-closure-admission-decision-plan.md) | derivative and property plans | Reduce toybox closure scope to retained Picard evidence and document provider admission gates. |
| [Equilibrium relevance probe for Picard closure error plan](../../plans/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error-plan.md) | derivative and property plans | Build a small objective/Jacobian/Hessian probe without creating M4 route behavior. |

## Current Issues

| Issue | Status | Depends On | Summary |
| --- | --- | --- | --- |
| [#221](https://github.com/ePC-SAFT/ePC-SAFT/issues/221) | closed | none | Hardened Picard autodiff and exact implicit sensitivity baselines in the Python toybox. |
| [#222](https://github.com/ePC-SAFT/ePC-SAFT/issues/222) | closed | none | Added associating-compound pressure-density validation with honest data points and dotted exact-vs-Picard curves. |
| [#223](https://github.com/ePC-SAFT/ePC-SAFT/issues/223) | ready / HITL | none | Decide whether Picard clears the toybox evidence gates for later provider admission. |
| [#224](https://github.com/ePC-SAFT/ePC-SAFT/issues/224) | ready / HITL | none | Probe whether Picard closure error is dangerous for later equilibrium objective, Jacobian, and Hessian work. |
| [#227](https://github.com/ePC-SAFT/ePC-SAFT/issues/227) | ready / HITL | none | Add a SciPy pure-component saturation solver so toybox pressure plots become true vapor-pressure predictions. |

## Closed Issues

- [https://github.com/ePC-SAFT/ePC-SAFT/issues/222](https://github.com/ePC-SAFT/ePC-SAFT/issues/222) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/226](https://github.com/ePC-SAFT/ePC-SAFT/pull/226) on 2026-06-04

## Historical Seed Work

The first explicit-association toybox slices were completed before this
milestone existed and remain recorded under M3 because they were originally
framed as provider EOS evidence:

| Issue | PR | Summary |
| --- | --- | --- |
| [#214](https://github.com/ePC-SAFT/ePC-SAFT/issues/214) | [#215](https://github.com/ePC-SAFT/ePC-SAFT/pull/215) | Built Python toybox for explicit association closure accuracy. |
| [#216](https://github.com/ePC-SAFT/ePC-SAFT/issues/216) | [#217](https://github.com/ePC-SAFT/ePC-SAFT/pull/217) | Added hard-chain and dispersion context to the explicit association toybox. |
| [#218](https://github.com/ePC-SAFT/ePC-SAFT/issues/218) | [#219](https://github.com/ePC-SAFT/ePC-SAFT/pull/219) | Extended explicit association toybox with follow-up analysis evidence lanes. |

Future Python-only toybox development should prefer this milestone unless the
work has already crossed into provider implementation, equilibrium
implementation, or benchmark-evidence admission.
