from __future__ import annotations

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.real_system_topology_map import (
    expand_real_system_rows,
    load_real_system_topology_map,
)


def test_real_system_topology_map_covers_representative_families() -> None:
    rows = load_real_system_topology_map()

    required_ids = {
        "acid_1",
        "alkanol_2b",
        "water_3b_assigned_4c_rigorous",
        "primary_amine_3b",
        "secondary_amine_2b",
        "gross_methanol_cyclohexane_2b",
    }
    assert required_ids <= {row["system_id"] for row in rows}
    for row in rows:
        assert {
            "system_id",
            "source_paper",
            "component_family",
            "assigned_topology",
            "rigorous_topology",
            "parameter_source_status",
            "validation_role",
        } <= set(row)
        assert str(row["assigned_topology"]).startswith("hr_")
        assert str(row["rigorous_topology"]).startswith("hr_")


def test_real_system_topology_expansion_rejects_bad_topology() -> None:
    rows = [
        {
            "system_id": "bad",
            "source_paper": "source",
            "component_family": "family",
            "assigned_topology": "hr_9z",
            "rigorous_topology": "hr_2b",
            "parameter_source_status": "screening",
            "validation_role": "diagnostic",
        }
    ]

    with pytest.raises(ValueError, match="assigned_topology"):
        expand_real_system_rows(rows)
