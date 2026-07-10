from __future__ import annotations

import json

import pytest
from epcsaft._types import InputError
from epcsaft.state.native_adapter import ePCSAFTMixture


def _write_ssmds_dataset(tmp_path):
    dataset = tmp_path / "synthetic_liquid_electrolyte"
    pure_dir = dataset / "pure"
    pure_dir.mkdir(parents=True)
    (pure_dir / "components.csv").write_text(
        "\n".join(
            [
                "component,MW,m,s,e,e_assoc,vol_a,assoc_scheme,z,dielc,d_born,f_solv",
                "Solv,0.018,1.0,3.7,150,0,0,,0,78,0,1.4",
                "Cat+,0.023,1,2.8,100,0,0,,1,8,3.4,1",
                "An-,0.035,1,2.7,100,0,0,,-1,8,4.1,1",
            ]
        ),
        encoding="utf-8",
    )
    (dataset / "user_options.json").write_text(
        json.dumps(
            {
                "elec_model": {
                    "relative_permittivity_rule": "linear",
                    "born_model": {
                        "enabled": True,
                        "born_diameter_rule": "fitted",
                        "solvation_shell_model": True,
                        "dielectric_saturation": True,
                        "bulk_mode": "mix",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    return dataset


def test_liquid_electrolyte_dataset_rejects_missing_interaction_sources(tmp_path) -> None:
    dataset = _write_ssmds_dataset(tmp_path)
    species = ("Solv", "Cat+", "An-")
    x = [0.98, 0.01, 0.01]

    with pytest.raises(InputError, match=r"(?i)interaction family k_ij.*source matrix"):
        ePCSAFTMixture.from_dataset(dataset, species, x, 298.15)
