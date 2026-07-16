# epcsaft

> [!IMPORTANT]
> This is the preserved legacy/lab repository for the original ePC-SAFT
> monorepo. v0.2.0 is historical lab evidence retained in this archive. This
> This lab does not publish packages to PyPI or own production release
> authority.
> Clean production packages are migrated separately and do not inherit this
> repository's runtime authority automatically.

`epcsaft` is a Windows-first Python package for PC-SAFT and electrolyte PC-SAFT thermodynamic calculations. The public API is Python; the equation-of-state runtime is implemented in native C++ through `pybind11`.

This release is still a monorepo transition build. Ipopt-backed equilibrium is
owned by `epcsaft-equilibrium`, and Ceres-backed regression is owned by
`epcsaft-regression`. Those extension packages are workspace-transition
packages in this tranche; install them from this checkout, not against a
provider-only `epcsaft` wheel.

Historical package evidence: `0.2.0`

## What You Can Use It For

- Build PC-SAFT/ePC-SAFT mixtures from user-owned parameter data.
- Evaluate pressure, density, residual properties, fugacity coefficients, activity coefficients, and derivatives.
- Use the constructor-configured `bubble_pressure`, `dew_pressure`, and scoped
  nonassociating hydrocarbon `single_component_vle` routes from
  `epcsaft_equilibrium` when the package is built with optional native Ipopt.
- Run supported pure-neutral parameter-regression workflows from `epcsaft_regression`.
- Inspect each package's `capabilities()` report before selecting optional native solver paths.

The main provider objects are `ParameterSet`, `ModelOptions`, `Mixture`,
`State`, and `create_input_template(...)`. Import `Equilibrium` from
`epcsaft_equilibrium` and `Regression` from `epcsaft_regression`.

## Historical v0.2.0 evidence

The `v0.2.0` GitHub release is historical lab evidence: a Windows CPython 3.13
wheel and source archive retained at:

<https://github.com/tannerpolley/ePC-SAFT-lab/releases/tag/v0.2.0>

This archive does not claim a current clean-package release. Use the retained
artifacts for historical inspection or build/install the packages locally.

### Historical wheel

Windows users on Python 3.13 can download the wheel and install it directly:

```powershell
python -m pip install C:\path\to\epcsaft-0.2.0-*.whl
```

Use the historical wheel only as archived evidence; this lab has no PyPI
publication path.

### Tagged Source

The `v0.2.0` tag supports source installs that build the native extension locally. Source installs require Python `>=3.9`, a C++ compiler, CMake, and Ninja or another CMake generator:

```powershell
python -m pip install "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT-lab.git@v0.2.0#subdirectory=packages/epcsaft"
```

With `uv`:

```powershell
uv add "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT-lab.git@v0.2.0#subdirectory=packages/epcsaft"
```

### Local Clone

For a local source install:

```powershell
git clone https://github.com/tannerpolley/ePC-SAFT-lab.git ePC-SAFT-lab
cd ePC-SAFT-lab
python -m pip install packages/epcsaft
```

For editable development:

```powershell
python -m pip install -e packages/epcsaft
```

Editable installs use the same native build backend as wheel installs. If you change C++ sources, pybind bindings, CMake files, or build metadata, rerun the editable install command so the native extension is rebuilt.

Equilibrium and regression workflows live in the monorepo workspace packages
under `packages/`. In a source checkout, use the uv workspace environment before
importing `epcsaft_equilibrium` or `epcsaft_regression`. Do not install these
transition packages against provider-only `epcsaft` wheels; they require the
matching workspace provider build with the relevant native symbols enabled.
Retired sibling extension checkouts are not part of the current development,
release, or install-proof workflow.

## Verify The Install

```python
import epcsaft
import epcsaft_equilibrium
import epcsaft_regression

print(epcsaft.__version__)
print(epcsaft.runtime_build_info())
print(epcsaft.capabilities())
print(epcsaft_equilibrium.capabilities())
print(epcsaft_regression.capabilities())
```

## Quick Example

