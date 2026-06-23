# Pure Component Saturation-Properties Reference Data

This folder owns reusable pure-component saturation-pressure and saturated
liquid-density input tables.

Layout:

- `<component>/saturation_properties.csv`
  - component-owned saturation-property rows.
  - Source provenance belongs in row fields such as `source_name` and
    `source_url`, not in the folder or filename.
- `<component>/data_request_manifest.csv`
  - optional source-request status for the same component.

Do not create combined component filenames such as `water_methanol_*.csv`.
Split reusable pure-component data by component and keep source identity in the
rows.
