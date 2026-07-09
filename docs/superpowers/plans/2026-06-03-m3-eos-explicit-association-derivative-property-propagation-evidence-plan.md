# Explicit Association Derivative And Property Propagation Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the Python-only explicit association toybox so exact implicit association and the active explicit Picard candidate are compared on amortized timing, derivative agreement, propagated EOS property proxies, water topology behavior, and local objective sensitivity before any provider implementation decision.

**Architecture:** Keep the work entirely under `analyses/package_validation/explicit_association_toybox` and add figure-owned analysis lanes that reuse the existing exact mass-action baseline, closure evaluators, hard-chain and dispersion scalar helpers, real-system topology metadata, and fixed-state property residual scaffolding. New modules produce retained CSVs, plotted-data CSVs, PNGs, and PDF artifacts with exact implicit timing kept as a first-class baseline column.

**Tech Stack:** Python stdlib, NumPy, PyYAML, Matplotlib, pytest, existing toybox scripts, and optional provider state calls already used by the property-residual lane; no provider runtime change, no equilibrium package change, no regression package change, and no new dependency.

---

## Intake

- Source spec: `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-derivative-property-propagation-evidence.md`
- Related completed issue evidence: GitHub issue `#218`, PR `#219`
- Prior plan context:
  - `docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-follow-up-analysis-roadmap-plan.md`
  - `docs/superpowers/plans/2026-06-03-m3-eos-explicit-association-toybox-hc-dispersion-extension-plan.md`
  - `docs/superpowers/plans/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-plan.md`
- Milestone linkage: `M3 - EOS`
- Package boundary: analysis-only evidence under `analyses/package_validation/explicit_association_toybox/**`
- User planning decisions:
  - Plan slice: one cohesive M3 analysis slice.
  - Evidence thresholds: provisional numeric gates, retained in config and revisable from results.
  - Objective diagnostic: include compact gradient and Hessian-proxy diagnostics.

## Required Development Skills

- Use `superpowers:test-driven-development` for each implementation task.
- Use `chemical-engineer` for association thermodynamics, residual Helmholtz interpretation, and water topology conclusions.
- Use `matplotlib-plotting` for every new or updated figure.
- Use `superpowers:systematic-debugging` if timing evidence is noisy enough to change conclusions.
- Use `superpowers:verification-before-completion` before any worker reports the plan complete.

## Acceptance Criteria

- [ ] Amortized timing output retains exact implicit median elapsed time, exact implicit IQR, exact implicit iteration count, closure median elapsed time, closure IQR, and speedup by topology and site count.
- [ ] Derivative-agreement output compares exact implicit and explicit closures for `a_assoc`, pressure proxy, composition sensitivity, and chemical-potential-like or fugacity-like proxy targets.
- [ ] Asymmetric binary outputs include one associating plus one inert component, two associating components with cross association, unequal `Delta` strength, non-50/50 composition, and at least one water-like 3B/4C contrast row.
- [ ] Total EOS impact output ranks closures by `ares_assoc` error, total `ares` error, pressure proxy error, chemical-potential proxy error, fugacity proxy error, exact implicit timing, closure timing, and evidence band.
- [ ] Water fork output compares assigned `3B` and rigorous-label `4C` topology rows with pressure residual in MPa and `Z` residual, without presenting fixed-state diagnostics as VLE validation.
- [ ] Local objective sensitivity output reports exact and closure objective values, gradient max absolute error, Hessian-proxy max absolute error, exact implicit timing, closure timing, and evidence band.
- [ ] Rows with reduced site information remain diagnostic-only in all new evidence bands unless a row is explicitly marked as a failure-mode diagnostic.
- [ ] Every new or updated figure workflow writes retained CSV, plotted-data CSV, PNG, and PDF files under its figure-owned `output` folder.
- [ ] `analysis.yaml` and `README.md` list the new commands and state that this remains analysis-only toybox evidence.
- [ ] Final implementation reporting renders every new or updated plot inline with absolute filesystem paths and includes compact Markdown tables from retained data.
- [ ] No `packages/epcsaft/**`, `packages/epcsaft-equilibrium/**`, `packages/epcsaft-regression/**`, public API, native SDK, capability contract, or dependency file is changed.

## Non-Goals

- No provider runtime implementation of explicit association closures.
- No public Python API change.
- No equilibrium route implementation, Ipopt work, HELD work, phase discovery, flash, bubble, dew, or LLE work.
- No regression package work.
- No claim that centered perturbation diagnostics are production exact derivatives.
- No source AAD summary values treated as raw validation data.
- No broad gallery folder; keep each figure's generated artifacts inside the figure-owned `output` folder.

## File Map

Create:

