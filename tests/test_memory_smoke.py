from pathlib import Path

from adapters.memory_skill_adapter import MemorySkillAdapter
from core.memory_core import MemoryCore


def test_memory_core_status_uses_injected_workspace(tmp_path: Path):
    core = MemoryCore(workspace_root=str(tmp_path))
    status = core.status()
    assert status["workspace"] == str(tmp_path)
    assert status["daily_dir"] == str(tmp_path / "memory" / "daily")


def test_memory_adapter_consolidate_smoke(tmp_path: Path):
    adapter = MemorySkillAdapter(MemoryCore(workspace_root=str(tmp_path)))
    result = adapter.execute("memory_consolidate", {})
    assert result.ok is True
    assert isinstance(result.data, dict)
    assert "processed" in result.data
