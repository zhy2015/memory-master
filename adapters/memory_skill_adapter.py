"""Memory skill adapter.

Thin anti-corruption layer that exposes MemoryCore through the global ISkill contract.
"""

from __future__ import annotations

from typing import Dict, List

from core.infra.skill_contracts import ExecutionResult, GlobalContext, ISkill, ToolSchema
from memory.core.memory_core import MemoryCore


class MemorySkillAdapter(ISkill):
    name = "system_memory"
    description = "Provides long-term memory maintenance and recall capabilities."

    def __init__(self, memory_core: MemoryCore | None = None):
        self.memory_core = memory_core or MemoryCore()
        self.context = GlobalContext()

    def init(self, context: GlobalContext) -> None:
        self.context = context

    def shutdown(self) -> None:
        return None

    def get_tool_schemas(self) -> List[ToolSchema]:
        return [
            ToolSchema(
                name="memory_status",
                description="Get memory system status.",
                parameters={"type": "object", "properties": {}},
            ),
            ToolSchema(
                name="memory_consolidate",
                description="Run memory consolidation/archival maintenance.",
                parameters={"type": "object", "properties": {}},
            ),
            ToolSchema(
                name="memory_search",
                description="Search memory using a query string.",
                parameters={
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            ),
        ]

    def execute(self, tool_name: str, params: Dict[str, object]) -> ExecutionResult:
        try:
            if tool_name == "memory_status":
                return ExecutionResult.success(self.memory_core.status())
            if tool_name == "memory_consolidate":
                return ExecutionResult.success(self.memory_core.consolidate())
            if tool_name == "memory_search":
                query = str(params.get("query", "")).strip()
                if not query:
                    return ExecutionResult.failure("Missing query", code="INVALID_PARAMS")
                return ExecutionResult.success(self.memory_core.search(query))
            return ExecutionResult.failure(f"Unknown tool: {tool_name}", code="UNKNOWN_TOOL")
        except Exception as exc:
            return ExecutionResult.failure(str(exc), code="EXECUTION_ERROR")
