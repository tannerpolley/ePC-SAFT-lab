`generate_clean_literature_overlays.py` regenerates the retained literature-table
overlay CSVs, dense smooth-curve plotted-data snapshots, fit-statistics files,
and PNG/SVG plots for Gross 2002 Figures 2-10.

The harder missing-source-data figures are rechecked with the user-level
`consensus-figure-digitizer` skill, driven by
`shared/source/gross_2002_hard_case_digitization_manifest.csv`. The skill-owned
utility refines figure-local calibrated source points against visible paper ink
and writes per-figure CSV/QA overlay artifacts plus a shared score summary.

Figure-local script folders are retained under `figures/figure_*/scripts/`.
