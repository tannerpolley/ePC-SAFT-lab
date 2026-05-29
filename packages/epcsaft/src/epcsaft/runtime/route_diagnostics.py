"""Provider-owned typed views over public route diagnostics payloads."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

_RESIDUAL_EVIDENCE_KEYS = (
    "ln_fugacity_consistency_norm",
    "chemical_potential_consistency_norm",
    "neutral_fugacity_residual_norm",
    "salt_pair_fugacity_residual_norm",
    "mean_ionic_fugacity_residual_norm",
)

_CONSTRAINT_EVIDENCE_KEYS = (
    "material_balance_norm",
    "pressure_consistency_norm",
    "charge_balance_norm",
    "phase_distance",
)

_ADMISSIBILITY_EVIDENCE_KEYS = (
    "phase_distance",
    "density_backend",
    "density_recompute_relative_errors",
)

_PHASE_ELIGIBILITY_EVIDENCE_KEYS = (
    "phase_eligibility_mask_available",
    "phase_eligibility_mask",
    "phase_eligibility_shape",
)

_STABILITY_EVIDENCE_KEYS = (
    "tpdf_stability",
    "stability_certificate",
)


@dataclass(frozen=True, slots=True)
class RouteDiagnosticsView:
    """Read-only typed view over serialized route diagnostics."""

    diagnostics: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "diagnostics", dict(self.diagnostics or {}))

    @property
    def route_status(self) -> str:
        """Return the route status token, including reactive-specialized payloads."""
        return str(
            self.diagnostics.get(
                "route_status",
                self.diagnostics.get("reactive_route_status", self.diagnostics.get("equilibrium_route", "")),
            )
        )

    @property
    def solver_backend(self) -> str:
        """Return the native solver backend token when present."""
        return str(self.diagnostics.get("solver_backend", self.diagnostics.get("backend", "")))

    @property
    def route_accepted(self) -> bool:
        """Return whether the outer route accepted the result."""
        return bool(self.diagnostics.get("route_accepted", self.diagnostics.get("accepted", False)))

    @property
    def postsolve_accepted(self) -> bool:
        """Return whether postsolve certification accepted the route."""
        return bool(self.diagnostics.get("postsolve_accepted", self.diagnostics.get("accepted", False)))

    @property
    def postsolve_certification(self) -> Mapping[str, Any]:
        """Return the normalized route certification summary."""
        summary = self.diagnostics.get("postsolve_certification", {})
        if isinstance(summary, Mapping):
            return dict(summary)
        return _postsolve_certification_summary(self.diagnostics)

    @property
    def certification_status(self) -> str:
        """Return the normalized route certification status token."""
        return str(self.postsolve_certification.get("status", ""))

    @property
    def postsolve_certification_accepted(self) -> bool:
        """Return whether the shared certification summary accepted the route."""
        return bool(self.postsolve_certification.get("accepted", False))

    @property
    def stability_checked(self) -> bool:
        """Return whether route diagnostics include stability-certificate evidence."""
        return bool(self.postsolve_certification.get("stability_checked", False))

    @property
    def gradient_is_exact(self) -> bool:
        """Return whether the route reports exact gradients."""
        return bool(
            self.diagnostics.get(
                "gradient_is_exact",
                _approximation_is_exact(self.diagnostics.get("gradient_approximation", "")),
            )
        )

    @property
    def jacobian_is_exact(self) -> bool:
        """Return whether the route reports exact Jacobians."""
        return bool(
            self.diagnostics.get(
                "jacobian_is_exact",
                _approximation_is_exact(self.diagnostics.get("jacobian_approximation", "")),
            )
        )

    @property
    def hessian_is_exact(self) -> bool:
        """Return whether the route reports an exact Hessian path."""
        return bool(
            self.diagnostics.get(
                "hessian_is_exact",
                _approximation_is_exact(self.diagnostics.get("hessian_approximation", "")),
            )
        )

    @property
    def exact_derivatives_required(self) -> bool:
        """Return whether exact gradient and Jacobian routes were required."""
        return bool(
            self.diagnostics.get(
                "exact_derivatives_required",
                bool(self.diagnostics.get("exact_gradient_required", False))
                and bool(self.diagnostics.get("exact_jacobian_required", False)),
            )
        )

    @property
    def residual_families(self) -> tuple[str, ...]:
        """Return active residual families."""
        return tuple(str(item) for item in _diagnostic_sequence(self.diagnostics.get("residual_families", ())))

    @property
    def constraint_families(self) -> tuple[str, ...]:
        """Return active hard-constraint families."""
        return tuple(str(item) for item in _diagnostic_sequence(self.diagnostics.get("constraint_families", ())))

    @property
    def selected_seed_name(self) -> str:
        """Return the selected deterministic seed name."""
        return str(self.diagnostics.get("seed_name", ""))

    @property
    def seed_attempts(self) -> tuple[Mapping[str, Any], ...]:
        """Return normalized seed-attempt rows."""
        attempts = self.diagnostics.get("seed_attempts", ())
        return tuple(
            dict(item) if isinstance(item, Mapping) else {"value": item} for item in _diagnostic_sequence(attempts)
        )

    @property
    def seed_attempt_count(self) -> int:
        """Return the reported seed-attempt count."""
        return int(self.diagnostics.get("seed_attempt_count", len(self.seed_attempts)))

    def to_dict(self) -> dict[str, Any]:
        """Return a copy of the underlying diagnostics payload."""
        return dict(self.diagnostics)


def _approximation_is_exact(value: Any) -> bool:
    return str(value).strip().lower() == "exact"


def _diagnostic_sequence(value: Any) -> list[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        return []
    return list(value)


def _has_any_key(diagnostics: Mapping[str, Any], keys: tuple[str, ...]) -> bool:
    return any(key in diagnostics for key in keys)


def _stability_evidence(diagnostics: Mapping[str, Any]) -> tuple[str, Mapping[str, Any] | None]:
    for key in _STABILITY_EVIDENCE_KEYS:
        payload = diagnostics.get(key)
        if isinstance(payload, Mapping):
            return key, payload
    return "", None


def _postsolve_certification_summary(diagnostics: Mapping[str, Any]) -> dict[str, Any]:
    route_accepted = bool(diagnostics.get("route_accepted", diagnostics.get("accepted", False)))
    postsolve_accepted = bool(diagnostics.get("postsolve_accepted", diagnostics.get("accepted", False)))
    solver_accepted = bool(diagnostics.get("solver_accepted", False))
    stability_source, stability_payload = _stability_evidence(diagnostics)
    stability_checked = stability_payload is not None
    stability_accepted = bool(stability_payload.get("accepted", False)) if stability_payload is not None else False
    candidate_set_complete = (
        bool(stability_payload.get("candidate_set_complete", False)) if stability_payload is not None else False
    )
    failure_reason = str(
        diagnostics.get(
            "failure_reason",
            diagnostics.get(
                "rejection_reason",
                "" if route_accepted and postsolve_accepted else diagnostics.get("route_status", ""),
            ),
        )
    )

    if not route_accepted:
        status = str(diagnostics.get("route_status", "route_rejected"))
    elif not postsolve_accepted:
        status = "postsolve_rejected"
    elif not stability_checked:
        status = "optimizer_converged_uncertified"
    elif not stability_accepted:
        status = "unstable"
    elif not candidate_set_complete:
        status = "optimizer_converged_uncertified"
    else:
        status = str(diagnostics.get("route_status", "production_accepted"))

    out = {
        "accepted": route_accepted
        and postsolve_accepted
        and stability_checked
        and stability_accepted
        and candidate_set_complete,
        "status": status,
        "route_accepted": route_accepted,
        "postsolve_accepted": postsolve_accepted,
        "solver_accepted": solver_accepted,
        "stability_checked": stability_checked,
        "stability_accepted": stability_accepted,
        "candidate_set_complete": candidate_set_complete,
        "stability_source": stability_source,
        "failure_reason": "" if status in {"accepted", "production_accepted"} else failure_reason,
        "active_residuals_reported": bool(diagnostics.get("residual_families"))
        or _has_any_key(diagnostics, _RESIDUAL_EVIDENCE_KEYS),
        "hard_constraints_reported": bool(diagnostics.get("constraint_families"))
        or _has_any_key(diagnostics, _CONSTRAINT_EVIDENCE_KEYS),
        "physical_admissibility_reported": _has_any_key(diagnostics, _ADMISSIBILITY_EVIDENCE_KEYS),
        "phase_eligibility_reported": _has_any_key(diagnostics, _PHASE_ELIGIBILITY_EVIDENCE_KEYS),
    }
    if stability_payload is not None:
        for key in (
            "method",
            "phase_discovery_backend",
            "phase_distance",
            "min_tpd",
            "candidate_mass_balance_norm",
            "tpd_candidate_count",
            "unique_candidate_count",
            "selected_candidate_count",
            "stage9_phase_discovery_steps",
            "deterministic_screening_status",
            "deterministic_screening_is_full_held",
            "deterministic_candidate_count",
            "continuous_tpd_status",
            "continuous_tpd_backend",
            "continuous_tpd_start_count",
            "continuous_tpd_solve_count",
            "continuous_tpd_converged_count",
            "continuous_tpd_iteration_count_total",
            "continuous_tpd_iteration_count_max",
            "continuous_tpd_min",
            "continuous_tpd_step_final_max",
            "held_stage_i_status",
            "held_stage_i_start_count",
            "held_stage_i_negative_tpd_found",
            "held_stage_i_min_tpd",
            "held_stage_ii_status",
            "held_stage_ii_candidate_count",
            "held_stage_iii_status",
            "held_stage_iii_refined_phase_count",
        ):
            if key in stability_payload:
                out[key] = stability_payload[key]
    return out


__all__ = ["RouteDiagnosticsView"]
