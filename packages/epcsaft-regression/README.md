# epcsaft-regression

Monorepo transition package for the Ceres-backed regression extension.

Use `from epcsaft_regression import Regression` for the current regression
workflow object and related fitting helpers. This checkout consumes the
provider SDK and its own package-owned native module; Ceres symbols are no
longer exported by the provider `_core`.

This package is not a standalone PyPI artifact in the current tranche. Install
it through the repository uv workspace so it uses the matching `epcsaft`
provider SDK and the package-owned native module built with
`EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE=ON`.
