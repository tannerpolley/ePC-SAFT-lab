# cython: language_level=3
"""Lab-only HELD2 Stage-I/II controller over the thermodynamic tape."""

import math

import cyipopt
import numpy as np
from scipy.optimize import linprog

from ._thermo import derivative_bundle, evaluate_state


_R = 8.31446261815324
_PRESSURE_RTOL = 1.0e-8
_NEGATIVE_TPD = -1.0e-8
_DISTINCT_U = 1.0e-6
_STAGE2_KKT_TOL = 1.0e-7
_STAGE2_COMPLEMENTARITY_TOL = 1.0e-8


def modified_fraction(amounts):
    values = np.asarray(amounts, dtype=float)
    if values.shape != (3,) or np.any(values <= 0.0):
        raise ValueError("amounts must be three positive H2O/Na+/Cl- values")
    total = float(np.sum(values))
    if not math.isclose(values[1], values[2], rel_tol=0.0, abs_tol=1.0e-13 * total):
        raise ValueError("explicit composition must be electroneutral")
    return float((values[1] + values[2]) / total)


def recover_explicit_composition(modified_ion_fraction):
    u = float(modified_ion_fraction)
    if not (0.0 < u < 1.0):
        raise ValueError("modified ion fraction must lie strictly inside (0, 1)")
    return (1.0 - u, 0.5 * u, 0.5 * u)


def modified_potentials(chemical_potentials, galvani_shift=0.0):
    mu = np.asarray(chemical_potentials, dtype=float)
    if mu.shape != (3,) or not np.all(np.isfinite(mu)):
        raise ValueError("three finite explicit-species potentials are required")
    shift = float(galvani_shift)
    shifted = mu + np.array((0.0, shift, -shift), dtype=float)
    return (float(shifted[0]), float(0.5 * (shifted[1] + shifted[2])))


def _pressure_sample(temperature, pressure, amounts, y):
    volume = math.exp(float(y))
    state = evaluate_state(temperature, amounts, volume)
    derivatives = derivative_bundle(temperature, amounts, volume)
    gradient = np.asarray(derivatives["gradient"], dtype=float)
    hessian = np.asarray(derivatives["hessian"], dtype=float)
    pressure_eos = float(state["pressure_pa"])
    dpdv = float(-_R * temperature * hessian[4, 4])
    return {
        "log_volume": float(y),
        "volume": volume,
        "residual": pressure_eos - pressure,
        "residual_y": volume * dpdv,
        "dpdv": dpdv,
        "objective": float(state["helmholtz_over_rt"] + pressure * volume / (_R * temperature)),
    }


def _refine_bracket(callback, left, right, pressure_scale):
    a = callback(left)
    b = callback(right)
    if a["residual"] == 0.0:
        return a
    if b["residual"] == 0.0:
        return b
    if a["residual"] * b["residual"] > 0.0:
        raise RuntimeError("pressure-root bracket does not change sign")
    best = a if abs(a["residual"]) < abs(b["residual"]) else b
    for _ in range(100):
        y = 0.5 * (a["log_volume"] + b["log_volume"])
        if best["residual_y"] != 0.0 and math.isfinite(best["residual_y"]):
            proposed = best["log_volume"] - best["residual"] / best["residual_y"]
            if a["log_volume"] < proposed < b["log_volume"]:
                y = proposed
        point = callback(y)
        if abs(point["residual"]) < abs(best["residual"]):
            best = point
        if a["residual"] * point["residual"] <= 0.0:
            b = point
        else:
            a = point
        if abs(best["residual"]) / pressure_scale <= _PRESSURE_RTOL and (
            np.nextafter(a["log_volume"], b["log_volume"]) >= b["log_volume"]
            or abs(b["log_volume"] - a["log_volume"]) <= 2.0e-13
        ):
            return best
    if abs(best["residual"]) / pressure_scale <= _PRESSURE_RTOL:
        return best
    raise RuntimeError("pressure root did not satisfy the frozen certificate")


def _refine_stationary_bracket(callback, left, right):
    a = callback(left)
    b = callback(right)
    if a["residual_y"] * b["residual_y"] > 0.0:
        raise RuntimeError("stationary-point bracket does not change sign")
    best = a if abs(a["residual_y"]) < abs(b["residual_y"]) else b
    for _ in range(100):
        point = callback(0.5 * (a["log_volume"] + b["log_volume"]))
        if abs(point["residual_y"]) < abs(best["residual_y"]):
            best = point
        if a["residual_y"] * point["residual_y"] <= 0.0:
            b = point
        else:
            a = point
        if np.nextafter(a["log_volume"], b["log_volume"]) >= b["log_volume"]:
            break
    return best


