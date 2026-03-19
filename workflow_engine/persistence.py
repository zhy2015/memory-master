"""Simple JSON persistence for workflow runs."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from uuid import uuid4


def _json_default(value):
    if hasattr(value, "value"):
        return value.value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


class WorkflowRunStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.history_dir = self.root / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def save_pipeline_state(self, pipeline, *, event: str, extra: Dict[str, Any] | None = None) -> Path:
        run_id = (extra or {}).get("run_id") or str(uuid4())
        payload = {
            "run_id": run_id,
            "event": event,
            "saved_at": datetime.now().isoformat(),
            "pipeline": {
                "pipeline_id": pipeline.pipeline_id,
                "name": pipeline.name,
                "nodes": {nid: asdict(node) for nid, node in pipeline.nodes.items()},
                "edges": pipeline.edges,
            },
            "extra": extra or {},
        }
        latest = self.root / f"{pipeline.pipeline_id}.json"
        latest.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
        stamp = payload["saved_at"].replace(":", "-")
        hist = self.history_dir / f"{pipeline.pipeline_id}--{stamp}--{event}.json"
        hist.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
        return latest

    def load_pipeline_state(self, pipeline_id: str) -> Dict[str, Any]:
        path = self.root / f"{pipeline_id}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def list_history(self, pipeline_id: str) -> list:
        return sorted(str(p) for p in self.history_dir.glob(f"{pipeline_id}--*.json"))
