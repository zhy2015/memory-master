from pathlib import Path

from memory_master import MemoryMaster


WORKSPACE = Path('/Users/hidream/.openclaw/workspace')


def test_workspace_status_and_search_smoke():
    mm = MemoryMaster(str(WORKSPACE))
    status = mm.status()
    assert status['status'] == 'success'
    result = mm.search('Moltbook', limit=3)
    assert result['status'] == 'success'
    assert isinstance(result['results'], list)