- `analyses/package_validation/explicit_association_toybox/config/propagation_evidence.yaml`
- `analyses/package_validation/explicit_association_toybox/config/asymmetric_binary_cases.yaml`
- `analyses/package_validation/explicit_association_toybox/scripts/propagation_evidence.py`
- `analyses/package_validation/explicit_association_toybox/scripts/amortized_timing.py`
- `analyses/package_validation/explicit_association_toybox/scripts/derivative_agreement.py`
- `analyses/package_validation/explicit_association_toybox/scripts/asymmetric_binary_closures.py`
- `analyses/package_validation/explicit_association_toybox/scripts/total_eos_impact.py`
- `analyses/package_validation/explicit_association_toybox/scripts/water_topology_fork.py`
- `analyses/package_validation/explicit_association_toybox/scripts/equilibrium_style_objective_sensitivity.py`
- `analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/generate_data.py`
- `analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/render_figure.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_propagation_evidence.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_amortized_timing.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_derivative_agreement.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_asymmetric_binary_closures.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_total_eos_impact.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_water_topology_fork.py`
- `analyses/package_validation/explicit_association_toybox/tests/test_equilibrium_style_objective_sensitivity.py`

Modify:

- `analyses/package_validation/explicit_association_toybox/README.md`
- `analyses/package_validation/explicit_association_toybox/analysis.yaml`
- `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`

## Evidence Bands

Use `config/propagation_evidence.yaml` as the single analysis-local threshold file:

```yaml
evidence_bands:
  exact_reference:
    max_assoc_ares_rel_error: 1.0e-12
    max_derivative_rel_error: 1.0e-10
    max_property_rel_error: 1.0e-10
  candidate_accuracy:
    max_assoc_ares_rel_error: 2.5e-2
    max_derivative_rel_error: 5.0e-2
    max_property_rel_error: 5.0e-2
    min_speedup_vs_exact_implicit: 2.0
  speed_only_candidate:
    max_assoc_ares_rel_error: 8.0e-2
    min_speedup_vs_exact_implicit: 5.0
  diagnostic_only:
    reason: interpretation_or_failure_mode
  reject_for_provider_path:
    max_mass_action_residual_inf: 1.0e-3
```

The analysis may report stricter conclusions than these gates when retained data justifies it, but every output row must carry the band that these provisional thresholds assign.

## Task 1: Add Shared Propagation Evidence Utilities

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/config/propagation_evidence.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/propagation_evidence.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_propagation_evidence.py`

- [ ] **Step 1: Write the failing threshold loader test**

Add `test_propagation_evidence.py` with assertions that `load_propagation_thresholds()` returns thresholds for `exact_reference`, `candidate_accuracy`, `speed_only_candidate`, `diagnostic_only`, and `reject_for_provider_path`.

```python
from analyses.package_validation.explicit_association_toybox.scripts.propagation_evidence import (
    classify_propagated_evidence_band,
    load_propagation_thresholds,
)


def test_load_propagation_thresholds_has_all_bands() -> None:
    thresholds = load_propagation_thresholds()
    assert {
        "exact_reference",
        "candidate_accuracy",
        "speed_only_candidate",
        "diagnostic_only",
        "reject_for_provider_path",
    } <= set(thresholds)
    assert thresholds["candidate_accuracy"]["max_derivative_rel_error"] == 5.0e-2
```

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_propagation_evidence.py -q
```

Expected result: fail because `propagation_evidence.py` does not exist yet.

- [ ] **Step 2: Add the threshold config**

Create `config/propagation_evidence.yaml` with the exact `evidence_bands` block from this plan. Keep values numeric except `diagnostic_only.reason`.

- [ ] **Step 3: Implement loader and classifier**

Create `propagation_evidence.py` with:

```python
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import numpy as np
import yaml

ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_THRESHOLDS = ANALYSIS_ROOT / "config" / "propagation_evidence.yaml"


def load_propagation_thresholds(path: Path = DEFAULT_THRESHOLDS) -> dict[str, dict[str, float | str]]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping) or not isinstance(data.get("evidence_bands"), Mapping):
        raise ValueError(f"{path} must define an evidence_bands mapping.")
    return {str(key): dict(value) for key, value in data["evidence_bands"].items()}


def classify_propagated_evidence_band(
    *,
    association_model: str,
    assoc_ares_rel_error: float,
    derivative_rel_error: float,
    property_rel_error: float,
    mass_action_residual_inf: float,
    speedup_vs_exact_implicit: float,
    information_loss: str,
    thresholds: Mapping[str, Mapping[str, float | str]],
) -> str:
    reject = thresholds["reject_for_provider_path"]
    if not np.all(np.isfinite([assoc_ares_rel_error, derivative_rel_error, property_rel_error])):
        return "reject_for_provider_path"
    if mass_action_residual_inf > float(reject["max_mass_action_residual_inf"]):
        return "reject_for_provider_path"
    if information_loss != "none":
        return "diagnostic_only"
    if association_model == "implicit_exact":
        exact = thresholds["exact_reference"]
        if (
            assoc_ares_rel_error <= float(exact["max_assoc_ares_rel_error"])
            and derivative_rel_error <= float(exact["max_derivative_rel_error"])
            and property_rel_error <= float(exact["max_property_rel_error"])
        ):
            return "exact_reference"
    candidate = thresholds["candidate_accuracy"]
    if (
        assoc_ares_rel_error <= float(candidate["max_assoc_ares_rel_error"])
        and derivative_rel_error <= float(candidate["max_derivative_rel_error"])
        and property_rel_error <= float(candidate["max_property_rel_error"])
        and speedup_vs_exact_implicit >= float(candidate["min_speedup_vs_exact_implicit"])
    ):
        return "candidate_accuracy"
    speed = thresholds["speed_only_candidate"]
    if (
        assoc_ares_rel_error <= float(speed["max_assoc_ares_rel_error"])
        and speedup_vs_exact_implicit >= float(speed["min_speedup_vs_exact_implicit"])
    ):
        return "speed_only_candidate"
    return "diagnostic_only"
```

