#!/usr/bin/env python3
"""Demo pipeline: write -> consolidate -> index -> search -> status."""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory_master import MemoryMaster
from workflow_engine import WorkflowEngine, WorkflowNode, WorkflowPipeline
from workflow_engine.registry import ActionRegistry


def build_registry(mm: MemoryMaster) -> ActionRegistry:
    registry = ActionRegistry()
    registry.register("write", lambda content: mm.write_daily(content, metadata={"source": "pipeline_demo"}))
    registry.register("consolidate", lambda dry_run=False: mm.consolidate(dry_run=dry_run))
    registry.register("index", lambda: mm.build_index())
    registry.register("status", lambda: mm.status())
    registry.register("search", lambda query, limit=3: mm.search(query=query, limit=limit))
    return registry


async def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp)
        mm = MemoryMaster(workspace)
        registry = build_registry(mm)

        pipeline = (
            WorkflowPipeline("memory-demo", "memory demo")
            .add_node(WorkflowNode("write_log", "write", inputs={"content": "LEARNED: workflow demos make adoption easier"}, outputs=["file"]))
            .add_node(WorkflowNode("consolidate", "consolidate", outputs=["insights_merged"]))
            .add_node(WorkflowNode("index", "index", outputs=["indexed_chunks"]))
            .add_node(WorkflowNode("search", "search", inputs={"query": "workflow demos", "limit": "3"}, outputs=["results"]))
            .add_node(WorkflowNode("status", "status", outputs=["status"]))
            .add_edge("write_log", "consolidate")
            .add_edge("consolidate", "index")
            .add_edge("index", "search")
            .add_edge("search", "status")
        )

        result = await WorkflowEngine(registry.as_dict()).execute(pipeline)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
