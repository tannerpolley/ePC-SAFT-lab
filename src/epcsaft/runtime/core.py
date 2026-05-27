"""Runtime metadata and capability discovery for downstream applications."""

from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from functools import lru_cache
from importlib import metadata
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

from .capability_evidence import (
    DERIVATIVE_COVERAGE_ROWS,
    EQUILIBRIUM_PROBLEM_OBJECT_CLASSES,
    EQUILIBRIUM_ROUTE_DERIVATIVE_EVIDENCE,
    REGRESSION_CAPABILITY_DIMENSIONS,
    REGRESSION_CAPABILITY_KEYS,
    REGRESSION_CAPABILITY_REVISIT_AFTER,
    REGRESSION_TARGET_KIND_EVIDENCE,
    TEST_SLICES,
    VALIDATION_LANES,
    public_ipopt_route_family_map,
    public_ipopt_routes_by_family,
    registered_ipopt_public_routes,
)
from .equilibrium_activation import EQUILIBRIUM_ACTIVATION_MATRIX


def _package_version() -> str:
    try:
        return metadata.version("epcsaft")
    except metadata.PackageNotFoundError:
        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        if pyproject.exists():
            match = re.search(
                r'(?m)^version\s*=\s*"([^"]+)"',
                pyproject.read_text(encoding="utf-8", errors="replace"),
            )
            if match:
                return match.group(1)
        return "0+unknown"


__version__ = _package_version()


def _direct_url_payload() -> dict:
    try:
        text = metadata.distribution("epcsaft").read_text("direct_url.json")
    except metadata.PackageNotFoundError:
        return {}
    if not text:
        return {}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _path_from_file_url(url: str | None) -> Path | None:
    if not url:
        return None
    parsed = urlparse(str(url))
    if parsed.scheme != "file":
        return None
    raw_path = unquote(parsed.path)
    if parsed.netloc:
        raw_path = f"//{parsed.netloc}{raw_path}"
    return Path(url2pathname(raw_path))


def _source_checkout_from_package() -> Path | None:
    package_path = Path(__file__).resolve()
    for candidate in (package_path.parents[2], package_path.parents[1]):
        if (candidate / ".git").exists():
            return candidate
    return None


def _source_checkout_from_direct_url(payload: dict) -> Path | None:
    source = _path_from_file_url(payload.get("url"))
    if source is None:
        return None
    if source.is_file():
        source = source.parent
    for candidate in (source, *source.parents):
        if (candidate / ".git").exists():
            return candidate
    return source if source.exists() else None


def _git_commit(source_root: Path | None) -> str:
    if source_root is None or not source_root.exists():
        return "unknown"
    try:
        completed = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "--short=12", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2.0,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    commit = completed.stdout.strip()
    return commit if completed.returncode == 0 and commit else "unknown"


def _native_extension_path() -> Path | None:
    try:
        from .. import _core
    except (ImportError, OSError):
        return None
    return Path(_core.__file__).resolve()


def _platform_label() -> str:
    if os.name == "nt":
        return sys.platform
    return platform.platform()


def _machine_label() -> str:
    if os.name == "nt":
        return os.environ.get("PROCESSOR_ARCHITECTURE", "unknown")
    return platform.machine()


def _native_cppad_backend_info() -> dict[str, object]:
    try:
        from .. import _core
    except (ImportError, OSError):
        return {
            "backend": "cppad",
            "status": "required_native_extension_missing",
            "required": True,
            "compiled": False,
            "available": False,
        }
    try:
        smoke = _core._native_cppad_smoke()
    except AttributeError:
        return {
            "backend": "cppad",
            "status": "required_cppad_smoke_missing",
            "required": True,
            "compiled": False,
            "available": False,
        }
    status = str(smoke.get("status", "required_cppad_status_missing"))
    compiled = bool(smoke.get("cppad_compiled", False))
    return {
        "backend": "cppad",
        "status": status,
        "required": True,
        "compiled": compiled,
        "available": status == "enabled_available" and compiled,
    }


