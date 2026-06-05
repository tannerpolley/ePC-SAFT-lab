# Explicit Association Closure Toybox

This analysis compares explicit PC-SAFT association closures against an
independent Python exact mass-action baseline. It is package-validation
analysis code, not package runtime code.

## Commands

- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/topology_validation_matrix/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/topology_error_heatmaps/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_smoothness/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/timing_pareto/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/timing_repeatability/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/hessian_agreement/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/jax_picard_derivatives/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/quick_phase_equilibrium/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/quick_phase_equilibrium/scripts/render_figure.py`
- `uv run python -m analyses.package_validation.explicit_association_toybox.scripts.public_property_sources --allow-network --output data/reference/pure_component/saturation_density/water_methanol_nist_saturation.csv`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/pure_saturation_validation/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_property_evidence/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/cppad_shaped_picard_derivative_evidence/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/picard_stress_evidence/scripts/render_figure.py`
- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`

## Boundary

The analysis may import NumPy, Matplotlib, and existing package APIs. It must
not add provider C++, public API, equilibrium, regression, or dependency
behavior.

HC and dispersion are scalar fixed-state context terms for total `ares`
comparison. The property residual lane additionally uses them in a toy PC-SAFT
pressure-density coupling for diagnostic density-root checks. That coupling
uses the legacy PC-SAFT liquid packing-fraction seed only as a verified
reference behavior; the toybox keeps a bracketed pure-Python root solve with
recorded bracket policy and pressure-evaluation counts.

Huang/Radosz Table VII rows are treated as exact topology reductions only under
their stated site-interaction assumptions. The only retained explicit
approximation candidate is Picard: seven damped updates with damping `0.5`.

Public saturation rows are source data for fixed-state diagnostics. The
property residual lane evaluates provider pressure/density probes and a
toy PC-SAFT exact-vs-Picard pressure-density coupling at experimental
saturated-liquid density and saturation pressure. It solves fixed-state liquid
density roots, but it does not solve vapor-liquid equilibrium, vapor pressure,
bubble/dew routes, or phase coexistence. Model curves should be read as
fixed-state diagnostic curves until a coexistence solve exists.

The `pure_saturation_validation` lane is the first toybox coexistence solve. It
uses a SciPy pure-component pressure/fugacity-equality solve for exact implicit
association and Picard on the same path. It remains analysis-only evidence and
does not add provider or equilibrium package API behavior.

`scripts/toy_property_eos.py` is the pressure/density playground. It is kept
smaller than the legacy reference script on purpose: hard-chain and dispersion
come from shared scalar kernels, exact implicit and Picard differ only in the
association closure, and mixture cases must provide an explicit composition
vector.

## Derivative And Property Propagation

This toybox section compares exact implicit association against Picard after
propagation into local derivatives and EOS-like property proxies. It remains
analysis-only evidence.

- `amortized_timing`: exact implicit timing baseline, closure timing, and speedup by topology.
- `derivative_agreement`: Picard derivative agreement against exact implicit
  sensitivities. First derivatives of association with respect to density,
  association strength, and binary composition use an implicit-function-theorem
  mass-action Jacobian baseline; pressure/fugacity proxy derivatives retain
  that exact baseline inside centered perturbations.
- `hessian_agreement`: Picard second-derivative agreement for association
  targets. The exact baseline is a centered difference of the exact implicit
  first-derivative functions, with retained mass-action Jacobian condition
  numbers and residual norms.
- `jax_picard_derivatives`: JAX autodiff comparison for Picard first
  derivatives and Hessians. The public figure commands run through the default
  toybox entrypoints; the analysis-only JAX backend still lives in the
  non-default `autodiff` dependency group and is not part of provider runtime
  or the default development group.
- `asymmetric_binary_closures`: asymmetric composition, cross-association, inert-component, and water-like topology cases.
- `total_eos_impact`: total neutral `ares`, pressure proxy, chemical-potential proxy, and fugacity proxy ranking.
- `water_topology_fork`: water-specific 3B/4C and fixed-state residual diagnostics.
- `equilibrium_style_objective_sensitivity`: local objective gradient and Hessian-proxy diagnostics for future equilibrium discussions.
- `quick_phase_equilibrium`: pure-component toy phase-pair pressure and
  reduced-chemical-potential equality residuals. This is a fast exact-vs-Picard
  equilibrium playground, not a provider VLE or saturation validation claim.
- `cppad_shaped_picard_property_evidence`: pure and mixture association case
  matrix comparing exact implicit, Picard NumPy, and Picard JAX values for
  association energy, total residual Helmholtz proxy, pressure proxy,
  fugacity-like proxy, and fixed-density grid status.
- `cppad_shaped_picard_derivative_evidence`: JAX Jacobian, gradient, Hessian,
  Hessian-vector-shaped, and local quadratic diagnostics compared against
  exact implicit finite-difference baselines. This is a CppAD-shaped proxy, not
  provider CppAD proof.
- `picard_stress_evidence`: final post-#223 stress matrix over topology,
  density, temperature, strength, composition, policy-grid timing, property
  proxies, derivative proxies, Hessian proxies, and an M8-only decision memo for
  #161 closure discussion.
- `docs/jax_picard_autodiff_plan.md`: plan for comparing JAX autodiff Jacobians and Hessians of the explicit Picard closure against implicit exact sensitivities.
- `references/legacy_pcsaft_electrolyte.py`: frozen legacy reference specimen used to inspect pressure-density conventions. The toybox ports only the useful pressure and density-root ideas.
- `docs/saturation_property_validation_lane.md`: required contract before plotting exact-vs-Picard saturation pressure or liquid-density model curves.

The water topology fork is a fixed-state diagnostic. It compares topology and
parameter assumptions against retained pressure and `Z` residuals, but it is
not a VLE validation or saturation solver.

## Outputs

Retained model CSVs, plotted data snapshots, rendered figures, and MPLGallery
sidecars live under each `figures/<figure_id>/output/` folder. Public
water/methanol saturation-pressure and saturated-liquid-density source rows live
under `data/reference/pure_component/saturation_density/`. Disposable run
payloads, if added later, belong under a figure-local `output/runs/` folder and
remain ignored.
