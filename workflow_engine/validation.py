"""Pipeline validation helpers."""

from __future__ import annotations

from typing import Dict, List, Set


VALID_ON_ERROR = {"fail", "skip"}


class PipelineValidationError(ValueError):
    pass


def validate_pipeline_data(data: dict) -> None:
    if not isinstance(data, dict):
        raise PipelineValidationError("Pipeline definition must be an object")
    if not data.get("pipeline_id"):
        raise PipelineValidationError("Missing pipeline_id")
    nodes = data.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise PipelineValidationError("Pipeline must define a non-empty nodes list")

    node_ids: Set[str] = set()
    for node in nodes:
        node_id = node.get("node_id")
        action = node.get("action")
        if not node_id:
            raise PipelineValidationError("Node missing node_id")
        if node_id in node_ids:
            raise PipelineValidationError(f"Duplicate node_id: {node_id}")
        node_ids.add(node_id)
        if not action:
            raise PipelineValidationError(f"Node {node_id} missing action")
        retries = node.get("retries", 0)
        if not isinstance(retries, int) or retries < 0:
            raise PipelineValidationError(f"Node {node_id} has invalid retries: {retries}")
        on_error = node.get("on_error", "fail")
        if on_error not in VALID_ON_ERROR:
            raise PipelineValidationError(f"Node {node_id} has invalid on_error policy: {on_error}")

    for edge in data.get("edges", []):
        if not isinstance(edge, list) or len(edge) != 2:
            raise PipelineValidationError(f"Invalid edge: {edge}")
        src, dst = edge
        if src not in node_ids or dst not in node_ids:
            raise PipelineValidationError(f"Edge references unknown node: {edge}")