- [ ] **Step 4: Add focused classifier tests**

Extend `test_propagation_evidence.py`:

```python
def test_classify_candidate_accuracy_when_derivatives_and_properties_are_bounded() -> None:
    thresholds = load_propagation_thresholds()
    band = classify_propagated_evidence_band(
        association_model="explicit_approx",
        assoc_ares_rel_error=1.0e-2,
        derivative_rel_error=2.0e-2,
        property_rel_error=3.0e-2,
        mass_action_residual_inf=1.0e-6,
        speedup_vs_exact_implicit=4.0,
        information_loss="none",
        thresholds=thresholds,
    )
    assert band == "candidate_accuracy"


def test_classify_information_loss_as_diagnostic() -> None:
    thresholds = load_propagation_thresholds()
    band = classify_propagated_evidence_band(
        association_model="explicit_approx",
        assoc_ares_rel_error=1.0e-3,
        derivative_rel_error=1.0e-3,
        property_rel_error=1.0e-3,
        mass_action_residual_inf=1.0e-6,
        speedup_vs_exact_implicit=12.0,
        information_loss="reduced_site_information",
        thresholds=thresholds,
    )
    assert band == "diagnostic_only"
```

- [ ] **Step 5: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_propagation_evidence.py -q
```

Expected result: all propagation evidence tests pass.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/config/propagation_evidence.yaml analyses/package_validation/explicit_association_toybox/scripts/propagation_evidence.py analyses/package_validation/explicit_association_toybox/tests/test_propagation_evidence.py
git commit -m "feat: add association propagation evidence bands"
```

## Task 2: Add Amortized Timing Benchmark

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/amortized_timing.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_amortized_timing.py`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`

- [ ] **Step 1: Write the failing timing summary test**

Create `test_amortized_timing.py`:

```python
from analyses.package_validation.explicit_association_toybox.scripts.amortized_timing import (
    summarize_amortized_timing_samples,
)


def test_summarize_amortized_timing_samples_keeps_exact_baseline_columns() -> None:
    rows = summarize_amortized_timing_samples(
        [
            {
                "case_id": "two_site",
                "topology_id": "2B",
                "site_count": 2,
                "closure_name": "damped_picard_7_05",
                "exact_implicit_elapsed_seconds": 0.004,
                "closure_elapsed_seconds": 0.001,
                "exact_iteration_count": 20,
            },
            {
                "case_id": "two_site",
                "topology_id": "2B",
                "site_count": 2,
                "closure_name": "damped_picard_7_05",
                "exact_implicit_elapsed_seconds": 0.006,
                "closure_elapsed_seconds": 0.002,
                "exact_iteration_count": 22,
            },
        ]
    )
    assert rows == [
        {
            "case_id": "two_site",
            "topology_id": "2B",
            "site_count": 2,
            "closure_name": "damped_picard_7_05",
            "repeat_count": 2,
            "exact_implicit_elapsed_median_seconds": 0.005,
            "closure_elapsed_median_seconds": 0.0015,
            "exact_implicit_elapsed_iqr_seconds": 0.001,
            "closure_elapsed_iqr_seconds": 0.0005,
            "speedup_vs_exact_implicit": 0.005 / 0.0015,
            "exact_iteration_count_median": 21.0,
        }
    ]
```

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_amortized_timing.py -q
```

Expected result: fail because `amortized_timing.py` does not exist yet.

- [ ] **Step 2: Implement timing summarization and runner**

Create `amortized_timing.py` with `summarize_amortized_timing_samples(samples)` and `run_amortized_timings(repeat_count=101)`. Reuse `topology_system`, `solve_exact_site_fractions`, `evaluate_closure`, and `timed_closure`. Default closure names:

```python
DEFAULT_CLOSURES = (
    "damped_picard_7_05",
)
```

The runner must emit raw sample rows with:

```text
case_id
topology_id
site_count
closure_name
exact_implicit_elapsed_seconds
closure_elapsed_seconds
exact_iteration_count
```

Use at least 2B, 3B, and 4C topologies at low and moderate `rho * Delta`.

- [ ] **Step 3: Add figure data generator**

Create `figures/amortized_timing/scripts/generate_data.py` that writes:

```text
analyses/package_validation/explicit_association_toybox/figures/amortized_timing/output/amortized_timing.csv
```

Use `repeat_count=101` for normal generation and a `--repeat-count` CLI argument for quicker debug runs.

- [ ] **Step 4: Add timing renderer**

Create `figures/amortized_timing/scripts/render_figure.py` that reads the retained CSV and writes:

```text
amortized_timing_plotted_data.csv
amortized_timing.png
amortized_timing.pdf
```

Plot closure median elapsed time, exact implicit median elapsed time, and speedup. The exact implicit baseline must be visible in the figure or in a clearly labeled panel.

- [ ] **Step 5: Register commands**

Modify `analysis.yaml`:

```yaml
  generate_amortized_timing: uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/generate_data.py
  render_amortized_timing: uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/render_figure.py