```python
import numpy as np
from epcsaft import Mixture, ParameterSet, State

parameters = ParameterSet.from_dict(
    {
        "schema": "epcsaft.parameter-set",
        "schema_version": 2,
        "components": ["Toluene"],
        "pure_records": [
            {
                "component": "Toluene",
                "molar_mass": 92.1405e-3,
                "molar_mass_units": "kg/mol",
                "m": 2.8149,
                "sigma": 3.7169,
                "epsilon_k": 285.69,
                "charge": 0.0,
                "epsilon_k_ab": 0.0,
                "kappa_ab": 0.0,
                "association_scheme": None,
                "association_sites": [],
                "relative_permittivity": 1.0,
                "born_diameter": 0.0,
                "solvation_factor": 1.0,
            }
        ],
        "interactions": [],
        "interaction_policies": [],
        "metadata": {
            "source": "Gross and Sadowski (2001), Table 2",
            "source_backed": True,
            "auxiliary_neutral_fields": "equation_structural_neutral_inactive",
        },
    }
)
mixture = Mixture(parameters)

state = State(mixture, T=320.0, x=np.asarray([1.0]), P=101325.0)

print(state.density())                  # mol/m^3
print(state.pressure())                 # Pa
print(state.z())                        # compressibility factor
print(state.ares())                     # residual Helmholtz energy
print(state.fugacity_coefficients())    # phi_i
```

## Pressure And Density

`State` uses one closure variable:

- `State(..., P=...)` solves the EOS pressure-density closure.
- `State(..., rho=...)` evaluates properties at the supplied molar density.
- `State(..., P=..., rho_guess=...)` solves pressure closure using a previous good density as the initial guess.

For repeated calculations at nearby conditions:

```python
base = State(mixture, T=320.0, x=np.asarray([1.0]), P=101325.0)
next_state = State(
    mixture,
    T=321.0,
    x=np.asarray([1.0]),
    P=101325.0,
    rho_guess=base.density(),
)
```

To check whether an externally supplied density is pressure-consistent:

```python
density_state = State(mixture, T=320.0, x=np.asarray([1.0]), rho=base.density())
print(density_state.pressure() - 101325.0)
```

## Parameter Data

Most users should own their parameter folders:

```python
from epcsaft import create_input_template

template_root = create_input_template(
    r"C:\path\to\my_epcsaft_data\water_salt_case",
    components=["H2O", "Na+", "Cl-"],
)
```

The generated `parameter_set.json` contains no scientific numbers. Fill every
required value and its source before loading it; missing values fail with the
component and field name. Then pass the loaded `ParameterSet` to `Mixture`:

```python
import numpy as np
from epcsaft import Mixture, ParameterSet, State

species = ["H2O", "Na+", "Cl-"]
parameters = ParameterSet.from_records(
    pure_records=loaded_pure_records,
    interactions=loaded_interactions,
    interaction_policies=loaded_interaction_policies,
)
mixture = Mixture(parameters, components=species)
state = State(mixture, T=298.15, P=101325.0, x=np.asarray([0.9998, 1e-4, 1e-4]))
```

Full paper-validation parameter snapshots live under `analyses/paper_validation/<paper_id>/parameters/`.

## Optional Ipopt Support

Ipopt is an optional native dependency for constrained-NLP equilibrium routes in
the current transition build. Long term, Ipopt belongs to the
`epcsaft-equilibrium` extension package. On Windows, source and editable
installs automatically use the local SDK at
`%USERPROFILE%\Documents\deps\ipopt-msvc` when that directory exists. Otherwise
point the build backend at an Ipopt install root:

```powershell
$env:EPCSAFT_PEP517_IPOPT_ROOT = "$env:USERPROFILE\Documents\deps\ipopt-msvc"
python -m pip install "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT-lab.git@v0.2.0"
```

Use `EPCSAFT_PEP517_IPOPT_DIR` instead when the install provides an `IpoptConfig.cmake` directory. Runtime processes that execute Ipopt on Windows must expose the SDK `bin` directory through both `PATH` and `EPCSAFT_RUNTIME_DLL_DIRS`; repo build scripts do this automatically for the local SDK.

The public equilibrium API does not expose a solver-backend selector. Import
`Equilibrium` from `epcsaft_equilibrium` and use the certified route specs and
ordinary solver tolerances when validating constrained-NLP behavior. The
currently exposed route names are `bubble_pressure`, `dew_pressure`, and scoped
nonassociating hydrocarbon `single_component_vle`. Neutral LLE remains an
internal validation path because its sampled-candidate Stage II audit is not a
global HELD proof.

## Documentation

- User guide: <https://epcsaft.readthedocs.io/en/latest/>
- Parameter templates: <https://epcsaft.readthedocs.io/en/latest/user_parameter_templates.html>
- User options: <https://epcsaft.readthedocs.io/en/latest/user_options.html>
- Equilibrium cookbook: <https://epcsaft.readthedocs.io/en/latest/equilibrium_cookbook.html>
- API reference: <https://epcsaft.readthedocs.io/en/latest/api_reference.html>

For source contributors, see `docs/pages/development_workflows.rst` in the repository. The README intentionally stays focused on package users.

## License

GNU General Public License v3.0. See `LICENSE`.
