from __future__ import annotations

import csv
import json
import math
import sys
import sys as _bootstrap_sys
from pathlib import Path
from pathlib import Path as _BootstrapPath

for _candidate in _BootstrapPath(__file__).resolve().parents:
    if (_candidate / "scripts" / "plot_outputs.py").is_file():
        if str(_candidate) not in _bootstrap_sys.path:
            _bootstrap_sys.path.insert(0, str(_candidate))
        break
else:
    raise ModuleNotFoundError("Could not locate repo root containing scripts/plot_outputs.py")
from collections.abc import Iterable

import numpy as np
import pandas as pd

from scripts.dev.native_runtime_env import apply_to_current_process
from scripts.plot_outputs import REPO_ROOT, analysis_root

apply_to_current_process()
from scripts._epcsaft_oop import epcsaft_relative_permittivity

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
ANALYSIS_ROOT = analysis_root(__file__)
if str(ANALYSIS_ROOT) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_ROOT))

from shared import _common as common

SOURCE_ROOT = Path(__file__).resolve().parent
FIGURES_ROOT = ANALYSIS_ROOT / "figures"
DATASET = "2025_Figiel"

FIELDNAMES = [
    "figure_id",
    "panel_id",
    "series_id",
    "series_label",
    "source_type",
    "dataset",
    "parameter_set",
    "salt",
    "ion",
    "solvent_system",
    "composition",
    "composition_basis",
    "target_w_org",
    "x_name",
    "x_value",
    "x_units",
    "y_name",
    "y_value",
    "y_units",
    "curve_points",
    "user_options",
    "source_file",
    "category",
    "display_order",
]
NUMERIC_FIELDS = {"target_w_org", "x_value", "y_value", "curve_points", "display_order"}

FIG5_PANELS = [
    ("a)", ["LiCl", "NaCl", "KCl"], "Cl$^-$ salts in water"),
    ("b)", ["LiBr", "NaBr", "KBr"], "Br$^-$ salts in water"),
]
FIG8_PANELS = [
    ("a)", "LiBr", 5.0, 3.0),
    ("b)", "NaI", 1.5, 1.125),
    ("c)", "NaBr", 1.5, 1.125),
]
FIG8_CURVE_MAX_OVERRIDES = {
    ("NaI", "methanol"): 0.77,
    ("NaBr", "ethanol"): 0.195,
}
FIG9_PANELS = [
    ("a)", "NaBr", "water-methanol", 3.0),
    ("b)", "NaBr", "water-ethanol", 4.0),
    ("c)", "NaCl", "water-methanol", 2.0),
    ("d)", "NaCl", "water-ethanol", 2.0),
]
FIG9_TARGETS = (0.8, 0.4)
FIG9_DATA_TOL = 0.08
FIG9_CURVE_MAX_BY_PANEL = {
    "b)": {0.8: 1.5},
    "c)": {0.8: 0.6},
    "d)": {0.8: 0.3},
}
PURE_SOLVENT_DIELC = {
    "water": 78.09,
    "methanol": 33.05,
    "ethanol": 24.88,
}
FIG2_SERIES = (
    ("Nortemann", "NaCl", "gray circles"),
    ("Haggis", "NaBr", "green squares"),
    ("Buchner", "NaCl", "blue triangles"),
    ("Wei", "LiCl", "orange upside-down triangles"),
)


def figure_number(figure_id: str) -> int:
    suffix = str(figure_id).rsplit("_", 1)[-1]
    return int(suffix)


def figure_dirname(figure_id: str) -> str:
    return f"figure_{figure_number(figure_id):02d}"


def figure_root(figure_id: str) -> Path:
    return FIGURES_ROOT / figure_dirname(figure_id)


def payload_path(figure_id: str) -> Path:
    return figure_root(figure_id) / "results" / f"{figure_id}_series.csv"


def figure_input_dir(figure_id: str) -> Path:
    return figure_root(figure_id) / "source"


def figure_input_path(figure_id: str, *parts: str) -> Path:
    return figure_input_dir(figure_id).joinpath(*parts)


def figure_script_path(figure_id: str, script_name: str) -> Path:
    return figure_root(figure_id) / "scripts" / script_name


def _format_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        return format(value, ".17g")
    if isinstance(value, int):
        return str(value)
    return str(value)


