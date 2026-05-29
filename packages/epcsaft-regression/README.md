# epcsaft-regression

Monorepo transition package for the Ceres-backed regression extension.

Use `from epcsaft_regression import Regression` for the current regression
workflow object and related fitting helpers. This checkout still consumes a
transition provider-native bridge while the native/provider contract is
tightened, but the source ownership now lives here instead of under the core
provider package.

This package is not a standalone PyPI artifact in the current tranche. Install
it through the repository uv workspace so it uses the matching `epcsaft`
provider build with `EPCSAFT_ENABLE_REGRESSION_NATIVE=ON`.
