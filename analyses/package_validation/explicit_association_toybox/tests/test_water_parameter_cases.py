from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.water_parameter_cases import (
    link_water_cases_to_public_sources,
    load_water_parameter_cases,
)


def test_water_parameter_cases_record_source_and_diameter_policy() -> None:
    rows = load_water_parameter_cases()

    assert {
        "water_assigned_3b_provider_default",
        "water_rigorous_4c_source_label_only",
    } <= {row["case_id"] for row in rows}
    for row in rows:
        assert {
            "case_id",
            "topology_id",
            "parameter_source",
            "sigma_policy",
            "temperature_range_k",
            "property_source",
            "comparison_role",
        } <= set(row)
        assert str(row["topology_id"]).startswith("hr_")
        assert len(row["temperature_range_k"]) == 2


def test_water_cases_link_to_public_property_source_metadata() -> None:
    rows = link_water_cases_to_public_sources(load_water_parameter_cases())

    assert rows
    for row in rows:
        assert row["property_source_component"] == "water"
        assert row["property_source_name"] == "nist_chemistry_webbook"
