from pathlib import Path

from memory_master import MemoryMaster
from adapters.memory_skill_adapter import MemorySkillAdapter


def test_memory_master_recall_combines_sources(tmp_path: Path):
    mem = tmp_path / 'memory'
    (mem / 'core').mkdir(parents=True)
    (mem / 'daily').mkdir(parents=True)
    (mem / 'todos').mkdir(parents=True)
    (mem / 'core' / 'MEMORY.md').write_text('Moltbook signal\n', encoding='utf-8')
    (mem / 'todos' / 'active.md').write_text('## [TODO-001] Moltbook\n', encoding='utf-8')
    (mem / 'heartbeat-state.json').write_text('{"lastMoltbookCheck":"now"}', encoding='utf-8')

    mm = MemoryMaster(str(tmp_path))
    result = mm.recall('Moltbook', limit=3)
    assert result['status'] == 'success'
    assert 'memory_search' in result
    assert result['active_todos']['todo_count'] == 1
    assert result['heartbeat_state']['lastMoltbookCheck'] == 'now'


def test_memory_adapter_exposes_recall_tool(tmp_path: Path):
    mem = tmp_path / 'memory'
    (mem / 'core').mkdir(parents=True)
    (mem / 'daily').mkdir(parents=True)
    (mem / 'todos').mkdir(parents=True)
    (mem / 'core' / 'MEMORY.md').write_text('Moltbook signal\n', encoding='utf-8')
    (mem / 'todos' / 'active.md').write_text('## [TODO-001] Moltbook\n', encoding='utf-8')
    (mem / 'heartbeat-state.json').write_text('{"lastMoltbookCheck":"now"}', encoding='utf-8')

    adapter = MemorySkillAdapter(memory_core=MemoryMaster(str(tmp_path)))
    result = adapter.execute('memory_recall', {'query': 'Moltbook', 'limit': 3})
    assert result.ok is True
    assert result.data['status'] == 'success'