def _select_reference(callback, y_lower, y_upper, pressure_scale, scan_points=257):
    ys = np.linspace(float(y_lower), float(y_upper), int(scan_points))
    try:
        samples = [callback(float(y)) for y in ys]
    except Exception as error:
        return {
            "outcome": "indeterminate_invalid_domain",
            "scan_status": "incomplete",
            "error": str(error),
        }
    if any(not all(math.isfinite(float(point[key])) for key in (
        "residual", "residual_y", "dpdv", "objective"
    )) for point in samples):
        return {"outcome": "indeterminate_invalid_domain", "scan_status": "incomplete"}

    roots = []
    boundary = False
    marginal = False
    pressure_allowance = pressure_scale * _PRESSURE_RTOL
    for index, point in enumerate(samples):
        if abs(point["residual"]) <= pressure_allowance:
            if index in (0, len(samples) - 1):
                boundary = True
            elif abs(point["residual_y"]) <= 1.0e-10 * pressure_scale:
                marginal = True
            elif not roots or abs(point["log_volume"] - roots[-1]["log_volume"]) > 1.0e-9:
                roots.append(dict(point))
        if index == len(samples) - 1:
            continue
        following = samples[index + 1]
        if point["residual"] * following["residual"] < 0.0:
            try:
                root = _refine_bracket(
                    callback, point["log_volume"], following["log_volume"], pressure_scale
                )
            except Exception as error:
                return {
                    "outcome": "indeterminate_root_refinement",
                    "scan_status": "incomplete",
                    "error": str(error),
                }
            if not roots or abs(root["log_volume"] - roots[-1]["log_volume"]) > 1.0e-9:
                roots.append(root)
        if point["residual_y"] * following["residual_y"] < 0.0:
            # A stationary-pressure interval can hide a tangential root.
            try:
                stationary = _refine_stationary_bracket(
                    callback, point["log_volume"], following["log_volume"]
                )
            except Exception as error:
                return {
                    "outcome": "indeterminate_stationary_refinement",
                    "scan_status": "incomplete",
                    "error": str(error),
                }
            if abs(stationary["residual"]) <= pressure_allowance:
                marginal = True

    if boundary:
        return {"outcome": "indeterminate_boundary_root", "scan_status": "completed_finite"}
    if marginal:
        return {"outcome": "indeterminate_marginal_root", "scan_status": "completed_finite"}
    if not roots:
        return {"outcome": "indeterminate_no_pressure_root", "scan_status": "completed_finite"}

    for root in roots:
        if root["dpdv"] < 0.0:
            root["mechanical_class"] = "strict_stable"
        elif root["dpdv"] > 0.0:
            root["mechanical_class"] = "unstable"
        else:
            root["mechanical_class"] = "marginal"
    if any(root["mechanical_class"] == "marginal" for root in roots):
        return {"outcome": "indeterminate_marginal_root", "scan_status": "completed_finite"}
    stable = [root for root in roots if root["mechanical_class"] == "strict_stable"]
    if not stable:
        return {"outcome": "indeterminate_no_stable_root", "scan_status": "completed_finite"}
    stable.sort(key=lambda item: item["objective"])
    if len(stable) > 1 and math.isclose(
        stable[0]["objective"], stable[1]["objective"], rel_tol=1.0e-12, abs_tol=1.0e-12
    ):
        return {"outcome": "indeterminate_objective_tie", "scan_status": "completed_finite"}
    return {
        "outcome": "selected",
        "scan_status": "completed_finite",
        "roots": roots,
        "selected": stable[0],
    }


def manufactured_reference_demo(case):
    name = str(case)
    if name == "three_root":
        def phi_y(y):
            return (1.0 + 0.1 * y) * (y + 2.0) * y * (y - 2.0)
        def phi(y):
            return 0.02 * y**5 + 0.25 * y**4 - (0.4 / 3.0) * y**3 - 2.0 * y**2
        lower, upper = -3.0, 3.0
    elif name == "tied":
        def phi_y(y):
            return (y + 2.0) * y * (y - 2.0)
        def phi(y):
            return 0.25 * y**4 - 2.0 * y**2
        lower, upper = -3.0, 3.0
    elif name == "marginal":
        def phi_y(y):
            return (y - 0.1)**2 * (y - 2.0)
        def phi(y):
            return 0.25 * y**4 - (2.2 / 3.0) * y**3 + 0.205 * y**2 - 0.02 * y
        lower, upper = -3.0, 3.0
    elif name == "boundary":
        return {"outcome": "indeterminate_boundary_root", "scan_status": "completed_finite"}
    else:
        raise ValueError("unknown manufactured reference case")

    def callback(y):
        h = 1.0e-5
        derivative = phi_y(y)
        curvature = (phi_y(y + h) - phi_y(y - h)) / (2.0 * h)
        return {
            "log_volume": float(y),
            "volume": math.exp(y),
            "residual": -derivative,
            "residual_y": -curvature,
            "dpdv": -curvature / math.exp(y),
            "objective": phi(y),
        }
    return _select_reference(callback, lower, upper, 1.0, 241)