def _composition_json(comp: dict[str, float] | None) -> str:
    if not comp:
        return ""
    return json.dumps({k: float(v) for k, v in sorted(comp.items())}, sort_keys=True, separators=(",", ":"))


def _options_json(options: dict | None) -> str:
    return json.dumps(options or {}, sort_keys=True, separators=(",", ":"))


def _source_ref(path: Path | None) -> str:
    return path.relative_to(REPO_ROOT).as_posix() if path is not None else ""


def _row(
    *,
    figure_id: str,
    panel_id: str,
    series_id: str,
    series_label: str,
    source_type: str,
    x_name: str,
    x_value: float,
    y_name: str,
    y_value: float,
    display_order: int,
    dataset: str = "",
    parameter_set: str = "",
    salt: str = "",
    ion: str = "",
    solvent_system: str = "",
    composition: dict[str, float] | None = None,
    composition_basis: str = "",
    target_w_org: float | None = None,
    x_units: str = "",
    y_units: str = "",
    curve_points: int | None = None,
    user_options: dict | None = None,
    source_file: Path | None = None,
    category: str = "",
) -> dict[str, str]:
    data = {
        "figure_id": figure_id,
        "panel_id": panel_id,
        "series_id": series_id,
        "series_label": series_label,
        "source_type": source_type,
        "dataset": dataset,
        "parameter_set": parameter_set,
        "salt": salt,
        "ion": ion,
        "solvent_system": solvent_system,
        "composition": _composition_json(composition),
        "composition_basis": composition_basis,
        "target_w_org": target_w_org,
        "x_name": x_name,
        "x_value": x_value,
        "x_units": x_units,
        "y_name": y_name,
        "y_value": y_value,
        "y_units": y_units,
        "curve_points": curve_points,
        "user_options": _options_json(user_options),
        "source_file": _source_ref(source_file),
        "category": category,
        "display_order": display_order,
    }
    return {field: _format_value(data.get(field, "")) for field in FIELDNAMES}


def _write_payload(figure_id: str, rows: list[dict[str, str]]) -> Path:
    path = payload_path(figure_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=FIELDNAMES).to_csv(path, index=False)
    return path


def read_payload(figure_id: str) -> list[dict[str, str]]:
    path = payload_path(figure_id)
    if not path.exists():
        raise FileNotFoundError(f"Missing generated payload {path}. Run generate_figure_data.py first.")
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def select_rows(rows: Iterable[dict[str, str]], **criteria: str) -> list[dict[str, str]]:
    out = []
    for row in rows:
        if all(row.get(key, "") == str(value) for key, value in criteria.items()):
            out.append(row)
    return sorted(out, key=lambda row: (float(row.get("display_order") or 0.0), float(row.get("x_value") or 0.0)))


def xy(rows: Iterable[dict[str, str]]) -> tuple[list[float], list[float]]:
    selected = list(rows)
    return [float(row["x_value"]) for row in selected], [float(row["y_value"]) for row in selected]


