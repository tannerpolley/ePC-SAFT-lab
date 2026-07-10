from __future__ import annotations

import hashlib
import importlib
from pathlib import Path
from typing import Any

import epcsaft
import numpy as np
import pytest
from epcsaft._core import NativeValueError
from epcsaft._types import InputError
from epcsaft.state.native_adapter import ePCSAFTMixture
from epcsaft_equilibrium import workflows
from epcsaft_equilibrium._native import extension_native_core

figure01 = importlib.import_module(
    "analyses.paper_validation.2002_gross.figures.figure_01.scripts.generate_data"
)
REPO_ROOT = Path(__file__).resolve().parents[3]
GENERATOR_PATH = (
    REPO_ROOT
    / "analyses"
    / "paper_validation"
    / "2002_gross"
    / "figures"
    / "figure_01"
    / "scripts"
    / "generate_data.py"
)
REGISTER_BINDINGS_PATH = (
    REPO_ROOT
    / "packages"
    / "epcsaft-equilibrium"
    / "src"
    / "epcsaft_equilibrium"
    / "native"
    / "equilibrium"
    / "register_bindings.cpp"
)
RETAINED_PLOT = GENERATOR_PATH.parents[1] / "results" / "figure_01.png"
SOURCE_IMAGE_PATH = GENERATOR_PATH.parents[1] / "source" / "figure_01.png"
PARAMETER_CSV = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "parameters" / "pure" / "any_solvent.csv"
SOURCE_COMPONENTS = ("methanol", "1-pentanol", "1-nonanol")
SOURCE_DOCUMENT = "Gross and Sadowski 2002 Figure 1"
SOURCE_PARAMETER_TABLE = "Gross2002 Table1"


def _source_fingerprint() -> str:
    return hashlib.sha256(SOURCE_IMAGE_PATH.read_bytes()).hexdigest()


def _source_curve_row(component: str) -> dict[str, Any]:
    return next(
        row
        for row in figure01._model_reference_rows(figure01._source_rows())
        if row["component"] == component and row["branch"] == "vapor"
    )


def _associating_mixture(
    components: tuple[str, ...] = ("methanol",),
    *,
    charges: tuple[float, ...] | None = None,
    d_born: tuple[float, ...] | None = None,
    f_solv: tuple[float, ...] | None = None,
    association_site_count: tuple[int, ...] | None = None,
    k_ij: np.ndarray | None = None,
) -> ePCSAFTMixture:
    parameters = figure01._load_parameters()
    rows = [parameters[component] for component in components]
    count = len(rows)
    payload: dict[str, Any] = {
        "MW": np.asarray([float(row["MW"]) for row in rows]),
        "m": np.asarray([float(row["m"]) for row in rows]),
        "s": np.asarray([float(row["s"]) for row in rows]),
        "e": np.asarray([float(row["e"]) for row in rows]),
        "e_assoc": np.asarray([float(row["e_assoc"]) for row in rows]),
        "vol_a": np.asarray([float(row["vol_a"]) for row in rows]),
        "assoc_scheme": [
            "3B" if association_site_count is not None else row["assoc_scheme"]
            for row in rows
        ],
    }
    if charges is not None:
        payload["z"] = np.asarray(charges, dtype=float)
        payload["dielc"] = np.asarray([float(row["dielc"]) for row in rows])
    if d_born is not None:
        payload["d_born"] = np.asarray(d_born, dtype=float)
    if f_solv is not None:
        payload["f_solv"] = np.asarray(f_solv, dtype=float)
    if association_site_count is not None:
        payload["assoc_num"] = np.asarray(association_site_count, dtype=int)
    if k_ij is not None:
        payload["k_ij"] = np.asarray(k_ij, dtype=float)
    parameters = epcsaft.ParameterSet.from_dict(
        payload,
        species=list(components),
        metadata={
            "source": SOURCE_PARAMETER_TABLE,
            "paper": "Gross and Sadowski 2002",
            "table": "Table 1",
            "figure": "Figure 1",
            "source_path": str(PARAMETER_CSV.relative_to(REPO_ROOT)),
            "source_backed": True,
            "source_fingerprint": _source_fingerprint(),
        },
    )
    model_options = epcsaft.ModelOptions(
        born_model=epcsaft.BornModelOptions(enabled=False),
    )
    runtime_payload = parameters.to_runtime_dict(
        user_options=model_options.to_runtime_options(parameters),
    )
    runtime_payload["z"] = np.asarray(
        charges if charges is not None else (0.0,) * count,
        dtype=float,
    )
    runtime_payload["dielc"] = np.asarray([float(row["dielc"]) for row in rows])
    runtime_payload["d_born"] = np.asarray(
        d_born if d_born is not None else (0.0,) * count,
        dtype=float,
    )
    runtime_payload["f_solv"] = np.asarray(
        f_solv if f_solv is not None else (1.0,) * count,
        dtype=float,
    )
    if k_ij is not None:
        runtime_payload["k_ij"] = np.asarray(k_ij, dtype=float)
    return ePCSAFTMixture.from_params(runtime_payload, species=list(components))


