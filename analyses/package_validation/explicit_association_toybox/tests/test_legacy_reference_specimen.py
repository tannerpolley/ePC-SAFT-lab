from __future__ import annotations

from pathlib import Path

TOYBOX_ROOT = Path(__file__).resolve().parents[1]


def test_legacy_pcsaft_reference_specimen_is_frozen_with_density_seed() -> None:
    reference = TOYBOX_ROOT / "references" / "legacy_pcsaft_electrolyte.py"

    text = reference.read_text(encoding="utf-8")

    assert "def pcsaft_den" in text
    assert "def denfit" in text
    assert "eta_guess = 0.5" in text


def test_toy_property_eos_records_legacy_liquid_density_seed_policy() -> None:
    toybox = TOYBOX_ROOT / "scripts" / "toy_property_eos.py"

    text = toybox.read_text(encoding="utf-8")

    assert "legacy_pcsaft_liquid_eta_0_5" in text