def rows_by_key(rows: Iterable[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row.get(key, ""), []).append(row)
    return {name: select_rows(values) for name, values in grouped.items()}


def _salt_xion_to_species_molefraction(x_ion: float, salt: str, solvent_system: str) -> np.ndarray:
    species = common.species_for_combo(salt, solvent_system)
    nu_cat, nu_an = common.stoich_for_salt(salt)
    ion_total = float(x_ion)
    if not 0.0 <= ion_total < 1.0:
        raise ValueError(f"x_ion must lie in [0, 1). Got {x_ion!r}")
    solvent_fraction = 1.0 - ion_total
    species_x = np.zeros(len(species), dtype=float)
    ion_denom = float(nu_cat + nu_an)
    species_x[0] = ion_total * float(nu_cat) / ion_denom
    species_x[1] = ion_total * float(nu_an) / ion_denom
    for index in range(2, len(species)):
        species_x[index] = solvent_fraction / float(len(species) - 2)
    return species_x


def _relative_permittivity_curve(
    dataset_name: str,
    salt: str,
    solvent_system: str,
    x_ion_grid: Iterable[float],
    *,
    user_options: dict | None = None,
) -> np.ndarray:
    comp = {solvent_system: 1.0}
    params = common.build_params(dataset_name, salt, solvent_system, comp, user_options=user_options)
    values = []
    for x_ion in x_ion_grid:
        x = _salt_xion_to_species_molefraction(float(x_ion), salt, solvent_system)
        eps_r = float(epcsaft_relative_permittivity(x, params)[0])
        values.append(eps_r)
    return np.asarray(values, dtype=float)


def _figure1_profile_rows() -> list[dict[str, str]]:
    config_path = figure_input_path("figure_1", "schematic_profile.json")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    eps_ion = float(config["eps_ion"])
    eps_bulk = float(config["eps_bulk"])
    shell_position = float(config["shell_position"])
    domain_max = float(config["domain_max"])
    points = [
        (0.0, eps_ion),
        (shell_position, eps_ion),
        (shell_position, eps_bulk),
        (domain_max, eps_bulk),
    ]
    rows: list[dict[str, str]] = []
    for order, (x_value, y_value) in enumerate(points):
        rows.append(
            _row(
                figure_id="figure_1",
                panel_id="main",
                series_id="profile",
                series_label="Schematic profile",
                source_type="schematic",
                x_name="radial_position",
                x_value=float(x_value),
                x_units="-",
                y_name="epsilon_r",
                y_value=float(y_value),
                y_units="-",
                curve_points=len(points),
                source_file=config_path,
                category="step_profile",
                display_order=order,
            )
        )
    return rows


def generate_figure_1() -> list[dict[str, str]]:
    return _figure1_profile_rows()


def generate_figure_2() -> list[dict[str, str]]:
    figure_id = "figure_2"
    source = figure_input_path(figure_id, "dielc_salts_in_water.csv")
    _, raw_rows = common.read_csv_rows(source)

    rows: list[dict[str, str]] = []
    order = 0
    for source_label, salt, _caption_label in FIG2_SERIES:
        for raw in raw_rows:
            row_source = str(raw.get("source", "")).strip()
            row_salt = str(raw.get("Salt", raw.get("salt", ""))).strip()
            x_ion = common.parse_float(raw.get("x_ion"))
            eps_r = common.parse_float(raw.get("dielc"))
            if row_source != source_label or row_salt != salt or x_ion is None or eps_r is None:
                continue
            rows.append(
                _row(
                    figure_id=figure_id,
                    panel_id="main",
                    series_id=f"data_{source_label}_{salt}",
                    series_label=f"{salt} ({source_label})",
                    source_type="literature",
                    salt=salt,
                    solvent_system="water",
                    composition={"water": 1.0},
                    composition_basis="mole_fraction",
                    x_name="x_ion",
                    x_value=float(x_ion),
                    x_units="mol/mol",
                    y_name="epsilon_r",
                    y_value=float(eps_r),
                    y_units="-",
                    source_file=source,
                    category=source_label,
                    display_order=order,
                )
            )
            order += 1

    x_grid = np.linspace(0.0, 0.30, 400)
    curve_specs = (
        ("model_rule1", "Rule 1", {"elec_model": {"relative_permittivity_rule": "linear"}}),
        ("model_empirical", "Eq. 11 fit", None),
    )
    for series_id, label, options in curve_specs:
        eps_curve = _relative_permittivity_curve(DATASET, "NaCl", "water", x_grid, user_options=options)
        for x_value, y_value in zip(x_grid, eps_curve):
            rows.append(
                _row(
                    figure_id=figure_id,
                    panel_id="main",
                    series_id=series_id,
                    series_label=label,
                    source_type="model",
                    dataset=DATASET,
                    parameter_set=DATASET,
                    salt="NaCl",
                    solvent_system="water",
                    composition={"water": 1.0},
                    composition_basis="mole_fraction",
                    x_name="x_ion",
                    x_value=float(x_value),
                    x_units="mol/mol",
                    y_name="epsilon_r",
                    y_value=float(y_value),
                    y_units="-",
                    curve_points=len(x_grid),
                    user_options=options,
                    category=series_id,
                    display_order=order,
                )
            )
            order += 1
    return rows


def generate_figure_3() -> list[dict[str, str]]:
    figure_id = "figure_3"
    water_source = figure_input_path(figure_id, "dielc_salts_in_water.csv")
    organic_source = figure_input_path(figure_id, "dielc_single_solvent_digitized.csv")
    rows: list[dict[str, str]] = []
    order = 0

    _, water_rows = common.read_csv_rows(water_source)
    for raw in water_rows:
        x_ion = common.parse_float(raw.get("x_ion"))
        eps_r = common.parse_float(raw.get("dielc"))
        salt = str(raw.get("Salt", raw.get("salt", ""))).strip()
        if x_ion is None or eps_r is None or not salt:
            continue
        rows.append(
            _row(
                figure_id=figure_id,
                panel_id="main",
                series_id="data_water",
                series_label="Water data",
                source_type="literature",
                salt=salt,
                solvent_system="water",
                composition={"water": 1.0},
                composition_basis="mole_fraction",
                x_name="x_ion",
                x_value=float(x_ion),
                x_units="mol/mol",
                y_name="epsilon_ratio",
                y_value=float(eps_r) / PURE_SOLVENT_DIELC["water"],
                y_units="-",
                source_file=water_source,
                category="water",
                display_order=order,
            )
        )
        order += 1

    _, organic_rows = common.read_csv_rows(organic_source)
    for raw in organic_rows:
        solvent = str(raw.get("solvent", "")).strip().lower()
        salt = str(raw.get("salt", "")).strip()
        x_ion = common.parse_float(raw.get("x_ion"))
        eps_ratio = common.parse_float(raw.get("epsilon_ratio"))
        if solvent not in {"methanol", "ethanol"} or x_ion is None or eps_ratio is None:
            continue
        rows.append(
            _row(
                figure_id=figure_id,
                panel_id="main",
                series_id=f"data_{solvent}",
                series_label=f"{solvent.title()} data",
                source_type="digitized",
                salt=salt,
                solvent_system=solvent,
                composition={solvent: 1.0},
                composition_basis="mole_fraction",
                x_name="x_ion",
                x_value=float(x_ion),
                x_units="mol/mol",
                y_name="epsilon_ratio",
                y_value=float(eps_ratio),
                y_units="-",
                source_file=organic_source,
                category=solvent,
                display_order=order,
            )
        )
        order += 1

    x_grid = np.linspace(0.0, 0.20, 400)
    y_curve = 1.0 / (1.0 + 7.01 * x_grid)
    for x_value, y_value in zip(x_grid, y_curve):
        rows.append(
            _row(
                figure_id=figure_id,
                panel_id="main",
                series_id="model_empirical_ratio",
                series_label="Eq. 11",
                source_type="model",
                dataset=DATASET,
                parameter_set=DATASET,
                x_name="x_ion",
                x_value=float(x_value),
                x_units="mol/mol",
                y_name="epsilon_ratio",
                y_value=float(y_value),
                y_units="-",
                curve_points=len(x_grid),
                category="eq11",
                display_order=order,
            )
        )
        order += 1
    return rows


def generate_figure_4() -> list[dict[str, str]]:
    figure_id = "figure_4"
    source = figure_input_path(figure_id, "water.csv")
    _, raw_rows = common.read_csv_rows(source)
    literature: dict[str, float] = {}
    for raw in raw_rows:
        ion = str(raw.get("Ion", "")).strip()
        value = common.parse_float(raw.get("Gsolv (kJ/mol)"))
        if ion and value is not None:
            key = f"{ion}+" if ion in {"H", "Li", "Na", "K"} else f"{ion}-" if ion in {"Cl", "Br", "I"} else ion
            literature[key] = value

    rows: list[dict[str, str]] = []
    ions = ["Li+", "Na+", "K+", "Cl-", "Br-", "I-"]
    for order, ion in enumerate(ions):
        rows.append(
            _row(
                figure_id=figure_id,
                panel_id="combined",
                series_id="literature",
                series_label="Literature",
                source_type="literature",
                ion=ion,
                solvent_system="water",
                x_name="ion_index",
                x_value=float(order),
                y_name="negative_gsolv",
                y_value=-float(literature.get(ion, float("nan"))),
                y_units="kJ/mol",
                source_file=source,
                category=ion,
                display_order=order,
            )
        )
        for dataset, label in (("2025_Figiel", "ePC-SAFT 2025"), ("2020_Bulow", "ePC-SAFT 2020")):
            try:
                y_value = -common.gsolv_ion(dataset, ion, "water", {"water": 1.0})
            except Exception:
                y_value = float("nan")
            rows.append(
                _row(
                    figure_id=figure_id,
                    panel_id="combined",
                    series_id=f"model_{dataset}",
                    series_label=label,
                    source_type="model",
                    dataset=dataset,
                    parameter_set=dataset,
                    ion=ion,
                    solvent_system="water",
                    composition={"water": 1.0},
                    composition_basis="mole_fraction",
                    x_name="ion_index",
                    x_value=float(order),
                    y_name="negative_gsolv",
                    y_value=float(y_value),
                    y_units="kJ/mol",
                    curve_points=1,
                    category=ion,
                    display_order=order,
                )
            )
    return rows


def generate_figure_5() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    source_root = figure_input_dir("figure_5")
    order = 0
    for panel_id, salts, _title in FIG5_PANELS:
        for salt in salts:
            source = source_root / f"water-{salt}.csv"
            for entry in common.read_miac_dataset(source, "water"):
                rows.append(
                    _row(
                        figure_id="figure_5",
                        panel_id=panel_id,
                        series_id=f"data_{salt}",
                        series_label=f"{salt} data",
                        source_type="literature",
                        salt=salt,
                        solvent_system="water",
                        composition={"water": 1.0},
                        composition_basis="mole_fraction",
                        x_name="molality",
                        x_value=float(entry["molality"]),
                        x_units="mol/kg",
                        y_name="miac_m",
                        y_value=float(entry["miac_m"]),
                        y_units="-",
                        source_file=source,
                        category=salt,
                        display_order=order,
                    )
                )
                order += 1
            m_grid, y_model = common.mean_ionic_activity_curve(DATASET, salt, "water", {"water": 1.0}, 6.0, points=600)
            for m, y in zip(m_grid, y_model):
                rows.append(
                    _row(
                        figure_id="figure_5",
                        panel_id=panel_id,
                        series_id=f"model_{salt}",
                        series_label=f"{salt} model",
                        source_type="model",
                        dataset=DATASET,
                        parameter_set=DATASET,
                        salt=salt,
                        solvent_system="water",
                        composition={"water": 1.0},
                        composition_basis="mole_fraction",
                        x_name="molality",
                        x_value=float(m),
                        x_units="mol/kg",
                        y_name="miac_m",
                        y_value=float(y),
                        y_units="-",
                        curve_points=600,
                        category=salt,
                        display_order=order,
                    )
                )
                order += 1
    return rows


def _load_transfer_xy(path: Path) -> tuple[np.ndarray, np.ndarray]:
    fields, raw_rows = common.read_csv_rows(path)
    x_key, y_key = fields[0], fields[1]
    xs, ys = [], []
    for row in raw_rows:
        x = common.parse_float(row.get(x_key))
        y = common.parse_float(row.get(y_key))
        if x is not None and y is not None:
            xs.append(x)
            ys.append(y)
    return np.asarray(xs, dtype=float), np.asarray(ys, dtype=float)


def generate_figure_6() -> list[dict[str, str]]:
    data_root = figure_input_dir("figure_6")
    panels = [
        ("a)", "K+", "methanol", data_root / "K.csv"),
        ("b)", "Br-", "methanol", data_root / "Br.csv"),
        ("c)", "Na+", "ethanol", data_root / "Na.csv"),
        ("d)", "Cl-", "ethanol", data_root / "Cl.csv"),
    ]
    rows: list[dict[str, str]] = []
    order = 0
    for panel_id, ion, organic, source in panels:
        x_data, y_data = _load_transfer_xy(source)
        solvent_system = f"water-{organic}"
        for x_value, y_value in zip(x_data, y_data):
            rows.append(
                _row(
                    figure_id="figure_6",
                    panel_id=panel_id,
                    series_id=f"data_{ion}_{organic}",
                    series_label="Literature data",
                    source_type="literature",
                    ion=ion,
                    solvent_system=solvent_system,
                    x_name=f"x_{organic}",
                    x_value=float(x_value),
                    x_units="-",
                    y_name="gtrans",
                    y_value=float(y_value),
                    y_units="kJ/mol",
                    source_file=source,
                    category=f"{ion}_{organic}",
                    display_order=order,
                )
            )
            order += 1
        x_grid = np.linspace(0.0, 1.0, 401)
        y_model = common.transfer_curve(DATASET, ion, organic, x_grid)
        for x_value, y_value in zip(x_grid, y_model):
            rows.append(
                _row(
                    figure_id="figure_6",
                    panel_id=panel_id,
                    series_id=f"model_{ion}_{organic}",
                    series_label="ePC-SAFT fit",
                    source_type="model",
                    dataset=DATASET,
                    parameter_set=DATASET,
                    ion=ion,
                    solvent_system=solvent_system,
                    composition_basis="mole_fraction",
                    x_name=f"x_{organic}",
                    x_value=float(x_value),
                    x_units="-",
                    y_name="gtrans",
                    y_value=float(y_value),
                    y_units="kJ/mol",
                    curve_points=401,
                    category=f"{ion}_{organic}",
                    display_order=order,
                )
            )
            order += 1
    return rows


def generate_figure_7() -> list[dict[str, str]]:
    source = figure_input_path("figure_7", "methanol-NaBr.csv")
    data = common.read_miac_dataset(source, "methanol")
    m_max = max(float(row["molality"]) for row in data)
    rows: list[dict[str, str]] = []
    order = 0
    for entry in data:
        rows.append(
            _row(
                figure_id="figure_7",
                panel_id="main",
                series_id="data_NaBr_methanol",
                series_label="Literature",
                source_type="literature",
                salt="NaBr",
                solvent_system="methanol",
                composition={"methanol": 1.0},
                composition_basis="mole_fraction",
                x_name="molality",
                x_value=float(entry["molality"]),
                x_units="mol/kg",
                y_name="miac_m",
                y_value=float(entry["miac_m"]),
                y_units="-",
                source_file=source,
                category="NaBr",
                display_order=order,
            )
        )
        order += 1
    for series_id, label, options in (
        ("model_default", "Figiel 2025", None),
        ("model_rule1", "Rule 1", {"elec_model": {"relative_permittivity_rule": "linear"}}),
    ):
        m_grid, y_model = common.mean_ionic_activity_curve(
            DATASET, "NaBr", "methanol", {"methanol": 1.0}, m_max, points=500, user_options=options
        )
        for m, y in zip(m_grid, y_model):
            rows.append(
                _row(
                    figure_id="figure_7",
                    panel_id="main",
                    series_id=series_id,
                    series_label=label,
                    source_type="model",
                    dataset=DATASET,
                    parameter_set=DATASET,
                    salt="NaBr",
                    solvent_system="methanol",
                    composition={"methanol": 1.0},
                    composition_basis="mole_fraction",
                    x_name="molality",
                    x_value=float(m),
                    x_units="mol/kg",
                    y_name="miac_m",
                    y_value=float(y),
                    y_units="-",
                    curve_points=500,
                    user_options=options,
                    category="NaBr",
                    display_order=order,
                )
            )
            order += 1
    return rows


def generate_figure_8() -> list[dict[str, str]]:
    source_root = figure_input_dir("figure_8")
    rows: list[dict[str, str]] = []
    order = 0
    for panel_id, salt, m_max, _y_max in FIG8_PANELS:
        for solvent, label in (("methanol", "Methanol"), ("ethanol", "Ethanol")):
            source = source_root / f"{solvent}-{salt}.csv"
            for entry in common.read_miac_dataset(source, solvent):
                rows.append(
                    _row(
                        figure_id="figure_8",
                        panel_id=panel_id,
                        series_id=f"data_{salt}_{solvent}",
                        series_label=f"{label} data",
                        source_type="literature",
                        salt=salt,
                        solvent_system=solvent,
                        composition={solvent: 1.0},
                        composition_basis="mole_fraction",
                        x_name="molality",
                        x_value=float(entry["molality"]),
                        x_units="mol/kg",
                        y_name="miac_m",
                        y_value=float(entry["miac_m"]),
                        y_units="-",
                        source_file=source,
                        category=f"{salt}_{solvent}",
                        display_order=order,
                    )
                )
                order += 1
            curve_max = FIG8_CURVE_MAX_OVERRIDES.get((salt, solvent), m_max)
            m_grid, y_model = common.mean_ionic_activity_curve(
                DATASET, salt, solvent, {solvent: 1.0}, curve_max, points=600
            )
            for m, y in zip(m_grid, y_model):
                rows.append(
                    _row(
                        figure_id="figure_8",
                        panel_id=panel_id,
                        series_id=f"model_{salt}_{solvent}",
                        series_label=f"{label} model",
                        source_type="model",
                        dataset=DATASET,
                        parameter_set=DATASET,
                        salt=salt,
                        solvent_system=solvent,
                        composition={solvent: 1.0},
                        composition_basis="mole_fraction",
                        x_name="molality",
                        x_value=float(m),
                        x_units="mol/kg",
                        y_name="miac_m",
                        y_value=float(y),
                        y_units="-",
                        curve_points=600,
                        category=f"{salt}_{solvent}",
                        display_order=order,
                    )
                )
                order += 1
    return rows


def _read_weight_fraction_dataset(path: Path, solvent_system: str) -> list[dict[str, object]]:
    fields, raw_rows = common.read_csv_rows(path)
    lookup = {field.lower(): field for field in fields}
    molality_key = next((lookup[c] for c in ("molality", "m") if c in lookup), None)
    gamma_key = next((lookup[c] for c in ("miac_m", "gamma") if c in lookup), None)
    if molality_key is None or gamma_key is None:
        raise ValueError(f"Missing columns in {path}")
    organic = next(s for s in solvent_system.split("-") if s != "water")
    w_org_key = lookup.get(f"w_{organic}_salt_free".lower()) or lookup.get(f"w_{organic}".lower())
    w_water_key = (
        lookup.get("w_h2o_salt_free") or lookup.get("w_water_salt_free") or lookup.get("w_h2o") or lookup.get("w_water")
    )
    org_key = lookup.get(f"x_{organic}".lower()) or (
        lookup.get("x_methanol") if organic == "methanol" else lookup.get("x_ethanol")
    )
    water_key = lookup.get("x_h2o") or lookup.get("x_water")
    out = []
    for row in raw_rows:
        m = common.parse_float(row.get(molality_key))
        y = common.parse_float(row.get(gamma_key))
        w_org = common.parse_float(row.get(w_org_key)) if w_org_key else None
        w_water = common.parse_float(row.get(w_water_key)) if w_water_key else None
        if w_org is None:
            w_org = common.parse_float(row.get(org_key)) if org_key else None
            w_water = common.parse_float(row.get(water_key)) if water_key else None
        if m is None or y is None or w_org is None:
            continue
        if w_water is None:
            w_water = 1.0 - w_org
        weight_comp = common.normalized_comp(solvent_system, {"water": w_water, organic: w_org})
        out.append(
            {
                "molality": m,
                "miac_m": y,
                "w_org": weight_comp[organic],
                "weight_signature": tuple((s, round(weight_comp[s], 6)) for s in weight_comp),
                "weight_comp": weight_comp,
            }
        )
    out.sort(key=lambda item: float(item["molality"]))
    return out


def _group_by_weight(
    entries: Iterable[dict[str, object]],
) -> dict[tuple[tuple[str, float], ...], list[dict[str, object]]]:
    grouped: dict[tuple[tuple[str, float], ...], list[dict[str, object]]] = {}
    for entry in entries:
        grouped.setdefault(entry["weight_signature"], []).append(entry)
    for values in grouped.values():
        values.sort(key=lambda item: float(item["molality"]))
    return grouped


def _closest_group(
    entries: list[dict[str, object]], target_w_org: float, tol: float = FIG9_DATA_TOL
) -> list[dict[str, object]] | None:
    candidates = []
    for values in _group_by_weight(entries).values():
        w_org = float(values[0]["w_org"])
        candidates.append((abs(w_org - target_w_org), values))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1] if candidates[0][0] <= tol else None