def _native_ceres_backend_info() -> dict[str, object]:
    try:
        from .. import _core
    except (ImportError, OSError):
        return {
            "backend": "ceres",
            "status": "native_extension_missing",
            "required": False,
            "required_for": ["epcsaft-regression"],
            "compiled": False,
            "available": False,
        }
    try:
        smoke = _core._native_ceres_smoke()
    except AttributeError:
        return {
            "backend": "ceres",
            "status": "ceres_probe_missing",
            "required": False,
            "required_for": ["epcsaft-regression"],
            "compiled": False,
            "available": False,
        }
    status = str(smoke.get("status", "ceres_probe_missing"))
    compiled = bool(smoke.get("compiled", False))
    return {
        "backend": "ceres",
        "status": status,
        "required": False,
        "required_for": ["epcsaft-regression"],
        "compiled": compiled,
        "available": status == "enabled_available" and compiled,
    }


def _native_ipopt_backend_info() -> dict[str, object]:
    try:
        from .. import _core
    except (ImportError, OSError):
        return {
            "backend": "ipopt",
            "status": "native_extension_missing",
            "required": False,
            "compiled": False,
            "available": False,
            "adapter_available": False,
            "adapter_kind": "native_tnlp_adapter",
            "adapter_source_available": False,
            "requires_exact_gradient": True,
            "requires_exact_jacobian": True,
        }
    try:
        smoke = _core._native_ipopt_smoke()
    except AttributeError:
        return {
            "backend": "ipopt",
            "status": "ipopt_probe_missing",
            "required": False,
            "compiled": False,
            "available": False,
            "adapter_available": False,
            "adapter_kind": "native_tnlp_adapter",
            "adapter_source_available": False,
            "requires_exact_gradient": True,
            "requires_exact_jacobian": True,
        }
    status = str(smoke.get("status", "ipopt_probe_missing"))
    compiled = bool(smoke.get("compiled", False))
    return {
        "backend": "ipopt",
        "status": status,
        "required": False,
        "compiled": compiled,
        "available": status == "enabled_available" and compiled,
        "adapter_available": bool(smoke.get("adapter_available", False)),
        "adapter_kind": str(smoke.get("adapter_kind", "native_tnlp_adapter")),
        "adapter_source_available": bool(smoke.get("adapter_source_available", False)),
        "requires_exact_gradient": bool(smoke.get("requires_exact_gradient", True)),
        "requires_exact_jacobian": bool(smoke.get("requires_exact_jacobian", True)),
    }


