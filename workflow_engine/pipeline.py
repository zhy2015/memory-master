"""Minimal DAG-style workflow engine extracted for memory-master."""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .context import WorkflowContext, get_context
from .uri import SkillURIRegistry

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
    retries: int = 0
    timeout: Optional[float] = None
    on_error: str = "fail"
    status: NodeStatus = NodeStatus.PENDING
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class WorkflowPipeline:
    pipeline_id: str
    name: str
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)
    on_error: str = "fail"

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
        run_store: Optional[object] = None,
        uri_registry: Optional[SkillURIRegistry] = None,
    ):
        self.actions = actions
        self.context = context or get_context()
        self.run_store = run_store
        self.uri_registry = uri_registry or SkillURIRegistry(actions)
        self._callbacks: List[Callable[[str, Dict[str, Any]], Awaitable[None] | None]] = []

    def on_node_complete(self, callback: Callable[[str, Dict[str, Any]], Awaitable[None] | None]):
        self._callbacks.append(callback)

    async def execute(self, pipeline: WorkflowPipeline, *, resume: bool = False) -> Dict[str, Any]:
        run_id = None
        if resume and self.run_store is not None:
            self._resume_pipeline_state(pipeline)
            try:
                run_id = self.run_store.load_pipeline_state(pipeline.pipeline_id).get("run_id")
            except FileNotFoundError:
                run_id = None
        if self.run_store is not None:
            meta = {"run_id": run_id} if run_id else {}
            self.run_store.save_pipeline_state(pipeline, event="started" if not resume else "resumed", extra=meta)
            if not run_id:
                run_id = self.run_store.load_pipeline_state(pipeline.pipeline_id).get("run_id")
        order = self._topological_sort(pipeline)
        for node_id in order:
            node = pipeline.nodes[node_id]
            if resume and node.status == NodeStatus.SUCCESS:
                continue
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
            if self.run_store is not None:
                self.run_store.save_pipeline_state(pipeline, event=f"node_complete:{node_id}", extra={**payload, "run_id": run_id})
            if node.status == NodeStatus.FAILED:
                if self.run_store is not None:
                    self.run_store.save_pipeline_state(pipeline, event="failed", extra={"node_id": node_id, "error": node.error, "run_id": run_id})
                if pipeline.on_error == "continue":
                    continue
                raise RuntimeError(f"Pipeline failed at node {node_id}: {node.error}")
        result = {nid: node.result for nid, node in pipeline.nodes.items() if node.status == NodeStatus.SUCCESS}
        if self.run_store is not None:
            self.run_store.save_pipeline_state(pipeline, event="completed", extra={"result": result, "run_id": run_id})
        return result


    def _resume_pipeline_state(self, pipeline: WorkflowPipeline) -> None:
        if self.run_store is None:
            return
        try:
            saved = self.run_store.load_pipeline_state(pipeline.pipeline_id)
        except FileNotFoundError:
            return
        saved_nodes = saved.get("pipeline", {}).get("nodes", {})
        for node_id, node_data in saved_nodes.items():
            if node_id not in pipeline.nodes:
                continue
            node = pipeline.nodes[node_id]
            status = node_data.get("status")
            if status == NodeStatus.SUCCESS.value:
                node.status = NodeStatus.SUCCESS
                node.result = node_data.get("result", {})
            elif status == NodeStatus.RUNNING.value:
                node.status = NodeStatus.PENDING
                node.result = {}
                node.error = None

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
        attempt = 0
        last_error = None
        while attempt <= node.retries:
            node.status = NodeStatus.RUNNING
            try:
                kwargs = await self._resolve_inputs(node, pipeline)
                handler = self.uri_registry.resolve(node.action)
                if getattr(node, "timeout", None):
                    result = await asyncio.wait_for(asyncio.to_thread(lambda: handler(**kwargs) or {}), timeout=node.timeout)
                else:
                    result = handler(**kwargs) or {}
                if not isinstance(result, dict):
                    result = {"value": result}
                for key in node.outputs:
                    if key in result:
                        await self.context.set(f"{node.node_id}.{key}", result[key])
                node.result = result
                node.error = None
                node.status = NodeStatus.SUCCESS
                return
            except Exception as exc:
                last_error = exc
                node.error = str(exc)
                attempt += 1
                if attempt <= node.retries:
                    continue
                if node.on_error == "skip":
                    node.status = NodeStatus.SUCCESS
                    node.result = {"skipped": True, "error": str(exc)}
                    return
                node.status = NodeStatus.FAILED
                return
        if last_error is not None:
            node.error = str(last_error)
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
