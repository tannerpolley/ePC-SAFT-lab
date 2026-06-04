# Reference Specimens

This folder stores frozen legacy inputs used to inspect behavior while building
the explicit association toybox. Reference files are not imported by analysis
scripts and should not be edited to add new toybox behavior.

## Files

- `legacy_pcsaft_electrolyte.py`: copied from
  `C:\Users\Tanner\Documents\Workspaces\Engineering\MEA-Thermodynamics\archive\legacy_scripts\pcsaft_models_polley\pcsaft_electrolyte.py`.
  The toybox ports only the useful pressure-density ideas: `P = rho R T Z`,
  the liquid density seed based on `eta = 0.5`, and explicit density-root
  diagnostics. It does not inherit the broader electrolyte, fitting, or legacy
  solver surface.
