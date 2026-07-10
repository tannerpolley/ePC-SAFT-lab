# epcsaft-equilibrium

Ipopt-backed equilibrium extension package for the ePC-SAFT monorepo.

Use `from epcsaft_equilibrium import Equilibrium` for constructor-configured
`bubble_pressure`, `dew_pressure`, and scoped nonassociating hydrocarbon
`single_component_vle` routes. Neutral LLE, neutral TP flash, and bubble/dew
temperature routes are closed. In particular, the retained neutral-LLE
sampled-candidate Stage II audit is not a global HELD proof. The extension
depends on the provider package and its `provider_native_sdk()` contract; the
provider root does not re-export `Equilibrium`.

This package is not published to PyPI in the current tranche, but it owns its
package-local build metadata and native module. Build proof is repository-owned:

```bash
uv run python scripts/dev/build_extension_dists.py --mode monorepo --package epcsaft-equilibrium
uv run python scripts/dev/build_extension_dists.py --mode installed-provider --package epcsaft-equilibrium
```

The monorepo mode consumes the sibling `packages/epcsaft` provider SDK. The
installed-provider mode consumes the same SDK from an installed provider wheel
or sdist. Both commands discover a shared Linux Ipopt installation; set
`EPCSAFT_IPOPT_ROOT` for an explicit root. Missing SDK metadata or missing
Ipopt configuration fails the build.
