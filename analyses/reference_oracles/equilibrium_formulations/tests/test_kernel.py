from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from analyses.reference_oracles.equilibrium_formulations.kernel import (
    BoxDomain,
    CandidateOutcome,
    Certificate,
    DirectAdapter,
    DirectProblem,
    FormulationDescriptor,
    NumericalKind,
    ResidualAdapter,
    ResidualProblem,
    check_direct_derivatives,
    check_residual_derivatives,
    run_direct,
    run_residual,
    summarize_convergence,
)

DIRECT_ID = "manufactured.direct-quadratic.v1"
RESIDUAL_ID = "manufactured.linear-residual.v1"
DIRECT_DESCRIPTOR = FormulationDescriptor(
    formulation_id=DIRECT_ID,
    family="manufactured direct test",
    numerical_kind=NumericalKind.DIRECT_MINIMIZATION,
)
RESIDUAL_DESCRIPTOR = FormulationDescriptor(
    formulation_id=RESIDUAL_ID,
    family="manufactured residual test",
    numerical_kind=NumericalKind.RESIDUAL_SOLVE,
)


@dataclass(frozen=True)
class QuadraticAdapter(DirectAdapter):
    descriptor: FormulationDescriptor = DIRECT_DESCRIPTOR

    def build(self) -> DirectProblem:
        target = np.asarray([0.25, 0.75])
        return DirectProblem(
            descriptor=self.descriptor,
            domain=BoxDomain.from_sequences([0.0, 0.0], [1.0, 1.0], [1.0, 1.0]),
            objective=lambda vector: float(np.dot(vector - target, vector - target)),
            gradient=lambda vector: 2.0 * (vector - target),
        )

    def starts(self, seed: int) -> tuple[np.ndarray, ...]:
        generator = np.random.default_rng(seed)
        return (np.asarray([0.9, 0.1]), generator.uniform(0.0, 1.0, size=2))

    def certify(self, vector: np.ndarray) -> Certificate:
        gap = float(np.max(np.abs(vector - np.asarray([0.25, 0.75]))))
        return Certificate(self.descriptor.formulation_id, gap < 1.0e-8, {"analytic_solution_gap": gap}, True)


@dataclass(frozen=True)
class LinearResidualAdapter(ResidualAdapter):
    descriptor: FormulationDescriptor = RESIDUAL_DESCRIPTOR

    def build(self) -> ResidualProblem:
        matrix = np.asarray([[2.0, 1.0], [1.0, -1.0]])
        right_hand_side = np.asarray([1.0, 0.0])
        return ResidualProblem(
            descriptor=self.descriptor,
            domain=BoxDomain.from_sequences([-1.0, -1.0], [1.0, 1.0], [1.0, 1.0]),
            residual=lambda vector: matrix @ vector - right_hand_side,
            jacobian=lambda _vector: matrix,
        )

    def starts(self, seed: int) -> tuple[np.ndarray, ...]:
        generator = np.random.default_rng(seed)
        return (np.asarray([-0.5, 0.5]), generator.uniform(-1.0, 1.0, size=2))

    def certify(self, vector: np.ndarray) -> Certificate:
        gap = float(np.max(np.abs(vector - np.asarray([1.0 / 3.0, 1.0 / 3.0]))))
        return Certificate(self.descriptor.formulation_id, gap < 1.0e-8, {"analytic_root_gap": gap}, True)


def test_direct_and_residual_paths_recover_known_solutions_without_fallback() -> None:
    direct = run_direct(QuadraticAdapter(), seed=1729)
    residual = run_residual(LinearResidualAdapter(), seed=1729)

    assert direct.selected.vector == pytest.approx([0.25, 0.75], abs=1.0e-9)
    assert residual.selected.vector == pytest.approx([1.0 / 3.0, 1.0 / 3.0], abs=1.0e-9)
    assert direct.certificate.accepted
    assert residual.certificate.accepted
    assert direct.backend.ipopt_used is False
    assert residual.backend.ipopt_used is False
    assert direct.backend.ipopt_available is False
    assert residual.backend.ipopt_available is False
    assert direct.backend.fallback_used is False
    assert residual.backend.fallback_used is False
    assert "excluded" in direct.backend.availability_note


def test_seeded_multistart_receipt_is_deterministic() -> None:
    first = run_direct(QuadraticAdapter(), seed=20260713)
    second = run_direct(QuadraticAdapter(), seed=20260713)

    assert first == second


def test_analytic_direct_gradient_and_residual_jacobian_match_central_differences() -> None:
    direct_receipt = check_direct_derivatives(QuadraticAdapter().build(), np.asarray([0.4, 0.6]))
    residual_receipt = check_residual_derivatives(LinearResidualAdapter().build(), np.asarray([0.4, 0.6]))

    assert direct_receipt.max_abs_error < 1.0e-9
    assert residual_receipt.max_abs_error < 1.0e-9