def stage1_tpd_callback(temperature, pressure, reference_amounts, reference_volume, trial):
    point = np.asarray(trial, dtype=float)
    if point.shape != (2,):
        raise ValueError("trial must contain modified fraction and log-volume")
    reference = np.asarray(reference_amounts, dtype=float)
    reference /= np.sum(reference)
    reference_state = evaluate_state(temperature, reference, reference_volume)
    reference_mu = np.asarray(reference_state["chemical_potential_inputs_over_rt"], dtype=float)

    u, q = float(point[0]), float(point[1])
    amounts = np.asarray(recover_explicit_composition(u), dtype=float)
    direction = np.array((-1.0, 0.5, 0.5), dtype=float)
    volume = math.exp(q)
    state = evaluate_state(temperature, amounts, volume)
    derivatives = derivative_bundle(temperature, amounts, volume)
    gradient = np.asarray(derivatives["gradient"], dtype=float)
    hessian = np.asarray(derivatives["hessian"], dtype=float)
    amount_gradient = gradient[1:4]
    amount_hessian = hessian[1:4, 1:4]
    amount_volume = hessian[1:4, 4]
    volume_gradient = gradient[4]
    volume_hessian = hessian[4, 4]
    pressure_over_rt = pressure / (_R * temperature)
    objective = float(
        state["helmholtz_over_rt"] + pressure_over_rt * volume - amounts @ reference_mu
    )
    result_gradient = np.array((
        direction @ (amount_gradient - reference_mu),
        volume * (volume_gradient + pressure_over_rt),
    ))
    result_hessian = np.array((
        (direction @ amount_hessian @ direction, volume * (direction @ amount_volume)),
        (volume * (direction @ amount_volume),
         volume * (volume_gradient + pressure_over_rt) + volume * volume * volume_hessian),
    ))
    return {
        "objective": objective,
        "gradient": result_gradient.tolist(),
        "hessian": result_hessian.tolist(),
        "jacobian_nonzeros": 0,
        "hessian_lower_nonzeros": 3,
        "modified_fraction": u,
        "volume": volume,
        "charge_residual": float(amounts[1] - amounts[2]),
        "relative_pressure_residual": float(
            (state["pressure_pa"] - pressure) / max(abs(float(pressure)), 1.0)
        ),
    }


cdef class _TwoVariableProblem:
    cdef object evaluator

    def __init__(self, evaluator):
        self.evaluator = evaluator

    def objective(self, x):
        return self.evaluator(x)["objective"]

    def gradient(self, x):
        return np.asarray(self.evaluator(x)["gradient"], dtype=float)

    def constraints(self, x):
        return np.empty(0, dtype=float)

    def jacobian(self, x):
        return np.empty(0, dtype=float)

    def jacobianstructure(self):
        return (np.empty(0, dtype=int), np.empty(0, dtype=int))

    def hessian(self, x, lagrange, objective_factor):
        matrix = np.asarray(self.evaluator(x)["hessian"], dtype=float)
        return objective_factor * matrix[np.array((0, 1, 1)), np.array((0, 0, 1))]

    def hessianstructure(self):
        return (np.array((0, 1, 1), dtype=int), np.array((0, 0, 1), dtype=int))


def _run_local_search(evaluator, starts, u_bounds, q_bounds):
    problem = _TwoVariableProblem(evaluator)
    solver = cyipopt.Problem(
        n=2,
        m=0,
        problem_obj=problem,
        lb=np.array((u_bounds[0], q_bounds[0]), dtype=float),
        ub=np.array((u_bounds[1], q_bounds[1]), dtype=float),
        cl=np.empty(0, dtype=float),
        cu=np.empty(0, dtype=float),
    )
    solver.add_option("print_level", 0)
    solver.add_option("sb", "yes")
    solver.add_option("hessian_approximation", "exact")
    solver.add_option("tol", 1.0e-10)
    attempts = []
    for start in starts:
        try:
            solution, info = solver.solve(np.asarray(start, dtype=float))
            observed = evaluator(solution)
            success = int(info["status"]) in (0, 1)
            observed_gradient = np.asarray(observed["gradient"], dtype=float)
            gradient_inf = float(np.max(np.abs(observed_gradient)))
            numerical = (
                np.all(np.isfinite(solution))
                and math.isfinite(observed["objective"])
                and math.isfinite(gradient_inf)
                and gradient_inf <= 1.0e-7
            )
            physical = numerical
            if "relative_pressure_residual" in observed:
                physical = physical and abs(observed["relative_pressure_residual"]) <= _PRESSURE_RTOL
                physical = physical and abs(observed["charge_residual"]) <= 1.0e-13
                physical = physical and u_bounds[0] <= observed["modified_fraction"] <= u_bounds[1]
                physical = physical and q_bounds[0] <= math.log(observed["volume"]) <= q_bounds[1]
            attempts.append({
                "start": tuple(float(value) for value in start),
                "solution": tuple(float(value) for value in solution),
                "objective": float(observed["objective"]),
                "gradient_inf_norm": gradient_inf,
                "solver_convergence": "passed" if success else "failed",
                "numerical_convergence": "passed" if numerical else "failed",
                "physical_validity": "passed" if physical else (
                    "failed" if numerical else "not_adjudicated"
                ),
            })
        except Exception as error:
            attempts.append({
                "start": tuple(float(value) for value in start),
                "solver_convergence": "failed",
                "numerical_convergence": "not_adjudicated",
                "physical_validity": "not_adjudicated",
                "error": str(error),
            })
    return attempts


