from __future__ import annotations

import argparse
import csv
from collections.abc import Mapping
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import yaml

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ANALYSIS_ROOT.parents[2]
REFERENCE_SOURCE_DIR = REPO_ROOT / "data" / "reference" / "pure_component" / "saturation_density"
DEFAULT_CONFIG = ANALYSIS_ROOT / "config" / "public_property_sources.yaml"
DEFAULT_OUTPUT = REFERENCE_SOURCE_DIR / "water_methanol_nist_saturation.csv"
NIST_FLUID_URL = "https://webbook.nist.gov/cgi/fluid.cgi"


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "tr":
            self._row = []
        elif tag.lower() in {"th", "td"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        token = tag.lower()
        if token in {"th", "td"} and self._row is not None and self._cell is not None:
            self._row.append(" ".join(part.strip() for part in self._cell if part.strip()))
            self._cell = None
        elif token == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


def nist_saturation_url(source: Mapping[str, object]) -> str:
    params = {
        "Action": "Load",
        "ID": str(source["nist_id"]),
        "Type": "SatT",
        "TUnit": "K",
        "PUnit": "MPa",
        "DUnit": "mol/l",
        "HUnit": "kJ/mol",
        "WUnit": "m/s",
        "VisUnit": "uPa*s",
        "STUnit": "N/m",
        "RefState": "DEF",
        "Digits": "5",
        "TLow": str(source.get("temperature_low_K", 273.15)),
        "THigh": str(source.get("temperature_high_K", 293.15)),
        "TInc": str(source.get("temperature_increment_K", 10.0)),
    }
    return f"{NIST_FLUID_URL}?{urlencode(params)}"


def parse_nist_saturation_html(html: str, source_url: str) -> list[dict[str, object]]:
    parser = _TableParser()
    parser.feed(html)
    rows: list[dict[str, object]] = []
    for table_rows in _candidate_tables(parser.rows):
        header = [_normalize_header(value) for value in table_rows[0]]
        columns = _column_map(header)
        if columns is None:
            continue
        for raw in table_rows[1:]:
            if len(raw) <= max(columns.values()):
                continue
            phase = raw[columns["phase"]].strip().lower()
            if phase != "liquid":
                continue
            rows.append(
                {
                    "T_K": _parse_float(raw[columns["temperature"]]),
                    "p_sat_Pa": _parse_float(raw[columns["pressure"]]) * 1.0e6,
                    "rho_sat_liq_mol_m3": _parse_float(raw[columns["density"]]) * 1000.0,
                    "phase": "liquid",
                    "source_url": source_url,
                }
            )
    return rows


def fetch_nist_saturation(source: Mapping[str, object], *, allow_network: bool) -> list[dict[str, object]]:
    if not allow_network:
        raise ValueError("public data fetch requires allow_network=True")
    url = nist_saturation_url(source)
    request = Request(url, headers={"User-Agent": "ePC-SAFT validation toybox"})
    with urlopen(request, timeout=float(source.get("timeout_seconds", 30.0))) as response:
        html = response.read().decode("utf-8", errors="replace")
    rows = _select_source_rows(parse_nist_saturation_html(html, source_url=url), source)
    for row in rows:
        row["component"] = str(source["component"])
        row["source_name"] = str(source.get("source_name", "nist_chemistry_webbook"))
    return rows


def _select_source_rows(rows: list[dict[str, object]], source: Mapping[str, object]) -> list[dict[str, object]]:
    lo = float(source.get("temperature_low_K", float("-inf")))
    hi = float(source.get("temperature_high_K", float("inf")))
    filtered = [row for row in rows if lo <= float(row["T_K"]) <= hi]
    filtered.sort(key=lambda row: float(row["T_K"]))
    target_count = source.get("retained_temperature_points")
    if target_count is None or len(filtered) <= int(target_count):
        return filtered
    count = int(target_count)
    if count < 2:
        raise ValueError("retained_temperature_points must be at least 2 when provided.")
    indexes = np.linspace(0, len(filtered) - 1, count)
    selected_indexes = sorted({int(round(index)) for index in indexes})
    selected = [filtered[index] for index in selected_indexes]
    if len(selected) != count:
        raise ValueError("retained_temperature_points selection produced duplicate source rows.")
    return selected


def write_public_saturation_csv(rows: list[dict[str, object]], output_path: Path = DEFAULT_OUTPUT) -> Path:
    if not rows:
        raise RuntimeError("public saturation fetch produced no liquid rows.")
    fieldnames = [
        "component",
        "source_name",
        "T_K",
        "p_sat_Pa",
        "rho_sat_liq_mol_m3",
        "phase",
        "source_url",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in fieldnames} for row in rows)
    return output_path


def load_public_property_sources(path: Path = DEFAULT_CONFIG) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        raise ValueError(f"{path} must contain a sources list.")
    sources = []
    for item in data["sources"]:
        if not isinstance(item, dict):
            raise ValueError(f"{path} sources entries must be mappings.")
        sources.append(dict(item))
    return sources


def _candidate_tables(rows: list[list[str]]) -> list[list[list[str]]]:
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for row in rows:
        normalized = [_normalize_header(value) for value in row]
        if any("temperature" in value for value in normalized) and current:
            tables.append(current)
            current = [row]
        else:
            current.append(row)
    if current:
        tables.append(current)
    return tables


def _column_map(header: list[str]) -> dict[str, int] | None:
    positions: dict[str, int] = {}
    for idx, value in enumerate(header):
        if "temperature" in value and "k" in value:
            positions["temperature"] = idx
        elif "pressure" in value and "mpa" in value:
            positions["pressure"] = idx
        elif "density" in value and "mol" in value:
            positions["density"] = idx
        elif "phase" in value:
            positions["phase"] = idx
    required = {"temperature", "pressure", "density", "phase"}
    return positions if required <= set(positions) else None


def _normalize_header(value: str) -> str:
    return " ".join(value.lower().replace("\xa0", " ").split())


def _parse_float(value: str) -> float:
    return float(value.replace(",", "").strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch public saturation rows for the explicit association toybox.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args()
    rows: list[dict[str, object]] = []
    for source in load_public_property_sources(args.config):
        rows.extend(fetch_nist_saturation(source, allow_network=args.allow_network))
    output = write_public_saturation_csv(rows, args.output)
    print(output)


if __name__ == "__main__":
    main()
