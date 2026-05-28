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
    TEST_SLICES,
    VALIDATION_LANES,
)


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


def _capability_evidence_summary(derivative_coverage: dict[str, object]) -> dict[str, object]:
    derivative_rows = derivative_coverage.get("rows", [])
    return {
        "source": "registered_capability_evidence",
        "derivative_row_count": len(derivative_rows) if isinstance(derivative_rows, list) else 0,
        "pytest_slices": list(TEST_SLICES),
        "validation_lanes": list(VALIDATION_LANES),
        "cheap_validation_lanes": [name for name, lane in VALIDATION_LANES.items() if bool(lane["cheap_by_default"])],
    }


def _derivative_coverage_capabilities(cppad: dict[str, object]) -> dict[str, object]:
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
    }


def capabilities() -> dict[str, object]:
    """Return structured availability flags for high-level package workflows."""

    build_info = runtime_build_info()
    native_dependencies = build_info["native_dependencies"]  # type: ignore[index]
    cppad = dict(native_dependencies["cppad"])  # type: ignore[index]
    cppad_capability = {
        **cppad,
        "scope": "package-wide AD substrate; production derivative routes are listed in coverage_matrix",
    }
    derivative_coverage = _derivative_coverage_capabilities(cppad)
    return {
        "capability_report_owner": "epcsaft",
        "package": "epcsaft",
        "owner": "core_provider",
        "contract_id": "provider_api_v1",
        "native_sdk_contract_id": "provider_native_sdk_v1",
        "native_sdk_target": "epcsaft_provider_native",
        "native_dependencies": {
            "cppad": cppad_capability,
        },
        "reports_only_provider_capabilities_after_split": True,
        "native_extension": bool(build_info["native_extension_available"]),
        "capability_evidence": _capability_evidence_summary(derivative_coverage),
        "derivatives": {
            "cppad": cppad_capability,
            "coverage_matrix": derivative_coverage,
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
    }


__git_commit__ = str(runtime_build_info()["source_git_commit"])
