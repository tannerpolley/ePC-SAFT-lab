# epcsaft-equilibrium

Monorepo transition package for the Ipopt-backed equilibrium extension.

Use `from epcsaft_equilibrium import Equilibrium` for constructor-configured
neutral bubble, dew, flash, and nonassociating LLE routes. The extension
depends on the provider package and its `provider_native_sdk()` contract; the
provider root does not re-export `Equilibrium`.

This package is not a standalone PyPI artifact in the current tranche. Install
it through the repository uv workspace so it uses the matching `epcsaft`
provider build with `EPCSAFT_ENABLE_EQUILIBRIUM_NATIVE=ON`.
