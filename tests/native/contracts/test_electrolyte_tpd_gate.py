from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

from epcsaft_equilibrium._native import extension_native_core

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "scripts" / "validation" / "check_electrolyte_tpd_gate.py"


def _load_checker() -> Any:
    assert CHECKER_PATH.is_file(), f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}"
    spec = importlib.util.spec_from_file_location("check_electrolyte_tpd_gate", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_native_electrolyte_tpd_binding_is_exposed() -> None:
    core = extension_native_core()

    assert hasattr(core, "_native_electrolyte_tpd_phase_discovery")


def test_electrolyte_tpd_gate_uses_source_readiness_and_native_candidates() -> None:
    checker = _load_checker()

    payload = checker.evaluate_tpd_gate(
        require_source_gate=True,
        require_held2_readiness=True,
        require_native_tpd=True,
    )

    assert payload["complete"] is True
    assert payload["blockers"] == []
    assert payload["source_gate"]["complete"] is True
    assert payload["held2_readiness_gate"]["complete"] is True
    assert payload["electrolyte_tpd"]["status"] == "charge_neutral_tpd_screening_complete"
    assert payload["electrolyte_tpd"]["stability_checked"] is True
    assert payload["electrolyte_tpd"]["candidate_count"] > 0
    assert payload["electrolyte_tpd"]["selected_candidate_count"] > 0
    assert math.isfinite(float(payload["electrolyte_tpd"]["min_tpd"]))
    assert payload["electrolyte_tpd"]["max_candidate_charge_residual"] <= 1.0e-8
    assert payload["held2_status"]["readiness_only"] is True
    assert payload["held2_status"]["full_held2_claimed"] is False
    assert "held2_dual_phase_discovery" in payload["held2_status"]["pending_gates"]
    assert payload["public_route_state"]["electrolyte_lle"]["production_exposed"] is False
    assert payload["public_route_state"]["electrolyte_lle"]["public_routes"] == []


def test_cli_requires_complete_electrolyte_tpd_gate() -> None:
    assert CHECKER_PATH.is_file(), f"missing checker: {CHECKER_PATH.relative_to(REPO_ROOT)}"

    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            "--json",
            "--require-source-gate",
            "--require-held2-readiness",
            "--require-native-tpd",
            "--require-complete",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["complete"] is True
    assert payload["blockers"] == []
