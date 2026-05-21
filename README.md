# epcsaft

`epcsaft` is a Windows-first Python package for PC-SAFT and electrolyte PC-SAFT thermodynamic calculations. The public API is Python; the equation-of-state runtime and package-owned equilibrium/regression kernels are implemented in native C++ through `pybind11`.

Current package version: `0.2.0`

## What You Can Use It For

- Build PC-SAFT/ePC-SAFT mixtures from user-owned parameter data.
- Evaluate pressure, density, residual properties, fugacity coefficients, activity coefficients, and derivatives.
- Run supported neutral and electrolyte phase-equilibrium workflows.
- Run supported parameter-regression workflows.
- Inspect runtime capabilities with `capabilities()` before selecting optional native solver paths.

The main public objects are `ParameterSet`, `ModelOptions`, `Mixture`, `State`, `Equilibrium`, `Regression`, and `create_input_template(...)`.

## Install

### GitHub Release

The `v0.2.0` GitHub release should be published after final review:

<https://github.com/tannerpolley/ePC-SAFT/releases/tag/v0.2.0>

After that release exists, Windows users can download the wheel matching their Python version and install it directly:

```powershell
python -m pip install C:\path\to\epcsaft-0.2.0-*.whl
```

The automated wheel baseline is Windows CPython 3.13.

### PyPI

PyPI publishing is configured through GitHub Actions. When the project page is live at <https://pypi.org/project/epcsaft/>, install with:

```powershell
python -m pip install epcsaft
```

With `uv`:

```powershell
uv add epcsaft
```

If PyPI returns 404 for `epcsaft`, use the GitHub release wheel above.

### Tagged Source

After the `v0.2.0` tag exists, source installs build the native extension locally and require Python `>=3.9`, a C++ compiler, CMake, and Ninja or another CMake generator:

```powershell
python -m pip install "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@v0.2.0"
```

With `uv`:

```powershell
uv add "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@v0.2.0"
```

### Local Clone

For a local source install:

```powershell
git clone https://github.com/tannerpolley/ePC-SAFT.git
cd ePC-SAFT
python -m pip install .
```

For editable development:

```powershell
python -m pip install -e .
```

Editable installs use the same native build backend as wheel installs. If you change C++ sources, pybind bindings, CMake files, or build metadata, rerun the editable install command so the native extension is rebuilt.

## Verify The Install

```python
import epcsaft

print(epcsaft.__version__)
print(epcsaft.runtime_build_info())
print(epcsaft.capabilities())
```

## Quick Example

```python
import numpy as np
from epcsaft import Mixture, ParameterSet, State

parameters = ParameterSet.from_dict(
    {
        "MW": np.asarray([92.1405e-3]),
        "m": np.asarray([2.8149]),
        "s": np.asarray([3.7169]),
        "e": np.asarray([285.69]),
    },
    species=["Toluene"],
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

After filling in the generated files, load the tables in your workflow and construct a `ParameterSet`, then pass it to `Mixture`:

```python
import numpy as np
from epcsaft import Mixture, ParameterSet, State

species = ["H2O", "Na+", "Cl-"]
parameters = ParameterSet.from_records(
    pure_records=loaded_pure_records,
    binary_records=loaded_binary_records,
)
mixture = Mixture(parameters, components=species)
state = State(mixture, T=298.15, P=101325.0, x=np.asarray([0.9998, 1e-4, 1e-4]))
```

The source checkout contains reference/example datasets under `data/reference/epcsaft_parameters/`. Do not assume every installed wheel contains those source-checkout reference folders.

## Optional Ipopt Support

Ipopt is an optional native dependency for constrained-NLP equilibrium routes. On Windows, source and editable installs automatically use the local SDK at `%USERPROFILE%\Documents\deps\ipopt-msvc` when that directory exists. Otherwise point the build backend at an Ipopt install root:

```powershell
$env:EPCSAFT_PEP517_IPOPT_ROOT = "$env:USERPROFILE\Documents\deps\ipopt-msvc"
python -m pip install "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@v0.2.0"
```

Use `EPCSAFT_PEP517_IPOPT_DIR` instead when the install provides an `IpoptConfig.cmake` directory. Runtime processes that execute Ipopt on Windows must expose the SDK `bin` directory through both `PATH` and `EPCSAFT_RUNTIME_DLL_DIRS`; repo build scripts do this automatically for the local SDK.

Ipopt is not selected automatically by `solver_backend="auto"`. Use explicit Ipopt-backed routes or solver options when validating constrained-NLP behavior.

## Documentation

- User guide: <https://epcsaft.readthedocs.io/en/latest/>
- Parameter templates: <https://epcsaft.readthedocs.io/en/latest/user_parameter_templates.html>
- User options: <https://epcsaft.readthedocs.io/en/latest/user_options.html>
- Equilibrium cookbook: <https://epcsaft.readthedocs.io/en/latest/equilibrium_cookbook.html>
- API reference: <https://epcsaft.readthedocs.io/en/latest/api_reference.html>

For source contributors, see `docs/pages/development_workflows.rst` in the repository. The README intentionally stays focused on package users.

## License

GNU General Public License v3.0. See `LICENSE`.