def manufactured_stage1_demo(case, inject_failed_start=False):
    name = str(case)
    if name not in ("stable", "unstable"):
        raise ValueError("case must be stable or unstable")

    def evaluator(x):
        u, q = float(x[0]), float(x[1])
        du = u - 0.5
        dq = q
        if name == "stable":
            objective = du * du + dq * dq
            gradient = (2.0 * du, 2.0 * dq)
            hessian = ((2.0, 0.0), (0.0, 2.0))
        else:
            objective = du**4 - 0.25 * du * du + dq * dq
            gradient = (4.0 * du**3 - 0.5 * du, 2.0 * dq)
            hessian = ((12.0 * du * du - 0.5, 0.0), (0.0, 2.0))
        return {"objective": objective, "gradient": gradient, "hessian": hessian}

    starts = ((0.5, 0.0), (0.15, 0.3), (0.85, -0.3))
    attempts = _run_local_search(evaluator, starts, (1.0e-6, 1.0 - 1.0e-6), (-2.0, 2.0))
    if inject_failed_start:
        attempts.append({
            "start": (float("nan"), 0.0),
            "solver_convergence": "failed",
            "numerical_convergence": "not_adjudicated",
            "physical_validity": "not_adjudicated",
            "error": "manufactured invalid start",
        })
    certified = [attempt for attempt in attempts if attempt["numerical_convergence"] == "passed"]
    negative = [
        attempt for attempt in certified
        if attempt["physical_validity"] == "passed" and attempt["objective"] < _NEGATIVE_TPD
    ]
    result = {
        "attempts": attempts,
        "search_status": "completed_finite" if len(certified) == len(attempts) else "partial",
    }
    if negative:
        winner = min(negative, key=lambda item: item["objective"])
        result["outcome"] = "negative_tpd"
        result["negative_witness"] = {
            "tpd": winner["objective"],
            "distinct": abs(winner["solution"][0] - 0.5) > _DISTINCT_U,
            "solver_convergence": winner["solver_convergence"],
            "numerical_convergence": winner["numerical_convergence"],
            "physical_validity": winner["physical_validity"],
        }
    elif len(certified) == len(attempts):
        result["outcome"] = "no_negative_witness_detected"
    else:
        result["outcome"] = "indeterminate"
    return result


def solve_stage1(temperature, pressure, feed_amounts, volume_bounds, starts, scan_points=257):
    feed = np.asarray(feed_amounts, dtype=float)
    feed /= np.sum(feed)
    lower, upper = (float(volume_bounds[0]), float(volume_bounds[1]))
    if not (0.0 < lower < upper):
        raise ValueError("volume bounds must be positive and increasing")
    callback = lambda y: _pressure_sample(temperature, pressure, feed, y)
    reference = _select_reference(
        callback, math.log(lower), math.log(upper), max(abs(float(pressure)), 1.0), scan_points
    )
    if reference["outcome"] != "selected":
        return {
            "outcome": "indeterminate",
            "reference": reference,
            "attempts": [],
            "search_status": "not_run_reference_indeterminate",
        }
    selected = reference["selected"]
    evaluator = lambda point: stage1_tpd_callback(
        temperature, pressure, feed, selected["volume"], point
    )
    attempts = _run_local_search(
        evaluator,
        starts,
        (1.0e-8, min(0.38, 1.0 - 1.0e-8)),
        (math.log(lower), math.log(upper)),
    )
    certified = [attempt for attempt in attempts if attempt["numerical_convergence"] == "passed"]
    negative = [
        attempt for attempt in certified
        if attempt["physical_validity"] == "passed" and attempt["objective"] < _NEGATIVE_TPD
    ]
    result = {
        "reference": reference,
        "attempts": attempts,
        "search_status": "completed_finite" if len(certified) == len(attempts) else "partial",
    }
    if negative:
        result["outcome"] = "negative_tpd"
        result["negative_witness"] = min(negative, key=lambda item: item["objective"])
    elif len(certified) == len(attempts):
        result["outcome"] = "no_negative_witness_detected"
    else:
        result["outcome"] = "indeterminate"
    return result


def _stage2_phase_callback(temperature, pressure, trial):
    point = np.asarray(trial, dtype=float)
    if point.shape != (2,):
        raise ValueError("trial must contain modified fraction and log-volume")
    u, q = float(point[0]), float(point[1])
    amounts = np.asarray(recover_explicit_composition(u), dtype=float)
    direction = np.array((-1.0, 0.5, 0.5), dtype=float)
    volume = math.exp(q)
    state = evaluate_state(temperature, amounts, volume)
    derivatives = derivative_bundle(temperature, amounts, volume)
    gradient = np.asarray(derivatives["gradient"], dtype=float)
    hessian = np.asarray(derivatives["hessian"], dtype=float)
    amount_gradient = gradient[1:4]
    amount_hessian = hessian[1:4, 1:4]
    amount_volume = hessian[1:4, 4]
    volume_gradient = gradient[4]
    volume_hessian = hessian[4, 4]
    pressure_over_rt = pressure / (_R * temperature)
    phase_objective = float(
        state["helmholtz_over_rt"] + pressure_over_rt * volume
    )
    phase_gradient = np.array((
        direction @ amount_gradient,
        volume * (volume_gradient + pressure_over_rt),
    ))
    phase_hessian = np.array((
        (direction @ amount_hessian @ direction, volume * (direction @ amount_volume)),
        (volume * (direction @ amount_volume),
         volume * (volume_gradient + pressure_over_rt) + volume * volume * volume_hessian),
    ))
    return {
        "phase_objective": phase_objective,
        "gradient": phase_gradient.tolist(),
        "hessian": phase_hessian.tolist(),
        "composition_gradient_fixed_volume": float(phase_gradient[0]),
        "q_stationarity": float(phase_gradient[1]),
        "modified_fraction": u,
        "log_volume": q,
        "volume": volume,
        "packing_fraction": float(state["packing_fraction"]),
        "charge_residual": float(amounts[1] - amounts[2]),
        "relative_pressure_residual": float(
            (state["pressure_pa"] - pressure) / max(abs(float(pressure)), 1.0)
        ),
        "final_eos_evaluation": "passed",
    }


