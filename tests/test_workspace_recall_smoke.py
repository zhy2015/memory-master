from memory_master_workspace import get_memory_master


def test_workspace_recall_smoke():
    mm = get_memory_master('/Users/hidream/.openclaw/workspace')
    result = mm.recall('Moltbook', limit=3)
    assert result['status'] == 'success'
    assert 'memory_search' in result
    assert 'active_todos' in result
    assert 'heartbeat_state' in result