def _mtime_utc(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()


@lru_cache(maxsize=1)
def runtime_build_info() -> dict[str, object]:
    """Return JSON-like package, source, and native-extension metadata."""

    direct_url = _direct_url_payload()
    source_root = _source_checkout_from_package() or _source_checkout_from_direct_url(direct_url)
    native_path = _native_extension_path()
    ceres = _native_ceres_backend_info()
    direct_url_info = direct_url.get("dir_info") if isinstance(direct_url.get("dir_info"), dict) else {}
    return {
        "package_version": __version__,
        "source_git_commit": _git_commit(source_root),
        "source_root": None if source_root is None else str(source_root),
        "direct_url": direct_url.get("url"),
        "editable": bool(direct_url_info.get("editable", False)),
        "package_file": str(Path(__file__).resolve()),
        "native_extension": None if native_path is None else str(native_path),
        "native_extension_available": native_path is not None,
        "native_extension_mtime_utc": None if native_path is None else _mtime_utc(native_path),
        "python": sys.version.split()[0],
        "platform": _platform_label(),
        "machine": _machine_label(),
        "native_dependencies": {
            "ceres": ceres,
            "cppad": _native_cppad_backend_info(),
            "ipopt": _native_ipopt_backend_info(),
        },
    }


def _capability_value(value: object) -> object:
    if isinstance(value, tuple):
        return [_capability_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _capability_value(item) for key, item in value.items()}
    return value


def _registered_ipopt_public_routes() -> list[str]:
    return registered_ipopt_public_routes()


def _equilibrium_activation_capabilities(*, ipopt_route_available: bool) -> dict[str, object]:
    rows = [_capability_value(row) for row in EQUILIBRIUM_ACTIVATION_MATRIX]
    production_families = [str(row["key"]) for row in rows if bool(row["production_exposed"])]
    declared_not_exposed = [str(row["key"]) for row in rows if str(row["exposure_status"]) == "declared_not_exposed"]
    public_routes_by_family = {
        family: list(routes) for family, routes in public_ipopt_routes_by_family().items()
    }
    public_route_family_map = public_ipopt_route_family_map()
    return {
        "source": "native_cpp",
        "rows": rows,
        "production_families": production_families,
        "declared_not_exposed_families": declared_not_exposed,
        "public_routes": _registered_ipopt_public_routes(),
        "public_routes_by_family": public_routes_by_family,
        "public_route_family_map": dict(sorted(public_route_family_map.items())),
        "ipopt_available": ipopt_route_available,
    }


def _capability_evidence_summary(
    derivative_coverage: dict[str, object],
    activation: dict[str, object],
    regression_target_evidence: dict[str, object],
) -> dict[str, object]:
    derivative_rows = derivative_coverage.get("rows", [])
    regression_target_rows = regression_target_evidence.get("rows", [])
    return {
        "source": "registered_capability_evidence",
        "equilibrium_keys": list(activation["production_families"]),
        "equilibrium_route_derivative_row_count": len(EQUILIBRIUM_ROUTE_DERIVATIVE_EVIDENCE),
        "ipopt_public_routes": list(activation["public_routes"]),
        "declared_not_exposed_equilibrium_keys": list(activation["declared_not_exposed_families"]),
        "problem_object_classes": list(EQUILIBRIUM_PROBLEM_OBJECT_CLASSES),
        "regression_keys": list(REGRESSION_CAPABILITY_KEYS),
        "regression_claim_dimensions": list(REGRESSION_CAPABILITY_DIMENSIONS),
        "regression_target_kind_row_count": (
            len(regression_target_rows) if isinstance(regression_target_rows, list) else 0
        ),
        "derivative_row_count": len(derivative_rows) if isinstance(derivative_rows, list) else 0,
        "pytest_slices": list(TEST_SLICES),
        "validation_lanes": list(VALIDATION_LANES),
        "cheap_validation_lanes": [name for name, lane in VALIDATION_LANES.items() if bool(lane["cheap_by_default"])],
    }


def _derivative_coverage_capabilities(cppad: dict[str, object], ceres: dict[str, object]) -> dict[str, object]:
    cppad_available = bool(cppad.get("available", False))
    ceres_available = bool(ceres.get("available", False))
    coverage_rows = [_capability_value(row) for row in DERIVATIVE_COVERAGE_ROWS]
    return {
        "derivative_coverage_matrix_available": True,
        "implemented_routes_only": True,
        "minimum_columns": [
            "row_family",
            "subsystem",
            "quantity",
            "derivative",
            "backend",
            "supported",
            "classification",
            "reason",
            "tests",
        ],
        "rows": coverage_rows,
        "association_implicit_sensitivities": {
            "available": True,
            "production": True,
            "scope": "validated association solved-state reporting and implicit-sensitivity diagnostics",
        },
        "density_root_implicit_sensitivities": {
            "available": True,
            "production": True,
            "scope": "validated CppAD-implicit density sensitivities used by native regression Jacobians",
        },
        "speciation_implicit_sensitivities": {
            "available": True,
            "production": True,
            "scope": "public frontend requires CppAD-backed solved-state sensitivities; analytic kernels are internal only",
        },
        "born_ssmds_liquid_derivatives": {
            "available": True,
            "production": True,
            "phase_scope": "liquid_electrolyte_only",
            "vapor_support": False,
        },
        "regression_ceres_jacobians": {
            "available": bool(cppad_available and ceres_available),
            "production": bool(cppad_available and ceres_available),
            "routes": list(REGRESSION_CAPABILITY_KEYS),
            "backends": ["cppad_implicit"],
            "requires": ["ceres", "cppad"],
        },
    }


def _regression_target_kind_evidence() -> dict[str, object]:
    rows = [_capability_value(row) for row in REGRESSION_TARGET_KIND_EVIDENCE]
    production_targets = [
        str(row["target_kind"]) for row in rows if bool(row["public_production_supported_target_kind"])
    ]
    registry_only_targets = [
        str(row["target_kind"])
        for row in rows
        if bool(row["registry_known_target_kind"]) and not bool(row["public_production_supported_target_kind"])
    ]
    return {
        "source": "registered_capability_evidence",
        "dimensions": list(REGRESSION_CAPABILITY_DIMENSIONS),
        "revisit_after": list(REGRESSION_CAPABILITY_REVISIT_AFTER),
        "production_supported_target_kinds": production_targets,
        "registry_only_or_pending_target_kinds": registry_only_targets,
        "rows": rows,
    }


def _equilibrium_route_derivative_evidence() -> dict[str, object]:
    return {
        "source": "registered_capability_evidence",
        "implemented_capability_claims_only": False,
        "production_rows_are_capability_safe": True,
        "rows": [_capability_value(row) for row in EQUILIBRIUM_ROUTE_DERIVATIVE_EVIDENCE],
    }


def capabilities() -> dict[str, object]:
    """Return structured availability flags for high-level package workflows."""

    build_info = runtime_build_info()
    native_dependencies = build_info["native_dependencies"]  # type: ignore[index]
    ceres = dict(native_dependencies["ceres"])  # type: ignore[index]
    cppad = dict(native_dependencies["cppad"])  # type: ignore[index]
    ipopt = dict(native_dependencies["ipopt"])  # type: ignore[index]
    ipopt_route_available = bool(ipopt.get("available", False))
    ceres_available = bool(ceres.get("available", False))
    cppad_capability = {
        **cppad,
        "scope": "package-wide AD substrate; production derivative routes are listed in coverage_matrix",
    }
    ceres_capability: dict[str, object] = {
        **ceres,
        "production": ceres_available,
        "scope": "native optimizer backend owned by the regression extension",
        "native_hot_loop": ceres_available,
        "production_routes": ["regression:pure_neutral"],
    }
    if not ceres_available:
        ceres_capability["reason"] = "extension_dependency_missing"
    derivative_coverage = _derivative_coverage_capabilities(cppad, ceres)
    equilibrium_activation = _equilibrium_activation_capabilities(ipopt_route_available=ipopt_route_available)
    ipopt_public_routes = list(equilibrium_activation["public_routes"])
    public_routes_by_family = dict(equilibrium_activation["public_routes_by_family"])
    regression_target_evidence = _regression_target_kind_evidence()
    regression_route_available = bool(ceres_available and cppad_capability.get("available", False))
    provider_view = {
        "package": "epcsaft",
        "owner": "core_provider",
        "contract_id": "provider_api_v1",
        "native_dependencies": {
            "cppad": cppad_capability,
        },
        "reports_only_provider_capabilities_after_split": True,
    }
    equilibrium_view = {
        "package": "epcsaft-equilibrium",
        "owner": "equilibrium_extension",
        "native_dependencies": {
            "cppad": cppad_capability,
            "ipopt": ipopt,
        },
        "requires": ["epcsaft", "cppad", "ipopt"],
        "forbidden_default_dependencies": ["ceres"],
    }
    regression_view = {
        "package": "epcsaft-regression",
        "owner": "regression_extension",
        "native_dependencies": {
            "cppad": cppad_capability,
            "ceres": ceres_capability,
        },
        "requires": ["epcsaft", "cppad", "ceres"],
        "forbidden_default_dependencies": ["ipopt"],
    }
    return {
        "capability_report_owner": "epcsaft-transition-monorepo",
        "package_ownership": {
            "provider": "epcsaft",
            "equilibrium": "epcsaft-equilibrium",
            "regression": "epcsaft-regression",
        },
        "package_views": {
            "provider": provider_view,
            "equilibrium": equilibrium_view,
            "regression": regression_view,
        },
        "native_extension": bool(build_info["native_extension_available"]),
        "capability_evidence": _capability_evidence_summary(
            derivative_coverage,
            equilibrium_activation,
            regression_target_evidence,
        ),
        "derivatives": {
            "cppad": cppad_capability,
            "coverage_matrix": derivative_coverage,
            "equilibrium_route_evidence": _equilibrium_route_derivative_evidence(),
            "ssmds_born_derivatives": {
                "available": True,
                "production": True,
                "backend": "cppad",
                "phase_scope": "liquid_electrolyte_only",
                "parameters": ["d_born", "f_solv"],
                "vapor_support": False,
            },
            "property_derivative_result_apis": {
                "available": True,
                "result_shape": [
                    "supported",
                    "backend",
                    "derivative_backend",
                    "message",
                    "value",
                    "jacobian",
                    "outputs",
                    "variables",
                    "shape",
                ],
                "backend_labels": [
                    "cppad",
                    "cppad_implicit",
                    "cppad_explicit_density",
                ],
                "parameter_families": {
                    "state_property_derivative_supported": [
                        "m",
                        "sigma",
                        "epsilon",
                        "e_assoc",
                        "vol_a",
                        "k_ij",
                        "l_ij",
                        "k_hb_ij",
                        "d_born",
                        "f_solv",
                        "relative_permittivity",
                    ],
                    "regression_public_production_supported": list(
                        regression_target_evidence["production_supported_target_kinds"]
                    ),
                    "not_optimizer_support": [
                        "e_assoc",
                        "vol_a",
                        "l_ij",
                        "k_hb_ij",
                    ],
                    "production_scope": {
                        "e_assoc": "pure_associating_component_parameter_only",
                        "vol_a": "pure_associating_component_parameter_only",
                        "l_ij": "binary_pair_including_active_association",
                        "k_hb_ij": "active_association_binary_pair_only",
                    },
                    "association_affecting_nonproduction": {},
                },
                "state_methods": [
                    "pressure_density_derivative_result",
                    "pressure_composition_derivative_result",
                    "pressure_parameter_derivative_result",
                    "density_pressure_derivative_result",
                    "ares_composition_derivative_result",
                    "chemical_potential_composition_derivative_result",
                    "chemical_potential_parameter_derivative_result",
                    "ln_fugacity_composition_derivative_result",
                    "ln_fugacity_parameter_derivative_result",
                    "activity_composition_derivative_result",
                    "activity_parameter_derivative_result",
                    "relative_permittivity_composition_derivative_result",
                    "relative_permittivity_parameter_derivative_result",
                    "derivative_coverage_matrix",
                ],
            },
        },
        "optimizers": {
            "ceres": ceres_capability,
            "ipopt": {
                **ipopt,
                "solver_backend": "ipopt",
                "production": ipopt_route_available,
                "scope": "native Ipopt dependency for production equilibrium NLP routes",
                "formulations": ["thermodynamic_constrained_nlp"],
                "adapter_available": bool(ipopt.get("adapter_available", False)),
                "adapter_source_available": bool(ipopt.get("adapter_source_available", False)),
                "adapter_kind": ipopt.get("adapter_kind", "native_tnlp_adapter"),
                "public_routes": ipopt_public_routes,
            },
        },
        "equilibrium": {
            "activation_matrix": equilibrium_activation,
            "production_families": list(equilibrium_activation["production_families"]),
            "declared_not_exposed_families": list(equilibrium_activation["declared_not_exposed_families"]),
            "public_routes": ipopt_public_routes,
            "derivative_policy": {
                "accepted_derivative_backends": [
                    "cppad",
                    "cppad_implicit",
                    "cppad_explicit_density",
                ],
                "auto_policy": "public_frontend_forces_cppad_else_raise",
            },
            "bubble_dew_derived_routes": {
                "available": bool(equilibrium_activation["ipopt_available"]),
                "production": True,
                "entrypoint": "Equilibrium(mixture, route=..., ...).solve()",
                "public_routes": public_routes_by_family["bubble_dew_derived_routes"],
                "selector_core": True,
                "input_scope": "neutral non-reactive non-electrolyte non-associating mixtures",
                "requires": ["cppad", "ipopt"],
            },
            "neutral_tp_flash": {
                "available": bool(equilibrium_activation["ipopt_available"]),
                "production": True,
                "entrypoint": "Equilibrium(mixture, route='flash', T=..., P=..., z=...).solve()",
                "public_routes": public_routes_by_family["neutral_tp_flash"],
                "selector_core": True,
                "input_scope": "neutral non-reactive non-electrolyte non-associating two-phase mixtures",
                "requires": ["cppad", "ipopt"],
            },
            "neutral_lle": {
                "available": bool(equilibrium_activation["ipopt_available"]),
                "production": True,
                "entrypoint": "Equilibrium(mixture, route='lle', T=..., P=..., z=...).solve()",
                "public_routes": public_routes_by_family["neutral_lle"],
                "selector_core": True,
                "input_scope": "neutral non-reactive non-electrolyte non-associating liquid/liquid mixtures",
                "requires": ["cppad", "ipopt"],
            },
            "repeated_state_properties": {
                "available": True,
                "helpers": ["evaluate_fugacity_coefficients", "evaluate_fugacity_coefficients_batch"],
                "density_seed_parameter": "rho_guess",
            },
            "problem_objects": {
                "available": True,
                "backend": "constructor_configured_frontend",
                "classes": list(EQUILIBRIUM_PROBLEM_OBJECT_CLASSES),
                "entrypoint": "Equilibrium(mixture, route=..., ...)",
            },
            "contribution_maps": {
                "available": True,
                "backend": "native_term_payloads",
                "families": ["hard_chain", "dispersion", "association", "ionic", "born"],
                "inactive_terms_explicit": True,
            },
            "dataset_validation": {
                "available": True,
                "helper": "validate_dataset_bundle",
                "scope": "external parameter bundle structure and reaction/species consistency checks",
            },
        },
        "regression": {
            "target_kind_evidence": regression_target_evidence,
            "production_supported_target_kinds": list(regression_target_evidence["production_supported_target_kinds"]),
            "pure_neutral": {
                "available": regression_route_available,
                "production": regression_route_available,
                "backend": "native_ceres",
                "entrypoint": "Regression(mixture, ...).fit_pure_neutral(...)",
                "jacobian_backend": "cppad_implicit",
                "target_kinds": ["m", "s", "e"],
            },
            "binary_pair_constant_kij": {
                "available": regression_route_available,
                "production": regression_route_available,
                "backend": "native_ceres",
                "entrypoint": "fit_binary_parameters(..., parameters_to_fit=('k_ij',))",
                "jacobian_backend": "cppad_implicit",
                "target_kinds": ["k_ij"],
            },
            "liquid_electrolyte_born": {
                "available": regression_route_available,
                "production": regression_route_available,
                "backend": "native_ceres",
                "entrypoint": "fit_liquid_electrolyte_parameters(...)",
                "jacobian_backend": "cppad_implicit",
                "target_kinds": ["d_born", "f_solv"],
            },
        },
    }


__git_commit__ = str(runtime_build_info()["source_git_commit"])
