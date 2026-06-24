from __future__ import annotations

import pytest

from epcsaft_equilibrium.branch_tracing import (
    BranchTraceAnchor,
    BranchTraceOptions,
    validate_branch_trace_inputs,
)


def test_branch_trace_options_validate_supported_route_and_anchor_ids() -> None:
    anchors = [
        BranchTraceAnchor(anchor_id="low", coordinate=0.05, source_role="bubble_line", required=True),
        BranchTraceAnchor(anchor_id="high", coordinate=0.25, source_role="bubble_line", required=True),
    ]
    options = BranchTraceOptions(route="bubble_pressure", component_index=1, fixed_variable="T_K", fixed_value=373.15)

    validate_branch_trace_inputs(options, anchors)


def test_branch_trace_options_reject_duplicate_anchor_ids() -> None:
    anchors = [
        BranchTraceAnchor(anchor_id="same", coordinate=0.05, required=True),
        BranchTraceAnchor(anchor_id="same", coordinate=0.25, required=True),
    ]
    options = BranchTraceOptions(route="bubble_pressure", component_index=1, fixed_variable="T_K", fixed_value=373.15)

    with pytest.raises(ValueError, match="duplicate branch trace anchor id"):
        validate_branch_trace_inputs(options, anchors)


def test_branch_trace_options_reject_unsupported_route() -> None:
    anchors = [BranchTraceAnchor(anchor_id="a", coordinate=0.5, required=True)]
    options = BranchTraceOptions(route="flash", component_index=1, fixed_variable="T_K", fixed_value=373.15)

    with pytest.raises(ValueError, match="unsupported branch trace route"):
        validate_branch_trace_inputs(options, anchors)
