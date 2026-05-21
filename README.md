# epcsaft

`epcsaft` is a Python package for electrolyte PC-SAFT thermodynamic calculations. The public interface is Python, while the equation-of-state runtime and package-owned equilibrium/regression kernels are implemented in native C++ through `pybind11`.

Current release: `1.5.2`

## What This Package Does

Use `epcsaft` when you need to build PC-SAFT/ePC-SAFT mixtures, evaluate thermodynamic states, compute fugacity and activity coefficients, run supported phase-equilibrium workflows, or fit parameter sets against tabular data.

The main user objects are:

- `Mixture`: stores components, parameters, and model options.
- `State`: evaluates density, pressure, residual properties, fugacity coefficients, and derivatives at one thermodynamic condition.
- `Equilibrium`: owns supported phase-equilibrium workflow defaults and solve methods.
- `Regression`: owns supported parameter-regression workflow defaults and fit methods.
- `ParameterSet`, `ModelOptions`, and `create_input_template(...)`: define parameter data, model choices, and user-owned input scaffolds.
- `capabilities()`: reports which runtime and solver paths are available in the current install.

## Install

### From PyPI

The standard install command is:

```powershell
python -m pip install epcsaft
```

With `uv`:

```powershell
uv add epcsaft
```

The current public release is also available from GitHub.

### Install From The GitHub Release

Download the current release from:

<https://github.com/tannerpolley/ePC-SAFT/releases/tag/v1.5.2>

If a wheel matching your Python version and platform is attached to the release, install it directly:

```powershell
python -m pip install C:\path\to\epcsaft-1.5.2-*.whl
```

If you are installing from the release source archive or from the tagged Git source, a native build is required:

```powershell
python -m pip install "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@v1.5.2"
```

With `uv`:

```powershell
uv add "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@v1.5.2"
```

Source builds require Python `>=3.9`, a C++ compiler, CMake, and Ninja or another CMake generator. Python 3.13 is the current project smoke-test baseline.

### Install From A Local Clone

For a normal local source install:

```powershell
git clone https://github.com/tannerpolley/ePC-SAFT.git
cd ePC-SAFT
python -m pip install .
```

For an editable install while changing Python files:

```powershell
python -m pip install -e .
```

Editable installs use the same native build backend as wheel installs. Python source changes are picked up from the checkout. If you change C++ sources, pybind bindings, CMake files, or build metadata, rerun:

```powershell
python -m pip install -e .
```

With `uv`, use:

```powershell
uv pip install -e .
```

### Native IPOPT SDK Support

IPOPT support is a native build dependency for constrained-NLP equilibrium routes. On Windows, the local SDK root `%USERPROFILE%\Documents\deps\ipopt-msvc` is the preferred source. Source and editable installs pick it up automatically when that directory exists; otherwise point the build backend at an Ipopt install root explicitly:

```powershell
$env:EPCSAFT_PEP517_IPOPT_ROOT = "$env:USERPROFILE\Documents\deps\ipopt-msvc"
python -m pip install "epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@v1.5.2"
```

Use `EPCSAFT_PEP517_IPOPT_DIR` instead when the install provides an `IpoptConfig.cmake` directory. Runtime processes that execute Ipopt on Windows must expose the SDK `bin` directory through both `PATH` and `EPCSAFT_RUNTIME_DLL_DIRS`; repo build scripts do this automatically for the local SDK.

IPOPT is never selected automatically by `solver_backend="auto"`. Use explicit Ipopt-backed routes or explicit solver options when validating native constrained-NLP behavior.

## Architecture And Diagnostics

The documentation includes short reference pages for the package architecture, parameter schema, equilibrium problem objects, and diagnostics:

- `docs/pages/package_architecture.rst`
- `docs/pages/parameter_schema.rst`
- `docs/pages/equilibrium_architecture.rst`
- `docs/pages/diagnostics.rst`

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
print(state.z())                        # Z
print(state.ares())                     # residual Helmholtz energy
print(state.fugacity_coefficients())    # phi_i
```

## Pressure, Density, And `rho_guess`

State construction uses exactly one closure variable:

- `State(..., P=...)` solves the EOS pressure-density closure.
- `State(..., rho=...)` evaluates properties at the supplied molar density.
- `State(..., P=..., rho_guess=...)` still solves exact pressure closure, but seeds the density solve with a previous good density.

For repeated calculations at nearby conditions, reuse the previous accepted pressure-state density:

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

Most users should create and own their parameter folders:

```python
from epcsaft import create_input_template

template_root = create_input_template(
    r"C:\path\to\my_epcsaft_data\water_salt_case",
    components=["H2O", "Na+", "Cl-"],
)
```

After filling in the generated files, load the tables in your own workflow and
construct a `ParameterSet` from the records, then pass it to `Mixture`:

```python
import numpy as np
from epcsaft import Mixture, ParameterSet, State

species = ["H2O", "Na+", "Cl-"]
parameters = ParameterSet.from_records(pure_records=loaded_pure_records, binary_records=loaded_binary_records)
mixture = Mixture(parameters, components=species)
state = State(mixture, T=298.15, P=101325.0, x=np.asarray([0.9998, 1e-4, 1e-4]))
```

The source checkout contains reference/example datasets under `data/reference/epcsaft_parameters/`. Those folders are useful for comparison, validation, and paper-reproduction workflows. Do not assume every installed wheel contains those source-checkout reference folders.

## Equilibrium And Speciation

Use `capabilities()` and the documentation before wiring a high-level equilibrium workflow. The package includes native-backed paths for neutral phase equilibrium, electrolyte LLE, fixed-liquid electrolyte bubble pressure, reactive speciation, reactive staged equilibrium, and scoped reactive electrolyte bubble pressure.

Important boundaries:

- Electrolyte bubble pressure is for fixed liquid composition with neutral vapor species; ions remain liquid-only.
- Reactive electrolyte bubble pressure is staged: native speciation first, then fixed-liquid electrolyte bubble pressure.
- IPOPT is an optional native dependency; implemented native equilibrium routes use exact Hessians by default when it is compiled, with limited-memory Hessians available only as an explicit solver opt-out.
- Full downstream case-study models should own their own data, balances, run matrices, and acceptance criteria.

For examples, see the equilibrium cookbook:

<https://epcsaft.readthedocs.io/en/latest/equilibrium_cookbook.html>

## Documentation

- User guide: <https://epcsaft.readthedocs.io/en/latest/>
- Parameter templates: <https://epcsaft.readthedocs.io/en/latest/user_parameter_templates.html>
- User options: <https://epcsaft.readthedocs.io/en/latest/user_options.html>
- Equilibrium cookbook: <https://epcsaft.readthedocs.io/en/latest/equilibrium_cookbook.html>
- API reference: <https://epcsaft.readthedocs.io/en/latest/api_reference.html>

For source contributors, see `docs/pages/development_workflows.rst` in the repository. The README intentionally stays focused on package users.

## License

GNU General Public License v3.0. See `LICENSE`.
