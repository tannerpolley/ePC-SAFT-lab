# Gross 2002 Full Replication Checker And Scoring Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the #279 foundation for Gross/Sadowski 2002 full figure replication: a strict checker, full-replication manifest contract, score/source metadata schemas, and readiness docs without implementing figure-specific model curves.

**Architecture:** Add a new sibling checker, `scripts/validation/check_gross_2002_full_replication.py`, so the #275 association-acceptance checker remains evidence-scoped and unchanged. The new checker has a foundation gate for #279 and a final complete gate for #286; the manifest records all Figure 1-10 contracts, while figure-family issues later fill the source/model/plot artifacts and raise records from planned to accepted.

**Tech Stack:** Python stdlib JSON/CSV/pathlib/argparse, existing validation checker patterns, pytest through `run_pytest.py`, Sphinx docs validation, GitHub issue mirror metadata, and the repo cleanup hook.

---

## Intake

- Source spec: `docs/superpowers/specs/2026-06-19-m4-equilibrium-gross-2002-full-figure-replication.md`
- Issue mirror: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0279-add-gross-2002-full-replication-checker-and-scoring-schema.md`
- GitHub issue: `https://github.com/ePC-SAFT/ePC-SAFT/issues/279`
- Milestone: `M4 - Equilibrium`
- Package owner: `packages/epcsaft-equilibrium`
- Validation root: `analyses/paper_validation/2002_gross`
- Auto Mode authorization: `.superpowers/runs/2026-06-19-gross-2002-full-figure-replication/auto-mode-authorization.json`

## Planning Decisions

- Use a sibling checker instead of extending `check_gross_2002_association_acceptance.py`, preserving #275 behavior.
- Add a #279 foundation mode: `--require-foundation` must pass when the manifest, artifact contract, source metadata schema, score schema, and planned Figure 1-10 records are valid.
- Keep `--require-complete` as the final campaign gate for #286. During #279 it should return exit code `2` with named figure blockers because the figure-specific model/source artifacts are intentionally not present yet.
- Correct the #279 proof oracle in the issue mirror and GitHub body to use the foundation gate plus an expected blocked readout from the complete gate.
- Do not add broad public capability claims, electrolyte admission, reactive admission, or generalized associating phase-set admission.

## Test Complete And Metrics

Test-complete for #279 means:

- New red tests fail before `scripts/validation/check_gross_2002_full_replication.py` exists.
- The new checker passes `--require-foundation` against the committed full-replication manifest.
- The same checker reports named blockers, not a clean pass, under `--require-complete` until #280-#285 provide accepted figure artifacts.
- Existing #275 acceptance behavior still passes its checker tests.
- Docs validation and cleanup hook pass.

Numerical metrics are required by the schema even though #279 does not compute real figure scores yet:

- Pure-component `T-rho` replication gate: normalized score `>= 7.0`, vapor and liquid branch coverage required.
- VLE replication gate: normalized score `>= 7.0` for each required series.
- LLE/VLLE phase-boundary gate: normalized score `>= 6.5` for each required branch and derivative status `verified_exact` when the accepted route is associating.
- Diagnostic-only evidence: normalized score cap `<= 4.0` and cannot satisfy full replication.
- Source metadata must record axis calibration, units, series labels, provenance, digitization uncertainty, and QA overlay path before a figure can be accepted.

## Acceptance Coverage

- Strict full-replication checker entry point: Tasks 1-2.
- Red contract tests for missing source CSV, metadata, QA overlay, model curve, plot, sidecar, score JSON, and derivative receipts: Task 1.
- Full-replication manifest for Figures 1-10: Task 3.
- Score JSON fields and source metadata fields: Tasks 2-3.
- Keep #275 checker behavior intact: Task 4.
- Update M4 docs and #279 mirror to distinguish #275 acceptance from full paper replication: Task 5.

## Non-Goals

