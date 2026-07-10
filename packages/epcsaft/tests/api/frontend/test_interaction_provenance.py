from __future__ import annotations

import json
from pathlib import Path

import pytest
from epcsaft import ParameterSet
from epcsaft._types import InputError
from epcsaft.frontend import mixture as mixture_module
from epcsaft.model import datasets
from epcsaft.model import parameters as parameter_model

REPO_ROOT = Path(__file__).resolve().parents[5]


def _pure_record(component: str) -> dict[str, object]:
    return {
        "component": component,
        "molar_mass": 44.01e-3,
        "molar_mass_units": "kg/mol",
        "m": 2.1,
        "sigma": 3.4,
        "epsilon_k": 220.0,
        "charge": 0.0,
        "epsilon_k_ab": 0.0,
        "kappa_ab": 0.0,
        "association_scheme": None,
        "association_sites": [],
        "relative_permittivity": 1.0,
        "born_diameter": 0.0,
        "solvation_factor": 1.0,
    }


def _parameter_payload(*components: str) -> dict[str, object]:
    return {
        "schema": "epcsaft.parameter-set",
        "schema_version": 2,
        "components": list(components),
        "pure_records": [_pure_record(component) for component in components],
        "interactions": [],
        "interaction_policies": [],
        "metadata": {"source": "Test literature table", "source_backed": True},
        "runtime_options": {},
    }


def test_parameter_schema_v2_replaces_scalar_defaulted_binary_records() -> None:
    parameters = ParameterSet.from_dict(_parameter_payload("Component A"))

    serialized = json.loads(parameters.to_json())
    assert serialized["schema_version"] == 2
    assert serialized["interactions"] == []
    assert serialized["interaction_policies"] == []
    assert "binary_records" not in serialized

    legacy = _parameter_payload("Component A")
    legacy["schema_version"] = 1
    legacy["binary_records"] = []
    legacy.pop("interactions")
    legacy.pop("interaction_policies")
    with pytest.raises(InputError, match=r"schema_version 2"):
        ParameterSet.from_dict(legacy)


def _provenance(*, kind: str = "literature", source: str = "Source Table 4") -> dict[str, str]:
    return {"kind": kind, "source": source}


def _constant(
    family: str,
    *,
    components: tuple[str, str] = ("Component A", "Component B"),
    value: object = 0.1,
    provenance: object | None = None,
) -> dict[str, object]:
    return {
        "kind": "constant",
        "family": family,
        "components": list(components),
        "value": value,
        "provenance": _provenance() if provenance is None else provenance,
    }


def _structural_zero(family: str) -> dict[str, object]:
    return {
        "kind": "structural_zero",
        "family": family,
        "components": ["Component A", "Component B"],
        "reason": "This named pair follows the cited equation policy.",
        "provenance": _provenance(kind="model_structural_zero", source="EqID pair-policy"),
    }


@pytest.mark.parametrize("kind", ["", "measured", "guessed"])
def test_interaction_provenance_rejects_unknown_kinds(kind: str) -> None:
    provenance_type = parameter_model.InteractionProvenance

    with pytest.raises(InputError, match=r"provenance kind"):
        provenance_type(kind=kind, source="Source Table 4")


def test_interaction_provenance_requires_a_nonblank_source_identity() -> None:
    provenance_type = parameter_model.InteractionProvenance

    with pytest.raises(InputError, match=r"provenance source.*nonblank"):
        provenance_type(kind="literature", source="")


@pytest.mark.parametrize("value", [None, "", float("nan"), float("inf"), float("-inf")])
def test_constant_interaction_rejects_absent_blank_or_nonfinite_values(value: object) -> None:
    payload = _parameter_payload("Component A", "Component B")
    payload["interactions"] = [_constant("k_ij", value=value)]

    with pytest.raises(InputError, match=r"constant interaction value.*finite"):
        ParameterSet.from_dict(payload)


