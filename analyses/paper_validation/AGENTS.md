# Paper Validation Instructions

Paper-validation analyses are retained literature reproduction workflows and
use the repo-specific exception layout from `docs/pages/project_structure.rst`.

Use `figures/figure_NN/source/` for source assets and
`figures/figure_NN/results/` for retained generated outputs. Use
`tables/table_###/source/` for extracted paper tables and conversions.

Parameter snapshots used to execute the analysis belong directly under
`parameters/mixed/`, `parameters/pure/`, and `parameters/user_options.json`.
Do not add nested dataset-name folders under `parameters/`.

Keep paper source manifests, copied paper notes, plotted data snapshots, and
rendered outputs traceable to the cited source. Application-specific
conclusions remain analysis output, not package capability claims.
