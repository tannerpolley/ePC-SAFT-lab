# Explicit Association Toybox Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python-only package-validation analysis toybox that compares explicit PC-SAFT association closures against an independent exact mass-action baseline across EOS diagnostic grids.

**Architecture:** Keep the toybox under `analyses/package_validation/explicit_association_toybox` as analysis code, not package runtime code. Implement an independent NumPy exact baseline, closure evaluators, metrics, grid runner, retained CSV outputs, and figure rendering; do not change provider C++ or public APIs.

**Tech Stack:** Python, NumPy, pandas-compatible CSV output, Matplotlib, pytest, existing analysis layout conventions.

---

## Intake

- Source Spec: `docs/superpowers/specs/2026-06-03-m3-eos-explicit-association-toybox-design.md`
- Related follow-up spec: `docs/superpowers/specs/2026-06-03-m3-eos-paper-backed-association-closure-validation-matrix-design.md`
- Source Issue: none yet.
- Milestone Linkage: `M3 - EOS` primary; possible later `M6 - Validation` if retained grids become benchmark evidence.
- Package Boundary: analysis-only under `analyses/package_validation`; no `packages/epcsaft/**` runtime edits.
- TDD Policy: Required.
- SciPy Policy: Defer SciPy. This plan must not add SciPy imports or dependency declarations.
- Data Scope: synthetic systems first; no Gross/Sadowski parameter snapshots in this first plan.
- Threshold Policy: configurable evidence bands with a visible 2-3 percent reference line; no production admission from this analysis.
- Completion Sub-Skill: Use `superpowers:verification-before-completion` before claiming completion.

## Acceptance Criteria

- [ ] `analyses/package_validation/explicit_association_toybox/README.md` and `analysis.yaml` document the analysis purpose, commands, outputs, and analysis-only boundary.
- [ ] The toybox implements an independent Python exact mass-action baseline with residual diagnostics, site-fraction bounds, and explicit failure on nonconvergence.
- [ ] Closure evaluators cover one-component 2B exact reduction and `damped_picard_7_05` as the only active explicit approximation candidate.
- [ ] Tests prove the 2B exact reduction matches the exact baseline for its declared topology and that the active approximate closure produces bounded labeled outputs on controlled systems.
- [ ] Metrics report site-fraction error, mass-action residual norm, association Helmholtz error, association compressibility contribution error, association residual chemical-potential contribution error, association fugacity contribution error, runtime, and evidence band.
- [ ] Grid generation writes retained CSV summaries under figure-owned `output/` folders and generated run payloads under ignored `output/runs/`.
- [ ] Figure rendering produces at least one accuracy summary figure and a plotted-data CSV from retained generated data.
- [ ] No provider C++, public API, equilibrium, regression, or package dependency behavior changes.
- [ ] Structure tests continue to enforce analysis layout and no unscoped SciPy imports.

## Non-Goals

- Do not add provider C++ implementation paths for explicit association closures.
- Do not expose new public `epcsaft` APIs.
- Do not create equilibrium route prototypes.
- Do not add Gross/Sadowski paper snapshots in this first implementation.
- Do not add the full Huang/Radosz/Gross paper-backed topology matrix in this
  first implementation; that belongs to the related validation-matrix spec and
  a separate later plan.
- Do not use SciPy in committed analysis runtime code.
- Do not claim exact PC-SAFT production behavior from approximate closures.

## File Map

- Create: `analyses/package_validation/explicit_association_toybox/README.md`
- Create: `analyses/package_validation/explicit_association_toybox/analysis.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/config/closure_sweep.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/config/systems.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/__init__.py`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/association_models.py`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/exact_baseline.py`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/closure_models.py`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/metrics.py`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/run_grid.py`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/summarize_results.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/input/.gitkeep`
- Create: `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/.gitkeep`
- Create: `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_exact_2b_reduction.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_mass_action_metrics.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`
- Modify: `tests/workflows/repo/test_project_structure.py` only if a structure guard is needed for the new retained analysis root.