- No figure-specific source digitization, model curve generation, or rendered paper-scale plot implementation.
- No public electrolyte, reactive, CE, CPE, or generalized phase-count admission.
- No broad associating-family capability claim.
- No changes to provider thermodynamic kernels or equilibrium route admission.

## File Map

- Create: `scripts/validation/check_gross_2002_full_replication.py`
- Create: `tests/native/contracts/test_gross_2002_full_replication_checker.py`
- Create: `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`
- Modify: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0279-add-gross-2002-full-replication-checker-and-scoring-schema.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`

### Task 1: Add Red Contract Tests For The Full-Replication Checker

**Use Cases:**
- A worker marks a figure accepted without a source CSV; the checker reports `gross_2002_figure_NN_source_csv_missing`.
- A digitized figure lacks calibration metadata or QA overlay; the checker reports the exact missing artifact.
- A future figure issue supplies score JSON below the family threshold; the checker blocks acceptance with the normalized score blocker.
- #279 foundation work can pass without real model curves while the final #286 complete gate remains blocked.

**Files:**
- Create: `tests/native/contracts/test_gross_2002_full_replication_checker.py`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [ ] **Step 1: Create the failing import and helper fixtures**

  Add the test file with this starting structure:

  ```python
  from __future__ import annotations

  import json
  from pathlib import Path

  from scripts.validation import check_gross_2002_full_replication as checker


  def _write(path: Path, text: str = "artifact\n") -> str:
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(text, encoding="utf-8")
      return str(path)


  def _artifact_set(tmp_path: Path, figure_id: str, *, score: float = 8.0) -> dict[str, str]:
      source_csv = _write(tmp_path / figure_id / "source.csv", "x,y\n0.1,1.0\n")
      metadata_json = _write(
          tmp_path / figure_id / "metadata.json",
          json.dumps(
              {
                  "provenance": "unit-test digitization",
                  "axis_calibration": {"x": "composition", "y": "temperature_K"},
                  "units": {"x": "mole_fraction", "y": "K"},
                  "series_labels": ["liquid"],
                  "digitization_uncertainty": {"x": 0.002, "y": 0.2},
                  "qa_overlay": str(tmp_path / figure_id / "qa_overlay.png"),
              }
          )
          + "\n",
      )
      qa_overlay = _write(tmp_path / figure_id / "qa_overlay.png")
      model_csv = _write(tmp_path / figure_id / "model.csv", "x,y\n0.1,1.1\n")
      plotted_csv = _write(tmp_path / figure_id / "plotted.csv", "x_source,y_source,x_model,y_model\n0.1,1.0,0.1,1.1\n")
      score_json = _write(
          tmp_path / figure_id / "score.json",
          json.dumps(
              {
                  "source_point_count": 1,
                  "model_point_count": 1,
                  "rmse_axis": {"x": 0.0, "y": 0.1},
                  "max_axis_error": {"x": 0.0, "y": 0.1},
                  "normalized_plot_score": score,
                  "branch_coverage_score": 1.0,
                  "derivative_status": "verified_exact",
                  "pass": score >= 7.0,
              }
          )
          + "\n",
      )
      summary_json = _write(tmp_path / figure_id / "summary.json", "{}\n")
      png = _write(tmp_path / figure_id / "plot.png")
      svg = _write(tmp_path / figure_id / "plot.svg")
      sidecar = _write(tmp_path / figure_id / "plot.mpl.yaml", "kind: matplotlib-figure\n")
      return {
          "source_csv": source_csv,
          "source_metadata_json": metadata_json,
          "digitization_qa_overlay": qa_overlay,
          "model_csv": model_csv,
          "plotted_csv": plotted_csv,
          "score_json": score_json,
          "summary_json": summary_json,
          "png": png,
          "svg": svg,
          "sidecar": sidecar,
      }
  ```

- [ ] **Step 2: Add the foundation-mode test**

  Add a test proving the #279 mode accepts planned records:

  ```python
  def test_foundation_payload_accepts_planned_all_figures() -> None:
      payload = {
          "campaign": "gross_2002_full_replication",
          "artifact_contract": {"required_artifacts": list(checker.REQUIRED_ACCEPTED_ARTIFACT_KEYS)},
          "source_metadata_schema": {"required_fields": list(checker.REQUIRED_SOURCE_METADATA_FIELDS)},
          "score_schema": {"required_fields": list(checker.REQUIRED_SCORE_FIELDS)},
          "figures": [
              {
                  "figure_id": f"figure_{number:02d}",
                  "plot_family": "vle" if number not in (1, 8, 10) else "phase_boundary",
                  "replication_status": "planned",
                  "counts_toward_completion": False,
                  "acceptance_threshold": 7.0,
              }
              for number in range(1, 11)
          ],
          "blockers": [],
      }

      result = checker.evaluate_payload(payload, require_foundation=True)

      assert result["foundation_complete"] is True
      assert result["complete"] is False
      assert result["planned_figures"] == [f"figure_{number:02d}" for number in range(1, 11)]
      assert result["blockers"] == []
  ```

- [ ] **Step 3: Add missing-artifact and score-gate tests**

  Add tests for accepted records:

  ```python
  def test_accepted_figure_requires_all_replication_artifacts(tmp_path: Path) -> None:
      artifacts = _artifact_set(tmp_path, "figure_08")
      artifacts.pop("source_metadata_json")
      payload = {
          "campaign": "gross_2002_full_replication",
          "artifact_contract": {"required_artifacts": list(checker.REQUIRED_ACCEPTED_ARTIFACT_KEYS)},
          "source_metadata_schema": {"required_fields": list(checker.REQUIRED_SOURCE_METADATA_FIELDS)},
          "score_schema": {"required_fields": list(checker.REQUIRED_SCORE_FIELDS)},
          "figures": [
              {
                  "figure_id": "figure_08",
                  "plot_family": "phase_boundary",
                  "replication_status": "accepted",
                  "counts_toward_completion": True,
                  "acceptance_threshold": 6.5,
                  "artifacts": artifacts,
                  "derivative_status": "verified_exact",
              }
          ],
          "blockers": [],
      }

      result = checker.evaluate_payload(payload, require_complete=True)

      assert result["complete"] is False
      assert "gross_2002_figure_08_source_metadata_json_missing" in result["blockers"]


  def test_low_score_blocks_accepted_figure(tmp_path: Path) -> None:
      artifacts = _artifact_set(tmp_path, "figure_02", score=5.0)
      payload = {
          "campaign": "gross_2002_full_replication",
          "artifact_contract": {"required_artifacts": list(checker.REQUIRED_ACCEPTED_ARTIFACT_KEYS)},
          "source_metadata_schema": {"required_fields": list(checker.REQUIRED_SOURCE_METADATA_FIELDS)},
          "score_schema": {"required_fields": list(checker.REQUIRED_SCORE_FIELDS)},
          "figures": [
              {
                  "figure_id": "figure_02",
                  "plot_family": "vle",
                  "replication_status": "accepted",
                  "counts_toward_completion": True,
                  "acceptance_threshold": 7.0,
                  "artifacts": artifacts,
                  "derivative_status": "not_required",
              }
          ],
          "blockers": [],
      }

      result = checker.evaluate_payload(payload, require_complete=True)

      assert result["complete"] is False
      assert "gross_2002_figure_02_score_below_threshold" in result["blockers"]
  ```

- [ ] **Step 4: Add CLI tests for #279 and #286 modes**

  Add CLI tests:

  ```python
  def test_cli_foundation_passes_committed_manifest(capsys) -> None:
      exit_code = checker.main(["--json", "--require-foundation"])

      payload = json.loads(capsys.readouterr().out)
      assert exit_code == 0
      assert payload["foundation_complete"] is True
      assert payload["complete"] is False


  def test_cli_require_complete_reports_planned_figure_blockers(capsys) -> None:
      exit_code = checker.main(["--json", "--require-complete"])

      payload = json.loads(capsys.readouterr().out)
      assert exit_code == 2
      assert "gross_2002_figure_01_full_replication_missing" in payload["blockers"]
      assert "gross_2002_figure_10_full_replication_missing" in payload["blockers"]
  ```

- [ ] **Step 5: Run the new tests and verify the expected failure**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

  Expected before implementation: import failure for `scripts.validation.check_gross_2002_full_replication`.

- [ ] **Step 6: Commit checkpoint after the red tests**

  Commit after the red test file is present:

  ```powershell
  git add tests/native/contracts/test_gross_2002_full_replication_checker.py
  git commit -m "Add Gross 2002 full replication checker contract tests"
  ```

### Task 2: Implement The Full-Replication Checker Entry Point

**Use Cases:**
- #279 needs a checker command that passes foundation readiness without requiring figure-specific artifacts.
- #286 needs the same checker to fail under `--require-complete` until all Figure 1-10 records are accepted.
- Accepted associating figures need exact derivative status in their score records before they can count.
- The checker must emit stable JSON for issue automation and retained evidence summaries.

**Files:**
- Create: `scripts/validation/check_gross_2002_full_replication.py`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [ ] **Step 1: Create constants and repo helpers**

  Create `scripts/validation/check_gross_2002_full_replication.py` with constants:

  ```python
  REQUIRED_FIGURES = tuple(f"figure_{number:02d}" for number in range(1, 11))
  REQUIRED_ACCEPTED_ARTIFACT_KEYS = (
      "source_csv",
      "source_metadata_json",
      "digitization_qa_overlay",
      "model_csv",
      "plotted_csv",
      "score_json",
      "summary_json",
      "png",
      "svg",
      "sidecar",
  )
  REQUIRED_SOURCE_METADATA_FIELDS = (
      "provenance",
      "axis_calibration",
      "units",
      "series_labels",
      "digitization_uncertainty",
      "qa_overlay",
  )
  REQUIRED_SCORE_FIELDS = (
      "source_point_count",
      "model_point_count",
      "rmse_axis",
      "max_axis_error",
      "normalized_plot_score",
      "branch_coverage_score",
      "derivative_status",
      "pass",
  )
  PLOT_FAMILY_THRESHOLDS = {"t_rho": 7.0, "vle": 7.0, "phase_boundary": 6.5}
  DIAGNOSTIC_SCORE_CAP = 4.0
  ```

  Also add `_jsonable`, `_repo_path`, `_relative`, `_read_json`, and `_path_exists` using the same style as `check_gross_2002_association_acceptance.py`.

- [ ] **Step 2: Implement score and metadata validation**

  Add:

  ```python
  def _score_payload(path_value: str) -> dict[str, Any]:
      path = _repo_path(path_value)
      if not path.is_file():
          return {}
      return _read_json(path)


  def _metadata_payload(path_value: str) -> dict[str, Any]:
      path = _repo_path(path_value)
      if not path.is_file():
          return {}
      return _read_json(path)


  def _accepted_record_blockers(record: dict[str, Any]) -> list[str]:
      figure_id = str(record.get("figure_id", "unknown"))
      blockers: list[str] = []
      artifacts = record.get("artifacts", {})
      if not isinstance(artifacts, dict):
          return [f"gross_2002_{figure_id}_artifacts_missing"]
      for key in REQUIRED_ACCEPTED_ARTIFACT_KEYS:
          if not _path_exists(artifacts.get(key, "")):
              blockers.append(f"gross_2002_{figure_id}_{key}_missing")
      metadata = _metadata_payload(str(artifacts.get("source_metadata_json", "")))
      for field in REQUIRED_SOURCE_METADATA_FIELDS:
          if field not in metadata:
              blockers.append(f"gross_2002_{figure_id}_source_metadata_{field}_missing")
      score = _score_payload(str(artifacts.get("score_json", "")))
      for field in REQUIRED_SCORE_FIELDS:
          if field not in score:
              blockers.append(f"gross_2002_{figure_id}_score_{field}_missing")
      threshold = float(record.get("acceptance_threshold", PLOT_FAMILY_THRESHOLDS.get(str(record.get("plot_family", "")), 7.0)))
      normalized_score = float(score.get("normalized_plot_score", -1.0) or -1.0)
      if normalized_score < threshold or score.get("pass") is not True:
          blockers.append(f"gross_2002_{figure_id}_score_below_threshold")
      if record.get("requires_exact_association_hessian") and score.get("derivative_status") != "verified_exact":
          blockers.append(f"gross_2002_{figure_id}_exact_association_hessian_missing")
      return blockers
  ```

- [ ] **Step 3: Implement `evaluate_payload` with separate foundation and complete gates**

  Add `evaluate_payload(payload, require_foundation=False, require_complete=False, require_exact_association_hessian=False, require_fresh_native=False)`.

  Required behavior:

  - `foundation_complete` is true when the manifest has all ten figure IDs, a required artifact contract, source metadata schema, score schema, and thresholds for `t_rho`, `vle`, and `phase_boundary`.
  - `complete` is true only when all ten required figures count toward completion, have `replication_status == "accepted"`, and have no blockers.
  - Planned records are accepted for foundation mode but report `gross_2002_figure_NN_full_replication_missing` under `--require-complete`.
  - Figure 2 remains blocked under `--require-complete` until its source identity is resolved by a later issue.

- [ ] **Step 4: Implement manifest loading, summary writing, and CLI**

  Add:

  - `MANIFEST_PATH = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared" / "gross_2002_full_replication_manifest.json"`
  - `SUMMARY_DIR = REPO_ROOT / "analyses" / "paper_validation" / "2002_gross" / "shared" / "results"`
  - `evaluate_campaign(...)`
  - `_write_campaign_summary(...)`
  - `main(argv=None)`

  CLI flags:

  ```text
  --manifest
  --json
  --require-foundation
  --require-complete
  --require-exact-association-hessian
  --require-fresh-native
  --write-summary
  ```

  Exit codes:

  - `0` when the requested gate passes.
  - `2` when the requested gate is blocked with named blockers.

