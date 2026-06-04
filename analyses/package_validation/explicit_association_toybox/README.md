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
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_sensitivity/scripts/render_figure.py`
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
- `uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/render_figure.py`
- `uv run python -m analyses.package_validation.explicit_association_toybox.scripts.public_property_sources --allow-network --output analyses/package_validation/explicit_association_toybox/shared/source/public_saturation_properties.csv`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py`
- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`

## Boundary

The analysis may import NumPy, Matplotlib, and existing package APIs. It must
not add provider C++, public API, equilibrium, regression, or dependency
behavior.

HC and dispersion are scalar fixed-state context terms for total `ares`
comparison. They do not solve density, pressure, or phase roots.

Huang/Radosz Table VII rows are treated as exact topology reductions only under
their stated site-interaction assumptions. Closure A is equivalent only for the
one-associating-component 2B donor-acceptor topology. Closure B/C/D comparisons
remain comparisons against the exact mass-action baseline, not new EOS theory.

Public saturation rows are source data for fixed-state diagnostics. The
property residual lane evaluates provider pressure at experimental saturated
liquid density and provider liquid density at experimental saturation pressure;
it does not solve vapor-liquid equilibrium, vapor pressure, bubble/dew routes,
or phase coexistence.

## Derivative And Property Propagation

This toybox section compares exact implicit association against explicit
closure candidates after propagation into local derivatives and EOS-like
property proxies. It remains analysis-only evidence.

- `amortized_timing`: exact implicit timing baseline, closure timing, and speedup by topology.
- `derivative_agreement`: centered perturbation agreement for association, pressure-proxy, composition, chemical-potential-like, and fugacity-like targets.
- `asymmetric_binary_closures`: asymmetric composition, cross-association, inert-component, and water-like topology cases.
- `total_eos_impact`: total neutral `ares`, pressure proxy, chemical-potential proxy, and fugacity proxy ranking.
- `water_topology_fork`: water-specific 3B/4C and fixed-state residual diagnostics.
- `equilibrium_style_objective_sensitivity`: local objective gradient and Hessian-proxy diagnostics for future equilibrium discussions.

The water topology fork is a fixed-state diagnostic. It compares topology and
parameter assumptions against retained pressure and `Z` residuals, but it is
not a VLE validation or saturation solver.

## Outputs

Retained model CSVs, plotted data snapshots, rendered figures, and MPLGallery
sidecars live under each `figures/<figure_id>/output/` folder. Public source CSVs
and source-request status rows live under `shared/source/`. Disposable run
payloads, if added later, belong under a figure-local `output/runs/` folder and
remain ignored.