```

- [ ] **Step 6: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_amortized_timing.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/generate_data.py --repeat-count 11
uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/render_figure.py
```

Expected result: the test passes and the retained timing CSV has nonempty exact implicit timing columns.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/amortized_timing.py analyses/package_validation/explicit_association_toybox/figures/amortized_timing analyses/package_validation/explicit_association_toybox/tests/test_amortized_timing.py analyses/package_validation/explicit_association_toybox/analysis.yaml
git commit -m "feat: add amortized association closure timing"
```

## Task 3: Add Derivative Agreement Diagnostics

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/derivative_agreement.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_derivative_agreement.py`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`

- [ ] **Step 1: Write the failing centered perturbation test**

Create `test_derivative_agreement.py`:

```python
from analyses.package_validation.explicit_association_toybox.scripts.derivative_agreement import (
    centered_slope,
    summarize_derivative_agreement,
)


def test_centered_slope_uses_symmetric_samples() -> None:
    slope = centered_slope(lambda value: value * value, base_value=3.0, step_size=1.0e-5)
    assert abs(slope - 6.0) < 1.0e-8


def test_summarize_derivative_agreement_reports_required_targets() -> None:
    rows = summarize_derivative_agreement(
        [
            {
                "case_id": "case",
                "closure_name": "closure",
                "target": "a_assoc_density",
                "exact_derivative": 2.0,
                "closure_derivative": 2.1,
                "exact_implicit_elapsed_seconds": 0.004,
                "closure_elapsed_seconds": 0.001,
            }
        ]
    )
    assert rows[0]["derivative_abs_error"] == 0.10000000000000009
    assert rows[0]["derivative_rel_error"] == 0.050000000000000044
    assert rows[0]["speedup_vs_exact_implicit"] == 4.0
```

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_derivative_agreement.py -q
```

Expected result: fail because `derivative_agreement.py` does not exist yet.

- [ ] **Step 2: Implement derivative targets**

Create `derivative_agreement.py` with:

```python
DERIVATIVE_TARGETS = (
    "a_assoc_density",
    "a_assoc_strength",
    "a_assoc_composition_0",
    "pressure_proxy_density",
    "mu_proxy_composition_0",
    "fugacity_proxy_composition_0",
)
```

Implement:

- `centered_slope(function, base_value, step_size)`
- `evaluate_association_value(system, closure_name, density, strength, composition, exact=False)`
- `pressure_proxy_from_ares(density, ares_value, density_slope)`
- `mu_proxy_from_composition_slope(composition_slope)`
- `fugacity_proxy_from_mu(mu_proxy)`
- `run_derivative_agreement_cases()`
- `summarize_derivative_agreement(samples)`

The exact path must call `solve_exact_site_fractions`; closure paths must call `evaluate_closure`.

- [ ] **Step 3: Add figure workflow**

Create the generator and renderer for:

```text
figures/derivative_agreement/output/derivative_agreement.csv
figures/derivative_agreement/output/derivative_agreement_plotted_data.csv
figures/derivative_agreement/output/derivative_agreement.png
figures/derivative_agreement/output/derivative_agreement.pdf
```

Plot derivative relative error by target and closure, with exact implicit timing and closure timing summarized in plotted data.

- [ ] **Step 4: Register commands**

Modify `analysis.yaml`:

```yaml
  generate_derivative_agreement: uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/generate_data.py
  render_derivative_agreement: uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/render_figure.py
```

- [ ] **Step 5: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_derivative_agreement.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/render_figure.py
```

Expected result: tests pass and every retained row contains `exact_derivative`, `closure_derivative`, `derivative_abs_error`, `derivative_rel_error`, `exact_implicit_elapsed_seconds`, and `closure_elapsed_seconds`.

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/derivative_agreement.py analyses/package_validation/explicit_association_toybox/figures/derivative_agreement analyses/package_validation/explicit_association_toybox/tests/test_derivative_agreement.py analyses/package_validation/explicit_association_toybox/analysis.yaml
git commit -m "feat: compare association closure derivative agreement"
```

## Task 4: Add Asymmetric Binary Closure Cases

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/config/asymmetric_binary_cases.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/asymmetric_binary_closures.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_asymmetric_binary_closures.py`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`