- [ ] **Step 5: Run the checker tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

  Expected after implementation and before Task 3: tests that need the committed manifest still fail with `gross_2002_full_replication_manifest_missing`.

- [ ] **Step 6: Commit checkpoint after checker implementation**

  Commit:

  ```powershell
  git add scripts/validation/check_gross_2002_full_replication.py
  git commit -m "Add Gross 2002 full replication checker"
  ```

### Task 3: Add The Full-Replication Manifest And Schema Contract

**Use Cases:**
- Figure-specific issues need one manifest location that defines required artifacts, thresholds, source metadata, and score fields.
- #279 must represent every Gross 2002 figure without granting completion credit before source/model evidence exists.
- The checker must be able to produce a retained foundation summary from committed metadata.
- Future workers must know which coordinate family and threshold applies to each figure.

**Files:**
- Create: `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`

- [ ] **Step 1: Create the manifest shell**

  Create `analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json` with:

  ```json
  {
    "campaign": "gross_2002_full_replication",
    "source_paper": "Gross and Sadowski 2002",
    "source_markdown": "analyses/paper_validation/2002_gross/docs/md/source_01_gross_2002.md",
    "source_pdf": "analyses/paper_validation/2002_gross/docs/pdf/source_01_gross_2002.pdf",
    "association_acceptance_manifest": "analyses/paper_validation/2002_gross/shared/gross_2002_association_acceptance_manifest.json",
    "artifact_contract": {
      "required_artifacts": [
        "source_csv",
        "source_metadata_json",
        "digitization_qa_overlay",
        "model_csv",
        "plotted_csv",
        "score_json",
        "summary_json",
        "png",
        "svg",
        "sidecar"
      ]
    },
    "source_metadata_schema": {
      "required_fields": [
        "provenance",
        "axis_calibration",
        "units",
        "series_labels",
        "digitization_uncertainty",
        "qa_overlay"
      ]
    },
    "score_schema": {
      "required_fields": [
        "source_point_count",
        "model_point_count",
        "rmse_axis",
        "max_axis_error",
        "normalized_plot_score",
        "branch_coverage_score",
        "derivative_status",
        "pass"
      ],
      "thresholds": {
        "t_rho": 7.0,
        "vle": 7.0,
        "phase_boundary": 6.5,
        "diagnostic_score_cap": 4.0
      }
    },
    "summary_artifacts": {
      "json": "analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json",
      "csv": "analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv"
    },
    "figures": []
  }
  ```