def _native_validation(component: str, *, mixture: ePCSAFTMixture | None = None) -> dict[str, Any]:
    source_row = _source_curve_row(component)
    native = extension_native_core()
    return native._native_associating_single_component_vle_validation_result(
        mixture or figure01._mixture(component, figure01._load_parameters()),
        float(source_row["temperature_K"]),
        220,
        1.0e-8,
        0.0,
        20,
        1.0e-8,
        1.0e-3,
        1.0e-8,
        1.0e-8,
        {},
        print_level=0,
    )


def test_figure01_uses_internal_associating_saturation_validation() -> None:
    generator = GENERATOR_PATH.read_text(encoding="utf-8")
    bindings = REGISTER_BINDINGS_PATH.read_text(encoding="utf-8")

    assert "epcsaft_equilibrium.Equilibrium(" not in generator
    assert "_run_associating_single_component_vle_validation" in generator
    assert '_native_associating_single_component_vle_validation_result"' in bindings
    assert 'out["public_route_admission"] = "closed";' in bindings
    assert 'out["production_exposed"] = false;' in bindings


def test_figure01_source_backed_components_have_exact_provenance_and_fingerprint() -> None:
    source_rows = figure01._source_rows()
    parameters = figure01._load_parameters()
    fingerprint = _source_fingerprint()

    assert {row["component"] for row in source_rows} == set(SOURCE_COMPONENTS)
    assert SOURCE_IMAGE_PATH.is_file()
    assert len(fingerprint) == 64
    for component in SOURCE_COMPONENTS:
        component_rows = [row for row in source_rows if row["component"] == component]
        curve_rows = [row for row in component_rows if row["source_role"] == "paper_pc_saft_curve"]
        parameter_row = parameters[component]

        assert curve_rows
        assert {row["source_document"] for row in component_rows} == {SOURCE_DOCUMENT}
        assert {row["source_method"] for row in curve_rows} == {"published_figure_curve_trace"}
        assert {row["source_fingerprint"] for row in component_rows} == {fingerprint}
        assert parameter_row["source"] == SOURCE_PARAMETER_TABLE
        assert parameter_row["assoc_scheme"] == "2B"
        assert float(parameter_row["e_assoc"]) > 0.0
        assert float(parameter_row["vol_a"]) > 0.0
        assert float(parameter_row["z"]) == pytest.approx(0.0)
        assert float(parameter_row["d_born"]) == pytest.approx(0.0)
        assert float(parameter_row["f_solv"]) == pytest.approx(1.0)


