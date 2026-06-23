# Neutral Pure-Component Regression Basis

This folder is the phase-1 data foundation for neutral-component regression of `m`, `s`, and `e`.

Current scope:

- species: `Methane`, `Ethane`, `Propane`
- target parameters from the workbook: `m`, `s`, `e`
- property data basis: saturation properties under `saturation_properties/`
  and figure/source-specific saturation-density traces under
  `saturation_density/`

Files:

- `hydrocarbon_basis_workbook_reference.csv`
  - workbook reference targets for `m`, `s`, and `e`
- `saturation_properties/<component>/saturation_properties.csv`
  - component-owned public saturation-pressure and saturated-liquid-density
    rows used by package validation.
  - Source provenance belongs in row fields such as `source_name` and
    `source_url`, not in the filename.
- `saturation_density/<component>/saturation_density.csv`
  - component-owned pure-component saturation-density reference rows used by
    paper-validation figures or package validation.
- `association_aad/<component>/association_aad.csv`
  - component-owned pure-association AAD reference rows used by association
    validation gates.
- `saturation_properties/<component>/data_request_manifest.csv`
  - source-request status for component-owned public saturation-property data.

Notes:

- The saturation-properties CSV files were collected from public
  fluid-property tables using saturation-property queries over explicit
  temperature grids.
- These are trusted NIST thermophysical-property values and are suitable as an initial neutral-only fitting basis.
- They are not a substitute for a literature-curated experimental regression dataset if the goal is paper-grade parameter validation.
- Component-scoped reference folders must not be named after author/year or
  paper-validation context. Keep source provenance in columns such as
  `source_reference`, `source_document`, and `source_method`.
- The workbook reference file is taken from:
  - `workbooks/PC-SAFT Calculations - Hydrocarbon Basis.xlsm`
  - sheet: `PC-SAFT Liquid`
  - species row: `B13:D13`
  - `m`: `B16:D16`
  - `s`: `B17:D17`
  - `e`: `B18:D18`
