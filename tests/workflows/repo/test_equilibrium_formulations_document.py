from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FORMULATIONS_PATH = REPO_ROOT / "docs" / "latex" / "equilibrium_formulations.tex"
OTHER_MATH_OWNERS = (
    REPO_ROOT / "docs" / "latex" / "equations.tex",
    REPO_ROOT / "docs" / "latex" / "algorithms.tex",
    REPO_ROOT / "docs" / "latex" / "explicit_assocation.tex",
)

LABEL_PATTERN = re.compile(r"\\label\{([^}]+)\}")
REFERENCE_PATTERN = re.compile(r"\\(?:eqref|ref)\{([^}]+)\}")
CITATION_PATTERN = re.compile(r"\\cite\{([^}]+)\}")
BIBITEM_PATTERN = re.compile(r"\\bibitem\{([^}]+)\}")

BIBLIOGRAPHY_RECORDS = {
    "Pereira2012": (
        "F.~E. Pereira, G.~Jackson, A.~Galindo, and C.~S. Adjiman",
        "https://doi.org/10.1016/j.compchemeng.2011.07.009",
    ),
    "Perdomo2025": (
        "F.~A. Perdomo, G.~Jackson, A.~Mitsos, A.~Galindo, and C.~S. Adjiman",
        "https://doi.org/10.1016/j.compchemeng.2024.108977",
    ),
    "Ascani2022": (
        "M.~Ascani, G.~Sadowski, and C.~Held",
        "https://doi.org/10.1021/acs.jced.1c00866",
    ),
    "Ascani2023": (
        "M.~Ascani, G.~Sadowski, and C.~Held",
        "https://doi.org/10.3390/molecules28041768",
    ),
}


def _source() -> str:
    assert FORMULATIONS_PATH.is_file(), "missing canonical equilibrium formulations TeX owner"
    return FORMULATIONS_PATH.read_text(encoding="utf-8")


def test_equilibrium_formulations_document_owns_all_required_families() -> None:
    source = _source()
    normalized = " ".join(source.split())

    required_sections = (
        "Shared notation, conventions, and topology",
        "Public pressure-boundary and pure-saturation formulations",
        "Neutral HELD",
        "Association-aware neutral HELD",
        "Perdomo modified-mole HELD2",
        "Ascani counterion-pair equilibrium",
        "Standalone chemical equilibrium",
        "Coupled phase-and-chemical equilibrium",
        "Source-to-formulation reconciliation",
        "Thermodynamic and numerical consistency review",
    )
    for section in required_sections:
        assert section in source

    for evidence_label in ("verified", "inference", "assumption", "unknown"):
        assert f"\\Evidence{{{evidence_label}}}" in source

    for required_guard in (
        "canonical Stage III problem is direct total-free-energy minimization",
        "Residual solving is not the canonical Stage III formulation",
        "individual ionic chemical-potential equality is not a certificate",
        "Perdomo and Ascani formulations are not equated",
        "CPE is not standalone CE followed by a nonreactive flash",
    ):
        assert required_guard.lower() in normalized.lower()


def test_equilibrium_formulations_document_preserves_current_public_surface() -> None:
    source = _source()
    normalized = " ".join(source.split())

    assert (
        "The complete production-exposed equilibrium route set is "
        r"\texttt{bubble\_pressure}, \texttt{dew\_pressure}, and "
        r"scoped \texttt{single\_component\_vle}."
    ) in normalized
    for closed_status in (
        "Neutral HELD & internal components; controller absent/deferred",
        "Association-aware neutral HELD & internal components; controller absent/deferred",
        "Perdomo modified-mole HELD2 & absent/deferred",
        "Ascani counterion-pair equilibrium & internal components; controller absent/deferred",
        "Standalone CE & public schemas/helpers; executable solver internal validation only",
        "CPE & absent/deferred",
    ):
        assert closed_status in source


def test_equilibrium_formulations_labels_references_and_citations_are_isolated() -> None:
    source = _source()
    labels = LABEL_PATTERN.findall(source)
    references = REFERENCE_PATTERN.findall(source)
    citations = [key for group in CITATION_PATTERN.findall(source) for key in group.split(",")]
    bibitems = BIBITEM_PATTERN.findall(source)

    assert labels
    assert all(label.startswith(("eq:eqform:", "sec:eqform:", "tab:eqform:", "app:eqform:")) for label in labels)
    assert [label for label, count in Counter(labels).items() if count > 1] == []
    assert set(references) <= set(labels)
    assert citations
    assert set(citations) == set(bibitems) == set(BIBLIOGRAPHY_RECORDS)
    assert [key for key, count in Counter(bibitems).items() if count > 1] == []

    other_labels = {
        label
        for owner in OTHER_MATH_OWNERS
        for label in LABEL_PATTERN.findall(owner.read_text(encoding="utf-8"))
    }
    assert set(labels).isdisjoint(other_labels)


def test_equilibrium_formulations_is_standalone_and_source_reconciled() -> None:
    source = _source()

    assert "\\input{" not in source
    assert "\\include{" not in source
    assert "% EqID:" not in source
    assert "\\begin{thebibliography}" in source
    for key, (authors, doi) in BIBLIOGRAPHY_RECORDS.items():
        record = source.split(f"\\bibitem{{{key}}}", maxsplit=1)[1].split("\\bibitem", maxsplit=1)[0]
        assert authors in record
        assert doi in record
    assert "Source equation or statement" in source
    assert "Repository formulation owner" in source
    assert "Degrees of freedom / rank" in source
    assert "Certificate independence" in source
    assert "Phase-degeneracy behavior" in source
