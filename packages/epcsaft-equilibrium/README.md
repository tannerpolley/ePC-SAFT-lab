# epcsaft-equilibrium

Ipopt-backed equilibrium extension package for the ePC-SAFT monorepo.

Use `from epcsaft_equilibrium import Equilibrium` for constructor-configured
neutral bubble, dew, flash, and nonassociating LLE routes. The extension
depends on the provider package and its `provider_native_sdk()` contract; the
provider root does not re-export `Equilibrium`.

This package is not published to PyPI in the current tranche, but it owns its
package-local build metadata and native module. Build proof is repository-owned:

```powershell
uv run python scripts/dev/build_extension_dists.py --mode monorepo --package epcsaft-equilibrium --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"
uv run python scripts/dev/build_extension_dists.py --mode installed-provider --package epcsaft-equilibrium --ipopt-root "$env:USERPROFILE\Documents\deps\ipopt-msvc"
```

The monorepo mode consumes the sibling `packages/epcsaft` provider SDK. The
installed-provider mode consumes the same SDK from an installed provider wheel
or sdist. Missing SDK metadata or missing Ipopt configuration fails the build.
