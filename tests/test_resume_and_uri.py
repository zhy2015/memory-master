import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from memory_master import MemoryMaster
from workflow_engine import (
    SkillURIRegistry,
    WorkflowEngine,
    WorkflowNode,
    WorkflowPipeline,
    WorkflowRunStore,
    build_memory_registry,
)


class ResumeAndURITest(unittest.TestCase):
    def test_skill_uri_registry_resolves_memory_scheme(self):
        with tempfile.TemporaryDirectory() as tmp:
            mm = MemoryMaster(tmp)
            actions = build_memory_registry(mm).as_dict()
            uri = SkillURIRegistry(actions)
            handler = uri.resolve("skill://memory-master/status")
            result = handler()
            self.assertEqual(result["status"], "success")

    def test_resume_skips_completed_nodes(self):
        with tempfile.TemporaryDirectory() as tmp:
            mm = MemoryMaster(tmp)
            registry = build_memory_registry(mm)
            store = WorkflowRunStore(Path(tmp) / "workflow-runs")

            pipeline = (
                WorkflowPipeline("resume-demo", "resume demo")
                .add_node(WorkflowNode("write", "skill://memory-master/write", inputs={"content": "LEARNED: resume avoids duplicate work"}, outputs=["file"]))
                .add_node(WorkflowNode("index", "skill://memory-master/index", outputs=["indexed_chunks"]))
                .add_edge("write", "index")
            )

            asyncio.run(WorkflowEngine(registry.as_dict(), run_store=store).execute(pipeline))

            run_file = Path(tmp) / "workflow-runs" / "resume-demo.json"
            payload = json.loads(run_file.read_text(encoding="utf-8"))
            payload["pipeline"]["nodes"]["write"]["status"] = "success"
            payload["pipeline"]["nodes"]["index"]["status"] = "pending"
            run_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

            rerun = (
                WorkflowPipeline("resume-demo", "resume demo")
                .add_node(WorkflowNode("write", "skill://memory-master/write", inputs={"content": "LEARNED: resume avoids duplicate work"}, outputs=["file"]))
                .add_node(WorkflowNode("index", "skill://memory-master/index", outputs=["indexed_chunks"]))
                .add_edge("write", "index")
            )

            result = asyncio.run(WorkflowEngine(registry.as_dict(), run_store=store).execute(rerun, resume=True))
            self.assertIn("index", result)
            daily_files = list((Path(tmp) / "memory" / "daily").glob("*.md"))
            self.assertEqual(len(daily_files), 1)


if __name__ == "__main__":
    unittest.main()