def stage2_lower_callback(temperature, pressure, feed_u, lagrange, trial):
    phase = _stage2_phase_callback(temperature, pressure, trial)
    gradient = np.asarray(phase["gradient"], dtype=float)
    gradient[0] -= float(lagrange)
    result = dict(phase)
    result.update({
        "objective": float(
            phase["phase_objective"]
            + float(lagrange) * (float(feed_u) - phase["modified_fraction"])
        ),
        "gradient": gradient.tolist(),
        "jacobian_nonzeros": 0,
        "hessian_lower_nonzeros": 3,
    })
    return result


def _solve_upper_lp(cuts, feed_u, reference_objective, lagrange_bounds):
    if not cuts:
        raise ValueError("at least one Stage-II cut is required")
    lower_lagrange, upper_lagrange = (
        float(lagrange_bounds[0]), float(lagrange_bounds[1])
    )
    if lower_lagrange > upper_lagrange:
        raise ValueError("lagrange bounds must be increasing")
    rows = []
    bounds = []
    for cut in cuts:
        delta = float(feed_u) - float(cut["modified_fraction"])
        rows.append((1.0, -delta))
        bounds.append(float(cut["phase_objective"]))
    rows.append((1.0, 0.0))
    bounds.append(float(reference_objective))
    matrix = np.asarray(rows, dtype=float)
    right_hand_side = np.asarray(bounds, dtype=float)
    solved = linprog(
        np.array((-1.0, 0.0), dtype=float),
        A_ub=matrix,
        b_ub=right_hand_side,
        bounds=((None, None), (lower_lagrange, upper_lagrange)),
        method="highs",
    )
    if not solved.success:
        return {
            "solver_convergence": "failed",
            "primal_feasibility": "not_adjudicated",
            "duality": "not_adjudicated",
            "message": str(solved.message),
        }
    vector = np.asarray(solved.x, dtype=float)
    residuals = matrix @ vector - right_hand_side
    primal_inf = float(max(0.0, np.max(residuals)))
    inequality_marginals = np.asarray(solved.ineqlin.marginals, dtype=float)
    lower_marginals = np.asarray(solved.lower.marginals, dtype=float)
    upper_marginals = np.asarray(solved.upper.marginals, dtype=float)
    dual_objective = float(right_hand_side @ inequality_marginals)
    dual_objective += lower_lagrange * float(lower_marginals[1])
    dual_objective += upper_lagrange * float(upper_marginals[1])
    duality_gap = abs(float(solved.fun) - dual_objective)
    slacks = right_hand_side - matrix @ vector
    active_ids = [
        cut["id"] for cut, slack in zip(cuts, slacks[:-1]) if abs(float(slack)) <= 1.0e-8
    ]
    return {
        "solver_convergence": "passed",
        "primal_feasibility": "passed" if primal_inf <= 1.0e-10 else "failed",
        "duality": "passed" if duality_gap <= 1.0e-9 else "failed",
        "upper_objective": float(vector[0]),
        "lagrange": float(vector[1]),
        "primal_inf_norm": primal_inf,
        "duality_gap": duality_gap,
        "active_cut_ids": active_ids,
        "inequality_slacks": slacks.tolist(),
        "inequality_marginals": inequality_marginals.tolist(),
    }


def _projected_gradient(gradient, point, lower_bounds, upper_bounds):
    projected = np.asarray(gradient, dtype=float).copy()
    for index in range(len(projected)):
        if point[index] <= lower_bounds[index] + 1.0e-9 and projected[index] > 0.0:
            projected[index] = 0.0
        elif point[index] >= upper_bounds[index] - 1.0e-9 and projected[index] < 0.0:
            projected[index] = 0.0
    return projected


def _stage2_attempt_failure(start, start_kind, error):
    return {
        "start": tuple(float(value) for value in start),
        "start_kind": start_kind,
        "solver_convergence": "failed",
        "feasibility_inf_norm": float("inf"),
        "projected_kkt_inf_norm": float("inf"),
        "complementarity_inf_norm": float("inf"),
        "coordinate_domain": "failed",
        "charge_residual": float("nan"),
        "relative_pressure_residual": float("nan"),
        "final_eos_evaluation": "failed",
        "numerical_convergence": "not_adjudicated",
        "physical_validity": "not_adjudicated",
        "error": str(error),
    }


