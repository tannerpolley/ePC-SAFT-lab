# Changelog

## 0.2.0 - 2026-05-21

### Changed

- Documented the current public package surface: `ParameterSet`, `ModelOptions`, `Mixture`, `State`, `Equilibrium`, `Regression`, `create_input_template(...)`, `runtime_build_info()`, and `capabilities()`.
- Limited release claims to the current production-exposed equilibrium families: constructor-configured neutral bubble/dew routes and neutral TP flash when the native Ipopt dependency is available.
- Kept native package builds on the Windows Ceres/CppAD baseline and made Ipopt an explicit optional native dependency for source/editable builds and hosted CI.
- Prepared Windows CPython 3.13 release artifacts and a manual PyPI Trusted Publishing workflow for use after the PyPI pending publisher exists.
- Updated release installation docs and README wording so GitHub release wheels are the current install path until the `epcsaft` project exists on PyPI.

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
- User-owned parameter-folder workflow for source-checkout parameter data.
- Native-backed regression and equilibrium work that fed the current capability registry.
- Source-checkout contracts for neutral equilibrium and additional route-family diagnostics that remain controlled by `capabilities()`.
- Native system Ipopt discovery is explicit build-gate work for the planned constrained-NLP adapter.

### Distribution

- Package metadata is prepared for the `epcsaft` distribution name.
- Current official install path is GitHub release/tag installation.
- `README.md` and the Sphinx overview describe release installation without assuming PyPI is already published.
- Source distributions explicitly include `README.md` and `LICENSE`.
