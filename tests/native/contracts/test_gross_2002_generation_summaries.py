from __future__ import annotations

import importlib
import inspect

import pytest


@pytest.mark.parametrize("figure_number", range(2, 11))
def test_gross_generator_persists_render_only_freshness_summary(
    figure_number: int,
) -> None:
    module = importlib.import_module(
        "analyses.paper_validation.2002_gross.figures."
        f"figure_{figure_number:02d}.scripts.generate_data"
    )

    main_source = inspect.getsource(module.main)

    assert "_write_json(SUMMARY_JSON, summary)" in main_source
