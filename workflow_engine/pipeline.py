"""Minimal DAG-style workflow engine extracted for memory-master."""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .context import WorkflowContext, get_context

ActionHandler = Callable[..., Dict[str, Any]]


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class WorkflowNode:
    node_id: str
    action: str
    inputs: Dict[str, str] = field(default_factory=dict)
    outputs: List[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class WorkflowPipeline:
    pipeline_id: str
    name: str
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)

    def add_node(self, node: WorkflowNode) -> "WorkflowPipeline":
        self.nodes[node.node_id] = node
        return self

    def add_edge(self, from_node: str, to_node: str) -> "WorkflowPipeline":
        self.edges.setdefault(from_node, []).append(to_node)
        return self


class WorkflowEngine:
    def __init__(
        self,
        actions: Dict[str, ActionHandler],
        context: Optional[WorkflowContext] = None,
    ):
        self.actions = actions
        self.context = context or get_context()
        self._callbacks: List[Callable[[str, Dict[str, Any]], Awaitable[None] | None]] = []

    def on_node_complete(self, callback: Callable[[str, Dict[str, Any]], Awaitable[None] | None]):
        self._callbacks.append(callback)

    async def execute(self, pipeline: WorkflowPipeline) -> Dict[str, Any]:
        order = self._topological_sort(pipeline)
        for node_id in order:
            node = pipeline.nodes[node_id]
            await self._execute_node(node, pipeline)
            payload = {
                "status": node.status.value,
                "outputs": node.result,
                "error": node.error,
            }
            for cb in self._callbacks:
                maybe = cb(node_id, payload)
                if asyncio.iscoroutine(maybe):
                    asyncio.create_task(maybe)
            if node.status == NodeStatus.FAILED:
                raise RuntimeError(f"Pipeline failed at node {node_id}: {node.error}")
        return {nid: node.result for nid, node in pipeline.nodes.items() if node.status == NodeStatus.SUCCESS}

    def _topological_sort(self, pipeline: WorkflowPipeline) -> List[str]:
        in_degree = {node_id: 0 for node_id in pipeline.nodes}
        for _, targets in pipeline.edges.items():
            for target in targets:
                in_degree[target] += 1
        queue = deque([n for n, d in in_degree.items() if d == 0])
        result: List[str] = []
        while queue:
            node_id = queue.popleft()
            result.append(node_id)
            for nxt in pipeline.edges.get(node_id, []):
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)
        if len(result) != len(pipeline.nodes):
            raise ValueError("Workflow contains cycles")
        return result

    async def _execute_node(self, node: WorkflowNode, pipeline: WorkflowPipeline) -> None:
        node.status = NodeStatus.RUNNING
        try:
            kwargs = await self._resolve_inputs(node, pipeline)
            if node.action not in self.actions:
                raise KeyError(f"Unknown action: {node.action}")
            result = self.actions[node.action](**kwargs) or {}
            if not isinstance(result, dict):
                result = {"value": result}
            for key in node.outputs:
                if key in result:
                    await self.context.set(f"{node.node_id}.{key}", result[key])
            node.result = result
            node.status = NodeStatus.SUCCESS
        except Exception as exc:
            node.error = str(exc)
            node.status = NodeStatus.FAILED

    async def _resolve_inputs(self, node: WorkflowNode, pipeline: WorkflowPipeline) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {}
        for param, source in node.inputs.items():
            if "." in source:
                source_node_id, output_key = source.split(".", 1)
                source_node = pipeline.nodes.get(source_node_id)
                if source_node and source_node.status == NodeStatus.SUCCESS:
                    kwargs[param] = source_node.result.get(output_key)
                else:
                    kwargs[param] = await self.context.get(f"{source_node_id}.{output_key}")
            else:
                kwargs[param] = self._coerce_literal(source)
        return kwargs

    @staticmethod
    def _coerce_literal(value: Any) -> Any:
        if not isinstance(value, str):
            return value
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value


async def run_pipeline(pipeline: WorkflowPipeline, actions: Dict[str, ActionHandler]) -> Dict[str, Any]:
    engine = WorkflowEngine(actions=actions)
    return await engine.execute(pipeline)
