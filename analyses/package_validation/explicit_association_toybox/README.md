# Explicit Association Closure Toybox

This analysis compares explicit PC-SAFT association closures against an
independent Python exact mass-action baseline. It is package-validation
analysis code, not package runtime code.

## Commands

- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/residual_ares_error/scripts/render_figure.py`
- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`

## Boundary

The analysis may import NumPy, Matplotlib, and existing package APIs. It must
not add provider C++, public API, equilibrium, regression, or dependency
behavior.

HC and dispersion are scalar fixed-state context terms for total `ares`
comparison. They do not solve density, pressure, or phase roots.

## Outputs

Retained model CSVs, plotted data snapshots, rendered figures, and MPLGallery
sidecars live under `figures/closure_accuracy/output/`. Disposable run payloads,
if added later, belong under `figures/closure_accuracy/output/runs/` and remain
ignored.
