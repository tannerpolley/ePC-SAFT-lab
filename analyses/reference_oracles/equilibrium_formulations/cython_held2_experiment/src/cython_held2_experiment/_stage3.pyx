# cython: language_level=3
"""Lab-only HELD2 Stage-III, certification, and tracing experiment."""

import math

import cyipopt
import numpy as np

from ._held2 import (
    _manufactured_stage2_phase,
    _stage2_phase_callback,
    manufactured_stage1_demo,
    manufactured_stage2_demo,
    modified_fraction,
    recover_explicit_composition,
    solve_stage1,
    solve_stage2,
)


_KKT_TOL = 1.0e-7
_FEASIBILITY_TOL = 1.0e-8
_COMPLEMENTARITY_TOL = 1.0e-8
_PRESSURE_TOL = 1.0e-8
_POTENTIAL_TOL = 1.0e-7
_MATERIAL_TOL = 1.0e-8
_CHARGE_TOL = 1.0e-13
_DISTINCT_TOL = 1.0e-3
_INACTIVE_BETA = 1.0e-8


def _stage3_structures(phase_count):
    count = int(phase_count)
    jacobian_rows = []
    jacobian_columns = []
    hessian_rows = []
    hessian_columns = []
    for phase in range(count):
        beta = phase
        u = count + phase
        q = 2 * count + phase
        jacobian_rows.extend((0, 1, 1))
        jacobian_columns.extend((beta, beta, u))
        hessian_rows.extend((u, q, u, q, q))
        hessian_columns.extend((beta, beta, u, u, q))
    return (
        np.asarray(jacobian_rows, dtype=int),
        np.asarray(jacobian_columns, dtype=int),
        np.asarray(hessian_rows, dtype=int),
        np.asarray(hessian_columns, dtype=int),
    )


def _physical_stage3_evaluation(
    point,
    feed_u,
    phase_evaluator,
    lagrange=None,
    objective_factor=1.0,
):
    values = np.asarray(point, dtype=float)
    if values.ndim != 1 or values.size % 3 != 0:
        raise ValueError("Stage-III point must contain beta, u, and q blocks")
    phase_count = values.size // 3
    beta = values[:phase_count]
    modified = values[phase_count:2 * phase_count]
    log_volume = values[2 * phase_count:]
    phases = [
        phase_evaluator((modified[index], log_volume[index]))
        for index in range(phase_count)
    ]

    objective = float(sum(
        beta[index] * float(phases[index]["phase_objective"])
        for index in range(phase_count)
    ))
    gradient = np.zeros(3 * phase_count, dtype=float)
    objective_hessian = np.zeros((3 * phase_count, 3 * phase_count), dtype=float)
    for index, phase in enumerate(phases):
        phase_gradient = np.asarray(phase["gradient"], dtype=float)
        phase_hessian = np.asarray(phase["hessian"], dtype=float)
        beta_index = index
        u_index = phase_count + index
        q_index = 2 * phase_count + index
        gradient[beta_index] = float(phase["phase_objective"])
        gradient[u_index] = beta[index] * phase_gradient[0]
        gradient[q_index] = beta[index] * phase_gradient[1]
        objective_hessian[u_index, beta_index] = phase_gradient[0]
        objective_hessian[beta_index, u_index] = phase_gradient[0]
        objective_hessian[q_index, beta_index] = phase_gradient[1]
        objective_hessian[beta_index, q_index] = phase_gradient[1]
        objective_hessian[u_index, u_index] = beta[index] * phase_hessian[0, 0]
        objective_hessian[q_index, u_index] = beta[index] * phase_hessian[1, 0]
        objective_hessian[u_index, q_index] = beta[index] * phase_hessian[0, 1]
        objective_hessian[q_index, q_index] = beta[index] * phase_hessian[1, 1]

    constraints = np.asarray((
        float(np.sum(beta) - 1.0),
        float(beta @ modified - float(feed_u)),
    ))
    jacobian = np.zeros((2, 3 * phase_count), dtype=float)
    jacobian[0, :phase_count] = 1.0
    jacobian[1, :phase_count] = modified
    jacobian[1, phase_count:2 * phase_count] = beta
    constraint_hessian = np.zeros_like(objective_hessian)
    for index in range(phase_count):
        constraint_hessian[phase_count + index, index] = 1.0
        constraint_hessian[index, phase_count + index] = 1.0

    multipliers = np.zeros(2, dtype=float) if lagrange is None else np.asarray(lagrange, dtype=float)
    if multipliers.shape != (2,):
        raise ValueError("Stage-III constraint multipliers must contain two values")
    lagrangian_gradient = (
        float(objective_factor) * gradient + jacobian.T @ multipliers
    )
    lagrangian_hessian = (
        float(objective_factor) * objective_hessian
        + multipliers[1] * constraint_hessian
    )
    return {
        "objective": objective,
        "gradient": gradient,
        "constraints": constraints,
        "jacobian": jacobian,
        "objective_hessian": objective_hessian,
        "hessian": lagrangian_hessian,
        "lagrangian_gradient": lagrangian_gradient,
        "phases": phases,
        "jacobian_nonzeros": 3 * phase_count,
        "hessian_lower_nonzeros": 5 * phase_count,
    }


