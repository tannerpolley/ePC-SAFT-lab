`generate_clean_literature_overlays.py` regenerates the retained
literature-table overlays for Gross 2002 Figures 2-10.

The script reads each figure's canonical `results/model_curve.csv`, writes
`source/literature_points.csv`, rewrites the dense `results/plotted_data.csv`,
and renders `results/figure_NN.{png,svg,pdf}`. Acceptance scores remain in each
figure's `results/fit_statistics.csv`.