def test_wrong_derivatives_are_detected_independently() -> None:
    direct = QuadraticAdapter().build()
    wrong_direct = DirectProblem(direct.descriptor, direct.domain, direct.objective, lambda vector: vector)
    residual = LinearResidualAdapter().build()
    wrong_residual = ResidualProblem(
        residual.descriptor,
        residual.domain,
        residual.residual,
        lambda _vector: np.eye(2),
    )

    assert check_direct_derivatives(wrong_direct, np.asarray([0.4, 0.6])).max_abs_error > 0.1
    assert check_residual_derivatives(wrong_residual, np.asarray([0.4, 0.6])).max_abs_error > 0.1


def test_numerical_kind_and_certificate_identity_must_match() -> None:
    with pytest.raises(TypeError, match="residual formulation"):
        run_residual(QuadraticAdapter(), seed=1)  # type: ignore[arg-type]

    class MismatchedCertificate(QuadraticAdapter):
        def certify(self, vector: np.ndarray) -> Certificate:
            return Certificate(RESIDUAL_ID, True, {}, True)

    with pytest.raises(ValueError, match="certificate formulation_id"):
        run_direct(MismatchedCertificate(), seed=1)

    class MismatchedProblem(QuadraticAdapter):
        def build(self) -> DirectProblem:
            problem = super().build()
            other = FormulationDescriptor(
                "manufactured.other-direct.v1",
                "other manufactured direct test",
                NumericalKind.DIRECT_MINIMIZATION,
            )
            return DirectProblem(other, problem.domain, problem.objective, problem.gradient)

    with pytest.raises(ValueError, match="problem formulation_id"):
        run_direct(MismatchedProblem(), seed=1)


