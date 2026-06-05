# Neutral Pure-Component Regression Basis

This folder is the phase-1 data foundation for neutral-component regression of `m`, `s`, and `e`.

Current scope:

- species: `Methane`, `Ethane`, `Propane`
- target parameters from the workbook: `m`, `s`, `e`
- property data basis: saturation pressure and saturated liquid density under
  `saturation_density/`

Files:

- `hydrocarbon_basis_workbook_reference.csv`
  - workbook reference targets for `m`, `s`, and `e`
- `saturation_density/methane_nist_saturation.csv`
- `saturation_density/ethane_nist_saturation.csv`
- `saturation_density/propane_nist_saturation.csv`
- `saturation_density/water_methanol_nist_saturation.csv`
  - public NIST Chemistry WebBook saturation-pressure and saturated-liquid
    density rows for the explicit association toybox
- `saturation_density/water_methanol_data_request_manifest.csv`
  - source-request status for the water/methanol public saturation data

Notes:

- The saturation CSV files were collected from the NIST Chemistry WebBook fluid-property tables using saturation-property queries over explicit temperature grids.
- These are trusted NIST thermophysical-property values and are suitable as an initial neutral-only fitting basis.
- They are not a substitute for a literature-curated experimental regression dataset if the goal is paper-grade parameter validation.
- The workbook reference file is taken from:
  - `workbooks/PC-SAFT Calculations - Hydrocarbon Basis.xlsm`
  - sheet: `PC-SAFT Liquid`
  - species row: `B13:D13`
  - `m`: `B16:D16`
  - `s`: `B17:D17`
  - `e`: `B18:D18`