## Task 1: Scaffold The Analysis Contract

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/README.md`
- Create: `analyses/package_validation/explicit_association_toybox/analysis.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/config/closure_sweep.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/config/systems.yaml`
- Create: `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/input/.gitkeep`
- Create: `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/.gitkeep`
- Test: `tests/workflows/repo/test_project_structure.py`

- [ ] **Step 1: Create the analysis root and metadata**

  Write `analysis.yaml` with this content:

  ```yaml
  analysis_id: explicit_association_toybox
  title: Explicit association closure toybox
  kind: package_validation
  status: active
  package: epcsaft
  commands:
    generate_data: uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py
    render_plots: uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py
    tests: uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
  outputs:
    figures: figures/closure_accuracy/output
    runs: figures/closure_accuracy/output/runs
  ```

- [ ] **Step 2: Document the analysis boundary**

  Write `README.md` with these sections:

  ```markdown
  # Explicit Association Closure Toybox

  This analysis compares explicit PC-SAFT association closures against an
  independent Python exact mass-action baseline. It is package-validation
  analysis code, not package runtime code.

  ## Commands

  - `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py`
  - `uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py`
  - `uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q`

  ## Boundary

  The analysis may import NumPy, Matplotlib, and existing package APIs. It must
  not add provider C++, public API, equilibrium, regression, or dependency
  behavior.
  ```

- [ ] **Step 3: Add first synthetic configs**

  Write `config/systems.yaml`:

  ```yaml
  systems:
    symmetric_2b_pure:
      description: Pure symmetric donor-acceptor 2B system.
      component_count: 1
      site_component_index: [0, 0]
      site_kind: [D, A]
      active_pairs:
        - [0, 1]
        - [1, 0]
      composition_grid:
        - [1.0]
      density_grid: [0.001, 0.01, 0.05, 0.1]
      strength_grid: [0.1, 1.0, 10.0, 50.0]
    one_assoc_one_inert:
      description: One associating component diluted by one inert component.
      component_count: 2
      site_component_index: [0, 0]
      site_kind: [D, A]
      active_pairs:
        - [0, 1]
        - [1, 0]
      composition_grid:
        - [0.95, 0.05]
        - [0.50, 0.50]
        - [0.05, 0.95]
      density_grid: [0.001, 0.01, 0.05, 0.1]
      strength_grid: [0.1, 1.0, 10.0, 50.0]
    full_matrix_four_site:
      description: Four-site synthetic full-matrix association stress case.
      component_count: 2
      site_component_index: [0, 0, 1, 1]
      site_kind: [D, A, D, A]
      active_pairs:
        - [0, 1]
        - [1, 0]
        - [0, 3]
        - [3, 0]
        - [2, 1]
        - [1, 2]
      composition_grid:
        - [0.8, 0.2]
        - [0.5, 0.5]
        - [0.2, 0.8]
      density_grid: [0.001, 0.01, 0.05]
      strength_grid: [0.1, 1.0, 10.0]
  ```

  Write `config/closure_sweep.yaml`:

  ```yaml
  evidence_bands:
    thermodynamic_relative_reference: 0.03
    mass_residual_tight: 1.0e-10
    mass_residual_loose: 1.0e-6
    site_fraction_abs_tight: 1.0e-10
    site_fraction_abs_loose: 1.0e-3
  closures:
    - name: exact_2b_reduction
      kind: exact_reduction
    - name: damped_picard_7_05
      kind: explicit_approx
      picard_steps: 7
      damping: 0.5
  ```

- [ ] **Step 4: Run the structure suite**

  Run:

  ```powershell
  uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
  ```

  Expected: PASS. If it fails because the analysis root needs explicit registration, add the narrowest structure-test update that recognizes this analysis root.

- [ ] **Step 5: Commit the scaffold**

  ```powershell
  git add analyses/package_validation/explicit_association_toybox tests/workflows/repo/test_project_structure.py
  git commit -m "docs: scaffold explicit association toybox"
  ```

## Task 2: Implement The Exact Python Baseline

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/association_models.py`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/exact_baseline.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_mass_action_metrics.py`

- [ ] **Step 1: Write failing tests for mass-action residuals and exact solve**

  Write `test_mass_action_metrics.py`:

  ```python
  from __future__ import annotations

  import numpy as np

  from analyses.package_validation.explicit_association_toybox.scripts.association_models import (
      AssociationSystem,
      association_helmholtz,
      mass_action_residual,
  )
  from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import (
      solve_exact_site_fractions,
      stable_two_class_2b_solution,
  )


  def test_symmetric_2b_formula_satisfies_mass_action() -> None:
      system = AssociationSystem(
          component_count=1,
          site_component_index=np.array([0, 0], dtype=int),
          site_kind=("D", "A"),
          active_pairs=((0, 1), (1, 0)),
      )
      density = 0.25
      composition = np.array([1.0])
      delta = system.delta_matrix(strength=4.0)

      xa = stable_two_class_2b_solution(density=density, x_assoc=composition[0], delta_da=delta[0, 1])

      residual = mass_action_residual(xa, density=density, x_assoc=system.x_assoc(composition), delta=delta)
      assert np.linalg.norm(residual, ord=np.inf) < 1.0e-12


  def test_exact_solver_returns_bounded_site_fractions_and_helmholtz() -> None:
      system = AssociationSystem(
          component_count=2,
          site_component_index=np.array([0, 0], dtype=int),
          site_kind=("D", "A"),
          active_pairs=((0, 1), (1, 0)),
      )
      density = 0.1
      composition = np.array([0.5, 0.5])
      delta = system.delta_matrix(strength=10.0)

      result = solve_exact_site_fractions(
          density=density,
          x_assoc=system.x_assoc(composition),
          delta=delta,
      )

      assert result.converged is True
      assert result.residual_norm <= 1.0e-10
      assert np.all(result.xa > 0.0)
      assert np.all(result.xa <= 1.0)
      assert association_helmholtz(result.xa, composition, system.site_component_index) <= 0.0
  ```

- [ ] **Step 2: Run the tests and verify the expected failure**

  Run:

  ```powershell
  uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_mass_action_metrics.py -q
  ```

  Expected: FAIL because `association_models.py` and `exact_baseline.py` do not exist yet.

- [ ] **Step 3: Implement system helpers and exact baseline**

  Create `association_models.py` with:

  ```python
  from __future__ import annotations

  from dataclasses import dataclass
  from typing import Sequence

  import numpy as np


  @dataclass(frozen=True)
  class AssociationSystem:
      component_count: int
      site_component_index: np.ndarray
      site_kind: tuple[str, ...]
      active_pairs: tuple[tuple[int, int], ...]

      def __post_init__(self) -> None:
          if self.site_component_index.ndim != 1:
              raise ValueError("site_component_index must be one-dimensional.")
          if len(self.site_kind) != self.site_component_index.size:
              raise ValueError("site_kind length must match site count.")
          if np.any(self.site_component_index < 0) or np.any(self.site_component_index >= self.component_count):
              raise ValueError("site_component_index contains an invalid component index.")

      @property
      def site_count(self) -> int:
          return int(self.site_component_index.size)

      def x_assoc(self, composition: np.ndarray) -> np.ndarray:
          composition = np.asarray(composition, dtype=float)
          if composition.shape != (self.component_count,):
              raise ValueError("composition length must match component_count.")
          if not np.isclose(float(np.sum(composition)), 1.0):
              raise ValueError("composition must sum to one.")
          if np.any(composition < 0.0):
              raise ValueError("composition must be nonnegative.")
          return composition[self.site_component_index]

      def delta_matrix(self, strength: float) -> np.ndarray:
          if not np.isfinite(strength) or strength < 0.0:
              raise ValueError("strength must be finite and nonnegative.")
          delta = np.zeros((self.site_count, self.site_count), dtype=float)
          for i, j in self.active_pairs:
              delta[i, j] = float(strength)
          return delta


  def mass_action_residual(xa: np.ndarray, *, density: float, x_assoc: np.ndarray, delta: np.ndarray) -> np.ndarray:
      xa = np.asarray(xa, dtype=float)
      x_assoc = np.asarray(x_assoc, dtype=float)
      delta = np.asarray(delta, dtype=float)
      if delta.shape != (xa.size, xa.size):
          raise ValueError("delta must be a square matrix matching xa.")
      return xa * (1.0 + density * (delta @ (x_assoc * xa))) - 1.0


  def association_helmholtz(xa: np.ndarray, composition: np.ndarray, site_component_index: np.ndarray) -> float:
      xa = np.asarray(xa, dtype=float)
      composition = np.asarray(composition, dtype=float)
      site_component_index = np.asarray(site_component_index, dtype=int)
      if np.any(xa <= 0.0):
          raise ValueError("site fractions must be positive for association Helmholtz evaluation.")
      terms = np.log(xa) - 0.5 * xa + 0.5
      weights = composition[site_component_index]
      return float(np.sum(weights * terms))
  ```

  Create `exact_baseline.py` with:

  ```python
  from __future__ import annotations

  from dataclasses import dataclass

  import numpy as np

  from .association_models import mass_action_residual


  @dataclass(frozen=True)
  class ExactAssociationResult:
      xa: np.ndarray
      converged: bool
      iteration_count: int
      update_norm: float
      residual_norm: float


  def stable_two_class_2b_solution(*, density: float, x_assoc: float, delta_da: float) -> np.ndarray:
      c = density * x_assoc * delta_da
      if c < 0.0 or not np.isfinite(c):
          raise ValueError("2B strength must be finite and nonnegative.")
      value = 2.0 / (1.0 + np.sqrt(1.0 + 4.0 * c))
      return np.array([value, value], dtype=float)


  def solve_exact_site_fractions(
      *,
      density: float,
      x_assoc: np.ndarray,
      delta: np.ndarray,
      max_iterations: int = 100,
      update_tolerance: float = 1.0e-15,
      residual_tolerance: float = 1.0e-10,
      relaxation_factor: float = 0.5,
  ) -> ExactAssociationResult:
      if density <= 0.0 or not np.isfinite(density):
          raise ValueError("density must be positive and finite.")
      x_assoc = np.asarray(x_assoc, dtype=float)
      delta = np.asarray(delta, dtype=float)
      if delta.shape != (x_assoc.size, x_assoc.size):
          raise ValueError("delta must be square and match x_assoc.")
      xa_old = np.ones_like(x_assoc, dtype=float)
      update_norm = float("inf")
      residual_norm = float("inf")
      for iteration in range(1, max_iterations + 1):
          xa_new = 1.0 / (1.0 + density * (delta @ (x_assoc * xa_old)))
          update_norm = float(np.sum(np.abs(xa_new - xa_old)))
          xa_mixed = relaxation_factor * (xa_new + xa_old)
          residual = mass_action_residual(xa_mixed, density=density, x_assoc=x_assoc, delta=delta)
          residual_norm = float(np.linalg.norm(residual, ord=np.inf))
          if (
              update_norm <= update_tolerance
              and residual_norm <= residual_tolerance
              and np.all(xa_mixed > 0.0)
              and np.all(xa_mixed <= 1.0)
          ):
              return ExactAssociationResult(xa=xa_mixed, converged=True, iteration_count=iteration, update_norm=update_norm, residual_norm=residual_norm)
          xa_old = xa_mixed
      raise RuntimeError(
          "association exact baseline solve did not converge; "
          f"iteration_count={max_iterations}; update_norm={update_norm}; residual_norm={residual_norm}"
      )
  ```

- [ ] **Step 4: Run the tests and verify they pass**

  ```powershell
  uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_mass_action_metrics.py -q
  ```

  Expected: PASS.

- [ ] **Step 5: Commit**

  ```powershell
  git add analyses/package_validation/explicit_association_toybox/scripts analyses/package_validation/explicit_association_toybox/tests/test_mass_action_metrics.py
  git commit -m "test: add explicit association exact baseline"
  ```

## Task 3: Add Explicit Closure Evaluators

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/closure_models.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_exact_2b_reduction.py`