def manufactured_stage3_evaluation(point, lagrange, objective_factor):
    return _physical_stage3_evaluation(
        point,
        0.5,
        _manufactured_stage2_phase,
        lagrange,
        objective_factor,
    )


def _chart_evaluation(chart, lower, scale, feed_u, phase_evaluator, lagrange=None, objective_factor=1.0):
    chart_values = np.asarray(chart, dtype=float)
    physical = lower + scale * chart_values
    evaluated = _physical_stage3_evaluation(
        physical,
        feed_u,
        phase_evaluator,
        lagrange,
        objective_factor,
    )
    chart_gradient = scale * np.asarray(evaluated["gradient"])
    chart_jacobian = np.asarray(evaluated["jacobian"]) * scale[np.newaxis, :]
    chart_hessian = (
        scale[:, np.newaxis] * np.asarray(evaluated["hessian"])
        * scale[np.newaxis, :]
    )
    result = dict(evaluated)
    result.update({
        "physical": physical,
        "gradient": chart_gradient,
        "jacobian": chart_jacobian,
        "hessian": chart_hessian,
    })
    return result


cdef class _StageThreeProblem:
    cdef object evaluator
    cdef object jacobian_rows
    cdef object jacobian_columns
    cdef object hessian_rows
    cdef object hessian_columns

    def __init__(self, evaluator, phase_count):
        self.evaluator = evaluator
        (
            self.jacobian_rows,
            self.jacobian_columns,
            self.hessian_rows,
            self.hessian_columns,
        ) = _stage3_structures(phase_count)

    def objective(self, x):
        return self.evaluator(x)["objective"]

    def gradient(self, x):
        return np.asarray(self.evaluator(x)["gradient"], dtype=float)

    def constraints(self, x):
        return np.asarray(self.evaluator(x)["constraints"], dtype=float)

    def jacobian(self, x):
        matrix = np.asarray(self.evaluator(x)["jacobian"], dtype=float)
        return matrix[self.jacobian_rows, self.jacobian_columns]

    def jacobianstructure(self):
        return self.jacobian_rows, self.jacobian_columns

    def hessian(self, x, lagrange, objective_factor):
        matrix = np.asarray(
            self.evaluator(x, lagrange, objective_factor)["hessian"],
            dtype=float,
        )
        return matrix[self.hessian_rows, self.hessian_columns]

    def hessianstructure(self):
        return self.hessian_rows, self.hessian_columns