def _figure9_curve_m_max(panel_id: str, target_w_org: float, default_max: float) -> float:
    return min(default_max, FIG9_CURVE_MAX_BY_PANEL.get(panel_id, {}).get(target_w_org, default_max))


def generate_figure_9() -> list[dict[str, str]]:
    source_root = figure_input_dir("figure_9")
    rows: list[dict[str, str]] = []
    order = 0
    for panel_id, salt, solvent_system, m_max in FIG9_PANELS:
        source = source_root / f"{solvent_system}-{salt}.csv"
        entries = _read_weight_fraction_dataset(source, solvent_system) if source.exists() else []
        for target_w_org in FIG9_TARGETS:
            selected = _closest_group(entries, target_w_org) if entries else None
            if selected:
                for entry in selected:
                    rows.append(
                        _row(
                            figure_id="figure_9",
                            panel_id=panel_id,
                            series_id=f"data_{salt}_{solvent_system}_w{target_w_org:.1f}",
                            series_label=f"w_org={target_w_org:.1f} data",
                            source_type="literature",
                            salt=salt,
                            solvent_system=solvent_system,
                            composition=entry["weight_comp"],
                            composition_basis="salt_free_weight_fraction",
                            target_w_org=target_w_org,
                            x_name="molality",
                            x_value=float(entry["molality"]),
                            x_units="mol/kg",
                            y_name="miac_m",
                            y_value=float(entry["miac_m"]),
                            y_units="-",
                            source_file=source,
                            category=f"{salt}_{solvent_system}_w{target_w_org:.1f}",
                            display_order=order,
                        )
                    )
                    order += 1
            curve_max = _figure9_curve_m_max(panel_id, target_w_org, m_max)
            comp_model = common.target_weight_fraction_to_comp(solvent_system, target_w_org)
            m_grid, y_model = common.mean_ionic_activity_curve(
                DATASET, salt, solvent_system, comp_model, curve_max, points=600
            )
            for m, y in zip(m_grid, y_model):
                rows.append(
                    _row(
                        figure_id="figure_9",
                        panel_id=panel_id,
                        series_id=f"model_{salt}_{solvent_system}_w{target_w_org:.1f}",
                        series_label=f"w_org={target_w_org:.1f} model",
                        source_type="model",
                        dataset=DATASET,
                        parameter_set=DATASET,
                        salt=salt,
                        solvent_system=solvent_system,
                        composition=comp_model,
                        composition_basis="salt_free_weight_fraction",
                        target_w_org=target_w_org,
                        x_name="molality",
                        x_value=float(m),
                        x_units="mol/kg",
                        y_name="miac_m",
                        y_value=float(y),
                        y_units="-",
                        curve_points=600,
                        category=f"{salt}_{solvent_system}_w{target_w_org:.1f}",
                        display_order=order,
                    )
                )
                order += 1
    return rows