def test_zero_interaction_requires_explicit_provenance() -> None:
    payload = _parameter_payload("Component A", "Component B")
    record = _constant("k_ij", value=0.0)
    record.pop("provenance")
    payload["interactions"] = [record]

    with pytest.raises(InputError, match=r"interaction.*provenance"):
        ParameterSet.from_dict(payload)


@pytest.mark.parametrize(
    "record,match",
    [
        ({"kind": "constant", "family": "k_ij", "components": ["Component A"], "value": 0.1, "provenance": _provenance()}, r"exactly two"),
        (_constant("k_ij", components=("Component A", "Component A")), r"diagonal"),
        (_constant("unknown_family"), r"interaction family"),
        ({**_constant("k_ij"), "mystery": 1}, r"unsupported key.*mystery"),
    ],
)
def test_interaction_records_reject_invalid_shape_family_and_unknown_fields(
    record: dict[str, object],
    match: str,
) -> None:
    payload = _parameter_payload("Component A", "Component B")
    payload["interactions"] = [record]

    with pytest.raises(InputError, match=match):
        ParameterSet.from_dict(payload)


@pytest.mark.parametrize("reverse", [False, True])
def test_duplicate_or_reversed_interaction_records_are_rejected(reverse: bool) -> None:
    payload = _parameter_payload("Component A", "Component B")
    duplicate = _constant(
        "k_ij",
        components=("Component B", "Component A") if reverse else ("Component A", "Component B"),
        value=0.2,
    )
    payload["interactions"] = [_constant("k_ij"), duplicate]

    with pytest.raises(InputError, match=r"(?i)duplicate.*k_ij.*Component A.*Component B"):
        ParameterSet.from_dict(payload)


def test_parameter_set_requires_every_off_diagonal_interaction_family() -> None:
    payload = _parameter_payload("Component A", "Component B")
    payload["interactions"] = [_constant("k_ij")]

    with pytest.raises(InputError, match=r"(?i)missing interaction.*l_ij.*k_hb_ij.*Component A.*Component B"):
        ParameterSet.from_dict(payload)


def test_named_structural_zero_policies_complete_the_interaction_graph() -> None:
    payload = _parameter_payload("Component A", "Component B")
    payload["interactions"] = [_constant("k_ij", value=0.125)]
    payload["interaction_policies"] = [_structural_zero("l_ij"), _structural_zero("k_hb_ij")]

    parameters = ParameterSet.from_dict(payload)
    runtime = parameters.to_runtime_dict()

    assert runtime["k_ij"].tolist() == [[0.0, 0.125], [0.125, 0.0]]
    assert runtime["l_ij"].tolist() == [[0.0, 0.0], [0.0, 0.0]]
    assert runtime["k_hb"].tolist() == [[0.0, 0.0], [0.0, 0.0]]
    assert runtime["_binary_interaction_provenance_status"] == "complete_interaction_graph"
    receipt = runtime["_interaction_provenance_receipt"]
    assert receipt["diagonal_policy"] == "equation_defined_identity_zero"
    assert receipt["constant_record_count"] == 1
    assert receipt["structural_zero_policy_count"] == 2


@pytest.mark.parametrize("misplaced_field", ["interactions", "interaction_policies"])
def test_direct_parameter_set_construction_rejects_misplaced_interaction_owner(
    misplaced_field: str,
) -> None:
    valid_payload = _parameter_payload("Component A", "Component B")
    valid_payload["interactions"] = [_constant("k_ij", value=0.125)]
    valid_payload["interaction_policies"] = [_structural_zero("l_ij"), _structural_zero("k_hb_ij")]
    valid = ParameterSet.from_dict(valid_payload)
    misplaced = (
        valid.interaction_policies[0]
        if misplaced_field == "interactions"
        else valid.interactions[0]
    )

    with pytest.raises(InputError, match=rf"{misplaced_field}.*typed"):
        ParameterSet(
            components=valid.components,
            pure_records=valid.pure_records,
            interactions=(misplaced,) if misplaced_field == "interactions" else valid.interactions,
            interaction_policies=(misplaced,)
            if misplaced_field == "interaction_policies"
            else valid.interaction_policies,
            metadata=valid.metadata,
        )


