"""Canonical retained-source and run-contract data for NIST VLE validation."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "data" / "reference" / "pure_component" / "saturation_properties"

SOLVER_TOLERANCE = 1.0e-7
MAX_ITERATIONS = 500


@dataclass(frozen=True)
class NistSourceSpec:
    relative_path: str
    source_url: str
    temperatures_K: tuple[float, ...]


NIST_SOURCE_MANIFEST = {
    "Methane": NistSourceSpec(
        relative_path="methane/saturation_properties.csv",
        source_url="https://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID=C74828&Type=SatP&Digits=8&THigh=180&TLow=100&TInc=10&RefState=DEF&TUnit=K&PUnit=Pa&DUnit=kg%2Fm3&HUnit=kJ%2Fmol&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm",
        temperatures_K=tuple(float(value) for value in range(100, 181, 10)),
    ),
    "Ethane": NistSourceSpec(
        relative_path="ethane/saturation_properties.csv",
        source_url="https://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID=C74840&Type=SatP&Digits=8&THigh=280&TLow=100&TInc=20&RefState=DEF&TUnit=K&PUnit=Pa&DUnit=kg%2Fm3&HUnit=kJ%2Fmol&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm",
        temperatures_K=tuple(float(value) for value in range(100, 281, 20)),
    ),
    "Propane": NistSourceSpec(
        relative_path="propane/saturation_properties.csv",
        source_url="https://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID=C74986&Type=SatP&Digits=8&THigh=340&TLow=100&TInc=20&RefState=DEF&TUnit=K&PUnit=Pa&DUnit=kg%2Fm3&HUnit=kJ%2Fmol&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm",
        temperatures_K=tuple(float(value) for value in range(100, 341, 20)),
    ),
}
EXPECTED_SOURCE_GRID = frozenset(
    (species, temperature) for species, spec in NIST_SOURCE_MANIFEST.items() for temperature in spec.temperatures_K
)


def expected_source_url(species: str) -> str:
    try:
        return NIST_SOURCE_MANIFEST[species].source_url
    except KeyError as exc:
        raise ValueError(f"unsupported NIST saturation species: {species!r}") from exc


def _load_species_rows(species: str) -> list[dict[str, str]]:
    try:
        spec = NIST_SOURCE_MANIFEST[species]
    except KeyError as exc:
        raise ValueError(f"unsupported NIST saturation species: {species!r}") from exc

    path = SOURCE_ROOT / spec.relative_path
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    expected_temperatures = set(spec.temperatures_K)
    seen_temperatures: set[float] = set()
    if len(rows) != len(expected_temperatures):
        raise ValueError(
            f"retained NIST row count mismatch for {species}: expected {len(expected_temperatures)}, got {len(rows)}"
        )
    for row in rows:
        if row.get("species") != species:
            raise ValueError(f"retained NIST species mismatch for {species}: {row.get('species')!r}")
        if row.get("source") != spec.source_url:
            raise ValueError(f"retained NIST source URL mismatch for {species}")
        try:
            temperature = float(row["T_K"])
            pressure = float(row["p_sat_Pa"])
            liquid_density = float(row["rho_sat_liq_kg_m3"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"retained NIST row has invalid numeric fields for {species}") from exc
        if temperature not in expected_temperatures or temperature in seen_temperatures:
            raise ValueError(f"retained NIST temperature grid mismatch for {species}")
        if not all(math.isfinite(value) and value > 0.0 for value in (pressure, liquid_density)):
            raise ValueError(f"retained NIST raw values must be positive and finite for {species}")
        seen_temperatures.add(temperature)
    if seen_temperatures != expected_temperatures:
        raise ValueError(f"retained NIST temperature grid mismatch for {species}")
    return rows


def load_canonical_source_rows(species: str | None = None) -> list[dict[str, str]]:
    species_names = (species,) if species is not None else tuple(NIST_SOURCE_MANIFEST)
    rows: list[dict[str, str]] = []
    for species_name in species_names:
        rows.extend(_load_species_rows(species_name))
    return rows
