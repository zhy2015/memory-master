import asyncio
import tempfile
import unittest

from memory_master import MemoryMaster
from workflow_engine import ActionRegistry, WorkflowEngine, WorkflowNode, WorkflowPipeline


class RegistryDemoTest(unittest.TestCase):
    def test_registry_driven_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            mm = MemoryMaster(tmp)
            registry = ActionRegistry()
            registry.register_many(
                {
                    "write": lambda content: mm.write_daily(content),
                    "consolidate": lambda: mm.consolidate(),
                    "index": lambda: mm.build_index(),
                    "search": lambda query: mm.search(query=query, limit=2),
                }
            )

            pipeline = (
                WorkflowPipeline("registry-demo", "registry demo")
                .add_node(WorkflowNode("write", "write", inputs={"content": "LEARNED: registry layer helps"}, outputs=["file"]))
                .add_node(WorkflowNode("consolidate", "consolidate", outputs=["insights_merged"]))
                .add_node(WorkflowNode("index", "index", outputs=["indexed_chunks"]))
                .add_node(WorkflowNode("search", "search", inputs={"query": "registry layer"}, outputs=["results"]))
                .add_edge("write", "consolidate")
                .add_edge("consolidate", "index")
                .add_edge("index", "search")
            )

            result = asyncio.run(WorkflowEngine(registry.as_dict()).execute(pipeline))
            self.assertIn("search", result)
            self.assertEqual(result["search"]["status"], "success")


if __name__ == "__main__":
    unittest.main()
