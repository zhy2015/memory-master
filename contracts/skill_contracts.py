"""Local mirror of the governance foundation contract.

This repository keeps a vendored copy so it remains runnable standalone,
while staying structurally aligned with skill-governance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class ToolSchema:
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionResult:
    ok: bool
    data: Any = None
    error: Optional[str] = None
    code: str = "OK"
    meta: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def success(cls, data: Any = None, **meta: Any) -> "ExecutionResult":
        return cls(ok=True, data=data, meta=meta)

    @classmethod
    def failure(cls, error: str, code: str = "ERROR", **meta: Any) -> "ExecutionResult":
        return cls(ok=False, error=error, code=code, meta=meta)


@dataclass(frozen=True)
class GlobalContext:
    config: Dict[str, Any] = field(default_factory=dict)
    logger: Any = None
    telemetry: Any = None
    storage: Any = None


@dataclass(frozen=True)
class SkillDescriptor:
    name: str
    description: str
    task_nodes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    category: str | None = None
    visibility: str = "public"
    status: str = "experimental"
    owner: str | None = None


@dataclass(frozen=True)
class TaskContext:
    task_node: str | None
    intent: str
    channel: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SkillCandidate:
    descriptor: SkillDescriptor
    score: float
    reason: str


@runtime_checkable
class ISkill(Protocol):
    name: str
    description: str

    def get_tool_schemas(self) -> List[ToolSchema]:
        ...

    def init(self, context: GlobalContext) -> None:
        ...

    def shutdown(self) -> None:
        ...

    def execute(self, tool_name: str, params: Dict[str, Any]) -> ExecutionResult:
        ...
