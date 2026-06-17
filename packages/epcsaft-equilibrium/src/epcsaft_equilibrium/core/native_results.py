"""Internal conversion helpers for native equilibrium payloads."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

import numpy as np

from epcsaft import SolutionError

_ROUTE_STRING_DIAGNOSTIC_KEYS = (
    "solver_status",
    "application_status",
    "rejection_reason",
    "last_callback_exception",
    "problem_name",
    "adapter_kind",
    "activation_compiler",
    "variable_model",
    "density_backend",
    "gradient_approximation",
    "jacobian_approximation",
    "hessian_approximation",
    "hessian_backend",
    "route_refinement_kind",
    "residual_derivative_backend",
    "option_profile",
    "solver_acceptance_policy",
    "exact_hessian_policy",
    "scaling_contract",
    "residual_scaling_policy",
    "linear_solver_policy",
    "barrier_policy",
    "scaling_method",
    "linear_solver_requested",
    "linear_solver_selected",
)

_ROUTE_BOOL_DIAGNOSTIC_KEYS = (
    "exact_gradient_required",
    "exact_jacobian_required",
    "exact_hessian_available",
    "warm_start_requested",
    "warm_start_used",
    "solver_accepted",
    "solver_feasible_point",
    "postsolve_accepted",
    "residual_exact_jacobian_available",
    "residual_exact_hessian_available",
    "scaled_acceptance_passed",
    "profile_exact_hessian_gate",
    "variable_scaling_quality_passed",
    "constraint_scaling_quality_passed",
    "restoration_phase_observed",
)

_ROUTE_INT_DIAGNOSTIC_KEYS = (
    "max_iterations",
    "acceptable_iteration_limit",
    "iteration_count",
    "iteration_history_limit",
    "iteration_history_size",
    "requested_phase_count",
    "ipopt_print_level",
    "variable_scaling_count",
    "constraint_scaling_count",
    "eval_h_calls",
    "active_lower_bound_count",
    "active_upper_bound_count",
    "active_variable_bound_count",
    "step_trial_count_max",
)

_ROUTE_FLOAT_DIAGNOSTIC_KEYS = (
    "objective_scaling",
    "acceptable_tolerance",
    "constraint_violation_tolerance",
    "ipopt_unscaled_constraint_violation_tolerance",
    "dual_infeasibility_tolerance",
    "complementarity_tolerance",
    "variable_scaling_min",
    "variable_scaling_max",
    "constraint_scaling_min",
    "constraint_scaling_max",
    "scaled_constraint_violation_inf_norm",
    "scaled_stationarity_inf_norm",
    "scaled_complementarity_inf_norm",
    "bound_complementarity_inf_norm",
    "barrier_parameter_final",
    "regularization_size_final",
    "regularization_size_max",
    "bound_push",
    "bound_frac",
)

_ROUTE_SEQUENCE_DIAGNOSTIC_KEYS = (
    "residual_families",
    "constraint_families",
    "requested_phase_kinds",
)

_ROUTE_MAPPING_DIAGNOSTIC_KEYS = (
    "activation_plan",
    "variable_layout",
)

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
    "physical_evidence",
)


def _approximation_is_exact(value: Any) -> bool:
    return str(value).strip().lower() == "exact"


def _diagnostic_sequence(value: Any) -> list[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        return []
    return list(value)


def _normalized_seed_attempts(
    attempts: Any,
    *,
    selected_seed_name: str,
    gradient_approximation: str,
    jacobian_approximation: str,
    hessian_approximation: str,
    exact_gradient_required: bool,
    exact_jacobian_required: bool,
    exact_hessian_available: bool,
) -> list[Any]:
    normalized: list[Any] = []
    for attempt in attempts:
        if not isinstance(attempt, Mapping):
            normalized.append(attempt)
            continue
        row = dict(attempt)
        row["route_status"] = str(row.get("status", ""))
        row["route_accepted"] = bool(row.get("accepted", False))
        row["solver_accepted"] = bool(row.get("solver_accepted", False))
        row["selected_seed"] = bool(selected_seed_name) and str(row.get("seed_name", "")) == selected_seed_name
        row["gradient_approximation"] = gradient_approximation
        row["jacobian_approximation"] = jacobian_approximation
        row["hessian_approximation"] = hessian_approximation
        row["exact_gradient_required"] = exact_gradient_required
        row["exact_jacobian_required"] = exact_jacobian_required
        row["exact_hessian_available"] = exact_hessian_available
        row["gradient_is_exact"] = _approximation_is_exact(gradient_approximation)
        row["jacobian_is_exact"] = _approximation_is_exact(jacobian_approximation)
        row["hessian_is_exact"] = _approximation_is_exact(hessian_approximation)
        normalized.append(row)
    return normalized


def _diagnostics(payload: Mapping[str, Any]) -> dict[str, Any]:
    diagnostics = payload.get("diagnostics", {})
    if isinstance(diagnostics, Mapping):
        return dict(diagnostics)
    return {}


def _route_physical_evidence(route: Mapping[str, Any]) -> dict[str, Any]:
    evidence = route.get("physical_evidence", {})
    return dict(evidence) if isinstance(evidence, Mapping) else {}


def native_route_phase_labels(route: Mapping[str, Any], route_label: str) -> tuple[str, ...]:
    """Return phase labels owned by the native route evidence payload."""
    evidence = _route_physical_evidence(route)
    labels = evidence.get("phase_labels", route.get("phase_labels", ()))
    if not isinstance(labels, Sequence) or isinstance(labels, (str, bytes)):
        raise SolutionError(f"Native neutral {route_label} route returned invalid phase labels.")
    out = tuple(str(label) for label in labels)
    if not out:
        raise SolutionError(f"Native neutral {route_label} route did not return phase labels.")
    return out


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
    stability_accepted = (
        bool(stability_payload.get("accepted", stability_payload.get("stability_accepted", False)))
        if stability_payload is not None
        else False
    )
    candidate_set_complete = (
        bool(stability_payload.get("candidate_set_complete", stability_payload.get("candidate_completeness_accepted", False)))
        if stability_payload is not None
        else False
    )
    raw_stability_certificate = diagnostics.get("stability_certificate", "")
    if isinstance(raw_stability_certificate, Mapping):
        certificate_status = str(raw_stability_certificate.get("status", diagnostics.get("phase_set_status", "")))
        local_postsolve_only = (
            str(raw_stability_certificate.get("method", "")) == "postsolve_local_only"
            and (
                certificate_status == "not_required"
                or bool(diagnostics.get("stability_checked", True)) is False
            )
        )
    else:
        local_postsolve_only = (
            str(raw_stability_certificate) == "postsolve_local_only"
            and str(diagnostics.get("phase_set_status", "")) == "not_required"
        )
    reported_stability_checked = False if local_postsolve_only else stability_checked
    reported_stability_accepted = (
        bool(diagnostics.get("stability_accepted", stability_accepted))
        if local_postsolve_only
        else stability_accepted
    )
    reported_candidate_set_complete = (
        bool(diagnostics.get("candidate_completeness_accepted", candidate_set_complete))
        if local_postsolve_only
        else candidate_set_complete
    )
    failure_reason = str(
        diagnostics.get(
            "failure_reason",
            diagnostics.get("rejection_reason", "" if route_accepted and postsolve_accepted else diagnostics.get("route_status", "")),
        )
    )

    if not route_accepted:
        status = str(diagnostics.get("route_status", "route_rejected"))
    elif not postsolve_accepted:
        status = "postsolve_rejected"
    elif local_postsolve_only:
        status = str(diagnostics.get("route_status", "accepted"))
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
        and (local_postsolve_only or (stability_checked and stability_accepted and candidate_set_complete)),
        "status": status,
        "route_accepted": route_accepted,
        "postsolve_accepted": postsolve_accepted,
        "solver_accepted": solver_accepted,
        "stability_checked": reported_stability_checked,
        "stability_accepted": reported_stability_accepted,
        "candidate_set_complete": reported_candidate_set_complete,
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


def with_postsolve_certification(diagnostics: Mapping[str, Any]) -> dict[str, Any]:
    """Return diagnostics with the shared postsolve-certification summary attached."""
    payload = dict(diagnostics)
    payload["postsolve_certification"] = _postsolve_certification_summary(payload)
    return payload


def native_route_diagnostics(
    route: Mapping[str, Any],
    *,
    route_status_key: str = "route_status",
    defaults: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return diagnostics for a native route acceptance gate."""
    postsolve = route.get("postsolve", {})
    diagnostics = dict(postsolve) if isinstance(postsolve, Mapping) else {}
    physical_evidence = _route_physical_evidence(route)
    if physical_evidence:
        diagnostics["physical_evidence"] = physical_evidence
        for key in ("phase_labels", "phase_roles"):
            if key in physical_evidence:
                diagnostics[key] = _diagnostic_sequence(physical_evidence[key])
    default_values = dict(defaults or {})
    diagnostics[route_status_key] = str(route.get("status", default_values.get("status", "")))
    diagnostics["solver_backend"] = str(route.get("backend", default_values.get("solver_backend", "")))
    for key in _ROUTE_STRING_DIAGNOSTIC_KEYS:
        if key in route or key in default_values:
            diagnostics[key] = str(route.get(key, default_values.get(key, "")))
    for key in _ROUTE_BOOL_DIAGNOSTIC_KEYS:
        if key in route or key in default_values:
            diagnostics[key] = bool(route.get(key, default_values.get(key, False)))
    for key in _ROUTE_INT_DIAGNOSTIC_KEYS:
        if key in route or key in default_values:
            diagnostics[key] = int(route.get(key, default_values.get(key, 0)))
    for key in _ROUTE_FLOAT_DIAGNOSTIC_KEYS:
        if key in route or key in default_values:
            diagnostics[key] = float(route.get(key, default_values.get(key, 0.0)))
    for key in _ROUTE_SEQUENCE_DIAGNOSTIC_KEYS:
        if key in route or key in default_values:
            diagnostics[key] = _diagnostic_sequence(route.get(key, default_values.get(key, ())))
    for key in _ROUTE_MAPPING_DIAGNOSTIC_KEYS:
        if key in route or key in default_values:
            value = route.get(key, default_values.get(key, {}))
            diagnostics[key] = dict(value) if isinstance(value, Mapping) else value
    if "compiled" in route or "compiled" in default_values:
        diagnostics["compiled"] = bool(route.get("compiled", default_values.get("compiled", False)))
    if "adapter_available" in route or "adapter_available" in default_values:
        diagnostics["adapter_available"] = bool(
            route.get("adapter_available", default_values.get("adapter_available", False))
        )
    if "ran" in route or "solver_ran" in default_values or "ran" in default_values:
        diagnostics["solver_ran"] = bool(
            route.get("ran", default_values.get("solver_ran", default_values.get("ran", False)))
        )
    diagnostics["route_accepted"] = bool(
        route.get("accepted", diagnostics.get("accepted", default_values.get("accepted", False)))
    )
    if "postsolve_accepted" not in diagnostics and "accepted" in diagnostics:
        diagnostics["postsolve_accepted"] = bool(diagnostics["accepted"])
    if "initial_point_strategy" in route or "initial_point_strategy" in default_values:
        diagnostics["initial_point_strategy"] = str(
            route.get("initial_point_strategy", default_values.get("initial_point_strategy", ""))
        )
    if "seed_name" in route or "seed_name" in default_values:
        diagnostics["seed_name"] = str(route.get("seed_name", default_values.get("seed_name", "")))
    diagnostics["gradient_is_exact"] = _approximation_is_exact(diagnostics.get("gradient_approximation", ""))
    diagnostics["jacobian_is_exact"] = _approximation_is_exact(diagnostics.get("jacobian_approximation", ""))
    diagnostics["hessian_is_exact"] = _approximation_is_exact(diagnostics.get("hessian_approximation", ""))
    diagnostics["exact_derivatives_required"] = bool(
        diagnostics.get("exact_gradient_required", False) and diagnostics.get("exact_jacobian_required", False)
    )
    if "seed_attempts" in route:
        normalized_attempts = _normalized_seed_attempts(
            route.get("seed_attempts", []),
            selected_seed_name=str(diagnostics.get("seed_name", "")),
            gradient_approximation=str(diagnostics.get("gradient_approximation", "")),
            jacobian_approximation=str(diagnostics.get("jacobian_approximation", "")),
            hessian_approximation=str(diagnostics.get("hessian_approximation", "")),
            exact_gradient_required=bool(diagnostics.get("exact_gradient_required", False)),
            exact_jacobian_required=bool(diagnostics.get("exact_jacobian_required", False)),
            exact_hessian_available=bool(diagnostics.get("exact_hessian_available", False)),
        )
        diagnostics["seed_attempts"] = normalized_attempts
        diagnostics["seed_attempt_count"] = len(normalized_attempts)
        diagnostics["seed_attempt_solver_accepted_count"] = sum(
            1
            for attempt in normalized_attempts
            if isinstance(attempt, Mapping) and bool(attempt.get("solver_accepted", False))
        )
        diagnostics["seed_attempt_route_accepted_count"] = sum(
            1
            for attempt in normalized_attempts
            if isinstance(attempt, Mapping) and bool(attempt.get("route_accepted", False))
        )
    if "iteration_history" in route:
        diagnostics["iteration_history"] = list(route.get("iteration_history", []))
    if "continuation_state" in route:
        state = route.get("continuation_state", {})
        diagnostics["continuation_state"] = dict(state) if isinstance(state, Mapping) else state
    for key in _STABILITY_EVIDENCE_KEYS:
        if key in route:
            value = route.get(key)
            diagnostics[key] = dict(value) if isinstance(value, Mapping) else value
    return with_postsolve_certification(diagnostics)


