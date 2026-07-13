from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
ISSUE_ROOT = REPO_ROOT / "docs" / "superpowers" / "issues"

NOTICE_A = (
    "**Source-faithful historical classification (2026-07-12):** Preserve this "
    "closed issue as component history only. Stage 1 doctrine supersedes any "
    "classification of sampled-candidate replay as a completed Pereira Stage II "
    "upper/lower loop or of current-route/local residual refinement as canonical "
    "Stage III. The retained work does not establish Pereira HELD parity, global "
    "phase-set completeness, or public route admission."
)
NOTICE_B = (
    "**Source-faithful historical classification (2026-07-12):** Preserve the "
    "exact association, local-equilibrium, or source-fixture evidence as internal "
    "component evidence only. It does not establish Pereira HELD parity, globally "
    "complete neutral or associating phase discovery, or public LLE admission. "
    "Literature and model reproduction belong to M6; runtime exposure remains "
    "governed by the native activation descriptor."
)
NOTICE_D = (
    "**Source-faithful historical classification (2026-07-12):** Preserve "
    "sampled-candidate, boundary-trace, exact local-refinement, and postsolve "
    "evidence as internal component evidence only. The former generalized "
    "phase-set and public multiphase admission claim is superseded because no "
    "global phase-set proof exists. Public multiphase remains closed pending #460."
)
NOTICE_E = (
    "**Source-faithful historical classification (2026-07-12):** Preserve this "
    "closed issue as component history only. Perdomo HELD2 requires modified-mole "
    "coordinates and direct total-free-energy Stage III; Ascani counterion-pair "
    "and mean-ionic work is a separate algorithm family. Existing receipts do not "
    "establish source-faithful Perdomo HELD2 parity or public `electrolyte_lle` "
    "admission, which remains closed pending #459."
)
NOTICE_F = (
    "**Source-faithful historical classification (2026-07-12):** The former "
    "public electrolyte GFPE admission is superseded. Preserve route-orchestration, "
    "local-solve, and postsolve receipts as internal evidence only; they do not "
    "establish source-faithful Perdomo HELD2 or current public exposure. "
    "`electrolyte_lle` remains closed pending #459; literature/model reproduction "
    "belongs to M6."
)
NOTICE_G = (
    "**Source-faithful historical classification (2026-07-12):** Preserve the "
    "Perdomo/Figiel Table 4 result as internal validation evidence only. It does "
    "not prove the complete Perdomo controller or current public `electrolyte_lle` "
    "admission; the route remains closed pending #459, and model-reproduction "
    "maturity is M6-owned."
)

EXPECTED_NOTICE_BY_ISSUE = {
    145: NOTICE_B,
    189: NOTICE_D,
    190: NOTICE_B,
    191: NOTICE_E,
    241: NOTICE_A,
    263: NOTICE_A,
    264: NOTICE_D,
    306: NOTICE_E,
    312: NOTICE_E,
    314: NOTICE_F,
    320: NOTICE_G,
    343: NOTICE_E,
    346: NOTICE_E,
    347: NOTICE_E,
    348: NOTICE_E,
    349: NOTICE_E,
    350: NOTICE_E,
    365: NOTICE_A,
}


def _mirror_by_issue() -> dict[int, tuple[Path, str]]:
    mirrors: dict[int, tuple[Path, str]] = {}
    for path in ISSUE_ROOT.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^issue: (\d+)$", text, re.MULTILINE)
        if match is not None:
            mirrors[int(match.group(1))] = (path, text)
    return mirrors


def test_superseded_equilibrium_issue_mirrors_have_exact_classification() -> None:
    mirrors = _mirror_by_issue()

    assert set(EXPECTED_NOTICE_BY_ISSUE) <= set(mirrors)
    for issue, notice in EXPECTED_NOTICE_BY_ISSUE.items():
        path, text = mirrors[issue]
        frontmatter_text, body = text.split("---", maxsplit=2)[1:]
        frontmatter = yaml.safe_load(frontmatter_text)

        assert frontmatter["state"] == "closed", path
        assert frontmatter["readiness"] == "closed", path
        assert str(frontmatter["last_synced"]) == "2026-07-12", path
        assert body.lstrip().startswith(notice), path
        assert text.count("Source-faithful historical classification (2026-07-12)") == 1, path
