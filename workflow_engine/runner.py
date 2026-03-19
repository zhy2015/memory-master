#!/usr/bin/env python3
"""CLI runner for memory-master workflows."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from memory_master import MemoryMaster
from workflow_engine import WorkflowEngine, WorkflowNode, WorkflowPipeline, WorkflowRunStore, build_memory_registry
from workflow_engine.validation import validate_pipeline_data


def load_pipeline(path: str | Path) -> WorkflowPipeline:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_pipeline_data(data)
    pipeline = WorkflowPipeline(data["pipeline_id"], data.get("name", data["pipeline_id"]), on_error=data.get("on_error", "fail"))
    for node in data.get("nodes", []):
        pipeline.add_node(
            WorkflowNode(
                node_id=node["node_id"],
                action=node["action"],
                inputs=node.get("inputs", {}),
                outputs=node.get("outputs", []),
                retries=node.get("retries", 0),
                timeout=node.get("timeout"),
                on_error=node.get("on_error", "fail"),
            )
        )
    for edge in data.get("edges", []):
        pipeline.add_edge(edge[0], edge[1])
    return pipeline


async def run(args):
    mm = MemoryMaster(args.workspace)
    registry = build_memory_registry(mm)
    store = WorkflowRunStore(Path(args.workspace) / "workflow-runs")
    pipeline = load_pipeline(args.pipeline)
    engine = WorkflowEngine(registry.as_dict(), run_store=store)
    result = await engine.execute(pipeline, resume=args.resume)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Run memory-master workflow pipelines")
    parser.add_argument("pipeline", help="Path to pipeline JSON definition")
    parser.add_argument("--workspace", default=".", help="Workspace root for MemoryMaster")
    parser.add_argument("--resume", action="store_true", help="Resume from saved workflow state")
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