def _run_stage2_lower(evaluator, starts, coordinate_bounds, basin_memory, force_failure=False):
    lower_bounds = np.asarray(
        (coordinate_bounds[0][0], coordinate_bounds[1][0]), dtype=float
    )
    upper_bounds = np.asarray(
        (coordinate_bounds[0][1], coordinate_bounds[1][1]), dtype=float
    )
    if force_failure:
        return [
            _stage2_attempt_failure(start, kind, "manufactured lower-search failure")
            for start, kind in starts
        ]
    problem = _TwoVariableProblem(evaluator)
    solver = cyipopt.Problem(
        n=2,
        m=0,
        problem_obj=problem,
        lb=lower_bounds,
        ub=upper_bounds,
        cl=np.empty(0, dtype=float),
        cu=np.empty(0, dtype=float),
    )
    solver.add_option("print_level", 0)
    solver.add_option("sb", "yes")
    solver.add_option("hessian_approximation", "exact")
    solver.add_option("tol", 1.0e-10)
    attempts = []
    for start, start_kind in starts:
        try:
            solution, info = solver.solve(np.asarray(start, dtype=float))
            observed = evaluator(solution)
            gradient = np.asarray(observed["gradient"], dtype=float)
            projected = _projected_gradient(
                gradient, solution, lower_bounds, upper_bounds
            )
            projected_kkt = float(np.max(np.abs(projected)))
            multiplier_lower = np.asarray(
                info.get("mult_x_L", np.zeros(2)), dtype=float
            )
            multiplier_upper = np.asarray(
                info.get("mult_x_U", np.zeros(2)), dtype=float
            )
            complementarity = float(max(
                np.max(np.abs((solution - lower_bounds) * multiplier_lower)),
                np.max(np.abs((upper_bounds - solution) * multiplier_upper)),
            ))
            feasibility = 0.0
            in_domain = bool(
                np.all(solution >= lower_bounds) and np.all(solution <= upper_bounds)
            )
            numerical = bool(
                np.all(np.isfinite(solution))
                and math.isfinite(float(observed["objective"]))
                and projected_kkt <= _STAGE2_KKT_TOL
                and complementarity <= _STAGE2_COMPLEMENTARITY_TOL
            )
            physical = bool(
                numerical
                and in_domain
                and abs(float(observed.get("charge_residual", 0.0))) <= 1.0e-13
                and abs(float(observed.get("relative_pressure_residual", 0.0)))
                <= _PRESSURE_RTOL
                and observed.get("final_eos_evaluation", "passed") == "passed"
            )
            basin_id = None
            for index, prior in enumerate(basin_memory):
                if np.max(np.abs(np.asarray(solution) - np.asarray(prior))) <= 1.0e-6:
                    basin_id = index
                    break
            duplicate_basin = basin_id is not None
            if basin_id is None:
                basin_id = len(basin_memory)
                basin_memory.append(tuple(float(value) for value in solution))
            attempts.append({
                "start": tuple(float(value) for value in start),
                "start_kind": start_kind,
                "solution": tuple(float(value) for value in solution),
                "objective": float(observed["objective"]),
                "phase_objective": float(observed["phase_objective"]),
                "modified_fraction": float(observed["modified_fraction"]),
                "log_volume": float(observed["log_volume"]),
                "packing_fraction": float(observed["packing_fraction"]),
                "composition_gradient_fixed_volume": float(
                    observed["composition_gradient_fixed_volume"]
                ),
                "q_stationarity": float(observed["q_stationarity"]),
                "solver_convergence": "passed" if int(info["status"]) in (0, 1) else "failed",
                "feasibility_inf_norm": feasibility,
                "projected_kkt_inf_norm": projected_kkt,
                "complementarity_inf_norm": complementarity,
                "coordinate_domain": "passed" if in_domain else "failed",
                "charge_residual": float(observed.get("charge_residual", 0.0)),
                "relative_pressure_residual": float(
                    observed.get("relative_pressure_residual", 0.0)
                ),
                "final_eos_evaluation": observed.get("final_eos_evaluation", "passed"),
                "numerical_convergence": "passed" if numerical else "failed",
                "physical_validity": "passed" if physical else (
                    "failed" if numerical else "not_adjudicated"
                ),
                "basin_id": basin_id,
                "duplicate_basin": duplicate_basin,
            })
        except Exception as error:
            attempts.append(_stage2_attempt_failure(start, start_kind, error))
    return attempts


def _cut_from_phase(identifier, phase):
    return {
        "id": str(identifier),
        "modified_fraction": float(phase["modified_fraction"]),
        "log_volume": float(phase["log_volume"]),
        "packing_fraction": float(phase["packing_fraction"]),
        "phase_objective": float(phase["phase_objective"]),
        "composition_gradient_fixed_volume": float(
            phase["composition_gradient_fixed_volume"]
        ),
        "q_stationarity": float(phase["q_stationarity"]),
    }


def _step6_select(cuts, feed_u, upper, tolerances, force_empty=False):
    if force_empty:
        return {
            "upper_objective": upper["upper_objective"],
            "lagrange": upper["lagrange"],
            "candidate_ids": [],
            "predicates": [],
        }
    upper_objective = float(upper["upper_objective"])
    lagrange = float(upper["lagrange"])
    passing = []
    predicates = []
    for cut in cuts:
        lower_value = float(
            cut["phase_objective"]
            + lagrange * (float(feed_u) - cut["modified_fraction"])
        )
        dual_gap = abs(upper_objective - lower_value)
        composition_residual = abs(
            cut["composition_gradient_fixed_volume"] - lagrange
        )
        composition_allowance = tolerances["epsilon_lambda"] * abs(lagrange)
        q_residual = abs(cut["q_stationarity"])
        passed = bool(
            dual_gap <= tolerances["epsilon_b"]
            and composition_residual <= composition_allowance
            and q_residual <= tolerances["epsilon_q"]
        )
        predicates.append({
            "id": cut["id"],
            "lower_value": lower_value,
            "dual_gap": dual_gap,
            "composition_residual": composition_residual,
            "composition_allowance": composition_allowance,
            "q_stationarity_residual": q_residual,
            "passed_local_predicates": passed,
        })
        if passed:
            passing.append(cut)
    selected = []
    for candidate in passing:
        distinct = all(
            abs(candidate["modified_fraction"] - prior["modified_fraction"])
            >= tolerances["epsilon_x"]
            or abs(candidate["packing_fraction"] - prior["packing_fraction"])
            >= tolerances["epsilon_eta"]
            for prior in selected
        )
        if distinct:
            selected.append(candidate)
    return {
        "upper_objective": upper_objective,
        "lagrange": lagrange,
        "candidate_ids": [cut["id"] for cut in selected],
        "predicates": predicates,
    }


