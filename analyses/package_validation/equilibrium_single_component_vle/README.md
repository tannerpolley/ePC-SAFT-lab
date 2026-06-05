# Equilibrium Single-Component VLE Validation

This package-validation analysis records public `epcsaft-equilibrium` single-component VLE route behavior against reusable pure-component NIST saturation rows.

The figure-owned workflow lives in `figures/hydrocarbon_saturation_pressure/`:

- `scripts/generate_data.py` runs `Equilibrium(mixture, route="single_component_vle", T=...).solve()` for methane, ethane, and propane.
- `scripts/render_figure.py` renders the retained pressure, pressure-error, and saturated-liquid-density-error plot from generated CSV output.
- `results/` contains the generated route comparison table, plotted-data snapshot, Matplotlib sidecar, and rendered SVG/PNG.

`figures/associating_saturation_scope/` records the available water and
methanol NIST saturation-pressure and saturated-liquid-density rows from
`data/reference/pure_component/saturation_density/`. It verifies that the
production route rejects the 2B associating Held parameter snapshots rather than
retaining a false fit curve.
