from __future__ import annotations


def test_dependency_probe_uses_cppad_and_imports_cyipopt() -> None:
    from cython_held2_experiment import dependency_probe

    result = dependency_probe()

    assert result["cppad_value"] == 9.0
    assert result["cppad_jacobian"] == 6.0
    assert result["cyipopt_module"] == "cyipopt"
