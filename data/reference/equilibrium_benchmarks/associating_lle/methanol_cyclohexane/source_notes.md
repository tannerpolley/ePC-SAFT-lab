# Gross/Sadowski 2002 Methanol/Cyclohexane Associating LLE Source Notes

This fixture uses the retained Gross and Sadowski 2002 paper-validation bundle for issue #145.

Source inputs:

- Pure associating methanol row: `analyses/paper_validation/2002_gross/tables/table_001/table_001.csv`, Table 1, methanol.
- Cyclohexane neutral PC-SAFT row: `analyses/paper_validation/2002_gross/parameters/pure/any_solvent.csv`, sourced there to Gross 2001 Table 2 and the Gross 2002 Table 2 binary context.
- Binary interaction: `analyses/paper_validation/2002_gross/tables/table_002/table_002.csv`, Table 2, methanol-cyclohexane PC-SAFT `k_ij = 0.051`.
- Experimental LLE branch: `analyses/paper_validation/2002_gross/figures/figure_08/source/paper_source_01_gross_2002_figure_008.png`, Figure 8 at `P = 1.013 bar`.

Digitization basis:

- Axis calibration used the visible plot frame: `x_methanol = 0` at pixel `(118, 895)`, `x_methanol = 1` at pixel `(801, 895)`, `T = 0 C` at pixel `(118, 895)`, and `T = 90 C` at pixel `(118, 12)`.
- Rows in `experimental_phase_points.csv` are rounded visual extractions of the lower liquid-liquid branch points only. They are intended as a source-backed proof target with loose first-gate thresholds, not as a high-precision regression dataset.
- The retained Figure 8 source image has overlapping markers and model curves, so the first #145 branch-comparison threshold is intentionally loose: `max_branch_composition_abs_error = 0.10` and `max_temperature_abs_error_K = 5.0`.

Scope:

- The fixture retains internal associating LLE source data and exact-association derivative evidence.
- Public `Equilibrium(..., route="lle")` is closed because sampled-candidate diagnostics do not establish global HELD phase-set completeness.
- Water/1-pentanol is retained as a later two-associating-component stress case and is not required for this fixture to complete.
