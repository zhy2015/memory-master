import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from memory_master import MemoryMaster
from workflow_engine import WorkflowEngine, WorkflowNode, WorkflowPipeline, WorkflowRunStore, build_memory_registry
from workflow_engine.validation import PipelineValidationError, validate_pipeline_data
from workflow_engine.runner import load_pipeline


class ValidationAndHistoryTest(unittest.TestCase):
    def test_validation_rejects_bad_policy(self):
        with self.assertRaises(PipelineValidationError):
            validate_pipeline_data(
                {
                    "pipeline_id": "bad",
                    "nodes": [{"node_id": "n1", "action": "x", "on_error": "explode"}],
                    "edges": [],
                }
            )

    def test_validation_rejects_unknown_edge_node(self):
        with self.assertRaises(PipelineValidationError):
            validate_pipeline_data(
                {
                    "pipeline_id": "bad-edge",
                    "nodes": [{"node_id": "n1", "action": "x"}],
                    "edges": [["n1", "n2"]],
                }
            )

    def test_runner_load_pipeline_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"pipeline_id": "x", "nodes": [], "edges": []}), encoding="utf-8")
            with self.assertRaises(PipelineValidationError):
                load_pipeline(path)

    def test_history_files_are_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            mm = MemoryMaster(tmp)
            registry = build_memory_registry(mm)
            store = WorkflowRunStore(Path(tmp) / "workflow-runs")
            pipeline = WorkflowPipeline("history-demo", "history demo").add_node(
                WorkflowNode("write", "skill://memory-master/write", inputs={"content": "LEARNED: history helps debugging"}, outputs=["file"])
            )
            asyncio.run(WorkflowEngine(registry.as_dict(), run_store=store).execute(pipeline))
            history = store.list_history("history-demo")
            self.assertGreaterEqual(len(history), 2)
            latest = store.load_pipeline_state("history-demo")
            self.assertIn("run_id", latest)
            self.assertEqual(latest["event"], "completed")


if __name__ == "__main__":
    unittest.main()
