from __future__ import annotations


def require_epcsaft_install() -> None:
    try:
        import epcsaft
        import epcsaft.model.datasets
        from epcsaft import (
            Mixture,
            State,
        )
    except Exception as exc:
        raise RuntimeError(
            "epcsaft must be importable from the active environment with the reset frontend API. "
            "Run `uv sync --no-install-workspace`, then `uv run python scripts/dev/build_epcsaft.py`, then retry."
        ) from exc
