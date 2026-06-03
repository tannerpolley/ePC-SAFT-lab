from __future__ import annotations

import pytest

from analyses.package_validation.explicit_association_toybox.scripts.public_property_sources import (
    fetch_nist_saturation,
    nist_saturation_url,
    parse_nist_saturation_html,
)


NIST_SATURATION_HTML = """
<html>
  <body>
    <table>
      <tr>
        <th>Temperature (K)</th>
        <th>Pressure (MPa)</th>
        <th>Density (mol/l)</th>
        <th>Phase</th>
      </tr>
      <tr>
        <td>283.15</td>
        <td>0.0060</td>
        <td>24.50</td>
        <td>liquid</td>
      </tr>
      <tr>
        <td>283.15</td>
        <td>0.0060</td>
        <td>0.0025</td>
        <td>vapor</td>
      </tr>
    </table>
  </body>
</html>
"""


def test_parse_nist_saturation_html_keeps_liquid_rows_and_converts_units() -> None:
    rows = parse_nist_saturation_html(NIST_SATURATION_HTML, source_url="https://webbook.nist.gov/example")

    assert rows == [
        {
            "T_K": 283.15,
            "p_sat_Pa": 6000.0,
            "rho_sat_liq_mol_m3": 24500.0,
            "phase": "liquid",
            "source_url": "https://webbook.nist.gov/example",
        }
    ]


def test_nist_saturation_url_encodes_requested_component_and_units() -> None:
    url = nist_saturation_url(
        {
            "nist_id": "C67561",
            "temperature_low_K": 273.15,
            "temperature_high_K": 293.15,
            "temperature_increment_K": 10.0,
        }
    )

    assert "ID=C67561" in url
    assert "Type=SatT" in url
    assert "TUnit=K" in url
    assert "PUnit=MPa" in url
    assert "DUnit=mol%2Fl" in url


def test_fetch_nist_saturation_requires_explicit_network_permission() -> None:
    with pytest.raises(ValueError, match="allow_network=True"):
        fetch_nist_saturation({"nist_id": "C67561"}, allow_network=False)
