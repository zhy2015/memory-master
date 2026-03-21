from memory_master_workspace import get_memory_master


def test_workspace_heartbeat_smoke():
    mm = get_memory_master('/Users/hidream/.openclaw/workspace')
    result = mm.heartbeat_status()
    assert result['status'] == 'success'
    assert result['exists'] is True
    assert isinstance(result['data'], dict)
