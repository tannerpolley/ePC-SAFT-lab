# cython: language_level=3
"""Lab-only HELD2 Stage-I controller over the experiment's thermodynamic tape."""

import math

import cyipopt
import numpy as np

from ._thermo import derivative_bundle, evaluate_state


_R = 8.31446261815324
_PRESSURE_RTOL = 1.0e-8
_NEGATIVE_TPD = -1.0e-8
_DISTINCT_U = 1.0e-6


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
