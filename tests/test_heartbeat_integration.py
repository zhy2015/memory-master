from pathlib import Path

from memory_master import MemoryMaster
from adapters.memory_skill_adapter import MemorySkillAdapter


def test_memory_master_reads_heartbeat_state(tmp_path: Path):
    mem = tmp_path / 'memory'
    mem.mkdir(parents=True)
    (mem / 'heartbeat-state.json').write_text('{"last": 1}', encoding='utf-8')

    mm = MemoryMaster(str(tmp_path))
    result = mm.heartbeat_status()
    assert result['exists'] is True
    assert result['data']['last'] == 1


def test_memory_adapter_exposes_heartbeat_tool(tmp_path: Path):
    mem = tmp_path / 'memory'
    mem.mkdir(parents=True)
    (mem / 'heartbeat-state.json').write_text('{"last": 1}', encoding='utf-8')

    adapter = MemorySkillAdapter(memory_core=MemoryMaster(str(tmp_path)))
    result = adapter.execute('memory_heartbeat_status', {})
    assert result.ok is True
    assert result.data['data']['last'] == 1
