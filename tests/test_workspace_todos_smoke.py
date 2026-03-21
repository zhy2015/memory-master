from pathlib import Path

from memory_master_workspace import get_memory_master


def test_workspace_todos_smoke():
    mm = get_memory_master('/Users/hidream/.openclaw/workspace')
    result = mm.read_active_todos()
    assert result['status'] == 'success'
    assert result['exists'] is True
    assert result['todo_count'] >= 1