def raise_native_route_rejected(
    route: Mapping[str, Any],
    message: str,
    *,
    route_status_key: str = "route_status",
    defaults: Mapping[str, Any] | None = None,
) -> None:
    """Raise a SolutionError with the shared native route diagnostics shape."""
    raise SolutionError(
        message,
        native_route_diagnostics(route, route_status_key=route_status_key, defaults=defaults),
    )


def equilibrium_route_diagnostics(
    route: Mapping[str, str], diagnostics: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Return public equilibrium-route diagnostics merged into an existing payload."""
    payload = dict(diagnostics or {})
    payload["equilibrium_route"] = str(route["route"])
    payload["route_reason"] = str(route["reason"])
    return payload


def with_equilibrium_route_diagnostics(result: Any, route: Mapping[str, str]) -> Any:
    """Return a public equilibrium result with canonical route diagnostics."""
    return replace(result, diagnostics=equilibrium_route_diagnostics(route, getattr(result, "diagnostics", None)))


def raise_with_equilibrium_route_diagnostics(exc: SolutionError, route: Mapping[str, str]) -> None:
    """Raise a SolutionError with canonical public route diagnostics."""
    raise SolutionError(
        exc.message,
        equilibrium_route_diagnostics(route, getattr(exc, "diagnostics", None)),
    ) from exc


def _phase_payload_to_public(phase: Mapping[str, Any], *, label: str | None = None):
    from ..workflows import EquilibriumPhase

    ln_fugacity = phase.get("ln_fugacity_coefficient")
    fugacity = phase.get("fugacity_coefficient")
    return EquilibriumPhase(
        str(phase["label"] if label is None else label),
        composition=np.asarray(phase["composition"], dtype=float),
        density=float(phase["density"]),
        temperature=float(phase["temperature"]),
        pressure=float(phase["pressure"]),
        phase_fraction=float(phase["phase_fraction"]),
        ln_fugacity_coefficient=None if ln_fugacity is None else np.asarray(ln_fugacity, dtype=float),
        fugacity_coefficient=None if fugacity is None else np.asarray(fugacity, dtype=float),
        diagnostics=_diagnostics(phase),
    )


def neutral_phase_payload_to_result(
    payload: Mapping[str, Any],
    *,
    problem_kind: str | None = None,
    phase_labels: Sequence[str] | None = None,
):
    """Convert an accepted native neutral phase payload into public dataclasses."""
    from ..workflows import EquilibriumResult

    diagnostics = _diagnostics(payload)
    if not bool(payload.get("accepted", False)):
        reason = str(payload.get("rejection_reason", diagnostics.get("rejection_reason", "native_rejected")))
        if "rejection_reason" not in diagnostics:
            diagnostics["rejection_reason"] = reason
        raise SolutionError(f"Native neutral two-phase EOS result was rejected: {reason}", diagnostics)

    phases_raw = payload.get("phases", ())
    if not isinstance(phases_raw, Sequence) or isinstance(phases_raw, (str, bytes)):
        raise SolutionError("Native neutral two-phase EOS result did not contain a phase sequence.", diagnostics)
    if phase_labels is not None and len(phase_labels) != len(phases_raw):
        raise SolutionError(
            "Native neutral two-phase EOS result label count did not match phase payloads.", diagnostics
        )
    labels = [None] * len(phases_raw) if phase_labels is None else list(phase_labels)
    phases = tuple(_phase_payload_to_public(phase, label=labels[index]) for index, phase in enumerate(phases_raw))
    if not phases:
        raise SolutionError("Native neutral two-phase EOS result accepted without phase payloads.", diagnostics)

    resolved_problem_kind = (
        payload.get("problem_kind", "neutral_two_phase_eos") if problem_kind is None else problem_kind
    )
    return EquilibriumResult(
        backend=str(payload.get("backend", "native_equilibrium_nlp")),
        problem_kind=str(resolved_problem_kind),
        phases=phases,
        stable=bool(payload.get("stable", False)),
        split_detected=bool(payload.get("split_detected", True)),
        diagnostics=diagnostics,
    )


def native_route_summed_phase_amounts(route: Mapping[str, Any], ncomp: int, route_label: str) -> np.ndarray:
    """Return the positive feed implied by a native two-phase route result."""
    try:
        phase_amounts = np.asarray(route["phase_amounts"], dtype=float)
    except (KeyError, TypeError, ValueError) as exc:
        raise SolutionError(f"Native neutral {route_label} route did not return phase amounts.") from exc
    if phase_amounts.ndim != 2 or phase_amounts.shape[1] != int(ncomp):
        raise SolutionError(f"Native neutral {route_label} route phase amounts had an invalid shape.")
    feed = np.sum(phase_amounts, axis=0)
    if not np.all(np.isfinite(feed)) or np.any(feed <= 0.0):
        raise SolutionError(f"Native neutral {route_label} route phase amounts did not define a positive feed.")
    return feed


def native_route_solved_pressure(route: Mapping[str, Any], route_label: str) -> float:
    """Return the final pressure variable from a native fixed-temperature route."""
    try:
        variables = np.asarray(route["variables"], dtype=float).flatten()
    except (KeyError, TypeError, ValueError) as exc:
        raise SolutionError(f"Native neutral {route_label} route did not return solver variables.") from exc
    if variables.size == 0:
        raise SolutionError(f"Native neutral {route_label} route returned no solver variables.")
    pressure = float(variables[-1])
    if not np.isfinite(pressure) or pressure <= 0.0:
        raise SolutionError(f"Native neutral {route_label} route must be a finite positive P value.")
    return pressure


def native_route_solved_temperature(route: Mapping[str, Any], route_label: str) -> float:
    """Return the final temperature variable from a native fixed-pressure route."""
    try:
        variables = np.asarray(route["variables"], dtype=float).flatten()
    except (KeyError, TypeError, ValueError) as exc:
        raise SolutionError(f"Native neutral {route_label} route did not return solver variables.") from exc
    if variables.size == 0:
        raise SolutionError(f"Native neutral {route_label} route returned no solver variables.")
    temperature = float(variables[-1])
    if not np.isfinite(temperature) or temperature <= 0.0:
        raise SolutionError(f"Native neutral {route_label} route must be a finite positive T value.")
    return temperature