def _initial_phase_fractions(modified, feed_u):
    values = np.asarray(modified, dtype=float)
    count = values.size
    if count < 2:
        raise ValueError("Stage III requires at least two candidate phases")
    order = np.argsort(values)
    lower_candidates = [index for index in order if values[index] <= feed_u]
    upper_candidates = [index for index in order if values[index] >= feed_u]
    if not lower_candidates or not upper_candidates:
        raise ValueError("candidate phases do not bracket the feed")
    left = lower_candidates[-1]
    right = upper_candidates[0]
    if left == right:
        alternatives = [index for index in order if index != left]
        if not alternatives:
            raise ValueError("candidate phase pool is degenerate")
        right = alternatives[-1] if values[alternatives[-1]] > feed_u else alternatives[0]
        left, right = sorted((left, right), key=lambda index: values[index])
    fractions = np.zeros(count, dtype=float)
    extra = [index for index in range(count) if index not in (left, right)]
    extra_fraction = min(0.02, 0.1 / max(1, len(extra)))
    for index in extra:
        fractions[index] = extra_fraction
    remaining = 1.0 - float(np.sum(fractions))
    remaining_feed = float(feed_u - fractions @ values)
    denominator = values[right] - values[left]
    if denominator <= 0.0:
        raise ValueError("candidate phase bracket is singular")
    fractions[right] = (remaining_feed - remaining * values[left]) / denominator
    fractions[left] = remaining - fractions[right]
    if np.any(fractions < 0.0):
        raise ValueError("candidate phase pool cannot initialize material balance")
    return fractions


def _stage3_bounds(phase_count, u_bounds, q_bounds):
    count = int(phase_count)
    lower = np.concatenate((
        np.zeros(count),
        np.full(count, float(u_bounds[0])),
        np.full(count, float(q_bounds[0])),
    ))
    upper = np.concatenate((
        np.ones(count),
        np.full(count, float(u_bounds[1])),
        np.full(count, float(q_bounds[1])),
    ))
    scale = upper - lower
    if np.any(scale <= 0.0):
        raise ValueError("Stage-III physical bounds must be increasing")
    return lower, upper, scale


def _phase_payload(candidate, beta, phase, lower_multiplier):
    u = float(phase["modified_fraction"])
    phase_gradient = np.asarray(phase["gradient"], dtype=float)
    phase_objective = float(phase["phase_objective"])
    modified_potentials = (
        phase_objective - u * phase_gradient[0],
        phase_objective + (1.0 - u) * phase_gradient[0],
    )
    return {
        "id": str(candidate["id"]),
        "beta": float(beta),
        "modified_fraction": u,
        "log_volume": float(phase["log_volume"]),
        "volume": float(phase.get("volume", math.exp(float(phase["log_volume"])))),
        "packing_fraction": float(phase["packing_fraction"]),
        "phase_objective": phase_objective,
        "modified_potentials": modified_potentials,
        "relative_pressure_residual": float(phase.get("relative_pressure_residual", 0.0)),
        "charge_residual": float(phase.get("charge_residual", 0.0)),
        "final_eos_evaluation": phase.get("final_eos_evaluation", "passed"),
        "beta_lower_multiplier": float(lower_multiplier),
    }