- [ ] **Step 1: Write closure tests first**

  Write `test_exact_2b_reduction.py`:

  ```python
  from __future__ import annotations

  import numpy as np

  from analyses.package_validation.explicit_association_toybox.scripts.association_models import (
      AssociationSystem,
      mass_action_residual,
  )
  from analyses.package_validation.explicit_association_toybox.scripts.closure_models import (
      evaluate_closure,
  )
  from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import (
      solve_exact_site_fractions,
  )


  def _system() -> AssociationSystem:
      return AssociationSystem(
          component_count=1,
          site_component_index=np.array([0, 0], dtype=int),
          site_kind=("D", "A"),
          active_pairs=((0, 1), (1, 0)),
      )


  def test_exact_2b_reduction_matches_exact_symmetric_2b_baseline() -> None:
      system = _system()
      density = 0.2
      composition = np.array([1.0])
      delta = system.delta_matrix(strength=3.0)
      exact = solve_exact_site_fractions(density=density, x_assoc=system.x_assoc(composition), delta=delta)

      closure = evaluate_closure(
          "exact_2b_reduction",
          system=system,
          density=density,
          composition=composition,
          delta=delta,
      )

      np.testing.assert_allclose(closure.xa, exact.xa, atol=1.0e-12, rtol=1.0e-12)
      assert closure.association_model == "implicit_exact"
      assert closure.exact_derivative_of == "exact_mass_action"


  def test_approximate_closures_are_bounded_and_labeled() -> None:
      system = _system()
      density = 0.2
      composition = np.array([1.0])
      delta = system.delta_matrix(strength=3.0)

      for name in ("damped_picard_7_05",):
          closure = evaluate_closure(name, system=system, density=density, composition=composition, delta=delta)
          assert np.all(closure.xa > 0.0), name
          assert np.all(closure.xa <= 1.0), name
          assert closure.association_model == "explicit_approx"
          assert closure.exact_derivative_of == "approximate_association_closure"
          residual = mass_action_residual(closure.xa, density=density, x_assoc=system.x_assoc(composition), delta=delta)
          assert np.isfinite(np.linalg.norm(residual, ord=np.inf))
  ```