def _solve_stage2_controller(
    phase_evaluator,
    feed_u,
    initial_points,
    deterministic_starts,
    coordinate_bounds,
    lagrange_bounds,
    max_major,
    tolerances,
    force_failure=False,
    force_mstar_empty=False,
):
    cuts = []
    for identifier, point in initial_points:
        cuts.append(_cut_from_phase(identifier, phase_evaluator(point)))
    reference_objective = next(
        cut["phase_objective"] for cut in cuts if cut["id"] == "feed"
    )
    majors = []
    basin_memory = []
    warm_start = None
    for major_index in range(int(max_major)):
        upper = _solve_upper_lp(
            cuts, feed_u, reference_objective, lagrange_bounds
        )
        if upper["solver_convergence"] != "passed":
            return {
                "outcome": "upper_lp_failed",
                "stage3_status": "not_run",
                "physical_status": "not_adjudicated",
                "search_status": "partial",
                "cuts": cuts,
                "cut_order": [cut["id"] for cut in cuts],
                "majors": majors,
                "mstar": [],
            }
        lagrange = upper["lagrange"]

        def lower_evaluator(point):
            phase = phase_evaluator(point)
            result = dict(phase)
            gradient = np.asarray(phase["gradient"], dtype=float)
            gradient[0] -= lagrange
            result["gradient"] = gradient.tolist()
            result["objective"] = float(
                phase["phase_objective"]
                + lagrange * (float(feed_u) - phase["modified_fraction"])
            )
            return result

        starts = [(tuple(start), "deterministic") for start in deterministic_starts]
        if warm_start is not None:
            starts.insert(0, (warm_start, "warm_start"))
        attempts = _run_stage2_lower(
            lower_evaluator,
            starts,
            coordinate_bounds,
            basin_memory,
            force_failure=force_failure,
        )
        certified = [
            attempt for attempt in attempts
            if attempt["numerical_convergence"] == "passed"
            and attempt["physical_validity"] == "passed"
        ]
        for attempt in attempts:
            attempt["improving"] = False
            attempt["distinct"] = False
            attempt["admitted"] = False
        admitted_cut = None
        if certified:
            best = min(certified, key=lambda attempt: attempt["objective"])
            warm_start = best["solution"]
            distinct = all(
                abs(best["modified_fraction"] - cut["modified_fraction"])
                >= tolerances["cut_distinct_u"]
                or abs(best["packing_fraction"] - cut["packing_fraction"])
                >= tolerances["cut_distinct_eta"]
                for cut in cuts
            )
            improving = bool(
                best["objective"]
                < float(upper["upper_objective"]) - tolerances["improvement"]
            )
            best["distinct"] = distinct
            best["improving"] = improving
            if distinct and improving:
                identifier = f"C{sum(cut['id'].startswith('C') for cut in cuts) + 1}"
                cut = _cut_from_phase(identifier, best)
                cuts.append(cut)
                admitted_cut = identifier
                best["admitted"] = True
        step6 = _step6_select(
            cuts, feed_u, upper, tolerances, force_empty=force_mstar_empty
        )
        mstar_ids = set(step6["candidate_ids"])
        mstar = [cut for cut in cuts if cut["id"] in mstar_ids]
        majors.append({
            "major_index": major_index,
            "event_order": (
                "upper_lp",
                "lower_search",
                "cut_admission",
                "step6",
            ),
            "upper_lp": upper,
            "lower_attempts": attempts,
            "admitted_cut": admitted_cut,
            "step6": step6,
        })
        if len(mstar) > 1:
            return {
                "outcome": "ready_stage3",
                "stage3_status": "ready",
                "physical_status": "not_adjudicated",
                "search_status": "completed_finite" if all(
                    attempt["numerical_convergence"] == "passed"
                    for major in majors for attempt in major["lower_attempts"]
                ) else "partial",
                "cuts": cuts,
                "cut_order": [cut["id"] for cut in cuts],
                "majors": majors,
                "mstar": mstar,
            }
        if admitted_cut is None:
            outcome = (
                "no_certified_improving_cut" if not certified else "mstar_empty"
            )
            return {
                "outcome": outcome,
                "stage3_status": "not_run",
                "physical_status": "not_adjudicated",
                "search_status": "partial" if not certified else "completed_finite",
                "cuts": cuts,
                "cut_order": [cut["id"] for cut in cuts],
                "majors": majors,
                "mstar": mstar,
            }
    return {
        "outcome": "resource_limited",
        "stage3_status": "not_run",
        "physical_status": "not_adjudicated",
        "search_status": "partial",
        "cuts": cuts,
        "cut_order": [cut["id"] for cut in cuts],
        "majors": majors,
        "mstar": [],
    }