def _solve_stage3_once(
    phase_evaluator,
    feed_u,
    candidates,
    u_bounds,
    q_bounds,
    initial_physical=None,
):
    pool = tuple(dict(candidate) for candidate in candidates)
    count = len(pool)
    lower, upper, scale = _stage3_bounds(count, u_bounds, q_bounds)
    if initial_physical is None:
        modified = np.asarray([candidate["modified_fraction"] for candidate in pool])
        beta = _initial_phase_fractions(modified, float(feed_u))
        log_volume = np.asarray([candidate["log_volume"] for candidate in pool])
        physical_start = np.concatenate((beta, modified, log_volume))
    else:
        physical_start = np.asarray(initial_physical, dtype=float)
    chart_start = np.clip((physical_start - lower) / scale, 1.0e-10, 1.0 - 1.0e-10)

    def evaluator(chart, lagrange=None, objective_factor=1.0):
        return _chart_evaluation(
            chart,
            lower,
            scale,
            feed_u,
            phase_evaluator,
            lagrange,
            objective_factor,
        )

    problem = _StageThreeProblem(evaluator, count)
    solver = cyipopt.Problem(
        n=3 * count,
        m=2,
        problem_obj=problem,
        lb=np.zeros(3 * count),
        ub=np.ones(3 * count),
        cl=np.zeros(2),
        cu=np.zeros(2),
    )
    solver.add_option("print_level", 0)
    solver.add_option("sb", "yes")
    solver.add_option("hessian_approximation", "exact")
    solver.add_option("tol", 1.0e-10)
    solver.add_option("max_iter", 500)
    try:
        chart_solution, info = solver.solve(chart_start)
        constraint_multipliers = np.asarray(info.get("mult_g", np.zeros(2)), dtype=float)
        final = evaluator(chart_solution, constraint_multipliers, 1.0)
    except Exception as error:
        return {
            "outcome": "solver_failure",
            "solver_status": "failed",
            "numerical_status": "not_adjudicated",
            "physical_status": "not_adjudicated",
            "error": str(error),
            "phases": [],
            "inactive_ids": [],
        }

    physical = np.asarray(final["physical"], dtype=float)
    physical_base = _physical_stage3_evaluation(
        physical,
        feed_u,
        phase_evaluator,
        constraint_multipliers,
        1.0,
    )
    chart_lower = np.asarray(info.get("mult_x_L", np.zeros(3 * count)), dtype=float)
    chart_upper = np.asarray(info.get("mult_x_U", np.zeros(3 * count)), dtype=float)
    physical_lower = chart_lower / scale
    physical_upper = chart_upper / scale
    physical_stationarity = (
        np.asarray(physical_base["lagrangian_gradient"])
        - physical_lower
        + physical_upper
    )
    chart_stationarity = (
        np.asarray(final["gradient"])
        + np.asarray(final["jacobian"]).T @ constraint_multipliers
        - chart_lower
        + chart_upper
    )
    reconstruction = float(np.max(np.abs(
        chart_stationarity - scale * physical_stationarity
    )))
    sign_valid = bool(np.all(chart_lower >= -1.0e-12) and np.all(chart_upper >= -1.0e-12))
    dual_pullback_status = "passed" if sign_valid and reconstruction <= 1.0e-8 else "failed"
    stationarity_inf = float(np.max(np.abs(physical_stationarity)))
    feasibility_inf = float(np.max(np.abs(physical_base["constraints"])))
    complementarity_inf = float(max(
        np.max(np.abs((physical - lower) * physical_lower)),
        np.max(np.abs((upper - physical) * physical_upper)),
    ))
    numerical = bool(
        np.all(np.isfinite(physical))
        and stationarity_inf <= _KKT_TOL
        and feasibility_inf <= _FEASIBILITY_TOL
        and complementarity_inf <= _COMPLEMENTARITY_TOL
        and dual_pullback_status == "passed"
    )
    solver_passed = int(info.get("status", -999)) in (0, 1)
    beta = physical[:count]
    phases = [
        _phase_payload(pool[index], beta[index], physical_base["phases"][index], physical_lower[index])
        for index in range(count)
    ]
    inactive_ids = [
        phase["id"] for phase in phases
        if phase["beta"] <= _INACTIVE_BETA
        and phase["beta_lower_multiplier"] > _KKT_TOL
        and abs(phase["beta"] * phase["beta_lower_multiplier"]) <= _COMPLEMENTARITY_TOL
    ]
    return {
        "outcome": "solved" if numerical else "numerical_rejection",
        "solver_status": "passed" if solver_passed else "failed",
        "numerical_status": "passed" if numerical else "failed",
        "physical_status": "not_adjudicated",
        "objective": float(physical_base["objective"]),
        "physical_solution": physical.tolist(),
        "constraint_multipliers": constraint_multipliers.tolist(),
        "stationarity_inf_norm": stationarity_inf,
        "feasibility_inf_norm": feasibility_inf,
        "complementarity_inf_norm": complementarity_inf,
        "dual_pullback": {
            "status": dual_pullback_status,
            "signs": "passed" if sign_valid else "failed",
            "reconstruction_inf_norm": reconstruction,
            "mapping": "z_physical_equals_z_chart_divided_by_affine_scale",
        },
        "phases": phases,
        "inactive_ids": inactive_ids,
    }


