from __future__ import annotations

from pathlib import Path

from core.memory_core import MemoryCore


def test_memory_core_search_returns_ranked_results(tmp_path: Path):
    daily = tmp_path / 'memory' / 'daily'
    core = tmp_path / 'memory' / 'core'
    daily.mkdir(parents=True)
    core.mkdir(parents=True)
    (core / 'MEMORY.md').write_text('alpha beta\n', encoding='utf-8')
    (daily / '2026-03-21.md').write_text('something alpha happened\nalpha again\n', encoding='utf-8')

    memory = MemoryCore(tmp_path)
    result = memory.search('alpha')

    assert result['backend'] == 'simple_text_search'
    assert len(result['results']) >= 1
    assert result['results'][0]['score'] >= 1
