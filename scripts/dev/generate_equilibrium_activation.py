"""Generate the Python mirror of the native equilibrium activation matrix."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import pprint
import shlex
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validation import native_freshness

SRC_ROOT = REPO_ROOT / "packages" / "epcsaft" / "src"
EQUILIBRIUM_SRC_ROOT = REPO_ROOT / "packages" / "epcsaft-equilibrium" / "src"
OUTPUT = (
    REPO_ROOT
    / "packages"
    / "epcsaft-equilibrium"
    / "src"
    / "epcsaft_equilibrium"
    / "equilibrium_activation.py"
)

_REPO_PATH_PREFIXES = ("analyses/", "data/", "docs/", "packages/", "scripts/", "tests/")
_RECEIPT_OWNER_PATHS = (
    "packages/epcsaft-equilibrium/src/epcsaft_equilibrium/capability_evidence.py",
    "scripts/dev/generate_equilibrium_activation.py",
)


def _require_fresh_native_metadata(native_core: object) -> dict[str, object]:
    receipt = native_freshness.build_equilibrium_native_receipt(
        native_module=native_core,
        checker_command=[
            "uv",
            "run",
            "--no-sync",
            "python",
            "scripts/dev/generate_equilibrium_activation.py",
            "--check",
        ],
    )
    try:
        native_freshness.require_equilibrium_native_fresh(receipt)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc
    return receipt


def _load_native_metadata() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))
    if str(EQUILIBRIUM_SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(EQUILIBRIUM_SRC_ROOT))

    from scripts.dev.native_runtime_env import apply_native_runtime_env

    apply_native_runtime_env(os.environ)
    native_candidates = sorted(EQUILIBRIUM_SRC_ROOT.glob("epcsaft_equilibrium/_native_core*.so"))
    if len(native_candidates) != 1:
        raise RuntimeError(
            "Expected exactly one built equilibrium native extension before generating "
            f"activation metadata, found {len(native_candidates)}."
        )
    spec = importlib.util.spec_from_file_location("_native_core", native_candidates[0])
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the built equilibrium native extension.")
    native_core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native_core)
    _require_fresh_native_metadata(native_core)
    return (
        [dict(row) for row in native_core._native_equilibrium_activation_matrix()],
        [dict(row) for row in native_core._native_equilibrium_selector_route_contracts()],
    )


def _production_proof_registry() -> dict[str, dict[str, object]]:
    if str(EQUILIBRIUM_SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(EQUILIBRIUM_SRC_ROOT))
    from epcsaft_equilibrium.capability_evidence import (
        CAPABILITY_EVIDENCE_BY_FAMILY,
        PROOF_EVIDENCE_BY_ID,
    )

    proof_ids = {
        str(proof_id)
        for family in CAPABILITY_EVIDENCE_BY_FAMILY.values()
        for proof_id in family["proof_ids"]
    }
    return {
        proof_id: dict(PROOF_EVIDENCE_BY_ID[proof_id])
        for proof_id in PROOF_EVIDENCE_BY_ID
        if proof_id in proof_ids
    }


def _execute_strict_checker(command: str) -> dict[str, object]:
    completed = subprocess.run(
        shlex.split(command),
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(
            f"Strict equilibrium proof checker failed with exit code {completed.returncode}: "
            f"{command}\n{detail}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Strict equilibrium proof checker emitted invalid JSON: {command}") from exc
    if not isinstance(payload, Mapping):
        raise RuntimeError(f"Strict equilibrium proof checker emitted a non-object payload: {command}")
    blockers = payload.get("blockers")
    if payload.get("complete") is not True or blockers != []:
        raise RuntimeError(
            f"Strict equilibrium proof checker did not report complete evidence: {command}"
        )
    freshness = payload.get("native_freshness_receipt")
    if not isinstance(freshness, Mapping):
        raise RuntimeError(f"Strict equilibrium proof checker omitted native freshness: {command}")
    current_identity = str(freshness.get("current_source_identity", ""))
    embedded_identity = str(freshness.get("embedded_source_identity", ""))
    if (
        freshness.get("freshness_mode") != "embedded_source_identity"
        or freshness.get("source_identity_matches") is not True
        or not current_identity
        or current_identity != embedded_identity
    ):
        raise RuntimeError(
            f"Strict equilibrium proof checker did not use the current embedded source identity: {command}"
        )
    checker = str(payload.get("checker", "")).strip()
    if not checker:
        raise RuntimeError(f"Strict equilibrium proof checker omitted its checker identity: {command}")
    return {
        "command": command,
        "checker": checker,
        "complete": True,
        "status": "passed",
        "reported_status": payload.get("status"),
        "blockers": [],
        "freshness_mode": freshness["freshness_mode"],
        "source_identity_matches": True,
        "current_source_identity": current_identity,
        "embedded_source_identity": embedded_identity,
    }


def _proof_file_paths(proof: Mapping[str, object]) -> list[str]:
    relative_paths = set(_RECEIPT_OWNER_PATHS)
    relative_paths.update(str(path) for path in proof.get("artifact_paths", ()))
    relative_paths.update(
        str(path)
        for path in proof.get("data_sources", ())
        if str(path).startswith(_REPO_PATH_PREFIXES)
    )
    relative_paths.update(str(node).partition("::")[0] for node in proof.get("proof_nodes", ()))
    for command in proof.get("strict_checkers", ()):
        relative_paths.update(
            token.partition("::")[0]
            for token in shlex.split(str(command))
            if ".py" in token and token.partition("::")[0].startswith(_REPO_PATH_PREFIXES)
        )
    return sorted(relative_paths)


def _proof_evidence_digest(proof_id: str, proof: Mapping[str, object]) -> str:
    digest = hashlib.sha256()
    digest.update(proof_id.encode("utf-8"))
    digest.update(b"\0")
    digest.update(json.dumps(proof, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    digest.update(b"\0")
    for relative in _proof_file_paths(proof):
        path = (REPO_ROOT / relative).resolve()
        try:
            path.relative_to(REPO_ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(f"Equilibrium proof evidence path escapes the repository: {relative}") from exc
        if not path.is_file():
            raise RuntimeError(f"Equilibrium proof evidence file is missing: {relative}")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def _generate_proof_execution_receipts() -> dict[str, dict[str, object]]:
    registry = _production_proof_registry()
    commands = dict.fromkeys(
        str(command)
        for proof in registry.values()
        for command in proof["strict_checkers"]
    )
    checker_receipts = {command: _execute_strict_checker(command) for command in commands}
    return {
        proof_id: {
            "status": "passed",
            "strict_checkers": [str(command) for command in proof["strict_checkers"]],
            "checker_receipts": [
                checker_receipts[str(command)] for command in proof["strict_checkers"]
            ],
            "evidence_digest": _proof_evidence_digest(proof_id, proof),
        }
        for proof_id, proof in registry.items()
    }


def _render(
    rows: list[dict[str, object]],
    selector_routes: list[dict[str, object]],
    proof_execution_receipts: dict[str, dict[str, object]],
) -> str:
    activation_payload = pprint.pformat(rows, width=100, sort_dicts=False)
    route_payload = pprint.pformat(selector_routes, width=100, sort_dicts=False)
    receipt_payload = pprint.pformat(proof_execution_receipts, width=100, sort_dicts=False)
    return (
        '"""Generated mirror of native equilibrium activation metadata."""\n\n'
        "from __future__ import annotations\n\n"
        "# Generated by scripts/dev/generate_equilibrium_activation.py from native C++ metadata.\n"
        f"EQUILIBRIUM_ACTIVATION_MATRIX = {activation_payload}\n\n"
        f"EQUILIBRIUM_SELECTOR_ROUTE_CONTRACTS = {route_payload}\n\n"
        f"EQUILIBRIUM_PROOF_EXECUTION_RECEIPTS = {receipt_payload}\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the tracked mirror is stale")
    args = parser.parse_args(argv)

    rendered = _render(*_load_native_metadata(), _generate_proof_execution_receipts())
    if args.check:
        existing = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if existing != rendered:
            print(f"{OUTPUT.relative_to(REPO_ROOT)} is stale", file=sys.stderr)
            return 1
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