def _step9(solve, feed_u, force_potential_failure=False):
    phases = solve["phases"]
    beta = np.asarray([phase["beta"] for phase in phases])
    modified = np.asarray([phase["modified_fraction"] for phase in phases])
    modified_balance = abs(float(beta @ modified - float(feed_u)))
    ordinary = np.asarray([
        recover_explicit_composition(value) for value in modified
    ])
    ordinary_feed = np.asarray(recover_explicit_composition(feed_u))
    ordinary_balance = float(np.max(np.abs(beta @ ordinary - ordinary_feed)))
    charge = max(abs(float(phase["charge_residual"])) for phase in phases)
    pressure = max(abs(float(phase["relative_pressure_residual"])) for phase in phases)
    potentials = np.asarray([phase["modified_potentials"] for phase in phases])
    potential_gap = float(np.max(np.ptp(potentials, axis=0)))
    if force_potential_failure:
        potential_gap = max(potential_gap, 1.0)
    distances = []
    for left in range(len(phases)):
        for right in range(left + 1, len(phases)):
            distances.append(max(
                abs(phases[left]["modified_fraction"] - phases[right]["modified_fraction"]),
                abs(phases[left]["packing_fraction"] - phases[right]["packing_fraction"]),
            ))
    minimum_distance = min(distances) if distances else 0.0
    domain_valid = all(
        phase["final_eos_evaluation"] == "passed"
        and 0.0 < phase["modified_fraction"] < 1.0
        and phase["volume"] > 0.0
        for phase in phases
    )
    objective_reconstructed = float(sum(
        phase["beta"] * phase["phase_objective"] for phase in phases
    ))
    objective_residual = abs(objective_reconstructed - float(solve["objective"]))
    stationarity = float(solve.get("stationarity_inf_norm", math.inf))
    feasibility = float(solve.get("feasibility_inf_norm", math.inf))
    complementarity = float(solve.get("complementarity_inf_norm", math.inf))
    dual_pullback_status = solve.get("dual_pullback", {}).get("status", "failed")
    kkt_and_feasibility = bool(
        np.all(np.isfinite((stationarity, feasibility, complementarity)))
        and stationarity <= _KKT_TOL
        and feasibility <= _FEASIBILITY_TOL
        and complementarity <= _COMPLEMENTARITY_TOL
        and dual_pullback_status == "passed"
    )
    checks = {
        "kkt_and_feasibility": "passed" if kkt_and_feasibility else "failed",
        "material_balance": "passed" if modified_balance <= _MATERIAL_TOL else "failed",
        "ordinary_balance": "passed" if ordinary_balance <= _MATERIAL_TOL else "failed",
        "phase_charge": "passed" if charge <= _CHARGE_TOL else "failed",
        "pressure_equality": "passed" if pressure <= _PRESSURE_TOL else "failed",
        "modified_potential_equality": "passed" if potential_gap <= _POTENTIAL_TOL else "failed",
        "phase_distinction": "passed" if minimum_distance >= _DISTINCT_TOL else "failed",
        "domain": "passed" if domain_valid else "failed",
        "total_free_energy": "passed" if objective_residual <= 1.0e-10 else "failed",
        "metrics": {
            "stationarity_inf_norm": stationarity,
            "feasibility_inf_norm": feasibility,
            "complementarity_inf_norm": complementarity,
            "dual_pullback_status": dual_pullback_status,
            "modified_material_residual": modified_balance,
            "ordinary_material_inf_norm": ordinary_balance,
            "charge_inf_norm": charge,
            "pressure_inf_norm": pressure,
            "modified_potential_gap": potential_gap,
            "minimum_phase_distance": minimum_distance,
            "total_free_energy_residual": objective_residual,
        },
    }
    checks["status"] = "passed" if all(
        value == "passed" for key, value in checks.items() if key not in ("metrics", "status")
    ) else "failed"
    return checks