- [ ] **Step 2: Run the tests and verify the expected failure**

  ```powershell
  uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_exact_2b_reduction.py -q
  ```

  Expected: FAIL because `closure_models.py` does not exist.

- [ ] **Step 3: Implement closure models**

  Create `closure_models.py` with:

  ```python
  from __future__ import annotations

  from dataclasses import dataclass

  import numpy as np

  from .association_models import AssociationSystem, mass_action_residual
  from .exact_baseline import stable_two_class_2b_solution


  @dataclass(frozen=True)
  class ClosureResult:
      name: str
      xa: np.ndarray
      association_model: str
      association_closure: str
      exact_derivative_of: str
      information_loss: str


  def _row_sum_initializer(density: float, x_assoc: np.ndarray, delta: np.ndarray) -> np.ndarray:
      strengths = density * np.sum(delta * x_assoc[np.newaxis, :], axis=1)
      return 2.0 / (1.0 + np.sqrt(1.0 + 4.0 * strengths))


  def _picard(density: float, x_assoc: np.ndarray, delta: np.ndarray, *, steps: int, damping: float) -> np.ndarray:
      xa = _row_sum_initializer(density, x_assoc, delta)
      for _ in range(steps):
          proposal = 1.0 / (1.0 + density * (delta @ (x_assoc * xa)))
          xa = (1.0 - damping) * xa + damping * proposal
      return xa


  def evaluate_closure(
      name: str,
      *,
      system: AssociationSystem,
      density: float,
      composition: np.ndarray,
      delta: np.ndarray,
  ) -> ClosureResult:
      x_assoc = system.x_assoc(composition)
      if name == "exact_2b_reduction":
          if system.site_count != 2 or tuple(system.site_kind) != ("D", "A"):
              raise ValueError("exact_2b_reduction requires a two-site D/A topology.")
          xa = stable_two_class_2b_solution(density=density, x_assoc=x_assoc[0], delta_da=delta[0, 1])
          return ClosureResult(name=name, xa=xa, association_model="implicit_exact", association_closure=name, exact_derivative_of="exact_mass_action", information_loss="none")
      if name == "damped_picard_7_05":
          xa = _picard(density, x_assoc, delta, steps=7, damping=0.5)
      else:
          raise ValueError(f"Unknown association closure: {name}")
      return ClosureResult(name=name, xa=xa, association_model="explicit_approx", association_closure=name, exact_derivative_of="approximate_association_closure", information_loss="none")
  ```