- [ ] **Step 1: Write failing case-loader tests**

Create `test_asymmetric_binary_closures.py`:

```python
from analyses.package_validation.explicit_association_toybox.scripts.asymmetric_binary_closures import (
    load_asymmetric_binary_cases,
)


def test_asymmetric_binary_cases_cover_required_roles() -> None:
    rows = load_asymmetric_binary_cases()
    roles = {row["case_role"] for row in rows}
    assert {
        "associating_plus_inert",
        "cross_associating_binary",
        "unequal_delta_binary",
        "non_equimolar_binary",
        "water_3b_4c_contrast",
    } <= roles
```

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_asymmetric_binary_closures.py -q
```

Expected result: fail because the config and loader do not exist yet.

- [ ] **Step 2: Add asymmetric case config**

Create `config/asymmetric_binary_cases.yaml` with rows using these exact `case_id` values:

```yaml
cases:
  - case_id: assoc_plus_inert_2b_x20
    case_role: associating_plus_inert
    component_count: 2
    site_component_index: [0, 0]
    site_kind: [D, A]
    active_pairs: [[0, 1], [1, 0]]
    composition: [0.2, 0.8]
    density: 0.05
    delta_pairs: [[0, 1, 10.0], [1, 0, 10.0]]
  - case_id: cross_assoc_binary_x30
    case_role: cross_associating_binary
    component_count: 2
    site_component_index: [0, 1]
    site_kind: [D, A]
    active_pairs: [[0, 1], [1, 0]]
    composition: [0.3, 0.7]
    density: 0.05
    delta_pairs: [[0, 1, 14.0], [1, 0, 6.0]]
  - case_id: unequal_delta_binary_x70
    case_role: unequal_delta_binary
    component_count: 2
    site_component_index: [0, 0, 1, 1]
    site_kind: [D, A, D, A]
    active_pairs: [[0, 1], [1, 0], [2, 3], [3, 2], [0, 3], [3, 0]]
    composition: [0.7, 0.3]
    density: 0.04
    delta_pairs: [[0, 1, 8.0], [1, 0, 8.0], [2, 3, 3.0], [3, 2, 3.0], [0, 3, 12.0], [3, 0, 12.0]]
  - case_id: non_equimolar_3b_like_binary
    case_role: non_equimolar_binary
    component_count: 2
    site_component_index: [0, 0, 0, 1]
    site_kind: [D, A, A, D]
    active_pairs: [[0, 1], [1, 0], [0, 2], [2, 0], [3, 1], [1, 3]]
    composition: [0.15, 0.85]
    density: 0.06
    delta_pairs: [[0, 1, 7.0], [1, 0, 7.0], [0, 2, 7.0], [2, 0, 7.0], [3, 1, 4.0], [1, 3, 4.0]]
  - case_id: water_3b_4c_contrast_binary
    case_role: water_3b_4c_contrast
    component_count: 2
    site_component_index: [0, 0, 0, 1, 1, 1, 1]
    site_kind: [D, A, A, D, D, A, A]
    active_pairs: [[0, 1], [1, 0], [0, 2], [2, 0], [3, 5], [5, 3], [4, 6], [6, 4]]
    composition: [0.5, 0.5]
    density: 0.05
    delta_pairs: [[0, 1, 10.0], [1, 0, 10.0], [0, 2, 10.0], [2, 0, 10.0], [3, 5, 10.0], [5, 3, 10.0], [4, 6, 10.0], [6, 4, 10.0]]
```

- [ ] **Step 3: Implement loader and evaluator**

Create `asymmetric_binary_closures.py` with:

- `load_asymmetric_binary_cases(path)`
- `build_association_system(case)`
- `delta_from_pairs(case)`
- `run_asymmetric_binary_closures(closure_names=...)`

Each output row must include `case_id`, `case_role`, `closure_name`, `composition`, `ares_assoc_rel_error`, `mass_action_residual_inf`, `exact_implicit_elapsed_seconds`, `closure_elapsed_seconds`, and `evidence_band`.

- [ ] **Step 4: Add figure workflow and register commands**

Create:

```text
figures/asymmetric_binary_closures/output/asymmetric_binary_closures.csv
figures/asymmetric_binary_closures/output/asymmetric_binary_closures_plotted_data.csv
figures/asymmetric_binary_closures/output/asymmetric_binary_closures.png
figures/asymmetric_binary_closures/output/asymmetric_binary_closures.pdf
```

Modify `analysis.yaml`:

```yaml
  generate_asymmetric_binary_closures: uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/generate_data.py
  render_asymmetric_binary_closures: uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py
```

- [ ] **Step 5: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_asymmetric_binary_closures.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/config/asymmetric_binary_cases.yaml analyses/package_validation/explicit_association_toybox/scripts/asymmetric_binary_closures.py analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures analyses/package_validation/explicit_association_toybox/tests/test_asymmetric_binary_closures.py analyses/package_validation/explicit_association_toybox/analysis.yaml
git commit -m "feat: add asymmetric association closure cases"
```

