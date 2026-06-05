# Pure Component Saturation And Density Reference Data

This folder owns reusable pure-component saturation-pressure and
saturated-liquid-density input tables.

Files:

- `methane_nist_saturation.csv`
- `ethane_nist_saturation.csv`
- `propane_nist_saturation.csv`
  - NIST Chemistry WebBook saturation tables for the neutral hydrocarbon route
    validation.
  - Density units: `rho_sat_liq_kg_m3`.
- `water_methanol_nist_saturation.csv`
  - NIST Chemistry WebBook liquid saturation rows for explicit-association
    toybox diagnostics.
  - Density units: `rho_sat_liq_mol_m3`.
- `water_methanol_data_request_manifest.csv`
  - request/source status for the public water and methanol saturation rows.

Generated model outputs and exact plotted-data snapshots stay with their owning
analysis figure `results/` or `output/` folders.
