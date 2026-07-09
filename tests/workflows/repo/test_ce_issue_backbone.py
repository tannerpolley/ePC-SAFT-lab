from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts import validate_issue_mirror

REPO_ROOT = Path(__file__).resolve().parents[3]
ISSUE_DIR = REPO_ROOT / "docs" / "superpowers" / "issues"
SOURCE_PLAN = "docs/superpowers/plans/2026-06-26-m4-equilibrium-standalone-chemical-equilibrium-before-cpe-plan.md"
ISSUE_MIRROR_VALIDATOR = REPO_ROOT / "scripts" / "validate_issue_mirror.py"
CURRENT_PLAN_VALIDATORS = (
    "scripts/validate_plan_task_use_cases.py",
    "scripts/validate_plan_outcome_proof.py",
)
RETIRED_PLAN_VALIDATORS = (
    "validate-plan-task-use-cases.ps1",
    "validate-plan-outcome-proof.ps1",
)
RETIRED_VALIDATORS = (*RETIRED_PLAN_VALIDATORS, "validate-issue-mirror.ps1")

CE_BACKBONE_ISSUES = {
    321: "M4 CE: standalone chemical/speciation equilibrium foundation before CPE",
    322: "M4 CE: write CE/CPE boundary doctrine and registry update",
    323: "M4 CE: define reaction-set schema and conservation-basis compiler",
    324: "M4 CE: define standard-state and equilibrium-constant registry",
    325: "M4 CE: build homogeneous CE residual and constrained objective core",
    326: "M4 CE: add single CE NLP activation path",
    327: "M4 CE: create Cantera and Pope reference-oracle harness",
    328: "M4 CE: design standalone speciation public API and result schema",
    329: "M4 CE: build standalone validation ladder",
    330: "M4 CE: activate standalone CE only after gates pass",
    331: "M4 CPE: define simultaneous phase-plus-chemistry interface contract",
}


def _mirror_paths(issue_number: int) -> list[Path]:
    return sorted(ISSUE_DIR.glob(f"*-issue-{issue_number:04d}-*.md"))


def _mirror_text(issue_number: int) -> str:
    matches = _mirror_paths(issue_number)
    rel_matches = [path.relative_to(REPO_ROOT).as_posix() for path in matches]
    assert len(matches) == 1, f"expected one mirror for #{issue_number}, found {rel_matches}"
    return matches[0].read_text(encoding="utf-8")


def test_ce_boundary_tracking_set_has_one_local_mirror_per_published_issue() -> None:
    missing = []
    duplicates: dict[str, list[str]] = {}

    for issue_number, title in CE_BACKBONE_ISSUES.items():
        matches = _mirror_paths(issue_number)
        if not matches:
            missing.append(f"#{issue_number} {title}")
        elif len(matches) > 1:
            duplicates[f"#{issue_number}"] = [path.relative_to(REPO_ROOT).as_posix() for path in matches]

    assert missing == []
    assert duplicates == {}


def test_ce_boundary_tracking_mirrors_link_plan_and_github_issues() -> None:
    for issue_number, title in CE_BACKBONE_ISSUES.items():
        text = _mirror_text(issue_number)

        assert f"\n# {title}\n" in text
        assert f"**GitHub Issue:** https://github.com/ePC-SAFT/ePC-SAFT/issues/{issue_number}" in text
        assert f"**Source Plan:** {SOURCE_PLAN}" in text
        assert "**GitHub Milestone:** M4 - Equilibrium" in text
        assert "area:equilibrium" in text
        assert "backend:ipopt" in text


def test_cpe_boundary_issue_stays_blocked_by_ce_activation_gate() -> None:
    ce_activation = _mirror_text(330)
    cpe_contract = _mirror_text(331)

    assert "**Classification:** HITL" in ce_activation
    assert "status:blocked" in ce_activation
    assert "https://github.com/ePC-SAFT/ePC-SAFT/issues/329" in ce_activation

    assert "**Classification:** HITL" in cpe_contract
    assert "status:blocked" in cpe_contract
    assert "https://github.com/ePC-SAFT/ePC-SAFT/issues/330" in cpe_contract


def test_repo_issue_mirror_validator_accepts_ce_backbone_mirrors() -> None:
    assert ISSUE_MIRROR_VALIDATOR.is_file(), f"missing validator: {ISSUE_MIRROR_VALIDATOR.relative_to(REPO_ROOT)}"

    for issue_number in CE_BACKBONE_ISSUES:
        mirror = _mirror_paths(issue_number)[0]
        result = subprocess.run(
            [
                sys.executable,
                str(ISSUE_MIRROR_VALIDATOR),
                "--issue-file",
                str(mirror),
                "--milestone-required",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

        assert result.returncode == 0, (
            f"{mirror.relative_to(REPO_ROOT).as_posix()} failed issue mirror validation\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def test_ce_mirrors_use_current_python_plan_validators() -> None:
    for issue_number in CE_BACKBONE_ISSUES:
        text = _mirror_text(issue_number)

        for validator_path in CURRENT_PLAN_VALIDATORS:
            assert validator_path in text
        for retired_name in RETIRED_PLAN_VALIDATORS:
            assert retired_name not in text


def test_retained_issue_mirrors_do_not_call_retired_validators() -> None:
    offenders = {
        path.relative_to(REPO_ROOT).as_posix(): [name for name in RETIRED_VALIDATORS if name in path.read_text(encoding="utf-8")]
        for path in sorted(ISSUE_DIR.glob("*.md"))
        if any(name in path.read_text(encoding="utf-8") for name in RETIRED_VALIDATORS)
    }

    assert offenders == {}


def test_issue_mirror_validator_rejects_retired_plan_validator_names(tmp_path: Path) -> None:
    source = _mirror_paths(321)[0]
    issue_file = tmp_path / "docs" / "superpowers" / "issues" / source.name
    issue_file.parent.mkdir(parents=True)
    text = source.read_text(encoding="utf-8")
    for current_path, retired_name in zip(CURRENT_PLAN_VALIDATORS, RETIRED_PLAN_VALIDATORS, strict=True):
        text = text.replace(current_path, f"scripts/{retired_name}")
    current_validator_prose = ", ".join(CURRENT_PLAN_VALIDATORS)
    text = text.replace(
        "\n## Proof Oracle\n",
        f"\nCurrent validator documentation: {current_validator_prose}\n\n## Proof Oracle\n",
        1,
    )
    issue_file.write_text(text, encoding="utf-8")

    result = validate_issue_mirror.validate(issue_file, tmp_path, milestone_required=True)

    assert result["ok"] is False
    assert result["errors"] == [
        "Proof Oracle must include validate_plan_task_use_cases.py",
        "Proof Oracle must include validate_plan_outcome_proof.py",
    ]
