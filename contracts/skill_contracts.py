"""Local copy of the narrow governance/adapter contract used by memory-master.

This keeps the adapter runnable and testable inside the standalone repository
without depending on workspace-specific package layout.
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
