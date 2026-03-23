from __future__ import annotations

from pathlib import Path

from daemon.insight_extractor import InsightExtractor


def test_insight_extractor_parses_failure_success_and_metrics(tmp_path: Path):
    log = tmp_path / '2026-03-21.md'
    log.write_text('FAILED step: missing config\nSUCCESS (cache warmed)\nSkills registered: 7\n', encoding='utf-8')

    extractor = InsightExtractor()
    insights = extractor.extract(log)

    types = {item['type'] for item in insights}
    assert {'failure_pattern', 'success_pattern', 'metric'} <= types
