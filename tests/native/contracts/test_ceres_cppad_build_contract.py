from __future__ import annotations

import json

import epcsaft
import epcsaft.regression.core as regression_core


REGRESSION_CAPABILITY_DIMENSIONS = (
    "registry_known_target_kind",
    "derivative_supported_target_kind",
    "optimizer_supported_target_kind",
    "public_production_supported_target_kind",
)


def test_runtime_reports_ceres_build_contract() -> None:
    info = epcsaft.runtime_build_info()
    ceres = info["native_dependencies"]["ceres"]

    assert ceres["backend"] == "ceres"
    assert ceres["status"] == "enabled_available"
    assert ceres["required"] is False
    assert ceres["required_for"] == ["epcsaft-regression"]
    assert ceres["compiled"] is True
    assert ceres["available"] is True

    capabilities = epcsaft.capabilities()
    assert capabilities["package_views"]["regression"]["native_dependencies"]["ceres"]["required"] is False
    assert capabilities["package_views"]["regression"]["forbidden_default_dependencies"] == ["ipopt"]
    assert capabilities["optimizers"]["ceres"]["status"] == ceres["status"]
    assert capabilities["optimizers"]["ceres"]["compiled"] is ceres["compiled"]
    assert capabilities["optimizers"]["ceres"]["production"] is ceres["available"]
    assert capabilities["optimizers"]["ceres"]["native_hot_loop"] is ceres["available"]


def test_ceres_cppad_capability_claims_require_enabled_native_dependencies() -> None:
    capabilities = epcsaft.capabilities()
    ceres = capabilities["optimizers"]["ceres"]
    cppad = capabilities["derivatives"]["cppad"]
    coverage = capabilities["derivatives"]["coverage_matrix"]

    assert ceres["compiled"] is True
    assert ceres["available"] is True
    assert cppad["compiled"] is True
    assert cppad["available"] is True

    jacobians = coverage["regression_ceres_jacobians"]
    assert jacobians["available"] is True
    assert jacobians["production"] is True
    assert jacobians["routes"] == [
        "pure_neutral",
        "binary_pair_constant_kij",
        "liquid_electrolyte_born",
    ]
    assert {row["quantity"] for row in coverage["rows"]}.issuperset({"pure_neutral_parameters"})
    assert "numerical" + "_derivative" not in json.dumps({"ceres": ceres, "cppad": cppad, "coverage": coverage}).lower()


def test_regression_capability_evidence_separates_registry_derivative_optimizer_and_public_claims() -> None:
    evidence = epcsaft.capabilities()["regression"]["target_kind_evidence"]
    rows = evidence["rows"]

    assert evidence["dimensions"] == list(REGRESSION_CAPABILITY_DIMENSIONS)
    assert evidence["revisit_after"] == ["#136", "#137"]
    assert {row["target_kind"] for row in rows} == set(regression_core.NATIVE_TARGET_KINDS)

    for row in rows:
        assert set(REGRESSION_CAPABILITY_DIMENSIONS).issubset(row)
        assert row["registry_known_target_kind"] is True
        if row["public_production_supported_target_kind"]:
            assert row["derivative_supported_target_kind"] is True
            assert row["optimizer_supported_target_kind"] is True
            assert row["tests"]


def test_association_affecting_regression_targets_remain_nonproduction_until_evidence_exists() -> None:
    rows = {
        row["target_kind"]: row
        for row in epcsaft.capabilities()["regression"]["target_kind_evidence"]["rows"]
    }

    for target in ("e_assoc", "vol_a"):
        assert rows[target]["derivative_supported_target_kind"] is True
        assert rows[target]["public_production_supported_target_kind"] is False
        assert rows[target]["optimizer_supported_target_kind"] is False
        assert rows[target]["revisit_after_issue"] == "#136"

    for target in ("k_hb_ij", "l_ij"):
        assert rows[target]["derivative_supported_target_kind"] is True
        assert rows[target]["public_production_supported_target_kind"] is False
        assert rows[target]["optimizer_supported_target_kind"] is False
        assert rows[target]["revisit_after_issue"] == "#137"

    assert rows["k_ij"]["public_production_supported_target_kind"] is True


def test_property_derivative_parameter_families_scope_active_association_lij_out_of_production() -> None:
    parameter_families = epcsaft.capabilities()["derivatives"]["property_derivative_result_apis"][
        "parameter_families"
    ]

    assert "production_supported" not in parameter_families
    assert {"e_assoc", "vol_a", "l_ij", "k_hb_ij"}.issubset(
        set(parameter_families["state_property_derivative_supported"])
    )
    assert {"e_assoc", "vol_a", "l_ij", "k_hb_ij"}.isdisjoint(
        set(parameter_families["regression_public_production_supported"])
    )
    assert parameter_families["production_scope"]["e_assoc"] == "pure_associating_component_parameter_only"
    assert parameter_families["production_scope"]["vol_a"] == "pure_associating_component_parameter_only"
    assert parameter_families["production_scope"]["l_ij"] == "binary_pair_including_active_association"
    assert parameter_families["production_scope"]["k_hb_ij"] == "active_association_binary_pair_only"
    assert parameter_families["association_affecting_nonproduction"] == {}