## Task 5: Add Total EOS Impact Ranking

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/total_eos_impact.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_total_eos_impact.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`

- [ ] **Step 1: Write failing total impact schema test**

Create `test_total_eos_impact.py`:

```python
from analyses.package_validation.explicit_association_toybox.scripts.total_eos_impact import (
    summarize_total_eos_impact,
)


def test_summarize_total_eos_impact_keeps_property_and_timing_columns() -> None:
    rows = summarize_total_eos_impact(
        [
            {
                "case_id": "case",
                "closure_name": "closure",
                "ares_assoc_rel_error": 0.01,
                "ares_total_abs_error": 0.02,
                "ares_total_rel_error": 0.03,
                "pressure_proxy_abs_error": 0.04,
                "pressure_proxy_rel_error": 0.05,
                "mu_proxy_max_abs_error": 0.06,
                "fugacity_proxy_max_abs_error": 0.07,
                "exact_implicit_elapsed_seconds": 0.004,
                "closure_elapsed_seconds": 0.001,
                "evidence_band": "candidate_accuracy",
            }
        ]
    )
    assert rows[0]["speedup_vs_exact_implicit"] == 4.0
    assert rows[0]["evidence_band"] == "candidate_accuracy"
```

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_total_eos_impact.py -q
```

Expected result: fail because `total_eos_impact.py` does not exist yet.

- [ ] **Step 2: Implement total EOS impact evaluator**

Create `total_eos_impact.py`. Reuse:

- `ToyPCSAFTState` and `state_from_config` from `pcsaft_inputs.py`
- `hard_chain_state` and `ares_hc`
- `mixed_dispersion_moments` and `ares_disp`
- exact association values from `solve_exact_site_fractions`
- closure association values from `evaluate_closure`
- pressure and composition proxy formulas from `derivative_agreement.py`
- evidence bands from `propagation_evidence.py`

Each retained row must include:

```text
case_id
closure_name
ares_assoc_rel_error
ares_total_abs_error
ares_total_rel_error
pressure_proxy_abs_error
pressure_proxy_rel_error
mu_proxy_max_abs_error
fugacity_proxy_max_abs_error
exact_implicit_elapsed_seconds
closure_elapsed_seconds
speedup_vs_exact_implicit
evidence_band
```

- [ ] **Step 3: Add figure workflow and register commands**

Create:

```text
figures/total_eos_impact/output/total_eos_impact.csv
figures/total_eos_impact/output/total_eos_impact_plotted_data.csv
figures/total_eos_impact/output/total_eos_impact.png
figures/total_eos_impact/output/total_eos_impact.pdf
```

Modify `analysis.yaml`:

```yaml
  generate_total_eos_impact: uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/generate_data.py
  render_total_eos_impact: uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py
```

- [ ] **Step 4: Expand output-schema coverage**

Modify `test_output_schema.py` so `REQUIRED_COLUMNS` includes the retained exact implicit timing and propagated proxy columns when rows come from the new total impact workflow:

```python
TOTAL_IMPACT_REQUIRED_COLUMNS = {
    "pressure_proxy_abs_error",
    "pressure_proxy_rel_error",
    "mu_proxy_max_abs_error",
    "fugacity_proxy_max_abs_error",
    "exact_implicit_elapsed_seconds",
    "closure_elapsed_seconds",
    "speedup_vs_exact_implicit",
}
```

- [ ] **Step 5: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_total_eos_impact.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/total_eos_impact.py analyses/package_validation/explicit_association_toybox/figures/total_eos_impact analyses/package_validation/explicit_association_toybox/tests/test_total_eos_impact.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py analyses/package_validation/explicit_association_toybox/analysis.yaml
git commit -m "feat: rank propagated total eos impact"
```

## Task 6: Add Water Topology Fork Diagnostics

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/water_topology_fork.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_water_topology_fork.py`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`
- Modify: `analyses/package_validation/explicit_association_toybox/README.md`

- [ ] **Step 1: Write failing water fork test**

Create `test_water_topology_fork.py`:

```python
from analyses.package_validation.explicit_association_toybox.scripts.water_topology_fork import (
    summarize_water_topology_fork,
)


def test_summarize_water_topology_fork_keeps_topology_and_residual_columns() -> None:
    rows = summarize_water_topology_fork(
        [
            {
                "case_id": "water_assigned_3b_provider_default",
                "assigned_topology": "3B",
                "rigorous_topology": "4C",
                "temperature_k": 298.15,
                "pressure_residual_mpa": 120.0,
                "z_residual_abs": 0.2,
                "exact_implicit_elapsed_seconds": 0.004,
                "closure_elapsed_seconds": 0.001,
            }
        ]
    )
    assert rows[0]["speedup_vs_exact_implicit"] == 4.0
    assert rows[0]["water_diagnostic_role"] == "fixed_state_warning"
```

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_water_topology_fork.py -q
```

Expected result: fail because `water_topology_fork.py` does not exist yet.