@pytest.mark.parametrize("component", SOURCE_COMPONENTS)
def test_private_gross_figure01_saturation_returns_raw_dict_with_source_contract(component: str) -> None:
    source_row = _source_curve_row(component)
    result = _native_validation(component)

    assert type(result) is dict
    assert not isinstance(result, workflows.EquilibriumResult)
    assert result["source_receipt"] == {
        "source": SOURCE_PARAMETER_TABLE,
        "paper": "Gross and Sadowski 2002",
        "table": "Table 1",
        "figure": "Figure 1",
        "source_path": str(PARAMETER_CSV.relative_to(REPO_ROOT)),
        "parameter_provenance_status": "source_backed_parameter_metadata",
        "parameter_provenance_fields": ["source", "paper", "table", "figure", "source_path"],
    }
    assert result["temperature_K"] == pytest.approx(float(source_row["temperature_K"]))
    assert result["validation_route"] == "internal_associating_single_component_vle_validation"
    assert result["solver_route"] == "single_component_vle_eos"
    assert result["validation_case"] == "gross_sadowski_2002_figure_1"
    assert result["source_component"] == component
    assert result["public_route_admission"] == "closed"
    assert result["production_exposed"] is False
    assert result["selector_dispatch_used"] is False
    assert result["global_phase_set_certified"] is False
    derivative_receipt = result["association_derivative_receipt"]
    assert derivative_receipt["association_active"] is True
    assert derivative_receipt["association_scheme"] == "2B"
    assert derivative_receipt["site_count_per_component"] == [2]
    assert derivative_receipt["derivative_mode"] == "cppad_implicit_association"
    assert derivative_receipt["exact_site_fraction_jacobian_available"] is True
    assert derivative_receipt["exact_site_fraction_hessian_available"] is True
    assert len(derivative_receipt["phases"]) == 2
    for phase_receipt in derivative_receipt["phases"]:
        assert phase_receipt["association_scheme"] == "2B"
        assert phase_receipt["derivative_backend"] == "cppad_implicit_association"
        assert phase_receipt["exact_site_fraction_jacobian_available"] is True
        assert phase_receipt["exact_site_fraction_hessian_available"] is True


def test_internal_associating_saturation_solves_source_backed_methanol_point() -> None:
    source_row = next(
        row
        for row in figure01._model_reference_rows(figure01._source_rows())
        if row["component"] == "methanol" and row["branch"] == "vapor"
    )
    parameters = figure01._load_parameters()
    mixture = figure01._mixture("methanol", parameters)

    solve = workflows._run_associating_single_component_vle_validation
    result = solve(
        mixture,
        temperature_K=float(source_row["temperature_K"]),
        solver_options={"max_iterations": 220, "tolerance": 1.0e-8, "ipopt_print_level": 0},
    )

    assert type(result) is dict
    assert result["route"] == "internal_associating_single_component_vle_validation"
    assert result["validation_route"] == "internal_associating_single_component_vle_validation"
    assert result["solver_route"] == "single_component_vle_eos"
    assert result["route_status"] == "internal_validation_accepted"
    assert result["public_route_admission"] == "closed"
    assert result["production_exposed"] is False
    assert result["selector_dispatch_used"] is False
    assert result["global_phase_set_certified"] is False
    assert RETAINED_PLOT.is_file()


def test_private_associating_saturation_rejects_non_pure_topology() -> None:
    mixture = _associating_mixture(("methanol", "1-pentanol"), k_ij=np.zeros((2, 2)))

    with pytest.raises(NativeValueError, match="exactly one component"):
        _native_validation("methanol", mixture=mixture)


def test_private_associating_saturation_rejects_non_2b_association_topology() -> None:
    mixture = _associating_mixture(("methanol",), association_site_count=(3,))

    with pytest.raises(NativeValueError, match="2B"):
        _native_validation("methanol", mixture=mixture)


def test_private_associating_saturation_rejects_charged_component() -> None:
    mixture = _associating_mixture(("methanol",), charges=(1.0,))

    with pytest.raises(NativeValueError, match="neutral"):
        _native_validation("methanol", mixture=mixture)


def test_private_associating_saturation_rejects_born_terms() -> None:
    mixture = _associating_mixture(("methanol",), d_born=(1.0,))

    with pytest.raises(NativeValueError, match=r"Born|neutral auxiliary record"):
        _native_validation("methanol", mixture=mixture)


def test_private_associating_saturation_rejects_binary_interaction_topology() -> None:
    mixture = _associating_mixture(
        ("methanol",),
        k_ij=np.asarray([[0.0135]]),
    )

    with pytest.raises(NativeValueError, match="binary"):
        _native_validation("methanol", mixture=mixture)


def test_private_associating_saturation_rejects_reaction_options() -> None:
    mixture = _associating_mixture(("methanol",))
    source_row = _source_curve_row("methanol")

    with pytest.raises((InputError, TypeError, ValueError), match="reaction"):
        workflows._run_associating_single_component_vle_validation(
            mixture,
            temperature_K=float(source_row["temperature_K"]),
            solver_options={"reaction": "association"},
        )
