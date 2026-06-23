# Analysis Workflow Instructions

This subtree owns source-controlled scientific analyses, validation studies,
and figure workflows. It is not package runtime code.

Keep each analysis self-contained under `analyses/{category}/{short_id}/`.
Use root `data/reference/` only for reusable stable inputs shared across
analyses or package tests.

Figure-owned layout is:
`figures/{figure_id}/source/`, `figures/{figure_id}/scripts/`, and
`figures/{figure_id}/results/`. Disposable run payloads go under
`figures/{figure_id}/results/runs/`.

Separate data generation from rendering. Retain exact plotted data snapshots
beside rendered SVG, PNG, and PDF figures.

Do not place analysis scripts in root `scripts/`, package `src`, or package
tests. Do not turn downstream metrics into package APIs.