- [ ] **Step 2: Fill Figure 1-10 records**

  Add one record per figure. Each record must include:

  ```json
  {
    "figure_id": "figure_01",
    "paper_plot_type": "T-rho saturated vapor/liquid densities",
    "system": "methanol, 1-pentanol, 1-nonanol",
    "plot_family": "t_rho",
    "replication_status": "planned",
    "counts_toward_completion": false,
    "acceptance_threshold": 7.0,
    "requires_exact_association_hessian": false,
    "source_image": "analyses/paper_validation/2002_gross/figures/figure_01/source/paper_source_01_gross_2002_figure_001.png",
    "planned_artifact_stem": "gross_2002_figure_01_replication",
    "remaining_work": [
      "retain source or digitized coexisting density data",
      "generate model vapor and liquid density curves",
      "score vapor and liquid branch agreement"
    ]
  }
  ```

  Use the source spec Figure Replication Matrix for the `paper_plot_type`, `system`, `plot_family`, `requires_exact_association_hessian`, and `remaining_work` values. Figures 8, 9, and 10 must set `requires_exact_association_hessian` to true for accepted associating route evidence.

- [ ] **Step 3: Run foundation and complete gates**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-foundation
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete
  ```

  Expected:

  - `--require-foundation` exits `0`.
  - `--require-complete` exits `2` and reports `gross_2002_figure_01_full_replication_missing` through `gross_2002_figure_10_full_replication_missing`.

- [ ] **Step 4: Run the full-replication checker tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py -q
  ```

  Expected: all tests in the new file pass.

