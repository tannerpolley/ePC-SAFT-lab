# Changelog

## 0.2.0 - 2026-05-21

### Changed

- Reset the independent package release line to `0.2.0` after unforking the project.
- Reworked GitHub Actions around the current Windows support baseline and current public API names.
- Updated release installation docs and README wording so PyPI is not claimed as available before the `epcsaft` project exists on PyPI.

## 0.1.2 - 2026-05-10

### Highlights

- Added a GitHub Actions workflow for PyPI Trusted Publishing.
- Added release/tag and manual-dispatch publishing paths for PyPI.
- Updated README and installation docs so PyPI is the primary install path once publishing is live.

## 0.1.1 - 2026-05-10

### Highlights

- Added PEP 660 editable-install support through the custom build backend.
- Documented `python -m pip install -e .` and `uv pip install -e .` as supported local development paths.
- Simplified the user-facing README and getting-started docs so install, editable install, first calculation, parameter folders, and next steps are easier to find.
- Moved maintainer and troubleshooting workflows out of the primary quick-start path.

## 0.1.0 - 2026-05-10

First official source-release baseline for `epcsaft`.

### Highlights

- Native C++ runtime exposed through the Python `epcsaft` API.
- Public mixture/state API with pressure closure, direct-density closure, `rho_guess` continuation, and density-consistency diagnostics.
- Native-backed fugacity, activity, residual-property, and runtime diagnostic calls.
- User-owned parameter-folder workflow with `create_parameter_template(...)` and `ePCSAFTMixture.from_dataset(...)`.
- Supported regression helpers for pure-component, ionic, binary, and scoped electrolyte workflows.
- Native-backed neutral equilibrium, electrolyte LLE, fixed-liquid electrolyte bubble pressure, reactive speciation, reactive staged equilibrium, and scoped reactive electrolyte bubble workflows.
- Native system Ipopt discovery is explicit build-gate work for the planned constrained-NLP adapter.

### Distribution

- Package metadata is prepared for the `epcsaft` distribution name.
- Current official install path is GitHub release/tag installation.
- `README.md` and the Sphinx overview describe release installation without assuming PyPI is already published.
- Source distributions explicitly include `README.md` and `LICENSE`.