def _retirement_decision(candidate_ids, inactive_ids):
    candidates = tuple(str(value) for value in candidate_ids)
    inactive = sorted({str(value) for value in inactive_ids})
    retirement = {
        "retired_ids": inactive,
        "basis": "kkt_certified_lower_bound_inactivity" if inactive else "none",
    }
    if inactive and len(candidates) - len(inactive) < 2:
        return {
            "proceed": False,
            "feedback": "insufficient_active_phases_after_kkt_retirement",
            "retirement": retirement,
            "active_set_confirmation": {
                "performed": False,
                "reason": "fewer_than_two_active_phases",
            },
        }
    return {
        "proceed": True,
        "feedback": None,
        "retirement": retirement,
        "active_set_confirmation": {"performed": False},
    }


def _solve_stage3_controller(
    phase_evaluator,
    feed_u,
    candidates,
    u_bounds,
    q_bounds,
    force_potential_failure=False,
):
    initial = _solve_stage3_once(
        phase_evaluator,
        feed_u,
        candidates,
        u_bounds,
        q_bounds,
    )
    if initial["numerical_status"] != "passed":
        return {
            **initial,
            "feedback": "stage3_numerical_rejection",
            "retirement": {"retired_ids": [], "basis": "none"},
            "active_set_confirmation": {"performed": False},
        }
    inactive = set(initial["inactive_ids"])
    retirement_decision = _retirement_decision(
        [candidate["id"] for candidate in candidates],
        inactive,
    )
    if not retirement_decision["proceed"]:
        return {
            **initial,
            "outcome": "return_to_stage2",
            "feedback": retirement_decision["feedback"],
            "physical_status": "not_adjudicated",
            "initial_solve": initial,
            "retirement": retirement_decision["retirement"],
            "active_set_confirmation": retirement_decision["active_set_confirmation"],
        }
    final = initial
    confirmation = retirement_decision["active_set_confirmation"]
    retirement = retirement_decision["retirement"]
    if inactive:
        retained_candidates = [
            candidate for candidate in candidates if candidate["id"] not in inactive
        ]
        retained_phases = [
            phase for phase in initial["phases"] if phase["id"] not in inactive
        ]
        retained_beta = np.asarray([phase["beta"] for phase in retained_phases])
        retained_beta /= np.sum(retained_beta)
        retained_u = np.asarray([phase["modified_fraction"] for phase in retained_phases])
        retained_q = np.asarray([phase["log_volume"] for phase in retained_phases])
        active_start = np.concatenate((retained_beta, retained_u, retained_q))
        final = _solve_stage3_once(
            phase_evaluator,
            feed_u,
            retained_candidates,
            u_bounds,
            q_bounds,
            active_start,
        )
        confirmation = {
            "performed": True,
            "settings_unchanged": True,
            "solver_status": final["solver_status"],
            "numerical_status": final["numerical_status"],
            "physical_status": "not_adjudicated",
            "remaining_inactive_ids": final["inactive_ids"],
        }
    if final["numerical_status"] != "passed":
        return {
            **final,
            "outcome": "return_to_stage2",
            "feedback": "active_set_confirmation_failed",
            "initial_solve": initial,
            "retirement": retirement,
            "active_set_confirmation": confirmation,
        }
    step9 = _step9(final, feed_u, force_potential_failure)
    physical_status = step9["status"]
    if confirmation["performed"]:
        confirmation["physical_status"] = physical_status
    accepted = physical_status == "passed"
    return {
        "outcome": "accepted" if accepted else "return_to_stage2",
        "feedback": None if accepted else "step9_physical_rejection",
        "solver_status": final["solver_status"],
        "numerical_status": final["numerical_status"],
        "physical_status": physical_status,
        "initial_solve": initial,
        "retirement": retirement,
        "active_set_confirmation": confirmation,
        "step9": step9,
        "phases": final["phases"],
        "objective": final["objective"],
    }