- [ ] **Step 5: Write retained foundation summary**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-foundation --write-summary
  ```

  Expected files:

  - `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json`
  - `analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv`

- [ ] **Step 6: Commit checkpoint after manifest and summary artifacts**

  Commit:

  ```powershell
  git add analyses/paper_validation/2002_gross/shared/gross_2002_full_replication_manifest.json analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv tests/native/contracts/test_gross_2002_full_replication_checker.py
  git commit -m "Add Gross 2002 full replication manifest contract"
  ```

### Task 4: Preserve The Existing Association-Acceptance Gate

**Use Cases:**
- #275 remains a narrower association-confidence receipt and must not silently become the full-campaign proof.
- Existing Figure 1/8/10 acceptance artifacts still validate under the old checker.
- Figure 2-7 and 9 source-requirement records keep no completion credit in the old checker.
- The new checker can coexist with the old checker in a single validation command.

**Files:**
- Modify: `tests/native/contracts/test_gross_2002_association_acceptance_checker.py` only if a regression assertion is needed.
- Test: `tests/native/contracts/test_gross_2002_association_acceptance_checker.py`

- [ ] **Step 1: Run existing #275 checker tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py -q
  ```

  Expected: existing tests pass without edits.

- [ ] **Step 2: Add one coexistence assertion only if the old tests do not cover source-requirement non-credit**

  If needed, add this assertion to `test_evaluate_payload_accepts_completed_campaign`:

  ```python
  assert result["source_requirement_figures"] == [
      "figure_02",
      "figure_03",
      "figure_04",
      "figure_05",
      "figure_06",
      "figure_07",
      "figure_09",
  ]
  ```

  If the assertion already exists, leave the file unchanged.

