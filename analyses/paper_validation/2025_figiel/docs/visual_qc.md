# Figiel 2025 Visual QA

## Figure 1
- Source image checked: `analyses/paper_validation/2025_figiel/figures/figure_01/source/paper_source_01_figiel_2025_figure_002.png`
- Caption/series/axes comparison: Verified the recreated step profile preserves the two-region dielectric schematic, the `r_i` and `r_i + \Delta r_i` break, and the `\epsilon_r / -` axis role.
- Intentional deviations: Rebuilt as a deterministic schematic from staged geometry metadata rather than duplicating paper typography or pixel layout.
- Pass/fail: Pass.

## Figure 2
- Source image checked: `analyses/paper_validation/2025_figiel/figures/figure_02/source/paper_source_01_figiel_2025_figure_003.png`
- Caption/series/axes comparison: Verified four literature marker groups in water and two black model curves over `x_ion` with the same scientific roles and comparable axis limits.
- Intentional deviations: Redrawn in house style from the staged `dielc_salts_in_water.csv` subset rather than matching the paper styling exactly.
- Pass/fail: Pass.

## Figure 3
- Source image checked: `analyses/paper_validation/2025_figiel/figures/figure_03/source/paper_source_01_figiel_2025_figure_004.png`
- Caption/series/axes comparison: Verified gray water circles, blue methanol triangles, green ethanol squares, and one Eq. 11 model curve over `x_ion` and `\epsilon_r / \epsilon_{r,\mathrm{solvent}}`.
- Intentional deviations: Water points come from the staged aqueous dielectric table. Methanol and ethanol points are tracked in `dielc_single_solvent_digitized.csv` as last-resort digitization because cited refs 57-60 were not recoverable locally or as structured tables during a quick targeted source search.
- Pass/fail: Pass.

## Figure 4
- Source image checked: `analyses/paper_validation/2025_figiel/figures/figure_04/source/paper_source_01_figiel_2025_figure_005.png`
- Caption/series/axes comparison: Verified one combined bar figure covering the six ions, literature values, and the two ePC-SAFT model variants with the published solvation-energy role and units.
- Intentional deviations: Retained one combined canonical PNG instead of auxiliary per-panel exports.
- Pass/fail: Pass.

## Figure 5
- Source image checked: `analyses/paper_validation/2025_figiel/figures/figure_05/source/paper_source_01_figiel_2025_figure_006.png`
- Caption/series/axes comparison: Verified two-panel water MIAC comparison for chloride and bromide salts with literature markers and model curves at the published temperature and pressure. Numeric fit-shape check confirms the model curves show the paper's initial `\gamma_{\pm,m}` depression and remain within the Figure 5 gate against the staged literature points.
- Intentional deviations: Retained only the combined canonical figure and removed auxiliary single-panel outputs. The water row in the local Figiel parameter snapshot uses the 2025 Figiel salt-water association/dispersion values evaluated at 298.15 K.
- Pass/fail: Pass.

## Figure 6
- Source image checked: `analyses/paper_validation/2025_figiel/figures/figure_06/source/paper_source_01_figiel_2025_figure_007.png`
- Caption/series/axes comparison: Verified the four transfer-energy panels, literature markers, and fitted model curves with matching axis roles and solvent labels.
- Intentional deviations: Retained only the single four-panel canonical figure and removed methanol-only, ethanol-only, and per-panel helper exports.
- Pass/fail: Pass.

## Figure 7
- Source image checked: `analyses/paper_validation/2025_figiel/figures/figure_07/source/paper_source_01_figiel_2025_figure_008.png`
- Caption/series/axes comparison: Verified the NaBr-in-methanol MIAC redraw with literature points, the Figiel 2025 model line, and the dashed Rule 1 comparison.
- Intentional deviations: Canonical export standardized to PNG.
- Pass/fail: Pass.

## Figure 8
- Source image checked: `analyses/paper_validation/2025_figiel/figures/figure_08/source/paper_source_01_figiel_2025_figure_009.png`
- Caption/series/axes comparison: Verified the three salt panels comparing methanol and ethanol data/model pairs with the same panel grouping, marker roles, and axis ranges.
- Intentional deviations: Retained only the combined canonical figure and removed per-panel helper exports.
- Pass/fail: Pass.

## Figure 9
- Source image checked: `analyses/paper_validation/2025_figiel/figures/figure_09/source/paper_source_01_figiel_2025_figure_010.png`
- Caption/series/axes comparison: Verified the four aqueous-organic MIAC panels for NaBr and NaCl at the staged salt-free organic weight fractions, with marker/curve roles preserved. Numeric fit-shape check confirms the 40 wt% model curves decrease from the infinite-dilution reference instead of rising above one.
- Intentional deviations: Retained only the combined four-panel canonical figure and removed auxiliary panel and 40 wt% helper exports from the validation package.
- Pass/fail: Pass.