- [ ] **Step 4: Run closure and baseline tests**

  ```powershell
  uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_mass_action_metrics.py analyses/package_validation/explicit_association_toybox/tests/test_exact_2b_reduction.py -q
  ```

  Expected: PASS.

- [ ] **Step 5: Commit**

  ```powershell
  git add analyses/package_validation/explicit_association_toybox/scripts/closure_models.py analyses/package_validation/explicit_association_toybox/tests/test_exact_2b_reduction.py
  git commit -m "feat: add explicit association closure models"
  ```

## Task 4: Add Metrics And Evidence Bands

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/metrics.py`
- Create: `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`

- [ ] **Step 1: Write metric and schema tests**

  Write `test_output_schema.py`:

  ```python
  from __future__ import annotations

  import numpy as np

  from analyses.package_validation.explicit_association_toybox.scripts.association_models import AssociationSystem
  from analyses.package_validation.explicit_association_toybox.scripts.closure_models import evaluate_closure
  from analyses.package_validation.explicit_association_toybox.scripts.exact_baseline import solve_exact_site_fractions
  from analyses.package_validation.explicit_association_toybox.scripts.metrics import metric_row


  REQUIRED_COLUMNS = {
      "system",
      "closure",
      "association_model",
      "exact_derivative_of",
      "density",
      "strength",
      "max_abs_x_error",
      "mass_residual_inf",
      "assoc_helmholtz_abs_error",
      "evidence_band",
  }


  def test_metric_row_contains_required_columns() -> None:
      system = AssociationSystem(
          component_count=1,
          site_component_index=np.array([0, 0], dtype=int),
          site_kind=("D", "A"),
          active_pairs=((0, 1), (1, 0)),
      )
      density = 0.1
      composition = np.array([1.0])
      delta = system.delta_matrix(strength=2.0)
      exact = solve_exact_site_fractions(density=density, x_assoc=system.x_assoc(composition), delta=delta)
      closure = evaluate_closure("damped_picard_7_05", system=system, density=density, composition=composition, delta=delta)

      row = metric_row(
          system_name="symmetric_2b_pure",
          system=system,
          density=density,
          strength=2.0,
          composition=composition,
          delta=delta,
          exact=exact,
          closure=closure,
          thresholds={"thermodynamic_relative_reference": 0.03, "mass_residual_loose": 1.0e-6},
      )

      assert REQUIRED_COLUMNS <= set(row)
      assert row["evidence_band"] in {
          "exact_reduction_verified",
          "promising_eos_approximation",
          "diagnostic_only",
          "reject_for_provider_path",
      }
  ```

- [ ] **Step 2: Run the schema test and verify the expected failure**

  ```powershell
  uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py -q
  ```

  Expected: FAIL because `metrics.py` does not exist.

- [ ] **Step 3: Implement metrics**

  Create `metrics.py`:

  ```python
  from __future__ import annotations

  import time
  from collections.abc import Mapping

  import numpy as np

  from .association_models import AssociationSystem, association_helmholtz, mass_action_residual
  from .closure_models import ClosureResult
  from .exact_baseline import ExactAssociationResult


  def classify_evidence_band(
      *,
      closure: ClosureResult,
      max_abs_x_error: float,
      mass_residual_inf: float,
      assoc_helmholtz_rel_error: float,
      thresholds: Mapping[str, float],
  ) -> str:
      if closure.association_model == "implicit_exact" and max_abs_x_error <= 1.0e-10 and mass_residual_inf <= 1.0e-10:
          return "exact_reduction_verified"
      if not np.isfinite(mass_residual_inf) or np.any(closure.xa <= 0.0) or np.any(closure.xa > 1.0):
          return "reject_for_provider_path"
      reference = float(thresholds.get("thermodynamic_relative_reference", 0.03))
      loose_residual = float(thresholds.get("mass_residual_loose", 1.0e-6))
      if assoc_helmholtz_rel_error <= reference and mass_residual_inf <= loose_residual:
          return "promising_eos_approximation"
      return "diagnostic_only"


  def metric_row(
      *,
      system_name: str,
      system: AssociationSystem,
      density: float,
      strength: float,
      composition: np.ndarray,
      delta: np.ndarray,
      exact: ExactAssociationResult,
      closure: ClosureResult,
      thresholds: Mapping[str, float],
      elapsed_seconds: float | None = None,
  ) -> dict[str, object]:
      residual = mass_action_residual(closure.xa, density=density, x_assoc=system.x_assoc(composition), delta=delta)
      exact_a = association_helmholtz(exact.xa, composition, system.site_component_index)
      closure_assoc = association_helmholtz(closure.xa, composition, system.site_component_index)
      abs_a = abs(closure_assoc - exact_a)
      rel_a = abs_a / max(abs(exact_a), 1.0e-14)
      max_abs_x = float(np.max(np.abs(closure.xa - exact.xa)))
      band = classify_evidence_band(
          closure=closure,
          max_abs_x_error=max_abs_x,
          mass_residual_inf=float(np.linalg.norm(residual, ord=np.inf)),
          assoc_helmholtz_rel_error=float(rel_a),
          thresholds=thresholds,
      )
      return {
          "system": system_name,
          "closure": closure.name,
          "association_model": closure.association_model,
          "association_closure": closure.association_closure,
          "exact_derivative_of": closure.exact_derivative_of,
          "information_loss": closure.information_loss,
          "density": density,
          "strength": strength,
          "composition": ";".join(f"{value:.12g}" for value in composition),
          "max_abs_x_error": max_abs_x,
          "max_rel_x_error": float(np.max(np.abs(closure.xa - exact.xa) / np.maximum(np.abs(exact.xa), 1.0e-14))),
          "mass_residual_inf": float(np.linalg.norm(residual, ord=np.inf)),
          "assoc_helmholtz_exact": exact_a,
          "assoc_helmholtz_closure": closure_assoc,
          "assoc_helmholtz_abs_error": abs_a,
          "assoc_helmholtz_rel_error": float(rel_a),
          "assoc_compressibility_abs_error": np.nan,
          "assoc_mu_abs_error": np.nan,
          "assoc_fugacity_abs_error": np.nan,
          "exact_iteration_count": exact.iteration_count,
          "exact_residual_norm": exact.residual_norm,
          "closure_elapsed_seconds": elapsed_seconds if elapsed_seconds is not None else np.nan,
          "evidence_band": band,
      }


  def timed_closure(callable_obj):
      start = time.perf_counter()
      result = callable_obj()
      return result, time.perf_counter() - start
  ```

- [ ] **Step 4: Run all toybox tests**

  ```powershell
  uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
  ```

  Expected: PASS.

- [ ] **Step 5: Commit**

  ```powershell
  git add analyses/package_validation/explicit_association_toybox/scripts/metrics.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py
  git commit -m "feat: add association toybox metrics"
  ```

## Task 5: Add Grid Runner And Retained Data Output

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/scripts/run_grid.py`
- Create: `analyses/package_validation/explicit_association_toybox/scripts/summarize_results.py`
- Modify: `analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py`

