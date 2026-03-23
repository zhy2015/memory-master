from pathlib import Path

from memory_master import MemoryMaster
from adapters.memory_skill_adapter import MemorySkillAdapter


def test_memory_master_reads_active_todos(tmp_path: Path):
    todos_dir = tmp_path / 'memory' / 'todos'
    todos_dir.mkdir(parents=True)
    active = todos_dir / 'active.md'
    active.write_text('## [TODO-001] Demo\n', encoding='utf-8')

    mm = MemoryMaster(str(tmp_path))
    result = mm.read_active_todos()
    assert result['exists'] is True
    assert result['todo_count'] == 1


def test_memory_adapter_exposes_todo_tools(tmp_path: Path):
    todos_dir = tmp_path / 'memory' / 'todos'
    todos_dir.mkdir(parents=True)
    (todos_dir / 'active.md').write_text('## [TODO-001] Demo\n', encoding='utf-8')

    adapter = MemorySkillAdapter(memory_core=MemoryMaster(str(tmp_path)))
    status = adapter.execute('memory_todos_status', {})
    todos = adapter.execute('memory_read_active_todos', {})

    assert status.ok is True
    assert todos.ok is True
    assert todos.data['todo_count'] == 1