def _manufactured_stage2_phase(point, single_well=False):
    u, q = float(point[0]), float(point[1])
    common_lagrange = -1.0 / 60.0
    if single_well:
        phase_objective = (u - 0.5)**2 + q*q
        composition_gradient = 2.0 * (u - 0.5)
        composition_curvature = 2.0
    else:
        left = u - 0.2
        right = u - 0.8
        phase_objective = 1000.0 * left*left * right*right + common_lagrange * left + q*q
        composition_gradient = (
            2000.0 * left * right * (2.0*u - 1.0) + common_lagrange
        )
        composition_curvature = 2000.0 * (
            (2.0*u - 1.0)**2 + 2.0 * left * right
        )
    return {
        "phase_objective": float(phase_objective),
        "objective": float(phase_objective),
        "gradient": (float(composition_gradient), float(2.0*q)),
        "hessian": ((float(composition_curvature), 0.0), (0.0, 2.0)),
        "composition_gradient_fixed_volume": float(composition_gradient),
        "q_stationarity": float(2.0*q),
        "modified_fraction": u,
        "log_volume": q,
        "volume": math.exp(q),
        "packing_fraction": float(1.0 / (1.0 + math.exp(q))),
        "charge_residual": 0.0,
        "relative_pressure_residual": 0.0,
        "final_eos_evaluation": "passed",
    }


def manufactured_stage2_demo(case):
    name = str(case)
    tolerances = {
        "epsilon_b": 1.0e-7,
        "epsilon_lambda": 1.0e-4,
        "epsilon_q": 1.0e-8,
        "epsilon_x": 1.0e-3,
        "epsilon_eta": 1.0e-3,
        "cut_distinct_u": 1.0e-6,
        "cut_distinct_eta": 1.0e-6,
        "improvement": 1.0e-9,
    }
    if name == "resource_limited":
        return _solve_stage2_controller(
            _manufactured_stage2_phase,
            0.5,
            (("feed", (0.5, 0.0)), ("witness", (0.2, 0.0))),
            ((0.2, 0.0), (0.8, 0.0), (0.5, 0.2)),
            ((1.0e-6, 1.0 - 1.0e-6), (-1.0, 1.0)),
            (-1.0 / 60.0 - 1.0e-6, -1.0 / 60.0 + 1.0e-6),
            0,
            tolerances,
        )
    if name == "no_certified_cut":
        return _solve_stage2_controller(
            _manufactured_stage2_phase,
            0.5,
            (("feed", (0.5, 0.0)), ("witness", (0.2, 0.0))),
            ((0.2, 0.0), (0.8, 0.0)),
            ((1.0e-6, 1.0 - 1.0e-6), (-1.0, 1.0)),
            (-1.0 / 60.0 - 1.0e-6, -1.0 / 60.0 + 1.0e-6),
            1,
            tolerances,
            force_failure=True,
        )
    if name == "mstar_empty":
        return _solve_stage2_controller(
            lambda point: _manufactured_stage2_phase(point, single_well=True),
            0.5,
            (("feed", (0.5, 0.0)),),
            ((0.5, 0.0), (0.4, 0.2)),
            ((1.0e-6, 1.0 - 1.0e-6), (-1.0, 1.0)),
            (0.0, 0.0),
            1,
            tolerances,
            force_mstar_empty=True,
        )
    if name != "two_phase":
        raise ValueError("unknown manufactured Stage-II case")
    return _solve_stage2_controller(
        _manufactured_stage2_phase,
        0.5,
        (("feed", (0.5, 0.0)), ("witness", (0.2, 0.0))),
        ((0.2, 0.0), (0.8, 0.0), (0.5, 0.2)),
        ((1.0e-6, 1.0 - 1.0e-6), (-1.0, 1.0)),
        (-1.0 / 60.0 - 1.0e-6, -1.0 / 60.0 + 1.0e-6),
        4,
        tolerances,
    )


def solve_stage2(
    temperature,
    pressure,
    feed_amounts,
    initial_candidates,
    volume_bounds,
    starts,
    lagrange_bounds,
    max_major=20,
):
    feed_u = modified_fraction(feed_amounts)
    lower_volume, upper_volume = (
        float(volume_bounds[0]), float(volume_bounds[1])
    )
    if not (0.0 < lower_volume < upper_volume):
        raise ValueError("volume bounds must be positive and increasing")
    initial_points = []
    for candidate in initial_candidates:
        identifier = str(candidate["id"])
        if "log_volume" in candidate:
            q = float(candidate["log_volume"])
        else:
            q = math.log(float(candidate["volume"]))
        initial_points.append((identifier, (float(candidate["modified_fraction"]), q)))
    if {identifier for identifier, _ in initial_points}.isdisjoint({"feed"}):
        raise ValueError("initial candidates must include the feed reference")
    tolerances = {
        "epsilon_b": 1.0e-8,
        "epsilon_lambda": 1.0e-6,
        "epsilon_q": 1.0e-8,
        "epsilon_x": 1.0e-3,
        "epsilon_eta": 1.0e-3,
        "cut_distinct_u": 1.0e-6,
        "cut_distinct_eta": 1.0e-6,
        "improvement": 1.0e-10,
    }
    return _solve_stage2_controller(
        lambda point: _stage2_phase_callback(temperature, pressure, point),
        feed_u,
        tuple(initial_points),
        tuple(tuple(float(value) for value in start) for start in starts),
        ((1.0e-8, min(0.38, 1.0 - 1.0e-8)),
         (math.log(lower_volume), math.log(upper_volume))),
        lagrange_bounds,
        max_major,
        tolerances,
    )