@pytest.mark.parametrize(
    ("lower", "upper", "scale", "match"),
    [
        ([0.0], [0.0], [1.0], "increasing"),
        ([0.0], [1.0, 2.0], [1.0], "dimensions"),
        ([0.0], [1.0], [0.0], "scale"),
        ([0.0], [np.inf], [1.0], "finite"),
    ],
)
def test_invalid_domains_are_rejected(
    lower: list[float],
    upper: list[float],
    scale: list[float],
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        BoxDomain.from_sequences(lower, upper, scale)


def test_nonfinite_callbacks_and_start_dimension_are_rejected() -> None:
    bad_descriptor = QuadraticAdapter().descriptor
    domain = BoxDomain.from_sequences([0.0], [1.0], [1.0])

    @dataclass(frozen=True)
    class BadAdapter(DirectAdapter):
        descriptor: FormulationDescriptor = bad_descriptor

        def build(self) -> DirectProblem:
            return DirectProblem(self.descriptor, domain, lambda _vector: np.nan, lambda _vector: np.asarray([0.0]))

        def starts(self, seed: int) -> tuple[np.ndarray, ...]:
            return (np.asarray([0.5]),)

        def certify(self, vector: np.ndarray) -> Certificate:
            return Certificate(self.descriptor.formulation_id, True, {}, False)

    with pytest.raises(ValueError, match="finite"):
        run_direct(BadAdapter(), seed=1)

    class BadStart(QuadraticAdapter):
        def starts(self, seed: int) -> tuple[np.ndarray, ...]:
            return (np.asarray([0.5]),)

    with pytest.raises(ValueError, match="start dimension"):
        run_direct(BadStart(), seed=1)


def test_family_certification_can_reject_a_lower_ordered_residual_root_without_masking_a_valid_root() -> None:
    descriptor = FormulationDescriptor(
        "manufactured.two-root.v1",
        "manufactured two-root topology test",
        NumericalKind.RESIDUAL_SOLVE,
    )

    class TwoRootAdapter(ResidualAdapter):
        def __init__(self) -> None:
            self.descriptor = descriptor

        def build(self) -> ResidualProblem:
            return ResidualProblem(
                self.descriptor,
                BoxDomain.from_sequences([0.0], [1.0], [1.0]),
                lambda vector: np.asarray([(vector[0] - 0.2) * (vector[0] - 0.8)]),
                lambda vector: np.asarray([[2.0 * vector[0] - 1.0]]),
            )

        def starts(self, seed: int) -> tuple[np.ndarray, ...]:
            return np.asarray([0.2]), np.asarray([0.8])

        def certify(self, vector: np.ndarray) -> Certificate:
            topology_valid = bool(vector[0] > 0.5)
            return Certificate(self.descriptor.formulation_id, topology_valid, {"topology_valid": topology_valid}, True)

    result = run_residual(TwoRootAdapter(), seed=1)

    assert result.selected.vector == pytest.approx([0.8])
    assert result.certificate.accepted
    assert sum(certificate is not None and certificate.accepted for certificate in result.candidate_certificates) == 1


def test_declared_variable_scale_is_used_in_the_direct_coordinate_step() -> None:
    descriptor = FormulationDescriptor(
        "manufactured.scaled-direct.v1",
        "manufactured scaled direct test",
        NumericalKind.DIRECT_MINIMIZATION,
    )
    target = 2.5e5
    scale = 1.0e6

    class ScaledAdapter(DirectAdapter):
        def __init__(self) -> None:
            self.descriptor = descriptor

        def build(self) -> DirectProblem:
            return DirectProblem(
                self.descriptor,
                BoxDomain.from_sequences([0.0], [scale], [scale]),
                lambda vector: float(((vector[0] - target) / scale) ** 2),
                lambda vector: np.asarray([2.0 * (vector[0] - target) / scale**2]),
            )

        def starts(self, seed: int) -> tuple[np.ndarray, ...]:
            return (np.asarray([9.0e5]),)

        def certify(self, vector: np.ndarray) -> Certificate:
            gap = abs(float(vector[0] - target))
            return Certificate(self.descriptor.formulation_id, gap < 1.0e-3, {"analytic_gap": gap}, True)

    result = run_direct(ScaledAdapter(), seed=1, max_iterations=10)

    assert result.selected.vector == pytest.approx([target], abs=1.0e-3)
    assert result.certificate.accepted


def test_declared_objective_and_residual_scales_make_unit_changes_iteration_invariant() -> None:
    class ObjectiveScaledAdapter(QuadraticAdapter):
        def __init__(self, multiplier: float) -> None:
            self.multiplier = multiplier

        def build(self) -> DirectProblem:
            base = super().build()
            return DirectProblem(
                base.descriptor,
                base.domain,
                lambda vector: self.multiplier * base.objective(vector),
                lambda vector: self.multiplier * base.gradient(vector),
                objective_scale=self.multiplier,
            )

    class RowScaledAdapter(LinearResidualAdapter):
        def __init__(self, multipliers: tuple[float, float]) -> None:
            self.multipliers = np.asarray(multipliers)

        def build(self) -> ResidualProblem:
            base = super().build()
            return ResidualProblem(
                base.descriptor,
                base.domain,
                lambda vector: self.multipliers * base.residual(vector),
                lambda vector: self.multipliers[:, np.newaxis] * base.jacobian(vector),
                residual_scale=tuple(float(value) for value in self.multipliers),
            )

    direct_unit = run_direct(ObjectiveScaledAdapter(1.0), seed=17)
    direct_converted = run_direct(ObjectiveScaledAdapter(1.0e6), seed=17)
    residual_unit = run_residual(RowScaledAdapter((1.0, 1.0)), seed=17)
    residual_converted = run_residual(RowScaledAdapter((1.0e-7, 1.0e8)), seed=17)

    assert direct_converted.selected.vector == pytest.approx(direct_unit.selected.vector, abs=1.0e-12)
    assert direct_converted.selected.iterations == direct_unit.selected.iterations
    assert direct_converted.selected.projected_gradient_inf_norm == pytest.approx(
        direct_unit.selected.projected_gradient_inf_norm,
        abs=1.0e-15,
    )
    assert residual_converted.selected.vector == pytest.approx(residual_unit.selected.vector, abs=1.0e-12)
    assert residual_converted.selected.iterations == residual_unit.selected.iterations


def test_invalid_objective_and_residual_scales_are_rejected() -> None:
    direct = QuadraticAdapter().build()
    residual = LinearResidualAdapter().build()

    with pytest.raises(ValueError, match="objective_scale"):
        DirectProblem(direct.descriptor, direct.domain, direct.objective, direct.gradient, objective_scale=0.0)
    with pytest.raises(ValueError, match="residual_scale"):
        ResidualProblem(
            residual.descriptor,
            residual.domain,
            residual.residual,
            residual.jacobian,
            residual_scale=(1.0, -1.0),
        )

    wrong_length = ResidualProblem(
        residual.descriptor,
        residual.domain,
        residual.residual,
        residual.jacobian,
        residual_scale=(1.0,),
    )
    with pytest.raises(ValueError, match="length"):
        run_residual(
            type(
                "WrongScaleAdapter",
                (LinearResidualAdapter,),
                {"build": lambda self: wrong_length},
            )(),
            seed=1,
        )


def test_convergence_summary_classifies_every_candidate_and_certificate() -> None:
    receipts = (run_direct(QuadraticAdapter(), seed=9), run_residual(LinearResidualAdapter(), seed=9))
    summary = summarize_convergence(receipts)

    assert len(summary.classifications) == sum(len(receipt.candidates) for receipt in receipts)
    assert summary.accepted_count == len(summary.classifications)
    assert summary.rejected_count == 0
    assert summary.not_converged_count == 0
    assert {item.outcome for item in summary.classifications} == {CandidateOutcome.ACCEPTED}