def test_frontend_does_not_own_a_second_interaction_matrix_serializer() -> None:
    assert not hasattr(mixture_module, "_binary_matrices")


def test_linear_temperature_interaction_is_typed_and_cannot_freeze_at_construction() -> None:
    payload = _parameter_payload("Component A", "Component B")
    payload["interactions"] = [
        {
            "kind": "linear_temperature",
            "family": "k_ij",
            "components": ["Component A", "Component B"],
            "slope": 1.6e-4,
            "intercept": -0.0461,
            "temperature_units": "K",
            "provenance": _provenance(source="Ascani 2023 Table 2"),
        }
    ]
    payload["interaction_policies"] = [_structural_zero("l_ij"), _structural_zero("k_hb_ij")]

    parameters = ParameterSet.from_dict(payload)
    serialized = json.loads(parameters.to_json())

    assert serialized["interactions"][0]["kind"] == "linear_temperature"
    with pytest.raises(InputError, match=r"state temperature.*linear_temperature.*k_ij"):
        parameters.to_runtime_dict()


@pytest.mark.parametrize(
    "field,value",
    [
        ("slope", float("nan")),
        ("intercept", ""),
        ("temperature_units", "degC"),
    ],
)
def test_linear_temperature_interaction_rejects_invalid_coefficients_and_units(
    field: str,
    value: object,
) -> None:
    payload = _parameter_payload("Component A", "Component B")
    record = {
        "kind": "linear_temperature",
        "family": "k_ij",
        "components": ["Component A", "Component B"],
        "slope": 1.6e-4,
        "intercept": -0.0461,
        "temperature_units": "K",
        "provenance": _provenance(source="Ascani 2023 Table 2"),
    }
    record[field] = value
    payload["interactions"] = [record]
    payload["interaction_policies"] = [_structural_zero("l_ij"), _structural_zero("k_hb_ij")]

    with pytest.raises(InputError, match=field):
        ParameterSet.from_dict(payload)


def _write_two_component_interaction_source(
    root: Path,
    *,
    k_forward: str = "0.125",
    k_reverse: str = "0.125",
    k_source: str = "Source Table 4",
    k_provenance_status: str = "source_backed",
    duplicate_manifest_pair: bool = False,
) -> Path:
    binary = root / "mixed" / "binary_interaction"
    binary.mkdir(parents=True)
    (binary / "k_ij.csv").write_text(
        "component,Component A,Component B\n"
        f"Component A,0,{k_forward}\n"
        f"Component B,{k_reverse},0\n",
        encoding="utf-8",
    )
    for name in ("l_ij.csv", "k_hb_ij.csv"):
        (binary / name).write_text(
            "component,Component A,Component B\n"
            "Component A,0,0\n"
            "Component B,0,0\n",
            encoding="utf-8",
        )
    duplicate = (
        f"k_ij,Component B,Component A,{k_forward},{k_source},{k_provenance_status}\n"
        if duplicate_manifest_pair
        else ""
    )
    (binary / "source_manifest.csv").write_text(
        "parameter,component_i,component_j,value,source,provenance_status\n"
        f"k_ij,Component A,Component B,{k_forward},{k_source},{k_provenance_status}\n"
        f"{duplicate}"
        "l_ij,Component A,Component B,0,Source Eq. 5,source_backed\n"
        "k_hb_ij,Component A,Component B,0,Source Eq. 6,source_backed\n",
        encoding="utf-8",
    )
    return root


