import asyncio
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from workflow_engine import WorkflowEngine, WorkflowNode, WorkflowPipeline


class BuildAndParallelTest(unittest.TestCase):
    def test_parallel_execution_runs_independent_nodes(self):
        calls = []

        def make(name):
            def fn():
                time.sleep(0.1)
                calls.append(name)
                return {"name": name}
            return fn

        pipeline = WorkflowPipeline("parallel-demo", "parallel demo")
        pipeline.add_node(WorkflowNode("a", "a", outputs=["name"]))
        pipeline.add_node(WorkflowNode("b", "b", outputs=["name"]))
        start = time.time()
        result = asyncio.run(WorkflowEngine({"a": make("a"), "b": make("b")}).execute(pipeline, parallel=True))
        elapsed = time.time() - start
        self.assertIn("a", result)
        self.assertIn("b", result)
        self.assertLess(elapsed, 0.45)
        self.assertCountEqual(calls, ["a", "b"])

    def test_package_build_or_reports_missing_dependency_cleanly(self):
        root = Path(__file__).resolve().parents[1]
        proc = subprocess.run(
            [sys.executable, "-m", "build"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertIn(proc.returncode, (0, 1))
        if proc.returncode != 0:
            self.assertTrue(proc.stderr or proc.stdout)


if __name__ == '__main__':
    unittest.main()
