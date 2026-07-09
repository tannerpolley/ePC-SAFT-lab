from __future__ import annotations

from pathlib import Path

from scripts.dev import check_text_gates


def _write_source(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_scan_text_file_accepts_descriptive_status_identifiers(tmp_path: Path) -> None:
    source = _write_source(
        tmp_path / "status_report.py",
        "\n".join(
            (
                'native_status = "converged"',
                'derivative_status = "verified_exact"',
                'phase_discovery_status = "not_applicable_homogeneous_single_phase"',
            )
        ),
    )

    matches = check_text_gates.scan_text_file(
        source,
        relative_path="scripts/validation/status_report.py",
    )

    assert matches == []


def test_scan_text_file_reports_exact_placeholder_with_location_and_token(tmp_path: Path) -> None:
    blocked_placeholder = "not" + "_applicable"
    source = _write_source(
        tmp_path / "solver.py",
        f'optimizer_backend = "ipopt"\nstatus = "{blocked_placeholder}"\n',
    )

    matches = check_text_gates.scan_text_file(
        source,
        relative_path="scripts/validation/solver.py",
    )

    assert len(matches) == 1
    assert matches[0].relative_path == "scripts/validation/solver.py"
    assert matches[0].line_number == 2
    assert matches[0].term == blocked_placeholder
    assert matches[0].render() == (
        f"scripts/validation/solver.py:2: blocked solver/derivative gate term {blocked_placeholder!r}"
    )


def test_scan_text_file_rejects_banned_phrase_only_at_semantic_boundaries(tmp_path: Path) -> None:
    blocked_phrase = "finite" + "_difference"
    source = _write_source(
        tmp_path / "derivatives.py",
        "\n".join(
            (
                f"prefixed_{blocked_phrase}_diagnostic = True",
                f'method = "{blocked_phrase}"',
            )
        ),
    )

    matches = check_text_gates.scan_text_file(
        source,
        relative_path="scripts/validation/derivatives.py",
    )

    assert [(match.line_number, match.term) for match in matches] == [(2, blocked_phrase)]
