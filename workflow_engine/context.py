"""Minimal async workflow context for memory pipelines."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ContextSnapshot:
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    version: int = 1


class WorkflowContext:
    def __init__(self, workflow_id: str = "default"):
        self.workflow_id = workflow_id
        self._data: Dict[str, Any] = {}
        self._lock = None
        self._version = 0
        self._history: List[ContextSnapshot] = []
        self._max_history = 10

    def _ensure_lock(self):
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def set(self, key: str, value: Any) -> None:
        async with self._ensure_lock():
            self._data[key] = value
            self._version += 1

    async def get(self, key: str, default: Any = None) -> Any:
        async with self._ensure_lock():
            return self._data.get(key, default)

    async def keys(self) -> List[str]:
        async with self._ensure_lock():
            return list(self._data.keys())

    async def to_dict(self) -> Dict[str, Any]:
        async with self._ensure_lock():
            return self._data.copy()

    async def snapshot(self) -> ContextSnapshot:
        async with self._ensure_lock():
            snapshot = ContextSnapshot(
                data=self._data.copy(),
                timestamp=time.time(),
                version=self._version,
            )
            self._history.append(snapshot)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history :]
            return snapshot

    async def restore(self, snapshot: ContextSnapshot) -> None:
        async with self._ensure_lock():
            self._data = snapshot.data.copy()
            self._version = snapshot.version

    async def clear(self) -> None:
        async with self._ensure_lock():
            self._data.clear()
            self._version += 1


_contexts: Dict[str, WorkflowContext] = {}


def get_context(workflow_id: str = "default") -> WorkflowContext:
    if workflow_id not in _contexts:
        _contexts[workflow_id] = WorkflowContext(workflow_id)
    return _contexts[workflow_id]


def clear_all_contexts() -> None:
    _contexts.clear()