def _write_pure_source(root: Path, components: tuple[str, ...]) -> Path:
    pure = root / "pure"
    pure.mkdir(parents=True, exist_ok=True)
    rows = [
        f"{component},2.1,3.4,220.0,0,0,,0,1,0,1,0.04401,Source Pure Table"
        for component in components
    ]
    (pure / "any_solvent.csv").write_text(
        "component,m,s,e,e_assoc,vol_a,assoc_scheme,z,dielc,d_born,f_solv,MW,source\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )
    return root


def _write_structural_zero_manifest(
    root: Path,
    *,
    value: str = "0",
    source: str = "Source Eq. 5",
    reason: str = "unmodified pair rule",
) -> None:
    binary = root / "mixed" / "binary_interaction"
    (binary / "source_manifest.csv").write_text(
        "parameter,component_i,component_j,value,source,provenance_status,reason\n"
        "k_ij,Component A,Component B,0.125,Source Table 4,source_backed,\n"
        f"l_ij,Component A,Component B,{value},{source},model_structural_zero,{reason}\n"
        "k_hb_ij,Component A,Component B,0,Source Eq. 6,source_backed,\n",
        encoding="utf-8",
    )


def test_source_interaction_loader_returns_typed_explicit_values_and_zeros(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")

    records = datasets._load_source_interactions(root, ("Component A", "Component B"))

    assert len(records) == 3
    assert {record.family for record in records} == {"k_ij", "l_ij", "k_hb_ij"}
    assert {record.value for record in records if record.family != "k_ij"} == {0.0}
    assert all(record.provenance.kind == "literature" for record in records)


def test_source_interaction_loader_preserves_fitted_provenance(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(
        tmp_path / "parameters",
        k_provenance_status="fitted",
    )

    records = datasets._load_source_interactions(root, ("Component A", "Component B"))
    by_family = {record.family: record for record in records}

    assert by_family["k_ij"].provenance.kind == "fitted"
    assert by_family["l_ij"].provenance.kind == "literature"


@pytest.mark.parametrize("provenance_status", ["source_backed", "fitted"])
@pytest.mark.parametrize(
    "source",
    [
        "default zero for unpublished values",
        "unpublished interaction value",
        "unresolved source reference",
        "no source reference",
    ],
)
def test_source_interaction_manifest_rejects_executable_status_with_non_evidence_source(
    tmp_path: Path,
    provenance_status: str,
    source: str,
) -> None:
    root = _write_two_component_interaction_source(
        tmp_path / "parameters",
        k_source=source,
        k_provenance_status=provenance_status,
    )

    with pytest.raises(InputError, match=r"(?i)source.*contradicts.*provenance status"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_loader_returns_named_structural_zero_policy(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    _write_structural_zero_manifest(root)

    loaded = datasets._load_source_interactions(root, ("Component A", "Component B"))

    policies = [item for item in loaded if isinstance(item, parameter_model.StructuralZeroPolicy)]
    assert len(policies) == 1
    assert policies[0].family == "l_ij"
    assert policies[0].reason == "unmodified pair rule"
    assert policies[0].provenance.kind == "model_structural_zero"
    assert not any(
        isinstance(item, parameter_model.ConstantInteractionRecord) and item.family == "l_ij"
        for item in loaded
    )


@pytest.mark.parametrize(
    ("value", "source", "reason", "match"),
    [
        ("0.1", "Source Eq. 5", "unmodified pair rule", r"(?i)structural zero.*numeric zero"),
        ("0*T+0", "Source Eq. 5", "unmodified pair rule", r"(?i)structural zero.*numeric zero"),
        ("0", "", "unmodified pair rule", r"(?i)structural zero.*source.*nonblank"),
        ("0", "Source Eq. 5", "", r"(?i)structural zero.*reason.*nonblank"),
    ],
)
def test_source_interaction_manifest_rejects_invalid_structural_zero_rows(
    tmp_path: Path,
    value: str,
    source: str,
    reason: str,
    match: str,
) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    _write_structural_zero_manifest(root, value=value, source=source, reason=reason)

    with pytest.raises(InputError, match=match):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


@pytest.mark.parametrize(
    "forward,reverse,match",
    [
        ("", "", r"(?i)blank.*k_ij.*Component A.*Component B"),
        ("nan", "nan", r"(?i)non-finite.*k_ij.*Component A.*Component B"),
        ("0.125", "0.126", r"asymmetric.*k_ij.*Component A.*Component B"),
    ],
)
def test_source_interaction_loader_rejects_blank_nonfinite_and_asymmetric_cells(
    tmp_path: Path,
    forward: str,
    reverse: str,
    match: str,
) -> None:
    root = _write_two_component_interaction_source(
        tmp_path / "parameters",
        k_forward=forward,
        k_reverse=reverse,
    )

    with pytest.raises(InputError, match=match):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_loader_rejects_zero_without_source_identity(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(
        tmp_path / "parameters",
        k_forward="0",
        k_reverse="0",
        k_source="",
    )

    with pytest.raises(InputError, match=r"provenance source.*nonblank"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_loader_rejects_duplicate_reversed_manifest_pairs(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(
        tmp_path / "parameters",
        duplicate_manifest_pair=True,
    )

    with pytest.raises(InputError, match=r"(?i)duplicate.*k_ij.*Component A.*Component B"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_manifest_requires_provenance_status_column(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    path = root / "mixed" / "binary_interaction" / "source_manifest.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text(
        "\n".join(",".join(line.split(",")[:-1]) for line in lines) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(InputError, match=r"missing required column.*provenance_status"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_manifest_rejects_blank_provenance_status(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    path = root / "mixed" / "binary_interaction" / "source_manifest.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[1] = lines[1].rsplit(",", 1)[0] + ","
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(InputError, match=r"(?i)explicit k_ij pair Component A.*Component B.*nonblank.*provenance status"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_manifest_rejects_duplicate_headers(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    path = root / "mixed" / "binary_interaction" / "source_manifest.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[0] += ",provenance_status"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(InputError, match=r"duplicate.*provenance_status"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_loader_rejects_unmanifested_nonzero_matrix_pair(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    binary = root / "mixed" / "binary_interaction"
    (binary / "k_ij.csv").write_text(
        "component,Component A,Component B,Component C\n"
        "Component A,0,0.125,0.2\n"
        "Component B,0.125,0,0\n"
        "Component C,0.2,0,0\n",
        encoding="utf-8",
    )
    for name in ("l_ij.csv", "k_hb_ij.csv"):
        (binary / name).write_text(
            "component,Component A,Component B,Component C\n"
            "Component A,0,0,0\n"
            "Component B,0,0,0\n"
            "Component C,0,0,0\n",
            encoding="utf-8",
        )

    with pytest.raises(InputError, match=r"(?i)matrix.*unmanifested.*k_ij.*Component A.*Component C"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_loader_rejects_invalid_matrix_dimensions(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    (root / "mixed" / "binary_interaction" / "k_ij.csv").write_text(
        "component,Component A,Component B\n"
        "Component A,0,0.125\n",
        encoding="utf-8",
    )

    with pytest.raises(InputError, match=r"invalid dimensions"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_loader_rejects_surplus_matrix_cells(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    (root / "mixed" / "binary_interaction" / "k_ij.csv").write_text(
        "component,Component A,Component B\n"
        "Component A,0,0.125,surplus\n"
        "Component B,0.125,0\n",
        encoding="utf-8",
    )

    with pytest.raises(InputError, match=r"(?i)matrix.*row 2.*surplus"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_manifest_rejects_unknown_columns(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    path = root / "mixed" / "binary_interaction" / "source_manifest.csv"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    path.write_text(
        lines[0] + ",mystery\n" + "\n".join(line + "," for line in lines[1:]) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(InputError, match=r"unsupported.*mystery"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_manifest_rejects_surplus_row_cells(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    path = root / "mixed" / "binary_interaction" / "source_manifest.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[1] += ",surplus"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(InputError, match=r"(?i)manifest.*row 2.*surplus"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_pure_csv_loader_rejects_surplus_cells(tmp_path: Path) -> None:
    path = tmp_path / "pure.csv"
    path.write_text(
        "component,m,s,e,e_assoc,vol_a,assoc_scheme,z,dielc,d_born,f_solv,MW,source\n"
        "Component A,2.1,3.4,220.0,0,0,,0,1,0,1,0.04401,Source Pure Table,surplus\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"row 2.*surplus"):
        datasets._load_component_rows(path)


def test_source_interaction_manifest_rejects_value_mismatch_for_valid_pair(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    path = root / "mixed" / "binary_interaction" / "source_manifest.csv"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("k_ij,Component A,Component B,0.125,", "k_ij,Component A,Component B,0.126,"), encoding="utf-8")

    with pytest.raises(InputError, match=r"source manifest value does not match matrix.*k_ij.*Component A.*Component B"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_source_interaction_manifest_rejects_unrequested_component_identities(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    path = root / "mixed" / "binary_interaction" / "source_manifest.csv"
    with path.open("a", encoding="utf-8") as handle:
        handle.write("k_ij,Component A,Ghost,0.25,Source Table 9,source_backed\n")

    with pytest.raises(InputError, match=r"(?i)manifest.*Ghost.*matrix"):
        datasets._load_source_interactions(root, ("Component A", "Component B"))


def test_gross_wildcard_zeros_do_not_complete_missing_pair_evidence() -> None:
    root = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "parameters"

    with pytest.raises(InputError, match=r"(?i)wildcard.*l_ij.*k_hb_ij.*methanol.*cyclohexane"):
        datasets._load_source_interactions(root, ("methanol", "cyclohexane"))


def test_baygi_table3_kij_values_match_matrix_and_manifest_without_resolving_wildcards() -> None:
    root = REPO_ROOT / "analyses" / "paper_validation" / "2015_baygi" / "parameters"
    binary = root / "mixed" / "binary_interaction"
    matrix = datasets._load_strict_interaction_matrix(binary / "k_ij.csv", "k_ij")
    manifest, wildcard_families = datasets._load_interaction_source_manifest(binary / "source_manifest.csv")
    expected = {
        ("MEA-2B", "H2O-2B"): -0.0420,
        ("MEA-3B", "H2O-2B"): -0.0146,
        ("MEA-4C", "H2O-2B"): -0.0362,
        ("MEA-2B", "H2O-4C"): -0.1305,
        ("MEA-3B", "H2O-4C"): -0.0520,
        ("MEA-4C", "H2O-4C"): -0.1245,
    }

    assert wildcard_families == {"l_ij", "k_hb_ij"}
    for pair, value in expected.items():
        normalized_pair = tuple(datasets._normalize_component(component) for component in pair)
        key = frozenset(normalized_pair)
        assert manifest[("k_ij", key)][0] == ("constant", value)
        assert matrix[normalized_pair] == ("constant", value)
        assert matrix[normalized_pair[::-1]] == ("constant", value)


def test_bulow_asymmetric_matrix_is_rejected_without_triangle_selection() -> None:
    root = REPO_ROOT / "analyses" / "paper_validation" / "2019_bulow" / "parameters"

    with pytest.raises(InputError, match=r"asymmetric.*k_ij.*H2O.*C6py\+"):
        datasets._load_source_interactions(root, ("H2O", "C6py+"))


def test_held_2012_has_complete_explicit_pair_family_records() -> None:
    root = REPO_ROOT / "analyses" / "paper_validation" / "2012_held" / "parameters"
    components = ("Br-", "Cl-", "Ethanol", "H2O", "I-", "K+", "Li+", "Methanol", "NH4+", "Na+")

    loaded = datasets._load_source_interactions(root, components)
    _manifest, wildcard_families = datasets._load_interaction_source_manifest(
        root / "mixed" / "binary_interaction" / "source_manifest.csv"
    )

    records = [item for item in loaded if not isinstance(item, parameter_model.StructuralZeroPolicy)]
    policies = [item for item in loaded if isinstance(item, parameter_model.StructuralZeroPolicy)]
    assert len(loaded) == 135
    assert len(records) == 47
    assert len(policies) == 88
    assert wildcard_families == set()
    by_key = {(record.family, frozenset(record.components)): record for record in records}
    fitted = {
        ("k_ij", frozenset(("H2O", "Ethanol"))): -0.049,
        ("k_ij", frozenset(("H2O", "Methanol"))): -0.085,
        ("l_ij", frozenset(("H2O", "Ethanol"))): -0.01,
        ("k_hb_ij", frozenset(("H2O", "Ethanol"))): 0.2,
    }
    for key, value in fitted.items():
        assert by_key[key].value == pytest.approx(value)
        assert by_key[key].provenance.kind == "fitted"
        assert by_key[key].provenance.source == "Held 2012 Table 5 footnote c / Hall et al. data"
    assert by_key[("k_ij", frozenset(("Br-", "Ethanol")))].provenance.kind == "literature"
    assert by_key[("k_ij", frozenset(("Br-", "Cl-")))].provenance.kind == "literature"
    assert sum(policy.family == "l_ij" for policy in policies) == 44
    assert sum(policy.family == "k_hb_ij" for policy in policies) == 44
    assert {policy.reason for policy in policies if policy.family == "l_ij"} == {"unmodified Lorentz rule"}
    assert {policy.reason for policy in policies if policy.family == "k_hb_ij"} == {
        "unmodified association-volume rule"
    }


def test_dataset_loading_and_runtime_serialization_share_the_typed_interaction_owner(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    _write_pure_source(root, ("Component A", "Component B"))

    parameters = ParameterSet.from_dataset(
        root,
        ("Component A", "Component B"),
        x=(0.4, 0.6),
        T=298.15,
    )
    direct_runtime = datasets.get_prop_dict(root, ("Component A", "Component B"), (0.4, 0.6), 298.15)
    typed_runtime = parameters.to_runtime_dict()

    assert len(parameters.interactions) == 3
    assert direct_runtime["k_ij"].tolist() == typed_runtime["k_ij"].tolist()
    assert direct_runtime["l_ij"].tolist() == typed_runtime["l_ij"].tolist()
    assert direct_runtime["k_hb"].tolist() == typed_runtime["k_hb"].tolist()
    assert not hasattr(datasets, "_matrix_value")


def test_dataset_loading_partitions_structural_zero_policies_from_interaction_records(tmp_path: Path) -> None:
    root = _write_two_component_interaction_source(tmp_path / "parameters")
    _write_structural_zero_manifest(root)
    _write_pure_source(root, ("Component A", "Component B"))

    parameters = ParameterSet.from_dataset(
        root,
        ("Component A", "Component B"),
        x=(0.4, 0.6),
        T=298.15,
    )

    assert {record.family for record in parameters.interactions} == {"k_ij", "k_hb_ij"}
    assert len(parameters.interaction_policies) == 1
    assert parameters.interaction_policies[0].family == "l_ij"
    assert parameters.interaction_policies[0].provenance.kind == "model_structural_zero"


def test_single_component_dataset_needs_no_off_diagonal_interaction_files(tmp_path: Path) -> None:
    root = _write_pure_source(tmp_path / "parameters", ("Component A",))

    parameters = ParameterSet.from_dataset(root, ("Component A",), x=(1.0,), T=298.15)
    runtime = parameters.to_runtime_dict()

    assert parameters.interactions == ()
    assert runtime["k_ij"].tolist() == [[0.0]]
    assert runtime["l_ij"].tolist() == [[0.0]]
    assert runtime["k_hb"].tolist() == [[0.0]]
