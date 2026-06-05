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

## Solver And Derivative Guidance

The toybox should stay light and should validate math shape, data behavior, and
admission evidence rather than production solver architecture.

- Use SciPy for analysis-only nonlinear solves, root finding, least-squares
  residual solves, saturation pressure, and pressure-density coupling.
- Use JAX for derivative evidence: residual Jacobians, selected gradients,
  selected Hessian diagnostics, smoothness checks, and comparison against exact
  implicit sensitivity baselines.
- Prefer Gauss-Newton Hessian diagnostics such as `J.T @ J` for residual
  objectives when that is the relevant nonlinear-system evidence.
- Keep full `jax.hessian(...)` checks small and selective. They are diagnostic
  spot checks, not the default path for figure generation or solver loops.
- Do not make Python Ipopt bindings a required M8 dependency. If a Python Ipopt
  adapter is explored, record the environment status plainly and keep the
  working analysis route independent of that adapter.
- Production exact Hessian of the Lagrangian and Ipopt callback behavior belong
  to CppAD/C++ package work, not to the Python toybox.

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
| [Explicit closure admission decision](../../specs/2026-06-04-m8-python-toybox-explicit-closure-admission-decision.md) | admission | Use fixed-grid relative-error, simulation-timing, and retained-figure evidence to recommend the final #161 Picard disposition. |
| [Equilibrium relevance probe for Picard closure error](../../specs/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error.md) | equilibrium probe | Probe whether Picard closure error breaks objective, Jacobian, and Hessian quality before any M4 implementation work. |
| [CppAD-shaped Picard property and derivative evidence](../../specs/2026-06-04-m8-python-toybox-cppad-shaped-picard-property-derivative-evidence.md) | derivatives / property validation | Test retained Picard across pure and mixture association schemes and compare NumPy/JAX values, Jacobians, and Hessians as CppAD-shaped evidence. |
| [Picard stress evidence to rescue or retire](../../specs/2026-06-05-m8-python-toybox-picard-stress-evidence-to-rescue-or-retire.md) | admission / stress testing | Define the harsh post-#223 evidence needed to either rescue Picard for more research or retire it cleanly. |

## Current Plans

| Plan | Depends On | Summary |
| --- | --- | --- |
| [Picard autodiff and exact implicit sensitivity baseline hardening plan](../../plans/2026-06-04-m8-python-toybox-picard-autodiff-and-exact-implicit-sensitivity-baseline-hardening-plan.md) | none | Build exact implicit sensitivity, JAX Picard derivative, and Hessian agreement lanes. |
| [Associating-compound pressure density validation lane plan](../../plans/2026-06-04-m8-python-toybox-associating-compound-pressure-density-validation-lane-plan.md) | none | Build associating-compound pressure-density and saturation-style validation plots. |
| [Pure-component saturation pressure solver plan](../../plans/2026-06-04-m8-python-toybox-pure-component-saturation-pressure-solver-plan.md) | none | Build a SciPy pure-component saturation solver for true toybox vapor-pressure predictions. |
| [Explicit closure admission decision plan](../../plans/2026-06-04-m8-python-toybox-explicit-closure-admission-decision-plan.md) | derivative and property plans | Generate the final Picard policy-grid, simulation-timing, plotted-data, and #161 decision memo packet. |
| [Equilibrium relevance probe for Picard closure error plan](../../plans/2026-06-04-m8-python-toybox-equilibrium-relevance-probe-for-picard-closure-error-plan.md) | derivative and property plans | Build a small objective/Jacobian/Hessian probe without creating M4 route behavior. |
| [CppAD-shaped Picard property and derivative evidence plan](../../plans/2026-06-04-m8-python-toybox-cppad-shaped-picard-property-derivative-evidence-plan.md) | derivative, saturation, and equilibrium-probe plans | Build broader pure/mixture property evidence plus JAX derivative evidence shaped like future CppAD provider blocks. |
| [Picard stress evidence to rescue or retire plan](../../plans/2026-06-05-m8-python-toybox-picard-stress-evidence-to-rescue-or-retire-plan.md) | issue #223 evidence | Run harsh post-#223 stress evidence that can rescue Picard for more M8 research or retire it cleanly. |

## Current Artifacts

| Artifact | Status | Summary |
| --- | --- | --- |
| [Picard stress evidence](../../../../analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/output/picard_stress_evidence.csv) | retained | Full 66-case, 25-policy stress matrix with exact implicit rows, Picard rows, relative errors, and simulation timing. |
| [Picard stress decision memo](../../../../analyses/package_validation/explicit_association_toybox/docs/picard_stress_rescue_or_retire_decision.md) | retained | M8-only decision memo selecting `retire_picard` under the stress gates. |

## Current Issues

| Issue | Status | Depends On | Summary |
| --- | --- | --- | --- |
| [#221](https://github.com/ePC-SAFT/ePC-SAFT/issues/221) | closed | none | Hardened Picard autodiff and exact implicit sensitivity baselines in the Python toybox. |
| [#222](https://github.com/ePC-SAFT/ePC-SAFT/issues/222) | closed | none | Added associating-compound pressure-density validation with honest data points and dotted exact-vs-Picard curves. |
| [#223](https://github.com/ePC-SAFT/ePC-SAFT/issues/223) | closed | #231 | Produced the final Picard fixed-grid relative-error and simulation-timing packet for #161 disposition. |
| [#224](https://github.com/ePC-SAFT/ePC-SAFT/issues/224) | closed | none | Probed whether Picard closure error is dangerous for later equilibrium objective, Jacobian, and Hessian work. |
| [#227](https://github.com/ePC-SAFT/ePC-SAFT/issues/227) | closed | none | Added a SciPy pure-component saturation solver so toybox pressure plots become true vapor-pressure predictions. |
| [#231](https://github.com/ePC-SAFT/ePC-SAFT/issues/231) | closed | #227 | Evaluated Picard explicit-association step-count and damping policy grids with CppAD-shaped handoff evidence. |

## Closed Issues

- [https://github.com/ePC-SAFT/ePC-SAFT/issues/222](https://github.com/ePC-SAFT/ePC-SAFT/issues/222) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/226](https://github.com/ePC-SAFT/ePC-SAFT/pull/226) on 2026-06-04
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/224](https://github.com/ePC-SAFT/ePC-SAFT/issues/224) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/229](https://github.com/ePC-SAFT/ePC-SAFT/pull/229) on 2026-06-05
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/227](https://github.com/ePC-SAFT/ePC-SAFT/issues/227) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/229](https://github.com/ePC-SAFT/ePC-SAFT/pull/229) on 2026-06-05
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/231](https://github.com/ePC-SAFT/ePC-SAFT/issues/231) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/232](https://github.com/ePC-SAFT/ePC-SAFT/pull/232) on 2026-06-05
- [https://github.com/ePC-SAFT/ePC-SAFT/issues/223](https://github.com/ePC-SAFT/ePC-SAFT/issues/223) closed by [https://github.com/ePC-SAFT/ePC-SAFT/pull/233](https://github.com/ePC-SAFT/ePC-SAFT/pull/233) on 2026-06-05

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
