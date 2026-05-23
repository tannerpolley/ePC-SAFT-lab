# Analysis Workflows

This directory contains source-controlled scientific analysis, validation, and figure workflows that are useful for developing and checking `epcsaft` but are not package runtime code.

The analysis taxonomy is:

```text
analyses/
  _template/
  paper_validation/
    <paper_id>/
  data_validation/
  package_validation/
```

Each real analysis should be self-contained inside one of those category folders:

```text
analyses/<category>/<short_id>/
  README.md
  analysis.yaml
  config/
  scripts/
  figures/
    <figure_id>/
      input/
      output/
      scripts/
  notebooks/
  tests/
```

Only create optional folders when the analysis needs them. Stable literature inputs that are reused by multiple analyses belong under `data/reference/`; analysis-specific inputs stay local under the owning `figures/<figure_id>/input/` folder for non-paper analyses.

Generated figure-local run payloads belong under `figures/<figure_id>/output/runs/` and are ignored for non-paper analyses. Retained model CSVs, plotted data snapshots, rendered figures, and `.mpl.yaml` sidecars belong together under the owning `figures/<figure_id>/output/` folder. Paper-validation roots are the explicit exception: they use `figures/<figure_id>/source/`, `figures/<figure_id>/results/`, top-level `tables/table_###/`, `docs/`, `parameters/`, `scripts/`, and `shared/`. The package-level `scripts/` directory is reserved for repo tooling such as builds, validation, data curation, packaging, and docs.