- [ ] **Step 2: Implement water fork rows**

Create `water_topology_fork.py`. It must join existing rows from:

- `config/water_parameter_cases.yaml`
- `config/real_system_topology_map.yaml`
- `figures/property_residuals/output/property_residuals.csv`
- exact/closure timing from the local association evaluator

Each output row must include:

```text
case_id
assigned_topology
rigorous_topology
parameter_source
sigma_policy
temperature_k
pressure_residual_mpa
z_residual_abs
exact_implicit_elapsed_seconds
closure_elapsed_seconds
speedup_vs_exact_implicit
water_diagnostic_role
```

Use `water_diagnostic_role="fixed_state_warning"` when `abs(pressure_residual_mpa) >= 10.0` or `z_residual_abs >= 0.1`.

- [ ] **Step 3: Add figure workflow and register commands**

Create:

```text
figures/water_topology_fork/output/water_topology_fork.csv
figures/water_topology_fork/output/water_topology_fork_plotted_data.csv
figures/water_topology_fork/output/water_topology_fork.png
figures/water_topology_fork/output/water_topology_fork.pdf
```

Modify `analysis.yaml`:

```yaml
  generate_water_topology_fork: uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/generate_data.py
  render_water_topology_fork: uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py
```

- [ ] **Step 4: Update README warning language**

Modify `README.md` to say:

```markdown
The water topology fork is a fixed-state diagnostic. It compares topology and parameter assumptions against retained pressure and `Z` residuals, but it is not a VLE validation or saturation solver.
```

- [ ] **Step 5: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_water_topology_fork.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/property_residuals/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/water_topology_fork.py analyses/package_validation/explicit_association_toybox/figures/water_topology_fork analyses/package_validation/explicit_association_toybox/tests/test_water_topology_fork.py analyses/package_validation/explicit_association_toybox/analysis.yaml analyses/package_validation/explicit_association_toybox/README.md
git commit -m "feat: add water topology fork diagnostics"
```

## Task 7: Add Local Objective Sensitivity Diagnostic

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/equilibrium_style_objective_sensitivity.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_equilibrium_style_objective_sensitivity.py`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`

- [ ] **Step 1: Write failing objective math tests**

Create `test_equilibrium_style_objective_sensitivity.py`:

```python
import numpy as np

from analyses.package_validation.explicit_association_toybox.scripts.equilibrium_style_objective_sensitivity import (
    local_objective_value,
    max_symmetric_matrix_abs_error,
)


def test_local_objective_value_combines_total_ares_and_pressure_proxy() -> None:
    assert local_objective_value(ares_total=2.0, pressure_proxy=3.0, pressure_weight=0.25) == 2.75


def test_max_symmetric_matrix_abs_error() -> None:
    exact = np.array([[1.0, 0.5], [0.5, 2.0]])
    closure = np.array([[1.1, 0.4], [0.6, 1.8]])
    assert max_symmetric_matrix_abs_error(exact, closure) == 0.19999999999999996
```

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_equilibrium_style_objective_sensitivity.py -q
```

Expected result: fail because the objective sensitivity module does not exist yet.

- [ ] **Step 2: Implement local objective sensitivity**

Create `equilibrium_style_objective_sensitivity.py` with:

```python
OBJECTIVE_COORDINATES = ("density", "composition_component_0")
```

Implement:

- `local_objective_value(ares_total, pressure_proxy, pressure_weight)`
- `objective_gradient(case, closure_name, coordinates=OBJECTIVE_COORDINATES)`
- `objective_hessian_proxy(case, closure_name, coordinates=OBJECTIVE_COORDINATES)`
- `max_symmetric_matrix_abs_error(exact, closure)`
- `run_objective_sensitivity_cases()`

Use this objective form exactly:

```text
local_objective = ares_total + pressure_weight * pressure_proxy
```

Use `pressure_weight=0.01` in the default analysis config. The exact path must use exact implicit association; explicit rows must use the closure path. The module must avoid route names and package-level equilibrium calls.

- [ ] **Step 3: Add retained outputs**

Create the generator and renderer for:

```text
figures/equilibrium_style_objective_sensitivity/output/equilibrium_style_objective_sensitivity.csv
figures/equilibrium_style_objective_sensitivity/output/equilibrium_style_objective_sensitivity_plotted_data.csv
figures/equilibrium_style_objective_sensitivity/output/equilibrium_style_objective_sensitivity.png
figures/equilibrium_style_objective_sensitivity/output/equilibrium_style_objective_sensitivity.pdf
```

Each retained row must include:

```text
case_id
closure_name
objective_value_exact
objective_value_closure
objective_abs_error
gradient_max_abs_error
hessian_proxy_max_abs_error
exact_implicit_elapsed_seconds
closure_elapsed_seconds
speedup_vs_exact_implicit
evidence_band
```

- [ ] **Step 4: Register commands**

Modify `analysis.yaml`:

```yaml
  generate_equilibrium_style_objective_sensitivity: uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/generate_data.py
  render_equilibrium_style_objective_sensitivity: uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/render_figure.py
```