- [ ] **Step 3: Run both checker test files together**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py -q
  ```

  Expected: both test files pass.

- [ ] **Step 4: Run both checker commands**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-foundation
  uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  ```

  Expected: both commands exit `0`.

- [ ] **Step 5: Commit checkpoint if Task 4 changed tests**

  Commit only if the test file changed:

  ```powershell
  git add tests/native/contracts/test_gross_2002_association_acceptance_checker.py
  git commit -m "Guard Gross 2002 acceptance checker scope"
  ```

### Task 5: Update Docs, Issue Mirror, And Proof Oracle

**Use Cases:**
- A future worker reading #279 sees the correct foundation proof command rather than the final #286 complete-campaign command as a required pass.
- M4 README distinguishes #275 acceptance evidence, #279 foundation readiness, and #286 full figure replication.
- The local mirror links to this plan so `resolve-issue 279` starts from a concrete implementation path.
- GitHub issue body stays aligned with the local mirror after the plan correction.

**Files:**
- Modify: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0279-add-gross-2002-full-replication-checker-and-scoring-schema.md`
- Modify: `docs/superpowers/milestones/M4-equilibrium/README.md`
- Test: `docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0279-add-gross-2002-full-replication-checker-and-scoring-schema.md`

- [ ] **Step 1: Link the source plan in #279 mirror**

  Change frontmatter:

  ```yaml
  source_plan: "docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0279-gross-2002-full-replication-checker-scoring-schema-plan.md"
  ```

  Change body:

  ```markdown
  **Source Plan:** docs/superpowers/plans/2026-06-19-m4-equilibrium-issue-0279-gross-2002-full-replication-checker-scoring-schema-plan.md
  ```

- [ ] **Step 2: Correct #279 proof oracle**

  Replace the current complete-only command with:

  ```markdown
  - uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-foundation
  - uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete
    - Expected for #279 closeout: exits 2 with named full-replication blockers for planned figure records; this is the #286 final gate, not a #279 pass gate.
  ```

- [ ] **Step 3: Update M4 README retained evidence**

  Add a retained-evidence row for the new foundation checker after the #275 row:

  ```markdown
  | `scripts/validation/check_gross_2002_full_replication.py --json --require-foundation` | `association` | Gross/Sadowski 2002 full-replication foundation for #279: validates the Figure 1-10 manifest, required source/digitization artifacts, score schema, source metadata schema, and planned blocker readout. This is not full figure replication until #280-#286 close. |
  ```

- [ ] **Step 4: Validate issue mirror and docs**

  Run:

  ```powershell
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\Tanner\.codex\plugins\cache\tanner-local\project\0.2.0+codex.20260604172859\skills\create-issues\scripts\validate-issue-mirror.ps1 -RepoRoot . -IssueFile docs\superpowers\issues\2026-06-19-m4-equilibrium-issue-0279-add-gross-2002-full-replication-checker-and-scoring-schema.md -MilestoneRequired
  uv run --no-sync python scripts/dev/validate_project.py docs
  ```

  Expected: issue mirror validator passes and docs build succeeds.

- [ ] **Step 5: Sync GitHub issue body**

  After local validation, update the GitHub body from the corrected local mirror content:

  ```powershell
  $path = 'docs\superpowers\issues\2026-06-19-m4-equilibrium-issue-0279-add-gross-2002-full-replication-checker-and-scoring-schema.md'
  $text = Get-Content -LiteralPath $path -Raw
  $body = [regex]::Replace($text, '(?s)^---\r?\n.*?\r?\n---\r?\n', '', 1)
  $body | gh issue edit 279 --repo ePC-SAFT/ePC-SAFT --body-file -
  ```

- [ ] **Step 6: Commit checkpoint after docs and mirror updates**

  Commit:

  ```powershell
  git add docs/superpowers/issues/2026-06-19-m4-equilibrium-issue-0279-add-gross-2002-full-replication-checker-and-scoring-schema.md docs/superpowers/milestones/M4-equilibrium/README.md
  git commit -m "Document Gross 2002 full replication foundation gate"
  ```

### Task 6: Final Verification And Closeout

**Use Cases:**
- The #279 PR proves the foundation gate, not the full figure campaign.
- The next figure-family issues remain blocked until #279 merges.
- The final handoff has exact commands and explains why `--require-complete` is still blocked.
- The repo is clean after validation.

**Files:**
- Test: `scripts/validation/check_gross_2002_full_replication.py`
- Test: `scripts/validation/check_gross_2002_association_acceptance.py`
- Test: `tests/native/contracts/test_gross_2002_full_replication_checker.py`
- Test: `tests/native/contracts/test_gross_2002_association_acceptance_checker.py`

- [ ] **Step 1: Run focused tests**

  Run:

  ```powershell
  uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py -q
  ```

  Expected: all selected tests pass.

- [ ] **Step 2: Run foundation and acceptance checkers**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-foundation --write-summary
  uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
  ```

  Expected: both commands exit `0`.

