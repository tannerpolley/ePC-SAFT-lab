import numpy as np

import cppad_py
import cyipopt


def dependency_probe():
    point = np.array([2.0], dtype=float)
    independent = cppad_py.independent(point)

    dependent = np.empty(1, dtype=cppad_py.a_double)
    dependent[0] = independent[0] * independent[0]
    function = cppad_py.d_fun(independent, dependent)

    point[0] = 3.0
    return {
        "cppad_value": float(function.forward(0, point)[0]),
        "cppad_jacobian": float(function.jacobian(point)[0, 0]),
        "cyipopt_module": cyipopt.__name__,
    }
