# epcsaft-equilibrium

Workspace package for the Ipopt-backed equilibrium extension.

Use `from epcsaft_equilibrium import Equilibrium` for constructor-configured
neutral bubble, dew, flash, and nonassociating LLE routes. The extension
depends on the provider package and its `provider_native_sdk()` contract; the
provider root does not re-export `Equilibrium`.