- [ ] **Step 1: Extend output tests for a tiny grid**

  Add this test to `test_output_schema.py`:

  ```python
  from pathlib import Path

  from analyses.package_validation.explicit_association_toybox.scripts.run_grid import run_grid


  def test_run_grid_writes_retained_csv(tmp_path: Path) -> None:
      output = tmp_path / "closure_metrics.csv"
      run_grid(output_path=output, system_names=("symmetric_2b_pure",), closure_names=("exact_2b_reduction",))
      text = output.read_text(encoding="utf-8")
      assert "system,closure," in text
      assert "symmetric_2b_pure,exact_2b_reduction" in text
  ```

- [ ] **Step 2: Run the grid test and verify the expected failure**

  ```powershell
  uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests/test_output_schema.py::test_run_grid_writes_retained_csv -q
  ```

  Expected: FAIL because `run_grid.py` does not exist.

- [ ] **Step 3: Implement the grid runner**

  Create `run_grid.py` with:

  ```python
  from __future__ import annotations

  import argparse
  import csv
  from pathlib import Path
  from typing import Iterable

  import numpy as np
  import yaml

  from .association_models import AssociationSystem
  from .closure_models import evaluate_closure
  from .exact_baseline import solve_exact_site_fractions
  from .metrics import metric_row, timed_closure

  ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
  DEFAULT_OUTPUT = ANALYSIS_ROOT / "figures" / "closure_accuracy" / "output" / "closure_metrics.csv"


  def _load_yaml(path: Path) -> dict:
      with path.open("r", encoding="utf-8") as handle:
          data = yaml.safe_load(handle)
      if not isinstance(data, dict):
          raise ValueError(f"{path} must contain a YAML mapping.")
      return data


  def _system_from_config(config: dict) -> AssociationSystem:
      return AssociationSystem(
          component_count=int(config["component_count"]),
          site_component_index=np.array(config["site_component_index"], dtype=int),
          site_kind=tuple(str(value) for value in config["site_kind"]),
          active_pairs=tuple(tuple(int(item) for item in pair) for pair in config["active_pairs"]),
      )


  def run_grid(
      *,
      output_path: Path = DEFAULT_OUTPUT,
      system_names: Iterable[str] | None = None,
      closure_names: Iterable[str] | None = None,
  ) -> Path:
      systems_doc = _load_yaml(ANALYSIS_ROOT / "config" / "systems.yaml")
      closures_doc = _load_yaml(ANALYSIS_ROOT / "config" / "closure_sweep.yaml")
      systems = systems_doc["systems"]
      closures = closures_doc["closures"]
      thresholds = closures_doc["evidence_bands"]
      selected_systems = set(system_names) if system_names is not None else set(systems)
      selected_closures = set(closure_names) if closure_names is not None else {closure["name"] for closure in closures}
      rows: list[dict[str, object]] = []
      for system_name, system_config in systems.items():
          if system_name not in selected_systems:
              continue
          system = _system_from_config(system_config)
          for composition_values in system_config["composition_grid"]:
              composition = np.array(composition_values, dtype=float)
              for density in system_config["density_grid"]:
                  for strength in system_config["strength_grid"]:
                      delta = system.delta_matrix(float(strength))
                      exact = solve_exact_site_fractions(density=float(density), x_assoc=system.x_assoc(composition), delta=delta)
                      for closure_config in closures:
                          closure_name = str(closure_config["name"])
                          if closure_name not in selected_closures:
                              continue
                          closure, elapsed = timed_closure(
                              lambda closure_name=closure_name: evaluate_closure(
                                  closure_name,
                                  system=system,
                                  density=float(density),
                                  composition=composition,
                                  delta=delta,
                              )
                          )
                          rows.append(
                              metric_row(
                                  system_name=system_name,
                                  system=system,
                                  density=float(density),
                                  strength=float(strength),
                                  composition=composition,
                                  delta=delta,
                                  exact=exact,
                                  closure=closure,
                                  thresholds=thresholds,
                                  elapsed_seconds=elapsed,
                              )
                          )
      if not rows:
          raise ValueError("grid selection produced no rows.")
      output_path.parent.mkdir(parents=True, exist_ok=True)
      with output_path.open("w", newline="", encoding="utf-8") as handle:
          writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
          writer.writeheader()
          writer.writerows(rows)
      return output_path


  def main() -> None:
      parser = argparse.ArgumentParser(description="Run explicit association closure accuracy grids.")
      parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
      args = parser.parse_args()
      path = run_grid(output_path=args.output)
      print(path)


  if __name__ == "__main__":
      main()
  ```

  Create `summarize_results.py`:

  ```python
  from __future__ import annotations

  import argparse
  import csv
  from collections import Counter
  from pathlib import Path

  from .run_grid import DEFAULT_OUTPUT


  def summarize(path: Path = DEFAULT_OUTPUT) -> dict[str, int]:
      with path.open("r", encoding="utf-8", newline="") as handle:
          rows = list(csv.DictReader(handle))
      return dict(Counter(row["evidence_band"] for row in rows))


  def main() -> None:
      parser = argparse.ArgumentParser(description="Summarize explicit association closure evidence bands.")
      parser.add_argument("--input", type=Path, default=DEFAULT_OUTPUT)
      args = parser.parse_args()
      for band, count in sorted(summarize(args.input).items()):
          print(f"{band}: {count}")


  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 4: Run tests and generate retained CSV**

  ```powershell
  uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
  uv run python analyses/package_validation/explicit_association_toybox/scripts/run_grid.py
  ```

  Expected: tests PASS and `figures/closure_accuracy/output/closure_metrics.csv` is written.

- [ ] **Step 5: Commit**

  ```powershell
  git add analyses/package_validation/explicit_association_toybox
  git commit -m "feat: add explicit association closure grid runner"
  ```

## Task 6: Add Figure Data Generation And Rendering

**Files:**
- Create: `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py`
- Create: `analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py`

- [ ] **Step 1: Add figure data script**

  Create `generate_data.py`:

  ```python
  from __future__ import annotations

  import sys
  from pathlib import Path

  ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
  REPO_ROOT = ANALYSIS_ROOT.parents[2]
  if str(REPO_ROOT) not in sys.path:
      sys.path.insert(0, str(REPO_ROOT))

  from analyses.package_validation.explicit_association_toybox.scripts.run_grid import DEFAULT_OUTPUT, run_grid


  def main() -> None:
      output = run_grid(output_path=DEFAULT_OUTPUT)
      print(output)


  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 2: Add figure renderer**

  Create `render_figure.py`:

  ```python
  from __future__ import annotations

  import csv
  from pathlib import Path

  import matplotlib.pyplot as plt

  ANALYSIS_ROOT = Path(__file__).resolve().parents[3]
  OUTPUT = ANALYSIS_ROOT / "figures" / "closure_accuracy" / "output"
  METRICS = OUTPUT / "closure_metrics.csv"
  FIGURE = OUTPUT / "closure_accuracy_summary.png"
  PLOTTED = OUTPUT / "closure_accuracy_summary_plotted_data.csv"
  PDF = OUTPUT / "closure_accuracy_summary.pdf"


  def _load_rows() -> list[dict[str, str]]:
      with METRICS.open("r", encoding="utf-8", newline="") as handle:
          return list(csv.DictReader(handle))


  def main() -> None:
      rows = _load_rows()
      grouped: dict[str, list[float]] = {}
      for row in rows:
          grouped.setdefault(row["closure"], []).append(float(row["assoc_helmholtz_rel_error"]))
      names = sorted(grouped)
      values = [max(grouped[name]) for name in names]
      OUTPUT.mkdir(parents=True, exist_ok=True)
      with PLOTTED.open("w", encoding="utf-8", newline="") as handle:
          writer = csv.writer(handle)
          writer.writerow(["closure", "max_assoc_helmholtz_rel_error"])
          writer.writerows(zip(names, values))
      fig, ax = plt.subplots(figsize=(9, 4.5))
      ax.bar(names, values)
      ax.axhline(0.03, color="black", linestyle="--", linewidth=1.0, label="3 percent reference")
      ax.set_ylabel("Max relative association Helmholtz error")
      ax.set_xlabel("Closure")
      ax.tick_params(axis="x", rotation=30)
      ax.legend()
      fig.tight_layout()
      fig.savefig(FIGURE, dpi=160)
      PDF.write_text(
          "figure: closure_accuracy_summary.png\n"
          "source_data: closure_accuracy_summary_plotted_data.csv\n"
          "reference_line: 0.03\n",
          encoding="utf-8",
      )
      print(FIGURE)


  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 3: Run figure scripts**

  ```powershell
  uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py
  uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py
  ```

  Expected:

  ```text
  analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/closure_metrics.csv
  analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/closure_accuracy_summary.png
  ```

- [ ] **Step 4: Verify retained artifacts**

  Confirm these files exist and are tracked:

  ```powershell
  Test-Path analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/closure_metrics.csv
  Test-Path analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/closure_accuracy_summary_plotted_data.csv
  Test-Path analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/closure_accuracy_summary.png
  Test-Path analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/output/closure_accuracy_summary.pdf
  ```

- [ ] **Step 5: Commit**

  ```powershell
  git add analyses/package_validation/explicit_association_toybox
  git commit -m "docs: add explicit association toybox outputs"
  ```

## Task 7: Final Validation And Guard Checks

**Files:**
- Modify: only scoped fixes discovered by validation.
- Test: `analyses/package_validation/explicit_association_toybox/tests`
- Test: `tests/workflows/repo/test_project_structure.py`

- [ ] **Step 1: Prove no SciPy imports were added**

  Run:

  ```powershell
  rg -n "import scipy|from scipy" analyses/package_validation/explicit_association_toybox packages tests scripts
  ```

  Expected: no matches.

- [ ] **Step 2: Run toybox tests**

  ```powershell
  uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
  ```

  Expected: PASS.

- [ ] **Step 3: Run figure generation**

  ```powershell
  uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py
  uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py
  ```

  Expected: retained CSV, plotted-data CSV, PNG, and PDF artifact are present under `figures/closure_accuracy/output/`.

- [ ] **Step 4: Run structure and quick validation**

  ```powershell
  uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
  uv run python scripts/dev/validate_project.py quick
  ```

  Expected: PASS.

- [ ] **Step 5: Run cleanup hook**

  ```powershell
  pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
  ```

  Expected: no leftover processes owned by this repo task.

- [ ] **Step 6: Commit final validation fixes**

  If validation requires small scoped edits, commit them:

  ```powershell
  git add analyses/package_validation/explicit_association_toybox tests/workflows/repo/test_project_structure.py
  git commit -m "test: validate explicit association toybox"
  ```

## Proof Oracle

```powershell
rg -n "import scipy|from scipy" analyses/package_validation/explicit_association_toybox packages tests scripts
uv run python run_pytest.py analyses/package_validation/explicit_association_toybox/tests -q
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/generate_data.py
uv run python analyses/package_validation/explicit_association_toybox/figures/closure_accuracy/scripts/render_figure.py
uv run python run_pytest.py tests/workflows/repo/test_project_structure.py -q
uv run python scripts/dev/validate_project.py quick
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.codex\hooks\codex-cleanup.ps1" -RepoRoot .
```

## Risk And Dependency Notes

- The toybox uses simplified synthetic `Delta` matrices first. That is intentional; it proves the closure machinery before Gross/Sadowski parameter snapshots are introduced.
- The first implementation does not add SciPy. A later issue may add a scoped project-structure exception for this analysis only.
- Association compressibility, residual chemical-potential, and fugacity contribution errors are represented in the schema from the start. If the first implementation cannot compute them with provider-equation consistency, keep their values explicit as `NaN` and do not classify approximate closures as production-ready from those missing columns.
- The retained PNG is useful for review, but the plotted-data CSV and full metrics CSV are the durable evidence artifacts.
- This analysis must not be used to close M4 associating equilibrium issues by itself. It can only inform later provider/equilibrium design.