- [ ] **Step 3: Run final complete-gate readout and record blockers**

  Run:

  ```powershell
  uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete
  ```

  Expected for #279: exit `2`; JSON includes named `gross_2002_figure_NN_full_replication_missing` blockers for records still owned by #280-#285. This is a correct #279 closeout result.

- [ ] **Step 4: Run docs validation and cleanup**

  Run:

  ```powershell
  uv run --no-sync python scripts/dev/validate_project.py docs
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  ```

  Expected: docs build succeeds and cleanup reports no matching leftover Codex processes.

- [ ] **Step 5: Review git state**

  Run:

  ```powershell
  git status --short --branch
  git log --oneline -5
  ```

  Expected: only intended #279 branch changes are present before PR publication.

- [ ] **Step 6: Final commit if any verification-only artifact changed**

  Commit retained summary changes if `--write-summary` changed them:

  ```powershell
  git add analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.json analyses/paper_validation/2002_gross/shared/results/gross_2002_full_replication_summary.csv
  git commit -m "Refresh Gross 2002 full replication foundation summary"
  ```

## Proof Oracle

Required pass commands for #279:

```powershell
uv run --no-sync python run_pytest.py tests/native/contracts/test_gross_2002_full_replication_checker.py tests/native/contracts/test_gross_2002_association_acceptance_checker.py -q
uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-foundation --write-summary
uv run --no-sync python scripts/validation/check_gross_2002_association_acceptance.py --json --require-complete --require-exact-association-hessian --require-fresh-native
uv run --no-sync python scripts/dev/validate_project.py docs
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Required blocked readout for #279:

```powershell
uv run --no-sync python scripts/validation/check_gross_2002_full_replication.py --json --require-complete
```

Expected: exit `2` with named figure blockers until #280-#285 land their source/model/plot evidence.

## Risk Notes

- The issue mirror originally listed `--require-complete` as a pass command. This plan corrects that because #279 is the foundation issue; #286 owns final complete-campaign acceptance.
- Figure 2 source identity remains unresolved and must stay blocked under the complete gate until its figure-family issue supplies provenance.
- The checker should not create figure artifacts or grant completion credit from schema-only records.
- Exact association derivative requirements should be evaluated only for accepted associating records, not for planned records.

## Recommended Implementation Route

Use `$superpowers-project:resolve-issue 279` after this plan is committed and the #279 mirror points to it. The issue is AFK-ready once the source plan link, corrected proof oracle, and M4 README row are committed and pushed.