GENERATORS = {
    "figure_1": generate_figure_1,
    "figure_2": generate_figure_2,
    "figure_3": generate_figure_3,
    "figure_4": generate_figure_4,
    "figure_5": generate_figure_5,
    "figure_6": generate_figure_6,
    "figure_7": generate_figure_7,
    "figure_8": generate_figure_8,
    "figure_9": generate_figure_9,
}


def write_figure(figure_id: str) -> Path:
    return _write_payload(figure_id, GENERATORS[figure_id]())


def write_all() -> list[Path]:
    return [write_figure(figure_id) for figure_id in GENERATORS]


def _compare_values(expected: str, actual: str, field: str, rtol: float, atol: float) -> bool:
    if field not in NUMERIC_FIELDS:
        return expected == actual
    if expected == actual:
        return True
    if not expected and not actual:
        return True
    try:
        exp = float(expected)
        act = float(actual)
    except ValueError:
        return expected == actual
    if math.isnan(exp) and math.isnan(act):
        return True
    return math.isclose(exp, act, rel_tol=rtol, abs_tol=atol)


def compare_all(rtol: float = 1e-9, atol: float = 1e-10) -> list[str]:
    failures: list[str] = []
    for figure_id, generator in GENERATORS.items():
        baseline_path = payload_path(figure_id)
        if not baseline_path.exists():
            failures.append(f"{figure_id}: missing baseline {baseline_path}")
            continue
        baseline = read_payload(figure_id)
        current = generator()
        if len(baseline) != len(current):
            failures.append(f"{figure_id}: row count changed, baseline={len(baseline)} current={len(current)}")
            continue
        for index, (expected, actual) in enumerate(zip(baseline, current), start=2):
            for field in FIELDNAMES:
                if not _compare_values(expected.get(field, ""), actual.get(field, ""), field, rtol, atol):
                    failures.append(
                        f"{figure_id}:{index}: {field} changed from {expected.get(field, '')!r} to {actual.get(field, '')!r}"
                    )
                    break
    return failures


def main() -> None:
    paths = write_all()
    for path in paths:
        print(path.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