- [ ] **Step 5: Verify and commit**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_equilibrium_style_objective_sensitivity.py -q
uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/render_figure.py
```

Commit:

```powershell
git add analyses/package_validation/explicit_association_toybox/scripts/equilibrium_style_objective_sensitivity.py analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity analyses/package_validation/explicit_association_toybox/tests/test_equilibrium_style_objective_sensitivity.py analyses/package_validation/explicit_association_toybox/analysis.yaml
git commit -m "feat: add local objective sensitivity diagnostics"
```

## Task 8: Documentation, Command Index, And Final Validation

**Files:**
- Modify: `analyses/package_validation/explicit_association_toybox/README.md`
- Modify: `analyses/package_validation/explicit_association_toybox/analysis.yaml`

- [ ] **Step 1: Update README lane index**

Add a "Derivative And Property Propagation" section to `README.md` with this exact lane list:

```markdown
## Derivative And Property Propagation

This toybox section compares exact implicit association against the active explicit Picard candidate after propagation into local derivatives and EOS-like property proxies. It remains analysis-only evidence.

- `amortized_timing`: exact implicit timing baseline, closure timing, and speedup by topology.
- `derivative_agreement`: centered perturbation agreement for association, pressure-proxy, composition, chemical-potential-like, and fugacity-like targets.
- `asymmetric_binary_closures`: asymmetric composition, cross-association, inert-component, and water-like topology cases.
- `total_eos_impact`: total neutral `ares`, pressure proxy, chemical-potential proxy, and fugacity proxy ranking.
- `water_topology_fork`: water-specific 3B/4C and fixed-state residual diagnostics.
- `equilibrium_style_objective_sensitivity`: local objective gradient and Hessian-proxy diagnostics for future equilibrium discussions.
```

- [ ] **Step 2: Run all analysis-local tests**

Run:

```powershell
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
```

Expected result: all toybox tests pass.

- [ ] **Step 3: Regenerate every new figure workflow**

Run:

```powershell
uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py
uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/render_figure.py
```

Expected result: every command exits successfully and writes the retained CSV, plotted-data CSV, PNG, and PDF artifact in its figure-owned output folder.

- [ ] **Step 4: Run repo structure and quick validation**

Run:

```powershell
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python scripts/dev/validate_project.py quick
```

Expected result: both commands pass.

- [ ] **Step 5: Run cleanup hook**

Run:

```powershell
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

Expected result: no task-owned stale processes remain.

- [ ] **Step 6: Report plots and findings in chat**

The final implementation response must render these PNGs with absolute paths and include compact Markdown tables from retained plotted data:

```text
analyses/package_validation/explicit_association_toybox/figures/amortized_timing/output/amortized_timing.png
analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/output/derivative_agreement.png
analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/output/asymmetric_binary_closures.png
analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/output/total_eos_impact.png
analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/output/water_topology_fork.png
analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/output/equilibrium_style_objective_sensitivity.png
```

The summary must answer:

- Which closures are still viable after derivative agreement checks?
- Whether `damped_picard_7_05` remains the accuracy candidate after propagated property errors.
- Whether `damped_picard_7_05` remains viable in low-to-moderate association regimes.
- Which topologies and `rho * Delta` ranges fail.
- Whether water needs a separate future evidence issue.
- Whether local objective gradients and Hessian proxies are too degraded for future equilibrium discussions.

- [ ] **Step 7: Commit final docs/index updates**

Run:

```powershell
git add analyses/package_validation/explicit_association_toybox/README.md analyses/package_validation/explicit_association_toybox/analysis.yaml
git commit -m "docs: document association propagation evidence lanes"
```

## Proof Oracle

- `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/amortized_timing/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/derivative_agreement/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/asymmetric_binary_closures/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/total_eos_impact/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/water_topology_fork/scripts/render_figure.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/generate_data.py`
- `uv run python analyses/package_validation/explicit_association_toybox/figures/equilibrium_style_objective_sensitivity/scripts/render_figure.py`
- `uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q`
- `uv run python scripts/dev/validate_project.py quick`
- `pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .`

## Risk And Dependency Notes

- This plan depends on the #218 toybox outputs and the HC/dispersion scalar helpers already present in `hard_chain.py`, `dispersion.py`, `pcsaft_inputs.py`, and total `ares` output-schema tests.
- Centered perturbation diagnostics are analysis evidence only. They compare exact implicit and explicit closure behavior inside the toybox and do not replace provider exact-derivative contracts.
- Timing evidence is Python-analysis timing. Report it as toybox timing, not provider native runtime performance.
- Water fixed-state pressure residuals are warning evidence. They must not be framed as saturation or VLE validation.
- The objective diagnostic is local and route-free. It exists to test whether derivative degradation would threaten later M4 work, not to implement M4 equilibrium behavior.
- All generated plots must be rendered inline in final chat with real retained-data tables because root `AGENTS.md` requires that for new or updated analysis artifacts.