def manufactured_stage3_demo(case):
    name = str(case)
    if name not in ("split", "inactive", "feedback"):
        raise ValueError("case must be split, inactive, or feedback")
    candidates = [
        {"id": "alpha", "modified_fraction": 0.2, "log_volume": 0.0},
        {"id": "beta", "modified_fraction": 0.8, "log_volume": 0.0},
    ]
    if name == "inactive":
        candidates.append({"id": "inactive", "modified_fraction": 0.5, "log_volume": 0.0})
    return _solve_stage3_controller(
        _manufactured_stage2_phase,
        0.5,
        candidates,
        (1.0e-8, 1.0 - 1.0e-8),
        (-1.0, 1.0),
        force_potential_failure=name == "feedback",
    )


def _trace_demo():
    initial = 1.0e-8
    target = 1.0e-14
    y = math.log(initial)
    target_y = math.log(target)
    ledger = []
    for iteration in range(64):
        residual = y - target_y
        ledger.append({
            "iteration": iteration,
            "fraction": math.exp(y),
            "log_residual": residual,
        })
        if abs(residual) <= 1.0e-10:
            break
        y -= 0.5 * residual
    final = math.exp(y)
    return {
        "status": "passed" if abs(y - target_y) <= 1.0e-10 else "failed",
        "initial_fraction": initial,
        "final_fraction": final,
        "target_fraction": target,
        "iterations": len(ledger),
        "ledger": ledger,
        "method": "damped_newton_in_log_trace_fraction",
    }


def manufactured_full_demo(case):
    name = str(case)
    if name not in ("stable", "unstable", "feedback", "trace"):
        raise ValueError("unknown full-controller manufactured case")
    ledger = [{"step": index, "status": "not_run"} for index in range(1, 11)]
    ledger[0] = {"step": 1, "status": "completed", "action": "modified_coordinate_construction"}
    if name == "stable":
        stage1 = manufactured_stage1_demo("stable")
        ledger[1] = {"step": 2, "status": "completed", "outcome": stage1["outcome"]}
        return {
            "outcome": "one_phase",
            "solver_status": "passed",
            "numerical_status": "passed",
            "physical_status": "passed",
            "stage1": stage1,
            "step_ledger": ledger,
        }

    stage1 = manufactured_stage1_demo("unstable")
    ledger[1] = {"step": 2, "status": "completed", "outcome": stage1["outcome"]}
    ledger[2] = {"step": 3, "status": "completed", "action": "dual_initialization"}
    stage2 = manufactured_stage2_demo("two_phase")
    ledger[3] = {"step": 4, "status": "completed", "action": "upper_linear_program"}
    ledger[4] = {"step": 5, "status": "completed", "action": "lower_local_multistart"}
    ledger[5] = {"step": 6, "status": "completed", "candidate_ids": [item["id"] for item in stage2["mstar"]]}
    ledger[6] = {"step": 7, "status": "completed", "major_iterations": len(stage2["majors"])}
    stage3_case = "feedback" if name == "feedback" else "split"
    stage3 = manufactured_stage3_demo(stage3_case)
    ledger[7] = {"step": 8, "status": "completed", "action": "extensive_gibbs_refinement"}
    ledger[8] = {"step": 9, "status": "completed", "outcome": stage3["physical_status"]}
    trace = None
    if name == "trace" and stage3["outcome"] == "accepted":
        trace = _trace_demo()
        ledger[9] = {"step": 10, "status": "completed", "outcome": trace["status"]}
    else:
        ledger[9] = {"step": 10, "status": "not_required"}
    result = {
        "outcome": "two_phase" if stage3["outcome"] == "accepted" else "return_to_stage2",
        "solver_status": stage3["solver_status"],
        "numerical_status": stage3["numerical_status"],
        "physical_status": stage3["physical_status"],
        "stage1": stage1,
        "stage2": stage2,
        "stage3": stage3,
        "step_ledger": ledger,
    }
    if trace is not None:
        result["trace"] = trace
    return result


