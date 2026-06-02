# Provider Package Instructions

This subtree owns the core `epcsaft` provider package: `Mixture`, `State`,
`ParameterSet`, `ModelOptions`, EOS/property evaluation, provider-native
`_core`, CppAD derivative substrate, provider capability evidence, and the
provider SDK.

Do not add equilibrium route assembly, Ipopt ownership, Ceres optimizer logic,
or regression workflow behavior here. If provider work appears to require
those, split the issue by package and milestone.

Provider public derivatives must remain CppAD-backed where public payloads
claim derivative support. Missing derivative coverage is an implementation
gap, not a runtime mode.

Keep native SDK manifests, CMake source lists, pybind bindings, `.pyi`
surfaces, and provider tests aligned when moving native or public-provider
code.

Focused validation:
- `uv run python run_pytest.py --provider-api -q`
- `uv run python run_pytest.py --native -q`
- `uv run python scripts/dev/build_epcsaft.py --clean --profile provider`
