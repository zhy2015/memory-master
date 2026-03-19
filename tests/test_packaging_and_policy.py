import asyncio
import tempfile
import time
import unittest
from pathlib import Path

from workflow_engine import WorkflowEngine, WorkflowNode, WorkflowPipeline
from workflow_engine.validation import PipelineValidationError, validate_pipeline_data


class PackagingAndPolicyTest(unittest.TestCase):
    def test_pyproject_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / 'pyproject.toml').exists())

    def test_timeout_marks_node_failed(self):
        def slow():
            time.sleep(0.2)
            return {"ok": True}

        pipeline = WorkflowPipeline("timeout-demo", "timeout demo").add_node(
            WorkflowNode("slow", "slow", timeout=0.01)
        )
        with self.assertRaises(RuntimeError):
            asyncio.run(WorkflowEngine({"slow": slow}).execute(pipeline))

    def test_pipeline_continue_policy(self):
        def bad():
            raise RuntimeError("boom")

        def good():
            return {"ok": True}

        pipeline = WorkflowPipeline("continue-demo", "continue demo", on_error="continue")
        pipeline.add_node(WorkflowNode("bad", "bad"))
        pipeline.add_node(WorkflowNode("good", "good", outputs=["ok"]))
        result = asyncio.run(WorkflowEngine({"bad": bad, "good": good}).execute(pipeline))
        self.assertIn("good", result)
        self.assertTrue(result["good"]["ok"])

    def test_validation_rejects_bad_timeout(self):
        with self.assertRaises(PipelineValidationError):
            validate_pipeline_data(
                {
                    "pipeline_id": "bad-timeout",
                    "nodes": [{"node_id": "n1", "action": "x", "timeout": "soon"}],
                    "edges": [],
                }
            )


if __name__ == '__main__':
    unittest.main()
