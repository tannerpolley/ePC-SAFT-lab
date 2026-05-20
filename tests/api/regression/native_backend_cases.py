from __future__ import annotations

import numpy as np

import epcsaft.regression as regression_module


def _minimal_nacl_records():
    return [
        {
            "T": 298.15,
            "P": 101325.0,
            "x_H2O": 0.996,
            "x_Na+": 0.002,
            "x_Cl-": 0.002,
            "osmotic_coefficient": 0.974,
            "mean_ionic_activity": 0.922,
        }
    ]

def _patch_native_generic_ceres_runner(monkeypatch, *, omit_result_keys=()):
    calls = []

    def fake_runner(
        fixed_payloads,
        native_records,
        optimization_names,
        species,
        theta0,
        lower,
        upper,
        *,
        component=None,
        pair=None,
        max_nfev=200,
    ):
        calls.append(
            {
                "fixed_payloads": fixed_payloads,
                "native_records": native_records,
                "optimization_names": tuple(optimization_names),
                "species": tuple(species),
                "theta0": np.asarray(theta0, dtype=float),
                "lower": np.asarray(lower, dtype=float),
                "upper": np.asarray(upper, dtype=float),
                "component": component,
                "pair": pair,
                "max_nfev": int(max_nfev),
            }
        )
        metrics = {str(record["term_name"]): 0.0 for record in native_records}
        if not metrics:
            metrics = {"residual": 0.0}
        result = {
            "x": np.asarray(theta0, dtype=float),
            "cost": 0.0,
            "residual_norm": 0.0,
            "initial_cost": 0.0,
            "initial_residual_norm": 0.0,
            "metrics_by_term": metrics,
            "success": True,
            "status": 1,
            "nfev": 1,
            "iterations": 0,
            "starts_tried": 1,
            "message": "patched native generic Ceres regression",
            "backend": "ceres",
            "optimizer_backend": "ceres",
            "derivative_backend": "cppad_implicit",
            "jacobian_available": True,
            "jacobian_backend": "cppad_implicit",
        }
        for key in omit_result_keys:
            result.pop(key, None)
        return result

    monkeypatch.setattr(regression_module, "_run_native_generic_ceres", fake_runner)
    return calls