def run_perdomo_table3_demo():
    temperature = 298.15
    pressure = 2508.0
    water_moles = 1000.0 / 18.01528
    feed_amounts = (water_moles, 5.6, 5.6)
    feed_u = modified_fraction(feed_amounts)
    volume_bounds = (1.5e-5, 0.2)
    starts = (
        (feed_u, math.log(1.8e-5)),
        (feed_u, math.log(9.8e-2)),
        (1.0e-6, math.log(9.8e-2)),
        (0.30, math.log(2.0e-5)),
    )
    stage1 = solve_stage1(
        temperature,
        pressure,
        feed_amounts,
        volume_bounds,
        starts,
        129,
    )
    result = {
        "source_case": "Perdomo_2025_Table_3_NaCl_water_5.6_molal",
        "temperature_k": temperature,
        "pressure_pa": pressure,
        "feed_amounts": feed_amounts,
        "feed_modified_ion_fraction": feed_u,
        "source_eos": "SAFT-gamma-Mie_GC",
        "experiment_eos": "ePC-SAFT_Figiel_2025_bounded_H2O_Na_Cl",
        "comparison_scope": "cross_EOS_controller_challenge_not_source_model_reproduction",
        "parameter_tuning": False,
        "stage1": stage1,
        "stage2": None,
        "stage3": None,
        "solver_status": "not_adjudicated",
        "numerical_status": "not_adjudicated",
        "physical_status": "not_adjudicated",
    }
    if stage1["outcome"] != "negative_tpd":
        result["terminal"] = "stage1_" + str(stage1["outcome"])
        result["solver_status"] = "passed" if stage1["attempts"] and all(
            attempt["solver_convergence"] == "passed" for attempt in stage1["attempts"]
        ) else "failed"
        result["numerical_status"] = "passed" if stage1["search_status"] == "completed_finite" else "failed"
        return result

    reference = stage1["reference"]["selected"]
    witness = stage1["negative_witness"]
    witness_u, witness_q = witness["solution"]
    feed_q = math.log(float(reference["volume"]))
    initial = (
        {"id": "feed", "modified_fraction": feed_u, "log_volume": feed_q},
        {"id": "witness", "modified_fraction": witness_u, "log_volume": witness_q},
    )
    gradients = [
        _stage2_phase_callback(temperature, pressure, (candidate["modified_fraction"], candidate["log_volume"]))[
            "composition_gradient_fixed_volume"
        ]
        for candidate in initial
    ]
    stage2 = solve_stage2(
        temperature,
        pressure,
        feed_amounts,
        initial,
        volume_bounds,
        starts,
        (min(gradients) - 10.0, max(gradients) + 10.0),
        max_major=3,
    )
    result["stage2"] = stage2
    if stage2["outcome"] != "ready_stage3":
        result["terminal"] = "stage2_" + str(stage2["outcome"])
        result["solver_status"] = "passed"
        result["numerical_status"] = "failed"
        return result

    stage3 = _solve_stage3_controller(
        lambda point: _stage2_phase_callback(temperature, pressure, point),
        feed_u,
        stage2["mstar"],
        (1.0e-8, 0.38),
        (math.log(volume_bounds[0]), math.log(volume_bounds[1])),
    )
    result["stage3"] = stage3
    result["terminal"] = "stage3_" + str(stage3["outcome"])
    result["solver_status"] = stage3["solver_status"]
    result["numerical_status"] = stage3["numerical_status"]
    result["physical_status"] = stage3["physical_status"]
    return result
