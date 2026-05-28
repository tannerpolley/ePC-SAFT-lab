# epcsaft-regression

Sibling repo for the Ceres-backed regression extension.

Use `from epcsaft_regression import Regression` for the current regression
workflow object and related fitting helpers. This checkout still consumes some
provider-private seams while the native/provider contract is tightened, but the
source ownership now lives here instead of under the core provider repo.
