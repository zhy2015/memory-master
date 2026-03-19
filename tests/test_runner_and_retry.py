import asyncio
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from workflow_engine import WorkflowEngine, WorkflowNode, WorkflowPipeline


class RunnerAndRetryTest(unittest.TestCase):
    def test_retry_then_success(self):
        state = {"calls": 0}

        def flaky():
            state["calls"] += 1
            if state["calls"] < 2:
                raise RuntimeError("boom")
            return {"ok": True}

        pipeline = WorkflowPipeline("retry-demo", "retry demo").add_node(
            WorkflowNode("flaky", "flaky", retries=1, outputs=["ok"])
        )
        result = asyncio.run(WorkflowEngine({"flaky": flaky}).execute(pipeline))
        self.assertTrue(result["flaky"]["ok"])
        self.assertEqual(state["calls"], 2)

    def test_skip_on_error(self):
        def always_fail():
            raise RuntimeError("nope")

        pipeline = WorkflowPipeline("skip-demo", "skip demo").add_node(
            WorkflowNode("bad", "bad", retries=0, on_error="skip")
        )
        result = asyncio.run(WorkflowEngine({"bad": always_fail}).execute(pipeline))
        self.assertTrue(result["bad"]["skipped"])

    def test_cli_runner_executes_pipeline_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pipeline_path = root / "pipeline.json"
            pipeline_path.write_text(
                json.dumps(
                    {
                        "pipeline_id": "cli-demo",
                        "name": "cli demo",
                        "nodes": [
                            {
                                "node_id": "write",
                                "action": "skill://memory-master/write",
                                "inputs": {"content": "LEARNED: cli tests keep runner honest"},
                                "outputs": ["file"],
                            },
                            {
                                "node_id": "index",
                                "action": "memory://index",
                                "outputs": ["indexed_chunks"],
                            },
                        ],
                        "edges": [["write", "index"]],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, "workflow_engine/runner.py", str(pipeline_path), "--workspace", str(root)],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(proc.stdout)
            self.assertIn("index", payload)


if __name__ == "__main__":
    unittest.main()
